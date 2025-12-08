from fastapi.testclient import TestClient
from unittest.mock import patch
from src.app.models.question import GeneratedQuestion

def test_language_filtering(client: TestClient):
    # Seed DB directly
    from src.app.core.database import get_session
    # We can't easily access the session used by the client dependency override directly here 
    # unless we use the same session fixture pattern. 
    # But checking conftest.py, client uses the session fixture.
    # So we can just POST to create data or mock the generator to create data.
    
    # Let's seed via the generate endpoint with a mock to ensure flow works
    with patch("src.app.services.generator.GeneratorService.generate_questions") as mock_generate:
        # Mock Sinhala Questions
        mock_generate.return_value = [
            GeneratedQuestion(
                subject="History", grade="10", medium="Sinhala",
                chapter_id="5", chapter_name="Kandy Era",
                question_type="mcq",
                question_text="Sinhala Question 1",
                options="[]", answer='""'
            )
        ]
        
        client.post("/generate", json={
            "subject": "History", "grade": "10", "medium": "Sinhala", 
            "chapter_id": "5", "chapter_name": "Kandy Era", "content": "..."
        })
        
        # Mock English Questions
        mock_generate.return_value = [
            GeneratedQuestion(
                subject="History", grade="10", medium="English",
                chapter_id="5", chapter_name="Kandy Era",
                question_type="mcq",
                question_text="English Question 1",
                options="[]", answer='""'
            )
        ]
        
        client.post("/generate", json={
            "subject": "History", "grade": "10", "medium": "English",
            "chapter_id": "5", "chapter_name": "Kandy Era", "content": "..."
        })
    
    # Test Filtering
    # 1. Get Sinhala
    response_si = client.get("/questions?medium=Sinhala")
    assert response_si.status_code == 200
    data_si = response_si.json()
    assert len(data_si) == 1
    assert data_si[0]["medium"] == "Sinhala"
    assert data_si[0]["chapter_name"] == "Kandy Era"
    
    # 2. Get English
    response_en = client.get("/questions?medium=English")
    assert response_en.status_code == 200
    data_en = response_en.json()
    assert len(data_en) == 1
    assert data_en[0]["medium"] == "English"

    # 3. Get All (no filter)
    response_all = client.get("/questions")
    assert response_all.status_code == 200
    data_all = response_all.json()
    assert len(data_all) == 2
