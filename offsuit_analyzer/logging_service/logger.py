"""Logging service for application-wide logging."""
from datetime import datetime
from typing import List
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


def get_all_logs() -> List[LogEntry]:
    """Retrieve all log entries.
    
    Returns:
        List of all LogEntry objects
    """
    return persistence.logs_collection.get_all_logs()

def main_to_text_file():
    logs = get_all_logs()

    output_file = "logs.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"Total logs: {len(logs)}\n\n")
        for log in logs:
            f.write(f"[{log.severity.value}] {log.timestamp}: {log.message}\n")

    print(f"Wrote {len(logs)} logs to {output_file}")

if __name__ == "__main__":
    main_to_text_file() 


    
