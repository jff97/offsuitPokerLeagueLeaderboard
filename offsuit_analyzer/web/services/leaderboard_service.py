
import pandas as pd
from offsuit_analyzer import persistence, analytics
from offsuit_analyzer.config import config

def get_players_outlasted_leaderboard() -> pd.DataFrame:
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    players_outlasted_leaderboard = analytics.build_players_outlasted_leaderboard(stored_rounds, min_rounds_required)
    return players_outlasted_leaderboard

def get_roi_leaderboard() -> pd.DataFrame:
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds, min_rounds_required)
    return roi_leaderboard

def get_trueskill_leaderboard() -> pd.DataFrame:
    stored_rounds = persistence.get_all_rounds()
    trueskill_leaderboard = analytics.build_trueskill_leaderboard(stored_rounds)
    return trueskill_leaderboard

def get_average_opponent_skill_leaderboard() -> pd.DataFrame:
    """Get leaderboard showing average opponent skill faced by each player."""
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER
    
    stored_rounds = persistence.get_all_rounds()
    avg_opponent_skill_leaderboard = analytics.build_average_opponent_skill_leaderboard(stored_rounds, min_rounds_required)
    return avg_opponent_skill_leaderboard

def get_first_place_leaderboard() -> pd.DataFrame:
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER
    
    stored_rounds = persistence.get_all_rounds()
    first_place_leaderboard = analytics.build_1st_place_win_leaderboard(stored_rounds, min_rounds_required)
    return first_place_leaderboard

def get_itm_percentage_leaderboard() -> pd.DataFrame:
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    itm_percentage_leaderboard = analytics.build_itm_percent_leaderboard(stored_rounds, min_rounds_required, config.PERCENT_FOR_ITM)
    return itm_percentage_leaderboard

# DISABLED: Player graph visualization removed for deployment size optimization
# def get_network_graph_image(searched_player_name: str = None):
#     """
#     Generate a player network graph visualization.
#     Returns BytesIO buffer containing the image.
#     """
#     stored_rounds = persistence.get_all_rounds()
#     return analytics.generate_graph_image_buffer(stored_rounds, searched_player_name, "Player Network - TrueSkill Colored")

# DISABLED: Community detection removed for deployment size optimization
# def get_community_disconnectedness_analysis():
#     stored_rounds = persistence.get_all_rounds()
#     return analytics.get_community_avg_disconnectedness_df(stored_rounds)

def get_placement_distributions() -> list:
    """
    Get KDE distribution curves for all players' placement patterns.
    Returns list of player distribution data.
    """
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    placement_distributions = analytics.build_placement_distribution_for_all_players(stored_rounds, min_rounds_required)
    return placement_distributions

def get_this_months_top_point_players() -> pd.DataFrame:
    return analytics.get_this_months_top_point_players()

def get_years_top_point_players(year: int) -> pd.DataFrame:
    stored_rounds = persistence.get_all_rounds()
    return analytics.get_top_point_players_for_year(stored_rounds, year)

def get_average_game_size_by_player() -> pd.DataFrame:
    """
    Get the average number of players in games for each unique player.
    
    Returns:
        DataFrame with player names and their average game size
    """
    min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER
    
    stored_rounds = persistence.get_all_rounds()
    return analytics.build_average_game_size_by_player(stored_rounds, min_rounds_required)

def get_bar_average_players_leaderboard() -> pd.DataFrame:
    """
    Get the average number of players for each bar.
    Filters to bars with more than the configured minimum rounds and excludes bars with 'legacy' in the name.
    
    Returns:
        DataFrame with bar names, average players, and rounds played
    """
    min_rounds_required = config.MINIMUM_ROUNDS_FOR_BAR_ANALYSIS
    
    stored_rounds = persistence.get_all_rounds()
    return analytics.build_bar_average_players_leaderboard(stored_rounds, min_rounds_required)
