import os
from dotenv import load_dotenv
from llama_index.core import (VectorStoreIndex, SimpleDirectoryReader, StorageContext, load_index_from_storage)
from flask import Flask, request, jsonify
from flask_bcrypt import Bcrypt
import asyncio

load_dotenv()
app = Flask(__name__)
bcrypt = Bcrypt(app)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize LLaMA index and query engine
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()

users = []

@app.route('/api/auth/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = {'username': username, 'password': hashed_password}
        users.append(user)
        return jsonify({'message': 'User created'}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating user'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data['username']
        password = data['password']
        user = next((u for u in users if u['username'] == username), None)
        if not user:
            return jsonify({'message': 'User not found'}), 404
        if not bcrypt.check_password_hash(user['password'], password):
            return jsonify({'message': 'Invalid password'}), 401
        return jsonify({'message': 'Login successful'}), 200
    except Exception as e:
        return jsonify({'message': 'Error logging in'}), 500

async def generate_response(query):
    try:
        response = await asyncio.get_event_loop().run_in_executor(None, query_engine.query, query)
        return response
    except Exception as e:
        return 'Error generating response'

@app.route('/api/chat', methods=['POST'])
async def chat():
    try:
        data = await request.get_json()
        query = data['query']
        response = await generate_response(query)
        return jsonify({'response': response}), 200
    except Exception as e:
        return jsonify({'message': 'Error generating response'}), 500

if __name__ == '__main__':
    app.run(debug=True)