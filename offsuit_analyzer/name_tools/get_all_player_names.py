from typing import List
from offsuit_analyzer import persistence


def get_all_unique_player_names() -> List[str]:
    """
    Get all unique player names from all rounds.
    
    Returns:
        A sorted list of all unique player names that appear in any round.
    """
    rounds = persistence.get_all_rounds()
    player_names = set()
    
    for round_obj in rounds:
        for player in round_obj.players:
            player_names.add(player.player_name)
    
    return sorted(list(player_names))
