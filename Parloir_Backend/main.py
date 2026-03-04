from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Parloir API",
    version="1.0.0",
    description="Backend API for Parloir - French Learning Platform"
)

# CORS - allows your HTML frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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