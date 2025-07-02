from pymongo import MongoClient

connection_string = "mongodb+srv://jff97:<password>@cosmosoffsuitstorage.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
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
