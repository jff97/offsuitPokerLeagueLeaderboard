"""
Poker Data Service - Clean interface for fetching poker round data.

This module encapsulates all API interactions and data transformations,
providing a simple interface for the rest of the application.
"""

from .external_data_client import get_this_months_rounds_for_bars
from .exportBarListTool import email_bar_list_report

__all__ = ["get_this_months_rounds_for_bars", "email_bar_list_report"]
