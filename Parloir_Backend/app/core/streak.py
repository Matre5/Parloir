from datetime import date, timedelta
from app.core.database import get_database
from bson import ObjectId

def update_streak(user_id: str):
    """Update streak whenever a user completes an essay or quiz"""
    print(f"🔥 update_streak called for user: {user_id}")
    db = get_database()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        print(f"❌ User not found: {user_id}")
        return
    
    print(f"✅ User found: {user.get('username')}, current_streak: {user.get('current_streak', 0)}")
    
    today = date.today().isoformat()
    last_activity = user.get("last_activity_date")
    current_streak = user.get("current_streak", 0)
    longest_streak = user.get("longest_streak", 0)
    
    if last_activity == today:
        print("Already counted today")
        return
    
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    if last_activity == yesterday:
        current_streak += 1
    else:
        current_streak = 1
    
    if current_streak > longest_streak:
        longest_streak = current_streak
    
    db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "last_activity_date": today
        }}
    )
    print(f"✅ Streak updated to {current_streak}")