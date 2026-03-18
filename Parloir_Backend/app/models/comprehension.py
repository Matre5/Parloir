from pydantic import BaseModel
from typing import Optional, List

class Article(BaseModel):
    id: str
    title: str
    content: str
    image_url: Optional[str] = None
    source: str
    difficulty: str  # A2, B1, B2
    date: str

class Question(BaseModel):
    id: str
    question: str
    type: str  # "multiple_choice", "true_false", "short_answer"
    options: Optional[List[str]] = None  # For multiple choice
    correct_answer: str

class Answer(BaseModel):
    question_id: str
    user_answer: str

class ComprehensionResponse(BaseModel):
    question_id: str
    is_correct: bool
    explanation: str
    correct_answer: str

class ReadingSession(BaseModel):
    id: str
    article_id: str
    article_title: str
    questions: List[Question]
    user_answers: List[Answer]
    score: int
    total_questions: int
    completed_at: str