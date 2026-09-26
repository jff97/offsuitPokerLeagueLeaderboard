from datetime import date
from typing import List

from offsuit_analyzer import persistence
from offsuit_analyzer.config import config
from offsuit_analyzer.datamodel import BoardWipeEvent, Round

CLEARED_BAR_FRACTION_THRESHOLD = 0.8
MINIMUM_DAYS_BETWEEN_WIPES = 17  # shortest a season ever runs, so a closer "wipe" is the same one re-detected


def record_board_wipe_events(this_months_rounds: List[Round]) -> bool:
    """Detect a season-ending board wipe from freshly fetched rounds and record it.

    Board-wipe events are permanent history: once recorded they are never
    recalculated or removed automatically. Returns True if a wipe was recorded.
    """
    if not _is_board_wipe(this_months_rounds):
        return False

    if _wipe_recently_recorded():
        return False

    persistence.record_board_wipe_events([BoardWipeEvent(board_wipe_date=date.today())])
    return True


def _wipe_recently_recorded() -> bool:
    """Boards can stay empty for days after a wipe, so don't register the same wipe twice."""
    board_wipe_dates = get_all_board_wipe_dates()
    if not board_wipe_dates:
        return False

    days_since_last_wipe = (date.today() - max(board_wipe_dates)).days
    return days_since_last_wipe < MINIMUM_DAYS_BETWEEN_WIPES


def _is_board_wipe(this_months_rounds: List[Round]) -> bool:
    """A board wipe is when most configured bars come back with no rounds on this fetch."""
    total_bar_count = len(config.BAR_CONFIGS)
    if total_bar_count == 0:
        return False

    cleared_bar_count = _count_cleared_bars(this_months_rounds, total_bar_count)
    return (cleared_bar_count / total_bar_count) >= CLEARED_BAR_FRACTION_THRESHOLD


def _count_cleared_bars(this_months_rounds: List[Round], total_bar_count: int) -> int:
    """Count configured bars that have zero rounds on the freshly fetched boards."""
    bars_with_rounds = {round_obj.bar_id for round_obj in this_months_rounds}
    return total_bar_count - len(bars_with_rounds)


def get_all_board_wipe_dates() -> List[date]:
    """Return every recorded board-wipe date."""
    return [board_wipe_event.board_wipe_date for board_wipe_event in persistence.get_all_board_wipe_events()]
