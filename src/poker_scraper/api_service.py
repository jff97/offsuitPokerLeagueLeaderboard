from . import data_service
from . import persistence
from . import analytics
from . import name_tools

from poker_scraper.config import config

def check_and_log_flagged_player_names():
    """Check for name clashes in player data and save as warnings."""
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
    """Refresh the rounds database with latest data from API and legacy CSV."""
    all_rounds = data_service.get_this_months_rounds_for_bars(config.BAR_CONFIGS)  
    persistence.store_rounds(all_rounds)
    check_and_log_flagged_player_names()  # Check for name clashes after data 

def refresh_legacy_rounds():
    all_rounds = data_service.get_june_data_as_rounds()
    persistence.store_rounds(all_rounds)

def get_percentile_leaderboard_from_rounds():
    """Generate percentile-based leaderboard from stored rounds."""
    stored_rounds = persistence.get_all_rounds()
    print("stored rounds length = " + str(len(stored_rounds)))
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds)
    return percentile_leaderboard

def get_percentile_leaderboard_from_rounds_no_round_limit():
    """Generate percentile-based leaderboard with no minimum round requirement."""
    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds, 1)
    return percentile_leaderboard

def get_roi_leaderboard_from_rounds():
    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds)
    return roi_leaderboard

def get_trueskill_leaderboard_from_rounds():
    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_trueskill_leaderboard(stored_rounds)
    return  roi_leaderboard

def get_placement_leaderboard_from_rounds():
    """Generate placement-based leaderboard from stored rounds."""
    stored_rounds = persistence.get_all_rounds()
    top3_leaderboard = analytics.build_top_3_finish_rate_leaderboard(stored_rounds)
    return top3_leaderboard
