import resend
import httpx
from app.core.config import settings
from typing import Optional

resend.api_key = settings.RESEND_API_KEY

def send_verification_email(to_email: str, verification_url: str, username: str) -> bool:
    """Send email verification email"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #f5f8f6;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #00520a 0%, #469110 100%);
                padding: 40px;
                text-align: center;
            }}
            .logo {{
                color: white;
                font-size: 32px;
                font-weight: 900;
                letter-spacing: -1px;
            }}
            .accent {{
                color: #E673AC;
            }}
            .content {{
                padding: 40px;
            }}
            h1 {{
                color: #00520a;
                font-size: 24px;
                font-weight: 900;
                margin: 0 0 20px 0;
            }}
            p {{
                color: #475569;
                font-size: 16px;
                line-height: 1.6;
                margin: 0 0 20px 0;
            }}
            .button {{
                display: inline-block;
                background-color: #E673AC;
                color: #000000;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 700;
                font-size: 16px;
                margin: 20px 150px;
            }}
            .button:hover {{
                background-color: #660033;
                color: #FFFFFF
            }}
            .footer {{
                background-color: #f8fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                color: #94a3b8;
                font-size: 12px;
                margin: 5px 0;
            }}
            .expiry {{
                padding: 12px 0;
                margin: 20px 0;
                border-radius: 4px;
            }}
            .expiry p {{
                color: #800000;
                font-size: 14px;
                margin: 0;
            }}
            .Final {{
                color: #00520a;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">Parloir<span class="accent">.</span></div>
            </div>
            
            <div class="content">
                <h1>Bienvenue sur Parloir, {username}! 🎉</h1>
                
                <p>Merci de vous être inscrit ! Pour commencer votre voyage d'apprentissage du français, veuillez vérifier votre adresse email.</p>
                
                <p>Cliquez sur le bouton ci-dessous pour activer votre compte :</p>
                
                <a href="{verification_url}" class="button">
                    Vérifier mon email
                </a>
                
                <div class="expiry">
                    <p><strong>Ce lien expire dans 24 heures.</strong> Si vous n'avez pas demandé cette vérification, vous pouvez ignorer cet email en toute sécurité.</p>
                </div>
                
                <p class="Final">Si le bouton ne fonctionne pas, copiez et collez ce lien dans votre navigateur :</p>
                <p style="word-break: break-all; color: #469110; font-size: 12px;">{verification_url}</p>
            </div>
            
            <div class="footer">
                <p>© 2026 Parloir. Keep writing, keep learning.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        with httpx.Client(verify=False) as client:  # bypasses SSL issue
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.SENDER_EMAIL,
                    "to": [to_email],
                    "subject": "Vérifiez votre email - Parloir",
                    "html": html_content,
                }
            )
            response.raise_for_status()
        print(f"✅ Verification email sent to {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def send_welcome_email(to_email: str, username: str) -> bool:
    """Send welcome email after verification"""
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Inter', sans-serif;
                background-color: #f5f8f6;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: white;
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #00520a 0%, #469110 100%);
                padding: 40px;
                text-align: center;
            }}
            .logo {{
                color: white;
                font-size: 32px;
                font-weight: 900;
            }}
            .content {{
                padding: 40px;
            }}
            h1 {{
                color: #00520a;
                font-size: 24px;
                font-weight: 900;
            }}
            p {{
                color: #475569;
                font-size: 16px;
                line-height: 1.6;
            }}
            .button {{
                display: inline-block;
                background-color: #E673AC;
                color: white;
                text-decoration: none;
                padding: 16px 32px;
                border-radius: 8px;
                font-weight: 700;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">parloir<span style="color: #E673AC;">.</span></div>
            </div>
            
            <div class="content">
                <h1>Email vérifié ! Bienvenue à bord, {username}! 🎉</h1>
                
                <p>Votre compte est maintenant activé ! Vous avez <strong>3 jours d'essai gratuit</strong> pour explorer toutes les fonctionnalités.</p>
                
                <p><strong>Pendant votre essai gratuit :</strong></p>
                <ul>
                    <li>✅ 10 messages avec le tuteur IA</li>
                    <li>✅ 2 corrections d'essais</li>
                    <li>✅ 3 quiz de compréhension</li>
                    <li>✅ Accès illimité au traducteur et à la liste de vocabulaire</li>
                </ul>
                
                <a href="{settings.FRONTEND_URL}" class="button">
                    🚀 Commencer maintenant
                </a>
                
                <p>Bon apprentissage !</p>
                <p><strong>L'équipe Parloir</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    try:
        with httpx.Client(verify=False) as client:  # bypasses SSL issue
            response = client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": settings.SENDER_EMAIL,
                    "to": [to_email],
                    "subject": "Bienvenue sur Parloir ! 🎉",
                    "html": html_content,
                }
            )
            response.raise_for_status()
        return True
        
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")
        return False