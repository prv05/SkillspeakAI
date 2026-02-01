from flask import Blueprint, jsonify, g, request
from utils.jwt_utils import token_required
from models.session import get_sessions_by_user, get_all_sessions, get_sessions_today
from models.feedback import get_feedback_by_user
from models.user import get_all_users, get_users_today, get_all_admin_users, get_admin_users_today
from mongo_client import mongo
from datetime import datetime, timedelta
from collections import Counter
from collections import defaultdict

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/stats', methods=['GET'])
def user_stats():
    sessions = get_sessions_by_user(g.user_id) if hasattr(g, 'user_id') else []
    feedbacks = get_feedback_by_user(g.user_id) if hasattr(g, 'user_id') else []
    total_chats = len(sessions)
    avg_score = (
        sum(f.get('score', 0) for f in feedbacks) / len(feedbacks)
        if feedbacks else 0
    )
    last_activity = max((s['timestamp'] for s in sessions), default=None)
    return jsonify({
        'total_chats': total_chats,
        'avg_feedback_score': avg_score,
        'last_activity': str(last_activity) if last_activity else None
    })

@dashboard_bp.route('/admin_stats', methods=['GET'])
def admin_stats():
    total_sessions = get_all_sessions()
    today_sessions = get_sessions_today()
    total_users = get_all_users()
    today_users = get_users_today()
    admin_users = get_all_admin_users()
    today_admins = get_admin_users_today()
    total_suggest_feedback = mongo.db.suggest_feedback.count_documents({})
    today = datetime.utcnow().date()
    tomorrow = today + timedelta(days=1)
    total_suggest_feedback_today = mongo.db.suggest_feedback.count_documents({
        'created_at': {
            '$gte': datetime(today.year, today.month, today.day),
            '$lt': datetime(tomorrow.year, tomorrow.month, tomorrow.day)
        }
    })
    return jsonify({
        'total_chats': len(total_sessions),
        'today_chats': len(today_sessions),
        'total_users': len(total_users),
        'today_users': len(today_users),
        'admin_users': len(admin_users),
        'today_admins': len(today_admins),
        'total_suggest_feedback': total_suggest_feedback,
        'total_suggest_feedback_today': total_suggest_feedback_today
    })

@dashboard_bp.route('/admin_user_growth', methods=['GET'])
def admin_user_growth():
    mode = request.args.get('mode', 'week')
    users = mongo.db.users.find()
    now = datetime.utcnow()
    data = []
    if mode == 'week':
        # Last 7 days, group by day
        days = [(now.date() - timedelta(days=i)) for i in range(6, -1, -1)]
        day_labels = [d.strftime('%a') for d in days]
        counts = Counter()
        for user in users:
            if 'created_at' in user:
                dt = user['created_at']
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', ''))
                day = dt.date()
                if day in days:
                    counts[day] += 1
        data = [counts[d] for d in days]
        return {'labels': day_labels, 'data': data}
    elif mode == 'month':
        # Current month, group by week (1-4)
        first = now.replace(day=1)
        weeks = [1, 2, 3, 4]
        week_labels = [f'Week {w}' for w in weeks]
        counts = Counter()
        for user in users:
            if 'created_at' in user:
                dt = user['created_at']
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', ''))
                if dt.year == now.year and dt.month == now.month:
                    week = (dt.day - 1) // 7 + 1
                    if week in weeks:
                        counts[week] += 1
        data = [counts[w] for w in weeks]
        return {'labels': week_labels, 'data': data}
    elif mode == 'year':
        # Current year, group by month
        months = list(range(1, 13))
        month_labels = [datetime(now.year, m, 1).strftime('%b') for m in months]
        counts = Counter()
        for user in users:
            if 'created_at' in user:
                dt = user['created_at']
                if isinstance(dt, str):
                    dt = datetime.fromisoformat(dt.replace('Z', ''))
                if dt.year == now.year:
                    counts[dt.month] += 1
        data = [counts[m] for m in months]
        return {'labels': month_labels, 'data': data}
    else:
        return {'labels': [], 'data': []}

@dashboard_bp.route('/admin_user_streak_stats', methods=['GET'])
def admin_user_streak_stats():
    users = list(mongo.db.users.find())
    daily = 0
    non_daily = 0
    for user in users:
        streak = user.get('streak', 0)
        if isinstance(streak, (int, float)) and streak > 0:
            daily += 1
        else:
            non_daily += 1
    return {'daily': daily, 'non_daily': non_daily}

