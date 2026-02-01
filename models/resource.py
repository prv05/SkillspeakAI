from mongo_client import mongo
from bson import ObjectId
from datetime import datetime

def create_resource(resource_data):
    resource_data['created_at'] = datetime.utcnow()
    return mongo.db.resources.insert_one(resource_data)

def get_resources_by_user(user_id):
    return list(mongo.db.resources.find({'user_id': user_id}))

def get_resource_by_id(resource_id):
    return mongo.db.resources.find_one({'_id': ObjectId(resource_id)})

def update_resource(resource_id, update_data):
    return mongo.db.resources.update_one({'_id': ObjectId(resource_id)}, {'$set': update_data})

def delete_resource(resource_id):
    return mongo.db.resources.delete_one({'_id': ObjectId(resource_id)}) 