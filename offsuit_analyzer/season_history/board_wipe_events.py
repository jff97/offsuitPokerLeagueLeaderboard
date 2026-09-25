from typing import Iterable, List

from offsuit_analyzer import persistence
from offsuit_analyzer.datamodel import Round


def get_observed_board_wipe_dates(all_rounds: Iterable[Round]) -> List[str]:
    return sorted({round_obj.round_date for round_obj in all_rounds if round_obj.round_date})


def get_board_wipe_dates_to_record(current_rounds: Iterable[Round]) -> List[str]:
    current_board_wipe_dates = get_observed_board_wipe_dates(current_rounds)
    stored_board_wipe_dates = {
        board_wipe_event.board_wipe_date.isoformat()
        for board_wipe_event in persistence.get_all_board_wipe_events()
    }
    stored_round_dates = persistence.get_all_round_dates()

    return sorted(set(current_board_wipe_dates) | stored_board_wipe_dates | set(stored_round_dates))
