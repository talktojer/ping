from flask import Blueprint, request, jsonify
import openai
import re
import os

openai_routes = Blueprint('openai_routes', __name__)
#OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")


@openai_routes.route('/get_completion', methods=['POST'])
def get_completion_route():
    data = request.json
    messages = data.get('messages')
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    completion = get_completion(messages)
    return jsonify({'completion': completion})
