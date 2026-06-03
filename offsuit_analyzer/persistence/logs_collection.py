"""Logs collection operations."""
from typing import List
from offsuit_analyzer.datamodel.log_entry import LogEntry
from . import cosmos_client


def save_log(log_entry: LogEntry) -> None:
    """Save a single log entry to the database.
    
    Args:
        log_entry: The LogEntry to save
    """
    collection = cosmos_client.db[cosmos_client.config.LOGS_COLLECTION_NAME]
    collection.insert_one(log_entry.to_dict())


def save_logs(log_entries: List[LogEntry]) -> None:
    """Save multiple log entries to the database.
    
    Args:
        log_entries: List of LogEntry objects to save
    """
    if not log_entries:
        return
    
    collection = cosmos_client.db[cosmos_client.config.LOGS_COLLECTION_NAME]
    collection.insert_many([log.to_dict() for log in log_entries])


def get_all_logs() -> List[LogEntry]:
    """Retrieve all log entries from the database.
    
    Returns:
        List of LogEntry objects
    """
    collection = cosmos_client.db[cosmos_client.config.LOGS_COLLECTION_NAME]
    docs = list(collection.find({}))
    return [LogEntry.from_dict(doc) for doc in docs]


def get_logs_by_severity(severity: str) -> List[LogEntry]:
    """Retrieve log entries filtered by severity.
    
    Args:
        severity: The severity level to filter by (info/warning/critical)
        
    Returns:
        List of LogEntry objects matching the severity
    """
    collection = cosmos_client.db[cosmos_client.config.LOGS_COLLECTION_NAME]
    docs = list(collection.find({"severity": severity}))
    return [LogEntry.from_dict(doc) for doc in docs]


def clear_all_logs() -> None:
    """Delete all log entries from the database."""
    collection = cosmos_client.db[cosmos_client.config.LOGS_COLLECTION_NAME]
    collection.delete_many({})
