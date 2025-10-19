from offsuit_analyzer import data_service
from offsuit_analyzer import persistence
from .name_tools_service import check_and_log_clashing_player_names
from .leaderboard_service import clear_leaderboard_caches, hydrate_leaderboard_caches

def refresh_rounds_database():
    """Refresh the rounds database with latest data from this months Keep the score API"""
    all_rounds = data_service.get_this_months_rounds_for_bars()  
    persistence.store_rounds(all_rounds)

def refresh_legacy_rounds():
    """Refresh with legacy June data."""
    all_rounds = data_service.get_june_data_as_rounds()
    persistence.store_rounds(all_rounds)

def email_json_rounds_to_admin():
    persistence.email_json_backup()

def refresh_leaderboard_caches():
    """Manually refresh leaderboard caches."""
    clear_leaderboard_caches()
    hydrate_leaderboard_caches()

def run_name_clash_detection():
    """Manually run name clash detection."""
    check_and_log_clashing_player_names()

