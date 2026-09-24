"""Wheel qualifier service built from current-month rounds."""
from collections import defaultdict
from typing import Dict, List, Set

from offsuit_analyzer import analytics, data_service
from offsuit_analyzer.datamodel.round import Round
from . import qualification_service


def _group_rounds_by_bar(rounds: List[Round]) -> Dict[str, List[Round]]:
    """Group supplied rounds by bar name."""
    # Input: list[Round]. Output: dict[bar_name, list[Round]].
    rounds_by_bar = defaultdict(list)
    for round_obj in rounds:
        rounds_by_bar[round_obj.bar_name].append(round_obj)
    return dict(rounds_by_bar)


def _get_players_who_played_every_round_for_bar(bar_rounds: List[Round]) -> List[str]:
    """Get players who appeared in every supplied round for one bar."""
    # Input: list[Round] for one bar. Output: list[player_name] seen in every round for that bar.
    player_appearances = defaultdict(int)
    for round_obj in bar_rounds:
        for player_name in {player.player_name for player in round_obj.players}:
            player_appearances[player_name] += 1

    required_rounds = len(bar_rounds)
    return sorted(
        [
            player_name
            for player_name, appearances in player_appearances.items()
            if appearances == required_rounds
        ]
    )


def get_players_who_played_every_round_by_bar() -> Dict[str, List[str]]:
    """
    Get players who appeared in every current-month round for each bar.

    This is intentionally unfiltered so it can be reused later for other
    displays that need every full-month attendee regardless of wheel criteria.
    """
    # Input: none. Output: dict[bar_name, list[player_name]] for full-month attendees by bar.
    rounds = data_service.get_this_months_rounds_for_bars()
    rounds_by_bar = _group_rounds_by_bar(rounds)
    return {
        bar_name: _get_players_who_played_every_round_for_bar(bar_rounds)
        for bar_name, bar_rounds in rounds_by_bar.items()
    }


def _filter_out_qualified_players(player_names: List[str], qualified_player_names: Set[str]) -> List[str]:
    """Remove tournament-qualified players from one bar's player list."""
    # Input: list[player_name] for one bar and set[player_name]. Output: filtered list[player_name].
    return [player_name for player_name in player_names if player_name not in qualified_player_names]


def _filter_out_unavailable_players(player_names: List[str], unavailable_players: Set[str]) -> List[str]:
    """Remove unavailable players from one bar's player list."""
    # Input: list[player_name] for one bar and set[player_name]. Output: filtered list[player_name].
    return [player_name for player_name in player_names if player_name not in unavailable_players]


def _get_wheel_qualifiers_for_bar(bar_rounds: List[Round], qualified_player_names: Set[str], unavailable_players: Set[str]) -> List[str]:
    """Get wheel qualifiers for one bar after attendance and filter rules."""
    # Input: list[Round] for one bar plus qualified/unavailable player sets. Output: filtered list[player_name] for that bar.
    player_names = _get_players_who_played_every_round_for_bar(bar_rounds)
    player_names = _filter_out_qualified_players(player_names, qualified_player_names)
    return _filter_out_unavailable_players(player_names, unavailable_players)


def get_wheel_qualifiers_by_bar() -> Dict[str, List[str]]:
    """
    Get wheel qualifiers by bar for the current month.

    Starts from all players who played every round at a bar, then filters out:
    - players who already qualify for the tournament
    - players currently marked unavailable
    """
    # Input: none. Output: dict[bar_name, list[player_name]] after qualified/unavailable filters are applied.
    rounds = data_service.get_this_months_rounds_for_bars()
    rounds_by_bar = _group_rounds_by_bar(rounds)

    unavailable_players = qualification_service.get_unavailable_players()
    qualified_players = analytics.get_qualified_players(rounds, unavailable_players)
    qualified_player_names = {
        qualifier.player_name
        for bar_qualifiers in qualified_players.qualifiers_by_bar.values()
        for qualifier in bar_qualifiers
    }

    qualifiers_by_bar: Dict[str, List[str]] = {}
    for bar_name, bar_rounds in rounds_by_bar.items():
        wheel_qualifiers = _get_wheel_qualifiers_for_bar(bar_rounds, qualified_player_names, unavailable_players)
        if wheel_qualifiers:
            qualifiers_by_bar[bar_name] = wheel_qualifiers

    return qualifiers_by_bar
