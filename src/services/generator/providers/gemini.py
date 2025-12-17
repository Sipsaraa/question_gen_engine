import os
import json
import google.generativeai as genai
from typing import List
from src.services.generator.providers.base import BaseLLMProvider
from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.models.generation_schema import QuestionBank

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            print("WARNING: GOOGLE_API_KEY not found for GeminiProvider.")
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.5-flash')

    @property
    def provider_name(self) -> str:
        return "Gemini"

    def generate_questions(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        if not self.api_key:
            raise ValueError("Google API Key is missing")

        prompt = self._build_prompt(content)
        
        try:
            print(f"DEBUG: Generating content ({content.subject}) with Gemini...")
            
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
                # We might want to raise this so the fallback can handle it if it's a parsing error?
                # For now, let's treat parsing error as a failure to generate valid questions.
                raise parse_error
            
            return self._convert_to_generated_questions(question_bank, content)

        except Exception as e:
            print(f"Error in GeminiProvider: {e}")
            raise e

    def _build_prompt(self, content: SyllabusContent) -> str:
        base_prompt = f"""
        You are an expert educational content creator.
        Analyze the following syllabus content and generate a 'QuestionBank' of items.
        
        Subject: {content.subject}
        Grade: {content.grade}
        Medium: {content.medium} (GENERATE CONTENT IN THIS LANGUAGE)
        
        Content:
        "{content.content}"
        """
        
        # Specific instructions based on generation type
        if content.generation_type == "physics":
            instructions = """
            Requirements (PHYSICS MODE):
            1. GENERATE AT LEAST 20 QUESTIONS.
            2. FOCUS ON CONCEPTUAL UNDERSTANDING and PHYSICAL ACCURACY.
            3. Questions should test application of concepts, not just memory.
            4. For numerical problems, ensure values are realistic and answers are physically meaningful.
            5. EXPLANATIONS MUST BE DEEP, rigorous, and explain the 'Physics' behind the answer.
            6. Create a mix of 'mcq', 'fill_in_the_blank', and 'structured' questions.
            7. CRITICAL (FORMATTING): 
               - Write ALL mathematical expressions and units in LaTeX enclosed in single `$` signs.
               - Example: $9.8 m/s^2$, $v = u + at$, $30^\circ$, $10^{-19} C$.
               - NEVER write units like m/s^2 plain. ALWAYS use $m/s^2$.
            """
        else:
            instructions = """
            Requirements:
            1. GENERATE AS MANY QUESTIONS AS POSSIBLE to cover every concept.
            2. create a mix of 'mcq' and 'fill_in_the_blank' questions.
            """

        common_instructions = """
        Common Rules:
        1. For 'fill_in_the_blank':
           - Use `{{0}}`, `{{1}}` for blanks in the `question_text`.
           - Provide `options` (including distractors) as a list of strings.
           - `answer` should be the list of correct words in order.
        2. For 'mcq':
           - `options` is the list of choices.
           - `answer` is a list containing the single correct option text.
        3. CRITICAL: For ALL items, provide a detailed `explanation`:
           - It MUST contain a theoretical explanation of WHY the answer is correct.
           - Use MDX format.
           - Use Single `$` for inline LaTeX equations (e.g. $E=mc^2$).
        """
        
        return base_prompt + instructions + common_instructions

    def _convert_to_generated_questions(self, question_bank: QuestionBank, content: SyllabusContent) -> List[GeneratedQuestion]:
        results = []
        for item in question_bank.questions:
            options_str = json.dumps(item.options)
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
