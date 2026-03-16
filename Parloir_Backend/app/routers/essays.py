from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.essays import (
    EssayPrompt, EssaySubmission, EssayResponse, 
    EssayGrade, GradingCriteria
)
from app.core.config import settings
from app.core.security import decode_token
from app.core.database import get_database
from bson import ObjectId
from datetime import datetime, date
from typing import List
import json
import random

# Initialization
router = APIRouter()
security = HTTPBearer()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# NOW define the dependency function
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract and verify user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")

# DELF-style prompt templates by level
DELF_PROMPT_TEMPLATES = {
    "A1": [
        {
            "type": "personal",
            "templates": [
                "Présentez-vous: votre nom, votre âge, votre famille et vos loisirs.",
                "Décrivez votre maison et votre chambre.",
                "Parlez de votre journée typique.",
                "Décrivez votre meilleur ami ou meilleure amie.",
                "Qu'est-ce que vous aimez manger? Décrivez vos plats préférés."
            ],
            "min_words": 80
        }
    ],
    "A2": [
        {
            "type": "narrative",
            "templates": [
                "Racontez vos dernières vacances. Où êtes-vous allé(e)? Qu'avez-vous fait?",
                "Décrivez votre routine quotidienne du matin au soir.",
                "Parlez d'un événement important dans votre vie.",
                "Racontez votre weekend dernier en détail.",
                "Décrivez votre ville ou village: les lieux, les activités, ce que vous aimez."
            ],
            "min_words": 150
        }
    ],
    "B1": [
        {
            "type": "opinion",
            "templates": [
                "Pensez-vous que les réseaux sociaux sont utiles pour les jeunes? Expliquez pourquoi.",
                "Faut-il interdire les téléphones portables à l'école? Donnez votre avis.",
                "Préférez-vous vivre en ville ou à la campagne? Justifiez votre réponse.",
                "Le sport est-il important dans la vie? Expliquez avec des exemples.",
                "Pensez-vous qu'il est important d'apprendre plusieurs langues? Pourquoi?"
            ],
            "min_words": 200
        }
    ],
    "B2": [
        {
            "type": "argumentative",
            "templates": [
                "L'impact du télétravail sur la vie urbaine: discutez les aspects positifs et négatifs.",
                "Les réseaux sociaux et la jeunesse: analysez les avantages et les inconvénients.",
                "Faut-il interdire les voitures en centre-ville? Présentez les deux côtés du débat.",
                "Le tourisme de masse: un bienfait ou un problème pour les villes historiques?",
                "L'intelligence artificielle dans l'éducation: opportunité ou menace?"
            ],
            "min_words": 250
        }
    ],
    "C1": [
        {
            "type": "synthesis",
            "templates": [
                "Analysez l'évolution du rôle de la famille dans la société française contemporaine.",
                "La mondialisation culturelle: uniformisation ou enrichissement?",
                "Les enjeux éthiques de la recherche scientifique moderne.",
                "Le rôle de l'État face aux défis environnementaux: jusqu'où doit-il intervenir?",
                "La place de la culture dans la construction de l'identité nationale."
            ],
            "min_words": 300
        }
    ],
    "C2": [
        {
            "type": "critical",
            "templates": [
                "Dans quelle mesure la technologie numérique transforme-t-elle nos modes de pensée?",
                "Peut-on concilier croissance économique et préservation de l'environnement?",
                "Le concept de 'progrès' a-t-il encore un sens au XXIe siècle?",
                "La démocratie face aux réseaux sociaux: quels défis, quelles solutions?",
                "L'art contemporain: rupture ou continuité avec la tradition?"
            ],
            "min_words": 350
        }
    ]
}

