from flask import Blueprint, request, jsonify
import openai
import re
import os

openai_routes = Blueprint('openai_routes', __name__)
OPENAI_API_KEY = "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"
def get_completion(messages):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.7,
        n=1,
        max_tokens=500
    )
    return response.choices[0].message.content
@openai_routes.route('/get_completion', methods=['POST'])
def get_completion_route():
    data = request.json
    messages = data.get('messages')
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    completion = get_completion(messages)
    return jsonify({'completion': completion})
