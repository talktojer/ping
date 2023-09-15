from flask import Blueprint, request, jsonify
import openai
import os
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configure OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_routes = Blueprint('openai_routes', __name__)

MAX_TOKENS = 2048
MAX_CONTEXT_QUESTIONS = 10

def get_completion(messages):
    try:
        # Initialize the conversation string
        conversation = ""
        
        # Limit the messages to the last 10
        limited_messages = messages[-MAX_CONTEXT_QUESTIONS:]

        # Build the conversation string
        for msg in limited_messages:
            conversation += f"{msg['username']}: {msg['message']}\n"

        # Add an explicit question to the prompt
        conversation += "admin: Can you hear me, bot?"

        payload = {
            "model": "text-davinci-002",
            "prompt": "Hello, can you hear me?",
            "max_tokens": 50,
            "temperature": 0.7
        }

        response = openai.Completion.create(**payload)

        logging.info(f"OpenAI API Response: {response}")

        if response and response.choices:
            completion = response.choices[0].text.strip()
            logging.info(f"Raw Bot Response: {completion}")
            return completion
        else:
            logging.warning("No completion generated by the API.")
            return "Error: No completion"
    except Exception as e:
        logging.error(f"Error: {e}")
        return None

@openai_routes.route('/get_completion', methods=['POST'])
def get_completion_route():
    data = request.json
    messages = data.get('messages')
    if not messages:
        return jsonify({'error': 'No messages provided'}), 400

    completion = get_completion(messages)
    return jsonify({'completion': completion})
