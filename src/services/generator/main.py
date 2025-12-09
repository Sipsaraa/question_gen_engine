from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session
from contextlib import asynccontextmanager
import os
import httpx

from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.core.database import get_session, create_db_and_tables
from src.services.generator.service import GeneratorService

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8000")
SERVICE_PORT = os.getenv("SERVICE_PORT", "8004")
SERVICE_URL = f"http://127.0.0.1:{SERVICE_PORT}"

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    
    # Registration
    try:
        async with httpx.AsyncClient() as client:
            print(f"Registering Generator at {SERVICE_URL} with Gateway {GATEWAY_URL}")
            await client.post(
                f"{GATEWAY_URL}/registry/register", 
                json={"name": "generator", "url": SERVICE_URL}
            )
    except Exception as e:
        print(f"Failed to register service: {e}")

    yield
    
    # Deregistration
    try:
        async with httpx.AsyncClient() as client:
             await client.post(
                f"{GATEWAY_URL}/registry/deregister", 
                json={"name": "generator", "url": SERVICE_URL}
            )
    except Exception as e:
        print(f"Failed to deregister service: {e}")

app = FastAPI(title="Generation Service", lifespan=lifespan)
generator_service = GeneratorService()

@app.post("/generate", response_model=List[GeneratedQuestion])
def generate_questions_endpoint(content: SyllabusContent, session: Session = Depends(get_session)):
    try:
        # 1. Generate
        questions = generator_service.generate_questions(content)
        
        # 2. Save (The Generation Service handles writing to DB)
        for q in questions:
            session.add(q)
        session.commit()
        
        # 3. Refresh
        for q in questions:
            session.refresh(q)
            
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    import os
    return {"status": "ok", "service": "Generation Service", "port": os.getenv("SERVICE_PORT")}
