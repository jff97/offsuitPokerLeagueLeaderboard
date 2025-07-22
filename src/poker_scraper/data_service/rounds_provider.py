"""Rounds provider - unified access to poker round data from all sources."""
from typing import List
from . import data_converter
from poker_scraper.datamodel import Round
from poker_scraper.config import BarConfig
from poker_scraper.config import config

def get_this_months_rounds_for_bars() -> List[Round]:
    """
    Fetch poker rounds for configured bars from all data sources.
    
    Returns:
        List of Round objects with calculated poker night dates from API and legacy sources
    """

    # Get API rounds
    api_tokens_with_day = [
        (config.token, config.poker_night) 
        for config in config.BAR_CONFIGS
    ]
    api_rounds = data_converter.get_list_of_rounds_from_api(api_tokens_with_day)
    
    return api_rounds
