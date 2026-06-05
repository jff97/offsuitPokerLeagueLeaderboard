import re
from typing import List, Dict, Any
from offsuit_analyzer.datamodel import Round, PlayerScore
from offsuit_analyzer import email_smtp_service
from offsuit_analyzer.config import config, BarConfig
from . import date_utils
from . import keep_the_score_api_client


def get_this_months_rounds_for_bars() -> List[Round]:
    """
    Fetch poker rounds for configured bars from all data sources.
    
    Returns:
        List of Round objects with calculated poker night dates from API and legacy sources
    """
    # Get API rounds using configured bar settings
    api_rounds = _get_list_of_rounds_from_api(config.BAR_CONFIGS)
    
    return api_rounds


def normalize_player_name(raw_name: str) -> str:
    """Clean and standardize player names."""
    name = str(raw_name).lower() # Convert to string and lowercase for uniformity
    name = re.sub(r'\s+', ' ', name) # Collapse all whitespace (tabs, newlines, multiple spaces) into a single space
    name = re.sub(r'[^a-z0-9 ?]', '', name) # Remove all characters except lowercase letters, numbers, and spaces, and ?
    name = name.strip() # Remove any leading or trailing spaces (could be left from previous step)

    return name



def _get_list_of_rounds_from_api(bar_configs: List[BarConfig]) -> List[Round]:
    """Fetch API data and convert directly to Round objects with correct round dates."""
    all_rounds: List[Round] = []
    for bar_config in bar_configs:
        bar_json_from_api: Dict[str, Any] = keep_the_score_api_client.fetch_board_json(bar_config.token)
        if "error" in bar_json_from_api:
            _email_keep_the_score_error(f"Error fetching token {bar_config.token}: {bar_json_from_api['error']}")
            continue
        
        # Convert this bar's data directly to Round objects
        bar_rounds: List[Round] = _convert_bar_json_to_round_objects(bar_config, bar_json_from_api)
        all_rounds.extend(bar_rounds)

    return all_rounds

def _email_keep_the_score_error(error_text: str):
    email_smtp_service.send_email(config.ADMIN_EMAIL, "Keep The Score API Error", error_text)

def _convert_bar_json_to_round_objects(bar_config: BarConfig, bar_json: Dict[str, Any]) -> List[Round]:
    """Convert a single bar's API JSON directly to Round objects with correct round dates.
    
    Builds Round objects directly with normalized player names and filtered scores.
    """
    # Extract bar info from the JSON
    board_info = bar_json.get("board", {})
    bar_name: str = board_info.get("appearance", {}).get("title", "Unknown Bar")
    board_id: str = str(board_info.get("id", "unknown"))
    
    players: List[Dict[str, Any]] = bar_json.get("players", [])
    
    # Build Round objects directly with normalized names and filtered scores
    all_rounds: List[Round] = []
    for round_obj in bar_json.get("rounds", []):
        player_scores: List[PlayerScore] = []
        round_scores: List[int] = round_obj.get("scores", [])
        
        for idx, score in enumerate(round_scores):
            if idx < len(players) and score > 0:  # Only include non-zero scores
                player: Dict[str, Any] = players[idx]
                player_name: str = player.get("name", "")
                normalized_name: str = normalize_player_name(player_name)
                
                player_score: PlayerScore = PlayerScore(
                    player_name=normalized_name,
                    points=score
                )
                player_scores.append(player_score)
        
        # Only create Round if it has players with points
        if player_scores:
            entry_date = round_obj.get("date")
            actual_round_date = date_utils.calculate_poker_night_date(entry_date, bar_config.poker_night) if entry_date else None
            
            round_object: Round = Round(
                round_id=str(round_obj.get("id")),
                bar_name=bar_name,
                round_date=actual_round_date,
                bar_id=board_id,
                players=tuple(player_scores)
            )
            all_rounds.append(round_object)
    
    # Filter out players with 0 total points across all rounds
    filtered_rounds: List[Round] = _remove_zero_total_players_from_rounds(all_rounds)
    
    return filtered_rounds

def _remove_zero_total_players_from_rounds(rounds: List[Round]) -> List[Round]:
    """Remove players who have 0 total points across all rounds."""
    # Calculate total points for each player
    player_totals: Dict[str, int] = {}
    for round_obj in rounds:
        for player_score in round_obj.players:
            player_totals[player_score.player_name] = player_totals.get(player_score.player_name, 0) + player_score.points
    
    # Get players with > 0 total points
    players_with_points: set[str] = {name for name, total in player_totals.items() if total > 0}
    
    # Filter rounds to only include players with > 0 total points
    filtered_rounds: List[Round] = []
    for round_obj in rounds:
        filtered_player_scores: List[PlayerScore] = [p for p in round_obj.players if p.player_name in players_with_points]
        
        if filtered_player_scores:  # Only include rounds that still have players
            filtered_round: Round = Round(
                round_id=round_obj.round_id,
                bar_name=round_obj.bar_name,
                round_date=round_obj.round_date,
                bar_id=round_obj.bar_id,
                players=tuple(filtered_player_scores)
            )
            filtered_rounds.append(filtered_round)
    
    return filtered_rounds
