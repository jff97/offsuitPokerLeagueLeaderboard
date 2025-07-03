import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from itertools import groupby
from operator import itemgetter
from keep_the_score_api_service import get_simplified_month_json


def normalize_player_name(raw_name: str) -> str:
    """Clean and standardize player names."""
    name = str(raw_name).strip().lower()
    name = re.sub(r'\s+', ' ', name)
    name = re.sub(r'[^a-z0-9 ]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return fix_special_name_cases(name)


def fix_special_name_cases(name: str) -> str:
    """Apply specific corrections for known name inconsistencies."""
    if "pyerre" in name:
        return "pyerre l"
    if "bonnie" in name:
        return "bonnie l"
    return name


def calculate_percentile_rank(placement: int, total_players: int) -> float:
    """
    Convert a placement into a percentile rank.
    100 means 1st place, 0 means last place.
    """
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)


def flatten_all_months_to_tuples(month_jsons: List[Dict[str, Any]]) -> List[Tuple[str, str, str, int]]:
    """
    Convert multiple nested JSON month responses into a combined flat list:
    (player_name, round_id, bar_name, points_scored)
    """
    all_flat_game_records = []

    for raw_json_data in month_jsons:
        for bar_token, bar_details in raw_json_data["bars"].items():
            bar_name = bar_details["bar_name"]

            for round_info in bar_details["rounds"]:
                round_id = round_info["round_id"]

                for score_entry in round_info["scores"]:
                    normalized_name = normalize_player_name(score_entry["name"])
                    points_scored = score_entry["points"]
                    all_flat_game_records.append((normalized_name, round_id, bar_name, points_scored))

    return all_flat_game_records


def rank_players_in_each_round(flat_game_records: List[Tuple[str, str, str, int]]) -> List[Dict[str, Any]]:
    """
    Given a combined list of flattened records, rank players per round and
    return a list of:
    {Player, RoundID, BarName, PercentileRank}
    """
    ranked_results = []

    flat_game_records.sort(key=itemgetter(1))  # sort by round_id

    for round_id, entries_for_round in groupby(flat_game_records, key=itemgetter(1)):
        players_in_round = list(entries_for_round)
        players_sorted_by_points = sorted(players_in_round, key=lambda x: x[3], reverse=True)

        total_players_in_round = len(players_sorted_by_points)
        point_to_placement_map = {}

        for index, (player_name, _, _, player_points) in enumerate(players_sorted_by_points):
            if player_points not in point_to_placement_map:
                point_to_placement_map[player_points] = index + 1

        for player_name, _, bar_name, player_points in players_sorted_by_points:
            placement_rank = point_to_placement_map[player_points]
            percentile_rank = calculate_percentile_rank(placement_rank, total_players_in_round)

            ranked_results.append({
                "Player": player_name,
                "RoundID": round_id,
                "BarName": bar_name,
                "PercentileRank": percentile_rank
            })

    return ranked_results


def build_percentile_leaderboard(
    ranked_player_results: List[Dict[str, Any]],
    min_rounds_required: int = 1
) -> pd.DataFrame:
    """
    Aggregate ranked results into a leaderboard sorted by average percentile rank.
    """
    player_aggregate_stats = defaultdict(lambda: {"TotalPercentile": 0, "RoundsPlayed": 0})

    for result in ranked_player_results:
        player_name = result["Player"]
        player_aggregate_stats[player_name]["TotalPercentile"] += result["PercentileRank"]
        player_aggregate_stats[player_name]["RoundsPlayed"] += 1

    leaderboard_records = []

    for player_name, stats in player_aggregate_stats.items():
        if stats["RoundsPlayed"] >= min_rounds_required:
            average_percentile = round(stats["TotalPercentile"] / stats["RoundsPlayed"], 2)
            leaderboard_records.append({
                "Player": player_name,
                "RoundsPlayed": stats["RoundsPlayed"],
                "AveragePercentileRank": average_percentile
            })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    leaderboard_df.sort_values(by="AveragePercentileRank", ascending=False, inplace=True)
    leaderboard_df.reset_index(drop=True, inplace=True)

    return leaderboard_df


def get_percentile_leaderboard_from_month_json_list(month_json_list: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Orchestrate full leaderboard from multiple month JSON objects.
    """
    all_flat_records = flatten_all_months_to_tuples(month_json_list)
    all_ranked_results = rank_players_in_each_round(all_flat_records)
    leaderboard = build_percentile_leaderboard(all_ranked_results)

    return leaderboard


def main():
    # Step 1: define which months (each month is a list of tokens and bar names)
    month_1 = [("pcynjwvnvgqme", "Hosed on Brady"), ("qdtgqhtjkrtpe", "Alibi")]
    
    # Step 2: fetch each month's JSON (you could add more here)
    json_month_1 = get_simplified_month_json(month_1)
    json_month_2 = {
    "_id": "202506",
    "month": "2025-06",
    "bars": {
        "hbrz1234bar": {
            "bar_name": "Old Town Pub",
            "rounds": [
                {
                    "date": "Wed, 12 Jun 2025 20:00:00 GMT",
                    "round_id": "5338888",
                    "scores": [
                        {"name": "Troy R", "player_id": "50311379", "points": 38},
                        {"name": "John F", "player_id": "50838511", "points": 32},
                        {"name": "Bonnie L", "player_id": "55075343", "points": 28},
                        {"name": "Sean G", "player_id": "52682799", "points": 20},
                        {"name": "Cindy R", "player_id": "50319129", "points": 16},
                        {"name": "Joe G", "player_id": "53919576", "points": 12}
                    ]
                }
            ]
        },
        "bkgx5678bar": {
            "bar_name": "The Daily Draw",
            "rounds": [
                {
                    "date": "Thu, 20 Jun 2025 19:00:00 GMT",
                    "round_id": "5339999",
                    "scores": [
                        {"name": "Will G", "player_id": "53926243", "points": 40},
                        {"name": "Greg S", "player_id": "52353907", "points": 35},
                        {"name": "Ahmad B", "player_id": "51920113", "points": 26},
                        {"name": "Nico A", "player_id": "50711851", "points": 21},
                        {"name": "Miguel Q", "player_id": "51973743", "points": 18},
                        {"name": "Amar", "player_id": "50625303", "points": 15},
                        {"name": "Mike M", "player_id": "41741662", "points": 12}
                    ]
                }
            ]
        }
    }
}


    # Step 3: run leaderboard across all selected months
    leaderboard = get_percentile_leaderboard_from_month_json_list([
        json_month_1,
        json_month_2
    ])
    print("\n🏆 Cumulative Leaderboard (sorted by average percentile rank):\n")
    print(leaderboard.to_string(index=False))


if __name__ == "__main__":
    main()
