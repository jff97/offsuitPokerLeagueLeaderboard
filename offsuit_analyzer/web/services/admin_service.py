from offsuit_analyzer import data_service
from offsuit_analyzer import persistence
from .name_tools_service import check_and_log_clashing_player_names
from .leaderboard_service import clear_leaderboard_caches, hydrate_leaderboard_caches

def refresh_rounds_database():
    """Refresh the rounds database with latest data from this months Keep the score API"""
    all_rounds = data_service.get_this_months_rounds_for_bars()  
    persistence.store_rounds(all_rounds)
    _trigger_post_data_update_tasks()

def refresh_legacy_rounds():
    """Refresh with legacy June data."""
    all_rounds = data_service.get_june_data_as_rounds()
    persistence.store_rounds(all_rounds)
    _trigger_post_data_update_tasks()

def email_json_rounds_to_admin():
    persistence.email_json_backup

def _trigger_post_data_update_tasks():
    """Tasks to run after new rounds are entered."""
    # Check for name clashes after data update
    check_and_log_clashing_player_names()

    # Clear leaderboard caching because leaderboards only change when rounds get updated
    clear_leaderboard_caches()
    
    # Pre-load cached functions so they are lightning fast for all users 
    hydrate_leaderboard_caches()
