from typing import List
from offsuit_analyzer.datamodel import Round, PlayerScore
from offsuit_analyzer.persistence import cosmos_client
from offsuit_analyzer.config import config

def add_hardcoded_round() -> None:
    """Add a manually created round with hardcoded parameters."""
    
    # Store original collection name
    original_collection_name = config.ROUNDS_COLLECTION_NAME
    
    try:
        # Temporarily switch to dev collection (or any other collection)
        config.ROUNDS_COLLECTION_NAME = "pokerRoundsCollectionDev"
        
        # Hardcoded round parameters
        round_id = "PabstLightLayton20250808"
        bar_name = "Pabst Light Plunder 2025-08-08"
        round_date = "2025-08-08"  # YYYY-MM-DD format
        bar_id = "PabstLightFakeBarID"
        
        # Hardcoded player scores - modify these as needed
        player_scores = [
            PlayerScore(player_name="greg h", points=30),
            PlayerScore(player_name="john f", points=25),
            PlayerScore(player_name="bill e", points=20),
            PlayerScore(player_name="lori h", points=15),
            PlayerScore(player_name="donovan b", points=10),
            PlayerScore(player_name="charlie t", points=8),
            PlayerScore(player_name="brandon c", points=6),
            PlayerScore(player_name="carol f", points=4),
            PlayerScore(player_name="geralyn g", points=2),
            PlayerScore(player_name="wyatt s", points=1),
        ]
        
        # Create the Round object
        manual_round = Round(
            round_id=round_id,
            bar_name=bar_name,
            round_date=round_date,
            bar_id=bar_id,
            players=tuple(player_scores)
        )
        
        # Store the round using cosmos client
        rounds_to_store: List[Round] = [manual_round]
        cosmos_client.store_rounds(rounds_to_store)
        
        print(f"✅ Successfully added manual round to {config.ROUNDS_COLLECTION_NAME}: {round_id}")
        print(f"   Bar: {bar_name}")
        print(f"   Date: {round_date}")
        print(f"   Players: {len(player_scores)}")
        
    finally:
        # Always restore original collection name
        config.ROUNDS_COLLECTION_NAME = original_collection_name

if __name__ == "__main__":
    add_hardcoded_round()
