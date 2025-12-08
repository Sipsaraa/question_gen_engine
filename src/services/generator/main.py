from fastapi import FastAPI, Depends, HTTPException
from typing import List
from sqlmodel import Session
from contextlib import asynccontextmanager

from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.core.database import get_session, create_db_and_tables
from src.services.generator.service import GeneratorService

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

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
    return {"status": "ok", "service": "Generation Service"}
