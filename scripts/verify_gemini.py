import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

try:
    from app.services.generator import GeneratorService
    from app.models.question import SyllabusContent
except ImportError:
    from src.app.services.generator import GeneratorService
    from src.app.models.question import SyllabusContent

def test_gemini_direct():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    print(f"Checking API Key... {'Found' if api_key else 'MISSING'}")
    
    if not api_key:
        print("ERROR: Please set GOOGLE_API_KEY in .env file")
        return

    print("Initializing GeneratorService...")
    generator = GeneratorService()

    # Including a concept likely to trigger a chemical formula in explanation
    content = SyllabusContent(
        subject="Science",
        grade="10",
        medium="English",
        content="Photosynthesis is the process used by plants to convert light energy into chemical energy. The chemical formula involves CO2 and H2O converting to glucose and oxygen."
    )

    print("\n--- Sending Request to Gemini ---")
    questions = generator.generate_questions(content)
    
    print("\n--- Result ---")
    if questions:
        print(f"SUCCESS: Generated {len(questions)} items.")
        for q in questions:
            print(f"\n[{q.question_type.upper()}] {q.question_text}")
            print(f"   Options: {q.options}")
            print(f"   Answer: {q.answer}")
            print(f"   Explanation: {q.explanation}")
    else:
        print("FAILURE: No items returned.")

if __name__ == "__main__":
    test_gemini_direct()
