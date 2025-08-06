from typing import List

from pymongo import MongoClient, ReplaceOne

from offsuit_analyzer.datamodel import Round
from offsuit_analyzer.datamodel import NameClash
from offsuit_analyzer.config import config

connection_string = (config.DATABASE_CONNECTION_STRING)
client = MongoClient(connection_string)
db = client[config.MONGO_DB_NAME]

rounds_collection = db[config.ROUNDS_COLLECTION_NAME]
warnings_collection = db[config.WARNINGS_COLLECTION_NAME]
name_clashes_collection = db[config.NAME_INFOS_COLLECTION_NAME]

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

def save_these_name_clashes(name_infos: List[NameClash]) -> None:
    if not name_infos:
        return
    operations = [
        ReplaceOne(
            filter={"name": name_info.unique_id()},
            replacement=name_info.to_dict(),
            upsert=True
        )
        for name_info in name_infos
    ]
    name_clashes_collection.bulk_write(operations, ordered=False)

def get_all_name_clashes() -> List[NameClash]:
    docs = list(name_clashes_collection.find({}))
    return [NameClash.from_dict(doc) for doc in docs]

def delete_these_name_clashes(name_infos: List[NameClash]) -> None:
    if not name_infos:
        return
    names_to_delete = [name_info.name for name_info in name_infos]
    name_clashes_collection.delete_many({"name": {"$in": names_to_delete}})

def delete_all_name_clashes() -> None:
    name_clashes_collection.delete_many({})
