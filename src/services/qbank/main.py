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
SERVICE_NAME = "science_qbank" if SERVICE_PORT == "8002" else "general_qbank" # Simple heuristic for now
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
SERVICE_URL = f"http://127.0.0.1:{SERVICE_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Registration
    try:
        async with httpx.AsyncClient() as client:
            print(f"Registering {SERVICE_NAME} at {SERVICE_URL} with Gateway...")
            await client.post(
                f"{GATEWAY_URL}/registry/register", 
                json={"name": SERVICE_NAME, "url": SERVICE_URL}
            )
    except Exception as e:
        print(f"Failed to register service: {e}")
        
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
    session: Session = Depends(get_session)
):
    query = select(GeneratedQuestion)
    if medium:
        query = query.where(GeneratedQuestion.medium == medium)
    if subject:
        query = query.where(GeneratedQuestion.subject == subject)
    return session.exec(query).all()

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "QBank Service"}
