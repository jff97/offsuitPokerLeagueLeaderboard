from functools import lru_cache
from offsuit_analyzer import persistence
from offsuit_analyzer import analytics
from offsuit_analyzer.config import config

@lru_cache(maxsize=4)
def get_percentile_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds, min_rounds_required)
    return percentile_leaderboard

@lru_cache(maxsize=4)
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

@lru_cache(maxsize=1)
def get_placement_leaderboard(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    placement_leaderboard = analytics.build_top_3_finish_rate_leaderboard(stored_rounds, min_rounds_required)
    return placement_leaderboard

def clear_leaderboard_caches():
    """Clear all leaderboard caches when data is updated."""
    get_percentile_leaderboard.cache_clear()
    get_roi_leaderboard.cache_clear()
    get_trueskill_leaderboard.cache_clear()
    get_placement_leaderboard.cache_clear()

def hydrate_leaderboard_caches():
    """Pre-load all leaderboard caches for fast response times."""
    get_percentile_leaderboard()
    get_roi_leaderboard()
    get_trueskill_leaderboard()
    get_placement_leaderboard()
