"""Qualification service - provides API for tournament qualifier calculation."""
from typing import Optional, Set

from offsuit_analyzer import data_service
from offsuit_analyzer.qualification import get_qualified_players


def _parse_excluded_players(excluded_players_param: Optional[str]) -> Set[str]:
    """Parse comma-separated player names into a set."""
    if not excluded_players_param:
        return set()
    return {name.strip() for name in excluded_players_param.split(',') if name.strip()}


def get_tournament_qualifiers(excluded_players: Optional[str] = None):
    """
    Get tournament qualifiers for this month's league season.
    
    Determines top 3 point holders from each bar, handling players who
    qualify at multiple bars by giving them their best placement.
    
    Args:
        excluded_players: Optional comma-separated string of player names to exclude
    
    Returns:
        QualifiedPlayersByBar object with qualified players organized by bar
    """
    excluded_set = _parse_excluded_players(excluded_players)
    this_months_rounds = data_service.get_this_months_rounds_for_bars()
    return get_qualified_players(this_months_rounds, excluded_set)
