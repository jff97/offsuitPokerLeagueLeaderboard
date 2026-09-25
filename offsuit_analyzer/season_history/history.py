"""Business logic for season-history persistence and season-window rebuilding."""
from datetime import date, timedelta
from typing import Dict, Iterable, List, Tuple, Union

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel import EventDate, Round, SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_year_month

DEFAULT_BOUNDARY_WEEKDAY = 5  # Saturday


def assign_season_windows_from_history(boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY) -> List[SeasonWindow]:
    """Read full event-date history, rebuild season windows, and persist them."""
    event_dates = [event_date.event_date for event_date in persistence.get_all_event_dates()]
    season_windows = calculate_season_windows(event_dates, boundary_weekday=boundary_weekday)
    persistence.save_season_windows(season_windows)
    return season_windows


def calculate_season_windows(
    event_dates: Iterable[Union[str, date]],
    boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY,
) -> List[SeasonWindow]:
    """Group observed dates into season windows by snapping to boundary-week poker weeks."""
    normalized_event_dates = sorted({EventDate(event_date=event_date).event_date for event_date in event_dates})
    if not normalized_event_dates:
        return []

    season_bounds: Dict[Tuple[int, int], Dict[str, date]] = {}
    for event_date in normalized_event_dates:
        week_start = _get_week_start(event_date, boundary_weekday)
        week_end = week_start + timedelta(days=6)
        year_month = derive_year_month(week_start, week_end)
        if year_month not in season_bounds:
            season_bounds[year_month] = {"start_date": week_start, "end_date": week_end}
            continue

        season_bounds[year_month]["start_date"] = min(season_bounds[year_month]["start_date"], week_start)
        season_bounds[year_month]["end_date"] = max(season_bounds[year_month]["end_date"], week_end)

    return [
        SeasonWindow(
            year=year,
            month=month,
            start_date=bounds["start_date"],
            end_date=bounds["end_date"],
        )
        for (year, month), bounds in sorted(season_bounds.items())
    ]


def get_observed_event_dates(all_rounds: Iterable[Round]) -> List[str]:
    return sorted({round_obj.round_date for round_obj in all_rounds if round_obj.round_date})


def get_event_dates_to_record(current_rounds: Iterable[Round]) -> List[str]:
    current_event_dates = get_observed_event_dates(current_rounds)
    stored_event_dates = {event_date.event_date.isoformat() for event_date in persistence.get_all_event_dates()}
    stored_round_dates = persistence.get_all_round_dates()

    if set(stored_round_dates).issubset(stored_event_dates):
        return current_event_dates

    return sorted(set(current_event_dates) | set(stored_round_dates))


def _get_week_start(event_date: date, boundary_weekday: int) -> date:
    days_back = (event_date.weekday() - boundary_weekday) % 7
    return event_date - timedelta(days=days_back)
