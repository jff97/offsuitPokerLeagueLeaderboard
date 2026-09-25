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

        start_season_month = _derive_season_month_for_day(start_day)
        end_season_month = _derive_season_month_for_day(end_day)

        if start_season_month != end_season_month:
            raise ValueError(
                "start_date and end_date must belong to the same season month: "
                f"{self.start_date} -> {start_season_month}, {self.end_date} -> {end_season_month}"
            )

        object.__setattr__(self, "season_month", start_season_month)

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


def _derive_season_month_for_day(observed_day: date) -> int:
    """Return the YYYYMM season key for a single observed day."""
    next_month_first_day = _get_first_day_of_next_month(observed_day)
    next_season_start_day = _get_season_start_day_for_month(next_month_first_day)

    if observed_day >= next_season_start_day:
        return int(next_month_first_day.strftime("%Y%m"))

    return int(observed_day.strftime("%Y%m"))


def _get_first_day_of_next_month(observed_day: date) -> date:
    """Return the first day of the month after observed_day."""
    if observed_day.month == 12:
        return date(observed_day.year + 1, 1, 1)

    return date(observed_day.year, observed_day.month + 1, 1)


def _get_season_start_day_for_month(month_first_day: date) -> date:
    """Return the Saturday before the given month begins."""
    days_back_to_saturday = (month_first_day.weekday() - 5) % 7
    if days_back_to_saturday == 0:
        days_back_to_saturday = 7

    return month_first_day - timedelta(days=days_back_to_saturday)