@dashboard_bp.route('/admin_user_streaks', methods=['GET'])
def admin_user_streaks():
    users = list(mongo.db.users.find())
    sessions = list(mongo.db.session.find())
    from datetime import datetime, timedelta
    now = datetime.utcnow().date()
    streak_days = 3  # Define streak as having a session for each of the last 3 days
    user_sessions = {}
    for s in sessions:
        uid = s.get('user_id')
        if not uid:
            continue
        dt = s.get('created_at')
        if isinstance(dt, str):
            try:
                dt = datetime.fromisoformat(dt.replace('Z', ''))
            except Exception:
                continue
        if not isinstance(dt, datetime):
            continue
        user_sessions.setdefault(str(uid), set()).add(dt.date())
    daily = 0
    non_daily = 0
    for u in users:
        uid = str(u['_id'])
        streak = True
        for i in range(streak_days):
            if (now - timedelta(days=i)) not in user_sessions.get(uid, set()):
                streak = False
                break
        if streak:
            daily += 1
        else:
            non_daily += 1
    return {'labels': ['Daily User', 'Non-Frequent User'], 'data': [daily, non_daily]}

@dashboard_bp.route('/admin_user_activity', methods=['GET'])
def admin_user_activity():
    today = datetime.utcnow().date()
    daily_users = 0
    non_daily_users = 0
    for user in mongo.db.users.find():
        last_login = user.get('last_login') or user.get('created_at')
        if last_login:
            if isinstance(last_login, str):
                try:
                    last_login = datetime.fromisoformat(last_login.replace('Z', ''))
                except Exception:
                    continue
            if last_login.date() == today:
                daily_users += 1
            else:
                non_daily_users += 1
    return {'daily_users': daily_users, 'non_daily_users': non_daily_users}

@dashboard_bp.route('/admin_user_streak', methods=['GET'])
def admin_user_streak():
    # Get all sessions, group by user
    from datetime import timedelta
    sessions = list(mongo.db.session.find())
    user_dates = defaultdict(set)
    for s in sessions:
        user = s.get('user_id')
        dt = s.get('created_at')
        if user and dt:
            if isinstance(dt, str):
                try:
                    dt = datetime.fromisoformat(dt.replace('Z', ''))
                except:
                    continue
            user_dates[user].add(dt.date())
    daily_users = 0
    non_daily_users = 0
    for dates in user_dates.values():
        if len(dates) < 2:
            non_daily_users += 1
            continue
        sorted_dates = sorted(dates)
        streak = 1
        max_streak = 1
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]) == timedelta(days=1):
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 1
        if max_streak >= 2:
            daily_users += 1
        else:
            non_daily_users += 1
    return {'daily_users': daily_users, 'non_daily_users': non_daily_users}

@dashboard_bp.route('/admin_recent_activity', methods=['GET'])
def admin_recent_activity():
    # Get recent sessions
    session_acts = []
    for s in mongo.db.session.find().sort('created_at', -1).limit(10):
        session_acts.append({
            'type': 'Session',
            'user': s.get('user_id', 'Unknown'),
            'detail': s.get('session_name', 'Session'),
            'time': s.get('created_at')
        })
    # Get recent suggestions
    suggest_acts = []
    for s in mongo.db.suggest_feedback.find().sort('created_at', -1).limit(10):
        suggest_acts.append({
            'type': 'Suggestion',
            'user': s.get('user_name', s.get('user_id', 'Unknown')),
            'detail': s.get('suggestion', ''),
            'time': s.get('created_at')
        })
    # Get recent user signups
    user_acts = []
    for u in mongo.db.users.find().sort('created_at', -1).limit(10):
        user_acts.append({
            'type': 'Signup',
            'user': u.get('name', u.get('email', 'Unknown')),
            'detail': 'New user signup',
            'time': u.get('created_at')
        })
    # Combine and sort all activities by time descending
    all_acts = session_acts + suggest_acts + user_acts
    def get_time(act):
        t = act['time']
        from datetime import datetime
        if isinstance(t, str):
            try:
                return datetime.fromisoformat(t.replace('Z', ''))
            except:
                return datetime.min
        return t or datetime.min
    all_acts.sort(key=get_time, reverse=True)
    # Limit to 20 most recent
    result = {'activities': all_acts[:20]}
    print(f"[DEBUG] /admin_recent_activity: {len(result['activities'])} activities. First: {result['activities'][:2]}")
    return result 