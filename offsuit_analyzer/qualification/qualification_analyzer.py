"""Qualification analyzer - determines tournament qualifiers from round results."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
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
    Aggregate total points for each player at each bar.
    
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


def _resolve_multi_bar_qualifications(
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]]
) -> Dict[BarName, List[PlayerQualification]]:
    """
    Resolve multi-bar qualifications according to rules.
    
    If a player qualifies at multiple bars:
    1. They take the spot where they have the best placement (1st > 2nd > 3rd)
    2. If same placement at multiple bars, they take the one with more points
    3. Other bars get the next-best available player
    
    Returns:
        Dict mapping bar_name -> [qualified_players]
    """
    # Build map: player -> list of (bar_name, placement, points) they qualified at
    player_qualifications: Dict[PlayerName, List[PlayerQualificationTuple]] = defaultdict(list)
    
    for bar_name, qualifiers in top_3_per_bar.items():
        for player_name, placement, points in qualifiers:
            player_qualifications[player_name].append((bar_name, placement, points))
    
    # For each player, determine which bar they'll take their spot at
    player_chosen_bar: Dict[PlayerName, BarName] = {}
    
    for player_name, bar_placements in player_qualifications.items():
        if len(bar_placements) == 1:
            # Only qualifies at one bar
            player_chosen_bar[player_name] = bar_placements[0][0]
        else:
            # Qualifies at multiple bars - choose best by placement, then by points
            best_bar, best_placement, best_points = min(
                bar_placements,
                key=lambda x: (x[1], -x[2])  # placement first, then points desc
            )
            player_chosen_bar[player_name] = best_bar
    
    # Rebuild qualifiers by bar, only including players who chose that bar
    final_qualifiers: Dict[BarName, List[PlayerQualification]] = defaultdict(list)
    
    for bar_name, qualifiers in top_3_per_bar.items():
        for player_name, placement, points in qualifiers:
            # Only include if player chose this bar
            if player_chosen_bar.get(player_name) == bar_name:
                final_qualifiers[bar_name].append(
                    PlayerQualification(
                        player_name=player_name,
                        placement=placement,
                        total_points=points,
                        bar_name=bar_name
                    )
                )
    
    return dict(final_qualifiers)


def get_qualified_players(
    rounds: List[Round],
    excluded_players: Optional[Set[str]] = None
) -> QualifiedPlayersByBar:
    """
    Calculate tournament qualifiers from round results.
    
    Determines top 3 total point holders from each bar. Handles multi-bar
    qualifications by having each player take their best spot.
    
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
    
    # Step 1: Aggregate points by bar and player
    bar_player_points = _aggregate_points_by_bar_and_player(rounds, excluded_players)
    
    # Step 2: Get top 3 per bar
    top_3_per_bar = _get_top_3_per_bar(bar_player_points)
    
    # Step 3: Resolve multi-bar qualifications
    final_qualifiers = _resolve_multi_bar_qualifications(top_3_per_bar)
    
    return QualifiedPlayersByBar(qualifiers_by_bar=final_qualifiers)
