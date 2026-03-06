from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.core.config import settings
import certifi

class MongoDB:
    client: MongoClient = None
    db = None

mongodb = MongoDB()

def connect_to_mongo():
    """Connect to MongoDB Atlas"""
    try:
        print(f"DEBUG: URI found in settings: {settings.MONGODB_URI[:25]}...") 
        
        mongodb.client = MongoClient(
            settings.MONGODB_URI,
            tlsCAFile=certifi.where()
        )

        mongodb.db = mongodb.client.parloir

        mongodb.client.admin.command("ping")

        print("✅ Connected to MongoDB!")

    except ConnectionFailure as e:
        print(f"❌ Could not connect to MongoDB: {e}")
        raise

def close_mongo_connection():
    """Close MongoDB connection"""
    if mongodb.client:
        mongodb.client.close()
        print("MongoDB connection closed")

def get_database():
    """Get database instance"""
    return mongodb.db