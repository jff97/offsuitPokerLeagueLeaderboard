from pymongo import MongoClient
import socket
from typing import List, Tuple


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
    rounds_collection = db["pokerRoundsCollectionTest"]
else:
    collection = db["monthly_data_prod"]   # Production collection
    rounds_collection = db["pokerRoundsCollectionProd"]

def store_month_document(month_doc: dict):
    if "_id" not in month_doc:
        raise ValueError("month_doc must have an '_id' field")
    return collection.replace_one({"_id": month_doc["_id"]}, month_doc, upsert=True)

def delete_all_data():
    return collection.delete_many({})

def delete_all_round_data():
    return rounds_collection.delete_many({})

def get_month_document(month_id: str) -> dict:
    return collection.find_one({"_id": month_id})

def store_flattened_rounds(list_of_rounds: list[Tuple[str, str, str, int]]):
    for r in list_of_rounds:
        round_doc = {
            "RoundId": r[0],
            "BarId": r[1],
            "Player": r[2],
            "Placement": r[3],
        }
        collection.replace_one(
            {"RoundId": round_doc["RoundId"], "BarId": round_doc["BarId"]},
            round_doc,
            upsert=True
        )


def get_round_by_id(round_id: str) -> List[dict]:
    return list(collection.find({"round_id": round_id}))

# Get all flattened player-round records from the collection
def get_all_rounds() -> List[Tuple[str, str, str, int]]:
    raw_docs = list(collection.find({}))
    return [
        (doc["RoundId"], doc["BarId"], doc["Player"], doc["Placement"])
        for doc in raw_docs
        if all(k in doc for k in ["RoundId", "BarId", "Player", "Placement"])
    ]

