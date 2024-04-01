import os
from dotenv import load_dotenv
from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from google.oauth2 import id_token
from google.auth.transport import requests
from flask import Flask, request, jsonify
from llama_index.llms.openai import OpenAI
from flask_bcrypt import Bcrypt
import asyncio
import logging
from flask_cors import CORS
from datetime import datetime
from pymongo import MongoClient

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("MODEL")
llm = OpenAI(MODEL)

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.RecruitWizer
users_collection = db.Users

# Initialize LLaMA index and query engine
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

from llama_index.core.memory import ChatMemoryBuffer

memory = ChatMemoryBuffer.from_defaults(token_limit=3900)
chat_engine = index.as_chat_engine(
    chat_mode="condense_plus_context",
    memory=memory,
    llm=llm,
    context_prompt=(
        "You are a chatbot, able to have normal interactions, as well as talk"
        " about the resume of Varun Yadav."
        "Here are the relevant documents for the context:\\n"
        "{context_str}"
        "\\nInstruction: Use the previous chat history, or the context above, to interact and help the user."
    ),
    verbose=False,
)

async def generate_response(query, email):
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, chat_engine.chat, query
        )
        response_str = str(response)
        await users_collection.insert_one({
            "email": email,
            "query": query,
            "date": datetime.now()
        })
        return response_str
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return "Error generating response"

@app.route("/chat", methods=["GET"])
async def chat():
    try:
        query = request.args.get("query")
        email = request.args.get("email")
        response = await generate_response(query, email)
        return jsonify({"response": response}), 200
    except Exception as e:
        logging.error(f"Error generating response: {e}")
        return jsonify({"message": "Error generating response"}), 500

if __name__ == "__main__":
    app.run(debug=True)
