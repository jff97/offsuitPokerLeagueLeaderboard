"""Rebuild season windows from stored event-date history."""
from datetime import date, timedelta
from typing import Dict, Iterable, List, Union

from offsuit_analyzer.datamodel import EventDate, SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_season_month
from offsuit_analyzer.persistence import event_dates_collection, season_windows_collection

DEFAULT_BOUNDARY_WEEKDAY = 5  # Saturday


def assign_season_windows_from_history(boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY) -> List[SeasonWindow]:
    """Read full event-date history, rebuild season windows, and persist them."""
    event_dates = [event_date.event_date for event_date in event_dates_collection.get_all_event_dates()]
    season_windows = calculate_season_windows(event_dates, boundary_weekday=boundary_weekday)
    season_windows_collection.save_season_windows(season_windows)
    return season_windows


def calculate_season_windows(
    event_dates: Iterable[Union[str, date]],
    boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY,
) -> List[SeasonWindow]:
    """Group observed dates into season windows by snapping to boundary-week poker weeks."""
    normalized_event_dates = sorted({EventDate(event_date=event_date).event_date for event_date in event_dates})
    if not normalized_event_dates:
        return []

    season_bounds: Dict[int, Dict[str, date]] = {}
    for event_date in normalized_event_dates:
        week_start = _get_week_start(event_date, boundary_weekday)
        week_end = week_start + timedelta(days=6)
        season_month = derive_season_month(week_start, week_end)
        if season_month not in season_bounds:
            season_bounds[season_month] = {"start_date": week_start, "end_date": week_end}
            continue

        season_bounds[season_month]["start_date"] = min(season_bounds[season_month]["start_date"], week_start)
        season_bounds[season_month]["end_date"] = max(season_bounds[season_month]["end_date"], week_end)

    return [
        SeasonWindow(
            season_month=season_month,
            start_date=bounds["start_date"],
            end_date=bounds["end_date"],
        )
        for season_month, bounds in sorted(season_bounds.items())
    ]


def _get_week_start(event_date: date, boundary_weekday: int) -> date:
    days_back = (event_date.weekday() - boundary_weekday) % 7
    return event_date - timedelta(days=days_back)
