from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import UserCreate, UserLogin, Token, UserResponse
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.core.database import get_database
from app.services.email import send_verification_email, send_welcome_email
from app.core.config import settings
from datetime import datetime, timedelta
from bson import ObjectId
import secrets

router = APIRouter()
security = HTTPBearer()


# HELPER FUNCTIONS
def generate_verification_token() -> str:
    """Generate secure verification token"""
    return secrets.token_urlsafe(32)


def create_trial_dates():
    """Create trial start and end dates (3 days)"""
    now = datetime.utcnow()
    return {
        "trial_start_date": now,
        "trial_end_date": now + timedelta(days=3)
    }

# REGISTER (WITH EMAIL VERIFICATION)
@router.post("/register", response_model=dict)
async def register(user: UserCreate, background_tasks: BackgroundTasks):
    """Register new user and send verification email"""
    
    db = get_database()
    users_collection = db.users
    
    # Check if user already exists
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    existing_username = users_collection.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Generate verification token
    verification_token = generate_verification_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Create trial dates
    trial_dates = create_trial_dates()
    
    # Hash password
    hashed_pwd = get_password_hash(user.password)
    
    # Create user document
    user_doc = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_pwd,
        "level": user.level,
        "profile_picture": None,
        "bio": None,
        "created_at": datetime.utcnow(),
        
        # Email verification
        "email_verified": False,
        "verification_token": verification_token,
        "verification_token_expires": verification_expires,
        
        # Trial & Subscription
        "subscription_status": "trial",
        "subscription_provider": None,
        "subscription_id": None,
        "subscription_plan": None,
        "trial_start_date": trial_dates["trial_start_date"],
        "trial_end_date": trial_dates["trial_end_date"],
        
        # Usage tracking
        "chat_messages_used": 0,
        "essays_graded": 0,
        "quizzes_taken": 0,
        
        # Payment IDs
        "stripe_customer_id": None,
        "paystack_customer_code": None
    }
    
    # Insert user
    result = users_collection.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    # Create verification URL
    verification_url = f"{settings.FRONTEND_URL}/verify-email.html?token={verification_token}"
    
    # Send verification email in background
    background_tasks.add_task(
        send_verification_email,
        user.email,
        verification_url,
        user.username
    )
    
    return {
        "message": "Registration successful! Please check your email to verify your account.",
        "email": user.email,
        "trial_days": 3
    }

# VERIFY EMAIL
@router.get("/verify-email/{token}")
async def verify_email(token: str, background_tasks: BackgroundTasks):
    """Verify user email with token"""
    
    db = get_database()
    users_collection = db.users
    
    # Find user with this token
    user = users_collection.find_one({
        "verification_token": token,
        "verification_token_expires": {"$gt": datetime.utcnow()}
    })
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired verification token"
        )
    
    # Check if already verified
    if user.get("email_verified"):
        raise HTTPException(
            status_code=400,
            detail="Email already verified"
        )
    
    # Update user - mark as verified
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "email_verified": True,
                "verification_token": None,
                "verification_token_expires": None
            }
        }
    )
    
    # Send welcome email in background
    background_tasks.add_task(
        send_welcome_email,
        user["email"],
        user["username"]
    )
    
    return {
        "message": "Email verified successfully! You can now log in.",
        "email_verified": True
    }

#Resend Email Verification 
@router.post("/resend-verification")
async def resend_verification(email: str, background_tasks: BackgroundTasks):
    """Resend verification email"""
    
    db = get_database()
    users_collection = db.users
    
    # Find user
    user = users_collection.find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get("email_verified"):
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new token
    verification_token = generate_verification_token()
    verification_expires = datetime.utcnow() + timedelta(hours=24)
    
    # Update user
    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "verification_token": verification_token,
                "verification_token_expires": verification_expires
            }
        }
    )
    
    # Create verification URL
    verification_url = f"{settings.FRONTEND_URL}/verify-email.html?token={verification_token}"
    
    # Send email in background
    background_tasks.add_task(
        send_verification_email,
        email,
        verification_url,
        user["username"]
    )
    
    return {
        "message": "Verification email sent! Please check your inbox.",
        "email": email
    }

