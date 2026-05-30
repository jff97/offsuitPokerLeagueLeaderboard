"""Qualification service - provides API for tournament qualifier calculation."""
from typing import List, Tuple
from offsuit_analyzer import data_service, analytics
from offsuit_analyzer.persistence import excluded_qualifiers_collection
from . import admin_service


def get_tournament_qualifiers():
    """
    Get tournament qualifiers for this month's league season.
    
    Determines top 3 point holders from each bar, handling players who
    qualify at multiple bars by giving them their best placement.
    
    Exclusions are managed via excluded_qualifiers_collection which provides
    a cleanup hook to wipe old exclusions mid-month (6th-18th).
    
    Returns:
        QualifiedPlayersByBar object with qualified players organized by bar
    """
    # Get excluded players from persistent collection (runs cleanup hook)
    excluded_set = excluded_qualifiers_collection.get_excluded_players()
    
    this_months_rounds = data_service.get_this_months_rounds_for_bars()
    return analytics.get_qualified_players(this_months_rounds, excluded_set)


def update_unavailable_players(unavailable_players: List[str]) -> Tuple[bool, str]:
    """
    Update the list of excluded players and refresh frontend leaderboard caches.
    
    This is a full sync operation: the provided list becomes the complete
    set of excluded players. Anyone not in the list is un-excluded.
    
    Args:
        unavailable_players: List of player names to exclude from qualification
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Update the collection (this replaces the entire list)
    excluded_qualifiers_collection.set_excluded_players(set(unavailable_players))
    
    # Trigger frontend update to refresh leaderboard caches
    success, message, _ = admin_service.trigger_frontend_update()
    if not success:
        print(f"Warning: Failed to trigger frontend update: {message}")
    
    return success, message
