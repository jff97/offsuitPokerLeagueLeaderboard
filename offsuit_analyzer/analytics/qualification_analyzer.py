"""Qualification analyzer - determines tournament qualifiers from round results."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime
from collections import defaultdict

from offsuit_analyzer.datamodel.round import Round

# Type aliases for clarity
BarName = str
PlayerName = str
Placement = int
Points = int
BarPlayerPoints = Dict[BarName, Dict[PlayerName, Points]]
PlayerQualificationTuple = Tuple[PlayerName, Placement, Points]


@dataclass(frozen=True)
class PlayerQualification:
    """Represents a player's qualification at a specific bar."""
    player_name: str
    placement: int  # 1, 2, or 3
    total_points: int
    bar_name: str


@dataclass
class QualifiedPlayersByBar:
    """Represents all qualified players organized by bar."""
    qualifiers_by_bar: Dict[str, List[PlayerQualification]] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dictionary."""
        return {
            bar_name: [
                {
                    "player_name": q.player_name,
                    "placement": q.placement,
                    "total_points": q.total_points,
                }
                for q in qualifiers
            ]
            for bar_name, qualifiers in self.qualifiers_by_bar.items()
        }


def _aggregate_points_by_bar_and_player(
    rounds: List[Round],
    excluded_players: Optional[Set[str]] = None
) -> BarPlayerPoints:
    """
    Aggregate total points for each player at each bar across all rounds.
    
    Returns:
        Dict mapping bar_name -> {player_name -> total_points}
    """
    if excluded_players is None:
        excluded_players = set()
    
    bar_player_points: BarPlayerPoints = defaultdict(lambda: defaultdict(int))
    
    for round_data in rounds:
        bar_name = round_data.bar_name
        for player_score in round_data.players:
            player_name = player_score.player_name
            
            if player_name not in excluded_players:
                bar_player_points[bar_name][player_name] += player_score.points
    
    return bar_player_points


def _get_top_3_per_bar(
    bar_player_points: BarPlayerPoints
) -> Dict[BarName, List[PlayerQualificationTuple]]:
    """
    Get top 3 qualifiers per bar sorted by points descending.
    
    Returns:
        Dict mapping bar_name -> [(player_name, placement, total_points), ...]
        where placement is 1, 2, or 3
    """
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]] = {}
    
    for bar_name, player_points in bar_player_points.items():
        # Sort players by points descending, then by name for consistent tie-breaking
        sorted_players = sorted(
            player_points.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        # Take top 3 with placement
        top_3 = [
            (player_name, placement, points)
            for placement, (player_name, points) in enumerate(sorted_players[:3], start=1)
        ]
        
        top_3_per_bar[bar_name] = top_3
    
    return top_3_per_bar


def _identify_multi_bar_qualifiers(
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]]
) -> Dict[PlayerName, List[Tuple[BarName, Placement, Points]]]:
    """
    Find players who appear in multiple bars' top 3.
    
    Returns:
        Dict mapping player_name -> [(bar_name, placement, points), ...]
        for players appearing at multiple bars only
    """
    player_qualifications: Dict[PlayerName, List[Tuple[BarName, Placement, Points]]] = defaultdict(list)
    
    for bar_name, qualifiers in top_3_per_bar.items():
        for player_name, placement, points in qualifiers:
            player_qualifications[player_name].append((bar_name, placement, points))
    
    # Return only those qualifying at multiple bars
    return {p: bars for p, bars in player_qualifications.items() if len(bars) > 1}


def _assign_best_bars_for_qualifiers(
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]],
    multi_bar_qualifiers: Dict[PlayerName, List[Tuple[BarName, Placement, Points]]]
) -> Dict[PlayerName, BarName]:
    """
    Lock each player to their best bar, making them unavailable elsewhere.
    
    For multi-bar qualifiers: lock to best placement (1 > 2 > 3), or most points if tied.
    For single-bar qualifiers: assign their only bar.
    
    Returns:
        Dict mapping player_name -> bar_name (the bar they're locked to)
    """
    player_qualified_bar: Dict[PlayerName, BarName] = {}
    
    # All players from top 3 (single-bar qualifiers)
    for bar_name, qualifiers in top_3_per_bar.items():
        for player_name, _, _ in qualifiers:
            if player_name not in multi_bar_qualifiers:
                player_qualified_bar[player_name] = bar_name
    
    # Multi-bar qualifiers: lock to best bar
    for player_name, bar_placements in multi_bar_qualifiers.items():
        best_bar, _, _ = min(
            bar_placements,
            key=lambda x: (x[1], -x[2])  # placement first, then points desc
        )
        player_qualified_bar[player_name] = best_bar
    
    return player_qualified_bar


def _build_initial_qualifiers(
    player_qualified_bar: Dict[PlayerName, BarName],
    bar_player_points: BarPlayerPoints
) -> Tuple[Dict[BarName, List[PlayerQualificationTuple]], Set[PlayerName]]:
    """
    Build initial qualifiers from locked bar assignments.
    
    Only includes players whose best bar is this bar (others are unavailable).
    
    Returns:
        Tuple of (qualifiers, already_assigned) where:
        - qualifiers: bar_name -> [(player_name, placement, points), ...]
        - already_assigned: set of player names already assigned to a bar
    """
    qualifiers: Dict[BarName, List[PlayerQualificationTuple]] = {}
    already_assigned: Set[PlayerName] = set()
    
    for bar_name, player_points in bar_player_points.items():
        # Sort players by points descending
        sorted_by_points = sorted(
            player_points.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        # Take top 3 who are locked to this bar
        bar_qualifiers = []
        for player_name, points in sorted_by_points:
            if len(bar_qualifiers) >= 3:
                break
            
            if player_qualified_bar.get(player_name) == bar_name:
                placement = len(bar_qualifiers) + 1
                bar_qualifiers.append((player_name, placement, points))
                already_assigned.add(player_name)
        
        qualifiers[bar_name] = bar_qualifiers
    
    return qualifiers, already_assigned


def _promote_next_available_players(
    bar_qualifiers: List[PlayerQualificationTuple],
    bar_name: BarName,
    sorted_all_players: List[Tuple[PlayerName, Points]],
    already_assigned: Set[PlayerName],
    player_qualified_bar: Dict[PlayerName, BarName]
) -> List[PlayerQualificationTuple]:
    """
    Promote additional players to fill a bar's qualifier slots (up to 3).
    
    Only promotes players who:
    - Haven't been assigned to another bar
    - Aren't locked to a different bar (either didn't qualify elsewhere OR locked here)
    
    Returns:
        Updated list with promoted players added
    """
    promotions = list(bar_qualifiers)  # Copy existing
    
    for player_name, points in sorted_all_players:
        if len(promotions) >= 3:
            break
        
        # Check if player is available (not locked elsewhere)
        is_available = player_name not in already_assigned
        is_locked_here = player_qualified_bar.get(player_name, bar_name) == bar_name
        
        if is_available and is_locked_here:
            placement = len(promotions) + 1
            promotions.append((player_name, placement, points))
            already_assigned.add(player_name)
    
    return promotions


def _resolve_multi_bar_conflicts(
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]],
    bar_player_points: BarPlayerPoints
) -> Tuple[Dict[BarName, List[PlayerQualificationTuple]], Dict[PlayerName, BarName]]:
    """
    Lock multi-bar qualifiers to their best bar and fill gaps to 3 per bar.
    
    Process:
    1. Identify which players qualified at multiple bars
    2. Lock each multi-bar player to their best bar (making them unavailable elsewhere)
    3. Build initial qualifiers from locked assignments
    4. Promote next-best players (who aren't locked elsewhere) to fill gaps
    
    Returns:
        Tuple of (final_qualifiers, player_qualified_bar) where:
        - final_qualifiers: bar_name -> [(player_name, placement, points), ...]
        - player_qualified_bar: player_name -> bar_name (their locked bar)
    """
    # Step 1: Identify conflicts
    multi_bar_qualifiers = _identify_multi_bar_qualifiers(top_3_per_bar)
    
    # Step 2: Lock to best bar
    player_qualified_bar = _assign_best_bars_for_qualifiers(top_3_per_bar, multi_bar_qualifiers)
    
    # Step 3: Build initial qualifiers from locks
    initial_qualifiers, already_assigned = _build_initial_qualifiers(
        player_qualified_bar, bar_player_points
    )
    
    # Step 4: Promote to fill gaps (respecting locks)
    final_qualifiers: Dict[BarName, List[PlayerQualificationTuple]] = {}
    
    for bar_name, bar_qualifiers in initial_qualifiers.items():
        sorted_all = sorted(
            bar_player_points[bar_name].items(),
            key=lambda x: (-x[1], x[0])
        )
        
        final_qualifiers[bar_name] = _promote_next_available_players(
            bar_qualifiers, bar_name, sorted_all, already_assigned, player_qualified_bar
        )
    
    return final_qualifiers, player_qualified_bar


def _convert_to_dataclass_objects(
    final_qualifiers_tuples: Dict[BarName, List[PlayerQualificationTuple]]
) -> Dict[BarName, List[PlayerQualification]]:
    """
    Convert tuple-based qualifiers to PlayerQualification dataclass objects.
    
    Args:
        final_qualifiers_tuples: bar_name -> [(player_name, placement, points), ...]
    
    Returns:
        bar_name -> [PlayerQualification, ...] objects
    """
    return {
        bar_name: [
            PlayerQualification(
                player_name=player_name,
                placement=placement,
                total_points=points,
                bar_name=bar_name
            )
            for player_name, placement, points in qualifiers
        ]
        for bar_name, qualifiers in final_qualifiers_tuples.items()
    }


def get_qualified_players(
    rounds: List[Round],
    excluded_players: Optional[Set[str]] = None
) -> QualifiedPlayersByBar:
    """
    Calculate tournament qualifiers from round results.
    
    Two-step process:
    1. Calculate top 3 per bar by total points across all rounds
    2. Resolve multi-bar conflicts and fill gaps to exactly 3 per bar
    
    Args:
        rounds: List of Round objects containing player scores
        excluded_players: Set of player names to exclude from qualification
    
    Returns:
        QualifiedPlayersByBar with qualified players organized by bar
    """
    if not rounds:
        return QualifiedPlayersByBar()
    
    if excluded_players is None:
        excluded_players = set()
    
    # Step 1: Aggregate points and get top 3 per bar
    bar_player_points = _aggregate_points_by_bar_and_player(rounds, excluded_players)
    top_3_per_bar = _get_top_3_per_bar(bar_player_points)
    
    # Step 2: Resolve multi-bar conflicts and fill gaps
    final_qualifiers_tuples, _ = _resolve_multi_bar_conflicts(top_3_per_bar, bar_player_points)
    
    # Convert to dataclass objects
    final_qualifiers = _convert_to_dataclass_objects(final_qualifiers_tuples)
    
    return QualifiedPlayersByBar(qualifiers_by_bar=final_qualifiers)
