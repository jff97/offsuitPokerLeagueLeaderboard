"""Rounds collection operations."""
from typing import List
from pymongo import ReplaceOne
from offsuit_analyzer.datamodel import Round
from . import cosmos_client


def store_rounds(rounds: List[Round]) -> None:
    if not rounds:
        return
    
    collection = cosmos_client.db[cosmos_client.config.ROUNDS_COLLECTION_NAME]
    
    operations = [
        ReplaceOne(
            filter=round_obj.unique_id(),
            replacement=round_obj.to_dict(),
            upsert=True
        )
        for round_obj in rounds
    ]

    collection.bulk_write(operations, ordered=False)


def get_all_rounds() -> List[Round]:
    collection = cosmos_client.db[cosmos_client.config.ROUNDS_COLLECTION_NAME]
    docs = list(collection.find({}))
    return [Round.from_dict(doc) for doc in docs]
