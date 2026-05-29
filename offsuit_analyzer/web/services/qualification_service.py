"""Qualification service - provides API for tournament qualifier calculation."""
from offsuit_analyzer import data_service
from offsuit_analyzer.qualification import get_qualified_players
from offsuit_analyzer.persistence import excluded_qualifiers_collection


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
    return get_qualified_players(this_months_rounds, excluded_set)
