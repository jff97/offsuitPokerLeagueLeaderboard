import pandas as pd
from collections import defaultdict
from typing import List
from offsuit_analyzer.datamodel import Round


def build_1st_place_win_leaderboard(rounds: List[Round], min_rounds_required: int) -> pd.DataFrame:
    """
    Build leaderboard showing percentage of first place finishes for each player.
    """
    stats = defaultdict(lambda: {"rounds": 0, "wins": 0})
    
    for round_obj in rounds:
        # Sort players by points to determine winner
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        winner = sorted_players[0].player_name if sorted_players else None
        
        # Update stats for all players in the round
        for player in round_obj.players:
            stats[player.player_name]["rounds"] += 1
            if player.player_name == winner:
                stats[player.player_name]["wins"] += 1

    leaderboard_records = []
    for player, player_stats in stats.items():
        if player_stats["rounds"] >= min_rounds_required:
            win_rate = round((player_stats["wins"] / player_stats["rounds"]) * 100, 2)
            leaderboard_records.append({
                "Player": player,
                "Win Rate": win_rate,  # Store as number
                "Wins": player_stats["wins"],
                "Rounds Played": player_stats["rounds"]
            })

    leaderboard_df = pd.DataFrame(leaderboard_records)
    if not leaderboard_df.empty:
        leaderboard_df.sort_values("Win Rate", ascending=False, inplace=True)
        leaderboard_df.reset_index(drop=True, inplace=True)
        # Format as percentage after sorting
        leaderboard_df["Win Rate"] = leaderboard_df["Win Rate"].apply(lambda x: f"{x:.2f}%")
    return leaderboard_df