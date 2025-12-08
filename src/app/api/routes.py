from fastapi import APIRouter, HTTPException, Depends
from typing import List
from sqlmodel import Session, select

from ..models.question import SyllabusContent, GeneratedQuestion
from ..core.database import get_session
from ..services.generator import GeneratorService

router = APIRouter()
generator_service = GeneratorService()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "Question Gen Engine"}

@router.post("/generate", response_model=List[GeneratedQuestion])
def generate_questions_endpoint(content: SyllabusContent, session: Session = Depends(get_session)):
    try:
        # 1. Generate
        questions = generator_service.generate_questions(content)
        
        # 2. Save
        for q in questions:
            session.add(q)
        session.commit()
        
        # 3. Refresh
        for q in questions:
            session.refresh(q)
            
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/questions", response_model=List[GeneratedQuestion])
def list_questions(session: Session = Depends(get_session)):
    return session.exec(select(GeneratedQuestion)).all()
