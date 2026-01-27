from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session
from contextlib import asynccontextmanager
import os
import httpx

from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.core.database import get_session, create_db_and_tables
from src.services.generator.service import GeneratorService

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://127.0.0.1:8000")
SERVICE_PORT = os.getenv("SERVICE_PORT", "8004")
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
                print(f"Registering Generator at {SERVICE_URL} with Gateway {GATEWAY_URL} (Attempt {attempt+1}/{max_retries})...")
                resp = await client.post(
                    f"{GATEWAY_URL}/registry/register", 
                    json={"name": "generator", "url": SERVICE_URL},
                    timeout=5.0
                )
                if resp.status_code == 200:
                    print(f"Successfully registered Generator")
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
