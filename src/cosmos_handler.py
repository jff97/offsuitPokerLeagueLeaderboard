from pymongo import MongoClient

connection_string = "mongodb+srv://jff97:REDACTED&*@cosmosoffsuitstorage.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
client = MongoClient(connection_string)
db = client["testdb"]
collection = db["testcollection"]

DOC_FILTER = {"_id": "hit_counter"}

def increment_hit_count():
    updated_doc = collection.find_one_and_update(
        DOC_FILTER,
        {"$inc": {"hits": 1}},
        upsert=True,
        return_document=True
    )
    return updated_doc["hits"]

def store_month_document(month_doc: dict):
    if "_id" not in month_doc:
        raise ValueError("month_doc must have an '_id' field")
    return collection.replace_one({"_id": month_doc["_id"]}, month_doc, upsert=True)

def delete_all_data():
    return collection.delete_many({})

def get_month_document(month_id: str) -> dict:
    """
    Retrieve a month document by its _id (e.g., '202507' for July 2025).
    """
    return collection.find_one({"_id": month_id})
