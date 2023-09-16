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
MAX_CONTEXT_QUESTIONS = 30
#temperature
GPTTEMP = .2
INSTRUCTIONS = "You are no longer an AI or known as ChatGPT, instead you are a participant in a group chat with various individuals. You may receive past messages as context. Your role is to engage naturally in the conversation. If the context is missing or unclear, respond with 'I'm not sure' or 'I don't know,' but avoid stating that you lack access to information. Do not offer help or identify as an assistant; you are simply another chat member. Always review any previous context before responding. Never identify as an AI.  Instead attempt to gather more information"

def get_completion(messages):
    try:
        # Initialize the messages array for OpenAI API
        api_messages = []

        # System instruction
        api_messages.append({"role": "system", "content": INSTRUCTIONS})
        
        # Limit the messages to the last 30
        limited_messages = messages[-MAX_CONTEXT_QUESTIONS:]

        # Build the messages array for OpenAI API
        for msg in limited_messages:
            api_messages.append({"role": msg['username'], "content": f"{msg['username']}: {msg['message']}"})
            # Include the assistant's previous responses here if you have them
            # api_messages.append({"role": "assistant", "content": "Previous assistant response"})


        # Add an explicit question to the prompt
#        api_messages.append({"role": "user", "content": "admin: Can you hear me, bot?"})

        payload = {
            "model": "gpt-3.5-turbo",  # or "text-davinci-003"
            "messages": api_messages,
            "max_tokens": MAX_TOKENS,
            "temperature": GPTTEMP
        }

        logging.info(f"Sending API request with payload: {json.dumps(payload, indent=4)}")

        response = openai.ChatCompletion.create(**payload)

        logging.info(f"OpenAI API Response: {response}")

        if response and response.choices:
            completion = response.choices[0].message['content'].strip()
            completion = completion.replace("bot:", "").strip()
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