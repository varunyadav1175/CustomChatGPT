import os
from dotenv import load_dotenv
from llama_index.core import (VectorStoreIndex,SimpleDirectoryReader,StorageContext,load_index_from_storage)
import logging
import sys


load_dotenv()

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)

query_engine = index.as_query_engine()
response = query_engine.query("which college did varun go to?")
print(response)