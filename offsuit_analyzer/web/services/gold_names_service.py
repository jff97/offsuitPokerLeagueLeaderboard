from typing import Dict, List

from offsuit_analyzer.season_history import gold_names_service


def get_gold_names_by_bar() -> Dict[str, List[str]]:
    return gold_names_service.get_gold_names_by_bar()
