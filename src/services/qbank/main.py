from fastapi import FastAPI, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select
from contextlib import asynccontextmanager

# Import shared components
from src.shared.models.question import GeneratedQuestion
from src.shared.core.database import get_session, create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="QBank Service", lifespan=lifespan)

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
