from typing import Iterable, List, Optional

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel import Round


def get_observed_board_wipe_dates(all_rounds: Iterable[Round]) -> List[str]:
    return sorted({round_obj.round_date for round_obj in all_rounds if round_obj.round_date})


def get_board_wipe_dates_to_record(
    current_rounds: Iterable[Round],
    stored_round_dates: Optional[Iterable[str]] = None,
) -> List[str]:
    current_board_wipe_dates = get_observed_board_wipe_dates(current_rounds)
    stored_board_wipe_dates = {
        board_wipe_event.board_wipe_date.isoformat()
        for board_wipe_event in persistence.get_all_board_wipe_events()
    }
    if stored_board_wipe_dates:
        return sorted(set(current_board_wipe_dates) | stored_board_wipe_dates)

    historical_round_dates = stored_round_dates if stored_round_dates is not None else persistence.get_all_round_dates()
    return sorted(set(current_board_wipe_dates) | set(historical_round_dates))
