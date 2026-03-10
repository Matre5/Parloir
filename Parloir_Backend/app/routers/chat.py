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
