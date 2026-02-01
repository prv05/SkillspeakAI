from mongo_client import mongo
from bson import ObjectId
from datetime import datetime

def create_feedback(feedback_data):
    feedback_data['created_at'] = datetime.utcnow()
    return mongo.db.feedback.insert_one(feedback_data)

def get_feedback_by_user(user_id):
    return list(mongo.db.feedback.find({'user_id': user_id}))

def get_feedback_by_id(feedback_id):
    return mongo.db.feedback.find_one({'_id': ObjectId(feedback_id)})

def update_feedback(feedback_id, update_data):
    return mongo.db.feedback.update_one({'_id': ObjectId(feedback_id)}, {'$set': update_data})

def delete_feedback(feedback_id):
    return mongo.db.feedback.delete_one({'_id': ObjectId(feedback_id)})

def get_all_feedback():
    return list(mongo.db.feedback.find())

def create_suggest_feedback(suggest_data):
    suggest_data['created_at'] = datetime.utcnow()
    suggest_data['status'] = suggest_data.get('status', 'seen')
    return mongo.db.suggest_feedback.insert_one(suggest_data)

def get_suggest_feedback_by_user(user_id):
    return list(mongo.db.suggest_feedback.find({'user_id': user_id}))

def get_all_suggest_feedback():
    return list(mongo.db.suggest_feedback.find())

def update_suggest_feedback_status(suggest_id, status):
    return mongo.db.suggest_feedback.update_one({'_id': ObjectId(suggest_id)}, {'$set': {'status': status}})

def delete_suggest_feedback(suggest_id):
    return mongo.db.suggest_feedback.delete_one({'_id': ObjectId(suggest_id)}) 