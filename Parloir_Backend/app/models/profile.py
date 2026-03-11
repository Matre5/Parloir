from pydantic import BaseModel
from typing import Optional

class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    learning_style: Optional[str] = None
    level: Optional[str] = None
    profile_picture: Optional[str] = None

class ProfileResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    learning_style: str
    level: str
    profile_picture: Optional[str] = None