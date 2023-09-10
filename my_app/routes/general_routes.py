from flask import Blueprint, request, jsonify, render_template_string, session
from datetime import datetime, timedelta
from my_app import db
from my_app.models import User
import requests


general_routes = Blueprint('general_routes', __name__)

@general_routes.route('/', methods=['GET'])
def index():
    username = session.get('username')
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            user.last_active = datetime.utcnow()
            db.session.commit()
    active_users = get_active_users()
    active_users_idle_times = {user.username: int((datetime.utcnow() - user.last_active).total_seconds()) for user in active_users}
    return render_template_string(open('index.html').read(), username=username, active_users_idle_times=active_users_idle_times)
    pass

@general_routes.route('/ping', methods=['POST'])
def ping():
    logging.info("Inside /ping")
    user = User.query.filter_by(username=session.get('username')).first()
    if user:
        user.last_active = datetime.utcnow()
        db.session.commit()
    try:
        data = request.get_json()
        # Use the logged-in username if available, otherwise default to 'Anon Pinger'
        name = session.get('username', data.get('name', 'Anon Pinger'))
        payload = f'Ping! From {name}'
        response = requests.post('http://ntfy.jersweb.net/ping-jer', data=payload)
        response.raise_for_status()
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error in /ping: {e}")
        return jsonify({"error": str(e)}), 500
    pass
