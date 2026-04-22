from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from typing import List
import os

from src.shared.models import SyllabusContent, GeneratedQuestion
from src.services.generator.service import GeneratorService

QT_INTERNAL_API_KEY = os.getenv("QT_INTERNAL_API_KEY", "default-insecure-key")
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


def verify_api_key(api_key_header: str = Security(api_key_header)):
    if not api_key_header or api_key_header != QT_INTERNAL_API_KEY:
        raise HTTPException(
            status_code=403, detail="Could not validate API key")
    return api_key_header


app = FastAPI(title="Question Gen Engine (Stateless)")
generator_service = GeneratorService()


@app.post("/generate", response_model=List[GeneratedQuestion])
def generate_questions_endpoint(
        content: SyllabusContent,
        api_key: str = Depends(verify_api_key)):
    try:
        questions = generator_service.generate_questions(content)
        return questions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Question Generation Engine"}
