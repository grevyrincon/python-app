from pymongo import MongoClient
import os

MONGO_URL = os.getenv("MONGO_URL") 
DB_NAME = "namesdb"

client = MongoClient(MONGO_URL)
db = client[DB_NAME]
names_collection = db["names"]
