from mongo_client import mongo
from datetime import datetime

def save_message(user_id, role, message, session_id=None, chat_id=None):
    doc = {
        "user_id": user_id,
        "role": role,
        "message": message,
        "timestamp": datetime.utcnow()
    }
    if session_id:
        doc["session_id"] = session_id
    if chat_id:
        doc["chat_id"] = chat_id
    return mongo.db.chats.insert_one(doc)

def get_chat_history(user_id, session_id=None, chat_id=None):
    query = {"user_id": user_id}
    if session_id:
        query["session_id"] = session_id
    if chat_id:
        query["chat_id"] = chat_id
    return list(mongo.db.chats.find(query).sort("timestamp", 1))

def get_all_chats():
    """Get all chat messages for admin monitoring"""
    return list(mongo.db.chats.find().sort("timestamp", -1)) 