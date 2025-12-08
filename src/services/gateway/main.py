import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from typing import List, Optional
from src.shared.models.question import GeneratedQuestion, SyllabusContent

app = FastAPI(title="Question Gen Gateway")

# Configuration
SCIENCE_SERVICE_URL = "http://localhost:8002"
GENERAL_SERVICE_URL = "http://localhost:8003"
GENERATION_SERVICE_URL = "http://localhost:8004"

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Gateway"}

@app.get("/questions", response_model=List[GeneratedQuestion])
async def list_questions(
    medium: Optional[str] = None, 
    subject: Optional[str] = None
):
    target_url = GENERAL_SERVICE_URL
    if subject and subject.lower() == "science":
        target_url = SCIENCE_SERVICE_URL
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward query params
            params = {}
            if medium: params['medium'] = medium
            if subject: params['subject'] = subject
            
            response = await client.get(f"{target_url}/questions", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unreachable: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

@app.post("/generate", response_model=List[GeneratedQuestion])
async def generate_questions(content: SyllabusContent):
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request body
            response = await client.post(
                f"{GENERATION_SERVICE_URL}/generate", 
                json=content.model_dump(),
                timeout=60.0 # Generation takes time
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Generation service unreachable: {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
