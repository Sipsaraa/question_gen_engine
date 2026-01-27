import httpx
from fastapi import FastAPI, HTTPException, Query, Request, UploadFile, File, Form
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from src.shared.models.question import GeneratedQuestion, SyllabusContent
from src.shared.utils.pdf_utils import extract_text_from_pdf
from src.shared.utils.pdf_generator import generate_question_pdf
from src.shared.utils.text_utils import chunk_text
import os

app = FastAPI(
    title="Question Gen Gateway",
    description="Gateway service for the Question Generation Engine. Routes requests to specialized services.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount Static Documentation (MkDocs)
site_path = os.path.join(os.getcwd(), "site")
if os.path.exists(site_path):
    app.mount("/help", StaticFiles(directory=site_path, html=True), name="help")
else:
    print("Warning: 'site' directory not found. Run 'mkdocs build' first.")

@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/help")

# Configuration
from pydantic import BaseModel

# Service Registry
SERVICE_REGISTRY = {
    "science_qbank": [], 
    "general_qbank": [],
    "generator": [] 
}

class ServiceRegistration(BaseModel):
    name: str
    url: str

@app.post("/registry/register", tags=["System"], summary="Register a Service")
def register_service(param: ServiceRegistration):
    """
    Registers a new service instance with the gateway.
    """
    if param.name not in SERVICE_REGISTRY:
        SERVICE_REGISTRY[param.name] = []
    
    if param.url not in SERVICE_REGISTRY[param.name]:
        SERVICE_REGISTRY[param.name].append(param.url)
        print(f"Registered {param.name} at {param.url}")
    return {"status": "registered", "current_nodes": len(SERVICE_REGISTRY[param.name])}

@app.post("/registry/deregister", tags=["System"], summary="Deregister a Service")
def deregister_service(param: ServiceRegistration):
    """
    Removes a service instance from the gateway registry.
    """
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

@app.get("/health", tags=["System"], summary="Health Check")
def health_check():
    """
    Checks the health of the Gateway service.
    """
    return {"status": "ok", "service": "Gateway", "registry": SERVICE_REGISTRY}

@app.get("/questions/export/pdf", tags=["Export"], summary="Export Questions to PDF")
async def export_questions_pdf(
    subject: str,
    grade: str,
    medium: str,
    chapter_id: str,
    start_id: Optional[int] = None,
    end_id: Optional[int] = None
):
    """
    Fetches questions from the QBank and generates a PDF file.
    """
    # 1. Fetch questions from QBank (or specific subject QBank)
    target_service = "general_qbank"
    if subject:
         # Try to find a specific service
        potential_service = f"{subject.lower()}_qbank"
        if potential_service in SERVICE_REGISTRY and SERVICE_REGISTRY[potential_service]:
            target_service = potential_service
            
    target_url = get_service_url(target_service)
    
    async with httpx.AsyncClient() as client:
        try:
            params = {
                "subject": subject,
                "grade": grade,
                "medium": medium,
                "chapter_id": chapter_id
            }
            if start_id:
                params["start_id"] = start_id
            if end_id:
                params["end_id"] = end_id
                
            print(f"Fetching questions from {target_url} with params {params}")
            response = await client.get(f"{target_url}/questions", params=params)
                
            print(f"Fetching questions from {target_url} with params {params}")
            response = await client.get(f"{target_url}/questions", params=params)
            response.raise_for_status()
            questions_data = response.json()
            
            # Convert back to objects
            questions = [GeneratedQuestion(**q) for q in questions_data]
            
            if not questions:
                # Return empty PDF or error? Error is better to inform user.
                raise HTTPException(status_code=404, detail="No questions found in the specified range.")
            
            # 2. Generate PDF
            pdf_buffer = generate_question_pdf(questions)
            
            # 3. Stream Response
            filename = f"questions_{subject}_{chapter_id}.pdf"
            return StreamingResponse(
                pdf_buffer, 
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        except httpx.RequestError as exc:
            raise HTTPException(status_code=503, detail=f"Service unreachable ({target_url}): {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)

@app.get("/questions", response_model=List[GeneratedQuestion], tags=["QBank"], summary="List Questions")
async def list_questions(
    medium: Optional[str] = None, 
    subject: Optional[str] = None
):
    """
    Retrieves a list of questions from the appropriate QBank service.
    """
    # Dynamic Lookup
    target_service = "general_qbank"
    
    if subject:
        # Try to find a specific service for this subject
        potential_service = f"{subject.lower()}_qbank"
        if potential_service in SERVICE_REGISTRY and SERVICE_REGISTRY[potential_service]:
            target_service = potential_service
        else:
            print(f"Warning: No dedicated service found for '{subject}', falling back to general_qbank.")
    
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

@app.post("/generate", response_model=List[GeneratedQuestion], tags=["Generator"], summary="Generate Questions")
async def generate_questions(content: SyllabusContent):
    """
    Triggers question generation based on syllabus content.
    """
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
            raise HTTPException(status_code=503, detail=f"Service unreachable ({target_url}): {exc}")
        except httpx.HTTPStatusError as exc:
            raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)



@app.post("/generate/pdf", response_model=List[GeneratedQuestion])
async def generate_questions_from_pdf(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: str = Form(...),
    medium: str = Form(...),
    chapter_id: str = Form(...),
    chapter_name: str = Form(...),
    generation_type: str = Form("general"),
):
    print(f"Received PDF upload for {subject} - {chapter_name} ({generation_type})")
    try:
        file_content = await file.read()
        text = extract_text_from_pdf(file_content)
        
        if not text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
        print(f"Extracted {len(text)} chars from PDF")
        
        # Chunk the text to avoid token limits
        chunks = chunk_text(text, max_chars=30000) # approx 7-8k tokens
        print(f"Split into {len(chunks)} chunks")
        
        all_questions = []
        target_url = get_service_url("generator")
        print(f"Routing PDF generation requests to: {target_url}") 
        
        async with httpx.AsyncClient() as client:
            for i, chunk in enumerate(chunks):
                print(f"Processing chunk {i+1}/{len(chunks)} ({len(chunk)} chars)...")
                
                # Create content object for this chunk
                content = SyllabusContent(
                    subject=subject,
                    grade=grade,
                    medium=medium,
                    chapter_id=chapter_id,
                    chapter_name=chapter_name,
                    content=chunk,
                    generation_type=generation_type
                )
                
                try:
                    # Forward the request body
                    response = await client.post(
                        f"{target_url}/generate", 
                        json=content.model_dump(),
                        timeout=120.0 
                    )
                    response.raise_for_status()
                    questions = response.json()
                    print(f"Got {len(questions)} questions from chunk {i+1}")
                    
                    # Convert dicts back to objects to ensure structure (optional but good practice)
                    # For now just extend the list
                    all_questions.extend(questions)
                    
                except httpx.RequestError as exc:
                    print(f"Error processing chunk {i+1}: {exc}")
                    # Decide if we want to fail completely or continue. 
                    # Failing completely is probably safer for now to avoid partial results masquerading as full success?
                    # But for large docs, partial might be better. Let's fail for now as requested by user effectively.
                    raise HTTPException(status_code=503, detail=f"Generation service unreachable during chunk {i+1}: {exc}")
                except httpx.HTTPStatusError as exc:
                    print(f"Error processing chunk {i+1}: {exc.response.text}")
                    raise HTTPException(status_code=exc.response.status_code, detail=f"Error in chunk {i+1}: {exc.response.text}")
                    
        return all_questions

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error processing PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))
