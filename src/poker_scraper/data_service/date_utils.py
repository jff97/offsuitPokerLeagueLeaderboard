"""Poker round date calculation utilities."""
from datetime import datetime, timedelta

def calculate_poker_night_date(api_date_str: str, target_weekday: int) -> str:
    """
    Calculate poker round date from API timestamp.
    
    Args:
        api_date_str: Date string from API (format: "Wed, 26 Jun 2024 14:30:00 GMT")
        target_weekday: Day of week when round occurred (0=Monday, 6=Sunday)
    
    Returns:
        Date string in YYYY-MM-DD format for the poker night
    """
    try:
        # Parse standard API format only
        entry_date = datetime.strptime(api_date_str, "%a, %d %b %Y %H:%M:%S GMT")
    except ValueError:
        # If parsing fails, return original
        return api_date_str
    
    # Calculate days to go back to find the target weekday
    entry_weekday = entry_date.weekday()
    days_back = (entry_weekday - target_weekday) % 7
    
    # If entry was on the same day, assume it's the previous week's round
    if days_back == 0:
        days_back = 7
    
    poker_date = entry_date - timedelta(days=days_back)
    return poker_date.strftime("%Y-%m-%d")
