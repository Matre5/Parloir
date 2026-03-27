from datetime import date
import random
from typing import Dict

class BookExcerpts:
    """Curated French book excerpts by CEFR level"""
    
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
            "image_url": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1551244072-5d12893278ab?w=800&h=400&fit=crop"
        },
        {
            "title": "Une journée à Paris",
            "content": """Marie habite à Paris depuis trois ans. Chaque matin, elle prend le métro pour aller au travail. Elle aime observer les gens dans le wagon.

Aujourd'hui, c'est samedi. Marie décide de visiter le Jardin du Luxembourg. Le soleil brille et les fleurs sont magnifiques. Elle s'assoit sur un banc avec un livre.

Des enfants jouent près de la fontaine. Leurs rires remplissent l'air de joie. Marie sourit en les regardant. Elle pense que Paris est vraiment une belle ville.

À midi, elle va dans un petit café. Elle commande un croque-monsieur et un café au lait. La serveuse est très gentille et elles discutent un peu.""",
            "source": "Texte original",
            "difficulty": "A1",
            "category": "Vie quotidienne",
            "image_url": "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1519608487953-e999c86e7455?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1516414447565-b14be0adf13e?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=800&h=400&fit=crop"
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
            "image_url": "https://images.unsplash.com/photo-1481931098730-318b6f776db0?w=800&h=400&fit=crop"
        }
    ]
    
    @staticmethod
    def get_daily_excerpt(user_level: str = "B1") -> Dict:
        """
        Get daily book excerpt based on user level
        Uses date-based seeding for consistency
        """
        # Map user level to excerpt pool
        if user_level in ["A1", "A2"]:
            pool = BookExcerpts.A1_A2_EXCERPTS
        elif user_level in ["B1", "B2"]:
            pool = BookExcerpts.B1_B2_EXCERPTS
        else:  # C1, C2
            pool = BookExcerpts.C1_C2_EXCERPTS
        
        # Use date-based seeding for consistent daily excerpt
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
            "date": today.isoformat()
        }