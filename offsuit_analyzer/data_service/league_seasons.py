#get date range 
from datetime import date

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel.poker_season import LeagueSeasonCalendar, MonthRange


def get_date_range_for_month(year: int, month: int) -> tuple[date | None, date | None]:
    # Mapping from month number to month name
    month_number_to_name = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December"
    }

    # Get the calendar for the given year
    calendar_obj: LeagueSeasonCalendar = persistence.get_calendar(year)
    if not calendar_obj:
        return None, None

    # Map numeric month to month name
    month_name = month_number_to_name.get(month)
    if not month_name:
        return None, None  # invalid month number

    # Lookup MonthRange by name
    month_range: MonthRange | None = calendar_obj.months.get(month_name)
    if not month_range:
        return None, None  # month not found in calendar

    return month_range.start_date, month_range.end_date
    

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

def save_calendar_year_league_seasons(data, year, calendar):
    _validate_calendar_data(data)

    # Upsert in DB (replace existing if present)
    persistence.upsert_calendar(calendar, year)

def get_calendar_year_seasons(year: int) -> LeagueSeasonCalendar | None:
    if not isinstance(year, int):
        raise ValueError("Year must be an integer")
    
    calendar = persistence.get_calendar(year)
    return calendar  # can be None if not created yet
