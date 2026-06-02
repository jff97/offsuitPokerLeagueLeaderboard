"""
Business logic for manipulating Keep The Score leaderboards.

This module orchestrates multiple API calls to provide higher-level functionality.
It uses keep_the_score_api_client for all API interactions and focuses on business logic.

Jobs:
- Add new rounds with player scores
- Update existing rounds with scores
- Manage players and scores on boards
- Expose services via API to frontend

Note: We don't handle validation/mistakes. Users can update bad data via Keep The Score web page.
"""

from typing import List, Dict, Any, Set
from offsuit_analyzer.data_service import keep_the_score_api_client as api


def _get_player_name_to_id_map(token: str) -> Dict[str, int]:
    """
    Get a mapping of lowercase player names to their IDs.
    
    Args:
        token: The board token
        
    Returns:
        Dictionary mapping lowercase name to player ID
    """
    players = api.get_all_players(token)
    return {p["name"].lower(): p["id"] for p in players}


def _get_existing_player_names(token: str) -> Set[str]:
    """
    Get a set of all existing player names (lowercase).
    
    Args:
        token: The board token
        
    Returns:
        Set of lowercase player names
    """
    players = api.get_all_players(token)
    return {p["name"].lower() for p in players}


def delete_all_rounds(token: str) -> Dict[str, Any]:
    """
    Delete all rounds from a board.
    
    Args:
        token: The board token
        
    Returns:
        Dictionary with deletion summary
    """
    # Get all round IDs
    round_ids = api.get_all_round_ids(token)
    
    # Delete each round
    errors = []
    for round_id in round_ids:
        result = api.delete_round(token, round_id)
        if "error" in result:
            errors.append({"round_id": round_id, "error": result["error"]})
    
    return {
        "deleted_count": len(round_ids) - len(errors),
        "error_count": len(errors),
        "errors": errors
    }


def update_round_scores(token: str, player_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Update player scores in the first available round.
    
    Args:
        token: The board token
        player_scores: List of dicts with 'name' and 'score' keys
                       Example: [{"name": "John", "score": 100}, {"name": "Jane", "score": 90}]
    
    Returns:
        Dictionary with round_id and update results
    """
    # Get name-to-ID mapping
    player_name_to_id = _get_player_name_to_id_map(token)
    
    # Get first available round
    round_ids = api.get_all_round_ids(token)
    if not round_ids:
        return {"error": "No rounds found"}
    
    round_id = round_ids[0]
    
    # Update scores
    for player_data in player_scores:
        player_name = player_data.get("name").lower()
        score = player_data.get("score")
        player_id = player_name_to_id[player_name]
        api.update_player_score(token, round_id, player_id, score)
    
    return {"round_id": round_id, "status": "updated"}


def _add_missing_players(token: str, player_scores: List[Dict[str, Any]]) -> None:
    """
    Add any players that don't exist on the board.
    
    Args:
        token: The board token
        player_scores: List of player data with 'name' keys
    """
    existing_names = _get_existing_player_names(token)
    
    for player_data in player_scores:
        player_name = player_data.get("name")
        if player_name.lower() not in existing_names:
            api.create_new_player(token, player_name)


def _create_new_round(token: str) -> int:
    """
    Create a new zeroed-out round on the board.
    
    Args:
        token: The board token
        
    Returns:
        The ID of the newly created round
        
    Raises:
        ValueError: If the API fails to return a round ID
    """
    result = api.start_new_round(token)
    
    # API returns: {'round': {'id': <id>, ...}, 'success': True}
    round_data = result.get("round", {})
    round_id = round_data.get("id")
    
    if not round_id:
        raise ValueError("Failed to create round - no ID returned from API")
    
    return round_id


def _update_scores_in_round(token: str, round_id: int, player_scores: List[Dict[str, Any]]) -> None:
    """
    Update player scores in a specific round.
    
    Args:
        token: The board token
        round_id: The ID of the round to update
        player_scores: List of dicts with 'name' and 'score' keys
        
    Raises:
        KeyError: If a player is not found after addition attempt
    """
    player_name_to_id = _get_player_name_to_id_map(token)
    
    for player_data in player_scores:
        player_name = player_data.get("name").lower()
        score = player_data.get("score")
        
        if player_name not in player_name_to_id:
            raise KeyError(f"Player '{player_name}' not found after creation attempt")
        
        player_id = player_name_to_id[player_name]
        api.update_player_score(token, round_id, player_id, score)


def add_new_round(token: str, player_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Add a new round with player scores.
    
    Orchestrates:
    1. Add any missing players to the board
    2. Create a new zeroed-out round
    3. Update player scores in the new round
    
    Args:
        token: The board token
        player_scores: List of dicts with 'name' and 'score' keys
                       Example: [{"name": "John", "score": 100}, {"name": "Jane", "score": 90}]
    
    Returns:
        Dictionary with round_id and status
    """
    _add_missing_players(token, player_scores)
    round_id = _create_new_round(token)
    _update_scores_in_round(token, round_id, player_scores)
    
    return {"round_id": round_id, "status": "completed"}
