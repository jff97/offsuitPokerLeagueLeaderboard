import requests
from datetime import datetime
import re
from collections import defaultdict
from pymongo import MongoClient
import pandas as pd
from operator import itemgetter
from itertools import groupby

# === CONFIGURATION ===
CONNECTION_STRING = "mongodb+srv://jff97:REDACTED&*@cosmosoffsuitstorage.global.mongocluster.cosmos.azure.com/?tls=true&authMechanism=SCRAM-SHA-256&retrywrites=false&maxIdleTimeMS=120000"
DB_NAME = "testdb"
COLLECTION_NAME = "pokerRoundsCollection"

# Put your API tokens and bar names here
TOKENS_AND_BARS = [
    ("qdtgqhtjkrtpe", "Alibi"),
    ("jykjlbzxzkqye", "Cork N Barrel"),
    ("xpwtrdfsvdtce", "Chatters"),
    ("czyvrxfdrjbye", "Mavricks"),
    ("vvkcftdnvdvge", "Layton Heights"),
    ("tbyyvqmpjsvke", "Tinys"),
    ("pcynjwvnvgqme", "Hosed on Brady"),
    ("jkhwxjkpxycle", "Witts End"),
    ("khptcxdgnpnbe", "Lakeside"),
    ("zyqphgqxppcde", "Brickyard Pub"),
    ("ybmwcqckckdhe", "South Bound Again"),
    ("pwtmrylcjnjye", "Anticipation Sunday"),
]

# === DATABASE SETUP ===
client = MongoClient(CONNECTION_STRING)
db = client[DB_NAME]
poker_rounds_collection = db[COLLECTION_NAME]

# === UTILITY FUNCTIONS ===

def fetch_board_json(token: str) -> dict:
    url = f"https://keepthescore.com/api/{token}/board/"
    headers = {"accept": "*/*"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API error for token {token}: {e}")
        return {}

def extract_scores_from_round(round_obj: dict, players: list) -> list:
    scores = []
    round_scores = round_obj.get("scores", [])
    for idx, score in enumerate(round_scores):
        if idx < len(players):
            player = players[idx]
            points = score if isinstance(score, (int, float)) else 0
            if points > 0:
                scores.append({
                    "name": player.get("name"),
                    "points": points
                })
    return scores

def build_round_documents(token: str, bar_name: str, bar_json: dict) -> list:
    rounds_docs = []
    players = bar_json.get("players", [])
    for round_obj in bar_json.get("rounds", []):
        round_id = round_obj.get("id")
        date = round_obj.get("date")
        scores = extract_scores_from_round(round_obj, players)
        if not scores:
            continue  # skip rounds with no scores > 0
        rounds_docs.append({
            "_id": f"{token}_{round_id}",
            "round_id": str(round_id),
            "bar_name": bar_name,
            "date": date,
            "scores": scores
        })
    return rounds_docs

def normalize_player_name(raw_name: str) -> str:
    name = str(raw_name).strip().lower()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    # Fix special cases if needed
    if "pyerre" in name:
        return "pyerre l"
    if "bonnie" in name:
        return "bonnie l"
    if "jarrett fre" in name:
        return "jarrett f"
    if "bartman" in name:
        return "brian p"
    return name

def calculate_percentile_rank(placement: int, total_players: int) -> float:
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)

def flatten_all_rounds_to_tuples(round_docs: list) -> list:
    """
    Converts round documents into flat tuples:
    (player_name, round_id, bar_name, points_scored)
    """
    flat_records = []
    for round_doc in round_docs:
        round_id = round_doc["round_id"]
        bar_name = round_doc["bar_name"]
        for score in round_doc["scores"]:
            points = score["points"]
            if points == 0:
                continue
            normalized_name = normalize_player_name(score["name"])
            flat_records.append((normalized_name, round_id, bar_name, points))
    return flat_records

