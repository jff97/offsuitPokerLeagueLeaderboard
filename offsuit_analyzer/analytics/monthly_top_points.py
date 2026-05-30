
from datetime import datetime, date
import pandas as pd
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer import data_service


def _rank_players_by_points(rounds: List[Round]) -> pd.DataFrame:
    """Rank players by their total points across rounds.
    
    Args:
        rounds: List of Round objects to aggregate points from
        
    Returns:
        DataFrame with 'player' and 'points' columns, sorted by points descending
    """
    player_points = {}
    for rnd in rounds:
        for player in rnd.players:
            player_points[player.player_name] = player_points.get(player.player_name, 0) + player.points

    df = pd.DataFrame({
        "player": list(player_points.keys()),
        "points": list(player_points.values()),
    })
    
    return df.sort_values("points", ascending=False).reset_index(drop=True)


def _get_top_point_players_for_date_range(stored_rounds: List[Round], start_date: date, end_date: date) -> pd.DataFrame:
    """Get top point players within a date range.
    
    Args:
        stored_rounds: All rounds to filter from
        start_date: Start of date range (inclusive)
        end_date: End of date range (inclusive)
        
    Returns:
        DataFrame with top players for the date range
    """
    # Convert dates to strings for comparison (round_date is already YYYY-MM-DD)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Filter rounds by date range
    filtered_rounds = [rnd for rnd in stored_rounds if start_str <= rnd.round_date <= end_str]
    
    # Build and return sorted dataframe from filtered rounds
    return _rank_players_by_points(filtered_rounds)


def get_this_months_top_point_players() -> pd.DataFrame:
    """Get top point players for the current month.
    
    Returns rounds currently visible in the API (current month only).
    The API auto-wipes when a new season starts.
    
    Returns:
        DataFrame with top players for the current month
    """
    # Get current visible rounds from API (already filtered to this month by the API)
    this_months_rounds = data_service.get_this_months_rounds_for_bars()
    
    # Build and return sorted dataframe from current month's rounds
    return _rank_players_by_points(this_months_rounds)



def get_top_point_players_for_year(stored_rounds: List[Round], year: int) -> pd.DataFrame:
    """Get top point players for a specific year.
    
    Args:
        stored_rounds: All rounds to filter from
        year: The year to get top players for
        
    Returns:
        DataFrame with top players for the year
    """
    years_start_date = datetime(year, 1, 1).date()
    years_end_date = datetime(year, 12, 31).date()
    return _get_top_point_players_for_date_range(stored_rounds, years_start_date, years_end_date)




