"""Rounds provider - unified access to poker round data from all sources."""
from typing import List
from .models import BarConfig
from .data_converter import get_list_of_rounds_from_api
from .legacy_data_client import get_june_data_as_rounds
from ..datamodel import Round

def get_rounds_for_bars(bar_configs: List[BarConfig], include_legacy: bool = True) -> List[Round]:
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
    api_rounds = get_list_of_rounds_from_api(api_tokens_with_day)
    
    # Add legacy rounds if requested
    if include_legacy:
        legacy_rounds = get_june_data_as_rounds()
        return api_rounds + legacy_rounds
    
    return api_rounds
