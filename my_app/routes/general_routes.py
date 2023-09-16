from flask import Blueprint, request, jsonify, render_template_string, session
from datetime import datetime, timedelta
from my_app import db
from my_app.models import User
from my_app import app
import requests
from my_app.models import SystemStatus, ChatMessage

import re
import os
import uuid
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import openai
from my_app.routes.openai_routes import get_completion  # Changed from get_bot_response to get_completion
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
limiter = Limiter(app=app, key_func=get_remote_address)

general_routes = Blueprint('general_routes', __name__)

def detect_bot_mention(message):
    return bool(re.search(r"@bot", message))

def fetch_last_n_messages(n=30):
    return (
        ChatMessage.query
        .filter(ChatMessage.username != 'bot')
        .order_by(ChatMessage.timestamp.desc())
        .limit(n)
        .all()
    )

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

bot_command_detected = False

@general_routes.route('/send_message', methods=['POST'])
@limiter.limit("5 per second")
def send_message():
    bot_response = ""
    unique_id = str(uuid.uuid4())
    client_ip = request.remote_addr

    existing_message = ChatMessage.query.filter_by(unique_id=unique_id).first()
    if existing_message:
        return jsonify({'status': 'duplicate'}), 409

    user_agent = request.headers.get('User-Agent')
    logging.debug(f"User-Agent: {user_agent}")

    data = request.json
    username = data.get('username')
    message = data.get('message')

    new_message = ChatMessage(username=username, message=message, unique_id=unique_id)
    logging.info(f"Committed messages to the database. Unique ID: {unique_id}")
    db.session.add(new_message)
    db.session.commit()

    if detect_bot_mention(message):
        last_n_messages = fetch_last_n_messages(30)  # fetching last 30 messages
        last_n_messages = sorted(last_n_messages, key=lambda x: x.timestamp)
        # Prepare the message list for OpenAI API call
        messages_for_openai = [
            {'username': msg.username, 'message': msg.message} 
            for msg in last_n_messages
        ]
        
        newest_message = {'username': username, 'message': message}
        messages_for_openai.append(newest_message)  # Adding the newest message to the end
        
        # Get bot response
        bot_response = get_completion(messages_for_openai)
        logging.debug(f"Bot response received: {bot_response}")

        if bot_response is not None:
            new_bot_message = ChatMessage(username="bot", message=bot_response)
            db.session.add(new_bot_message)
            db.session.commit()
            logging.info(f"Committed bot message: {new_bot_message.message}")
        else:
            logging.warning("Bot response is None. Skipping database insertion.")

    logging.debug(f"Committed messages to the database. Unique ID: {unique_id}")
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

@general_routes.route('/status', methods=['GET'])
def get_status():
    status = SystemStatus.query.first()
    return jsonify({"online": status.online}), 200
