from poker_data_transformer import get_list_of_rounds_from_api

from cosmos_handler import store_rounds, delete_all_round_data, get_all_logs, delete_all_logs, get_all_rounds, delete_all_warnings, save_warnings, get_all_warnings

from poker_analyzer import build_percentile_leaderboard, build_top_3_finish_rate_leaderboard
from script_to_migrate_legacy_csv import get_june_data_as_rounds
from poker_datamodel import Round
import name_tools

from typing import List

tokens_and_names = [
        ("jykjlbzxzkqye", "Cork N Barrel"),
        ("xpwtrdfsvdtce", "Chatters"),
        ("czyvrxfdrjbye", "Mavricks"),
        ("qdtgqhtjkrtpe", "Alibi"),
        ("vvkcftdnvdvge", "Layton Heights"),
        ("tbyyvqmpjsvke", "Tinys"),
        ("pcynjwvnvgqme", "Hosed on Brady"),
        ("jkhwxjkpxycle", "Witts End"),
        ("khptcxdgnpnbe", "Lakeside"),
        ("zyqphgqxppcde", "Brickyard Pub"),
        ("ybmwcqckckdhe", "South Bound Again"),
        ("pwtmrylcjnjye", "Anticipation Sunday"),
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
    new_api_rounds = get_list_of_rounds_from_api(tokens_and_names)
    store_rounds(new_api_rounds)
    refresh_june_legacy_csv_rounds()
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

def _compare_rounds(new_rounds: List[Round], old_rounds: List[Round]):
    set_new = set(new_rounds)
    set_old = set(old_rounds)
    print(f"New rounds count: {len(set(new_rounds))}, Old rounds count: {len(set(old_rounds))}")

    only_in_new = set_new - set_old
    only_in_old = set_old - set_new

    if not only_in_new and not only_in_old:
        print("✅ SUCCESS: Both round lists match exactly!")
    else:
        print("❌ MISMATCH FOUND:")
        if only_in_new:
            print(f"\nRounds only in NEW method ({len(only_in_new)}):")
            for round_obj in sorted(only_in_new):
                print(f"  {round_obj}")
        if only_in_old:
            print(f"\nRounds only in OLD method ({len(only_in_old)}):")
            for round_obj in sorted(only_in_old):
                print(f"  {round_obj}")


def refresh_june_legacy_csv_rounds():
    """Import and store legacy June CSV data as rounds."""
    legacy_rounds = get_june_data_as_rounds()
    store_rounds(legacy_rounds)
