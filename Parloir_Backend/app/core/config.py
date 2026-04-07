from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str
    
    # JWT Secret
    SECRET_KEY: str
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:8000"
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # JWT Settings
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Anthropic API
    ANTHROPIC_API_KEY: str
    
    #Cloudinary
    CLOUDINARY_CLOUD_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str
    
    #Email Resend
    RESEND_API_KEY: str
    SENDER_EMAIL: str = "onboarding@resend.dev"
    FRONTEND_URL: str = "http://localhost:5500"
    
    class Config:
        env_file = ".env"

# Create a single instance
settings = Settings()