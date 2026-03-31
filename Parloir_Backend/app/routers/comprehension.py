from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from anthropic import Anthropic
from app.models.comprehension import Article, Question
from app.core.config import settings
from app.core.security import decode_token
from app.core.database import get_database
from bson import ObjectId
from datetime import date
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


# ============================================
# BOOK EXCERPTS BY LEVEL (WITH CULTURAL CONTEXT!)
# ============================================

# A1-A2 Level Excerpts (Beginner)
A1_A2_EXCERPTS = [
    {
        "title": "Le Petit Prince découvre la rose",
        "content": """Un jour, une graine mystérieuse est arrivée sur la planète du petit prince. Il l'a regardée pousser avec curiosité. C'était une fleur qu'il n'avait jamais vue.

La fleur a commencé à se préparer dans le secret de sa chambre verte. Elle choisissait ses couleurs avec soin. Elle voulait apparaître dans tout son éclat.

Un matin enfin, elle s'est montrée. Le petit prince a admiré cette belle apparition. La rose était magnifique avec ses pétales délicats.

"Bonjour," dit la fleur. Le petit prince était émerveillé. C'était la première fois qu'il rencontrait une créature aussi belle sur sa petite planète.""",
        "source": "Le Petit Prince - Antoine de Saint-Exupéry",
        "difficulty": "A2",
        "category": "Littérature classique",
        "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "auto_stories",
                "title": "Le Petit Prince",
                "text": "Écrit en 1943, Le Petit Prince est le livre français le plus traduit au monde. Antoine de Saint-Exupéry était aussi un aviateur célèbre."
            },
            {
                "icon": "favorite",
                "title": "La rose",
                "text": "La rose symbolise l'amour et les relations humaines dans la culture française. Elle représente quelque chose de précieux qu'il faut protéger."
            }
        ]
    },
    {
        "title": "Le Corbeau et le Renard",
        "content": """Maître Corbeau, sur un arbre perché, tenait en son bec un fromage. Maître Renard, attiré par l'odeur, lui tint à peu près ce langage.

"Bonjour, Monsieur du Corbeau. Que vous êtes joli! Que vous me semblez beau! Sans mentir, si votre ramage se rapporte à votre plumage, vous êtes le phénix des hôtes de ces bois."

À ces mots, le Corbeau ne se sent pas de joie. Pour montrer sa belle voix, il ouvre un large bec et laisse tomber sa proie.

Le Renard s'en saisit et dit: "Mon bon Monsieur, apprenez que tout flatteur vit aux dépens de celui qui l'écoute. Cette leçon vaut bien un fromage, sans doute.""",
        "source": "Fables - Jean de La Fontaine",
        "difficulty": "A2",
        "category": "Fables",
        "image_url": "https://images.unsplash.com/photo-1551244072-5d12893278ab?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "menu_book",
                "title": "Les Fables de La Fontaine",
                "text": "Jean de La Fontaine (1621-1695) a écrit 243 fables qui sont enseignées à tous les enfants français. Elles contiennent des leçons morales importantes."
            },
            {
                "icon": "psychology",
                "title": "La flatterie",
                "text": "Cette fable enseigne que la flatterie est dangereuse. Dans la culture française, on valorise l'honnêteté plus que les compliments excessifs."
            }
        ]
    },
    {
        "title": "Une journée à Paris",
        "content": """Marie habite à Paris depuis trois ans. Chaque matin, elle prend le métro pour aller au travail. Elle aime observer les gens dans le wagon.

Aujourd'hui, c'est samedi. Marie décide de visiter le Jardin du Luxembourg. Le soleil brille et les fleurs sont magnifiques. Elle s'assoit sur un banc avec un livre.

Des enfants jouent près de la fontaine. Leurs rires remplissent l'air de joie. Marie sourit en les regardant. Elle pense que Paris est vraiment une belle ville.

À midi, elle va dans un petit café. Elle commande un croque-monsieur et un café au lait. La serveuse est très gentille et elles discutent un peu.""",
        "source": "Texte original - Vie quotidienne",
        "difficulty": "A1",
        "category": "Vie quotidienne",
        "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "park",
                "title": "Le Jardin du Luxembourg",
                "text": "Créé en 1612, c'est l'un des plus beaux jardins de Paris. Les Parisiens y viennent pour lire, se détendre et profiter du soleil."
            },
            {
                "icon": "restaurant",
                "title": "Le croque-monsieur",
                "text": "Sandwich chaud typiquement français avec du jambon et du fromage gratiné. C'est un classique des cafés parisiens depuis les années 1910."
            }
        ]
    }
]

