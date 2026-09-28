#gold names are if a player played every round in a season for a particular 
# bar then they will have their name golded on that bars keep the score page. 
#this does not look at the not making it list for saturday tournament its strictly focused on 
# whether a player played every round in a season for a particular bar.
from typing import Dict, List

from offsuit_analyzer.the_wheel import wheel_qualification_service


def get_gold_names_by_bar() -> Dict[str, List[str]]:
    """Get players who played every current-season round for each bar, eligible to be golded."""
    # Input: none.
    # Output: dict[bar_name, list[player_name]], unfiltered by tournament qualification/availability.
    return wheel_qualification_service.get_players_who_played_every_round_last_season_by_bar()