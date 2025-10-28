
from offsuit_analyzer import persistence, analytics
from offsuit_analyzer.config import config

def get_players_outlasted_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    players_outlasted_leaderboard = analytics.build_players_outlasted_leaderboard(stored_rounds, min_rounds_required)
    return players_outlasted_leaderboard

def get_roi_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds, min_rounds_required)
    return roi_leaderboard

def get_trueskill_leaderboard():
    stored_rounds = persistence.get_all_rounds()
    trueskill_leaderboard = analytics.build_trueskill_leaderboard(stored_rounds)
    return trueskill_leaderboard

def get_first_place_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER
    
    stored_rounds = persistence.get_all_rounds()
    first_place_leaderboard = analytics.build_1st_place_win_leaderboard(stored_rounds, min_rounds_required)
    return first_place_leaderboard

def get_itm_percentage_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    itm_percentage_leaderboard = analytics.build_itm_percent_leaderboard(stored_rounds, min_rounds_required, config.PERCENT_FOR_ITM)
    return itm_percentage_leaderboard

def get_network_graph_image(searched_player_name: str = None):
    """
    Generate a player network graph visualization.
    Returns BytesIO buffer containing the image.
    """
    stored_rounds = persistence.get_all_rounds()
    return analytics.generate_graph_image_buffer(stored_rounds, searched_player_name, "Player Network - TrueSkill Colored")

def get_community_disconnectedness_analysis():
    stored_rounds = persistence.get_all_rounds()
    return analytics.get_community_avg_disconnectedness_df(stored_rounds)
