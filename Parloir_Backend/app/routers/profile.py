from fastapi import APIRouter, HTTPException, Depends, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.profile import ProfileUpdate, ProfileResponse
from app.core.database import get_database
from app.core.security import decode_token
from app.core.config import settings
from bson import ObjectId
import cloudinary
import cloudinary.uploader

router = APIRouter()
security = HTTPBearer()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET
)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload.get("sub")

@router.get("/me", response_model=ProfileResponse)
async def get_profile(user_id: str = Depends(get_current_user)):
    db = get_database()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    print(f"DEBUG streak fields: {user.get('current_streak')} / {user.get('longest_streak')}")
    
    return ProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        learning_style=user.get("learning_style", "patient_mentor"),
        level=user.get("level", "A2"),
        profile_picture=user.get("profile_picture"),
        current_streak=user.get("current_streak", 0),
        longest_streak=user.get("longest_streak", 0),
    )

@router.put("/me", response_model=ProfileResponse)
async def update_profile(
    profile_update: ProfileUpdate,
    user_id: str = Depends(get_current_user)
):
    db = get_database()
    users_collection = db.users
    
    update_data = {}
    if profile_update.name is not None:
        update_data["name"] = profile_update.name
    if profile_update.learning_style is not None:
        update_data["learning_style"] = profile_update.learning_style
    if profile_update.level is not None:
        update_data["level"] = profile_update.level
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    result = users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    return ProfileResponse(
        id=str(user["_id"]),
        email=user["email"],
        name=user.get("name"),
        learning_style=user.get("learning_style", "patient_mentor"),
        level=user.get("level", "A2"),
        profile_picture=user.get("profile_picture"),
        current_streak=user.get("current_streak", 0),
        longest_streak=user.get("longest_streak", 0),
    )

@router.post("/upload-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")
    
    try:
        result = cloudinary.uploader.upload(
            contents,
            folder="parloir/profile_pictures",
            public_id=f"user_{user_id}",
            overwrite=True,
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto"},
                {"fetch_format": "auto"}
            ]
        )
        
        image_url = result["secure_url"]
        
        db = get_database()
        db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"profile_picture": image_url}}
        )
        
        return {"success": True, "url": image_url}
        
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")