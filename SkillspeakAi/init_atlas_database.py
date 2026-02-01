#!/usr/bin/env python3
"""
Database initialization script for MongoDB Atlas
This script will create all necessary collections and indexes for SkillSpeak AI
"""

from mongo_client import mongo
from datetime import datetime
from bson import ObjectId

def init_database():
    """Initialize the database with all required collections"""
    print("🚀 Initializing SkillSpeak AI Database in MongoDB Atlas...")
    
    # Create collections (MongoDB creates collections automatically when you insert data)
    collections = [
        'users',
        'session', 
        'feedback',
        'suggest_feedback',
        'system_settings'
    ]
    
    print(f"📋 Collections to be created: {', '.join(collections)}")
    
    # Create indexes for better performance
    create_indexes()
    
    # Insert sample data if collections are empty
    insert_sample_data()
    
    print("✅ Database initialization completed!")

def create_indexes():
    """Create indexes for better query performance"""
    print("🔍 Creating database indexes...")
    
    # Users collection indexes
    mongo.db.users.create_index("email", unique=True)
    mongo.db.users.create_index("role")
    mongo.db.users.create_index("status")
    mongo.db.users.create_index("created_at")
    
    # Session collection indexes
    mongo.db.session.create_index("session_id", unique=True)
    mongo.db.session.create_index("user_id")
    mongo.db.session.create_index("created_at")
    
    # Feedback collection indexes
    mongo.db.feedback.create_index("user_id")
    mongo.db.feedback.create_index("created_at")
    
    # Suggest feedback collection indexes
    mongo.db.suggest_feedback.create_index("user_id")
    mongo.db.suggest_feedback.create_index("status")
    mongo.db.suggest_feedback.create_index("created_at")
    
    # System settings collection indexes
    mongo.db.system_settings.create_index("setting_key", unique=True)
    mongo.db.system_settings.create_index("category")
    mongo.db.system_settings.create_index("updated_at")
    

    
    print("✅ Indexes created successfully!")

def insert_sample_data():
    """Insert sample data if collections are empty"""
    print("📝 Checking for sample data...")
    
    # Check if users collection is empty
    if mongo.db.users.count_documents({}) == 0:
        print("👥 Creating sample admin user...")
        sample_admin = {
            "_id": ObjectId(),
            "name": "Admin User",
            "email": "admin@skillspeak.ai",
            "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/8KqKqKq",  # password123
            "role": "admin",
            "status": "unblocked",
            "created_at": datetime.utcnow()
        }
        mongo.db.users.insert_one(sample_admin)
        print("✅ Sample admin user created!")
    
    # Check if feedback collection is empty
    if mongo.db.feedback.count_documents({}) == 0:
        print("💬 Creating sample feedback...")
        sample_feedback = {
            "_id": ObjectId(),
            "user_id": "sample_user",
            "message": "Great platform for improving communication skills!",
            "rating": 5,
            "created_at": datetime.utcnow()
        }
        mongo.db.feedback.insert_one(sample_feedback)
        print("✅ Sample feedback created!")
    
    # Check if system_settings collection is empty
    if mongo.db.system_settings.count_documents({}) == 0:
        print("⚙️ Creating default system settings...")
        default_settings = [
            {
                "_id": ObjectId(),
                "setting_key": "app_name",
                "setting_value": "SkillSpeak AI",
                "category": "general",
                "description": "Application name",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "setting_key": "app_version",
                "setting_value": "1.0.0",
                "category": "general",
                "description": "Application version",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "setting_key": "maintenance_mode",
                "setting_value": "false",
                "category": "system",
                "description": "Maintenance mode status",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "setting_key": "max_session_duration",
                "setting_value": "30",
                "category": "session",
                "description": "Maximum session duration in minutes",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            },
            {
                "_id": ObjectId(),
                "setting_key": "feedback_enabled",
                "setting_value": "true",
                "category": "features",
                "description": "Enable feedback feature",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        ]
        mongo.db.system_settings.insert_many(default_settings)
        print("✅ Default system settings created!")
    
    print("✅ Sample data check completed!")

def verify_connection():
    """Verify connection to MongoDB Atlas"""
    try:
        # Test the connection
        mongo.db.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        return True
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB Atlas: {e}")
        return False

def show_collection_stats():
    """Show statistics for all collections"""
    print("\n📊 Database Statistics:")
    print("-" * 40)
    
    collections = ['users', 'session', 'feedback', 'suggest_feedback', 'system_settings']
    
    for collection_name in collections:
        try:
            count = mongo.db[collection_name].count_documents({})
            print(f"{collection_name:20} : {count:5} documents")
        except Exception as e:
            print(f"{collection_name:20} : Error - {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("SkillSpeak AI - MongoDB Atlas Database Setup")
    print("=" * 50)
    
    # Verify connection first
    if verify_connection():
        # Initialize the database
        init_database()
        
        # Show statistics
        show_collection_stats()
        
        print("\n🎉 Database setup completed successfully!")
        print("You can now run your SkillSpeak AI application with MongoDB Atlas!")
    else:
        print("❌ Please check your MongoDB Atlas connection string in config.py")
        print("Make sure to replace <username>, <password>, and <cluster-url> with your actual values.")
