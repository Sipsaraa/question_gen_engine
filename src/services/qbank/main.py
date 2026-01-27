from fastapi import FastAPI, Depends, HTTPException
from typing import List, Optional
from sqlmodel import Session, select
from contextlib import asynccontextmanager
import os
import httpx

# Import shared components
from src.shared.models.question import GeneratedQuestion
from src.shared.core.database import get_session, create_db_and_tables

# Determine Service Name based on what we are running
# In a real setup, this might be passed as an ENV var 'SERVICE_NAME'
SERVICE_PORT = os.getenv("SERVICE_PORT", "8002")
SERVICE_NAME = os.getenv("SERVICE_NAME", "general_qbank") # Default to general if not specified
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
SERVICE_HOST = os.getenv("SERVICE_HOST", "127.0.0.1")
SERVICE_URL = f"http://{SERVICE_HOST}:{SERVICE_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Registration with Retry
    import time
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
    else:
        print("CRITICAL: Failed to register service after all attempts.")
        
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

app = FastAPI(title=f"{SERVICE_NAME.replace('_', ' ').title()}", lifespan=lifespan)

@app.get("/questions", response_model=List[GeneratedQuestion])
def list_questions(
    medium: Optional[str] = None, 
    subject: Optional[str] = None,
    grade: Optional[str] = None,
    chapter_id: Optional[str] = None,
    start_id: Optional[int] = None,
    end_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    query = select(GeneratedQuestion)
    if medium:
        query = query.where(GeneratedQuestion.medium == medium)
    if subject:
        query = query.where(GeneratedQuestion.subject == subject)
    if grade:
        query = query.where(GeneratedQuestion.grade == grade)
    if chapter_id:
        query = query.where(GeneratedQuestion.chapter_id == chapter_id)
    
    # ID Range Filter
    if start_id is not None:
        query = query.where(GeneratedQuestion.id >= start_id)
    if end_id is not None:
        query = query.where(GeneratedQuestion.id <= end_id)
        
    return session.exec(query).all()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "QBank Service"}
