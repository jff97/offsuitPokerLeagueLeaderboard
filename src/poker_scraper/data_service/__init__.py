"""
Poker Data Service - Clean interface for fetching poker round data.

This module encapsulates all API interactions and data transformations,
providing a simple interface for the rest of the application.
"""

from .rounds_provider import get_rounds_for_bars

__all__ = ["get_rounds_for_bars"]
