#gold names are if a player played every round in a season for a particular 
# bar then they will have their name golded on that bars keep the score page. 
#this does not look at the not making it list for saturday tournament its strictly focused on 
# whether a player played every round in a season for a particular bar.
from typing import Dict, List

from offsuit_analyzer.the_wheel import wheel_qualification_service
from offsuit_analyzer.data_service import keep_the_score_api_client
from offsuit_analyzer.data_service.external_data_client import normalize_player_name
from offsuit_analyzer.config import config

# Board JSON memoized per bar token for the duration of a single gold-name run; cleared in set_gold_names_on_keep_the_score's finally block.
_board_json_cache: Dict[str, dict] = {}


def _get_cached_board_json(bar_token: str) -> dict:
    if bar_token not in _board_json_cache:
        _board_json_cache[bar_token] = keep_the_score_api_client.fetch_board_json(bar_token)
    return _board_json_cache[bar_token]


def _get_last_season_gold_player_ids_at_each_bar() -> Dict[str, List[int]]:
    """Get players who played every round last season for each bar to be golded."""
    gold_names_by_bar_name = wheel_qualification_service.get_players_who_played_every_round_last_season_by_bar()
    bar_token_by_bar_name = _get_bar_token_by_bar_name()

    gold_player_ids_by_bar_token = {}

    for bar_name, player_names in gold_names_by_bar_name.items():
        bar_token = bar_token_by_bar_name.get(bar_name)
        if bar_token is None:
            continue
        gold_player_ids_by_bar_token[bar_token] = _get_player_ids_for_names(bar_token,player_names)

    return gold_player_ids_by_bar_token

def _get_player_ids_for_names(bar_token: str, player_names: List[str]) -> List[int]:
    players = _get_cached_board_json(bar_token).get("players", [])
    all_player_names_and_ids = {player["name"]: player["id"] for player in players}

    player_ids_by_normalized_name = {
        normalize_player_name(name): player_id
        for name, player_id in all_player_names_and_ids.items()
    }

    return [
        player_ids_by_normalized_name[normalize_player_name(name)]
        for name in player_names
        if normalize_player_name(name) in player_ids_by_normalized_name
    ]


def set_gold_names_on_keep_the_score() -> None:
    """Update every bar's Keep The Score page so only last season's gold names are golded."""
    try:
        new_gold_names_by_bar_token = _get_last_season_gold_player_ids_at_each_bar()
        for bar_token, gold_player_ids in new_gold_names_by_bar_token.items():
            _set_players_gold_for_bar(bar_token, gold_player_ids)
    finally:
        _board_json_cache.clear()


def _get_bar_token_by_bar_name() -> Dict[str, str]:
    """Fetch each configured bar's board title once and index tokens by title."""
    # TODO: once bar config moves to a DB-backed admin API (separate ticket), persist each
    # token's resolved bar_name in a collection (like season_windows_collection) and only
    # call get_board_title for tokens missing from it, instead of fetching live every run.
    return {
        _get_cached_board_json(bar_config.token).get("board", {}).get("appearance", {}).get("title", "Unknown"): bar_config.token
        for bar_config in config.BAR_CONFIGS
    }


def _set_players_gold_for_bar(bar_token: str, gold_player_ids: List[int]) -> None:
    #this function should first reset the players who are gold at this bar to default then gold the correct players
    """Reset every player at this bar to default color, then gold only the given names."""

    # Get the list of player IDs who are currently gold at this bar.
    gold_player_ids_at_bar_currently = _get_gold_player_ids_currently_on_bar(bar_token)

    # Reset all currently gold players to default color before setting the new gold players.
    _reset_players_to_default_color(bar_token, gold_player_ids_at_bar_currently)

    # make the newly calculated gold players gold at this bar.
    _set_players_gold(bar_token, gold_player_ids)
    

def _get_gold_player_ids_currently_on_bar(bar_token: str) -> List[int]:
    #fetch the board with fetch board json
    #get the list of players from the board json
    #from that list extract the players who are currently gold and return as a list of player IDs
    #return that
    board_json = _get_cached_board_json(bar_token)
    players = board_json.get("players", [])
    
    gold_players = [player["id"] for player in players if player.get("text_color") not in (None, "")]
    return gold_players


def _reset_players_to_default_color(bar_token: str, player_ids: List[int]) -> None:
    """Clear any existing gold color from every player at this bar."""
    for player_id in player_ids:
        keep_the_score_api_client.make_player_name_default_color_at_bar(bar_token, player_id)


def _set_players_gold(bar_token: str, gold_player_ids: List[int]) -> None:
    """Set only the given player IDs to gold at this bar."""
    for player_id in gold_player_ids:
        keep_the_score_api_client.make_player_name_gold_at_bar(bar_token, player_id)

if __name__ == "__main__":
    set_gold_names_on_keep_the_score()
    #command to run it as module is
    #python -m offsuit_analyzer.season_history.gold_names_service