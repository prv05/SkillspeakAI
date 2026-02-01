from flask import Blueprint, request, jsonify, g
from utils.jwt_utils import token_required
from models.user import get_user_by_id, update_user_profile

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/me', methods=['GET'])
@token_required
def get_profile():
    user = get_user_by_id(g.user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    user.pop('password', None)
    user['_id'] = str(user['_id'])
    return jsonify(user)

@profile_bp.route('/me', methods=['PUT'])
@token_required
def update_profile():
    data = request.json
    update_user_profile(g.user_id, data)
    return jsonify({'message': 'Profile updated'}) 

@profile_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'error': 'Current and new password are required'}), 400
        
        # Get user and verify current password
        from models.user import get_user_by_id, update_user_password
        from werkzeug.security import check_password_hash
        
        user = get_user_by_id(g.user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if not check_password_hash(user['password'], current_password):
            return jsonify({'error': 'Current password is incorrect'}), 400
        
        # Update password
        update_user_password(g.user_id, new_password)
        
        return jsonify({'message': 'Password changed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 