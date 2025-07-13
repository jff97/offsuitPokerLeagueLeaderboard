from poker_data_service import get_rounds_for_bars, BarConfig

from data_persistence import store_rounds, delete_all_round_data, get_all_logs, delete_all_logs, get_all_rounds, delete_all_warnings, save_warnings, get_all_warnings

from poker_analytics import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from poker_datamodel import Round
import name_tools

from typing import List

# Bar configurations with clean, readable format
bar_configs = [
    BarConfig("jykjlbzxzkqye", 2),  # Wednesday
    BarConfig("xpwtrdfsvdtce", 3),  # Thursday
    BarConfig("czyvrxfdrjbye", 3),  # Thursday
    BarConfig("qdtgqhtjkrtpe", 1),  # Tuesday
    BarConfig("vvkcftdnvdvge", 2),  # Wednesday
    BarConfig("tbyyvqmpjsvke", 5),  # Saturday
    BarConfig("pcynjwvnvgqme", 0),  # Monday
    BarConfig("jkhwxjkpxycle", 3),  # Thursday
    BarConfig("khptcxdgnpnbe", 0),  # Monday
    BarConfig("zyqphgqxppcde", 6),  # Sunday
    BarConfig("ybmwcqckckdhe", 2),  # Wednesday
    BarConfig("pwtmrylcjnjye", 6),  # Sunday
]

def check_and_log_flagged_player_names():
    """Check for name clashes in player data and save as warnings."""
    rounds = get_all_rounds()
    name_clashes = name_tools.detect_name_clashes(rounds)
    delete_all_warnings()
    if name_clashes:
        save_warnings(name_clashes)


def delete_logs():
    """Delete all log entries from the database."""
    delete_all_logs()

def get_all_logs_to_display_for_api() -> str:
    """Retrieve all logs formatted for HTML display."""
    list_of_all_log_strings = get_all_logs()
    combined_logs = "\n".join(list_of_all_log_strings)
    html_ready = combined_logs.replace("\n", "<br>")
    return html_ready

def delete_warnings():
    """Delete all warning entries from the database."""
    delete_all_warnings()

def get_all_warnings_to_display_for_api() -> str:
    """Retrieve all warnings formatted for HTML display."""
    list_of_all_warning_strings = get_all_warnings()
    combined_warnings = "\n".join(list_of_all_warning_strings)
    html_ready = combined_warnings.replace("\n", "<br>")
    return html_ready

def refresh_rounds_database():
    """Refresh the rounds database with latest data from API and legacy CSV."""
    delete_all_round_data()
    all_rounds = get_rounds_for_bars(bar_configs, include_legacy=True)  # Gets both API and legacy data
    store_rounds(all_rounds)
    check_and_log_flagged_player_names()  # Check for name clashes after data refresh

def get_percentile_leaderboard_from_rounds():
    """Generate percentile-based leaderboard from stored rounds."""
    stored_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(stored_rounds)
    return percentile_leaderboard.to_string(index=False)

def get_percentile_leaderboard_from_rounds_no_round_limit():
    """Generate percentile-based leaderboard with no minimum round requirement."""
    stored_rounds = get_all_rounds()
    percentile_leaderboard = build_percentile_leaderboard(stored_rounds, 1)
    return percentile_leaderboard.to_string(index=False)

def get_placement_leaderboard_from_rounds():
    """Generate placement-based leaderboard from stored rounds."""
    stored_rounds = get_all_rounds()
    top3_leaderboard = build_top_3_finish_rate_leaderboard(stored_rounds)
    return top3_leaderboard.to_string(index=False)