def get_daily_prompt_for_level(level: str) -> dict:
    """Generate a consistent daily prompt for a given level based on the date"""
    
    # Use today's date as seed for consistency
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))  # e.g., 20260316
    
    # Get templates for this level
    level_data = DELF_PROMPT_TEMPLATES.get(level, DELF_PROMPT_TEMPLATES["B1"])[0]
    templates = level_data["templates"]
    min_words = level_data["min_words"]
    prompt_type = level_data["type"]
    
    # Use seed to pick same prompt for the whole day
    random.seed(seed + hash(level))  # Different seed per level
    topic = random.choice(templates)
    
    # Reset random seed
    random.seed()
    
    prompt_id = f"{level.lower()}_{today.strftime('%Y%m%d')}"
    
    return {
        "id": prompt_id,
        "title": topic,
        "description": f"Niveau {level} - {min_words} mots minimum",
        "category": prompt_type,
        "min_words": min_words,
        "level": level,
        "date": today.isoformat()
    }

@router.get("/prompts", response_model=List[EssayPrompt])
async def get_essay_prompts(user_id: str = Depends(get_current_user)):
    """Get daily DELF-style prompts for all levels"""
    
    # Get user's level
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    user_level = user.get("level", "B1") if user else "B1"
    
    # Generate daily prompts for all levels
    all_levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
    prompts = []
    
    for level in all_levels:
        prompt_data = get_daily_prompt_for_level(level)
        
        # Mark user's current level
        if level == user_level:
            prompt_data["is_current_level"] = True
        
        prompts.append(EssayPrompt(**prompt_data))
    
    return prompts

@router.get("/prompts/today", response_model=EssayPrompt)
async def get_todays_prompt(user_id: str = Depends(get_current_user)):
    """Get today's prompt for the user's level"""
    
    # Get user level
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    user_level = user.get("level", "B1") if user else "B1"
    
    prompt_data = get_daily_prompt_for_level(user_level)
    return EssayPrompt(**prompt_data)

@router.get("/prompts/{prompt_id}", response_model=EssayPrompt)
async def get_prompt(prompt_id: str, user_id: str = Depends(get_current_user)):
    """Get a specific prompt by ID (format: level_date)"""
    
    # Parse prompt_id (e.g., "b1_20260316")
    parts = prompt_id.split("_")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid prompt ID format")
    
    level = parts[0].upper()
    
    if level not in ["A1", "A2", "B1", "B2", "C1", "C2"]:
        raise HTTPException(status_code=400, detail="Invalid level")
    
    prompt_data = get_daily_prompt_for_level(level)
    return EssayPrompt(**prompt_data)

@router.post("/submit", response_model=EssayResponse)
async def submit_essay(
    submission: EssaySubmission,
    user_id: str = Depends(get_current_user)
):
    """Submit essay for grading"""
    
    # Get user level
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_level = user.get("level", "B1")
    
    # Parse prompt to get level and validate
    parts = submission.prompt_id.split("_")
    if len(parts) != 2:
        raise HTTPException(status_code=400, detail="Invalid prompt ID")
    
    prompt_level = parts[0].upper()
    prompt_data = get_daily_prompt_for_level(prompt_level)
    
    # Count words
    word_count = len(submission.content.split())
    
    # Grade essay with AI
    grade = await grade_essay_with_ai(
        submission.content, 
        prompt_data["title"],
        prompt_data["description"],
        user_level,
        word_count,
        prompt_data["min_words"]
    )
    
    # Save to database
    essays_collection = db.essays
    
    essay_doc = {
        "user_id": user_id,
        "prompt_id": submission.prompt_id,
        "prompt_title": prompt_data["title"],
        "content": submission.content,
        "grade": grade.dict(),
        "word_count": word_count,
        "user_level": user_level,
        "submitted_at": datetime.utcnow()
    }
    
    result = essays_collection.insert_one(essay_doc)
    
    return EssayResponse(
        id=str(result.inserted_id),
        prompt_id=submission.prompt_id,
        prompt_title=prompt_data["title"],
        content=submission.content,
        grade=grade,
        word_count=word_count,
        submitted_at=essay_doc["submitted_at"].isoformat(),
        user_level=user_level
    )

