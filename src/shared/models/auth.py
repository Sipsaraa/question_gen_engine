from typing import Optional, List
from sqlmodel import SQLModel, Field
from datetime import datetime

# --- Pydantic Schemas (for API responses/requests) ---

class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Optional[str] = None
    permissions: List[str] = []

class UserLogin(SQLModel):
    username: str
    password: str

class APIKeyRequest(SQLModel):
    name: str # e.g. "Mobile App v1", "Frontend"
    permissions: List[str] = []

class APIKeyResponse(SQLModel):
    key_id: str
    name: str
    access_token: str
    created_at: datetime

# --- Database Models ---

class AdminUser(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    is_active: bool = Field(default=True)
    
class APIKeyMetadata(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    key_id: str = Field(index=True, unique=True, nullable=False) # Unique public ID for the key
    name: str = Field(nullable=False)
    owner: str = Field(default="admin") # Who created it
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    # Storing permissions as comma-separated string for simplicity in SQLModel/SQLite compat
    # In Postgres could be ARRAY, but string is portable.
    permissions: str = Field(default="") 
