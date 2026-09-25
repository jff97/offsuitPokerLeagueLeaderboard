from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any, Dict, Union


@dataclass(frozen=True)
class SeasonDateRange:
    """Stored date range for a season keyed by YYYYMM."""
    start_date: date
    end_date: date
    season_month: int = field(init=False)

    def __post_init__(self) -> None:
        start_day = _normalize_day(self.start_date)
        end_day = _normalize_day(self.end_date)

        if start_day > end_day:
            raise ValueError(f"start_date must be on or before end_date: {self.start_date} > {self.end_date}")

        derived_season_month = _derive_season_month_from_bounds(start_day, end_day)
        object.__setattr__(self, "start_date", start_day)
        object.__setattr__(self, "end_date", end_day)
        object.__setattr__(self, "season_month", derived_season_month)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the stored range to a database document."""
        return {
            "season_month": self.season_month,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonDateRange":
        """Create a stored range from a database document."""
        season_date_range = cls(
            start_date=_normalize_day(data["start_date"]),
            end_date=_normalize_day(data["end_date"]),
        )
        stored_season_month = data.get("season_month", data.get("month_key"))

        if stored_season_month is not None and stored_season_month != season_date_range.season_month:
            raise ValueError(
                "Stored season month does not match derived season month: "
                f"{stored_season_month} != {season_date_range.season_month}"
            )

        return season_date_range


def _normalize_day(day_value: Union[str, date]) -> date:
    """Convert a supported date value into a date object."""
    if isinstance(day_value, date):
        return day_value

    return datetime.strptime(day_value, "%Y-%m-%d").date()


def _derive_season_month_from_bounds(start_day: date, end_day: date) -> int:
    """Return the YYYYMM season key derived from the midpoint of the observed season range."""
    midpoint_day = _calculate_midpoint_day(start_day, end_day)
    return int(midpoint_day.strftime("%Y%m"))


def _calculate_midpoint_day(start_day: date, end_day: date) -> date:
    """Return the midpoint day between the observed start and end dates."""
    day_span = end_day - start_day
    midpoint_offset = timedelta(days=day_span.days // 2)
    return start_day + midpoint_offset
