"""Log entry data model."""
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class LogSeverity(Enum):
    """Log severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class LogEntry:
    """Represents a single log entry."""
    message: str
    severity: LogSeverity
    timestamp: datetime

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "message": self.message,
            "severity": self.severity.value,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: dict) -> 'LogEntry':
        """Create LogEntry from dictionary."""
        return LogEntry(
            message=data.get("message"),
            severity=LogSeverity(data.get("severity")),
            timestamp=data.get("timestamp")
        )
