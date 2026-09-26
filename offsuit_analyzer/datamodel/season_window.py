from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Tuple, Union


@dataclass(frozen=True)
class SeasonWindow:
    """Stored season window keyed by year and month."""
    year: int
    month: int
    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        start_day = _normalize_day(self.start_date)
        end_day = _normalize_day(self.end_date)

        if start_day > end_day:
            raise ValueError(f"start_date must be on or before end_date: {self.start_date} > {self.end_date}")

        derived_year, derived_month = _derive_year_month(start_day, end_day)
        if self.year != derived_year or self.month != derived_month:
            raise ValueError(
                "year/month must match midpoint-derived year/month: "
                f"({self.year}, {self.month}) != ({derived_year}, {derived_month})"
            )

        object.__setattr__(self, "start_date", start_day)
        object.__setattr__(self, "end_date", end_day)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "year": self.year,
            "month": self.month,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonWindow":
        return cls(
            year=data["year"],
            month=data["month"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )


def derive_year_month(start_date: Union[str, date], end_date: Union[str, date]) -> Tuple[int, int]:
    return _derive_year_month(_normalize_day(start_date), _normalize_day(end_date))


def _derive_year_month(start_day: date, end_day: date) -> Tuple[int, int]:
    midpoint_day = start_day + timedelta(days=(end_day - start_day).days // 2)
    return midpoint_day.year, midpoint_day.month


def _normalize_day(day_value: Union[str, date]) -> date:
    if isinstance(day_value, date):
        return day_value

    return datetime.strptime(day_value, "%Y-%m-%d").date()
