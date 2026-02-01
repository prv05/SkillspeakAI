from flask import Blueprint, request, jsonify, session, g
from models.user import create_user, get_user_by_email, check_password, get_user_by_id
from utils.jwt_utils import encode_auth_token, token_required

auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__)

@auth_bp.route('/signup', methods=['POST', 'OPTIONS'])
def signup():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        if get_user_by_email(data['email']):
            return jsonify({'error': 'User already exists'}), 400
        user_id = create_user(data)
        return jsonify({'message': 'User created successfully', 'user_id': str(user_id.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        user = get_user_by_email(data['email'])
        if not user or not check_password(user, data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        token = encode_auth_token(str(user['_id']), user.get('role', 'user'))
        return jsonify({
            'token': token, 
            'role': user.get('role', 'user'),
            'user': {
                'id': str(user['_id']), 
                'name': user.get('name'), 
                'email': user['email']
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
def me():
    try:
        user = get_user_by_email(session.get('email'))
        if not user:
            return jsonify({'error': 'User not found'}), 404
        user.pop('password', None)
        return jsonify(user) 
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@user_bp.route('/me', methods=['GET'])
@token_required
def get_current_user():
    user = get_user_by_id(g.user_id)
    if user:
        return jsonify({
            'name': user.get('name', ''),
            'email': user.get('email', '')
        }), 200
    return jsonify({'error': 'User not found'}), 404 