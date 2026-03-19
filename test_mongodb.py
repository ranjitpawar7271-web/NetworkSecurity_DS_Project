from pymongo import MongoClient
import certifi

uri = "mongodb+srv://ranjit_user:Ranjit12345@cluster0.z5bw0jx.mongodb.net/?appName=Cluster0"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where())

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)