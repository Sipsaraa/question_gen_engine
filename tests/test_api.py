from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from src.app.models.question import GeneratedQuestion

def test_health(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@patch("src.app.services.generator.GeneratorService.generate_questions")
def test_generate_questions(mock_generate, client: TestClient):
    # Mock LLM response
    mock_questions = [
        GeneratedQuestion(
            subject="Math", grade="10", medium="EN",
            chapter_id="1", chapter_name="Algebra",
            question_type="mcq",
            question_text="What is 2+2?",
            options='["3", "4", "5"]',
            answer='"4"',
            explanation="Basic arithmetic."
        )
    ]
    mock_generate.return_value = mock_questions

    payload = {
        "subject": "Math",
        "grade": "10",
        "medium": "EN",
        "chapter_id": "1",
        "chapter_name": "Algebra",
        "content": "Math syllabus content..."
    }
    
    response = client.post("/generate", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["question_text"] == "What is 2+2?"
    
    # Verify persistence check via list endpoint
    # Since we use the same session fixture, the post above should have saved it to our in-memory DB
    list_response = client.get("/questions")
    assert list_response.status_code == 200
    list_data = list_response.json()
    assert len(list_data) == 1
    assert list_data[0]["question_text"] == "What is 2+2?"
