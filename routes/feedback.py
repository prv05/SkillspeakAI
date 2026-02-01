from flask import Blueprint, request, jsonify
from models.feedback import create_feedback, get_feedback_by_user, get_feedback_by_id, update_feedback, delete_feedback, get_all_feedback, create_suggest_feedback, get_suggest_feedback_by_user, get_all_suggest_feedback, update_suggest_feedback_status, delete_suggest_feedback
from utils.ai_utils import get_ai_feedback
import json
from flask_jwt_extended import jwt_required, get_jwt_identity

feedback_bp = Blueprint('feedback', __name__)

@feedback_bp.route('/', methods=['POST'])
def add_feedback():
    """Add user feedback/suggestion for admin"""
    try:
        data = request.json
        if not data or 'input' not in data:
            return jsonify({'error': 'Input field is required'}), 400
        
        # Create feedback entry
        feedback_data = {
            'user_id': data.get('user_id', 'anonymous'),
            'input': data['input'],
            'type': 'user_suggestion',
            'status': 'pending',
            'created_at': data.get('created_at')
        }
        
        feedback_id = create_feedback(feedback_data)
        return jsonify({
            'message': 'Feedback submitted successfully',
            'feedback_id': str(feedback_id)
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/generate', methods=['POST'])
def generate_feedback():
    """Generate AI feedback for user input and store it automatically"""
    try:
        data = request.json
        if not data or 'input' not in data:
            return jsonify({'error': 'Input field is required'}), 400
        user_id = data.get('user_id', 'anonymous')
        # Get AI feedback using Ollama
        ai_response = get_ai_feedback(data['input'])
        # Parse AI response
        try:
            feedback_data = json.loads(ai_response)
        except json.JSONDecodeError:
            # If AI response is not valid JSON, create a structured response
            feedback_data = {
                'summary': ai_response[:200] + '...' if len(ai_response) > 200 else ai_response,
                'score': 7.5,
                'suggestions': ['Continue practicing', 'Focus on clarity', 'Work on confidence']
            }
        # Store AI feedback as type 'ai_feedback'
        create_feedback({
            'user_id': user_id,
            'input': data['input'],
            'type': 'ai_feedback',
            'status': 'completed',
            'ai_feedback': feedback_data.get('summary', '')
        })
        # Store improvement summary as type 'improvement'
        if 'summary' in feedback_data and feedback_data['summary']:
            create_feedback({
                'user_id': user_id,
                'input': data['input'],
                'type': 'improvement',
                'status': 'completed',
                'improvement': feedback_data['summary']
            })
        return jsonify({
            'feedback': feedback_data,
            'message': 'AI feedback generated and saved successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/user/<user_id>', methods=['GET'])
def list_user_feedback(user_id):
    """Get feedback for a specific user"""
    try:
        feedbacks = get_feedback_by_user(user_id)
        return jsonify([f for f in feedbacks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/list', methods=['GET'])
def list_current_user_feedback():
    user_id = request.args.get('user_id', 'anonymous')
    feedbacks = get_feedback_by_user(user_id)
    return jsonify({'feedback': feedbacks}), 200

@feedback_bp.route('/<feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    """Get specific feedback by ID"""
    try:
        feedback = get_feedback_by_id(feedback_id)
        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404
        return jsonify(feedback), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<feedback_id>', methods=['PUT'])
def update_feedback_route(feedback_id):
    """Update feedback (admin function)"""
    try:
        data = request.json
        update_feedback(feedback_id, data)
        return jsonify({'message': 'Feedback updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<feedback_id>', methods=['DELETE'])
def delete_feedback_route(feedback_id):
    """Delete feedback (admin function)"""
    try:
        delete_feedback(feedback_id)
        return jsonify({'message': 'Feedback deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/admin/all', methods=['GET'])
def get_all_feedback_admin():
    """Get all feedback for admin panel"""
    try:
        feedbacks = get_all_feedback()
        return jsonify([f for f in feedbacks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/admin/pending', methods=['GET'])
def get_pending_feedback():
    """Get pending feedback for admin review"""
    try:
        feedbacks = get_all_feedback()
        pending_feedbacks = [f for f in feedbacks if f.get('status') == 'pending']
        return jsonify(pending_feedbacks), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@feedback_bp.route('/ai_feedback', methods=['POST'])
def save_ai_feedback():
    data = request.json
    user_id = data.get('user_id', 'anonymous')
    feedbacks = data.get('feedbacks', [])
    summary = data.get('summary', '')
    # Save feedbacks as type 'ai_feedback'
    for fb in feedbacks:
        create_feedback({
            'user_id': user_id,
            'input': '',
            'type': 'ai_feedback',
            'status': 'completed',
            'ai_feedback': fb
        })
    # Save summary as type 'improvement'
    if summary:
        create_feedback({
            'user_id': user_id,
            'input': '',
            'type': 'improvement',
            'status': 'completed',
            'improvement': summary
        })
    return jsonify({'message': 'AI feedback and improvement saved'}), 201 

# --- SUGGESTED FEEDBACK ENDPOINTS ---
@feedback_bp.route('/suggest', methods=['POST'])
def add_suggest_feedback():
    """User submits a detailed suggestion for admin"""
    try:
        data = request.json
        if not data or 'suggestion' not in data:
            return jsonify({'error': 'Suggestion field is required'}), 400
        suggest_data = {
            'user_id': data.get('user_id', 'anonymous'),
            'user_name': data.get('user_name', ''),
            'suggestion': data['suggestion'],
            'status': 'seen',
            'created_at': data.get('created_at')
        }
        result = create_suggest_feedback(suggest_data)
        return jsonify({'message': 'Suggestion submitted', 'id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/suggest/all', methods=['GET'])
def get_all_suggest_feedback_route():
    try:
        feedbacks = get_all_suggest_feedback()
        for fb in feedbacks:
            fb['_id'] = str(fb['_id'])
        return jsonify({'suggest_feedback': feedbacks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/suggest/user/<user_id>', methods=['GET'])
def get_user_suggest_feedback(user_id):
    try:
        feedbacks = get_suggest_feedback_by_user(user_id)
        for fb in feedbacks:
            fb['_id'] = str(fb['_id'])
        return jsonify({'suggest_feedback': feedbacks}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/suggest/<suggest_id>/status', methods=['PUT'])
def update_suggest_status(suggest_id):
    try:
        data = request.json
        status = data.get('status')
        if status not in ['seen', 'working in progress', 'done']:
            return jsonify({'error': 'Invalid status'}), 400
        update_suggest_feedback_status(suggest_id, status)
        return jsonify({'message': 'Status updated'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/suggest/<suggest_id>', methods=['DELETE'])
def delete_suggest_feedback_route(suggest_id):
    try:
        delete_suggest_feedback(suggest_id)
        return jsonify({'message': 'Suggestion deleted'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500 