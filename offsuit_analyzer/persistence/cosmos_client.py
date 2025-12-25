"""Shared MongoDB connection."""
from pymongo import MongoClient
from offsuit_analyzer.config import config

connection_string = config.DATABASE_CONNECTION_STRING
client = MongoClient(connection_string)
db = client[config.MONGO_DB_NAME]
