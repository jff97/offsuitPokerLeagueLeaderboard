import csv
import io
import os
from typing import List, Dict, Any, Tuple
from ..datamodel import Round, PlayerScore
from . import data_converter

def _convert_json_rounds_to_round_objects(rounds: List[Dict[str, Any]]) -> List[Round]:
    """Convert a list of round documents into Round objects. Used by legacy CSV migration."""
    round_objects: List[Round] = []
    for round_doc in rounds:
        # Create PlayerScore objects from scores
        players: List[PlayerScore] = []
        for score_entry in round_doc.get("scores", []):
            if score_entry.get("points", 0) > 0:
                players.append(PlayerScore(
                    player_name=data_converter._normalize_player_name(score_entry["name"]),
                    points=score_entry["points"]
                ))
        
        # Create Round object with simple date
        round_obj = Round(
            round_id=round_doc["round_id"],
            bar_name=round_doc["bar_name"],
            round_date=round_doc["date"],  # Already in YYYY-MM-DD format
            bar_id=round_doc.get("bar_id", "legacy"),  # Store bar identifier, not token
            players=tuple(players)
        )
        round_objects.append(round_obj)
    
    return round_objects

def _map_month_to_list_of_rounds(monthly_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Convert old month document format to flat rounds list. Used for legacy CSV migration."""
    flattened_rounds: List[Dict[str, Any]] = []
    
    for bar_id, bar_info in monthly_data.get('bars', {}).items():
        bar_name: str = bar_info.get('bar_name')
        for round_info in bar_info.get('rounds', []):
            flattened_rounds.append({
                'bar_id': bar_id,
                'bar_name': bar_name,
                **round_info  # Merge in all round data
            })
    
    return flattened_rounds

def _get_csv_file_path(filename: str) -> str:
    """Get the absolute path to a CSV file in the legacy_data directory."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_dir = os.path.join(script_dir, "legacy_data")
    return os.path.join(csv_dir, filename)

def _read_csv_file(filename: str) -> str:
    """Read the contents of a CSV file and return as string."""
    csv_path = _get_csv_file_path(filename)
    with open(csv_path, 'r') as f:
        return f.read().strip()


def _parse_csv_to_bar_entry(csv_data: str, month_id: str, bar_id: str, bar_name: str) -> Dict[str, Dict[str, Any]]:
    """Parse a single bar's CSV into { bar_id: {bar_name, rounds} }."""
    reader = csv.DictReader(io.StringIO(csv_data.strip()))
    
    # Get round columns (skip empty, 'Totals', 'Player')
    round_cols: List[str] = [col for col in reader.fieldnames 
                            if col and col.lower() not in ('totals', 'total', 'player')]
    
    # Initialize rounds with basic structure
    rounds_list: List[Dict[str, Any]] = [{
        "round_id": f"{month_id}_{bar_id}_{idx}",
        "date": f"2025-06-{15 + idx:02d}",  # Simple date format for legacy
        "scores": [],
        "bar_id": bar_id  # Store as identifier, not secret token
    } for idx, _ in enumerate(round_cols, start=1)]
    
    # Process each player row
    for row in reader:
        # Get player name from various possible column names
        player_name: str = next((
            row.get(key, '').strip() 
            for key in ['Player', 'player', ''] + list(row.keys())
            if row.get(key, '').strip()
        ), '').strip()
        
        # Add scores for each round
        for i, round_col in enumerate(round_cols):
            try:
                points: int = int(row.get(round_col, '').strip().split()[0])
                if points > 0:
                    rounds_list[i]["scores"].append({
                        "name": player_name,
                        "points": points
                    })
            except (ValueError, IndexError):
                continue  # Skip invalid scores
    
    return {bar_id: {"bar_name": bar_name, "rounds": rounds_list}}

def _get_legacy_month_as_round_objects(month_id: str, bars: List[Tuple[str, str, str]]) -> List[Round]:
    """Convert legacy CSV data to Round objects."""
    month_doc: Dict[str, Any] = {"bars": {}}
    
    for bar_id, bar_name, csv_data in bars:
        entry = _parse_csv_to_bar_entry(csv_data, month_id, bar_id, bar_name)
        month_doc["bars"].update(entry)
    
    list_of_rounds: List[Dict[str, Any]] = _map_month_to_list_of_rounds(month_doc)
    return _convert_json_rounds_to_round_objects(list_of_rounds)

def get_june_data_as_rounds() -> List[Round]:
    """Get June 2025 legacy data as Round objects."""
    month_id: str = "202506"
    
    # Bar configurations: (bar_id, name, csv_filename) - using bar_id instead of token
    bar_configs: List[Tuple[str, str, str]] = [
        ("june_alibi", "legacyThe Alibi", "alibi.csv"),
        ("june_anticipation_sun", "legacyAnticipation", "anticipationSun.csv"),
        ("june_anticipation_tues", "legacyAnticipation Tues", "anticipationTues.csv"),
        ("june_brickyard", "legacyBrickyard Pub", "brickyard.csv"),
        ("june_chatters", "legacyChatter's", "chatters.csv"),
        ("june_cork_n_barrel", "legacyCork N Barrel", "corkNBarrel.csv"),
        ("june_hosed", "legacyHOSED ON BRADY", "hosed.csv"),
        ("june_lakeside", "legacyLakeside Pub & Grill", "lakeside.csv"),
        ("june_layton_heights", "legacyLAYTON HEIGHTS", "laytonHeights.csv"),
        ("june_mavericks", "legacyMavericks ", "mavricks.csv"),
        ("june_south_bound", "legacySouth Bound Again", "southBound.csv"),
        ("june_tinys", "legacyTiny's A Neighborhood Sports Tavern", "tinys.csv"),
        ("june_witts_end", "legacyWITTS END", "wittsEnd.csv"),
    ]
    
    # Load CSV data for each bar
    bars: List[Tuple[str, str, str]] = [(bar_id, name, _read_csv_file(filename)) 
                                       for bar_id, name, filename in bar_configs]
    
    return _get_legacy_month_as_round_objects(month_id, bars)

if __name__ == "__main__":
    get_june_data_as_rounds()
