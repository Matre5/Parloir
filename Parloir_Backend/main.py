from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import auth, chat, profile, translate, word, essays

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    connect_to_mongo()
    yield
    # Shutdown: Close MongoDB connection
    close_mongo_connection()

app = FastAPI(
    title="Parloir API",
    version="1.0.0",
    description="Backend API for Parloir - French Learning Platform",
    lifespan=lifespan
)

# CORS - allows your HTML frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:5501",
        "http://localhost:5501" ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(translate.router, prefix="/api/translate", tags=["Translate"])
app.include_router(word.router, prefix="/api/words", tags=["Words"])
app.include_router(essays.router, prefix="/api/essays", tags=["Essays"])

# Basic route to test if API is running
@app.get("/")
def read_root():
    return {
        "message": "Parloir API is running! 🚀",
        "version": "1.0.0",
        "status": "healthy"
    }

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy"}