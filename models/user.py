from mongo_client import mongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime, timedelta

def create_user(user_data):
    from bson import ObjectId
    from datetime import datetime
    # Ensure all required fields are present
    user_doc = {}
    user_doc['_id'] = ObjectId()  # Always generate a new ObjectId
    user_doc['name'] = user_data.get('name', '')
    user_doc['email'] = user_data['email']
    user_doc['password'] = generate_password_hash(user_data['password'])
    user_doc['role'] = user_data.get('role', 'user')
    user_doc['status'] = user_data.get('status', 'unblocked')
    user_doc['created_at'] = datetime.utcnow()
    return mongo.db.users.insert_one(user_doc)

def get_user_by_email(email):
    return mongo.db.users.find_one({"email": email})

def get_user_by_id(user_id):
    return mongo.db.users.find_one({"_id": ObjectId(user_id)})

def update_user_profile(user_id, update_data):
    return mongo.db.users.update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

def check_password(user, password):
    return check_password_hash(user['password'], password)

def get_all_users():
    return list(mongo.db.users.find())

def delete_user(user_id):
    return mongo.db.users.delete_one({"_id": ObjectId(user_id)})

def set_user_as_admin(user_id):
    """Set a user as admin"""
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"role": "admin"}}
    )

def is_admin(user_id):
    """Check if user is admin"""
    user = get_user_by_id(user_id)
    return user and user.get('role') == 'admin'

def update_user_password(user_id, new_password):
    """Update user password"""
    hashed_password = generate_password_hash(new_password)
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"password": hashed_password}}
    )

def block_user(user_id):
    """Block a user"""
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"status": "blocked", "blocked_at": datetime.utcnow()}}
    )

def unblock_user(user_id):
    """Unblock a user"""
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$unset": {"status": "", "blocked_at": ""}}
    )

def remove_admin_role(user_id):
    """Remove admin role from user"""
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"role": "user"}}
    )

def reset_user_password(user_id):
    """Reset user password to default"""
    default_password = "password123"  # You can change this default
    hashed_password = generate_password_hash(default_password)
    return mongo.db.users.update_one(
        {"_id": ObjectId(user_id)}, 
        {"$set": {"password": hashed_password}}
    )

def get_user_stats(user_id):
    """Get user statistics"""
    user = get_user_by_id(user_id)
    if not user:
        return None
    
    # Count user's feedback
    feedback_count = mongo.db.feedback.count_documents({"user_id": str(user_id)})
    
    # Count user's chat sessions (handle legacy documents where user_id stored as name or as string id)
    user_name = user.get('name', '')
    user_id_str = str(user['_id'])
    session_filter = {
        '$or': [
            {'user_id': user_id_str},
            {'user_id': user_name}
        ]
    }
    # Use the correct collection name: 'session'
    session_count = mongo.db.session.count_documents(session_filter)

    # Get last activity from the same collection with the same filter
    last_session = mongo.db.session.find_one(
        session_filter,
        sort=[('created_at', -1)]
    )
    
    return {
        "user": user,
        "feedback_count": feedback_count,
        "session_count": session_count,
        "last_activity": last_session.get("created_at") if last_session else None
    } 

def get_users_today():
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    return list(mongo.db.users.find({
        'created_at': {
            '$gte': datetime(today.year, today.month, today.day),
            '$lt': datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        }
    })) 

def get_all_admin_users():
    return list(mongo.db.users.find({'role': 'admin'}))

def get_admin_users_today():
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    return list(mongo.db.users.find({
        'role': 'admin',
        'created_at': {
            '$gte': datetime(today.year, today.month, today.day),
            '$lt': datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        }
    })) 

def get_daily_vs_nonfrequent_users():
    from datetime import datetime, timedelta
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    # Get all users
    all_users = list(mongo.db.users.find())
    user_ids = [u['_id'] for u in all_users]
    # Get users with a session today
    sessions_today = mongo.db.session.distinct('user_id', {
        'created_at': {
            '$gte': datetime(today.year, today.month, today.day),
            '$lt': datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        }
    })
    daily_user_ids = set(sessions_today)
    daily_count = len(daily_user_ids)
    non_frequent_count = len([uid for uid in user_ids if uid not in daily_user_ids])
    return {'daily': daily_count, 'non_frequent': non_frequent_count} 