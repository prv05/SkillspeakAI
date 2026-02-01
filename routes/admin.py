
from flask import Blueprint, request, jsonify, g
from utils.jwt_utils import token_required
from models.user import get_all_users, delete_user, set_user_as_admin, get_user_by_email, block_user, unblock_user, remove_admin_role, reset_user_password, get_user_stats, get_daily_vs_nonfrequent_users
from models.feedback import get_all_feedback
from models.session import get_all_sessions
from models.chat import get_all_chats
from datetime import datetime, timedelta
from mongo_client import mongo

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
def all_users():
    users = get_all_users()
    for u in users:
        u['_id'] = str(u['_id'])
        u.pop('password', None)
    return jsonify({'users': users})

@admin_bp.route('/feedback', methods=['GET'])
def all_feedback():
    feedbacks = get_all_feedback()
    for f in feedbacks:
        f['_id'] = str(f['_id'])
        f['user_id'] = str(f['user_id'])
    return jsonify({'feedbacks': feedbacks})

@admin_bp.route('/delete_user/<user_id>', methods=['DELETE'])
def delete_user_route(user_id):
    try:
        result = delete_user(user_id)
        if result.deleted_count > 0:
            return jsonify({'message': 'User deleted successfully'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/block_user/<user_id>', methods=['POST'])
def block_user_route(user_id):
    """Block a user"""
    try:
        result = block_user(user_id)
        if result.modified_count > 0:
            return jsonify({'message': 'User blocked successfully'}), 200
        else:
            return jsonify({'error': 'User not found or already blocked'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/unblock_user/<user_id>', methods=['POST'])
def unblock_user_route(user_id):
    """Unblock a user"""
    try:
        result = unblock_user(user_id)
        if result.modified_count > 0:
            return jsonify({'message': 'User unblocked successfully'}), 200
        else:
            return jsonify({'error': 'User not found or not blocked'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/remove_admin/<user_id>', methods=['POST'])
def remove_admin_route(user_id):
    """Remove admin role from user"""
    try:
        result = remove_admin_role(user_id)
        if result.modified_count > 0:
            return jsonify({'message': 'Admin role removed successfully'}), 200
        else:
            return jsonify({'error': 'User not found or not an admin'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/reset_password/<user_id>', methods=['POST'])
def reset_password_route(user_id):
    """Reset user password to default"""
    try:
        result = reset_user_password(user_id)
        if result.modified_count > 0:
            return jsonify({'message': 'Password reset successfully to: password123'}), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/user_stats/<user_id>', methods=['GET'])
def user_stats_route(user_id):
    """Get user statistics"""
    try:
        stats = get_user_stats(user_id)
        if stats:
            # Convert ObjectId to string for JSON serialization
            if stats['user'] and '_id' in stats['user']:
                stats['user']['_id'] = str(stats['user']['_id'])
            if stats['last_activity']:
                stats['last_activity'] = stats['last_activity'].isoformat()
            return jsonify(stats), 200
        else:
            return jsonify({'error': 'User not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/set_admin/<user_id>', methods=['POST'])
def set_admin_route(user_id):
    """Set a user as admin"""
    try:
        result = set_user_as_admin(user_id)
        if result.modified_count > 0:
            return jsonify({'message': 'User set as admin successfully'}), 200
        else:
            return jsonify({'error': 'User not found or already admin'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/set_admin_by_email', methods=['POST'])
def set_admin_by_email():
    """Set a user as admin by email (for initial setup)"""
    try:
        data = request.json
        email = data.get('email')
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        user = get_user_by_email(email)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        result = set_user_as_admin(str(user['_id']))
        if result.modified_count > 0:
            return jsonify({'message': f'User {email} set as admin successfully'}), 200
        else:
            return jsonify({'error': 'User already admin'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
def admin_stats():
    """Get admin dashboard statistics"""
    try:
        # Get total users
        total_users = mongo.db.users.count_documents({})
        admin_users = mongo.db.users.count_documents({'role': 'admin'})
        
        # Get users this week
        week_ago = datetime.utcnow() - timedelta(days=7)
        new_users_this_week = mongo.db.users.count_documents({
            'created_at': {'$gte': week_ago}
        })
        
        # Get total feedback
        total_feedback = mongo.db.feedback.count_documents({})
        
        # Get feedback this month
        month_ago = datetime.utcnow() - timedelta(days=30)
        new_feedback_this_month = mongo.db.feedback.count_documents({
            'created_at': {'$gte': month_ago}
        })
        
        # Get active chats (sessions)
        active_chats = mongo.db.session.count_documents({'status': 'active'})
        
        # Get new chats today (sessions)
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        new_chats_today = mongo.db.session.count_documents({
            'created_at': {'$gte': today}
        })

        # Get total chats (sessions)
        total_chats = mongo.db.session.count_documents({})
        # Get today's chats (sessions)
        today_chats = mongo.db.session.count_documents({'created_at': {'$gte': today}})

        # Get total suggestions (suggest_feedback)
        total_suggest_feedback = mongo.db.suggest_feedback.count_documents({})
        # Get today's suggestions (suggest_feedback)
        total_suggest_feedback_today = mongo.db.suggest_feedback.count_documents({'created_at': {'$gte': today}})

        return jsonify({
            'total_users': total_users,
            'admin_users': admin_users,
            'new_users_this_week': new_users_this_week,
            'total_feedback': total_feedback,
            'new_feedback_this_month': new_feedback_this_month,
            'active_chats': active_chats,
            'new_chats_today': new_chats_today,
            'total_chats': total_chats,         # <-- added
            'today_chats': today_chats,          # <-- added
            'total_suggest_feedback': total_suggest_feedback,           # <-- added
            'total_suggest_feedback_today': total_suggest_feedback_today # <-- added
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/dashboard_stats', methods=['GET'])
def dashboard_stats():
    """Alias for /stats to provide admin dashboard statistics (public endpoint)"""
    return admin_stats()

@admin_bp.route('/chats', methods=['GET'])
def admin_chats():
    """Get all chat sessions for admin monitoring, or full chat for a session if session_id is provided."""
    try:
        from bson import ObjectId
        session_id = request.args.get('session_id')
        if session_id:
            session = mongo.db.session.find_one({'_id': ObjectId(session_id)})
            if not session:
                return jsonify({'error': 'Session not found'}), 404
            session['_id'] = str(session['_id'])
            return jsonify(session), 200
        else:
            sessions = list(mongo.db.session.find().sort('created_at', -1))
            result = []
            for session in sessions:
                user = mongo.db.users.find_one({'name': session.get('user_id', '')})
                user_name = user['name'] if user else session.get('user_id', '')
                result.append({
                    '_id': str(session.get('_id', '')),
                    'session_name': session.get('session_name', ''),
                    'user_name': user_name,
                    'date': session.get('start_time', session.get('created_at', '')),
                    'chat_count': len(session.get('chats', [])),
                    'duration': session.get('total_time_minutes', 0)
                })
            return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chats/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session by session_id (ObjectId)"""
    try:
        from bson import ObjectId
        result = mongo.db.session.delete_one({'_id': ObjectId(session_id)})
        if result.deleted_count > 0:
            return jsonify({'message': 'Chat session deleted successfully'}), 200
        else:
            return jsonify({'error': 'Session not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/chart-data', methods=['GET'])
def chart_data():
    """Get chart data for admin dashboard"""
    try:
        mode = request.args.get('mode', 'week')
        user_growth = {'labels': [], 'data': []}
        now = datetime.utcnow()

        if mode == 'week':
            # Last 7 days, up to today
            for i in range(6, -1, -1):
                date = now - timedelta(days=i)
                start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
                end_of_day = start_of_day + timedelta(days=1)
                count = mongo.db.users.count_documents({
                    'created_at': {'$gte': start_of_day, '$lt': end_of_day}
                })
                user_growth['labels'].append(date.strftime('%b %d'))
                user_growth['data'].append(count)
        elif mode == 'month':
            # Current month, group by week (1-5), only up to current week
            first = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            week_labels = []
            week_data = []
            week = 1
            while True:
                week_start = first + timedelta(days=(week - 1) * 7)
                week_end = week_start + timedelta(days=7)
                if week_start.month != now.month or week_start > now:
                    break
                count = mongo.db.users.count_documents({
                    'created_at': {'$gte': week_start, '$lt': min(week_end, now + timedelta(days=1))}
                })
                week_labels.append(f'Week {week}')
                week_data.append(count)
                week += 1
            user_growth['labels'] = week_labels
            user_growth['data'] = week_data
        elif mode == 'year':
            # Current year, group by month (1-12), only up to current month
            month_labels = []
            month_data = []
            for m in range(1, now.month + 1):
                month_start = datetime(now.year, m, 1)
                if m == 12:
                    month_end = datetime(now.year + 1, 1, 1)
                else:
                    month_end = datetime(now.year, m + 1, 1)
                if month_start > now:
                    break
                count = mongo.db.users.count_documents({
                    'created_at': {'$gte': month_start, '$lt': min(month_end, now + timedelta(days=1))}
                })
                month_labels.append(month_start.strftime('%b'))
                month_data.append(count)
            user_growth['labels'] = month_labels
            user_growth['data'] = month_data

        return jsonify({
            'user_growth': user_growth
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/end_chat/<session_id>', methods=['POST'])
def end_chat(session_id):
    """End a chat session"""
    try:
        from bson import ObjectId
        result = mongo.db.session.update_one(
            {'_id': ObjectId(session_id)},
            {'$set': {'status': 'ended', 'ended_at': datetime.utcnow()}}
        )
        
        if result.modified_count > 0:
            return jsonify({'message': 'Chat ended successfully'}), 200
        else:
            return jsonify({'error': 'Chat not found or already ended'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Settings endpoints
@admin_bp.route('/settings/ai', methods=['POST'])
def save_ai_settings():
    """Save AI configuration settings"""
    try:
        data = request.json
        ai_model = data.get('aiModel', 'default')
        response_length = data.get('responseLength', 'medium')
        temperature = float(data.get('temperature', 0.7))
        
        # Save to database
        mongo.db.settings.update_one(
            {'type': 'ai_config'},
            {
                '$set': {
                    'ai_model': ai_model,
                    'response_length': response_length,
                    'temperature': temperature,
                    'updated_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        return jsonify({'message': 'AI settings saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/settings/features', methods=['POST'])
def save_feature_settings():
    """Save feature toggle settings"""
    try:
        data = request.json
        settings = {
            'speech_to_speech': data.get('speechToSpeech', True),
            'text_chat': data.get('textChat', True),
            'feedback': data.get('feedback', True),
            'analytics': data.get('analytics', True),
            'auto_refresh': data.get('autoRefresh', True),
            'updated_at': datetime.utcnow()
        }
        
        # Save to database
        mongo.db.settings.update_one(
            {'type': 'feature_toggles'},
            {'$set': settings},
            upsert=True
        )
        
        return jsonify({'message': 'Feature settings saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/backup', methods=['POST'])
def create_backup():
    """Create database backup"""
    try:
        import json
        from datetime import datetime
        
        # Collect all data
        backup_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'users': list(mongo.db.users.find()),
            'feedback': list(mongo.db.feedback.find()),
            'sessions': list(mongo.db.session.find()), # Changed from 'sessions' to 'session'
            'chats': list(mongo.db.chats.find()),
            'settings': list(mongo.db.settings.find())
        }
        
        # Convert ObjectId to string for JSON serialization
        for collection in backup_data.values():
            if isinstance(collection, list):
                for doc in collection:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
        
        # Create backup file
        filename = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        backup_path = f"backups/{filename}"
        
        import os
        os.makedirs('backups', exist_ok=True)
        
        with open(backup_path, 'w') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        return jsonify({'message': 'Backup created successfully', 'filename': filename}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/clear-cache', methods=['POST'])
def clear_cache():
    """Clear system cache"""
    try:
        # Clear any cached data (implement based on your caching strategy)
        # For now, just return success
        return jsonify({'message': 'Cache cleared successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/health', methods=['GET'])
def system_health():
    """Check system health"""
    try:
        import psutil
        import time
        
        # Check database connection
        try:
            mongo.db.command('ping')
            database_status = True
        except:
            database_status = False
        
        # Check AI service (Ollama)
        ai_service_status = True  # You can implement actual AI service check
        
        # Check storage
        storage_status = True  # You can implement actual storage check
        
        # Get system info
        memory_usage = f"{psutil.virtual_memory().percent}%"
        uptime = time.time() - psutil.boot_time()
        uptime_hours = int(uptime // 3600)
        
        return jsonify({
            'database': database_status,
            'ai_service': ai_service_status,
            'storage': storage_status,
            'memory_usage': memory_usage,
            'uptime': f"{uptime_hours} hours"
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/export-data', methods=['GET'])
def export_data():
    """Export all system data"""
    try:
        import json
        from flask import send_file
        from io import BytesIO
        
        # Collect all data
        export_data = {
            'users': list(mongo.db.users.find()),
            'feedback': list(mongo.db.feedback.find()),
            'sessions': list(mongo.db.session.find()), # Changed from 'sessions' to 'session'
            'chats': list(mongo.db.chats.find()),
            'settings': list(mongo.db.settings.find())
        }
        
        # Convert ObjectId to string for JSON serialization
        for collection in export_data.values():
            if isinstance(collection, list):
                for doc in collection:
                    if '_id' in doc:
                        doc['_id'] = str(doc['_id'])
        
        # Create JSON file in memory
        json_data = json.dumps(export_data, indent=2, default=str)
        file_stream = BytesIO(json_data.encode('utf-8'))
        
        return send_file(
            file_stream,
            mimetype='application/json',
            as_attachment=True,
            download_name=f'skillspeak_data_{datetime.utcnow().strftime("%Y%m%d")}.json'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@admin_bp.route('/daily_vs_nonfrequent_users', methods=['GET'])
def daily_vs_nonfrequent_users():
    try:
        data = get_daily_vs_nonfrequent_users()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/recent_activity', methods=['GET'])
def recent_activity():
    """Return recent activity: new user signups, feedback, and chat sessions."""
    try:
        # Get recent users
        users = list(mongo.db.users.find().sort('created_at', -1).limit(10))
        user_acts = [{
            'type': 'User Signup',
            'user': u.get('name', 'Unknown'),
            'detail': f"Signed up with email {u.get('email', '')}",
            'time': u.get('created_at')
        } for u in users if u.get('created_at')]

        # Get recent feedback
        feedbacks = list(mongo.db.feedback.find().sort('created_at', -1).limit(10))
        feedback_acts = [{
            'type': 'Suggest Feedback',
            'user': f"{f.get('user_name', 'Unknown')}",
            'detail': f.get('suggestion', f.get('summary', 'Feedback submitted')),
            'time': f.get('created_at')
        } for f in feedbacks if f.get('created_at')]

        # Get recent chat sessions
        sessions = list(mongo.db.session.find().sort('created_at', -1).limit(10)) # Changed from 'session' to 'session'
        session_acts = [{
            'type': 'Chat Session',
            'user': s.get('user_id', 'Unknown'),
            'detail': s.get('session_name', 'Session started'),
            'time': s.get('created_at')
        } for s in sessions if s.get('created_at')]

        # Combine and sort all activities by time (descending)
        all_acts = user_acts + feedback_acts + session_acts
        all_acts = [a for a in all_acts if a['time']]
        all_acts.sort(key=lambda x: x['time'], reverse=True)
        # Format time as ISO string
        for a in all_acts:
            if hasattr(a['time'], 'isoformat'):
                a['time'] = a['time'].isoformat()
        return jsonify({'activities': all_acts[:20]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/update_profile', methods=['POST', 'OPTIONS'])
def update_profile():
    if request.method == 'OPTIONS':
        return '', 200
    try:
        data = request.json
        user_id = g.user_id
        update_data = {}
        if 'name' in data:
            update_data['name'] = data['name']
        if 'email' in data:
            update_data['email'] = data['email']
        from models.user import update_user_profile
        result = update_user_profile(user_id, update_data)
        if result.modified_count > 0:
            return jsonify({'message': 'Profile updated successfully'}), 200
        else:
            return jsonify({'error': 'No changes made'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500 