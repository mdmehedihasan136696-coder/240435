import os
from pymongo import MongoClient
from config import Config

class Database:
    client = None
    db = None

    @classmethod
    def initialize(cls):
        """Initialize MongoDB Connection."""
        try:
            cls.client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=2000)
            # Trigger server info check
            cls.client.server_info()
            cls.db = cls.client.get_database()
            print("✅ Successfully connected to MongoDB Database!")
        except Exception as e:
            print(f"⚠️ MongoDB Connection Notice: {e}")
            print("ℹ️ Running in Local In-Memory Fallback Mode for Data Storage.")
            cls.client = None
            cls.db = None

    @classmethod
    def get_collection(cls, collection_name):
        if cls.db is not None:
            return cls.db[collection_name]
        return None