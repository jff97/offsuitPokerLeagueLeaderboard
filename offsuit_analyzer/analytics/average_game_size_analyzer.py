"""Average game size analyzer - calculates average number of players per game for each player."""
from typing import List, Dict
import pandas as pd
from collections import defaultdict
from offsuit_analyzer.datamodel.round import Round


def _calculate_average_game_sizes(rounds: List[Round], min_rounds_required: int = 0) -> Dict[str, Dict]:
    """
    Calculate the average game size for each player, filtering by minimum rounds played.
    
    For each player, tracks all games they played, calculates the average number of players
    in those games, and includes the round count.
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of rounds required to include a player (default: 0)
    
    Returns:
        Dictionary mapping player names to dict with 'avg_size' and 'rounds_played'
    """
    player_game_sizes = defaultdict(list)
    
    for round_obj in rounds:
        game_size = len(round_obj.players)
        for player in round_obj.players:
            player_game_sizes[player.player_name].append(game_size)
    
    # Calculate averages and filter by minimum rounds
    result = {}
    for player_name, sizes in player_game_sizes.items():
        rounds_played = len(sizes)
        if rounds_played >= min_rounds_required:
            avg_size = round(sum(sizes) / rounds_played, 2)
            result[player_name] = {
                'avg_size': avg_size,
                'rounds_played': rounds_played
            }
    
    return result


def build_average_game_size_by_player(rounds: List[Round], min_rounds_required: int = 0) -> pd.DataFrame:
    """
    Calculate the average number of players in games for each unique player.
    
    For each player, determines the average size (total number of players)
    of all games they participated in.
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of rounds required to be included in leaderboard
    
    Returns:
        DataFrame with columns for player name, average game size, and rounds played
    """
    player_stats = _calculate_average_game_sizes(rounds, min_rounds_required)
    
    leaderboard_records = []
    for player_name, stats in player_stats.items():
        leaderboard_records.append({
            "Player": player_name,
            "Average Game Size": stats['avg_size'],
            "Rounds Played": stats['rounds_played']
        })
    
    leaderboard_df = pd.DataFrame(leaderboard_records)
    if not leaderboard_df.empty:
        leaderboard_df.sort_values("Average Game Size", ascending=False, inplace=True)
        leaderboard_df.reset_index(drop=True, inplace=True)
    
    return leaderboard_df

