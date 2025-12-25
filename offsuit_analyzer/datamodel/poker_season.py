"""LeagueSeasonCalendar - Admin-maintained calendar of league season dates."""
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import date


@dataclass
class MonthRange:
    """Start and end dates for a month."""
    start_date: date | None
    end_date: date | None

    def to_dict(self) -> Dict[str, str | None]:
        return {
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MonthRange":
        start = data.get("start_date")
        end = data.get("end_date")
        start_dt = date.fromisoformat(start) if start else None
        end_dt = date.fromisoformat(end) if end else None
        return cls(start_date=start_dt, end_date=end_dt)


@dataclass
class LeagueSeasonCalendar:
    """Admin-maintained calendar of league season dates.
    
    Contains month date ranges for poker seasons. Admins input and maintain
    these dates. No validation—admins are responsible for accuracy.
    """
    months: Dict[str, MonthRange] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for database storage."""
        return {
            "months": {month: date_range.to_dict() for month, date_range in self.months.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LeagueSeasonCalendar":
        """Create from dict from database."""
        months = {
            month: MonthRange.from_dict(date_range)
            for month, date_range in data.get("months", {}).items()
        }
        return cls(months=months)

    def __str__(self) -> str:
        """Return readable string representation."""
        return f"LeagueSeasonCalendar ({len(self.months)} months)"
