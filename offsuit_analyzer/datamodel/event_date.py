from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Union


@dataclass(frozen=True)
class EventDate:
    """Stored event date observed during a refresh."""
    event_date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_date", _normalize_day(self.event_date))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_date": self.event_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EventDate":
        return cls(event_date=data["event_date"])


def _normalize_day(day_value: Union[str, date]) -> date:
    if isinstance(day_value, date):
        return day_value

    return datetime.strptime(day_value, "%Y-%m-%d").date()