# B1-B2 Level Excerpts (Intermediate)
B1_B2_EXCERPTS = [
    {
        "title": "L'évasion du Château d'If",
        "content": """Edmond Dantès était prisonnier depuis quatorze ans dans le Château d'If. Il avait perdu tout espoir de liberté quand il rencontra l'abbé Faria, un autre prisonnier érudit.

L'abbé lui enseigna les sciences, les langues et l'histoire. Ensemble, ils creusèrent un tunnel pendant des années. Mais un jour, l'abbé tomba gravement malade.

Avant de mourir, l'abbé révéla à Dantès l'existence d'un trésor caché sur l'île de Monte-Cristo. Il lui donna tous les détails nécessaires pour le trouver.

Après la mort de l'abbé, Dantès eut une idée audacieuse. Il prit la place du corps dans le sac mortuaire. Les gardiens jetèrent le sac à la mer, croyant que c'était l'abbé. Dantès était enfin libre!""",
        "source": "Le Comte de Monte-Cristo - Alexandre Dumas",
        "difficulty": "B1",
        "category": "Roman d'aventure",
        "image_url": "https://images.unsplash.com/photo-1519608487953-e999c86e7455?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "castle",
                "title": "Le Château d'If",
                "text": "Prison réelle située sur une île au large de Marseille. Construite au 16ème siècle, elle a inspiré de nombreux écrivains français."
            },
            {
                "icon": "auto_stories",
                "title": "Alexandre Dumas",
                "text": "L'un des écrivains français les plus populaires du 19ème siècle. Ses romans d'aventure comme Les Trois Mousquetaires sont lus dans le monde entier."
            }
        ]
    },
    {
        "title": "Jean Valjean et les chandeliers",
        "content": """Jean Valjean venait de passer dix-neuf ans au bagne pour avoir volé un pain. Libéré, personne ne voulait l'accueillir à cause de son passé. Seul l'évêque Myriel lui ouvrit sa porte.

Cette nuit-là, Valjean ne pouvait pas dormir. Il regardait l'argenterie de l'évêque qui brillait dans l'obscurité. La tentation était trop forte pour un homme habitué à la misère.

Au milieu de la nuit, il se leva et vola les chandeliers d'argent. Il s'enfuit dans la nuit, convaincu que personne ne le retrouverait.

Mais le lendemain matin, les gendarmes l'arrêtèrent et le ramenèrent chez l'évêque. Contre toute attente, l'évêque déclara avoir donné l'argenterie à Valjean. Il ajouta même: "Vous avez oublié les chandeliers que je vous ai donnés aussi!" Ce geste de miséricorde changea la vie de Valjean à jamais.""",
        "source": "Les Misérables - Victor Hugo",
        "difficulty": "B2",
        "category": "Roman social",
        "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "gavel",
                "title": "Le bagne",
                "text": "Prison de travaux forcés en France au 19ème siècle. Victor Hugo dénonçait la sévérité du système judiciaire qui condamnait des gens pour des petits vols."
            },
            {
                "icon": "favorite",
                "title": "La miséricorde",
                "text": "Le pardon et la rédemption sont des thèmes centraux de la culture catholique française. L'évêque représente la bonté qui peut transformer une vie."
            }
        ]
    },
    {
        "title": "Candide découvre le monde",
        "content": """Candide avait été élevé dans le château du baron de Thunder-ten-tronckh. Son précepteur, Pangloss, lui enseignait que tout est pour le mieux dans le meilleur des mondes possibles.

Un jour, le baron surprit Candide en train d'embrasser sa fille Cunégonde. Furieux, il chassa Candide du château. Le jeune homme se retrouva seul dans un monde qu'il ne connaissait pas.

Il fut enrôlé de force dans l'armée bulgare et connut les horreurs de la guerre. Il vit des villages entiers brûlés et des innocents massacrés. Cette réalité contredisait tout ce que Pangloss lui avait enseigné.

Candide commença à douter de la philosophie optimiste de son maître. Le monde n'était peut-être pas aussi parfait qu'on le lui avait dit.""",
        "source": "Candide - Voltaire",
        "difficulty": "B2",
        "category": "Conte philosophique",
        "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "school",
                "title": "Les Lumières",
                "text": "Voltaire était un philosophe des Lumières (18ème siècle). Ce mouvement valorisait la raison, la science et critiquait les superstitions."
            },
            {
                "icon": "psychology",
                "title": "L'optimisme",
                "text": "Voltaire critique la philosophie qui dit que 'tout est pour le mieux'. Il montre que le monde contient beaucoup de souffrances."
            }
        ]
    }
]

