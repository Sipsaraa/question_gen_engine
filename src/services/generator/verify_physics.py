import os
import sys
import json
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from src.shared.models.question import SyllabusContent
from src.services.generator.service import GeneratorService

def test_physics_gen():
    load_dotenv()
    service = GeneratorService()
    
    # Physics Content Sample
    content = SyllabusContent(
        subject="Physics",
        grade="11",
        medium="English",
        chapter_id="PH01",
        chapter_name="Kinematics",
        content="""
        Kinematics is the branch of mechanics that describes the motion of points, bodies (objects), and systems of bodies (groups of objects) without considering the forces that cause them to move.
        Equations of motion: v = u + at, s = ut + 0.5at^2, v^2 = u^2 + 2as.
        Projectile motion occurs when an object is thrown into the air and is subject only to gravity.
        """,
        generation_type="physics"
    )
    
    print("Testing Physics Generation...")
    print(f"Providers loaded: {[p.provider_name for p in service.providers]}")
    
    # Force Groq only for this test if available, to test the prompt specific to Groq
    # (Optional: modify service locally or just let the loop run, usually Gemini goes first)
    # Let's just run the standard generation which tries Gemini then Groq.
    
    questions = service.generate_questions(content)
    
    print(f"\nGenerated {len(questions)} questions.")
    if questions:
        print(f"First Question: {questions[0].question_text}")
        print(f"Explanation: {questions[0].explanation}")
    else:
        print("No questions generated.")

if __name__ == "__main__":
    test_physics_gen()
