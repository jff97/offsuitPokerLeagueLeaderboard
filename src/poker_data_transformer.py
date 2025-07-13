import re
from typing import List, Dict, Any
from datetime import datetime
from keep_the_score_api_service import fetch_board_json
from round import Round
from player_score import PlayerScore

def _convert_json_rounds_to_round_objects(rounds) -> List[Round]:
    """
    Convert a list of round documents into Round objects.
    """
    round_objects = []
    for round_document in rounds:
        bar_name = round_document.get("bar_name", "")
        round_id = round_document.get("round_id", "")
        date = round_document.get("date", "")
        scores_list = round_document.get("scores", [])

        players = []
        for score_entry in scores_list:
            points_scored = score_entry.get("points", 0)
            if points_scored == 0:
                continue
            raw_name = score_entry.get("name", "")
            normalized_name = _normalize_player_name(raw_name)

            player_score = PlayerScore(
                player_name=normalized_name,
                points=points_scored
            )
            players.append(player_score)

        round_obj = Round(
            round_id=round_id,
            bar_name=bar_name,
            date=date,
            players=tuple(players)
        )
        round_objects.append(round_obj)
    return round_objects

def _normalize_player_name(raw_name: str) -> str:
    """Clean and standardize player names."""
    name = str(raw_name).lower() # Convert to string and lowercase for uniformity
    name = re.sub(r'\s+', ' ', name) # Collapse all whitespace (tabs, newlines, multiple spaces) into a single space
    name = re.sub(r'[^a-z0-9 ]', '', name) # Remove all characters except lowercase letters, numbers, and spaces
    name = name.strip() # Remove any leading or trailing spaces (could be left from previous step)

    return name

def _map_month_to_list_of_rounds(monthly_data) -> List[Dict[str, Any]]:
    flattened_rounds = []

    general_month_info = {}
    for key, value in monthly_data.items():
        if key != 'bars' and key != '_id' and key != 'month':
            general_month_info[key] = value

    bars = monthly_data.get('bars', {})

    for bar_id in bars:
        bar_info = bars[bar_id]

        bar_name = bar_info.get('bar_name')

        rounds = bar_info.get('rounds', [])

        for round_info in rounds:
            round_document = {}

            for key in general_month_info:
                round_document[key] = general_month_info[key]

            round_document['bar_id'] = bar_id
            round_document['bar_name'] = bar_name

            for key, value in round_info.items():
                round_document[key] = value

            flattened_rounds.append(round_document)

    return flattened_rounds

def _get_list_of_rounds(api_tokens_and_bar_names):
    bar_data_list = []

    for token, bar_name in api_tokens_and_bar_names:
        bar_json_from_api = fetch_board_json(token)
        if "error" in bar_json_from_api:
            print(f"Error fetching {bar_name}: {bar_json_from_api['error']}")
            continue
        bar_data_list.append((token, bar_name, bar_json_from_api))

    old_schema = build_simplified_month_doc(bar_data_list)
    return _map_month_to_list_of_rounds(old_schema)

def _filter_zero_point_scores(scores: list) -> list:
    """Return only scores where points > 0."""
    return [score for score in scores if score.get("points", 0) > 0]

def _extract_scores_from_round(round_obj: dict, players: list) -> list:
    scores = []
    round_scores = round_obj.get("scores", [])
    for idx, score in enumerate(round_scores):
        if idx < len(players):
            player = players[idx]
            scores.append({
                "name": player.get("name"),
                "points": score
            })
    return _filter_zero_point_scores(scores)

def _build_rounds_list(bar_json: dict) -> list:
    rounds_list = []
    players = bar_json.get("players", [])
    for round_obj in bar_json.get("rounds", []):
        rounds_list.append({
            "round_id": str(round_obj.get("id")),
            "date": round_obj.get("date"),
            "scores": _extract_scores_from_round(round_obj, players)
        })
    return rounds_list

def build_simplified_month_doc(bar_data_list: list) -> dict:
    if not bar_data_list:
        return {"_id": "unknown_month", "month": "unknown_month", "bars": {}}

    first_bar_json = bar_data_list[0][2]
    update_date_str = first_bar_json.get('board', {}).get('update_date', '')
    month_str = _extract_month_from_update_date(update_date_str)

    month_doc = {
        "_id": month_str.replace("-", ""),
        "month": month_str,
        "bars": {}
    }

    for api_token, bar_name, bar_json in bar_data_list:
        month_doc["bars"][api_token] = _build_bar_entry(api_token, bar_name, bar_json)

    return month_doc

def _build_bar_entry(token: str, bar_name: str, bar_json: dict) -> dict:
    rounds = _build_rounds_list(bar_json)
    filtered_rounds = _remove_zero_total_players_from_bar(rounds)
    return {
        "bar_name": bar_name,
        "rounds": filtered_rounds
    }

def _remove_zero_total_players_from_bar(rounds: list) -> list:
    # Find player names who scored > 0 in any round
    players_with_points = set()
    for round_obj in rounds:
        for score in round_obj.get("scores", []):
            if score["points"] > 0:
                players_with_points.add(score["name"])

    # Filter out players with 0 total points
    filtered_rounds = []
    for round_obj in rounds:
        filtered_scores = [s for s in round_obj["scores"] if s["name"] in players_with_points]
        filtered_rounds.append({
            "round_id": round_obj["round_id"],
            "date": round_obj["date"],
            "scores": filtered_scores
        })

    return filtered_rounds

def _extract_month_from_update_date(update_date_str: str) -> str:
    try:
        dt = datetime.strptime(update_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m")
    except Exception:
        return "unknown_month"

def get_list_of_rounds_from_api(api_tokens_and_bar_names) -> List[Round]:
    list_of_simplified_rounds = _get_list_of_rounds(api_tokens_and_bar_names)
    round_objects = _convert_json_rounds_to_round_objects(list_of_simplified_rounds)
    return round_objects
