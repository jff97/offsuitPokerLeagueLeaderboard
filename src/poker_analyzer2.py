import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict, Any
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

    100 means top player (1st place),
    0 means last place,
    linearly scaled in between.
    """
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)


def flatten_game_data_to_tuples(raw_json_data: Dict[str, Any]) -> List[tuple]:
    """
    Convert nested service response into a flat list of tuples:
    (player_name, round_id, bar_name, points_scored)
    """
    flat_game_records = []

    for bar_token, bar_details in raw_json_data["bars"].items():
        bar_name = bar_details["bar_name"]

        for round_info in bar_details["rounds"]:
            round_id = round_info["round_id"]

            for score_entry in round_info["scores"]:
                normalized_name = normalize_player_name(score_entry["name"])
                points_scored = score_entry["points"]
                flat_game_records.append((normalized_name, round_id, bar_name, points_scored))

    return flat_game_records


def rank_players_in_each_round(flat_game_records: List[tuple]) -> List[Dict[str, Any]]:
    """
    Takes flat records and returns a list of dicts with:
    {Player, RoundID, BarName, PercentileRank}
    """
    ranked_results = []

    # Sort list so groupby works properly
    flat_game_records.sort(key=itemgetter(1))  # sort by round_id

    for round_id, entries_for_round in groupby(flat_game_records, key=itemgetter(1)):
        players_in_round = list(entries_for_round)
        players_sorted_by_points = sorted(players_in_round, key=lambda x: x[3], reverse=True)

        total_players_in_round = len(players_sorted_by_points)
        point_to_placement_map = {}

        # Assign placement ranks with ties having the same rank
        for index, (player_name, _, _, player_points) in enumerate(players_sorted_by_points):
            if player_points not in point_to_placement_map:
                point_to_placement_map[player_points] = index + 1  # rank starts at 1

        # Calculate percentile ranks for each player
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
    Only include players with at least `min_rounds_required` rounds played.
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


def run_leaderboard_from_service_json(service_json: Dict[str, Any]) -> pd.DataFrame:
    """
    Orchestrates the leaderboard generation:
    1. Flatten JSON to tuples
    2. Rank players per round
    3. Aggregate into percentile leaderboard
    """
    flat_records = flatten_game_data_to_tuples(service_json)
    ranked_results = rank_players_in_each_round(flat_records)
    leaderboard = build_percentile_leaderboard(ranked_results)

    print("\n🏆 Cumulative Leaderboard (sorted by average percentile rank):\n")
    print(leaderboard.to_string(index=False))

    return leaderboard


def main():
    tokens_and_names = [
        ("pcynjwvnvgqme", "Hosed on Brady"),
        ("qdtgqhtjkrtpe", "Alibi"),
    ]
    # Replace this with your actual JSON object (Python dict)
    service_json_data_for_one_month = get_simplified_month_json(tokens_and_names)

    if not service_json_data_for_one_month:
        print("No data provided.")
        return

    run_leaderboard_from_service_json(service_json_data_for_one_month)


if __name__ == "__main__":
    main()
