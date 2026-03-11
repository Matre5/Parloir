from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.profile import ProfileUpdate, ProfileResponse
from app.core.database import get_database
from app.core.security import decode_token
from bson import ObjectId

router = APIRouter()
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")  # Return user_id

@router.get("/me", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user)):
    """Get current user's profile"""
    db = get_database()
    users_collection = db.users
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return ProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        learning_style=user.get("learning_style", "patient_mentor"),
        level=user.get("level", "A2")
    )

@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update current user's profile"""
    db = get_database()
    users_collection = db.users
    
    # Build update document (only include fields that were provided)
    update_data = {}
    if profile_update.name is not None:
        update_data["name"] = profile_update.name
    if profile_update.learning_style is not None:
        update_data["learning_style"] = profile_update.learning_style
    if profile_update.level is not None:
        update_data["level"] = profile_update.level
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    # Update user
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get updated user
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    return ProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        learning_style=user.get("learning_style", "patient_mentor"),
        level=user.get("level", "A2")
    )