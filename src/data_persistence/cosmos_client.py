from typing import List
from pymongo import MongoClient
import socket
from poker_datamodel import Round

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
    warnings_collection = db["warningsCollectionTest"]
else:
    rounds_collection = db["pokerRoundsCollectionProd"]
    logs_collection = db["logsCollectionProd"]
    warnings_collection = db["warningsCollectionProd"]

def store_rounds(rounds: List[Round]):
    for round_obj in rounds:
        rounds_collection.replace_one(
            filter=round_obj.unique_id(),
            replacement=round_obj.to_dict(),
            upsert=True
        )

def get_all_rounds() -> List[Round]:
    docs = list(rounds_collection.find({}))
    return [Round.from_dict(doc) for doc in docs]

def delete_all_round_data() -> None:
    return rounds_collection.delete_many({})

def save_log(log_str: str) -> None:
    log_doc = {"log": log_str}
    logs_collection.insert_one(log_doc)

def save_logs(log_strings: List[str]) -> None:
    """Save multiple log entries efficiently using bulk insert."""
    if not log_strings:
        return
    
    log_docs = [{"log": log_str} for log_str in log_strings]
    logs_collection.insert_many(log_docs)

def get_all_logs() -> List[str]:
    """Retrieve all log entries from the database."""
    docs = list(logs_collection.find({}, {"_id": 0, "log": 1}))
    return [doc["log"] for doc in docs if "log" in doc]

def delete_all_logs() -> None:
    """Delete all log entries from the database."""
    logs_collection.delete_many({})

def save_warning(warning_str: str) -> None:
    """Save a single warning entry to the database."""
    warning_doc = {"warning": warning_str}
    warnings_collection.insert_one(warning_doc)

def save_warnings(warning_strings: List[str]) -> None:
    """Save multiple warning entries efficiently using bulk insert."""
    if not warning_strings:
        return
    
    warning_docs = [{"warning": warning_str} for warning_str in warning_strings]
    warnings_collection.insert_many(warning_docs)

def get_all_warnings() -> List[str]:
    """Retrieve all warning entries from the database."""
    docs = list(warnings_collection.find({}, {"_id": 0, "warning": 1}))
    return [doc["warning"] for doc in docs if "warning" in doc]

def delete_all_warnings() -> None:
    """Delete all warning entries from the database."""
    warnings_collection.delete_many({})

def main():
    """Print 10 rounds from the database for testing purposes."""
    try:
        rounds = get_all_rounds()
        print(f"Total rounds in database: {len(rounds)}")
        print("\nFirst 10 rounds:")
        print("-" * 80)
        
        for i, round_obj in enumerate(rounds[:10]):
            print(f"\nRound {i+1}:")
            print(f"  ID: {round_obj.round_id}")
            print(f"  Bar: {round_obj.bar_name}")
            print(f"  Date: {round_obj.round_date}")
            print(f"  Players ({len(round_obj.players)}):")
            
            # Sort players by points descending for better readability
            sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
            for j, player in enumerate(sorted_players):
                print(f"    {j+1}. {player.player_name}: {player.points} points")
        
        if len(rounds) == 0:
            print("No rounds found in database.")
        elif len(rounds) > 10:
            print(f"\n... and {len(rounds) - 10} more rounds")
            
    except Exception as e:
        print(f"Error retrieving rounds: {e}")

if __name__ == "__main__":
    main()
