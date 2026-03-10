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
    
    class Config:
        env_file = ".env"

# Create a single instance
settings = Settings()