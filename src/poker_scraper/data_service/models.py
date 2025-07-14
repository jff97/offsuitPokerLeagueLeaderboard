"""Configuration models for poker data service."""
from dataclasses import dataclass

@dataclass
class BarConfig:
    """Configuration for a bar's poker night."""
    token: str
    poker_night: int  # Weekday number: 0=Monday, 1=Tuesday, ..., 6=Sunday
