import httpx
from fastapi import FastAPI, HTTPException, Query, Request
from typing import List, Optional
from src.shared.models.question import GeneratedQuestion, SyllabusContent

app = FastAPI(title="Question Gen Gateway")

# Configuration
from pydantic import BaseModel

# Service Registry
SERVICE_REGISTRY = {
    "science_qbank": ["http://localhost:8002"], # Default fallbacks
    "general_qbank": ["http://localhost:8003"],
    "generator": [] 
}

class ServiceRegistration(BaseModel):
    name: str
    url: str

@app.post("/registry/register")
def register_service(param: ServiceRegistration):
    if param.name not in SERVICE_REGISTRY:
        SERVICE_REGISTRY[param.name] = []
    
    if param.url not in SERVICE_REGISTRY[param.name]:
        SERVICE_REGISTRY[param.name].append(param.url)
        print(f"Registered {param.name} at {param.url}")
    return {"status": "registered", "current_nodes": len(SERVICE_REGISTRY[param.name])}

@app.post("/registry/deregister")
def deregister_service(param: ServiceRegistration):
    if param.name in SERVICE_REGISTRY and param.url in SERVICE_REGISTRY[param.name]:
        SERVICE_REGISTRY[param.name].remove(param.url)
        print(f"Deregistered {param.name} at {param.url}")
    return {"status": "deregistered"}

import random

def get_service_url(service_name: str) -> str:
    urls = SERVICE_REGISTRY.get(service_name, [])
    if not urls:
        raise HTTPException(status_code=503, detail=f"No healthy instances for service: {service_name}")
    return random.choice(urls)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Gateway", "registry": SERVICE_REGISTRY}

@app.get("/questions", response_model=List[GeneratedQuestion])
async def list_questions(
    medium: Optional[str] = None, 
    subject: Optional[str] = None
):
    # Dynamic Lookup
    target_service = "general_qbank"
    if subject and subject.lower() == "science":
        target_service = "science_qbank"
    
    target_url = get_service_url(target_service)
    
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
            raise HTTPException(status_code=503, detail=f"Service unreachable ({target_url}): {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

@app.post("/generate", response_model=List[GeneratedQuestion])
async def generate_questions(content: SyllabusContent):
    target_url = get_service_url("generator")
    print(f"Routing generation request to: {target_url}") 
    
    async with httpx.AsyncClient() as client:
        try:
            # Forward the request body
            response = await client.post(
                f"{target_url}/generate", 
                json=content.model_dump(),
                timeout=60.0 # Generation takes time
            )
            response.raise_for_status()
            return response.json()
        except httpx.RequestError as exc:
            # Basic Retry or Remove from Registry logic could go here
            raise HTTPException(status_code=503, detail=f"Generation service unreachable ({target_url}): {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
