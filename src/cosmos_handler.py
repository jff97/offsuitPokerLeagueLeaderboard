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
    logs_collection = db["logsCollectionTest"]
else:
    rounds_collection = db["pokerRoundsCollectionProd"]
    logs_collection = db["logsCollectionProd"]

def store_flattened_rounds(list_of_rounds: List[Tuple[str, str, str, int]]):
    for r in list_of_rounds:
        # (player_name, round_id, bar_name, points_scored)
        round_doc = {
            "Player": r[0],   # player_name
            "RoundId": r[1],  # round_id
            "BarName": r[2],    # bar_name
            "Points": r[3],   # points_scored
        }
        rounds_collection.replace_one(
            {
                "Player": round_doc["Player"],
                "RoundId": round_doc["RoundId"],
                "BarName": round_doc["BarName"]
            },
            round_doc,
            upsert=True
        )

def get_round_by_id(round_id: str) -> List[dict]:
    return list(rounds_collection.find({"RoundId": round_id}))

def get_all_rounds() -> List[Tuple[str, str, str, int]]:
    raw_docs = list(rounds_collection.find({}))
    return [
        (doc["Player"], doc["RoundId"], doc["BarName"], doc["Points"])
        for doc in raw_docs
        if all(k in doc for k in ["Player", "RoundId", "BarName", "Points"])
    ]

def delete_all_round_data():
    return rounds_collection.delete_many({})

def save_log(log_str: str):
    log_doc = {"log": log_str}
    logs_collection.insert_one(log_doc)

def get_all_logs() -> List[str]:
    docs = list(logs_collection.find({}, {"_id": 0, "log": 1}))
    return [doc["log"] for doc in docs if "log" in doc]

def delete_all_logs():
    logs_collection.delete_many({})
