import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Connection
# Default to local MongoDB. To use Atlas, set the MONGO_URI environment variable.
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/skillspeak_ai')
MONGO_DBNAME = os.getenv('MONGO_DBNAME', 'skillspeak_ai')

JWT_SECRET = os.getenv('JWT_SECRET', 'supersecretjwtkey')
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/') 