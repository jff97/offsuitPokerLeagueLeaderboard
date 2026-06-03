"""Logging service for application-wide logging."""
from datetime import datetime
from offsuit_analyzer.datamodel.log_entry import LogEntry, LogSeverity
from offsuit_analyzer import persistence


def log_info(message: str) -> None:
    """Log an info-level message.
    
    Args:
        message: The message to log
    """
    log_entry = LogEntry(
        message=message,
        severity=LogSeverity.INFO,
        timestamp=datetime.utcnow()
    )
    persistence.logs_collection.save_log(log_entry)


def log_warning(message: str) -> None:
    """Log a warning-level message.
    
    Args:
        message: The message to log
    """
    log_entry = LogEntry(
        message=message,
        severity=LogSeverity.WARNING,
        timestamp=datetime.utcnow()
    )
    persistence.logs_collection.save_log(log_entry)


def log_critical(message: str) -> None:
    """Log a critical-level message.
    
    Args:
        message: The message to log
    """
    log_entry = LogEntry(
        message=message,
        severity=LogSeverity.CRITICAL,
        timestamp=datetime.utcnow()
    )
    persistence.logs_collection.save_log(log_entry)
