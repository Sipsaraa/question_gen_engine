from typing import Optional
from sqlmodel import Field, SQLModel

class SyllabusContent(SQLModel):
    subject: str
    grade: str
    medium: str
    chapter_id: str
    chapter_name: str
    content: str

class GeneratedQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    subject: str
    grade: str
    grade: str
    medium: str
    chapter_id: str
    chapter_name: str
    
    question_type: str # 'fill_in_the_blank' or 'mcq'
    question_text: str 
    
    # JSON strings for storage
    options: str = Field(default="[]") 
    answer: str = Field(default="")
    
    explanation: Optional[str] = None
