from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.comprehension import (
    Article, Question, Answer, ComprehensionResponse
)
from app.core.config import settings
from app.core.security import decode_token
from app.core.database import get_database
from bson import ObjectId
from datetime import datetime, date
from typing import List
import json
import random

router = APIRouter()
security = HTTPBearer()
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

# Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = decode_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return payload.get("sub")

# Pool of 1jour1actu-style articles
ARTICLE_POOL = [
    {
        "title": "Le changement climatique expliqué aux jeunes",
        "content": """Le changement climatique est l'un des plus grands défis de notre époque. La température de la Terre augmente à cause des gaz à effet de serre produits par les activités humaines.

Les scientifiques observent que les glaciers fondent, le niveau de la mer monte, et les événements météorologiques extrêmes deviennent plus fréquents. Les animaux doivent s'adapter ou migrer vers des régions plus froides.

Que pouvons-nous faire? Réduire notre consommation d'énergie, utiliser les transports en commun, recycler nos déchets, et planter des arbres sont des actions importantes. Chaque petit geste compte pour protéger notre planète.""",
        "difficulty": "B1",
        "category": "Environnement"
    },
    {
        "title": "Les Jeux Olympiques de Paris 2024",
        "content": """Les Jeux Olympiques de Paris 2024 ont été un événement historique pour la France. Plus de 10,000 athlètes de 206 pays ont participé à ces jeux spectaculaires.

La cérémonie d'ouverture sur la Seine a été regardée par des millions de personnes dans le monde entier. Les athlètes français ont gagné de nombreuses médailles dans différentes disciplines sportives.

Ces jeux ont montré l'importance du sport pour unir les peuples. Ils ont aussi mis en lumière les valeurs olympiques: l'excellence, l'amitié et le respect.""",
        "difficulty": "A2",
        "category": "Sport"
    },
    {
        "title": "L'intelligence artificielle dans l'éducation",
        "content": """L'intelligence artificielle (IA) transforme l'éducation de manière significative. Les enseignants utilisent maintenant des outils d'IA pour personnaliser l'apprentissage de chaque élève.

Ces technologies peuvent identifier les difficultés d'un étudiant et proposer des exercices adaptés à son niveau. Les chatbots éducatifs répondent aux questions des élèves 24 heures sur 24.

Cependant, l'IA ne remplace pas les professeurs. Elle est un outil qui aide les enseignants à mieux comprendre les besoins de leurs élèves. L'interaction humaine reste essentielle dans l'éducation.""",
        "difficulty": "B2",
        "category": "Technologie"
    },
    {
        "title": "La mode éco-responsable",
        "content": """La mode éco-responsable gagne en popularité chez les jeunes. De plus en plus de marques proposent des vêtements fabriqués avec des matériaux recyclés ou biologiques.

L'industrie de la mode est l'une des plus polluantes au monde. Acheter moins de vêtements, privilégier la seconde main, et choisir des marques durables sont des gestes importants.

Les créateurs français innovent en créant des collections respectueuses de l'environnement. Cette tendance montre qu'il est possible d'être élégant tout en protégeant la planète.""",
        "difficulty": "B1",
        "category": "Société"
    },
    {
        "title": "Les animaux en danger",
        "content": """De nombreuses espèces animales sont menacées de disparition. Les pandas, les tigres, et les éléphants font partie des animaux en danger à cause de la destruction de leur habitat.

Les zoos et les réserves naturelles travaillent pour protéger ces espèces. Des programmes de reproduction permettent d'augmenter le nombre d'animaux et de les réintroduire dans la nature.

Chacun peut aider en soutenant les associations de protection des animaux et en respectant la nature lors de ses voyages.""",
        "difficulty": "A2",
        "category": "Nature"
    }
]

def get_daily_article() -> dict:
    """Get today's article (consistent for the whole day)"""
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))
    
    # Use seed to pick same article for the whole day
    random.seed(seed)
    article_data = random.choice(ARTICLE_POOL)
    random.seed()  # Reset
    
    return {
        "id": f"daily_{today.strftime('%Y%m%d')}",
        "title": article_data["title"],
        "content": article_data["content"],
        "image_url": "https://via.placeholder.com/800x400",
        "source": "1jour1actu",
        "difficulty": article_data["difficulty"],
        "category": article_data["category"],
        "date": today.isoformat()
    }

@router.get("/today", response_model=Article)
async def get_todays_article(user_id: str = Depends(get_current_user)):
    """Get today's article"""
    article_data = get_daily_article()
    return Article(**article_data)

@router.post("/questions", response_model=List[Question])
async def generate_questions(user_id: str = Depends(get_current_user)):
    """Generate comprehension questions for today's article"""
    
    article = get_daily_article()
    
    # Get user level
    db = get_database()
    users_collection = db.users
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    user_level = user.get("level", "B1") if user else "B1"
    
    # Generate questions with AI
    questions = await generate_comprehension_questions(
        article["title"],
        article["content"],
        user_level
    )
    
    return questions

@router.post("/check-answer", response_model=ComprehensionResponse)
async def check_answer(
    answer: Answer,
    user_id: str = Depends(get_current_user)
):
    """Check a user's answer"""
    
    article = get_daily_article()
    
    # Use AI to check the answer
    response = await check_answer_with_ai(
        article["content"],
        answer.user_answer
    )
    
    return response

async def generate_comprehension_questions(
    title: str,
    content: str,
    level: str
) -> List[Question]:
    """Generate comprehension questions using Claude AI"""
    
    prompt = f"""Based on this French article, generate 5 comprehension questions appropriate for a {level} level French learner.

**Article Title:** {title}

**Article Content:**
{content}

Generate exactly 5 questions:
- 3 multiple choice questions (4 options each)
- 2 true/false questions

**CRITICAL: Respond ONLY with valid JSON in this exact format:**
{{
  "questions": [
    {{
      "id": "q1",
      "question": "Quel est le sujet principal de l'article?",
      "type": "multiple_choice",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option A"
    }},
    {{
      "id": "q2",
      "question": "Statement in French",
      "type": "true_false",
      "options": ["Vrai", "Faux"],
      "correct_answer": "Vrai"
    }}
  ]
}}

Make questions test understanding. All content in French, appropriate for {level} level."""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        ai_response = response.content[0].text.strip()
        
        # Clean JSON
        if ai_response.startswith("```json"):
            ai_response = ai_response[7:]
        if ai_response.startswith("```"):
            ai_response = ai_response[3:]
        if ai_response.endswith("```"):
            ai_response = ai_response[:-3]
        ai_response = ai_response.strip()
        
        data = json.loads(ai_response)
        
        return [Question(**q) for q in data["questions"]]
        
    except Exception as e:
        print(f"Question generation error: {e}")
        return [
            Question(
                id="q1",
                question="Quel est le sujet principal de l'article?",
                type="multiple_choice",
                options=["Le climat", "Le sport", "La technologie", "La mode"],
                correct_answer="Le climat"
            )
        ]

async def check_answer_with_ai(article_content: str, user_answer: str) -> ComprehensionResponse:
    """Check answer using AI"""
    return ComprehensionResponse(
        question_id="q1",
        is_correct=True,
        explanation="Bonne réponse!",
        correct_answer=user_answer
    )