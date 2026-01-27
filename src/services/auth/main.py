from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import List, Annotated
import os
import httpx
import time
import uuid
from contextlib import asynccontextmanager

from src.shared.core.database import get_session, create_db_and_tables
from src.shared.models.auth import (
    AdminUser, APIKeyMetadata, Token, TokenData, UserLogin, 
    APIKeyRequest, APIKeyResponse
)
from src.shared.utils.auth import (
    verify_password, create_access_token, create_api_key, 
    decode_token, get_password_hash
)

# Configuration
SERVICE_PORT = os.getenv("SERVICE_PORT", "8005")
SERVICE_NAME = "auth_service"
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway:8000")
SERVICE_HOST = os.getenv("SERVICE_HOST", "auth")
SERVICE_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Registration with Retry
    max_retries = 10
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                print(f"Registering {SERVICE_NAME} at {SERVICE_URL} with Gateway (Attempt {attempt+1}/{max_retries})...")
                resp = await client.post(
                    f"{GATEWAY_URL}/registry/register", 
                    json={"name": SERVICE_NAME, "url": SERVICE_URL},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    print(f"Successfully registered {SERVICE_NAME}")
                    break
        except Exception as e:
            print(f"Failed to register service (Attempt {attempt+1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
        else:
             if resp.status_code != 200:
                 print(f"Registration failed with status {resp.status_code}")
                 if attempt < max_retries - 1:
                    time.sleep(2)
    
    yield
    
    # Deregistration
    try:
        async with httpx.AsyncClient() as client:
             await client.post(
                f"{GATEWAY_URL}/registry/deregister", 
                json={"name": SERVICE_NAME, "url": SERVICE_URL}
            )
    except Exception as e:
        print(f"Failed to deregister service: {e}")

app = FastAPI(title="Auth Service", lifespan=lifespan)

# --- Dependencies ---

async def get_current_admin(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)):
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
    user = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return user

# --- Endpoints ---

@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    user = session.exec(select(AdminUser).where(AdminUser.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "type": "admin"}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=AdminUser)
async def read_users_me(current_user: Annotated[AdminUser, Depends(get_current_admin)]):
    return current_user

# --- API Key Management (Admin Only) ---

@app.post("/api-keys", response_model=APIKeyResponse)
async def create_new_api_key(
    request: APIKeyRequest,
    current_user: Annotated[AdminUser, Depends(get_current_admin)],
    session: Session = Depends(get_session)
):
    key_id = str(uuid.uuid4())
    permissions_str = ",".join(request.permissions)
    
    # Store Metadata
    api_key_meta = APIKeyMetadata(
        key_id=key_id,
        name=request.name,
        owner=current_user.username,
        permissions=permissions_str
    )
    session.add(api_key_meta)
    session.commit()
    session.refresh(api_key_meta)
    
    # Generate Token (embedding key_id and permissions)
    access_token = create_api_key(
        data={"sub": key_id, "type": "api_key", "permissions": permissions_str}
    )
    
    return APIKeyResponse(
        key_id=key_id,
        name=request.name,
        access_token=access_token,
        created_at=api_key_meta.created_at
    )

@app.get("/api-keys", response_model=List[APIKeyMetadata])
async def list_api_keys(
    current_user: Annotated[AdminUser, Depends(get_current_admin)],
    session: Session = Depends(get_session)
):
    return session.exec(select(APIKeyMetadata)).all()

@app.delete("/api-keys/{key_id}")
async def revoke_api_key(
    key_id: str,
    current_user: Annotated[AdminUser, Depends(get_current_admin)],
    session: Session = Depends(get_session)
):
    key_meta = session.exec(select(APIKeyMetadata).where(APIKeyMetadata.key_id == key_id)).first()
    if not key_meta:
        raise HTTPException(status_code=404, detail="API Key not found")
    
    key_meta.is_active = False
    session.add(key_meta)
    session.commit()
    return {"status": "revoked", "key_id": key_id}

# --- Internal Verification Endpoint ---

@app.post("/verify")
async def verify_token(
    token_data: dict, # Expects {"token": "..."}
    session: Session = Depends(get_session)
):
    token = token_data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")
        
    payload = decode_token(token)
    if not payload:
         raise HTTPException(status_code=401, detail="Invalid signature or expired")
         
    token_type = payload.get("type")
    
    if token_type == "api_key":
        # Check against DB for revocation
        key_id = payload.get("sub")
        key_meta = session.exec(select(APIKeyMetadata).where(APIKeyMetadata.key_id == key_id)).first()
        
        if not key_meta:
            raise HTTPException(status_code=401, detail="API Key metadata not found")
        
        if not key_meta.is_active:
             raise HTTPException(status_code=401, detail="API Key is revoked")
             
        return {"status": "valid", "user": key_meta.owner, "permissions": key_meta.permissions}
        
    elif token_type == "admin":
        # Check if admin user still exists/active
        username = payload.get("sub")
        user = session.exec(select(AdminUser).where(AdminUser.username == username)).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Admin user invalid")
        
        return {"status": "valid", "user": username, "role": "admin"}
        
    else:
        raise HTTPException(status_code=401, detail="Unknown token type")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Auth Service"}
