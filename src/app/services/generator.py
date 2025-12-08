import os
import json
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
from ..models.question import SyllabusContent, GeneratedQuestion

# Load env vars
load_dotenv()

# Configure GenAI
API_KEY = os.getenv("GOOGLE_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

class GeneratorService:
    def __init__(self):
        if not API_KEY:
            # In a real app, use a logger
            print("WARNING: GOOGLE_API_KEY not found in environment variables.")
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def generate_questions(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        """
        Uses Gemini to extract questions (Fill-blanks & MCQ) with Explanations.
        """
        prompt = f"""
        You are an expert educational content creator.
        Analyze the following syllabus content and generate 'GeneratedQuestion' items.
        
        Subject: {content.subject}
        Grade: {content.grade}
        Medium: {content.medium}
        
        Content:
        "{content.content}"
        
        Generate a mix of:
        1. **Fill-in-the-blank**: 
           - Use `{{0}}`, `{{1}}` for blanks.
           - Provide `options` (distractors included) for the blanks.
           - `answer` should be the list of correct words in order.
        2. **Multiple Choice (MCQ)**:
           - Standard question.
           - `options` is a list of choices.
           - `answer` is the correct option text.

        For ALL items, provide an `explanation` field:
        - Format as **MDX (Markdown)**.
        - Explain *why* the answer is correct.
        - Use LaTeX for equations: enclosed in single `$` (e.g. $E=mc^2$).
        
        Output purely as a JSON ARRAY.
        """
        
        try:
            print(f"DEBUG: Generating content ({content.subject})...")
            response = self.model.generate_content(prompt)
            
            # Cleanup Potential Markdown formatting
            text = response.text.replace("```json", "").replace("```", "").strip()
            
            data = json.loads(text)
            
            results = []
            for item in data:
                options_str = json.dumps(item.get("options", []))
                
                ans = item.get("answer")
                if isinstance(ans, (list, dict)):
                    answer_str = json.dumps(ans)
                else:
                    answer_str = str(ans)

                results.append(GeneratedQuestion(
                    subject=content.subject,
                    grade=content.grade,
                    medium=content.medium,
                    question_type=item.get('question_type', 'unknown'),
                    question_text=item.get('question_text', ''),
                    options=options_str,
                    answer=answer_str,
                    explanation=item.get('explanation', "")
                ))
            
            return results

        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            import traceback
            traceback.print_exc()
            return []
