from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from typing import Optional

class EssayPrompt(BaseModel):
    id: str
    title: str
    description: str
    category: str
    min_words: int
    level: str
    date: Optional[str] = None
    is_current_level: Optional[bool] = False

class EssaySubmission(BaseModel):
    prompt_id: str
    content: str

class GradingCriteria(BaseModel):
    score: int  # 0-100
    feedback: str
    examples: Optional[List[str]] = None

class EssayGrade(BaseModel):
    overall_score: int  # 0-100
    grammar: GradingCriteria
    vocabulary: GradingCriteria
    structure: GradingCriteria
    coherence: GradingCriteria
    suggestions: List[str]
    strengths: List[str]

class EssayResponse(BaseModel):
    id: str
    prompt_id: str
    prompt_title: str
    content: str
    grade: EssayGrade
    word_count: int
    submitted_at: str
    user_level: str