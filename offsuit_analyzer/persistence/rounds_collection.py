"""Rounds collection operations."""
from typing import List
from pymongo import ReplaceOne
from functools import cache
from offsuit_analyzer.datamodel import Round
from . import cosmos_client


def store_rounds(rounds: List[Round]) -> None:
    # Clear cache because if you are storing new rounds, the cache is now stale and should be refreshed on next read.
    clear_rounds_cache()  
    
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

def delete_round(round_id: str) -> bool:
    """Delete a round by its round ID.

    Args:
        round_id: The ID of the round to delete.

    Returns:
        True if a round was deleted, False otherwise.
    """
    # Clear cache because if you are deleting a round, the cache is now stale and should be refreshed on next read.
    clear_rounds_cache()  
    collection = cosmos_client.db[cosmos_client.config.ROUNDS_COLLECTION_NAME]
    result = collection.delete_one({"round_id": round_id})
    return result.deleted_count > 0

@cache
def get_all_rounds() -> List[Round]:
    collection = cosmos_client.db[cosmos_client.config.ROUNDS_COLLECTION_NAME]
    docs = list(collection.find({}))
    return [Round.from_dict(doc) for doc in docs]

def clear_rounds_cache() -> None:
    """Clear the cached rounds data."""
    get_all_rounds.cache_clear()


if __name__ == "__main__":
    round_id = ""

    success = delete_round(round_id)

    if success:
        print(f"Deleted round with id: {round_id}")
    else:
        print(f"No round found with id: {round_id}")