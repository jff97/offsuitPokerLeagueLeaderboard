"""Business logic for tracking players excluded from monthly qualification."""
from typing import List, Set

from offsuit_analyzer import persistence


def get_unavailable_players() -> Set[str]:
    """Get the set of players currently excluded from qualification this month."""
    return persistence.get_excluded_players()


def update_unavailable_players(unavailable_players: List[str]) -> None:
    """Replace the full set of excluded players for this month."""
    persistence.set_excluded_players(set(unavailable_players))
