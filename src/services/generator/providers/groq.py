import os
import json
import time
from typing import List
from groq import Groq
from src.services.generator.providers.base import BaseLLMProvider
from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.shared.models.generation_schema import QuestionBank
from src.shared.utils.text_utils import chunk_text
from src.services.generator.prompts import (
    SYSTEM_MESSAGE,
    BASE_PROMPT_TEMPLATE,
    PHYSICS_INSTRUCTIONS,
    GENERAL_INSTRUCTIONS,
    COMMON_INSTRUCTIONS
)


class GroqProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: str = None,
        model: str = "llama-3.3-70b-versatile"
    ):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.model_name = model
        if not self.api_key:
            print("WARNING: GROQ_API_KEY not found for GroqProvider.")
        else:
            self.client = Groq(api_key=self.api_key)

    @property
    def provider_name(self) -> str:
        return "Groq"

    def generate_questions(
        self,
        content: SyllabusContent
    ) -> List[GeneratedQuestion]:
        if not self.api_key:
            raise ValueError("Groq API Key is missing")

        # Check content length and chunk if necessary
        # We use smaller chunks to avoid token limits on Groq
        MAX_CHARS_PER_CHUNK = 8000

        if len(content.content) > MAX_CHARS_PER_CHUNK:
            print(
                "DEBUG: Content too large (",
                len(content.content),
                " chars). Chunking..."
            )
            chunks = chunk_text(content.content, max_chars=MAX_CHARS_PER_CHUNK)
            all_questions = []

            for i, chunk_text_str in enumerate(chunks):
                print(
                    "DEBUG: Processing chunk ",
                    i + 1,
                    "/",
                    len(chunks),
                    "..."
                )

                # Create a temporary content object for this chunk
                chunk_content = content.model_copy(
                    update={"content": chunk_text_str})

                try:
                    questions = self._generate_single_batch(chunk_content)
                    all_questions.extend(questions)

                    # Throttle if not the last chunk
                    if i < len(chunks) - 1:
                        print(
                            "DEBUG: Sleeping 60s to respect Rate Limit...")
                        time.sleep(60)

                except Exception as e:
                    print(
                        "Error processing chunk ",
                        i + 1,
                        ": ",
                        e
                    )
                    continue

            return all_questions
        else:
            return self._generate_single_batch(content)

    def _generate_single_batch(
        self,
        content: SyllabusContent
    ) -> List[GeneratedQuestion]:
        prompt = self._build_prompt(content)

        try:
            print(
                "DEBUG: Generating content (",
                content.subject,
                "- ",
                content.generation_type,
                ") with Groq (",
                self.model_name,
                ") ..."
            )

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_MESSAGE
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_tokens=2048,
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
        base_prompt = BASE_PROMPT_TEMPLATE.format(
            subject=content.subject,
            grade=content.grade,
            medium=content.medium,
            content=content.content
        )

        if content.generation_type == "physics":
            instructions = PHYSICS_INSTRUCTIONS
        else:
            instructions = GENERAL_INSTRUCTIONS

        return base_prompt + instructions + COMMON_INSTRUCTIONS

    def _convert_to_generated_questions(
        self,
        question_bank: QuestionBank,
        content: SyllabusContent
    ) -> List[GeneratedQuestion]:
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
