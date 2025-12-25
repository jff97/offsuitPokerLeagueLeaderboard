from datetime import date
from offsuit_analyzer import data_service
from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel.poker_season import LeagueSeasonCalendar
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
    if not isinstance(year, int):
        raise ValueError("Year must be an integer")
    
    calendar = persistence.get_calendar(year)
    return calendar  # can be None if not created yet

def upsert_season_calendar(data: dict):
    """
    Create or update a season calendar for a given year.
    Expects data = {'year': 2025, 'months': {...}}.
    Performs upsert — no duplicates or orphaned calendars.
    """
    year = data.get('year')
    # Build calendar object from dict
    calendar = LeagueSeasonCalendar.from_dict(data)
    _validate_calendar_data(data)

    # Upsert in DB (replace existing if present)
    persistence.upsert_calendar(calendar, year)

def _validate_calendar_data(data: dict):
    months = data.get('months')
    if not months or not isinstance(months, dict):
        raise ValueError("Months must be provided as a dictionary")

    for month, month_data in months.items():
        start = month_data.get('start_date')
        end = month_data.get('end_date')

        # Skip months that are empty
        if not start and not end:
            continue
        if not start or not end:
            raise ValueError(f"Month '{month}' must have both start_date and end_date if any date is provided")

        try:
            start_dt = date.fromisoformat(start)
            end_dt = date.fromisoformat(end)
        except ValueError:
            raise ValueError(f"Month '{month}' dates must be in YYYY-MM-DD format")

        if start_dt > end_dt:
            raise ValueError(f"Month '{month}' start_date ({start}) must be on or before end_date ({end})")

    # Check for overlaps after all individual month validations
    _check_month_overlaps(months)


def _check_month_overlaps(months: dict):
    month_ranges = []
    for month, month_data in months.items():
        start = month_data.get("start_date")
        end = month_data.get("end_date")

        # Skip months that are empty
        if not start or not end:
            continue

        start_dt = date.fromisoformat(start)
        end_dt = date.fromisoformat(end)
        for existing_start, existing_end, existing_name in month_ranges:
            # Overlap occurs if start < existing_end and end > existing_start
            # Allow touching: start == existing_end or end == existing_start is OK
            if start_dt < existing_end and end_dt > existing_start:
                raise ValueError(
                    f"Month '{month}' ({start_dt} to {end_dt}) overlaps with "
                    f"month '{existing_name}' ({existing_start} to {existing_end})"
                )
        month_ranges.append((start_dt, end_dt, month))
