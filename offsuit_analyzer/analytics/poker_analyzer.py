import pandas as pd
from collections import defaultdict
from typing import List, Dict, Any
from offsuit_analyzer.datamodel import Round


def _calculate_percentile_rank(placement: int, total_players: int) -> float:
    """
    Convert a placement into a percentile rank.
    100 means 1st place, 0 means last place.
    """
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)


def _rank_players_in_each_round(rounds: List[Round]) -> List[Dict[str, Any]]:

    ranked_results = []

    for round_obj in rounds:
        # Sort players by points descending
        players_sorted_by_points = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        
        total_players_in_round = len(players_sorted_by_points)
        point_to_placement_map = {}

        for index, player in enumerate(players_sorted_by_points):
            if player.points not in point_to_placement_map:
                point_to_placement_map[player.points] = index + 1

        for player in players_sorted_by_points:
            placement_rank = point_to_placement_map[player.points]
            percentile_rank = _calculate_percentile_rank(placement_rank, total_players_in_round)

            ranked_results.append({
                "Player": player.player_name,
                "RoundID": round_obj.round_id,
                "BarName": round_obj.bar_name,
                "PercentileRank": percentile_rank,
                "Placement": placement_rank
            })

    return ranked_results

def _sort_dataframe_by_percentage_column(df: pd.DataFrame, percentage_column: str) -> pd.DataFrame:
    """
    Helper function to sort a DataFrame by a column containing percentage strings.
    Creates a temporary numeric column for sorting, then removes it.
    """
    if df.empty:
        return df
    
    df["_sort"] = df[percentage_column].str.rstrip('%').astype(float)
    df.sort_values(by="_sort", ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.drop(columns=["_sort"], inplace=True)
    return df

def build_percentile_leaderboard(rounds: List[Round], min_rounds_required: int) -> pd.DataFrame:
    """
    Rank and aggregate ranked results into a leaderboard sorted by average percentile rank.
    """
    ranked_results = _rank_players_in_each_round(rounds)

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
                "Avg Players Outlasted": f"{average_percentile:.2f}%",
                "Rounds Played": stats["RoundsPlayed"]
            })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    if leaderboard_df.empty:
        leaderboard_df = pd.DataFrame([["No players met the minimum round requirement"]], columns=["Message"])
    else:
        leaderboard_df = _sort_dataframe_by_percentage_column(leaderboard_df, "Avg Players Outlasted")

    return leaderboard_df

def build_1st_place_win_leaderboard(rounds: List[Round], min_rounds_required: int) -> pd.DataFrame:
    """
    Rank and build a leaderboard showing percentage of times each player finishes in 1st place.
    """
    # Calculate column headers once
    win_rate_col = "Win Rate"
    first_place_col = "Wins"
    rounds_played_col = "Rounds Played"
    
    ranked_results = _rank_players_in_each_round(rounds)

    first_place_counts = defaultdict(int)
    total_counts = defaultdict(int)

    for result in ranked_results:
        player = result["Player"]
        placement = result.get("Placement", None)
        total_counts[player] += 1
        if placement is not None and placement == 1:
            first_place_counts[player] += 1

    leaderboard_records = []
    for player, total in total_counts.items():
        if total < min_rounds_required:
            continue  # Skip players with insufficient rounds
            
        first_place = first_place_counts[player]
        rate = round((first_place / total) * 100, 2) if total > 0 else 0
        leaderboard_records.append({
            "Player": player,
            win_rate_col: f"{rate:.2f}%",
            first_place_col: first_place,
            rounds_played_col: total
        })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    if leaderboard_df.empty:
        leaderboard_df = pd.DataFrame([["No players found"]], columns=["Message"])
    else:
        leaderboard_df = _sort_dataframe_by_percentage_column(leaderboard_df, win_rate_col)

    return leaderboard_df

def build_itm_percent_leaderboard(rounds: List[Round], min_rounds: int, percent_for_itm: float) -> pd.DataFrame:
    """
    Rank and build a leaderboard showing percentage of times each player finishes in top X percentile.
    Only includes players with more than `min_rounds` played.
    
    Args:
        rounds: List of Round objects
        min_rounds: Minimum rounds required to be included in leaderboard
        percent_for_itm: The percentile threshold (e.g., 20.0 for top 20%)
    """
    # Calculate column headers once
    top_finishes_col = f"ITM Finishes"
    rounds_played_col = "Rounds Played"
    rate_col = f"ITM %"
    
    ranked_results = _rank_players_in_each_round(rounds)

    top_percentile_counts = defaultdict(int)
    total_counts = defaultdict(int)

    for result in ranked_results:
        player = result["Player"]
        percentile_rank = result.get("PercentileRank", None)
        total_counts[player] += 1
        if percentile_rank is not None and percentile_rank >= (100 - percent_for_itm):
            top_percentile_counts[player] += 1

    leaderboard_records = []
    for player, total in total_counts.items():
        if total < min_rounds:
            continue  # Skip players with insufficient rounds

        top_percentile_finishes = top_percentile_counts[player]
        rate = round((top_percentile_finishes / total) * 100, 2)
        leaderboard_records.append({
            "Player": player,
            rate_col: f"{rate:.2f}%",
            top_finishes_col: top_percentile_finishes,
            rounds_played_col: total
            
        })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    leaderboard_df = _sort_dataframe_by_percentage_column(leaderboard_df, rate_col)
    return leaderboard_df
    return leaderboard_df
