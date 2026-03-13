from pydantic import BaseModel
from typing import Optional

class TranslateRequest(BaseModel):
    text: str
    source_lang: str = "auto"  # "auto", "fr", "en"
    target_lang: str  # "fr" or "en"
    
class TranslateResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    pronunciation: Optional[str] = None