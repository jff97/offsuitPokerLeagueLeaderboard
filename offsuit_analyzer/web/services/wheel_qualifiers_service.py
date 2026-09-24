"""Wheel qualifier service built from current-month rounds."""
from collections import defaultdict
from typing import Dict, List, Set

from offsuit_analyzer import analytics, data_service
from offsuit_analyzer.datamodel.round import Round
from . import qualification_service


def _get_players_who_played_every_round_by_bar_for_rounds(rounds: List[Round]) -> Dict[str, List[str]]:
    """
    Get players who appeared in every supplied round for each bar.
    """
    # Input: list[Round]. Output: dict[bar_name, list[player_name]] for players seen in every round at that bar.
    rounds_by_bar = defaultdict(list)
    for round_obj in rounds:
        rounds_by_bar[round_obj.bar_name].append(round_obj)

    players_by_bar: Dict[str, List[str]] = {}
    for bar_name, bar_rounds in rounds_by_bar.items():
        player_appearances = defaultdict(int)

        for round_obj in bar_rounds:
            for player_name in {player.player_name for player in round_obj.players}:
                player_appearances[player_name] += 1

        required_rounds = len(bar_rounds)
        players_by_bar[bar_name] = sorted(
            [
                player_name
                for player_name, appearances in player_appearances.items()
                if appearances == required_rounds
            ]
        )

    return dict(players_by_bar)


def get_players_who_played_every_round_by_bar() -> Dict[str, List[str]]:
    """
    Get players who appeared in every current-month round for each bar.

    This is intentionally unfiltered so it can be reused later for other
    displays that need every full-month attendee regardless of wheel criteria.
    """
    # Input: none. Output: dict[bar_name, list[player_name]] for full-month attendees by bar.
    rounds = data_service.get_this_months_rounds_for_bars()
    return _get_players_who_played_every_round_by_bar_for_rounds(rounds)


def _filter_out_qualified_players(players_by_bar: Dict[str, List[str]], qualified_player_names: Set[str]) -> Dict[str, List[str]]:
    """Remove tournament-qualified players from each bar's player list."""
    # Input: dict[bar_name, list[player_name]] and set[player_name]. Output: same dict shape without tournament-qualified players.
    filtered_players_by_bar: Dict[str, List[str]] = {}
    for bar_name, player_names in players_by_bar.items():
        eligible_players = [
            player_name
            for player_name in player_names
            if player_name not in qualified_player_names
        ]
        if eligible_players:
            filtered_players_by_bar[bar_name] = eligible_players

    return filtered_players_by_bar


def _filter_out_unavailable_players(players_by_bar: Dict[str, List[str]], unavailable_players: Set[str]) -> Dict[str, List[str]]:
    """Remove unavailable players from each bar's player list."""
    # Input: dict[bar_name, list[player_name]] and set[player_name]. Output: same dict shape without unavailable players.
    filtered_players_by_bar: Dict[str, List[str]] = {}
    for bar_name, player_names in players_by_bar.items():
        eligible_players = [
            player_name
            for player_name in player_names
            if player_name not in unavailable_players
        ]
        if eligible_players:
            filtered_players_by_bar[bar_name] = eligible_players

    return filtered_players_by_bar


def get_wheel_qualifiers_by_bar() -> Dict[str, List[str]]:
    """
    Get wheel qualifiers by bar for the current month.

    Starts from all players who played every round at a bar, then filters out:
    - players who already qualify for the tournament
    - players currently marked unavailable
    """
    # Input: none. Output: dict[bar_name, list[player_name]] after qualified/unavailable filters are applied.
    rounds = data_service.get_this_months_rounds_for_bars()
    all_round_attendees = _get_players_who_played_every_round_by_bar_for_rounds(rounds)

    unavailable_players = qualification_service.get_unavailable_players()
    qualified_players = analytics.get_qualified_players(rounds, unavailable_players)
    qualified_player_names = {
        qualifier.player_name
        for bar_qualifiers in qualified_players.qualifiers_by_bar.values()
        for qualifier in bar_qualifiers
    }

    players_without_qualified = _filter_out_qualified_players(all_round_attendees, qualified_player_names)
    return _filter_out_unavailable_players(players_without_qualified, unavailable_players)
