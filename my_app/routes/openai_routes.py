from flask import Blueprint, request, jsonify
import openai
import os
import json
from langchain import OpenAI, PromptTemplate, LLMChain
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chains import ConversationChain
from .shared_resources import conversation_with_summary

def initialize_conversation_chain():
    global conversation_with_summary  # Declare the variable as global
    llm = OpenAI(temperature=0)
    conversation_with_summary = ConversationChain(
        llm=llm,
        memory=ConversationSummaryBufferMemory(llm=OpenAI(), max_token_limit=40),
        verbose=True
    )
openai.api_key = os.getenv("OPENAI_API_KEY")
openai_routes = Blueprint('openai_routes', __name__)

def get_completion(messages):
    try:
        limited_messages = messages[-10:]
        print(type(last_ten_messages_dict_with_username), last_ten_messages_dict_with_username)
        formatted_input = {
            'adjective': 'funny',
            'conversation': str(last_ten_messages_dict_with_username)
        }
        logging.debug("Calling predict() with formatted_input: %s", formatted_input)
        try:
            bot_response = conversation_with_summary.predict(values=formatted_input)
        except Exception as e:
            print(f"An error occurred: {e}")
        logging.debug(f"Bot response: {bot_response}")
        return bot_response

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