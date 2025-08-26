from functools import lru_cache
from offsuit_analyzer import persistence
from offsuit_analyzer import analytics
from offsuit_analyzer.config import config
from offsuit_analyzer.analytics.skill_island_visualization import generate_rounds_image_buffer
import io

def get_percentile_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds, min_rounds_required)
    return percentile_leaderboard

def get_roi_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds, min_rounds_required)
    return roi_leaderboard

@lru_cache(maxsize=1)
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

def clear_leaderboard_caches():
    """Clear all leaderboard caches when data is updated."""
    get_trueskill_leaderboard.cache_clear()

def hydrate_leaderboard_caches():
    """Pre-load all leaderboard caches for fast response times."""
    get_trueskill_leaderboard()

def get_network_graph_image(searched_player_name: str = None):
    """
    Generate a player network graph visualization.
    Returns BytesIO buffer containing the image.
    """
    stored_rounds = persistence.get_all_rounds()
    return generate_rounds_image_buffer(stored_rounds, searched_player_name, "Player Network - TrueSkill Colored")
