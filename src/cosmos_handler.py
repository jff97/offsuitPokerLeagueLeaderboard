from typing import List
from pymongo import MongoClient
import socket
from player_at_round_result import PlayerAtRoundResult

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

def store_flattened_rounds(entries: List[PlayerAtRoundResult]):
    for entry in entries:
        rounds_collection.replace_one(
            filter=entry.unique_id(),
            replacement=entry.to_dict(),
            upsert=True
        )

def get_all_round_entries() -> List[PlayerAtRoundResult]:
    docs = list(rounds_collection.find({}))
    return [PlayerAtRoundResult.from_dict(doc) for doc in docs]

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
