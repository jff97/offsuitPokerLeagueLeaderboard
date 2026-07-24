"""Poker round date calculation utilities."""
from datetime import datetime, timedelta
import pytz

from offsuit_analyzer.config import Config

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
        # Parse standard API format (GMT time)
        entry_date_gmt = datetime.strptime(api_date_str, "%a, %d %b %Y %H:%M:%S GMT")
        # Localize to GMT
        entry_date_gmt = pytz.UTC.localize(entry_date_gmt)
        # Convert to Central Time
        config = Config()
        central_tz = pytz.timezone(config.POKER_TIMEZONE)
        entry_date = entry_date_gmt.astimezone(central_tz)
        print(f"Parsed API date: {entry_date} (Central Time)")
    except ValueError:
        # If parsing fails, return original
        return api_date_str
    
    # Calculate days to go back to find the target weekday
    entry_weekday = entry_date.weekday()
    days_back = (entry_weekday - target_weekday) % 7
    
    poker_date = entry_date - timedelta(days=days_back)
    return poker_date.strftime("%Y-%m-%d")


if __name__ == "__main__":
    # Test cases: (api_date_str, target_weekday, expected_result, description)
    test_cases = [
        # Normal case: entered during day on poker night (Wednesday=2)
        ("Wed, 15 Jul 2026 14:30:00 GMT", 2, "2026-07-15", "Entry Wed 09:30 Central (poker day)"),
        
        # Early morning entry (likely from previous night's late entries)
        ("Thu, 16 Jul 2026 03:00:00 GMT", 2, "2026-07-15", "Entry Wed 22:00 Central (previous night's game)"),
        
        # Entry day before poker night
        ("Tue, 14 Jul 2026 20:00:00 GMT", 2, "2026-07-08", "Entry Tue 15:00 Central (day before Wednesday game)"),
        
        # Different day: Monday poker night, entry on Monday afternoon
        ("Mon, 13 Jul 2026 10:00:00 GMT", 0, "2026-07-13", "Entry Mon 05:00 Central (poker day)"),
        
        # Same day different timezone: Saturday entry (poker on Friday)
        ("Sat, 11 Jul 2026 08:30:00 GMT", 4, "2026-07-10", "Entry Sat 03:30 Central (previous Friday's game)"),
        
        # Edge case: entry at midnight UTC (becomes previous day in Central)
        ("Wed, 15 Jul 2026 00:00:00 GMT", 2, "2026-07-08", "Entry Tue 19:00 Central (previous Wednesday)"),
        
        # Sunday entry, poker on Friday
        ("Sun, 12 Jul 2026 14:00:00 GMT", 4, "2026-07-10", "Entry Sun 09:00 Central (previous Friday)"),
        
        # Same weekday as target but wrong week
        ("Wed, 22 Jul 2026 10:00:00 GMT", 2, "2026-07-22", "Entry Wed 05:00 Central (poker day, week after)"),
        
        # Late evening entry same day as target
        ("Mon, 13 Jul 2026 23:00:00 GMT", 0, "2026-07-13", "Entry Mon 18:00 Central (poker day)"),
        
        # Friday entry, poker on Friday
        ("Fri, 10 Jul 2026 16:30:00 GMT", 4, "2026-07-10", "Entry Fri 11:30 Central (poker day)"),
        
        # Thursday entry at 9 AM, poker on Thursday
        ("Thu, 16 Jul 2026 14:00:00 GMT", 3, "2026-07-16", "Entry Thu 09:00 Central (poker day)"),
        
        # Saturday late evening, poker on Sunday
        ("Sat, 11 Jul 2026 23:45:00 GMT", 6, "2026-07-05", "Entry Sat 18:45 Central (previous Sunday)"),
        
        # Tuesday early morning (Monday late night in Central), poker on Monday
        ("Tue, 14 Jul 2026 03:30:00 GMT", 0, "2026-07-13", "Entry Mon 22:30 Central (poker day)"),
        
        # Two weeks back: Friday entry, poker on Friday
        ("Fri, 03 Jul 2026 15:00:00 GMT", 4, "2026-07-03", "Entry Fri 10:00 Central (poker day)"),
        
        # Early morning Thursday (2 AM Central), poker on Monday
        ("Thu, 16 Jul 2026 07:00:00 GMT", 0, "2026-07-13", "Entry Thu 02:00 Central (previous Monday game)"),
        
        # Sunday midnight UTC, poker on Sunday
        ("Sun, 12 Jul 2026 00:00:00 GMT", 6, "2026-07-05", "Entry Sat 19:00 Central (previous Sunday)"),
        
        # Friday early morning (6:30 AM Central), poker on Friday
        ("Fri, 10 Jul 2026 11:30:00 GMT", 4, "2026-07-10", "Entry Fri 06:30 Central (poker day)"),
    ]
    
    passed = 0
    failed = 0
    
    print("Running Poker Night Date Tests\n")
    print("-" * 80)
    
    for api_date, target_day, expected, description in test_cases:
        result = calculate_poker_night_date(api_date, target_day)
        status = "PASS" if result == expected else "FAIL"
        
        if result == expected:
            passed += 1
        else:
            failed += 1
        
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        print(f"[{status}] {description}")
        print(f"      Input: {api_date}, Target: {day_names[target_day]}")
        print(f"      Expected: {expected}, Got: {result}")
        print()
    
    print("-" * 80)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")