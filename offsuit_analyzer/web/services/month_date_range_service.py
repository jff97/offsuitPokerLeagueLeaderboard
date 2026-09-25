"""Determine and persist current month season date ranges from incoming API rounds."""
from datetime import datetime
from typing import List, Optional, Tuple
import pytz

from offsuit_analyzer.config import config
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer.datamodel.month_date_range import MonthDateRange
from offsuit_analyzer.persistence import month_date_ranges_collection


def determine_round_date_bounds(rounds: List[Round]) -> Optional[Tuple[str, str]]:
    """Return the earliest and latest round_date values found in rounds.

    Input:
        rounds: API rounds for the currently visible season

    Output:
        (start_date, end_date) as YYYY-MM-DD strings, or None when no valid dates exist
    """
    round_dates: List[str] = [round_obj.round_date for round_obj in rounds if round_obj.round_date]

    if not round_dates:
        return None

    start_date: str = min(round_dates)
    end_date: str = max(round_dates)
    return start_date, end_date


def build_current_month_date_range(rounds: List[Round]) -> Optional[MonthDateRange]:
    """Build the current month date range from the incoming current-season rounds.

    Input:
        rounds: API rounds for the current month refresh cycle

    Output:
        MonthDateRange keyed by the current YYYYMM value, or None when no dates exist
    """
    date_bounds = determine_round_date_bounds(rounds)
    if date_bounds is None:
        return None

    start_date, end_date = date_bounds
    return MonthDateRange(
        month_key=_get_current_month_key(),
        start_date=start_date,
        end_date=end_date,
    )


def merge_month_date_ranges(
    existing_month_date_range: Optional[MonthDateRange],
    observed_month_date_range: MonthDateRange
) -> MonthDateRange:
    """Merge an observed range into the stored current-month range.

    Input:
        existing_month_date_range: previously stored value for the same YYYYMM key
        observed_month_date_range: current value derived from fresh API rounds

    Output:
        A MonthDateRange whose start only moves earlier and whose end only moves later
    """
    if existing_month_date_range is None:
        return observed_month_date_range

    if existing_month_date_range.month_key != observed_month_date_range.month_key:
        raise ValueError(
            "Cannot merge month date ranges with different month keys: "
            f"{existing_month_date_range.month_key} != {observed_month_date_range.month_key}"
        )

    return MonthDateRange(
        month_key=observed_month_date_range.month_key,
        start_date=min(existing_month_date_range.start_date, observed_month_date_range.start_date),
        end_date=max(existing_month_date_range.end_date, observed_month_date_range.end_date),
    )


def update_current_month_date_range(rounds: List[Round]) -> Optional[MonthDateRange]:
    """Persist the current month date range using the latest incoming API rounds.

    Input:
        rounds: API rounds currently visible for the current month

    Output:
        The saved MonthDateRange, or None when there are no dated rounds to store
    """
    observed_month_date_range = build_current_month_date_range(rounds)
    if observed_month_date_range is None:
        return None

    existing_month_date_range = month_date_ranges_collection.get_month_date_range(
        observed_month_date_range.month_key
    )
    merged_month_date_range = merge_month_date_ranges(
        existing_month_date_range,
        observed_month_date_range,
    )
    month_date_ranges_collection.save_month_date_range(merged_month_date_range)
    return merged_month_date_range


def _get_current_month_key() -> int:
    """Return the current season key as YYYYMM in the configured poker timezone."""
    poker_timezone = pytz.timezone(config.POKER_TIMEZONE)
    current_time = datetime.now(poker_timezone)
    return int(current_time.strftime("%Y%m"))
