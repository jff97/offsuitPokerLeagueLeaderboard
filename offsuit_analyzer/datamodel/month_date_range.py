from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class MonthDateRange:
    """Stored date range for a season keyed by YYYYMM."""
    month_key: int
    start_date: str
    end_date: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert the stored range to a database document."""
        return {
            "month_key": self.month_key,
            "start_date": self.start_date,
            "end_date": self.end_date,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonthDateRange":
        """Create a stored range from a database document."""
        return cls(
            month_key=data["month_key"],
            start_date=data["start_date"],
            end_date=data["end_date"],
        )
