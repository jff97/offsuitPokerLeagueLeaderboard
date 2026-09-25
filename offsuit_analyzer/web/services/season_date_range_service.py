"""Determine and persist current season date ranges from incoming API rounds."""
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Tuple

from offsuit_analyzer.datamodel import Round, SeasonDateRange
from offsuit_analyzer.persistence import season_date_ranges_collection

MIN_ROUNDS_PER_STALE_BAR = 3
MAX_STALE_BARS_FOR_ROLLOVER = 2


def update_current_season_date_range(rounds: List[Round]) -> bool:
    """Persist the current season date range using the latest incoming API rounds."""
    dated_round_days = _get_dated_round_days(rounds)
    if _is_empty_round_observation(dated_round_days):
        return _seed_current_season_date_range()

    observed_season_date_range = _build_current_season_date_range(dated_round_days)
    if _is_near_empty_round_observation(rounds, observed_season_date_range):
        return _seed_current_season_date_range()

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


def _is_empty_round_observation(round_days: List[date]) -> bool:
    """Return True when the refresh produced no usable dated rounds."""
    return not _current_season_has_dated_rounds(round_days)


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


def _seed_current_season_date_range() -> bool:
    """Ensure the current month has a seeded season date range for rollover transitions."""
    today = _get_current_poker_date()
    current_season_date_range = SeasonDateRange(
        start_date=today,
        end_date=today,
    )
    saved_season_date_range = season_date_ranges_collection.get_season_date_range(
        current_season_date_range.season_month
    )
    if saved_season_date_range is None:
        season_date_ranges_collection.save_season_date_range(current_season_date_range)
    return True


def _is_near_empty_round_observation(
    rounds: List[Round],
    observed_season_date_range: SeasonDateRange,
) -> bool:
    """Return True when only a couple uncleared previous-month bars remain populated."""
    current_poker_date = _get_current_poker_date()
    previous_season_month = _get_previous_season_month(current_poker_date)
    if observed_season_date_range.season_month != previous_season_month:
        return False

    rounds_by_bar = _group_rounds_by_bar(rounds)
    active_bar_count = len(rounds_by_bar)
    configured_bar_count = _get_configured_bar_count()

    if active_bar_count == 0 or active_bar_count > MAX_STALE_BARS_FOR_ROLLOVER:
        return False

    if configured_bar_count > active_bar_count and not _all_active_bars_have_stale_round_counts(rounds_by_bar):
        return False

    return configured_bar_count > active_bar_count


def _get_current_poker_date() -> date:
    """Return today's date in the configured poker timezone."""
    import pytz
    from offsuit_analyzer.config import config

    return datetime.now(pytz.timezone(config.POKER_TIMEZONE)).date()


def _get_previous_season_month(current_poker_date: date) -> int:
    """Return the YYYYMM key for the month immediately before the current poker date."""
    previous_month_day = current_poker_date.replace(day=1) - timedelta(days=1)
    return int(previous_month_day.strftime("%Y%m"))


def _get_configured_bar_count() -> int:
    """Return the number of configured bars expected in the monthly refresh."""
    from offsuit_analyzer.config import config

    return len(config.BAR_CONFIGS)


def _group_rounds_by_bar(rounds: List[Round]) -> Dict[str, List[Round]]:
    """Group supplied rounds by bar identifier."""
    rounds_by_bar: Dict[str, List[Round]] = defaultdict(list)
    for round_obj in rounds:
        rounds_by_bar[round_obj.bar_id].append(round_obj)
    return dict(rounds_by_bar)


def _all_active_bars_have_stale_round_counts(rounds_by_bar: Dict[str, List[Round]]) -> bool:
    """Return True when every remaining populated bar looks like an uncleared old board."""
    return all(len(bar_rounds) >= MIN_ROUNDS_PER_STALE_BAR for bar_rounds in rounds_by_bar.values())


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
