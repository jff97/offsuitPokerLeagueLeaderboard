from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict


@dataclass(frozen=True)
class SeasonDateRange:
    """Stored date range for a season keyed by YYYYMM."""
    start_date: str
    end_date: str
    season_month: int = field(init=False)

    def __post_init__(self) -> None:
        start_day = _parse_day(self.start_date)
        end_day = _parse_day(self.end_date)

        if start_day > end_day:
            raise ValueError(f"start_date must be on or before end_date: {self.start_date} > {self.end_date}")

        derived_season_month = _derive_season_month_from_bounds(start_day, end_day)
        object.__setattr__(self, "season_month", derived_season_month)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the stored range to a database document."""
        return {
            "season_month": self.season_month,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonDateRange":
        """Create a stored range from a database document."""
        season_date_range = cls(
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
        stored_season_month = data.get("season_month", data.get("month_key"))

        if stored_season_month is not None and stored_season_month != season_date_range.season_month:
            raise ValueError(
                "Stored season month does not match derived season month: "
                f"{stored_season_month} != {season_date_range.season_month}"
            )

        return season_date_range


def _parse_day(day_text: str) -> date:
    """Convert a YYYY-MM-DD string into a date."""
    return datetime.strptime(day_text, "%Y-%m-%d").date()


def _derive_season_month_from_bounds(start_day: date, end_day: date) -> int:
    """Return the YYYYMM season key for the month containing the most observed season days."""
    day_counts_by_month = _count_days_by_month(start_day, end_day)
    return _select_season_month_from_day_counts(day_counts_by_month, end_day)


def _count_days_by_month(start_day: date, end_day: date) -> Dict[int, int]:
    """Count how many observed days in the season range fall in each YYYYMM month."""
    day_counts_by_month: Dict[int, int] = {}
    current_day = start_day

    while current_day <= end_day:
        month_key = int(current_day.strftime("%Y%m"))
        existing_count = day_counts_by_month.get(month_key, 0)
        day_counts_by_month[month_key] = existing_count + 1
        current_day = current_day + timedelta(days=1)

    return day_counts_by_month


def _select_season_month_from_day_counts(day_counts_by_month: Dict[int, int], end_day: date) -> int:
    """Choose the season month from observed day counts, using the latest month to break ties."""
    if not day_counts_by_month:
        raise ValueError("Cannot derive season month without any observed days.")

    highest_day_count = max(day_counts_by_month.values())
    candidate_months = [
        month_key
        for month_key, day_count in day_counts_by_month.items()
        if day_count == highest_day_count
    ]

    if len(candidate_months) == 1:
        return candidate_months[0]

    ending_month = int(end_day.strftime("%Y%m"))
    if ending_month in candidate_months:
        return ending_month

    return max(candidate_months)