def rank_players_in_each_round(flat_game_records: list) -> list:
    ranked_results = []
    flat_game_records.sort(key=itemgetter(1))  # sort by round_id

    for round_id, group in groupby(flat_game_records, key=itemgetter(1)):
        players = list(group)
        players_sorted = sorted(players, key=lambda x: x[3], reverse=True)
        total_players = len(players_sorted)

        point_to_placement = {}
        for idx, (_, _, _, pts) in enumerate(players_sorted):
            if pts not in point_to_placement:
                point_to_placement[pts] = idx + 1

        for player_name, _, bar_name, pts in players_sorted:
            placement = point_to_placement[pts]
            percentile = calculate_percentile_rank(placement, total_players)
            ranked_results.append({
                "Player": player_name,
                "RoundID": round_id,
                "BarName": bar_name,
                "PercentileRank": percentile,
                "Placement": placement
            })
    return ranked_results

def build_percentile_leaderboard(flat_game_records: list, min_rounds_required=2) -> pd.DataFrame:
    ranked_results = rank_players_in_each_round(flat_game_records)
    player_stats = defaultdict(lambda: {"TotalPercentile": 0, "RoundsPlayed": 0})

    for res in ranked_results:
        p = res["Player"]
        player_stats[p]["TotalPercentile"] += res["PercentileRank"]
        player_stats[p]["RoundsPlayed"] += 1

    leaderboard = []
    for player, stats in player_stats.items():
        if stats["RoundsPlayed"] >= min_rounds_required:
            avg_percentile = round(stats["TotalPercentile"] / stats["RoundsPlayed"], 2)
            leaderboard.append({
                "Player": player,
                "RoundsPlayed": stats["RoundsPlayed"],
                "AveragePercentileRank": avg_percentile
            })

    df = pd.DataFrame(leaderboard)
    df.sort_values(by="AveragePercentileRank", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def build_top3_finish_rate_leaderboard(flat_game_records: list, min_rounds=8) -> pd.DataFrame:
    ranked_results = rank_players_in_each_round(flat_game_records)
    top3_counts = defaultdict(int)
    total_counts = defaultdict(int)

    for res in ranked_results:
        player = res["Player"]
        placement = res["Placement"]
        total_counts[player] += 1
        if placement <= 3:
            top3_counts[player] += 1

    leaderboard = []
    for player, total in total_counts.items():
        if total < min_rounds:
            continue
        top3 = top3_counts[player]
        rate = round((top3 / total) * 100, 2)
        leaderboard.append({
            "Player": player,
            "Top3Finishes": top3,
            "RoundsPlayed": total,
            "Top3RatePercent": rate
        })

    df = pd.DataFrame(leaderboard)
    df.sort_values(by="Top3RatePercent", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

# === MAIN FLOW ===

def refresh_data(api_tokens_and_bars):
    print("Deleting old round documents from MongoDB...")
    poker_rounds_collection.delete_many({})

    print("Fetching new data and storing rounds...")
    all_round_docs = []
    for token, bar_name in api_tokens_and_bars:
        bar_json = fetch_board_json(token)
        if not bar_json or "error" in bar_json:
            print(f"Skipping bar {bar_name} due to fetch error.")
            continue
        rounds_docs = build_round_documents(token, bar_name, bar_json)
        all_round_docs.extend(rounds_docs)

    if not all_round_docs:
        print("No round data to store. Exiting.")
        return

    # Bulk insert all rounds
    poker_rounds_collection.insert_many(all_round_docs)
    print(f"Inserted {len(all_round_docs)} rounds into MongoDB.")

def load_all_rounds() -> list:
    return list(poker_rounds_collection.find({}))

def main():
    refresh_data(TOKENS_AND_BARS)
    print("\nLoading rounds from DB for analysis...")
    round_docs = load_all_rounds()

    flat_records = flatten_all_rounds_to_tuples(round_docs)
    if not flat_records:
        print("No game records found after flattening.")
        return

    print("\n🏆 Percentile Leaderboard (min 8 rounds played):")
    percentile_df = build_percentile_leaderboard(flat_records)
    if percentile_df.empty:
        print("No players qualified for the percentile leaderboard.")
    else:
        print(percentile_df.to_string(index=False))

    print("\n🥇 Top 3 Finish Rate Leaderboard (min 8 rounds played):")
    top3_df = build_top3_finish_rate_leaderboard(flat_records)
    if top3_df.empty:
        print("No players qualified for the top 3 finish rate leaderboard.")
    else:
        print(top3_df.to_string(index=False))


if __name__ == "__main__":
    main()
