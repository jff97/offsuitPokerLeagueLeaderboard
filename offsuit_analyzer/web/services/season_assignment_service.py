"""Season-history service wrappers."""
from typing import List

from offsuit_analyzer import season_history
from offsuit_analyzer.datamodel import Round

def refresh_board_wipe_events_and_season_windows(this_months_rounds: List[Round]) -> None:
    """Detect a season-ending board wipe from freshly fetched rounds, then rebuild season windows if one occurred."""
    new_wipe_detected = season_history.record_board_wipe_events(this_months_rounds)
    if new_wipe_detected:
        season_history.assign_season_windows_from_history()