#Login
@router.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login user - must have verified email"""
    
    db = get_database()
    users_collection = db.users
    
    # Find user
    db_user = users_collection.find_one({"email": user.email})
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Verify password
    if not verify_password(user.password, db_user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check email verification
    if not db_user.get("email_verified", False):
        raise HTTPException(
            status_code=403,
            detail="Please verify your email before logging in. Check your inbox for the verification link."
        )
    
    # Check if trial expired and no subscription
    if db_user.get("trial_end_date"):
        if datetime.utcnow() > db_user["trial_end_date"]:
            if db_user.get("subscription_status") != "active":
                # Trial expired, update status
                users_collection.update_one(
                    {"_id": db_user["_id"]},
                    {"$set": {"subscription_status": "expired"}}
                )
                db_user["subscription_status"] = "expired"
    
    # Generate tokens
    user_id = str(db_user["_id"])
    access_token = create_access_token({"sub": user_id})
    refresh_token = create_refresh_token({"sub": user_id})
    
    # Create response
    user_response = UserResponse(
        id=user_id,
        username=db_user["username"],
        email=db_user["email"],
        level=db_user.get("level", "B1"),
        profile_picture=db_user.get("profile_picture"),
        bio=db_user.get("bio"),
        created_at=db_user.get("created_at", datetime.utcnow()),
        email_verified=db_user.get("email_verified", False),
        subscription_status=db_user.get("subscription_status", "trial"),
        trial_end_date=db_user.get("trial_end_date")
    )
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user_response
    )

# GET CURRENT USER
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user_id = payload.get("sub")
    
    db = get_database()
    users_collection = db.users
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current user info"""
    
    return UserResponse(
        id=str(current_user["_id"]),
        username=current_user["username"],
        email=current_user["email"],
        level=current_user.get("level", "B1"),
        profile_picture=current_user.get("profile_picture"),
        bio=current_user.get("bio"),
        created_at=current_user.get("created_at", datetime.utcnow()),
        email_verified=current_user.get("email_verified", False),
        subscription_status=current_user.get("subscription_status", "trial"),
        trial_end_date=current_user.get("trial_end_date")
    )

# REFRESH TOKEN

@router.post("/refresh")
async def refresh_access_token(refresh_token: str):
    """Refresh access token using refresh token"""
    
    payload = decode_token(refresh_token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    user_id = payload.get("sub")
    
    # Generate new access token
    new_access_token = create_access_token({"sub": user_id})
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

# @router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
# async def register(user: UserCreate):
#     """Register a new user"""
#     db = get_database()
#     users_collection = db.users
    
#     # Check if user already exists
#     existing_user = users_collection.find_one({"email": user.email})
#     if existing_user:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Email already registered"
#         )
    
#     # Hash password
#     password_hash = get_password_hash(user.password)
    
#     # Create user document
#     user_doc = {
#         "email": user.email,
#         "password_hash": password_hash,
#         "learning_style": user.learning_style,
#         "level": user.level,
#         "refresh_token": None,
#         "created_at": datetime.utcnow()
#     }
    
#     # Insert into database
#     result = users_collection.insert_one(user_doc)
#     user_id = str(result.inserted_id)
    
#     # Create tokens
#     access_token = create_access_token(data={"sub": user_id})
#     refresh_token = create_refresh_token(data={"sub": user_id})
    
#     # Update refresh token in database
#     users_collection.update_one(
#         {"_id": result.inserted_id},
#         {"$set": {"refresh_token": refresh_token}}
#     )
    
#     # Prepare response
#     user_response = UserResponse(
#         id=user_id,
#         email=user.email,
#         learning_style=user.learning_style,
#         level=user.level,
#         created_at=user_doc["created_at"]
#     )
    
#     return Token(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         user=user_response
#     )

# @router.post("/login", response_model=Token)
# async def login(credentials: UserLogin):
#     """Login user"""
#     db = get_database()
#     users_collection = db.users
    
#     # Find user by email
#     user = users_collection.find_one({"email": credentials.email})
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password"
#         )
    
#     # Verify password
#     if not verify_password(credentials.password, user["password_hash"]):
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password"
#         )
    
#     # Create tokens
#     user_id = str(user["_id"])
#     access_token = create_access_token(data={"sub": user_id})
#     refresh_token = create_refresh_token(data={"sub": user_id})
    
#     # Update refresh token
#     users_collection.update_one(
#         {"_id": user["_id"]},
#         {"$set": {"refresh_token": refresh_token}}
#     )
    
#     # Prepare response
#     user_response = UserResponse(
#         id=user_id,
#         email=user["email"],
#         learning_style=user.get("learning_style", "patient_mentor"),
#         level=user.get("level", "A2"),
#         created_at=user["created_at"]
#     )
    
#     return Token(
#         access_token=access_token,
#         refresh_token=refresh_token,
#         user=user_response
#     )

# @router.post("/logout")
# async def logout(user_id: str):
#     """Logout user by invalidating refresh token"""
#     db = get_database()
#     users_collection = db.users
    
#     users_collection.update_one(
#         {"_id": ObjectId(user_id)},
#         {"$set": {"refresh_token": None}}
#     )
    
#     return {"message": "Logged out successfully"}