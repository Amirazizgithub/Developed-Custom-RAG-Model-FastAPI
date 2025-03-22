import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()


class MongoDB:
    def __init__(self):
        # Connection details for data visualization
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING_URI")
        # Create a MongoClient using the connection string
        self.client = MongoClient(self.connection_string)

    def get_client(self):
        return self.client


mongo_db = MongoDB()
