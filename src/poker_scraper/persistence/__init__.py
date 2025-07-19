"""
Data Persistence Module - Handles all database operations.

This module encapsulates database interactions for rounds, logs, and warnings,
providing a clean interface for storage and retrieval operations.
"""

from .cosmos_client import (
    store_rounds,
    get_all_rounds,
    save_log,
    save_logs,
    get_all_logs,
    delete_all_logs,
    save_warning,
    save_warnings,
    get_all_warnings,
    delete_all_warnings
)

__all__ = [
    "store_rounds",
    "get_all_rounds", 
    "save_log",
    "save_logs",
    "get_all_logs",
    "delete_all_logs",
    "save_warning",
    "save_warnings", 
    "get_all_warnings",
    "delete_all_warnings"
]
