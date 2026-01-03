
from datetime import datetime, date
import pandas as pd
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer.data_service import league_seasons


def _get_top_point_players_for_date_range(stored_rounds: List[Round], start_date: date, end_date: date):
    """Get top point players within a date range."""
    # Convert dates to strings for comparison (round_date is already YYYY-MM-DD)
    start_str = start_date.strftime("%Y-%m-%d")
    end_str = end_date.strftime("%Y-%m-%d")
    
    # Filter rounds by date range
    filtered_rounds = [rnd for rnd in stored_rounds if start_str <= rnd.round_date <= end_str]
    
    # Accumulate points by player
    player_points = {}
    for rnd in filtered_rounds:
        for player in rnd.players:
            player_points[player.player_name] = player_points.get(player.player_name, 0) + player.points

    df = pd.DataFrame({
        "player": list(player_points.keys()),
        "points": list(player_points.values()),
    })
    
    return df.sort_values("points", ascending=False).reset_index(drop=True)


def get_top_point_players_for_month(stored_rounds: List[Round], month: int, year: int):
    start_date, end_date = league_seasons.get_date_range_for_month(year, month)
    return _get_top_point_players_for_date_range(stored_rounds, start_date, end_date)



def get_top_point_players_for_year(stored_rounds: List[Round], year: int):
    years_start_date = datetime(year, 1, 1).date()
    years_end_date = datetime(year, 12, 31).date()
    return _get_top_point_players_for_date_range(stored_rounds, years_start_date, years_end_date)




