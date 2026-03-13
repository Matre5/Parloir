from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.core.security import decode_token

router = APIRouter()

# Initialize Anthropic client
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Security scheme
security = HTTPBearer()

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return payload.get("sub")  # Return user_id

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """Chat with AI French tutor"""
    
    # Build conversation with system prompt
    messages = []
    
    # Add conversation history
    for msg in chat_request.conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add new user message
    messages.append({
        "role": "user",
        "content": chat_request.message
    })
    
    system_prompt = """You are a patient, encouraging French tutor for an A2-B2 level learner. 

    Your teaching style:
    - Always respond in French (unless explaining complex grammar)
    - Communicate like a local except asked otherwise
    - Gently correct mistakes without being harsh
    - Use simple, clear French appropriate for their level
    - Be conversational and friendly
    - Encourage the learner
    - If they make mistakes, acknowledge them kindly and show the correct form

    Example correction format:
    "Bonne tentative! 👍 On dit plutôt: '[correct sentence]'. Continue comme ça!"

    Keep responses concise (2-4 sentences) unless they ask for detailed explanations. """
    
    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        
        # Extract response text
        ai_response = response.content[0].text
        
        return ChatResponse(
            response=ai_response,
            corrected_message=None
        )
        
    except Exception as e:
        print(f"Anthropic API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI response: {str(e)}"
        )

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.chat import ChatRequest, ChatResponse
from app.core.config import settings
from app.core.security import decode_token
from app.core.database import get_database
from bson import ObjectId

router = APIRouter()

# Initialize Anthropic client
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Security scheme
security = HTTPBearer()

# Dependency to get current user from token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    
    # Decode token
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    
    return payload.get("sub")  # Return user_id

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(
    chat_request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """Chat with AI French tutor"""
    
    # Get user profile from database to access their level
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's French level and learning style
    user_level = user.get("level", "A2")
    learning_style = user.get("learning_style", "patient_mentor")
    user_name = user.get("name", "there")
    
    # Build conversation with system prompt
    messages = []
    
    # Add conversation history
    for msg in chat_request.conversation_history:
        messages.append({
            "role": msg.role,
            "content": msg.content
        })
    
    # Add new user message
    messages.append({
        "role": "user",
        "content": chat_request.message
    })
    
    # Adaptive system prompt based on user level
    level_guidance = {
        "A1": "Use very simple French with present tense. Keep sentences short (5-8 words). Use common, everyday vocabulary. Provide lots of encouragement.",
        "A2": "Use simple French with present and near future tenses. Keep sentences straightforward. Use familiar vocabulary and explain new words. Be encouraging.",
        "B1": "Use clear French with past, present, and future tenses. Introduce some complex sentences. Use varied vocabulary and idiomatic expressions occasionally.",
        "B2": "Use natural French with all tenses including subjunctive. Use complex sentences and varied vocabulary. Introduce idiomatic expressions and cultural references.",
        "C1": "Use sophisticated French with nuanced expressions. Challenge with abstract topics and advanced grammar. Use idioms and cultural references naturally.",
        "C2": "Use native-level French. Discuss abstract and complex topics. Use advanced vocabulary, idioms, and subtle expressions naturally."
    }
    
    style_guidance = {
        "patient_mentor": "Be patient, warm, and encouraging. Celebrate small victories. Explain gently.",
        "strict_teacher": "Be direct and precise. Point out errors clearly. Maintain high standards while remaining respectful.",
        "friendly_tutor": "Be casual and conversational. Use humor when appropriate. Make learning feel natural and fun.",
        "conversational": "Act like a French friend chatting naturally. Keep corrections subtle and integrated into natural responses."
    }
    
    # Dynamic system prompt
    system_prompt = f"""You are a French tutor helping {user_name}, who is at {user_level} level.

**Level Guidelines ({user_level}):**
{level_guidance.get(user_level, level_guidance["A2"])}

**Teaching Style ({learning_style}):**
{style_guidance.get(learning_style, style_guidance["patient_mentor"])}

**Your approach:**
- Always respond in French (unless explaining complex grammar for beginners)
- Communicate like a local except asked otherwise
- Gently correct mistakes without being harsh
- Adapt complexity to their {user_level} level
- If they make mistakes, acknowledge them kindly and show the correct form in english
- Keep responses concise (2-4 sentences) unless they ask for detailed explanations

**Example correction format:**
"Bonne tentative! 👍 On dit plutôt: '[correct sentence]'. Continue comme ça!"
"""
    
    try:
        # Call Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages
        )
        
        # Extract response text
        ai_response = response.content[0].text
        
        return ChatResponse(
            response=ai_response,
            corrected_message=None
        )
        
    except Exception as e:
        print(f"Anthropic API error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get AI response: {str(e)}"
        )