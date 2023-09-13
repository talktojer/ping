from flask import Blueprint, request, jsonify
import openai
import os
import json
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



openai.api_key = os.getenv("OPENAI_API_KEY")
openai_routes = Blueprint('openai_routes', __name__)

def get_completion(messages):
    try:
        limited_messages = messages[-10:]
        conversation = "\n".join([f"{msg['username']}: {msg['message']}" for msg in limited_messages])
        
        payload = {
            "engine": "text-davinci-002",
            "prompt": conversation,
            "max_tokens": 2048
        }
        
        # Log the API request payload
        logging.info(f"Sending API request with payload: {json.dumps(payload)}")
        
        response = openai.Completion.create(**payload)
        logging.info(f"OpenAI API Response: {response}")
        logging.info(f"Raw Bot Response: {response.choices[0].text}")
        completion = response.choices[0].text.strip()
        return completion
    except Exception as e:
        logging.error(f"Error: {e}")
        return None
        

        
        
        return completion
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

def get_bot_response(conversation_history):
    try:
        filtered_history = [line for line in conversation_history.split('\n') if not (line.startswith('bot: ') and len(line) == 5)]
        conversation = "\n".join(filtered_history)
        
        payload = {
            "engine": "text-davinci-002",
            "prompt": conversation,
            "max_tokens": 2048
        }
        
        # Log the API request payload
        logging.info(f"Sending API request with payload: {json.dumps(payload)}")
        
        response = openai.Completion.create(**payload)
        logging.info(f"OpenAI API Response: {response}")
        logging.info(f"Raw Bot Response: {response.choices[0].text}")
        return response.choices[0].text.strip()
    except Exception as e:
        logging.error(f"Error: {e}")
        return None
