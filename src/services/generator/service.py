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

import os
import time
from typing import List
from dotenv import load_dotenv
from src.shared.models.question import SyllabusContent, GeneratedQuestion
from src.services.generator.providers.gemini import GeminiProvider
from src.services.generator.providers.groq import GroqProvider

# Load env vars
load_dotenv()

class GeneratorService:
    def __init__(self):
        self.providers = []
        
        # Initialize providers
        # 1. Gemini (Primary)
        gemini_key = os.getenv("GOOGLE_API_KEY")
        if gemini_key:
            self.providers.append(GeminiProvider(api_key=gemini_key))
        
        # 2. Groq (Fallback) - Great for speed and often has generous free tiers
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            self.providers.append(GroqProvider(api_key=groq_key))
            
        if not self.providers:
            print("CRITICAL WARNING: No LLM providers configured. Check GOOGLE_API_KEY and GROQ_API_KEY.")

    def generate_questions(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        """
        Attempts to generate questions using configured providers in order.
        Falls back to the next provider if the current one fails.
        """
        errors = []
        
        for provider in self.providers:
            try:
                print(f"Attempting generation with provider: {provider.provider_name}")
                result = provider.generate_questions(content)
                if result:
                    print(f"Successfully generated {len(result)} questions with {provider.provider_name}")
                    return result
            except Exception as e:
                error_msg = f"Provider {provider.provider_name} failed: {str(e)}"
                print(error_msg)
                errors.append(error_msg)
                # Continue to next provider
                
        # If we get here, all providers failed
        print("All providers failed to generate questions.")
        for err in errors:
            print(f"- {err}")
            
        return []

