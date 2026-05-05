from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Base user fields shared across models
class UserBase(BaseModel):
    username: str
    email: EmailStr
    level: str = "B1"

# For creating a new user (registration)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(..., min_length=6)
    level: str = "B1"

# For login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Full user model (what's stored in database)
class UserInDB(BaseModel):
    id: Optional[str] = None
    username: str
    email: EmailStr
    hashed_password: str
    level: str = "B1"
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    
    # Email Verification
    email_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires: Optional[datetime] = None
    
    # Trial & Subscription
    subscription_status: str = "trial"
    subscription_provider: Optional[str] = None
    subscription_id: Optional[str] = None
    subscription_plan: Optional[str] = None
    trial_start_date: Optional[datetime] = None
    trial_end_date: Optional[datetime] = None
    
    # Usage Tracking
    chat_messages_used: int = 0
    essays_graded: int = 0
    quizzes_taken: int = 0
    
    # Payment IDs
    stripe_customer_id: Optional[str] = None
    paystack_customer_code: Optional[str] = None

# For API responses (what user sees)
class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    level: str
    profile_picture: Optional[str] = None
    bio: Optional[str] = None
    created_at: datetime
    email_verified: bool
    subscription_status: str
    trial_end_date: Optional[datetime] = None
    current_streak: int = 0
    longest_streak: int = 0

# For updating user profile
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    level: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None

# Auth token response
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
    