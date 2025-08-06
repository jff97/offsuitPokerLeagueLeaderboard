"""
Poker Data Service - Clean interface for fetching poker round data.

This module encapsulates all API interactions and data transformations,
providing a simple interface for the rest of the application.
"""

from .external_data_client import get_this_months_rounds_for_bars
from .legacy_data_client import get_june_data_as_rounds

__all__ = ["get_this_months_rounds_for_bars", "get_june_data_as_rounds"]
