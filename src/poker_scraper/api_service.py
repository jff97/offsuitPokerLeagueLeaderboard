import textwrap
from . import data_service
from . import persistence  
from . import analytics
from . import name_tools
from poker_scraper.config import config



def _debug_print_rounds(rounds):
    """DEBUG: Print first 10 rounds stored in database. REMOVE THIS FUNCTION WHEN DONE DEBUGGING."""
    import json  # TODO: Remove this import and function when debugging is complete
    print(f"\nDEBUG: Total {len(rounds)} rounds stored")
    print("DEBUG: First 10 rounds:")
    for i, round_obj in enumerate(rounds[:100]):
        print(f"\n  Round {i+1}:")
        print(json.dumps(round_obj.to_dict(), indent=4))
    print("DEBUG: End of rounds\n")

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
    persistence.delete_all_round_data()
    all_rounds = data_service.get_rounds_for_bars(config.BAR_CONFIGS, include_legacy=True)  # Gets both API and legacy data
    persistence.store_rounds(all_rounds)
    check_and_log_flagged_player_names()  # Check for name clashes after data refresh
    #_debug_print_rounds(all_rounds)  # DEBUG: Pretty print first 10 rounds

def get_percentile_leaderboard_from_rounds():
    """Generate percentile-based leaderboard from stored rounds."""
    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds)
    return percentile_leaderboard.to_string(index=False)

def get_percentile_leaderboard_from_rounds_no_round_limit():
    """Generate percentile-based leaderboard with no minimum round requirement."""
    stored_rounds = persistence.get_all_rounds()
    percentile_leaderboard = analytics.build_percentile_leaderboard(stored_rounds, 1)
    return percentile_leaderboard.to_string(index=False)

def get_roi_leaderboard_from_rounds():
    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_roi_leaderboard(stored_rounds)
    return roi_leaderboard.to_string(index=False)

def get_trueskill_leaderboard_from_rounds():
    trueskill_info = textwrap.dedent("""
        Why We Use TrueSkill™ for Rankings

        - 🎮 Used by Xbox Live for popular games like Halo, Call of Duty, Gears of War, Forza, Overwatch, Team Fortress 2, and CS:GO.
        - ♟️ Adapted by chess, Go, and board game leagues to track true skill.
        - 🏆 Ranks players by considering not just wins, but the skill level of the opponents you face.
        - 🔄 Adjusts your ranking after every game.

        Note: Your TrueSkill score is a **relative skill estimate**, not a point total or winning percentage. Higher means stronger player, but it’s not a direct measure of any one stat.
    """)


    stored_rounds = persistence.get_all_rounds()
    roi_leaderboard = analytics.build_trueskill_leaderboard(stored_rounds)
    return trueskill_info + "\n\n" + roi_leaderboard.to_string(index=False)



def get_placement_leaderboard_from_rounds():
    """Generate placement-based leaderboard from stored rounds."""
    stored_rounds = persistence.get_all_rounds()
    top3_leaderboard = analytics.build_top_3_finish_rate_leaderboard(stored_rounds)
    return top3_leaderboard.to_string(index=False)
