from pymongo import MongoClient
import socket

def is_localhost():
    try:
        return socket.gethostname() == "JohnsPC"
    except Exception:
        return False

connection_string = (
    "mongodb+srv://jff97:REDACTED&*@cosmosoffsuitstorage.global.mongocluster.cosmos.azure.com/"
    "?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
)
client = MongoClient(connection_string)
db = client["offsuitpokeranalyzerdb"]
if is_localhost():
    collection = db["monthly_data_test"]   # Local/testing collection
else:
    collection = db["monthly_data_prod"]   # Production collection

def store_month_document(month_doc: dict):
    if "_id" not in month_doc:
        raise ValueError("month_doc must have an '_id' field")
    return collection.replace_one({"_id": month_doc["_id"]}, month_doc, upsert=True)

def delete_all_data():
    return collection.delete_many({})

def get_month_document(month_id: str) -> dict:
    return collection.find_one({"_id": month_id})
