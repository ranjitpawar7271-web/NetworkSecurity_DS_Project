from pymongo import MongoClient
import certifi
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get MongoDB URI securely
uri = os.getenv("MONGO_DB_URL")

# Create client
client = MongoClient(uri, tlsCAFile=certifi.where())

try:
    client.admin.command('ping')
    print("MongoDB connected securely")
except Exception as e:
    print(e)