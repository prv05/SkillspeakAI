from flask import Flask, render_template, make_response
from flask_cors import CORS
from mongo_client import mongo
from config import MONGO_URI, UPLOAD_FOLDER
import os
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from datetime import datetime

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500", "http://127.0.0.1:5501", "http://localhost:5500", "http://localhost:5501"], supports_credentials=True)  # Allow multiple frontend origins
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["MONGO_URI"] = "mongodb://localhost:27017/skillspeak_ai"

# JWT config
app.config["JWT_SECRET_KEY"] = "your-secret-key"  # Use a strong, random key in production!
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
jwt = JWTManager(app)

# MongoDB
mongo.init_app(app)
# Use mongo.db directly throughout the app

# Register blueprints
from routes.auth import auth_bp, user_bp
from routes.voice import voice_bp
from routes.feedback import feedback_bp
from routes.profile import profile_bp
from routes.dashboard import dashboard_bp
from routes.admin import admin_bp
from routes.session import session_bp

CORS(auth_bp, origins=["http://127.0.0.1:5500", "http://127.0.0.1:5501", "http://localhost:5500", "http://localhost:5501"], supports_credentials=True)
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(voice_bp, url_prefix='/api/voice')
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
app.register_blueprint(admin_bp, url_prefix='/api/admin')
app.register_blueprint(session_bp, url_prefix='/api/session')

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return {'error': 'Not found'}, 404

@app.errorhandler(500)
def server_error(e):
    return {'error': 'Server error'}, 500

# Add security headers to all responses
@app.after_request
def add_security_headers(response):
    # Remove restrictive CSP that blocks eval()
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self' http://127.0.0.1:5000;"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

@app.route('/')
def index():
    return {'message': 'SkillSpeak AI API is running!'}, 200

@app.route('/api/feedback/count')
def feedback_count():
    from mongo_client import mongo
    return {'count': mongo.db.feedback.count_documents({})}

@app.route('/admin-profile')
def admin_profile():
    # Replace with real admin data fetching logic
    admin_name = "Pratham Vernekar"  # Example, replace with DB/session fetch
    admin_email = "prathamvernekar05@gmail.com"  # Example, replace with DB/session fetch
    return render_template('admin.html', admin_name=admin_name, admin_email=admin_email)

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)