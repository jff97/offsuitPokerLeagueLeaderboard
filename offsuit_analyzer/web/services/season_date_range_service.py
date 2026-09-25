"""Determine and persist current season date ranges from incoming API rounds."""
from datetime import date, datetime
from typing import List, Tuple

from offsuit_analyzer.datamodel import Round, SeasonDateRange
from offsuit_analyzer.persistence import season_date_ranges_collection


def update_current_season_date_range(rounds: List[Round]) -> bool:
    """Persist the current season date range using the latest incoming API rounds."""
    dated_round_days = _get_dated_round_days(rounds)
    if not dated_round_days:
        return False

    observed_season_date_range = _build_current_season_date_range(dated_round_days)
    saved_season_date_range = season_date_ranges_collection.get_season_date_range(
        observed_season_date_range.season_month
    )
    merged_season_date_range = observed_season_date_range
    if saved_season_date_range is not None:
        merged_season_date_range = _merge_season_date_ranges(
            saved_season_date_range,
            observed_season_date_range,
        )
    season_date_ranges_collection.save_season_date_range(merged_season_date_range)
    return True


def _current_season_has_dated_rounds(round_days: List[date]) -> bool:
    """Return True when at least one round has a usable date."""
    return len(round_days) > 0


def _determine_current_season_date_bounds(round_days: List[date]) -> Tuple[date, date]:
    """Return the earliest and latest round_date values found in rounds."""
    if not _current_season_has_dated_rounds(round_days):
        raise ValueError("Current season rounds do not contain any round_date values.")

    return min(round_days), max(round_days)


def _build_current_season_date_range(round_days: List[date]) -> SeasonDateRange:
    """Build the current season date range from the incoming current-season rounds."""
    start_date, end_date = _determine_current_season_date_bounds(round_days)
    return SeasonDateRange(
        start_date=start_date,
        end_date=end_date,
    )


def _merge_season_date_ranges(
    stored_season_date_range: SeasonDateRange,
    observed_season_date_range: SeasonDateRange
) -> SeasonDateRange:
    """Merge a stored season range with the newly observed current season range."""
    if stored_season_date_range.season_month != observed_season_date_range.season_month:
        raise ValueError(
            "Cannot merge season date ranges with different season months: "
            f"{stored_season_date_range.season_month} != {observed_season_date_range.season_month}"
        )

    return SeasonDateRange(
        start_date=min(stored_season_date_range.start_date, observed_season_date_range.start_date),
        end_date=max(stored_season_date_range.end_date, observed_season_date_range.end_date),
    )

def _get_dated_round_days(rounds: List[Round]) -> List[date]:
    """Extract round_date values that are present as date objects."""
    return [
        datetime.strptime(round_obj.round_date, "%Y-%m-%d").date()
        for round_obj in rounds
        if round_obj.round_date
    ]
