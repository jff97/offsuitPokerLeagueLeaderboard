from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, Union


@dataclass(frozen=True)
class SeasonWindow:
    """Stored season window keyed by YYYYMM."""
    season_month: int
    start_date: date
    end_date: date

    def __post_init__(self) -> None:
        start_day = _normalize_day(self.start_date)
        end_day = _normalize_day(self.end_date)

        if start_day > end_day:
            raise ValueError(f"start_date must be on or before end_date: {self.start_date} > {self.end_date}")

        derived_season_month = _derive_season_month(start_day, end_day)
        if self.season_month != derived_season_month:
            raise ValueError(
                "season_month must match midpoint-derived season month: "
                f"{self.season_month} != {derived_season_month}"
            )

        object.__setattr__(self, "start_date", start_day)
        object.__setattr__(self, "end_date", end_day)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "season_month": self.season_month,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SeasonWindow":
        return cls(
            season_month=data["season_month"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )


def derive_season_month(start_date: Union[str, date], end_date: Union[str, date]) -> int:
    return _derive_season_month(_normalize_day(start_date), _normalize_day(end_date))


def _derive_season_month(start_day: date, end_day: date) -> int:
    midpoint_day = start_day + timedelta(days=(end_day - start_day).days // 2)
    return int(midpoint_day.strftime("%Y%m"))


def _normalize_day(day_value: Union[str, date]) -> date:
    if isinstance(day_value, date):
        return day_value

    return datetime.strptime(day_value, "%Y-%m-%d").date()
