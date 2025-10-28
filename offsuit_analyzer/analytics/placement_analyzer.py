import pandas as pd
from collections import defaultdict
from typing import List
from offsuit_analyzer.datamodel import Round


def _calculate_players_outlasted(placement: int, total_players: int) -> float:
    """
    Convert a placement into a percentage of players outlasted.
    100 means outlasted everyone (1st place), 0 means outlasted no one (last place).
    """
    if total_players <= 1:
        return 100.0
    return round((1 - (placement - 1) / (total_players - 1)) * 100, 2)


def build_players_outlasted_leaderboard(rounds: List[Round], min_rounds_required: int) -> pd.DataFrame:
    """
    Calculate each player's average percentage of players outlasted across all rounds.
    100% means always outlasting everyone (1st place), 0% means never outlasting anyone (last place)
    """
    player_stats = defaultdict(lambda: {"TotalOutlasted": 0, "RoundsPlayed": 0})

    for round_obj in rounds:
        # Sort players by points to determine placements
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        total_players = len(sorted_players)
        
        for placement, player in enumerate(sorted_players, 1):
            outlasted = _calculate_players_outlasted(placement, total_players)
            player_stats[player.player_name]["TotalOutlasted"] += outlasted
            player_stats[player.player_name]["RoundsPlayed"] += 1

    leaderboard_records = []

    for player_name, stats in player_stats.items():
        if stats["RoundsPlayed"] >= min_rounds_required:
            avg_outlasted = round(stats["TotalOutlasted"] / stats["RoundsPlayed"], 2)
            leaderboard_records.append({
                "Player": player_name,
                "Players Outlasted": avg_outlasted,  # Store as number
                "Rounds Played": stats["RoundsPlayed"]
            })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    if not leaderboard_df.empty:
        leaderboard_df.sort_values("Players Outlasted", ascending=False, inplace=True)
        leaderboard_df.reset_index(drop=True, inplace=True)
        # Format as percentage after sorting
        leaderboard_df["Players Outlasted"] = leaderboard_df["Players Outlasted"].apply(lambda x: f"{x:.2f}%")
    return leaderboard_df


def build_itm_percent_leaderboard(rounds: List[Round], min_rounds: int, percent_for_itm: float) -> pd.DataFrame:
    """
    Build a leaderboard showing percentage of times each player finishes in top X percentile.
    Only includes players with more than `min_rounds` played.
    
    Args:
        rounds: List of Round objects
        min_rounds: Minimum rounds required to be included in leaderboard
        percent_for_itm: The percentile threshold (e.g., 20.0 for top 20%)
    """
    stats = defaultdict(lambda: {"rounds": 0, "itm_finishes": 0})
    
    for round_obj in rounds:
        # Sort players by points to determine placements
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        total_players = len(sorted_players)
        
        for placement, player in enumerate(sorted_players, 1):
            stats[player.player_name]["rounds"] += 1
            outlasted = _calculate_players_outlasted(placement, total_players)
            if outlasted >= (100 - percent_for_itm):
                stats[player.player_name]["itm_finishes"] += 1

    leaderboard_records = []
    for player, player_stats in stats.items():
        if player_stats["rounds"] >= min_rounds:
            itm_rate = round((player_stats["itm_finishes"] / player_stats["rounds"]) * 100, 2)
            leaderboard_records.append({
                "Player": player,
                "ITM %": itm_rate,  # Store as number
                "ITM Finishes": player_stats["itm_finishes"],
                "Rounds Played": player_stats["rounds"]
            })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    if not leaderboard_df.empty:
        leaderboard_df.sort_values("ITM %", ascending=False, inplace=True)
        leaderboard_df.reset_index(drop=True, inplace=True)
        # Format as percentage after sorting
        leaderboard_df["ITM %"] = leaderboard_df["ITM %"].apply(lambda x: f"{x:.2f}%")
    return leaderboard_df
