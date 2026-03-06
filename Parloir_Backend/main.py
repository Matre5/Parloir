from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import Settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.routers import auth

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
    allow_origins=[Settings.FRONTEND_URL, "http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth router
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

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