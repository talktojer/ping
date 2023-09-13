from flask import Blueprint, request, jsonify
import openai
import os
import json

openai.api_key = os.getenv("OPENAI_API_KEY")
openai_routes = Blueprint('openai_routes', __name__)

def get_completion(messages):
    try:
        limited_messages = messages[-10:]
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=limited_messages,
            temperature=0.7,
            n=1,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return None

@openai_routes.route('/get_completion', methods=['POST'])
def get_completion_route():
    data = request.json
    messages = data.get('messages')
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    completion = get_completion(messages)
    return jsonify({'completion': completion})