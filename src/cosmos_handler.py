from pymongo import MongoClient
import socket
from typing import List, Tuple

def _is_localhost():
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
if _is_localhost():
    rounds_collection = db["pokerRoundsCollectionTest"]
else:
    rounds_collection = db["pokerRoundsCollectionProd"]

def store_flattened_rounds(list_of_rounds: list[Tuple[str, str, str, int]]):
    for r in list_of_rounds:
        round_doc = {
            "RoundId": r[0],
            "BarId": r[1],
            "Player": r[2],
            "Placement": r[3],
        }
        rounds_collection.replace_one(
            {"RoundId": round_doc["RoundId"], "BarId": round_doc["BarId"]},
            round_doc,
            upsert=True
        )

def get_round_by_id(round_id: str) -> List[dict]:
    return list(rounds_collection.find({"round_id": round_id}))

def get_all_rounds() -> List[Tuple[str, str, str, int]]:
    raw_docs = list(rounds_collection.find({}))
    return [
        (doc["RoundId"], doc["BarId"], doc["Player"], doc["Placement"])
        for doc in raw_docs
        if all(k in doc for k in ["RoundId", "BarId", "Player", "Placement"])
    ]

def delete_all_round_data():
    return rounds_collection.delete_many({})
