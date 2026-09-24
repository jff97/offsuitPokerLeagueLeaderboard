"""Wheel qualifier service built from current-month rounds."""
from collections import defaultdict
from typing import Dict, List, Optional, Set

from offsuit_analyzer import analytics, data_service
from offsuit_analyzer.datamodel.round import Round
from offsuit_analyzer.persistence import excluded_qualifiers_collection


def get_players_who_played_every_round_by_bar(
    rounds: Optional[List[Round]] = None
) -> Dict[str, List[str]]:
    """
    Get players who appeared in every current-month round for each bar.

    This is intentionally unfiltered so it can be reused later for other
    displays that need every full-month attendee regardless of wheel criteria.
    """
    if rounds is None:
        rounds = data_service.get_this_months_rounds_for_bars()

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


def get_wheel_qualifiers_by_bar() -> Dict[str, List[str]]:
    """
    Get wheel qualifiers by bar for the current month.

    Starts from all players who played every round at a bar, then filters out:
    - players who already qualify for the tournament
    - players currently marked unavailable
    """
    rounds = data_service.get_this_months_rounds_for_bars()
    all_round_attendees = get_players_who_played_every_round_by_bar(rounds)

    unavailable_players = excluded_qualifiers_collection.get_excluded_players()
    qualified_players = analytics.get_qualified_players(rounds, unavailable_players)
    qualified_player_names = {
        qualifier.player_name
        for bar_qualifiers in qualified_players.qualifiers_by_bar.values()
        for qualifier in bar_qualifiers
    }

    excluded_players: Set[str] = qualified_player_names | unavailable_players

    filtered_players_by_bar: Dict[str, List[str]] = {}
    for bar_name, player_names in all_round_attendees.items():
        eligible_players = [
            player_name
            for player_name in player_names
            if player_name not in excluded_players
        ]
        if eligible_players:
            filtered_players_by_bar[bar_name] = eligible_players

    return filtered_players_by_bar
