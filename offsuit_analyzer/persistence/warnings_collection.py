"""Warnings collection operations."""
from typing import List
from . import cosmos_client


def save_warnings(warning_strings: List[str]) -> None:
    """Save multiple warning entries efficiently using bulk insert."""
    if not warning_strings:
        return
    
    collection = cosmos_client.db[cosmos_client.config.WARNINGS_COLLECTION_NAME]
    
    warning_docs = [{"warning": warning_str} for warning_str in warning_strings]
    collection.insert_many(warning_docs)


def get_all_warnings() -> List[str]:
    """Retrieve all warning entries from the database."""
    collection = cosmos_client.db[cosmos_client.config.WARNINGS_COLLECTION_NAME]
    docs = list(collection.find({}, {"_id": 0, "warning": 1}))
    return [doc["warning"] for doc in docs if "warning" in doc]


def delete_all_warnings() -> None:
    """Delete all warning entries from the database."""
    collection = cosmos_client.db[cosmos_client.config.WARNINGS_COLLECTION_NAME]
    collection.delete_many({})
