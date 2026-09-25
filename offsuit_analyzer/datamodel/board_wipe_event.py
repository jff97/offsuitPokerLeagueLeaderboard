from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Dict, Union


@dataclass(frozen=True)
class BoardWipeEvent:
    """Stored board-wipe event observed during a refresh."""
    board_wipe_date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "board_wipe_date", _normalize_day(self.board_wipe_date))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "board_wipe_date": self.board_wipe_date.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoardWipeEvent":
        return cls(board_wipe_date=data["board_wipe_date"])


def _normalize_day(day_value: Union[str, date]) -> date:
    if isinstance(day_value, date):
        return day_value

    return datetime.strptime(day_value, "%Y-%m-%d").date()
