import re
from typing import List, Dict, Any, Tuple
from . import api_client
from poker_scraper.datamodel import Round, PlayerScore
from . import date_utils

def _create_round_object(round_data: Dict[str, Any]) -> Round:
    """Create a Round object from round data dictionary."""
    players: List[PlayerScore] = []
    for score_entry in round_data.get("scores", []):
        points_scored: int = score_entry.get("points", 0)
        if points_scored <= 0:
            continue
        
        normalized_name: str = _normalize_player_name(score_entry["name"])
        player_score: PlayerScore = PlayerScore(
            player_name=normalized_name,
            points=points_scored
        )
        players.append(player_score)

    return Round(
        round_id=round_data["round_id"],
        bar_name=round_data["bar_name"],
        round_date=round_data["round_date"],  # Already converted date
        bar_id=round_data.get("bar_id", ""),  # Store bar identifier, not token
        players=tuple(players)
    )

def _normalize_player_name(raw_name: str) -> str:
    """Clean and standardize player names."""
    name = str(raw_name).lower() # Convert to string and lowercase for uniformity
    name = re.sub(r'\s+', ' ', name) # Collapse all whitespace (tabs, newlines, multiple spaces) into a single space
    name = re.sub(r'[^a-z0-9 ?]', '', name) # Remove all characters except lowercase letters, numbers, and spaces
    name = name.strip() # Remove any leading or trailing spaces (could be left from previous step)

    return name

def get_list_of_rounds_from_api(api_tokens_with_day: List[Tuple[str, int]]) -> List[Round]:
    """Fetch API data and convert directly to Round objects with correct round dates."""
    all_rounds: List[Round] = []

    for token, target_weekday in api_tokens_with_day:
        bar_json_from_api: Dict[str, Any] = api_client.fetch_board_json(token)
        if "error" in bar_json_from_api:
            print(f"Error fetching token {token}: {bar_json_from_api['error']}")
            continue
        
        # Convert this bar's data directly to Round objects
        bar_rounds: List[Round] = _convert_bar_json_to_round_objects(token, target_weekday, bar_json_from_api)
        all_rounds.extend(bar_rounds)

    return all_rounds

def _convert_bar_json_to_round_objects(bar_token: str, target_weekday: int, bar_json: Dict[str, Any]) -> List[Round]:
    """Convert a single bar's API JSON directly to Round objects with correct round dates."""
    # Extract bar info from the JSON
    board_info = bar_json.get("board", {})
    bar_name: str = board_info.get("appearance", {}).get("title", "Unknown Bar")
    board_id: str = str(board_info.get("id", "unknown"))  # Use board ID as bar_id
    
    players: List[Dict[str, Any]] = bar_json.get("players", [])
    
    # First pass: collect all rounds with scores
    temp_rounds: List[Dict[str, Any]] = []
    for round_obj in bar_json.get("rounds", []):
        scores: List[Dict[str, Any]] = []
        round_scores: List[int] = round_obj.get("scores", [])
        for idx, score in enumerate(round_scores):
            if idx < len(players) and score > 0:  # Only include non-zero scores
                player: Dict[str, Any] = players[idx]
                scores.append({
                    "name": player.get("name"),
                    "points": score
                })
        
        # Only include rounds that have players with points
        if scores:
            entry_date = round_obj.get("date")
            # Convert API entry date to actual round date immediately
            actual_round_date = date_utils.calculate_poker_night_date(entry_date, target_weekday) if entry_date else None
            
            temp_rounds.append({
                "round_id": str(round_obj.get("id")),
                "bar_id": board_id,  # Use board ID from API, not token
                "bar_name": bar_name,
                "round_date": actual_round_date,  # Store calculated date
                "scores": scores
            })
    
    # Second pass: filter out players with 0 total points across all rounds
    filtered_rounds: List[Dict[str, Any]] = _remove_zero_total_players_from_rounds(temp_rounds)
    
    # Third pass: convert to Round objects using shared function
    return [_create_round_object(round_data) for round_data in filtered_rounds]

def _remove_zero_total_players_from_rounds(rounds: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Remove players who have 0 total points across all rounds."""
    # Calculate total points for each player
    player_totals: Dict[str, int] = {}
    for round_obj in rounds:
        for score in round_obj["scores"]:
            player_name: str = score["name"]
            player_totals[player_name] = player_totals.get(player_name, 0) + score["points"]
    
    # Get players with > 0 total points
    players_with_points: set[str] = {name for name, total in player_totals.items() if total > 0}
    
    # Filter rounds to only include players with > 0 total points
    filtered_rounds: List[Dict[str, Any]] = []
    for round_obj in rounds:
        filtered_scores: List[Dict[str, Any]] = [s for s in round_obj["scores"] if s["name"] in players_with_points]
        if filtered_scores:  # Only include rounds that still have players
            filtered_rounds.append({
                **round_obj,  # Copy all round data
                "scores": filtered_scores  # Replace with filtered scores
            })
    
    return filtered_rounds
