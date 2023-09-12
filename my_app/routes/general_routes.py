from flask import Blueprint, request, jsonify, render_template_string, session
from datetime import datetime, timedelta
from my_app import db
from my_app.models import User
import requests
from my_app.models import SystemStatus, ChatMessage
import logging
import re
from my_app.routes.openai_routes import get_completion
import os



general_routes = Blueprint('general_routes', __name__)


if detect_bot_mention(message):
    last_six_messages = fetch_last_n_messages()
    
    # Convert ChatMessage objects to a list of dictionaries
    last_six_messages_list = [
        {"role": "user", "content": f"{msg.username}: {msg.message}"}
        for msg in last_six_messages
    ]
    
    # Add the system message to initialize the conversation
    last_six_messages_list.insert(0, {"role": "system", "content": "You are a helpful assistant."})
    
    bot_response = get_completion(last_six_messages_list)
    
    new_bot_message = ChatMessage(username="bot", message=bot_response)
    db.session.add(new_bot_message)
def detect_bot_mention(message):
    return bool(re.search(r"@bot", message))    
def fetch_last_n_messages(n=6):
    return ChatMessage.query.order_by(ChatMessage.timestamp.desc()).limit(n).all()

def get_active_users():
    five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
    active_users = User.query.filter(User.last_active >= five_minutes_ago).all()
    print("Active users:", active_users)  # Debug line
    return active_users

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

@general_routes.route('/status', methods=['GET'])
def get_status():
    status = SystemStatus.query.first()
    return jsonify({"online": status.online}), 200

from my_app.models import ChatMessage

@general_routes.route('/send_message', methods=['POST'])
def send_message():
    data = request.json
    username = data.get('username')
    message = data.get('message')

    if detect_bot_mention(message):
        last_six_messages = fetch_last_n_messages()
        
        # Convert ChatMessage objects to a list of dictionaries
        last_six_messages_dict = [
            {"role": "user", "content": msg.message}  # Removed "username": msg.username
            for msg in last_six_messages
        ]
            
        bot_response = get_completion(last_six_messages_dict)
        
        new_bot_message = ChatMessage(username="bot", message=bot_response)
        db.session.add(new_bot_message)

    new_message = ChatMessage(username=username, message=message)
    db.session.add(new_message)
    db.session.commit()

    return jsonify({'status': 'success'})


@general_routes.route('/get_messages', methods=['GET'])
def get_messages():
    all_messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
    messages = [{"username": msg.username, "message": msg.message} for msg in all_messages]
    return jsonify({"messages": messages}), 200

@general_routes.route('/fetch_messages', methods=['GET'])
def fetch_messages():
    messages = ChatMessage.query.order_by(ChatMessage.timestamp).all()
    messages_list = [{'username': msg.username, 'message': msg.message} for msg in messages]
    return jsonify(messages_list)

@general_routes.route('/clear_messages', methods=['POST'])
def clear_messages():
    ChatMessage.query.delete()
    db.session.commit()
    return jsonify({'status': 'success'})