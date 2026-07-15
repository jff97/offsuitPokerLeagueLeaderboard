"""Bar analyzer - calculates average number of players per bar and other bar statistics."""
import pandas as pd
from collections import defaultdict
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer.analytics import trueskill_analyzer
from offsuit_analyzer.config import config


def _is_legacy_bar(bar_name: str) -> bool:
    """
    Filter function to check if a bar name contains 'legacy'.
    
    Args:
        bar_name: Name of the bar to check
    
    Returns:
        True if the bar name contains 'legacy' (case-insensitive), False otherwise
    """
    return "legacy" in bar_name.lower()


def _get_qualifying_bars(rounds: List[Round], min_rounds_required: int) -> dict:
    """
    Group rounds by bar name and filter to qualifying bars.
    
    A bar qualifies if:
    - It has more than min_rounds_required rounds
    - Its name does not contain 'legacy'
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of rounds required for a bar
    
    Returns:
        Dictionary mapping bar names to lists of their qualifying Round objects
    """
    # Group rounds by bar
    bar_rounds = defaultdict(list)
    for round_obj in rounds:
        bar_rounds[round_obj.bar_name].append(round_obj)
    
    # Filter bars by minimum rounds and legacy status
    qualifying_bars = {}
    for bar_name, bar_round_list in bar_rounds.items():
        if len(bar_round_list) > min_rounds_required and not _is_legacy_bar(bar_name):
            qualifying_bars[bar_name] = bar_round_list
    
    return qualifying_bars


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
    qualifying_bars = _get_qualifying_bars(rounds, min_rounds_required)
    
    records = []
    for bar_name, bar_round_list in qualifying_bars.items():
        player_counts = [len(round_obj.players) for round_obj in bar_round_list]
        rounds_played = len(bar_round_list)
        avg_players = round(sum(player_counts) / rounds_played, 2)
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

def _get_player_trueskill_map(rounds: List[Round]) -> dict:
    """
    Get a mapping of player names to their current trueskill raw scores (mu).
    
    Uses raw score (mu) instead of conservative score to avoid penalizing bars with new players
    who have high uncertainty (sigma).
    
    Scrapes the trueskill scores from the existing trueskill leaderboard calculation.
    
    Args:
        rounds: List of Round objects
    
    Returns:
        Dictionary mapping player names to their trueskill raw scores (mu)
    """
    # Get the existing trueskill leaderboard (already calculated)
    trueskill_df = trueskill_analyzer.build_trueskill_leaderboard(rounds)
    
    # Build map from player name to raw score (mu)
    player_trueskill_map = {}
    for _, row in trueskill_df.iterrows():
        player_trueskill_map[row['Name']] = row['Raw Ranking']
    
    return player_trueskill_map


def build_bar_average_trueskill_leaderboard(rounds: List[Round], min_rounds_required: int = 4) -> pd.DataFrame:
    """
    Build a leaderboard showing average trueskill score for each bar.
    
    Calculates the average trueskill rating across all player appearances at each bar.
    Each player appearance counts separately - if a player shows up 3 times, all 3 trueskill scores are included.
    
    Filters bars to only include those with:
    - More than min_rounds_required rounds
    - Names that do not contain 'legacy'
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of rounds required for a bar to be included (default: 4, must have > this many)
    
    Returns:
        DataFrame with bar names, average trueskill score, and rounds played, sorted by average trueskill descending
    """
    qualifying_bars = _get_qualifying_bars(rounds, min_rounds_required)
    player_trueskill_map = _get_player_trueskill_map(rounds)
    
    records = []
    for bar_name, bar_round_list in qualifying_bars.items():
        trueskill_scores = []
        
        # Collect all trueskill scores for every player appearance at this bar
        for round_obj in bar_round_list:
            for player in round_obj.players:
                if player.player_name in player_trueskill_map:
                    trueskill_scores.append(player_trueskill_map[player.player_name])
        
        # Calculate average if we have scores
        if trueskill_scores:
            avg_trueskill = round(sum(trueskill_scores) / len(trueskill_scores), 2)
            rounds_played = len(bar_round_list)
            records.append({
                "Bar": bar_name,
                "Avg TrueSkill": avg_trueskill,
                "Rounds Played": rounds_played
            })
    
    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values("Avg TrueSkill", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    
    return df