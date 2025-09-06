import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from offsuit_analyzer.persistence.cosmos_client import get_all_rounds

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

if __name__ == "__main__":
    export_rounds_to_json()
