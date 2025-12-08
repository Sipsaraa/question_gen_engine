import sys
import os

# Add the src structure to path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.app.services.generator import GeneratorService
from src.app.models.question import SyllabusContent

def main():
    print("Initializing Generator...")
    service = GeneratorService()
    
    content = SyllabusContent(
        subject="Physics",
        grade="10",
        medium="English",
        content="""
        Newton's second law of motion pertains to the behavior of objects for which all existing forces are not balanced. 
        The second law states that the acceleration of an object is dependent upon two variables - the net force acting upon the object and the mass of the object. 
        The acceleration of an object depends directly upon the net force acting upon the object, and inversely upon the mass of the object. 
        As the force acting upon an object is increased, the acceleration of the object is increased. 
        As the mass of an object is increased, the acceleration of the object is decreased.
        Equation: F = ma
        """
    )
    
    print("Generating Questions...")
    questions = service.generate_questions(content)
    
    print(f"\nGenerated {len(questions)} questions:\n")
    for q in questions:
        print(f"[{q.question_type.upper()}] {q.question_text}")
        print(f"Options: {q.options}")
        print(f"Answer: {q.answer}")
        print(f"Explanation: {q.explanation}")
        print("-" * 50)

if __name__ == "__main__":
    main()
