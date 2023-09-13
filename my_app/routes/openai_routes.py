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
        conversation = "\n".join([f"{msg['username']}: {msg['message']}" for msg in limited_messages])
        
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=conversation,
            max_tokens=50
        )
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

def get_bot_response(conversation):
    try:
        response = openai.Completion.create(
            engine="text-davinci-002",
            prompt=conversation,
            max_tokens=50
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"Error: {e}")
        return None