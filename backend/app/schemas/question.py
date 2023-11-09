from typing import List, Optional
from pydantic import BaseModel

class QuestionCreate(BaseModel):
    text: str
    category_id: Optional[int]

class OptionCreate(BaseModel):
    answer: str
    is_correct: bool

class QuizQuestionCreate(BaseModel):
    question: QuestionCreate
    options: List[OptionCreate]