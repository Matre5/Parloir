from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.translate import TranslateRequest, TranslateResponse
from app.core.config import settings
from app.core.security import decode_token
from app.core.database import get_database
from bson import ObjectId

router = APIRouter()
security = HTTPBearer()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Dependency to get current user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")

@router.post("/", response_model=TranslateResponse)
async def translate_text(
    translate_request: TranslateRequest,
    user_id: str = Depends(get_current_user)
):
    """Translate text between French and English"""
    
    # Get user's level for context-aware translation
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    user_level = user.get("level", "A2") if user else "A2"
    
    # Detect source language if auto
    detected_lang = translate_request.source_lang
    if detected_lang == "auto":
        # Simple detection: if has French chars, assume French
        french_chars = set("àâäæçéèêëïîôùûüÿœÀÂÄÆÇÉÈÊËÏÎÔÙÛÜŸŒ")
        has_french = any(char in french_chars for char in translate_request.text)
        detected_lang = "fr" if has_french else "en"
    
    # Build translation prompt
    if translate_request.target_lang == "fr":
        prompt = f"""Translate this English text to French at {user_level} level:

"{translate_request.text}"

Provide:
1. The French translation (appropriate for {user_level} level learner)
2. A simple pronunciation guide using English phonetics

Format your response EXACTLY like this:
TRANSLATION: [French translation here]
PRONUNCIATION: [phonetic guide here]"""
    else:  # target is English
        prompt = f"""Translate this French text to English:

"{translate_request.text}"

Provide a natural, accurate English translation.

Format your response EXACTLY like this:
TRANSLATION: [English translation here]"""
    
    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        ai_response = response.content[0].text
        
        # Parse response
        translation = ""
        pronunciation = None

        lines = ai_response.split('\n')
        translation_lines = []
        in_translation = False

        for line in lines:
            if line.startswith('TRANSLATION:'):
                translation_lines.append(line.replace('TRANSLATION:', '').strip())
                in_translation = True
            elif line.startswith('PRONUNCIATION:'):
                pronunciation = line.replace('PRONUNCIATION:', '').strip()
                in_translation = False
            elif in_translation:
                translation_lines.append(line)

        translation = '\n'.join(translation_lines).strip()

        if not translation:
            translation = ai_response.strip()
        
        return TranslateResponse(
            original_text=translate_request.text,
            translated_text=translation,
            source_lang=detected_lang,
            target_lang=translate_request.target_lang,
            pronunciation=pronunciation
        )
        
    except Exception as e:
        print(f"Translation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Translation failed: {str(e)}"
        )