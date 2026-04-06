from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    hashed_password: str
    level: str = "B1"
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    created_at: Optional[datetime] = None
    
    # Email Verification (NEW!)
    email_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    
    # Trial & Subscription (NEW!)
    subscription_status: str = "trial"  # trial, active, expired, cancelled
    subscription_provider: Optional[str] = None  # stripe, paystack
    subscription_id: Optional[str] = None
    subscription_plan: Optional[str] = None  # monthly, yearly
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    
    # Usage Tracking (NEW!)
    chat_messages_used: int = 0
    essays_graded: int = 0
    quizzes_taken: int = 0
    
    # Payment IDs (NEW!)
    stripe_customer_id: Optional[str] = None
    paystack_customer_code: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    username: str
    email: EmailStr
    level: str = "A2"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str
    password_hash: str
    refresh_token: Optional[str] = None
    created_at: datetime

class UserResponse(UserBase):
    id: str
    created_at: datetime
    username: str
    email: str
    level: str
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    email_verified: bool
    subscription_status: str
    trial_end_date: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    level: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
