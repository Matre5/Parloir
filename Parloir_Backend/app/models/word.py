from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WordCreate(BaseModel):
    word: str
    translation: str
    context: Optional[str] = None  # Sentence where they saw it
    source: str = "manual"  # "chat", "translate", "manual"
    
class WordUpdate(BaseModel):
    status: Optional[str] = None  # "learning", "practicing", "learned"
    notes: Optional[str] = None

class WordResponse(BaseModel):
    id: str
    word: str
    translation: str
    context: Optional[str] = None
    source: str
    status: str
    notes: Optional[str] = None
    created_at: str
    updated_at: str