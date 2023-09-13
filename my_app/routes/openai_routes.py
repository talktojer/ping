from flask import Blueprint, request, jsonify
import openai
import os
import json


openai.api_key = os.getenv("OPENAI_API_KEY")
openai_routes = Blueprint('openai_routes', __name__)

def get_completion(messages):
    try:
        limited_messages = messages[-10:]
        conversation = "\n".join([f"{msg['username']}: {msg['message']}" for msg in limited_messages])
        
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=conversation,
            max_tokens=2048
        )
        print(f"OpenAI API Response: {response}")
        print(f"Raw Bot Response: {response.choices[0].text}")
        completion = response.choices[0].text.strip()
        

        
        
        return completion
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

def get_bot_response(conversation_history):
    try:
        # Filter out lines where the bot didn't respond
        filtered_history = [line for line in conversation_history.split('\n') if not (line.startswith('bot: ') and len(line) == 5)]
        
        # Reconstruct the conversation
        conversation = "\n".join(filtered_history)
        
        print(f"Filtered Conversation Prompt: {conversation}")
        
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=conversation,
            max_tokens=2048
        )
        
        
        print(f"OpenAI API Response: {response}")
        print(f"Raw Bot Response: {response.choices[0].text}")
        
        return response.choices[0].text.strip()
        
    except Exception as e:
        print(f"Error: {e}")
        return None
