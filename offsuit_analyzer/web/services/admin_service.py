from datetime import date
from offsuit_analyzer import data_service
from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel.poker_season import LeagueSeasonCalendar
from offsuit_analyzer.data_service import league_seasons
from .name_tools_service import check_and_log_clashing_player_names

def refresh_rounds_database():
    """Refresh the rounds database with latest data from this months Keep the score API"""
    all_rounds = data_service.get_this_months_rounds_for_bars()  
    persistence.store_rounds(all_rounds)

def refresh_legacy_rounds():
    """Refresh with legacy June data."""
    all_rounds = data_service.get_june_data_as_rounds()
    persistence.store_rounds(all_rounds)

def email_json_rounds_to_admin():
    persistence.email_json_rounds_backup()

def email_bar_list_to_admin():
    """Email bar list report to admin."""
    data_service.email_bar_list_report()

def run_name_clash_detection():
    """Manually run name clash detection."""
    check_and_log_clashing_player_names()


def get_season_calendar(year: int) -> LeagueSeasonCalendar | None:
    """
    Retrieve the season calendar for the specified year.
    """
    return league_seasons.get_calendar_year_seasons(year)

def upsert_season_calendar(data: dict):
    """
    Create or update a season calendar for a given year.
    Expects data = {'year': 2025, 'months': {...}}.
    Performs upsert — no duplicates or orphaned calendars.
    """
    year = data.get('year')
    # Build calendar object from dict
    calendar = LeagueSeasonCalendar.from_dict(data)
    league_seasons.save_calendar_year_league_seasons(data, year, calendar)