# C1-C2 Level Excerpts (Advanced)
C1_C2_EXCERPTS = [
    {
        "title": "L'absurde quotidien",
        "content": """Aujourd'hui, maman est morte. Ou peut-être hier, je ne sais pas. J'ai reçu un télégramme de l'asile: "Mère décédée. Enterrement demain. Sentiments distingués." Cela ne veut rien dire. C'était peut-être hier.

L'asile de vieillards est à Marengo, à quatre-vingts kilomètres d'Alger. Je prendrai l'autobus à deux heures et j'arriverai dans l'après-midi. Ainsi, je pourrai veiller et je rentrerai demain soir.

J'ai demandé deux jours de congé à mon patron et il ne pouvait pas me les refuser avec une excuse pareille. Mais il n'avait pas l'air content. Je lui ai même dit: "Ce n'est pas de ma faute." Il n'a pas répondu.

J'ai pensé alors que je n'aurais pas dû lui dire cela. En somme, je n'avais pas à m'excuser. C'était plutôt à lui de me présenter ses condoléances. Mais il le fera sans doute après-demain, quand il me verra en deuil.""",
        "source": "L'Étranger - Albert Camus",
        "difficulty": "C1",
        "category": "Roman existentialiste",
        "image_url": "https://images.unsplash.com/photo-1516414447565-b14be0adf13e?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "psychology",
                "title": "L'existentialisme",
                "text": "Mouvement philosophique français du 20ème siècle. Camus explore l'absurdité de l'existence humaine."
            },
            {
                "icon": "public",
                "title": "L'Algérie française",
                "text": "L'histoire se déroule à Alger quand l'Algérie était colonie française (avant 1962)."
            }
        ]
    },
    {
        "title": "Emma Bovary rêve d'ailleurs",
        "content": """Emma lisait des romans qui parlaient d'amour, de passion et de luxe. Elle rêvait d'une vie différente, loin de la monotonie de son existence provinciale avec Charles, son mari médecin.

Elle imaginait des bals somptueux dans des châteaux, des amants élégants et des aventures romantiques. La réalité de Yonville, avec ses commérages et sa petitesse, l'étouffait chaque jour davantage.

Charles l'aimait sincèrement, mais il était trop ordinaire pour satisfaire ses aspirations. Elle le trouvait ennuyeux avec sa médecine de campagne et ses manières simples.

Emma commença à chercher ailleurs ce que son mariage ne lui offrait pas. Elle dépensait sans compter pour s'acheter de belles robes et des objets de luxe. Elle voulait créer l'illusion d'une vie élégante, même si cela menait sa famille à la ruine.""",
        "source": "Madame Bovary - Gustave Flaubert",
        "difficulty": "C2",
        "category": "Roman réaliste",
        "image_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "auto_stories",
                "title": "Le réalisme",
                "text": "Flaubert est le maître du réalisme français (19ème siècle). Il décrit la vie quotidienne sans embellissement."
            },
            {
                "icon": "favorite_border",
                "title": "Le bovarysme",
                "text": "Terme créé d'après ce roman: insatisfaction chronique et tendance à s'évader dans le rêve."
            }
        ]
    },
    {
        "title": "La madeleine de Proust",
        "content": """Il y avait déjà bien des années que, de Combray, tout ce qui n'était pas le théâtre et le drame de mon coucher n'existait plus pour moi, quand un jour d'hiver, comme je rentrais à la maison, ma mère me proposa de prendre du thé.

J'acceptai machinalement et elle fit apporter une de ces pâtisseries qu'on appelle Petites Madeleines. Je portai à mes lèvres une cuillerée du thé où j'avais laissé s'amollir un morceau de madeleine.

Mais à l'instant même où la gorgée mêlée des miettes du gâteau toucha mon palais, je tressaillis, attentif à ce qui se passait d'extraordinaire en moi. Un plaisir délicieux m'avait envahi, isolé, sans la notion de sa cause.

Il m'avait aussitôt rendu les vicissitudes de la vie indifférentes, ses désastres inoffensifs, sa brièveté illusoire. Je sentais vibrer en moi quelque chose qui venait de très loin, peut-être du fond de mon enfance.""",
        "source": "À la recherche du temps perdu - Marcel Proust",
        "difficulty": "C2",
        "category": "Roman psychologique",
        "image_url": "https://images.unsplash.com/photo-1481931098730-318b6f776db0?w=800&h=400&fit=crop",
        "cultural_context": [
            {
                "icon": "cake",
                "title": "La madeleine",
                "text": "'Madeleine de Proust' désigne maintenant un souvenir déclenché par une odeur ou un goût."
            },
            {
                "icon": "schedule",
                "title": "La mémoire involontaire",
                "text": "Proust explore comment les sensations font resurgir des souvenirs enfouis."
            }
        ]
    }
]


