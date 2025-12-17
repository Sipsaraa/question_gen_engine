from abc import ABC, abstractmethod
from typing import List, Optional
from src.shared.models.question import SyllabusContent, GeneratedQuestion

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM Providers to ensure consistent interface.
    """
    
    @abstractmethod
    def generate_questions(self, content: SyllabusContent) -> List[GeneratedQuestion]:
        """
        Generates questions based on the provided syllabus content.
        
        Args:
            content (SyllabusContent): The content to generate questions from.
            
        Returns:
            List[GeneratedQuestion]: A list of generated questions.
        """
        pass
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns the name of the provider."""
        pass
