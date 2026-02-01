import jwt
from flask import request, jsonify, g
from functools import wraps
from config import JWT_SECRET
from datetime import datetime, timedelta

def encode_auth_token(user_id, role):
    payload = {
        'exp': datetime.utcnow() + timedelta(days=1),
        'iat': datetime.utcnow(),
        'sub': str(user_id),
        'role': role
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def decode_auth_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(' ')[-1]
        if not token:
            return jsonify({'error': 'Token is missing!'}), 401
        data = decode_auth_token(token)
        if not data:
            return jsonify({'error': 'Token is invalid or expired!'}), 401
        g.user_id = data['sub']
        g.user_role = data['role']
        return f(*args, **kwargs)
    return decorated 