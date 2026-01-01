import os
import json
import time
from typing import List, Optional
from groq import Groq
from src.services.generator.providers.base import BaseLLMProvider
from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.models.generation_schema import QuestionBank
from src.shared.utils.text_utils import chunk_text

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str = None, model: str = "qwen/qwen3-32b"):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found for GroqProvider.")
        else:
            self.client = Groq(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "Groq"

    def generate_questions(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        if not self.api_key:
            raise ValueError("Groq API Key is missing")

        # Check content length and chunk if necessary
        # 1 token approx 4 chars. Limit 6000 TPM. 
        # Safe limit: 4000 tokens -> ~16000 chars. 
        # We use 15000 chars to be safe including prompt overhead.
        MAX_CHARS_PER_CHUNK = 15000
        
        if len(content.content) > MAX_CHARS_PER_CHUNK:
            print(f"DEBUG: Content too large ({len(content.content)} chars). Chunking...")
            chunks = chunk_text(content.content, max_chars=MAX_CHARS_PER_CHUNK)
            all_questions = []
            
            for i, chunk_text_str in enumerate(chunks):
                print(f"DEBUG: Processing chunk {i+1}/{len(chunks)}...")
                
                # Create a temporary content object for this chunk
                chunk_content = content.model_copy(update={"content": chunk_text_str})
                
                try:
                    questions = self._generate_single_batch(chunk_content)
                    all_questions.extend(questions)
                    
                    # Throttle if not the last chunk
                    if i < len(chunks) - 1:
                        print("DEBUG: Sleeping 60s to respect Rate Limit (6000 TPM)...")
                        time.sleep(60)
                        
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {e}")
                    # Continue to next chunk or raise? 
                    # For now, let's log and continue to try getting partial results
                    continue
            
            return all_questions
        else:
             return self._generate_single_batch(content)

    def _generate_single_batch(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        prompt = self._build_prompt(content)
        
        try:
            print(f"DEBUG: Generating content ({content.subject}- {content.generation_type}) with Groq ({self.model_name})...")
            
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educational content creator. You must output a SINGLE valid JSON object. Do not wrap the output in a list."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=8192,
                top_p=1,
                stream=False,
                response_format={"type": "json_object"}
            )
            
            response_text = completion.choices[0].message.content
            
            # Parse the structured response
            try:
                question_bank = QuestionBank.model_validate_json(response_text)
            except Exception as parse_error:
                print(f"Error parsing JSON from Groq: {parse_error}")
                print(f"Raw response: {response_text}")
                raise parse_error
            
            return self._convert_to_generated_questions(question_bank, content)

        except Exception as e:
            print(f"Error in GroqProvider: {e}")
            raise e

    def _build_prompt(self, content: SyllabusContent) -> str:
        # Schema definition for Groq to ensure compliance
        schema_json = json.dumps(QuestionBank.model_json_schema(), indent=2)
        
        base_prompt = f"""
        Analyze the following syllabus content and generate a 'QuestionBank' of items in JSON format.
        
        Subject: {content.subject}
        Grade: {content.grade}
        Medium: {content.medium} (GENERATE CONTENT IN THIS LANGUAGE)
        
        Content:
        "{content.content}"
        """
        
        if content.generation_type == "physics":
            instructions = """
            Requirements (PHYSICS MODE):
            
            2. Questions MUST be physically accurate and test conceptual depth.
            3. Generate physics based questions with calculations.
            4. Include application-based problems with realistic values working out to meaningful answers.
            5. `explanation` must be detailed, citing physical laws or theorems.
            6. CRITICAL (FORMATTING): 
               - Write ALL mathematical expressions and units in LaTeX enclosed in single `$` signs.
               - Example: $9.8 m/s^2$, $v = u + at$, $30^\circ$.
               - NEVER write units like m/s^2 plain. ALWAYS use $m/s^2$.
            """
        else:
            instructions = """
            Requirements:
            1. GENERATE AS MANY QUESTIONS AS POSSIBLE to cover every concept.
            """
            
        common_instructions = f"""
        Common Rules:
        1. create a mix of 'mcq' and 'fill_in_the_blank' and 'structured' questions.
        2. AIM FOR MAXIMUM COVERAGE.
        3. For 'fill_in_the_blank': Use `{{0}}`, `{{1}}` placeholders. `answer` is list of correct words.
        4. For 'mcq': `answer` is list containing correct option text.
        5. For 'structured' (descriptive/essay):
           - `options` MUST be an empty list `[]`.
           - `answer` MUST be a list containing one string: the complete, detailed model answer/essay.
        6. 'explanation': MDX format, explain the concept.
        7. GENERATE AT LEAST 20 QUESTIONS. COMPULSORY.
        
        OUTPUT MUST BE VALID JSON MATCHING THIS SCHEMA:
        {schema_json}
        
        IMPORTANT: Return a SINGLE JSON OBJECT `{{ "questions": [...] }}`. Do NOT return a list `[...]`.
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
