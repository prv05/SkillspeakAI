from mongo_client import mongo
from bson import ObjectId
from datetime import datetime

def get_setting(setting_key):
    """Get a system setting by key"""
    setting = mongo.db.system_settings.find_one({"setting_key": setting_key})
    return setting.get("setting_value") if setting else None

def set_setting(setting_key, setting_value, category="general", description=""):
    """Set or update a system setting"""
    setting_data = {
        "setting_key": setting_key,
        "setting_value": str(setting_value),
        "category": category,
        "description": description,
        "updated_at": datetime.utcnow()
    }
    
    # Check if setting exists
    existing = mongo.db.system_settings.find_one({"setting_key": setting_key})
    
    if existing:
        # Update existing setting
        return mongo.db.system_settings.update_one(
            {"setting_key": setting_key},
            {"$set": setting_data}
        )
    else:
        # Create new setting
        setting_data["_id"] = ObjectId()
        setting_data["created_at"] = datetime.utcnow()
        return mongo.db.system_settings.insert_one(setting_data)

def get_settings_by_category(category):
    """Get all settings in a specific category"""
    return list(mongo.db.system_settings.find({"category": category}))

def get_all_settings():
    """Get all system settings"""
    return list(mongo.db.system_settings.find().sort("category", 1))

def delete_setting(setting_key):
    """Delete a system setting"""
    return mongo.db.system_settings.delete_one({"setting_key": setting_key})

def get_app_settings():
    """Get common application settings"""
    settings = {}
    all_settings = get_all_settings()
    
    for setting in all_settings:
        settings[setting["setting_key"]] = setting["setting_value"]
    
    return settings

def is_maintenance_mode():
    """Check if maintenance mode is enabled"""
    maintenance_setting = get_setting("maintenance_mode")
    return maintenance_setting == "true"

def get_max_session_duration():
    """Get maximum session duration in minutes"""
    duration = get_setting("max_session_duration")
    return int(duration) if duration else 30

def is_feedback_enabled():
    """Check if feedback feature is enabled"""
    feedback_setting = get_setting("feedback_enabled")
    return feedback_setting != "false"  # Default to true if not set
