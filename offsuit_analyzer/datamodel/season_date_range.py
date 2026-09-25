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
    """Return the YYYYMM season key derived only from the observed season date bounds."""
    midpoint_day = _calculate_midpoint_day(start_day, end_day)
    return int(midpoint_day.strftime("%Y%m"))


def _calculate_midpoint_day(start_day: date, end_day: date) -> date:
    """Return the midpoint day between the observed start and end dates."""
    day_span = end_day - start_day
    midpoint_offset = timedelta(days=day_span.days // 2)
    return start_day + midpoint_offset
