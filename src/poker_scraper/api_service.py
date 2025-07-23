from functools import lru_cache
from . import data_service
from . import persistence
from . import analytics
from . import name_tools 
from .config import config

def trigger_for_new_rounds_were_entered():
    # Check for name clashes after data update
    check_and_log_clashing_player_names()

    # we clear leaderboard caching because leaderboards only change when rounds get updated
    clear_all_lru_caches()
    
    #we call all the cached functions so they are lightning fast for all users 
    hydrate_cached_functions()

def check_and_log_clashing_player_names():
    name_tools.adaptive_name_problem_finder_process()
    
    rounds = persistence.get_all_rounds()
    name_clashes = name_tools.detect_name_clashes(rounds)
    persistence.delete_all_warnings()
    if name_clashes:
        persistence.save_warnings(name_clashes)

def delete_logs():
    """Delete all log entries from the database."""
    persistence.delete_all_logs()

def get_all_logs_to_display_for_api() -> str:
    """Retrieve all logs formatted for HTML display."""
    list_of_all_log_strings = persistence.get_all_logs()
    combined_logs = "\n".join(list_of_all_log_strings)
    html_ready = combined_logs.replace("\n", "<br>")
    return html_ready

def delete_warnings():
    """Delete all warning entries from the database."""
    persistence.delete_all_warnings()

def get_all_warnings_to_display_for_api() -> str:
    """Retrieve all warnings formatted for HTML display."""
    list_of_all_warning_strings = persistence.get_all_warnings()
    combined_warnings = "\n".join(list_of_all_warning_strings)
    html_ready = combined_warnings.replace("\n", "<br>")
    return html_ready

def refresh_rounds_database():
    """Refresh the rounds database with latest data from this months Keep the score API"""
    all_rounds = data_service.get_this_months_rounds_for_bars()  
    persistence.store_rounds(all_rounds)
    trigger_for_new_rounds_were_entered()

def refresh_legacy_rounds():
    all_rounds = data_service.get_june_data_as_rounds()
    persistence.store_rounds(all_rounds)
    trigger_for_new_rounds_were_entered()

@lru_cache(maxsize=4)
def get_percentile_leaderboard_from_rounds(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds, min_rounds_required)
    return percentile_leaderboard

@lru_cache(maxsize=4)
def get_roi_leaderboard_from_rounds(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds, min_rounds_required)
    return roi_leaderboard

@lru_cache(maxsize=1)
def get_trueskill_leaderboard_from_rounds():
    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_trueskill_leaderboard(stored_rounds)
    return  roi_leaderboard

@lru_cache(maxsize=1)
def get_placement_leaderboard_from_rounds(min_rounds_required: int = None):
    if min_rounds_required in (None, 0):
        min_rounds_required = config.MINIMUM_ROUNDS_TO_ANALYZE_PLAYER

    stored_rounds = persistence.get_all_rounds()
    top3_leaderboard = analytics.build_top_3_finish_rate_leaderboard(stored_rounds, min_rounds_required)
    return top3_leaderboard

def get_ambiguous_names():
    rounds = persistence.get_all_rounds()
    return name_tools.get_ambiguous_names_with_actions(rounds)

def get_all_name_clashes():
    return name_tools.get_all_name_problems_as_string()

def delete_all_name_clashes_temp():
    return name_tools.delete_all_name_clashes_temp_testing_method()

def hydrate_cached_functions():
    get_percentile_leaderboard_from_rounds()
    get_roi_leaderboard_from_rounds()
    get_trueskill_leaderboard_from_rounds()
    get_placement_leaderboard_from_rounds()

def clear_all_lru_caches():
    get_percentile_leaderboard_from_rounds.cache_clear()
    get_roi_leaderboard_from_rounds.cache_clear()
    get_trueskill_leaderboard_from_rounds.cache_clear()
    get_placement_leaderboard_from_rounds.cache_clear()
