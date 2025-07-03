import requests
from datetime import datetime

def fetch_board_json(token: str) -> dict:
    url = f"https://keepthescore.com/api/{token}/board/"
    headers = {"accept": "*/*"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def extract_month_from_update_date(update_date_str: str) -> str:
    try:
        dt = datetime.strptime(update_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m")
    except Exception:
        return "unknown_month"

def filter_zero_point_scores(scores: list) -> list:
    """Return only scores where points > 0."""
    return [score for score in scores if score.get("points", 0) > 0]

def extract_scores_from_round(round_obj: dict, players: list) -> list:
    scores = []
    round_scores = round_obj.get("scores", [])
    for idx, score in enumerate(round_scores):
        if idx < len(players):
            player = players[idx]
            scores.append({
                "name": player.get("name"),
                "points": score
            })
    return filter_zero_point_scores(scores)

def build_rounds_list(bar_json: dict) -> list:
    rounds_list = []
    players = bar_json.get("players", [])
    for round_obj in bar_json.get("rounds", []):
        rounds_list.append({
            "round_id": str(round_obj.get("id")),
            "date": round_obj.get("date"),
            "scores": extract_scores_from_round(round_obj, players)
        })
    return rounds_list

def remove_zero_total_players_from_bar(rounds: list) -> list:
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

def build_bar_entry(token: str, bar_name: str, bar_json: dict) -> dict:
    rounds = build_rounds_list(bar_json)
    filtered_rounds = remove_zero_total_players_from_bar(rounds)
    return {
        "bar_name": bar_name,
        "rounds": filtered_rounds
    }

def build_simplified_month_doc(bar_data_list: list) -> dict:
    if not bar_data_list:
        return {"_id": "unknown_month", "month": "unknown_month", "bars": {}}

    first_bar_json = bar_data_list[0][2]
    update_date_str = first_bar_json.get('board', {}).get('update_date', '')
    month_str = extract_month_from_update_date(update_date_str)

    month_doc = {
        "_id": month_str.replace("-", ""),
        "month": month_str,
        "bars": {}
    }

    for api_token, bar_name, bar_json in bar_data_list:
        month_doc["bars"][api_token] = build_bar_entry(api_token, bar_name, bar_json)

    return month_doc

def get_simplified_month_json(api_tokens_and_bar_names):
    bar_data_list = []

    for token, bar_name in api_tokens_and_bar_names:
        bar_json = fetch_board_json(token)
        if "error" in bar_json:
            print(f"Error fetching {bar_name}: {bar_json['error']}")
            continue
        bar_data_list.append((token, bar_name, bar_json))

    return build_simplified_month_doc(bar_data_list)

if __name__ == "__main__":
    tokens_and_names = [
        ("pcynjwvnvgqme", "Hosed on Brady"),
        ("qdtgqhtjkrtpe", "Alibi"),
    ]

    import pprint
    month_doc = get_simplified_month_json(tokens_and_names)
    pprint.pprint(month_doc, depth=8, compact=True)
