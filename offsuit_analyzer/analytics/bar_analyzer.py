"""Bar analyzer - calculates average number of players per bar and other bar statistics."""
import pandas as pd
from collections import defaultdict
from typing import List
from offsuit_analyzer.datamodel import Round


def _is_legacy_bar(bar_name: str) -> bool:
    """
    Filter function to check if a bar name contains 'legacy'.
    
    Args:
        bar_name: Name of the bar to check
    
    Returns:
        True if the bar name contains 'legacy' (case-insensitive), False otherwise
    """
    return "legacy" in bar_name.lower()


def build_bar_average_players_leaderboard(rounds: List[Round], min_rounds_required: int = 4) -> pd.DataFrame:
    """
    Build a leaderboard showing average number of players for each bar.
    
    Filters bars to only include those with:
    - More than min_rounds_required rounds
    - Names that do not contain 'legacy'
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of rounds required for a bar to be included (default: 4, must have > this many)
    
    Returns:
        DataFrame with bar names, average players, and rounds played, sorted by average players descending
    """
    bar_stats = defaultdict(lambda: {"player_counts": [], "rounds": 0})
    
    # Collect player counts for each bar
    for round_obj in rounds:
        bar_name = round_obj.bar_name
        player_count = len(round_obj.players)
        
        bar_stats[bar_name]["player_counts"].append(player_count)
        bar_stats[bar_name]["rounds"] += 1
    
    records = []
    for bar_name, stats in bar_stats.items():
        rounds_played = stats["rounds"]
        
        # Apply filters
        if rounds_played > min_rounds_required and not _is_legacy_bar(bar_name):
            avg_players = round(sum(stats["player_counts"]) / rounds_played, 2)
            records.append({
                "Bar": bar_name,
                "Avg Players": avg_players,
                "Rounds Played": rounds_played
            })
    
    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values("Avg Players", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    return df
