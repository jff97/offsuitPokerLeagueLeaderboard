import re
from typing import List, Dict, Any, Tuple
from datetime import datetime
from keep_the_score_api_service import fetch_board_json

def _flatten_rounds_to_tuples(rounds):
    """
    Convert a list of round documents into a flat list of tuples:
    (player_name, round_id, bar_name, points_scored)
    """
    all_flat_game_records = []

    for round_document in rounds:
        bar_name = round_document.get("bar_name", "")
        round_id = round_document.get("round_id", "")
        scores_list = round_document.get("scores", [])

        for score_entry in scores_list:
            points_scored = score_entry.get("points", 0)
            if points_scored == 0:
                continue  # skip players with 0 points
            raw_name = score_entry.get("name", "")
            normalized_name = _normalize_player_name(raw_name)

            all_flat_game_records.append((normalized_name, round_id, bar_name, points_scored))

    return all_flat_game_records

def flatten_months_to_tuples(month_jsons: List[Dict[str, Any]]) -> List[Tuple[str, str, str, int]]:
    """
    Convert multiple nested JSON month responses into a combined flat list:
    (player_name, round_id, bar_name, points_scored)
    """
    all_flat_game_records = []

    for raw_json_data in month_jsons:
        if not raw_json_data or "bars" not in raw_json_data:
            print("error one of the months is not returning data")
            continue  # Skip invalid or empty month JSON
        for bar_token, bar_details in raw_json_data["bars"].items():
            bar_name = bar_details["bar_name"]

            for round_info in bar_details["rounds"]:
                round_id = round_info["round_id"]

                for score_entry in round_info["scores"]:
                    points_scored = score_entry["points"]
                    if points_scored == 0:
                        continue  #  Skip players with 0 points (like original script)
                    normalized_name = _normalize_player_name(score_entry["name"])
                    all_flat_game_records.append((normalized_name, round_id, bar_name, points_scored))

    return all_flat_game_records

def _fix_special_name_cases(name: str) -> str:
    """Apply specific corrections for known name inconsistencies."""
    if "pyerre" in name:
        return "pyerre l"
    if "bonnie" in name:
        return "bonnie l"
    if "jarrett fre" in name:
        return "jarrett f"
    if "bartman" in name:
        return "brian p"
    if "cindy" in name:
        return "cindy r"
    if "wyatt" in name:
        return "wyatt s"
    if "rieley" in name:
        return "rieley p"
    if "ben" in name:
        return "ben d"
    return name

def _normalize_player_name(raw_name: str) -> str:
    """Clean and standardize player names."""
    name = str(raw_name).strip().lower()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return _fix_special_name_cases(name)

def _map_month_to_list_of_rounds(monthly_data):
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

def get_simplified_month_json(api_tokens_and_bar_names):
    bar_data_list = []

    for token, bar_name in api_tokens_and_bar_names:
        bar_json_from_api = fetch_board_json(token)
        if "error" in bar_json_from_api:
            print(f"Error fetching {bar_name}: {bar_json_from_api['error']}")
            continue
        bar_data_list.append((token, bar_name, bar_json_from_api))
    return build_simplified_month_doc(bar_data_list)

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

def get_flat_list_of_rounds_from_api(api_tokens_and_bar_names):
    list_of_simplified_rounds = _get_list_of_rounds(api_tokens_and_bar_names)
    flattened_records_from_round_format = _flatten_rounds_to_tuples(list_of_simplified_rounds)
    return flattened_records_from_round_format

def legacy_month_list_of_rounds_getter(api_tokens_and_bar_names):
    return flatten_months_to_tuples([get_simplified_month_json(api_tokens_and_bar_names)])