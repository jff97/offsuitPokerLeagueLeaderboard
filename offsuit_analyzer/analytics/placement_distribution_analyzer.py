import numpy as np
from scipy.stats import gaussian_kde
from collections import defaultdict
from typing import List, Dict, Any
from offsuit_analyzer.datamodel import Round


def _calculate_percentile_finish(placement: int, total_players: int) -> float:
    """
    Convert a placement into a percentile (0 to 1).
    1.0 means 1st place (best), 0.0 means last place (worst).
    """
    if total_players <= 1:
        return 1.0
    return 1 - (placement - 1) / (total_players - 1)


def _generate_kde_curve(percentiles: List[float], num_points: int = 50) -> List[Dict[str, float]]:
    """
    Generate a smooth KDE curve from percentile data.
    Returns a list of {x, y} points suitable for charting.
    """
    if len(percentiles) < 2:
        # Not enough data for KDE, return uniform distribution
        return [{"x": i / (num_points - 1), "y": 1.0} for i in range(num_points)]
    
    # Create KDE
    kde = gaussian_kde(percentiles, bw_method='scott')
    
    # Generate x points from 0 to 1
    x_points = np.linspace(0, 1, num_points)
    
    # Calculate density at each point
    y_points = kde(x_points)
    
    # Return as list of dicts
    return [{"x": round(x, 4), "y": round(y, 4)} for x, y in zip(x_points, y_points)]


def build_placement_distribution_for_all_players(rounds: List[Round], min_rounds_required: int = 5) -> List[Dict[str, Any]]:
    """
    Calculate KDE distribution curves for all players.
    Returns a list of player data with their placement distribution curves.
    """
    player_percentiles = defaultdict(list)
    
    # Collect percentile finishes for each player
    for round_obj in rounds:
        # Sort players by points to determine placements
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        total_players = len(sorted_players)
        
        for placement, player in enumerate(sorted_players, 1):
            percentile = _calculate_percentile_finish(placement, total_players)
            player_percentiles[player.player_name].append(percentile)
    
    # Build result list
    result = []
    for player_name, percentiles in player_percentiles.items():
        if len(percentiles) >= min_rounds_required:
            kde_data = _generate_kde_curve(percentiles)
            result.append({
                "playerName": player_name,
                "roundsPlayed": len(percentiles),
                "kdeData": kde_data
            })
    
    # Sort by rounds played (descending) for consistency
    result.sort(key=lambda x: x["roundsPlayed"], reverse=True)
    
    return result
