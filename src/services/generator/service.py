from src.services.generator.providers.groq import GroqProvider

import os
from typing import List
from dotenv import load_dotenv
from src.shared.models import SyllabusContent, GeneratedQuestion

# Load env vars
load_dotenv()


class GeneratorService:
    def __init__(self):
        self.providers = []

        # Load generator preferences from env
        primary = os.getenv("PRIMARY_GENERATOR", "groq").lower()
        fallback = os.getenv("FALLBACK_GENERATOR", "groq").lower()

        # Define available providers
        available_configs = {
            "groq": {
                "class": GroqProvider,
                "key_env": "GROQ_API_KEY",
                "display_name": "Groq"
            }
        }

        # Determine the order based on env vars
        requested_order = [primary, fallback]
        seen_providers = set()

        for provider_id in requested_order:
            if (provider_id not in available_configs or
                    provider_id in seen_providers):
                continue

            config = available_configs[provider_id]
            api_key = os.getenv(config["key_env"])

            if api_key:
                print(f"Initializing {config['display_name']} provider...")
                self.providers.append(config["class"](api_key=api_key))
                seen_providers.add(provider_id)
            else:
                print(
                    f"Skipping {config['display_name']}",
                    f"provider: {config['key_env']} not found."
                )

        if not self.providers:
            print(
                "CRITICAL WARNING: No LLM providers configured.",
                "Check GOOGLE_API_KEY and GROQ_API_KEY."
            )

    def generate_questions(
        self,
        content: SyllabusContent
    ) -> List[GeneratedQuestion]:
        """
        Attempts to generate questions using configured providers in order.
        Falls back to the next provider if the current one fails.
        """
        errors = []

        for provider in self.providers:
            try:
                print(
                    "Attempting generation with provider:",
                    provider.provider_name
                )
                result = provider.generate_questions(content)
                if result:
                    print(
                        "Successfully generated",
                        len(result),
                        "questions with",
                        provider.provider_name
                    )
                    return result
            except Exception as e:
                error_msg = (
                    f"Provider {provider.provider_name} failed: {str(e)}"
                )
                print(error_msg)
                errors.append(error_msg)
                # Continue to next provider

        # If we get here, all providers failed
        print("All providers failed to generate questions.")
        for err in errors:
            print(f"- {err}")

        return []
