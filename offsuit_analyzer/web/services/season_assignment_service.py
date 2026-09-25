"""Compatibility wrappers for season-history business logic."""
from datetime import date
from typing import Iterable, List, Union

from offsuit_analyzer import season_history
from offsuit_analyzer.datamodel import SeasonWindow

DEFAULT_BOUNDARY_WEEKDAY = season_history.DEFAULT_BOUNDARY_WEEKDAY


def assign_season_windows_from_history(boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY) -> List[SeasonWindow]:
    return season_history.assign_season_windows_from_history(boundary_weekday=boundary_weekday)


def calculate_season_windows(
    board_wipe_dates: Iterable[Union[str, date]],
    boundary_weekday: int = DEFAULT_BOUNDARY_WEEKDAY,
) -> List[SeasonWindow]:
    return season_history.calculate_season_windows(board_wipe_dates, boundary_weekday=boundary_weekday)
