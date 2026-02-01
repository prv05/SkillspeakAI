from flask import Blueprint, request, jsonify
from models.session import create_session, get_session_by_id, get_sessions_by_user, update_session, add_chat_to_session

session_bp = Blueprint('session', __name__)

@session_bp.route('/', methods=['POST'])
def create_session_route():
    data = request.json
    session_id = data.get('session_id')
    if not session_id:
        return jsonify({'error': 'session_id is required'}), 400
    create_session(data)
    return jsonify({'message': 'Session created'}), 201

@session_bp.route('/<session_id>', methods=['GET'])
def get_session(session_id):
    session = get_session_by_id(session_id)
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    return jsonify(session), 200

@session_bp.route('/user/<user_id>', methods=['GET'])
def get_sessions_for_user(user_id):
    print("Fetching sessions for user_id:", repr(user_id))
    sessions = get_sessions_by_user(user_id)
    return jsonify(sessions), 200

@session_bp.route('/<session_id>', methods=['PUT'])
def update_session_route(session_id):
    data = request.json
    update_session(session_id, data)
    return jsonify({'message': 'Session updated'}), 200

@session_bp.route('/<session_id>/add_chat', methods=['POST'])
def add_chat(session_id):
    chat = request.json
    add_chat_to_session(session_id, chat)
    return jsonify({'message': 'Chat added to session'}), 200 