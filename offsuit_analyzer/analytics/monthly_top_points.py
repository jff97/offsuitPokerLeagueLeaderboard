
from datetime import datetime
import pandas as pd
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer.data_service import league_seasons

def get_top_point_players_for_month(stored_rounds: List[Round], month: int, year: int):
    start_date, end_date = league_seasons.get_date_range_for_month(year, month)

    # Dictionary to accumulate points by player
    player_points = {}

    for rnd in stored_rounds:
        round_date = datetime.strptime(rnd.round_date, "%Y-%m-%d").date()
        if start_date <= round_date <= end_date:
            for player in rnd.players:
                player_points[player.player_name] = player_points.get(player.player_name, 0) + player.points

    # Convert dictionary to DataFrame with a single Month/Year column
    month_year_str = f"{month}-{year}"
    df = pd.DataFrame({
        "player": list(player_points.keys()),
        "points": list(player_points.values()),
        "month_year": [month_year_str] * len(player_points),
    })

    # Sort descending by points
    df = df.sort_values("points", ascending=False).reset_index(drop=True)

    return df

