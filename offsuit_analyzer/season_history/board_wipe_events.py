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
    historical_round_dates = set(stored_round_dates) if stored_round_dates is not None else set(persistence.get_all_round_dates())
    if stored_board_wipe_dates:
        earliest_recorded_board_wipe = min(stored_board_wipe_dates)
        legacy_board_wipe_dates = {round_date for round_date in historical_round_dates if round_date < earliest_recorded_board_wipe}
        return sorted(set(current_board_wipe_dates) | stored_board_wipe_dates | legacy_board_wipe_dates)

    return sorted(set(current_board_wipe_dates) | historical_round_dates)
