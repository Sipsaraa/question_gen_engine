import os
import json
import google.generativeai as genai
from typing import List
from dotenv import load_dotenv
from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.models.generation_schema import QuestionBank

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
        Uses Gemini to extract questions (Fill-blanks & MCQ) with Explanations
        using structured output.
        """
        prompt = f"""
        You are an expert educational content creator.
        Analyze the following syllabus content and generate a 'QuestionBank' of items.
        
        Subject: {content.subject}
        Grade: {content.grade}
        Medium: {content.medium} (GENERATE CONTENT IN THIS LANGUAGE)
        
        Content:
        "{content.content}"
        
        Requirements:
        1. create a mix of 'mcq' and 'fill_in_the_blank' questions.
        2. For 'fill_in_the_blank':
           - Use `{{0}}`, `{{1}}` for blanks in the `question_text`.
           - Provide `options` (including distractors) as a list of strings.
           - `answer` should be the list of correct words in order, matching the placeholders.
        3. For 'mcq':
           - `options` is the list of choices.
           - `answer` is a list containing the single correct option text.
        4. CRITICAL: For ALL items, provide a detailed `explanation`:
           - It MUST contain a theoretical explanation of WHY the answer is correct.
           - Do NOT just cite the text. Explain the underlying concept or principle.
           - Use MDX format.
           - Use Single `$` for inline LaTeX equations if needed (e.g. $E=mc^2$).
        """
        
        try:
            print(f"DEBUG: Generating content ({content.subject}) with structured output...")
            
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "response_schema": QuestionBank,
                }
            )
            
            # Parse the structured response
            try:
                question_bank = QuestionBank.model_validate_json(response.text)
            except Exception as parse_error:
                print(f"Error parsing JSON from Gemini: {parse_error}")
                print(f"Raw response: {response.text}")
                return []
            
            results = []
            for item in question_bank.questions:
                # Convert list answer to the format expected by GeneratedQuestion (stringified json or string)
                # The prompt asks for answer as a list for schema consistency, but GeneratedQuestion might expect something else.
                # Looking at the original code:
                # option_str = json.dumps(item.get("options", []))
                # ans = item.get("answer") -> if list/dict dump, else str.
                
                # In our new schema:
                # options is List[str] -> dumps
                # answer is List[str] -> dumps (for consistency)
                
                options_str = json.dumps(item.options)
                
                # For MCQ, the original code expected a single string if it wasn't a list/dict.
                # However, to be cleaner, we will store everything as a JSON string if possible, 
                # or match the previous behavior.
                # Previous behavior: 
                # if isinstance(ans, (list, dict)): answer_str = json.dumps(ans) else: answer_str = str(ans)
                
                # Our new schema ALWAYS returns a list for answer.
                # So we can just dump it.
                answer_str = json.dumps(item.answer)

                results.append(GeneratedQuestion(
                    subject=content.subject,
                    grade=content.grade,
                    medium=content.medium,
                    chapter_id=content.chapter_id,
                    chapter_name=content.chapter_name,
                    question_type=item.type.value,
                    question_text=item.question_text,
                    options=options_str,
                    answer=answer_str,
                    explanation=item.explanation
                ))
            
            return results

        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            import traceback
            traceback.print_exc()
            return []
