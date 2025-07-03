from datetime import datetime
import pprint
from keep_the_score_api_service import fetch_board_json

def extract_month_from_update_date(update_date_str: str) -> str:
    try:
        dt = datetime.strptime(update_date_str, "%a, %d %b %Y %H:%M:%S %Z")
        return dt.strftime("%Y-%m")
    except Exception:
        return "unknown_month"

def extract_scores_from_round(round_obj: dict, players: list) -> list:
    scores = []
    round_scores = round_obj.get("scores", [])
    for idx, score in enumerate(round_scores):
        if idx < len(players):
            player = players[idx]
            scores.append({
                "player_id": str(player.get("id")),
                "name": player.get("name"),
                "points": score
            })
    return scores

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

def build_bar_entry(token: str, bar_name: str, bar_json: dict) -> dict:
    return {
        "bar_name": bar_name,
        "rounds": build_rounds_list(bar_json)
    }

def build_month_doc(bar_data_list: list) -> dict:
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

    for token, bar_name, bar_json in bar_data_list:
        month_doc["bars"][token] = build_bar_entry(token, bar_name, bar_json)

    return month_doc

def tester_simulate_month_storage(tokens_and_names):
    bar_data_list = []

    for token, bar_name in tokens_and_names:
        print(f"Fetching data for bar '{bar_name}' with token '{token}'...")
        bar_json = fetch_board_json(token)
        if "error" in bar_json:
            print(f"Error fetching {bar_name}: {bar_json['error']}")
            continue
        bar_data_list.append((token, bar_name, bar_json))

    month_doc = build_month_doc(bar_data_list)

    print("\n=== Simulated Storage ===")
    print(f"Would store document with _id: {month_doc['_id']}")
    print("Document contents preview:")
    pprint.pprint(month_doc, depth=10, compact=True)


if __name__ == "__main__":
    tokens_and_names = [
        ("pcynjwvnvgqme", "Hosed on Brady")
    ]

    tester_simulate_month_storage(tokens_and_names)
