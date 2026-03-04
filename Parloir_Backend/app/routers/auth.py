from fastapi import APIRouter, HTTPException, status
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.core.database import get_database
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token
from datetime import datetime
from bson import ObjectId

router = APIRouter()

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user"""
    db = get_database()
    users_collection = db.users
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = get_password_hash(user.password)
    
    # Create user document
    user_doc = {
        "email": user.email,
        "password_hash": password_hash,
        "learning_style": user.learning_style,
        "level": user.level,
        "refresh_token": None,
        "created_at": datetime.utcnow()
    }
    
    # Insert into database
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Update refresh token in database
    users_collection.update_one(
        {"_id": result.inserted_id},
        {"$set": {"refresh_token": refresh_token}}
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user.email,
        learning_style=user.learning_style,
        level=user.level,
        created_at=user_doc["created_at"]
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    db = get_database()
    users_collection = db.users
    
    # Find user by email
    user = users_collection.find_one({"email": credentials.email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create tokens
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    
    # Update refresh token
    users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token": refresh_token}}
    )
    
    # Prepare response
    user_response = UserResponse(
        id=user_id,
        email=user["email"],
        learning_style=user.get("learning_style", "patient_mentor"),
        level=user.get("level", "A2"),
        created_at=user["created_at"]
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

@router.post("/logout")
async def logout(user_id: str):
    """Logout user by invalidating refresh token"""
    db = get_database()
    users_collection = db.users
    
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"refresh_token": None}}
    )
    
    return {"message": "Logged out successfully"}