import pandas as pd
import re
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from itertools import groupby
from operator import itemgetter
from keep_the_score_api_service import get_simplified_month_json
from cosmos_handler import get_month_document


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
    if "jarrett fre" in name:
        return "jarrett f"
    if "bartman" in name:
        return "brian p"
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
                    normalized_name = normalize_player_name(score_entry["name"])
                    all_flat_game_records.append((normalized_name, round_id, bar_name, points_scored))

    return all_flat_game_records

def rank_players_in_each_round(flat_game_records: List[Tuple[str, str, str, int]]) -> List[Dict[str, Any]]:
    """
    Given a combined list of flattened records, rank players per round and
    return a list of:
    {Player, RoundID, BarName, PercentileRank, Placement}
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
                "PercentileRank": percentile_rank,
                "Placement": placement_rank
            })

    return ranked_results


def build_percentile_leaderboard(
    flat_game_records: List[Tuple[str, str, str, int]],
    min_rounds_required: int = 8
) -> pd.DataFrame:
    """
    Rank and aggregate ranked results into a leaderboard sorted by average percentile rank.
    """
    ranked_results = rank_players_in_each_round(flat_game_records)

    player_aggregate_stats = defaultdict(lambda: {"TotalPercentile": 0, "RoundsPlayed": 0})

    for result in ranked_results:
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


def build_top_3_finish_rate_leaderboard(flat_game_records: List[Tuple[str, str, str, int]], min_rounds: int = 8) -> pd.DataFrame:
    """
    Rank and build a leaderboard showing percentage of times each player finishes in top 3.
    Only includes players with more than `min_rounds` rounds.
    """
    ranked_results = rank_players_in_each_round(flat_game_records)

    top3_counts = defaultdict(int)
    total_counts = defaultdict(int)

    for result in ranked_results:
        player = result["Player"]
        placement = result.get("Placement", None)
        total_counts[player] += 1
        if placement is not None and placement <= 3:
            top3_counts[player] += 1

    leaderboard_records = []
    for player, total in total_counts.items():
        if total <= min_rounds:
            continue  # Skip players with insufficient rounds

        top3 = top3_counts[player]
        rate = round((top3 / total) * 100, 2)
        leaderboard_records.append({
            "Player": player,
            "Top3Finishes": top3,
            "RoundsPlayed": total,
            "Top3RatePercent": rate
        })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    leaderboard_df.sort_values(by="Top3RatePercent", ascending=False, inplace=True)
    leaderboard_df.reset_index(drop=True, inplace=True)
    return leaderboard_df



def main():
    # Step 1: define which months (each month is a list of tokens and bar names)

    # Step 2: fetch each month's JSON (you could add more here)
    json_month_1 = get_month_document("202506") #this one is legacy allways stays there
    json_month_2 = get_month_document("202507")
    

    # Step 3: flatten once
    all_flat_records = flatten_all_months_to_tuples([json_month_1, json_month_2])

    # Step 4: build and print percentile leaderboard (ranking inside)
    percentile_leaderboard = build_percentile_leaderboard(all_flat_records)
    print("\n🏆 Cumulative Leaderboard (sorted by average percentile rank):\n")
    print(percentile_leaderboard.to_string(index=False))

    # Step 5: build and print top 3 finish rate leaderboard (ranking inside)
    top3_leaderboard = build_top_3_finish_rate_leaderboard(all_flat_records)
    print("\n🥇 Leaderboard by Top 3 Finish Percentage:\n")
    print(top3_leaderboard.to_string(index=False))


if __name__ == "__main__":
    main()
