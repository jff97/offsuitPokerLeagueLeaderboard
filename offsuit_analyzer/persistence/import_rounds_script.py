"""Import rounds data from a JSON file into the database."""
import json
from typing import List
from offsuit_analyzer.datamodel import Round
from .rounds_collection import store_rounds


def import_rounds_from_json_file(json_file_path: str) -> None:
    """
    Import a list of rounds from a JSON file and store them in the database.

    Args:
        json_file_path (str): Path to the JSON file containing rounds data.
                              The file should contain a list of dicts compatible with Round.from_dict().
    """
    with open(json_file_path, 'r', encoding='utf-8') as f:
        rounds_data = json.load(f)

    if not isinstance(rounds_data, list):
        raise ValueError("JSON file must contain a list of round objects.")

    rounds: List[Round] = [Round.from_dict(doc) for doc in rounds_data]
    print(f"Loaded {len(rounds)} rounds from JSON file.")
    
    if rounds:
        store_rounds(rounds)
        print(f"Successfully stored {len(rounds)} rounds in the database.")
    else:
        print("No rounds to import.")


if __name__ == "__main__":
    # Example usage - update the path as needed
    json_file_path = "C:\\Users\\jicfo\\Downloads\\20251224_rounds_export\\20251224rounds_export.json"
    import_rounds_from_json_file(json_file_path)
