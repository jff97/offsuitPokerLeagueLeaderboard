"""Business logic for season-window rebuilding from board-wipe history."""
from datetime import date, timedelta
from typing import Dict, Iterable, List, Union

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel import BoardWipeEvent, SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_season_month

DEFAULT_BOUNDARY_WEEKDAY = 5  # Saturday


def assign_season_windows_from_history(boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY) -> List[SeasonWindow]:
    """Read full board-wipe history, rebuild season windows, and persist them."""
    board_wipe_dates = [
        board_wipe_event.board_wipe_date
        for board_wipe_event in persistence.get_all_board_wipe_events()
    ]
    season_windows = calculate_season_windows(board_wipe_dates, boundary_weekday=boundary_weekday)
    persistence.save_season_windows(season_windows)
    return season_windows


def calculate_season_windows(
    board_wipe_dates: Iterable[Union[str, date]],
    boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY,
) -> List[SeasonWindow]:
    """Group observed dates into season windows by snapping to boundary-week poker weeks."""
    normalized_board_wipe_dates = sorted(
        {BoardWipeEvent(board_wipe_date=board_wipe_date).board_wipe_date for board_wipe_date in board_wipe_dates}
    )
    if not normalized_board_wipe_dates:
        return []

    season_bounds: Dict[int, Dict[str, date]] = {}
    for board_wipe_date in normalized_board_wipe_dates:
        week_start = _get_week_start(board_wipe_date, boundary_weekday)
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


def _get_week_start(board_wipe_date: date, boundary_weekday: int) -> date:
    days_back = (board_wipe_date.weekday() - boundary_weekday) % 7
    return board_wipe_date - timedelta(days=days_back)
