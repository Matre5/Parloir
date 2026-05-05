from datetime import date, timedelta
from app.core.database import get_database
from bson import ObjectId

def update_streak(user_id: str):
    """whenever a user completes an essay or quiz"""
    db = get_database()
    user = db.users.find_one({"_id": ObjectId(user_id)})
    
    if not user:
        return
    
    today = date.today().isoformat()
    last_activity = user.get("last_activity_date")
    current_streak = user.get("current_streak", 0)
    longest_streak = user.get("longest_streak", 0)
    
    if last_activity == today:
        # Already counted today, do nothing
        return
    
    from datetime import timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    
    if last_activity == yesterday:
        # Consecutive day — increment
        current_streak += 1
    else:
        # Missed a day or first time — reset
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