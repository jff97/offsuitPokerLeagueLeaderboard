import requests
from typing import List, Dict, Any

BASE_URL = "https://keepthescore.com/api"

def fetch_board_json(token: str) -> dict:
    url = f"{BASE_URL}/{token}/board/"
    headers = {"accept": "*/*"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

#current implementation of reset board is not allowed but lets look into using api/{token}/board/round/{round_id}
#along with the get entire board endpoint to get all rounds and delete them one by one.
#  
def delete_round(token: str, round_id: int) -> Dict[str, Any]:
    """
    Delete a single round from the board.
    
    Args:
        token: The board token
        round_id: The ID of the round to delete
        
    Returns:
        Dictionary with response or error
    """
    url = f"{BASE_URL}/{token}/board/round/{round_id}"
    headers = {"accept": "*/*"}
    
    try:
        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.text else {"success": True}
    except requests.RequestException as e:
        return {"error": str(e)}


def get_all_round_ids(token: str) -> List[int]:
    """
    Get all round IDs from the board.
    
    Args:
        token: The board token
        
    Returns:
        List of round IDs, or empty list if error
    """
    board_json = fetch_board_json(token)
    
    if "error" in board_json:
        return []
    
    rounds = board_json.get("rounds", [])
    return [round_obj.get("id") for round_obj in rounds if round_obj.get("id") is not None]


def start_new_round(token: str) -> Dict[str, Any]:
    """
    Create a new round on the board.
    
    Args:
        token: The board token
        
    Returns:
        Dictionary with response data including round_id or error
    """
    url = f"{BASE_URL}/{token}/board/round/start"
    headers = {"accept": "*/*", "Content-Type": "application/json"}
    
    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        return response.json() if response.text else {"success": True}
    except requests.RequestException as e:
        return {"error": str(e)}


def get_all_players(token: str) -> Dict[str, int]:
    """
    Get all players on the leaderboard, keyed by their raw (unnormalized) name.
    
    Args:
        token: The board token
        
    Returns:
        Dictionary mapping each player's raw name to their ID
    """
    board_json = fetch_board_json(token)
    
    if "error" in board_json:
        return {}
    
    players = board_json.get("players", [])
    return {p.get("name"): p.get("id") for p in players}


def update_player_score(token: str, round_id: int, player_id: int, score: int) -> Dict[str, Any]:
    """
    Update a player's score in a specific round.
    
    Args:
        token: The board token
        round_id: The ID of the round
        player_id: The ID of the player
        score: The score to set for the player
        
    Returns:
        Dictionary with response data or error
    """
    url = f"{BASE_URL}/{token}/board/round/score"
    headers = {"accept": "*/*", "Content-Type": "application/json"}
    
    payload = {
        "round_id": round_id,
        "player_id": player_id,
        "score": score
    }
    
    try:
        response = requests.patch(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json() if response.text else {"success": True}
    except requests.RequestException as e:
        return {"error": str(e)}


def get_board_title(token: str) -> str:
    """Get the board title from the API.
    
    Args:
        token: The board token
        
    Returns:
        str: The board title, or "Unknown" if not found
    """
    board_json = fetch_board_json(token)
    
    if "error" in board_json:
        return "Unknown"
    
    return board_json.get("board", {}).get("appearance", {}).get("title", "Unknown")


def create_new_player(token: str, player_name: str) -> Dict[str, Any]:
    """
    Create a new player on the board.
    
    Args:
        token: The board token
        player_name: The name of the player to create
        
    Returns:
        Dictionary with response data including player_id or error
    """
    url = f"{BASE_URL}/{token}/player"
    headers = {"accept": "*/*", "Content-Type": "application/json"}
    
    payload = {
        "name": player_name
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json() if response.text else {"success": True}
    except requests.RequestException as e:
        return {"error": str(e)}