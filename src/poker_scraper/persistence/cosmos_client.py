from typing import List
from pymongo import MongoClient, ReplaceOne
from poker_scraper.datamodel import Round
from poker_scraper.config import config

connection_string = (config.DATABASE_CONNECTION_STRING)
client = MongoClient(connection_string)
db = client[config.MONGO_DB_NAME]

rounds_collection = db[config.ROUNDS_COLLECTION_NAME]
logs_collection = db[config.LOGS_COLLECITON_NAME]
warnings_collection = db[config.WARNINGS_COLLECTION_NAME]

def store_rounds(rounds: List[Round]) -> None:
    if not rounds:
        return
    
    operations = [
        ReplaceOne(
            filter=round_obj.unique_id(),
            replacement=round_obj.to_dict(),
            upsert=True
        )
        for round_obj in rounds
    ]

    rounds_collection.bulk_write(operations, ordered=False)

def get_all_rounds() -> List[Round]:
    docs = list(rounds_collection.find({}))
    return [Round.from_dict(doc) for doc in docs]


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
            print(round_obj.to_dict())
        
        if len(rounds) == 0:
            print("No rounds found in database.")
        elif len(rounds) > 10:
            print(f"\n... and {len(rounds) - 10} more rounds")
            
    except Exception as e:
        print(f"Error retrieving rounds: {e}")

if __name__ == "__main__":
    main()