# ============================================
# DAILY EXCERPT LOGIC
# ============================================
def get_daily_excerpt(user_level: str = "B1") -> dict:
    """Get daily excerpt based on user level with date-based seeding"""
    
    # Map level to pool
    if user_level in ["A1", "A2"]:
        pool = A1_A2_EXCERPTS
    elif user_level in ["B1", "B2"]:
        pool = B1_B2_EXCERPTS
    else:  # C1, C2
        pool = C1_C2_EXCERPTS
    
    # Date-based seeding for consistency
    today = date.today()
    seed = int(today.strftime("%Y%m%d"))
    random.seed(seed)
    excerpt = random.choice(pool)
    random.seed()  # Reset
    
    return {
        "id": f"daily_{today.strftime('%Y%m%d')}",
        "title": excerpt["title"],
        "content": excerpt["content"],
        "image_url": excerpt["image_url"],
        "source": excerpt["source"],
        "difficulty": excerpt["difficulty"],
        "category": excerpt["category"],
        "cultural_context": excerpt.get("cultural_context", []),
        "date": today.isoformat()
    }


# ============================================
# API ENDPOINTS
# ============================================
@router.get("/today", response_model=Article)
async def get_todays_article(user_id: str = Depends(get_current_user)):
    """Get today's excerpt"""
    
    db = get_database()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    user_level = user.get("level", "B1") if user else "B1"
    
    excerpt = get_daily_excerpt(user_level)
    
    return Article(**excerpt)


@router.post("/questions", response_model=List[Question])
async def generate_questions(user_id: str = Depends(get_current_user)):
    """Generate AI questions"""
    
    db = get_database()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    user_level = user.get("level", "B1") if user else "B1"
    
    excerpt = get_daily_excerpt(user_level)
    
    questions = await generate_comprehension_questions(
        excerpt["title"],
        excerpt["content"],
        user_level
    )
    
    return questions


# ============================================
# AI QUESTION GENERATION
# ============================================
async def generate_comprehension_questions(title: str, content: str, level: str) -> List[Question]:
    """Generate questions using Claude"""
    
    prompt = f"""Generate 5 French comprehension questions for {level} level.

    Text: {title}
    {content}

    Format (JSON only):
    {{
    "questions": [
        {{"id": "q1", "question": "...", "type": "multiple_choice", "options": ["A","B","C","D"], "correct_answer": "A"}},
        {{"id": "q2", "question": "...", "type": "true_false", "options": ["Vrai","Faux"], "correct_answer": "Vrai"}}
    ]
    }}

    3 multiple choice + 2 true/false. All in French."""
    
    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        ai_text = response.content[0].text.strip()
        ai_text = ai_text.replace("```json", "").replace("```", "").strip()
        
        data = json.loads(ai_text)
        return [Question(**q) for q in data["questions"]]
        
    except Exception as e:
        print(f"AI error: {e}")
        return fallback_questions()


def fallback_questions() -> List[Question]:
    """Fallback if AI fails"""
    return [
        Question(
            id="q1",
            question="Quel est le thème principal?",
            type="multiple_choice",
            options=["L'amour", "L'aventure", "La nature", "La famille"],
            correct_answer="L'aventure"
        ),
        Question(
            id="q2",
            question="Le personnage est heureux.",
            type="true_false",
            options=["Vrai", "Faux"],
            correct_answer="Faux"
        )
    ]