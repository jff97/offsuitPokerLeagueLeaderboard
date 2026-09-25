"""Determine and persist current season date ranges from incoming API rounds."""
from typing import List, Tuple

from offsuit_analyzer.datamodel import Round, SeasonDateRange
from offsuit_analyzer.persistence import season_date_ranges_collection


def current_season_has_dated_rounds(rounds: List[Round]) -> bool:
    """Return True when at least one round has a usable date."""
    return len(_get_dated_round_values(rounds)) > 0


def determine_current_season_date_bounds(rounds: List[Round]) -> Tuple[str, str]:
    """Return the earliest and latest round_date values found in rounds."""
    dated_round_values = _get_dated_round_values(rounds)

    if not dated_round_values:
        raise ValueError("Current season rounds do not contain any round_date values.")

    return min(dated_round_values), max(dated_round_values)


def build_current_season_date_range(rounds: List[Round]) -> SeasonDateRange:
    """Build the current season date range from the incoming current-season rounds."""
    start_date, end_date = determine_current_season_date_bounds(rounds)
    return SeasonDateRange(
        start_date=start_date,
        end_date=end_date,
    )


def merge_season_date_ranges(
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


def update_current_season_date_range(rounds: List[Round]) -> bool:
    """Persist the current season date range using the latest incoming API rounds."""
    if not current_season_has_dated_rounds(rounds):
        return False

    observed_season_date_range = build_current_season_date_range(rounds)
    saved_season_date_range = _get_saved_season_date_range(observed_season_date_range.season_month)
    merged_season_date_range = observed_season_date_range
    if saved_season_date_range is not None:
        merged_season_date_range = merge_season_date_ranges(
            saved_season_date_range,
            observed_season_date_range,
        )
    season_date_ranges_collection.save_season_date_range(merged_season_date_range)
    return True


def _get_dated_round_values(rounds: List[Round]) -> List[str]:
    """Extract round_date values that are present."""
    return [round_obj.round_date for round_obj in rounds if round_obj.round_date]


def _get_saved_season_date_range(season_month: int):
    """Return the single saved season range for season_month, or None when absent."""
    saved_season_date_ranges = season_date_ranges_collection.get_season_date_ranges(season_month)

    if not saved_season_date_ranges:
        return None

    if len(saved_season_date_ranges) != 1:
        raise ValueError(
            f"Expected at most one saved season date range for {season_month}, "
            f"but found {len(saved_season_date_ranges)}."
        )

    return saved_season_date_ranges[0]
