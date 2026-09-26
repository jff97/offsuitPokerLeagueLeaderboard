"""Business logic for season-window rebuilding from board-wipe history."""
from datetime import date, timedelta
from typing import List

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel import SeasonWindow
from offsuit_analyzer.datamodel.season_window import derive_year_month
from . import board_wipe_events

DEFAULT_BOUNDARY_WEEKDAY = 5  # Saturday


def assign_season_windows_from_history() -> None:
    """Read full board-wipe history, rebuild season windows, and persist them."""
    board_wipe_dates = board_wipe_events.get_all_board_wipe_dates()
    season_windows = _calculate_season_windows(board_wipe_dates)
    persistence.save_season_windows(season_windows)


def _calculate_season_windows(board_wipe_dates: List[date]) -> List[SeasonWindow]:
    """Build one window per closed season: the span between two consecutive wipes.

    A wipe day is the first day of the new season (a new-season game is played that same
    night), so a season runs from its own wipe boundary up to the day before the next one.
    The still-open season since the most recent wipe has no known end yet, so it's excluded.
    """
    # set() guards against duplicate/adjacent boundaries in old or manually-edited wipe history.
    season_boundaries = sorted(
        {_get_week_start(board_wipe_date, DEFAULT_BOUNDARY_WEEKDAY) for board_wipe_date in board_wipe_dates}
    )

    season_windows: List[SeasonWindow] = []
    for this_boundary, next_boundary in zip(season_boundaries, season_boundaries[1:]):
        start_date = this_boundary
        end_date = next_boundary - timedelta(days=1)
        year, month = derive_year_month(start_date, end_date)
        season_windows.append(SeasonWindow(year=year, month=month, start_date=start_date, end_date=end_date))

    return season_windows


def _get_week_start(board_wipe_date: date, boundary_weekday: int) -> date:
    days_back = (board_wipe_date.weekday() - boundary_weekday) % 7
    return board_wipe_date - timedelta(days=days_back)