@router.get("/history", response_model=List[EssayResponse])
async def get_essay_history(user_id: str = Depends(get_current_user)):
    """Get user's essay history"""
    db = get_database()
    essays_collection = db.essays
    
    essays = list(essays_collection.find({"user_id": user_id}).sort("submitted_at", -1))
    
    return [
        EssayResponse(
            id=str(essay["_id"]),
            prompt_id=essay["prompt_id"],
            prompt_title=essay["prompt_title"],
            content=essay["content"],
            grade=EssayGrade(**essay["grade"]),
            word_count=essay["word_count"],
            submitted_at=essay["submitted_at"].isoformat(),
            user_level=essay["user_level"]
        )
        for essay in essays
    ]

async def grade_essay_with_ai(
    content: str,
    prompt_title: str,
    prompt_description: str,
    user_level: str,
    word_count: int,
    min_words: int
) -> EssayGrade:
    """Grade essay using Claude AI"""
    
    grading_prompt = f"""You are a French language teacher grading an essay from a {user_level} level student.

**Essay Prompt:** {prompt_title}
**Description:** {prompt_description}
**Required words:** {min_words}
**Actual words:** {word_count}

**Student's Essay:**
{content}

Grade this essay on four criteria, each scored 0-100:

1. **Grammar** - Verb conjugations, agreement, tenses, sentence structure
2. **Vocabulary** - Word choice, variety, appropriateness for level
3. **Structure** - Organization, paragraphs, introduction/conclusion, flow
4. **Coherence** - Logical progression, clarity, relevance to prompt

For each criterion, provide:
- A score (0-100)
- Specific feedback
- 2-3 examples from the text (good or areas to improve)

Also provide:
- Overall score (average of 4 criteria)
- 3-5 specific suggestions for improvement
- 2-3 strengths to celebrate

Remember: This is a {user_level} student. Grade appropriately for their level.

**CRITICAL: Respond ONLY with valid JSON in this exact format:**
{{
  "overall_score": 85,
  "grammar": {{
    "score": 80,
    "feedback": "Good use of present tense...",
    "examples": ["Example 1", "Example 2"]
  }},
  "vocabulary": {{
    "score": 85,
    "feedback": "Varied vocabulary...",
    "examples": ["Example 1", "Example 2"]
  }},
  "structure": {{
    "score": 90,
    "feedback": "Well organized...",
    "examples": ["Example 1", "Example 2"]
  }},
  "coherence": {{
    "score": 85,
    "feedback": "Clear and logical...",
    "examples": ["Example 1", "Example 2"]
  }},
  "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"],
  "strengths": ["Strength 1", "Strength 2"]
}}"""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": grading_prompt}]
        )
        
        ai_response = response.content[0].text
        
        # Clean JSON
        ai_response = ai_response.strip()
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()
        
        grade_data = json.loads(ai_response)
        
        return EssayGrade(
            overall_score=grade_data["overall_score"],
            grammar=GradingCriteria(**grade_data["grammar"]),
            vocabulary=GradingCriteria(**grade_data["vocabulary"]),
            structure=GradingCriteria(**grade_data["structure"]),
            coherence=GradingCriteria(**grade_data["coherence"]),
            suggestions=grade_data["suggestions"],
            strengths=grade_data["strengths"]
        )
        
    except Exception as e:
        print(f"Grading error: {e}")
        return EssayGrade(
            overall_score=70,
            grammar=GradingCriteria(score=70, feedback="Unable to grade. Please try again.", examples=[]),
            vocabulary=GradingCriteria(score=70, feedback="Unable to grade. Please try again.", examples=[]),
            structure=GradingCriteria(score=70, feedback="Unable to grade. Please try again.", examples=[]),
            coherence=GradingCriteria(score=70, feedback="Unable to grade. Please try again.", examples=[]),
            suggestions=["Please resubmit"],
            strengths=["Keep practicing!"]
        )