"""Rounds provider - unified access to poker round data from all sources."""
from typing import List
from . import data_converter
from poker_scraper.datamodel import Round
from poker_scraper.config import BarConfig

def get_this_months_rounds_for_bars(bar_configs: List[BarConfig]) -> List[Round]:
    """
    Fetch poker rounds for configured bars from all data sources.
    
    Args:
        bar_configs: List of bar configurations with tokens and poker night info
        include_legacy: Whether to include legacy CSV data (default: True)
        
    Returns:
        List of Round objects with calculated poker night dates from API and legacy sources
    """
    # Get API rounds
    api_tokens_with_day = [
        (config.token, config.poker_night) 
        for config in bar_configs
    ]
    api_rounds = data_converter.get_list_of_rounds_from_api(api_tokens_with_day)
    
    return api_rounds
