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
    page_title="Parloir - Your French AI Tutor",
    page_icon="🇫🇷",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CUSTOM CSS
# =========================

def load_css():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main Container */
    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 0;
    }
    
    /* Auth Card Container */
    .auth-card {
        background: white;
        padding: 3rem 2.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        max-width: 440px;
        margin: 4rem auto;
    }
    
    /* Logo/Title */
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Form Styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e2e8f0;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        transition: all 0.2s;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button Styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
    }
    
    /* Secondary Button */
    .secondary-button {
        background: transparent !important;
        color: #667eea !important;
        border: 2px solid #667eea !important;
    }
    
    /* Select Box */
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 1.5px solid #e2e8f0;
        padding: 0.75rem 1rem;
    }
    
    /* Success/Error Messages */
    .stAlert {
        border-radius: 8px;
        border: none;
        padding: 1rem;
    }
    
    /* Chat Container */
    .chat-container {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin: 2rem auto;
        max-width: 800px;
    }
    
    /* User Info Bar */
    .user-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Divider */
    .divider {
        text-align: center;
        margin: 2rem 0;
        color: #94a3b8;
        font-size: 0.875rem;
    }
    
    /* Link Styling */
    .link-text {
        text-align: center;
        margin-top: 1.5rem;
        color: #64748b;
        font-size: 0.9rem;
    }
    
    .link-text a {
        color: #667eea;
        text-decoration: none;
        font-weight: 600;
    }
    
    .link-text a:hover {
        text-decoration: underline;
    }
    
    /* Welcome Message */
    .welcome-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    /* Label Styling */
    .stTextInput > label, .stSelectbox > label {
        font-weight: 500;
        color: #1e293b;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
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
    """Beautiful login page"""
    
    # Container for centered card
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Logo and title
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
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
                        # Store tokens and user info in session
                        st.session_state.authenticated = True
                        st.session_state.access_token = tokens['access_token']
                        st.session_state.refresh_token = tokens['refresh_token']
                        st.session_state.user_info = tokens['user_info']
                        st.success("Connexion réussie! Bienvenue! 🎉")
                        st.rerun()
                    else:
                        st.error(message)
        
        # Divider
        st.markdown('<div class="divider">ou</div>', unsafe_allow_html=True)
        
        # Switch to signup
        if st.button("Créer un compte", key="to_signup", use_container_width=True):
            st.session_state.page = 'signup'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def signup_page(conn):
    """Beautiful signup page"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown('<h1 class="app-title">Rejoignez Parloir</h1>', unsafe_allow_html=True)
        st.markdown('<p class="app-subtitle">Commencez votre voyage en français</p>', unsafe_allow_html=True)
        
        # Signup form
        with st.form("signup_form", clear_on_submit=False):
            email = st.text_input("Email", placeholder="votre@email.com", key="signup_email")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="signup_password")
            confirm_password = st.text_input("Confirmer le mot de passe", type="password", placeholder="••••••••", key="confirm_password")
            
            learning_style = st.selectbox(
                "Style d'apprentissage",
                ["patient_mentor", "french_friend", "strict_professor", "exam_coach"],
                format_func=lambda x: {
                    "patient_mentor": "🌟 Patient Mentor",
                    "french_friend": "😊 French Friend",
                    "strict_professor": "📚 Strict Professor",
                    "exam_coach": "🎯 Exam Coach"
                }[x]
            )
            
            level = st.selectbox(
                "Niveau actuel",
                ["A1", "A2", "B1", "B2", "C1", "C2"],
                index=1  # Default to A2
            )
            
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
                        st.success("Compte créé! Connectez-vous maintenant 🎉")
                        # Auto-switch to login after 2 seconds
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(message)
        
        # Divider
        st.markdown('<div class="divider">Déjà un compte?</div>', unsafe_allow_html=True)
        
        # Switch to login
        if st.button("Se connecter", key="to_login", use_container_width=True):
            st.session_state.page = 'login'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# =========================
# MAIN APP (Protected)
# =========================

def main_app(conn):
    """Main application interface (protected)"""
    
    user = st.session_state.user_info
    
    # Header with user info
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f'<h1 class="welcome-message">Bonjour, {user["email"].split("@")[0]}! 👋</h1>', unsafe_allow_html=True)
    
    with col2:
        if st.button("Se déconnecter", key="logout"):
            logout_user(conn, user['id'])
            st.session_state.authenticated = False
            st.session_state.access_token = None
            st.session_state.refresh_token = None
            st.session_state.user_info = None
            st.rerun()
    
    # User info card
    st.markdown(f"""
    <div class="user-info">
        <div>
            <strong>Niveau:</strong> {user['level']} &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Style:</strong> {user['learning_style']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    st.markdown("### 💬 Conversation")
    
    # Placeholder for chat (we'll build this in the next phase)
    st.info("🚧 Chat interface coming soon! Your authentication is working perfectly.")
    
    # Test area
    with st.expander("🧪 Test Your Session"):
        st.json({
            "authenticated": st.session_state.authenticated,
            "user_id": user['id'],
            "email": user['email'],
            "level": user['level'],
            "learning_style": user['learning_style']
        })
    
    st.markdown('</div>', unsafe_allow_html=True)

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
            # Token expired - log out
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