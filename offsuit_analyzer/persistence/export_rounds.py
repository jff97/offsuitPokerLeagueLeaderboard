import json
import sys
import os
from datetime import datetime
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from offsuit_analyzer.persistence.cosmos_client import get_all_rounds, store_rounds
from offsuit_analyzer.datamodel.round import Round
from offsuit_analyzer.datamodel.player_score import PlayerScore

def export_rounds_to_json(filename: str = None) -> None:
    """Export all rounds from database to JSON file."""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"rounds_export_{timestamp}.json"
    
    print("Fetching rounds from database...")
    rounds = get_all_rounds()
    
    print(f"Converting {len(rounds)} rounds to JSON...")
    rounds_data = [round_obj.to_dict() for round_obj in rounds]
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(rounds_data, f, indent=2, ensure_ascii=False)
    
    print(f"Exported {len(rounds)} rounds to {filename}")

def get_round_by_id(rounds: List[Round], round_id: str) -> Round:
    """Get a specific round by its unique identifier from a list of rounds."""
    for round_obj in rounds:
        if round_obj.round_id == round_id:
            return round_obj
    raise ValueError(f"Round not found with round_id={round_id}")

def update_player_name_in_round(rounds: List[Round], round_id: str, old_name: str, new_name: str) -> Round:
    """Update a specific player name within a single round and return the updated round."""
    # Get the current round
    current_round = get_round_by_id(rounds, round_id)
    
    # Convert players tuple to list for modification
    updated_players = list(current_round.players)
    
    for i, player in enumerate(updated_players):
        if player.player_name == old_name:
            updated_players[i] = PlayerScore(new_name, player.points)
            # Create new round with updated players
            return Round(
                round_id=current_round.round_id,
                bar_name=current_round.bar_name,
                round_date=current_round.round_date,
                bar_id=current_round.bar_id,
                players=tuple(updated_players)
            )
    
    raise ValueError(f"Player '{old_name}' not found in round {round_id}")

def update_and_save_player_name_in_round(rounds: List[Round], round_id: str, old_name: str, new_name: str) -> Round:
    """Update a specific player name within a single round and save it to database."""
    updated_round = update_player_name_in_round(rounds, round_id, old_name, new_name)
    
    # This will overwrite the existing round in database due to upsert=True in store_rounds
    store_rounds([updated_round])
    
    return updated_round

def run_player_name_update(round_id: str, old_name: str, new_name: str) -> None:
    """Complete workflow: get all rounds, update player name, and save to database."""
    print(f"Fetching all rounds from database...")
    rounds = get_all_rounds()
    print(f"Found {len(rounds)} rounds")
    
    print(f"Updating player '{old_name}' to '{new_name}' in round {round_id}")
    updated_round = update_and_save_player_name_in_round(rounds, round_id, old_name, new_name)
    
    print(f"Successfully updated and saved round {round_id}")

if __name__ == "__main__":
    # Example usage - uncomment and modify as needed
    #run_player_name_update("5425395", "john f", "john fox")
    export_rounds_to_json()
