"""Excluded qualifiers collection operations - manages players excluded from monthly qualification."""
from datetime import datetime
from typing import Set
from offsuit_analyzer.config import config
from . import cosmos_client


def _get_collection():
    """Get the excluded qualifiers collection."""
    return cosmos_client.db[config.EXCLUDED_QUALIFIERS_COLLECTION_NAME]


def _should_cleanup() -> bool:
    """
    Check if cleanup should run (between 6th-18th of month).
    
    Returns True if current date is between the 6th and 18th inclusive.
    """
    today = datetime.now().day
    return 6 <= today <= 12


def _cleanup_if_needed() -> None:
    """
    Wipe excluded qualifiers if we're in the middle of the month (6th-18th).
    
    This ensures old exclusions don't carry over to the next month.
    The hook runs whenever qualifications are calculated, so clearing between
    the 6th-18th guarantees we never show old exclusions in new month while
    still protecting current month's exclusions.
    """
    if not _should_cleanup():
        return
    
    collection = _get_collection()
    collection.delete_many({})


def get_excluded_players() -> Set[str]:
    """
    Get all currently excluded player names.
    Runs cleanup hook first to clear old data if needed.
    
    Returns:
        Set of player names currently excluded from qualification
    """
    _cleanup_if_needed()
    
    collection = _get_collection()
    docs = list(collection.find({}))
    
    # Extract player names from documents
    excluded = {doc.get("player_name") for doc in docs if "player_name" in doc}
    return excluded


def set_excluded_players(player_names: Set[str]) -> None:
    """
    Replace the entire set of excluded players.
    
    This is an all-or-nothing sync: whatever players are in the set are excluded,
    anyone not in the set is removed from exclusion (if they were previously excluded).
    
    Args:
        player_names: Set of player names to exclude this month
    """
    collection = _get_collection()
    
    # Clear all existing exclusions
    collection.delete_many({})
    
    # Insert new exclusions with timestamp
    if player_names:
        now = datetime.now().isoformat()
        docs = [
            {
                "_id": player_name,
                "player_name": player_name,
                "excluded_at": now
            }
            for player_name in player_names
        ]
        collection.insert_many(docs)
