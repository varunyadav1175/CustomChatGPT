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
import psycopg2

# PostgreSQL connection
PG_HOST = os.environ.get("PG_HOST", "34.70.51.155")
PG_PORT = os.environ.get("PG_PORT", "5432")
PG_DATABASE = os.environ.get("PG_DATABASE")
PG_USER = "postgres"
PG_PASSWORD = "root"

conn = psycopg2.connect(
    host=PG_HOST,
    port=PG_PORT,
    database=PG_DATABASE,
    user=PG_USER,
    password=PG_PASSWORD,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()
app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
MODEL = os.environ.get("MODEL")
llm = OpenAI(MODEL)



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
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (email, query, date, response) VALUES (%s, %s, %s, %s)",
            (email, query, datetime.now(), response_str),
        )
        conn.commit()
        cur.close()
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

@app.route("/history", methods=["GET"])
def history():
    try:
        email = request.args.get("email")
        if not email:
            return jsonify({"message": "Email parameter is missing"}), 400

        cur = conn.cursor()
        cur.execute("SELECT date, query, response FROM users WHERE email = %s ORDER BY date DESC", (email,))
        rows = cur.fetchall()
        cur.close()

        history_entries = [{"date": row[0], "query": row[1], "response": row[2]} for row in rows]
        
        return jsonify({"history": history_entries}), 200
    except Exception as e:
        logging.error(f"Error fetching history: {e}")
        return jsonify({"message": "Error fetching history"}), 500

if __name__ == "__main__":
    app.run(debug=True)