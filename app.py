import streamlit as st
import sqlite3
from datetime import datetime

# Import our auth modules
from auth.database import initialize_database
from auth.auth import (
    register_user,
    login_user,
    verify_access_token,
    logout_user,
    get_current_user
)

# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="Parloir",
    page_icon="🇫🇷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS - BLOOMING ROMANCE
# =========================

def load_css():
    st.markdown("""
    <style>
    /* Import Playpen Sans */
    @import url('https://fonts.googleapis.com/css2?family=Playpen+Sans:wght@300;400;500;600&display=swap');
    
    /* Force Light Theme */
    [data-testid="stAppViewContainer"] {
        background-color: #FFFFFF !important;
    }
    
    [data-testid="stHeader"] {
        background-color: #FFFFFF !important;
    }
    
    /* Global Styles */
    * {
        font-family: 'Playpen Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Container */
    .main {
        background: #FFFFFF !important;
        padding: 0;
    }
    
    .block-container {
        padding: 80px 24px;
        max-width: 440px;
        background: #FFFFFF !important;
    }
    
    /* Fix Streamlit's default dark mode */
    .stApp {
        background-color: #FFFFFF !important;
    }
    
    /* Logo/Title */
    .app-title {
        font-size: 32px;
        font-weight: 600;
        text-align: center;
        color: #00520A;
        margin-bottom: 8px;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        text-align: center;
        color: #666;
        font-size: 14px;
        font-weight: 400;
        margin-bottom: 64px;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border: 1px solid #e5e5e5;
        border-radius: 0px;
        padding: 12px 16px;
        font-size: 15px;
        background: #FFFFFF;
        color: #1a1a1a;
        transition: all 0.2s ease;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: #469110;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #469110;
        box-shadow: 0 0 0 3px rgba(70, 145, 16, 0.05);
    }
    
    .stTextInput > label, .stSelectbox > label, .stTextArea > label {
        font-weight: 500;
        color: #1a1a1a;
        font-size: 13px;
        margin-bottom: 8px;
        letter-spacing: -0.2px;
    }
    
    /* Select Box */
    .stSelectbox > div > div {
        background: #FFFFFF !important;
    }
    
    .stSelectbox > div > div > div {
        background: #FFFFFF !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 0px !important;
    }
    
    .stSelectbox > div > div > div:hover {
        border-color: #469110 !important;
    }
    
    .stSelectbox [data-baseweb="select"] {
        background: #FFFFFF !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div {
        background: #FFFFFF !important;
        border: 1px solid #e5e5e5 !important;
        border-radius: 0px !important;
        padding: 12px 16px !important;
        color: #1a1a1a !important;
    }
    
    .stSelectbox [data-baseweb="select"] > div:hover {
        border-color: #469110 !important;
    }
    
    /* Text Area */
    .stTextArea > div > div > textarea {
        border: 1px solid #e5e5e5;
        border-radius: 0px;
        padding: 12px 16px;
        font-size: 15px;
        background: #FFFFFF;
        color: #1a1a1a;
        transition: all 0.2s ease;
        min-height: 200px;
    }
    
    .stTextArea > div > div > textarea:hover {
        border-color: #469110;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #469110;
        box-shadow: 0 0 0 3px rgba(70, 145, 16, 0.05);
    }
    
    /* Primary Button */
    .stButton > button,
    .stFormSubmitButton > button {
        background: #00520A !important;
        color: white !important;
        border: none !important;
        border-radius: 0px !important;
        padding: 14px 24px !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        width: 100% !important;
        transition: all 0.2s ease !important;
        letter-spacing: -0.2px !important;
    }
    
    .stButton > button:hover,
    .stFormSubmitButton > button:hover {
        background: #469110 !important;
        transform: translateY(-1px) !important;
        border: none !important;
    }
    
    .stButton > button:active,
    .stFormSubmitButton > button:active {
        transform: translateY(1px) !important;
    }
    
    /* Success/Error Messages */
    .stAlert {
        border-radius: 0px;
        border: 1px solid #e5e5e5;
        padding: 16px;
        background: #fafafa;
    }
    
    /* Divider */
    hr {
        margin: 32px 0;
        border: none;
        border-top: 1px solid #e5e5e5;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0px;
        border-bottom: 1px solid #e5e5e5;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 0px;
        padding: 12px 24px;
        font-size: 14px;
        font-weight: 500;
        color: #666;
        background: transparent;
        border-bottom: 2px solid transparent;
    }
    
    .stTabs [aria-selected="true"] {
        color: #00520A;
        border-bottom: 2px solid #00520A;
        background: transparent;
    }
    
    /* User Info Bar */
    .user-info {
        background: #00520A;
        color: white;
        padding: 16px 24px;
        margin-bottom: 32px;
        font-size: 14px;
        border: 1px solid #00520A;
    }
    
    /* Welcome Message */
    .welcome-message {
        color: #00520A;
        font-size: 24px;
        font-weight: 600;
        margin-bottom: 16px;
        letter-spacing: -0.5px;
    }
    
    /* Link Text */
    .link-text {
        text-align: center;
        margin-top: 32px;
        color: #666;
        font-size: 14px;
    }
    
    .link-text a {
        color: #469110;
        text-decoration: none;
        font-weight: 500;
    }
    
    .link-text a:hover {
        color: #00520A;
    }
    
    /* Secondary Actions */
    .secondary-action {
        text-align: center;
        margin-top: 12px;
    }
    
    /* Essay Prompt Card */
    .essay-prompt {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .essay-prompt h3 {
        color: #00520A;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 12px;
        letter-spacing: -0.3px;
    }
    
    .essay-prompt p {
        color: #666;
        font-size: 14px;
        line-height: 1.6;
    }
    
    /* Stats Grid */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
        margin-bottom: 32px;
    }
    
    .stat-card {
        background: #fafafa;
        border: 1px solid #e5e5e5;
        padding: 20px;
        text-align: center;
    }
    
    .stat-value {
        font-size: 24px;
        font-weight: 600;
        color: #00520A;
        letter-spacing: -0.5px;
    }
    
    .stat-label {
        font-size: 13px;
        color: #666;
        margin-top: 4px;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# DATABASE INITIALIZATION
# =========================

@st.cache_resource
def get_database_connection():
    """Initialize database connection (cached)"""
    return initialize_database()

# =========================
# SESSION STATE MANAGEMENT
# =========================

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None
    if 'user_info' not in st.session_state:
        st.session_state.user_info = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

# =========================
# AUTH PAGES
# =========================

def login_page(conn):
    """Clean minimal login page"""
    
    # Logo and title
    st.markdown('<h1 class="app-title">Parloir</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Votre professeur de français IA</p>', unsafe_allow_html=True)
    
    # Login form
    with st.form("login_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="votre@email.com", key="login_email")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="login_password")
        
        submit = st.form_submit_button("Se connecter")
        
        if submit:
            if not email or not password:
                st.error("Veuillez remplir tous les champs")
            else:
                success, message, tokens = login_user(conn, email, password)
                
                if success:
                    st.session_state.authenticated = True
                    st.session_state.access_token = tokens['access_token']
                    st.session_state.refresh_token = tokens['refresh_token']
                    st.session_state.user_info = tokens['user_info']
                    st.success("Connexion réussie")
                    st.rerun()
                else:
                    st.error(message)
    
    # Divider
    st.markdown("---")
    
    # Switch to signup
    st.markdown('<div class="secondary-action">', unsafe_allow_html=True)
    if st.button("Créer un compte", key="to_signup", use_container_width=True):
        st.session_state.page = 'signup'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

def signup_page(conn):
    """Clean minimal signup page"""
    
    st.markdown('<h1 class="app-title">Rejoignez Parloir</h1>', unsafe_allow_html=True)
    st.markdown('<p class="app-subtitle">Commencez votre voyage en français</p>', unsafe_allow_html=True)
    
    # Signup form
    with st.form("signup_form", clear_on_submit=False):
        email = st.text_input("Email", placeholder="votre@email.com", key="signup_email")
        password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="signup_password")
        confirm_password = st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••", key="confirm_password")
        
        st.markdown("---")
        
        learning_style = st.selectbox(
            "Style d'apprentissage",
            ["patient_mentor", "french_friend", "strict_professor", "exam_coach"],
            format_func=lambda x: {
                "patient_mentor": "Patient Mentor",
                "french_friend": "French Friend",
                "strict_professor": "Strict Professor",
                "exam_coach": "Exam Coach"
            }[x]
        )
        
        level = st.selectbox(
            "Niveau actuel",
            ["A1", "A2", "B1", "B2", "C1", "C2"],
            index=1
        )
        
        st.markdown("---")
        
        submit = st.form_submit_button("Créer mon compte")
        
        if submit:
            if not email or not password or not confirm_password:
                st.error("Veuillez remplir tous les champs")
            elif password != confirm_password:
                st.error("Les mots de passe ne correspondent pas")
            else:
                success, message, user_id = register_user(
                    conn, email, password, learning_style, level
                )
                
                if success:
                    st.success("Compte créé avec succès")
                    st.session_state.page = 'login'
                    st.rerun()
                else:
                    st.error(message)
    
    # Switch to login
    st.markdown('<div class="secondary-action">', unsafe_allow_html=True)
    if st.button("Se connecter", key="to_login", use_container_width=True):
        st.session_state.page = 'login'
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN APP (Protected)
# =========================

def main_app(conn):
    """Main application interface"""
    
    user = st.session_state.user_info
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<h1 class="welcome-message">Bonjour, {user["email"].split("@")[0]}</h1>', unsafe_allow_html=True)
    
    with col2:
        if st.button("Déconnexion", key="logout", use_container_width=True):
            logout_user(conn, user['id'])
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_info = None
            st.rerun()
    
    # User info bar
    st.markdown(f"""
    <div class="user-info">
        Niveau: {user['level']} | Style: {user['learning_style'].replace('_', ' ').title()}
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation tabs
    tab1, tab2, tab3 = st.tabs(["Conversation", "Mini Essais", "Progrès"])
    
    with tab1:
        chat_interface()
    
    with tab2:
        essay_interface()
    
    with tab3:
        progress_interface(user)

# =========================
# CHAT INTERFACE
# =========================

def chat_interface():
    """Chat/conversation interface"""
    
    st.markdown("### Conversation")
    
    st.info("L'interface de chat sera disponible bientôt. Votre système d'authentification fonctionne parfaitement.")
    
    # Placeholder for future chat
    st.text_area(
        "Votre message",
        placeholder="Écrivez en français...",
        height=100,
        key="chat_input"
    )
    
    if st.button("Envoyer", key="send_chat", use_container_width=True):
        st.success("Message envoyé (fonctionnalité à venir)")

# =========================
# ESSAY INTERFACE
# =========================

def essay_interface():
    """Daily mini essay interface"""
    
    st.markdown("### Mini Essais Quotidiens")
    
    # Essay prompt card
    st.markdown("""
    <div class="essay-prompt">
        <h3>Sujet du jour</h3>
        <p>Décrivez votre routine matinale idéale. Que feriez-vous si vous aviez tout le temps du monde?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Essay writing area
    essay_text = st.text_area(
        "Votre essai",
        placeholder="Commencez à écrire en français...",
        height=300,
        key="essay_input",
        help="Visez 100-200 mots"
    )
    
    # Word count
    if essay_text:
        word_count = len(essay_text.split())
        st.markdown(f"**Nombre de mots:** {word_count}")
    
    # Submit button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("Soumettre pour correction", key="submit_essay", use_container_width=True):
            if essay_text:
                st.success("Essai soumis! La correction sera disponible bientôt.")
            else:
                st.error("Veuillez écrire quelque chose avant de soumettre")
    
    with col2:
        if st.button("Nouveau sujet", key="new_topic", use_container_width=True):
            st.info("Nouveau sujet généré (fonctionnalité à venir)")
    
    st.markdown("---")
    
    # Past essays (placeholder)
    st.markdown("### Essais précédents")
    st.info("Vos essais corrigés apparaîtront ici")

# =========================
# PROGRESS INTERFACE
# =========================

def progress_interface(user):
    """Progress tracking interface"""
    
    st.markdown("### Vos progrès")
    
    # Stats grid
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Conversations</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Essais</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">0</div>
            <div class="stat-label">Jours actifs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Current level
    st.markdown("### Niveau actuel")
    st.markdown(f"**{user['level']}** - Élémentaire")
    
    st.markdown("---")
    
    # Weaknesses (placeholder)
    st.markdown("### Points à améliorer")
    st.info("Vos points faibles seront affichés ici après quelques conversations")

# =========================
# MAIN APP LOGIC
# =========================

def main():
    """Main application entry point"""
    
    # Load custom CSS
    load_css()
    
    # Initialize session state
    init_session_state()
    
    # Get database connection
    conn = get_database_connection()
    
    # Route based on authentication status
    if st.session_state.authenticated:
        # Verify token is still valid
        valid, user_info = verify_access_token(conn, st.session_state.access_token)
        
        if valid:
            main_app(conn)
        else:
            # Token expired
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.warning("Session expirée. Veuillez vous reconnecter.")
            st.rerun()
    else:
        # Show auth pages
        if st.session_state.page == 'login':
            login_page(conn)
        else:
            signup_page(conn)

if __name__ == "__main__":
    main()
