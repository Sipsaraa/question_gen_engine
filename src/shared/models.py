from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class SyllabusContent(BaseModel):
    subject: str
    grade: str
    medium: str
    chapter_id: str
    chapter_name: str
    content: str
    generation_type: str = "general"


class GeneratedQuestion(BaseModel):
    subject: str
    grade: str
    medium: str
    chapter_id: str
    chapter_name: str

    question_type: str  # 'fill_in_the_blank', 'mcq', or 'structured'
    question_text: str

    # JSON strings for storage
    options: str = Field(default="[]")
    answer: str = Field(default="")

    explanation: Optional[str] = None


class QuestionType(str, Enum):
    MCQ = "mcq"
    FILL_IN_THE_BLANK = "fill_in_the_blank"
    STRUCTURED = "structured"


class Question(BaseModel):
    type: QuestionType = Field(description="The type of the question.")
    question_text: str = Field(
        description=(
            "The actual question text. For fill-in-the-blank, use {0}, "
            "{1} placeholders."
        )
    )
    options: List[str] = Field(
        description=(
            "List of options. For MCQs, these are the choices. "
            "For fill-in-the-blank, these are words to choose from."
        )
    )
    answer: List[str] = Field(
        description=(
            "The correct answer(s). For MCQs, a single string in a list. "
            "For fill-in-the-blank, the ordered list of correct words."
        )
    )
    explanation: str = Field(
        description=(
            "A detailed theoretical explanation of WHY the answer is correct, "
            "using MDX format and LaTeX for math if needed."
        )
    )


class QuestionBank(BaseModel):
    questions: List[Question]
