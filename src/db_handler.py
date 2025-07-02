from pymongo import MongoClient

connection_string = "mongodb://your_primary_connection_string_here"
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
