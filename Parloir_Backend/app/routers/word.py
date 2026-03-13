from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.models.word import WordCreate, WordUpdate, WordResponse
from app.core.database import get_database
from app.core.security import decode_token
from bson import ObjectId
from datetime import datetime
from typing import List, Optional

router = APIRouter()
security = HTTPBearer()

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")

@router.post("/add", response_model=WordResponse)
async def add_word(
    word_data: WordCreate,
    user_id: str = Depends(get_current_user)
):
    """Add a word to user's word list"""
    db = get_database()
    words_collection = db.words
    
    # Check if word already exists for this user
    existing_word = words_collection.find_one({
        "user_id": user_id,
        "word": word_data.word.lower()
    })
    
    if existing_word:
        raise HTTPException(
            status_code=400,
            detail="Word already in your list"
        )
    
    # Create word document
    word_doc = {
        "user_id": user_id,
        "word": word_data.word.lower(),
        "translation": word_data.translation,
        "context": word_data.context,
        "source": word_data.source,
        "status": "learning",  # learning, practicing, learned
        "notes": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = words_collection.insert_one(word_doc)
    
    # Get inserted document
    word = words_collection.find_one({"_id": result.inserted_id})
    
    return WordResponse(
        id=str(word["_id"]),
        word=word["word"],
        translation=word["translation"],
        context=word.get("context"),
        source=word["source"],
        status=word["status"],
        notes=word.get("notes"),
        created_at=word["created_at"].isoformat(),
        updated_at=word["updated_at"].isoformat()
    )

@router.get("/list", response_model=List[WordResponse])
async def get_word_list(
    status: Optional[str] = None,
    search: Optional[str] = None,
    user_id: str = Depends(get_current_user)
):
    """Get user's word list with optional filtering"""
    db = get_database()
    words_collection = db.words
    
    # Build query
    query = {"user_id": user_id}
    
    if status:
        query["status"] = status
    
    if search:
        query["$or"] = [
            {"word": {"$regex": search, "$options": "i"}},
            {"translation": {"$regex": search, "$options": "i"}}
        ]
    
    # Get words, sorted by most recent first
    words = list(words_collection.find(query).sort("created_at", -1))
    
    return [
        WordResponse(
            id=str(word["_id"]),
            word=word["word"],
            translation=word["translation"],
            context=word.get("context"),
            source=word["source"],
            status=word["status"],
            notes=word.get("notes"),
            created_at=word["created_at"].isoformat(),
            updated_at=word["updated_at"].isoformat()
        )
        for word in words
    ]

@router.put("/{word_id}", response_model=WordResponse)
async def update_word(
    word_id: str,
    word_update: WordUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update a word's status or notes"""
    db = get_database()
    words_collection = db.words
    
    # Build update document
    update_data = {"updated_at": datetime.utcnow()}
    
    if word_update.status:
        update_data["status"] = word_update.status
    
    if word_update.notes is not None:
        update_data["notes"] = word_update.notes
    
    # Update word
    result = words_collection.update_one(
        {
            "_id": ObjectId(word_id),
            "user_id": user_id
        },
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Word not found")
    
    # Get updated word
    word = words_collection.find_one({"_id": ObjectId(word_id)})
    
    return WordResponse(
        id=str(word["_id"]),
        word=word["word"],
        translation=word["translation"],
        context=word.get("context"),
        source=word["source"],
        status=word["status"],
        notes=word.get("notes"),
        created_at=word["created_at"].isoformat(),
        updated_at=word["updated_at"].isoformat()
    )

@router.delete("/{word_id}")
async def delete_word(
    word_id: str,
    user_id: str = Depends(get_current_user)
):
    """Delete a word from the list"""
    db = get_database()
    words_collection = db.words
    
    result = words_collection.delete_one({
        "_id": ObjectId(word_id),
        "user_id": user_id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Word not found")
    
    return {"message": "Word deleted successfully"}

@router.get("/stats")
async def get_word_stats(user_id: str = Depends(get_current_user)):
    """Get statistics about user's word list"""
    db = get_database()
    words_collection = db.words
    
    total = words_collection.count_documents({"user_id": user_id})
    learning = words_collection.count_documents({"user_id": user_id, "status": "learning"})
    practicing = words_collection.count_documents({"user_id": user_id, "status": "practicing"})
    learned = words_collection.count_documents({"user_id": user_id, "status": "learned"})
    
    return {
        "total": total,
        "learning": learning,
        "practicing": practicing,
        "learned": learned
    }