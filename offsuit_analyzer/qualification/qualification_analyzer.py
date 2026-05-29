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

# Saturday to Friday week order in Python weekday format (Monday=0, Sunday=6)
WEEK_DAY_ORDER = [5, 6, 0, 1, 2, 3, 4]  # Sat, Sun, Mon, Tue, Wed, Thu, Fri


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


def _get_weekday_from_date(date_str: str) -> int:
    """
    Extract day of week from YYYY-MM-DD date string.
    Returns weekday as 0=Monday through 6=Sunday.
    """
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        return date_obj.weekday()
    except (ValueError, TypeError):
        return -1


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


def _resolve_multi_bar_conflicts(
    top_3_per_bar: Dict[BarName, List[PlayerQualificationTuple]],
    bar_player_points: BarPlayerPoints
) -> Dict[BarName, List[PlayerQualificationTuple]]:
    """
    Resolve players who qualify at multiple bars (Step 2).
    
    Rules:
    - If a player qualifies at different placements, they take best placement (1 > 2 > 3)
    - If same placement at multiple bars, they take the one with more points
    - Other bars get promoted players from their remaining list
    
    Returns:
        Dict mapping bar_name -> [(player_name, placement, total_points), ...]
    """
    # Build map: player -> [(bar_name, placement, points), ...]
    player_qualifications: Dict[PlayerName, List[PlayerQualificationTuple]] = defaultdict(list)
    
    for bar_name, qualifiers in top_3_per_bar.items():
        for player_name, placement, points in qualifiers:
            player_qualifications[player_name].append((bar_name, placement, points))
    
    # For each player, determine which bar they take (if multi-qualified)
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
    
    # Rebuild top 3 per bar with promotions
    resolved_qualifiers: Dict[BarName, List[PlayerQualificationTuple]] = {}
    
    for bar_name, player_points in bar_player_points.items():
        # Sort all players at this bar
        sorted_all_players = sorted(
            player_points.items(),
            key=lambda x: (-x[1], x[0])
        )
        
        # Fill 3 spots with only players who chose this bar
        bar_qualifiers = []
        for player_name, points in sorted_all_players:
            if len(bar_qualifiers) >= 3:
                break
            
            if player_chosen_bar.get(player_name) == bar_name:
                placement = len(bar_qualifiers) + 1
                bar_qualifiers.append((player_name, placement, points))
        
        resolved_qualifiers[bar_name] = bar_qualifiers
    
    return resolved_qualifiers


def _apply_chronological_lock_in(
    rounds: List[Round],
    resolved_qualifiers: Dict[BarName, List[PlayerQualificationTuple]],
    bar_player_points: BarPlayerPoints
) -> Dict[BarName, List[PlayerQualification]]:
    """
    Apply chronological lock-in (Step 3).
    
    Players who qualify earlier in the week (Sat-Thu) are locked in and 
    excluded from later bars, allowing promotions. Ensures each bar gets exactly 3 qualifiers.
    
    Returns:
        Dict mapping bar_name -> [qualified_players] (3 per bar)
    """
    # Track players who have already qualified
    already_qualified: Set[PlayerName] = set()
    
    # Final qualifiers - will be filled incrementally
    final_qualifiers: Dict[BarName, List[PlayerQualification]] = {}
    
    # Process each day in week order (Sat-Thu)
    for weekday in WEEK_DAY_ORDER:
        if weekday > 3:  # Thu is 3, skip Fri (4)
            continue
        
        # Process ALL bars on this day (not just ones with rounds that day)
        for bar_name, resolved_top_3 in resolved_qualifiers.items():
            # Skip if we already finalized this bar
            if bar_name in final_qualifiers:
                continue
            
            # Filter resolved top 3, removing already-qualified players
            available_qualifiers = [
                (player_name, points)
                for player_name, _, points in resolved_top_3
                if player_name not in already_qualified
            ]
            
            # If we don't have 3 yet, promote from remaining players at this bar
            if len(available_qualifiers) < 3:
                # Get all players at this bar sorted by total points
                all_players_at_bar = sorted(
                    bar_player_points[bar_name].items(),
                    key=lambda x: (-x[1], x[0])
                )
                
                # Add players who aren't already qualified and not already selected
                already_selected = {name for name, _ in available_qualifiers}
                for player_name, points in all_players_at_bar:
                    if player_name not in already_qualified and player_name not in already_selected:
                        available_qualifiers.append((player_name, points))
                    
                    if len(available_qualifiers) >= 3:
                        break
            
            # Take exactly 3 and add to finals
            bar_qualifiers = []
            for placement, (player_name, points) in enumerate(available_qualifiers[:3], start=1):
                bar_qualifiers.append(
                    PlayerQualification(
                        player_name=player_name,
                        placement=placement,
                        total_points=points,
                        bar_name=bar_name
                    )
                )
                # Lock in this player
                already_qualified.add(player_name)
            
            final_qualifiers[bar_name] = bar_qualifiers
    
    return final_qualifiers


def get_qualified_players(
    rounds: List[Round],
    excluded_players: Optional[Set[str]] = None
) -> QualifiedPlayersByBar:
    """
    Calculate tournament qualifiers from round results.
    
    Three-step process:
    1. Calculate top 3 per bar across all rounds (simultaneous)
    2. Resolve multi-bar conflicts (best placement or most points)
    3. Apply chronological lock-in (early qualifiers exclude later bars)
    
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
    
    # Step 1: Aggregate all points and get top 3 per bar
    bar_player_points = _aggregate_points_by_bar_and_player(rounds, excluded_players)
    top_3_per_bar = _get_top_3_per_bar(bar_player_points)
    
    # Step 2: Resolve multi-bar conflicts
    resolved_qualifiers = _resolve_multi_bar_conflicts(top_3_per_bar, bar_player_points)
    
    # Step 3: Apply chronological lock-in
    final_qualifiers = _apply_chronological_lock_in(rounds, resolved_qualifiers, bar_player_points)
    
    return QualifiedPlayersByBar(qualifiers_by_bar=final_qualifiers)
