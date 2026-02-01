from mongo_client import mongo
from bson import ObjectId
from datetime import datetime, timedelta

def create_session(session_data):
    # Auto-fill required fields with defaults if missing
    session_data.setdefault('session_id', f'session_{int(datetime.utcnow().timestamp())}')
    session_data.setdefault('user_id', None)
    session_data.setdefault('session_name', 'Interview Session')
    now_iso = datetime.utcnow().isoformat() + 'Z'
    session_data.setdefault('start_time', now_iso)
    session_data.setdefault('end_time', now_iso)  # Set to start_time initially
    session_data.setdefault('total_time_minutes', 0)
    session_data.setdefault('scores', 0)  # Or [] if you want a list
    session_data.setdefault('summary', "")
    # Ensure chats is an array of objects with required fields if provided, else empty array
    if 'chats' not in session_data or not isinstance(session_data['chats'], list):
        session_data['chats'] = []
    else:
        # Fill each chat with required fields if missing
        for chat in session_data['chats']:
            chat.setdefault('question', "")
            chat.setdefault('answer', "")
            chat.setdefault('ai_feedback', "")
            chat.setdefault('score', 0)
            chat.setdefault('summary', "")
            chat.setdefault('created_at', now_iso)
            chat.setdefault('updated_at', now_iso)
    session_data['created_at'] = datetime.utcnow()
    session_data['updated_at'] = datetime.utcnow()
    return mongo.db.session.insert_one(session_data)

def get_session_by_id(session_id):
    return mongo.db.session.find_one({'session_id': session_id})

def get_sessions_by_user(user_id):
    return list(mongo.db.session.find({'user_id': user_id}))

def update_session(session_id, update_data):
    update_data['updated_at'] = datetime.utcnow()
    return mongo.db.session.update_one({'session_id': session_id}, {'$set': update_data})

def add_chat_to_session(session_id, chat):
    return mongo.db.session.update_one({'session_id': session_id}, {'$push': {'chats': chat}, '$set': {'updated_at': datetime.utcnow()}}) 

def get_all_sessions():
    return list(mongo.db.session.find()) 

def get_sessions_today():
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    return list(mongo.db.session.find({
        'created_at': {
            '$gte': datetime(today.year, today.month, today.day),
            '$lt': datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        }
    })) 