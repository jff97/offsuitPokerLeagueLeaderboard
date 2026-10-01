"""Season-history service wrappers."""
import threading
from typing import List

from offsuit_analyzer import season_history, logging_service
from offsuit_analyzer.season_history import gold_names_service
from offsuit_analyzer.datamodel import Round

def refresh_board_wipe_events_and_season_windows(this_months_rounds: List[Round]) -> None:
    """Detect a season-ending board wipe from freshly fetched rounds, then rebuild season windows if one occurred."""
    new_wipe_detected = season_history.record_board_wipe_events(this_months_rounds)
    if new_wipe_detected: 
        season_history.assign_season_windows_from_history()
        threading.Thread(target=_set_gold_names_and_log_failures, daemon=True).start()


def _set_gold_names_and_log_failures() -> None:
    """Run gold-name sync off the request thread; log on failure since exceptions here never reach Flask's error handler."""
    try:
        gold_names_service.set_gold_names_on_keep_the_score()
    except Exception as e:
        logging_service.log_critical(f"Background gold-name sync failed: {e}")
