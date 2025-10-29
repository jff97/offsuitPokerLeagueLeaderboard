import math
import pandas as pd
from collections import defaultdict
from typing import List
from offsuit_analyzer.datamodel import Round
from config import config


def _calculate_num_paid(num_players: int, payout_percent: float) -> int:
    if num_players <= 0:
        return 0
    return max(2, math.ceil(num_players * payout_percent))


def _generate_normalized_payouts(num_players: int, payout_percent: float, steepness: float) -> List[float]:
    """
    Generate payout fractions summing to 1.0, divided among top N places.
    """
    num_paid = _calculate_num_paid(num_players, payout_percent)
    if num_paid == 0:
        return []

    weights = [1 / (place ** steepness) for place in range(1, num_paid + 1)]
    total_weight = sum(weights)
    payouts = [w / total_weight for w in weights]

    # Correction for rounding
    correction = 1.0 - sum(payouts)
    payouts[0] += correction

    return payouts

def _calculate_net_roi(placement: int, total_players: int, payout_percent: float, steepness: float) -> float:
    """
    Net ROI = (player payout from pool / 1 buy-in) - 1
            = (payout_fraction * total_players) - 1
    """
    payouts = _generate_normalized_payouts(total_players, payout_percent, steepness)
    if placement <= len(payouts):
        payout_from_pool = payouts[placement - 1] * total_players
        return payout_from_pool - 1.0
    return -1.0  # No payout = full loss


def build_roi_leaderboard(rounds: List[Round], min_rounds_required: int, payout_percent: float = config.PERCENT_FOR_ROI, steepness: float = config.STEEPNESS_FOR_ROI) -> pd.DataFrame:
    """
    Build a leaderboard showing each player's average net ROI across rounds.
    ROI is based on share of prize pool versus 1 unit buy-in.
    Output ROI is displayed as a percentage.
    """
    avg_roi_column = "AVG ROI"
    player_totals = defaultdict(lambda: {"TotalNetROI": 0.0, "RoundsPlayed": 0})

    for round_obj in rounds:
        # Sort players by points and calculate ROI based on placement
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        total_players = len(sorted_players)
        
        for index, player in enumerate(sorted_players):
            placement = index + 1  # Simple 1-based index for placement
            net_roi = _calculate_net_roi(placement, total_players, payout_percent, steepness)
            player_totals[player.player_name]["TotalNetROI"] += net_roi
            player_totals[player.player_name]["RoundsPlayed"] += 1

    records = []
    for player, stats in player_totals.items():
        if stats["RoundsPlayed"] >= min_rounds_required:
            avg_net_roi = round((stats["TotalNetROI"] / stats["RoundsPlayed"]) * 100, 2)
            records.append({
                "Player": player,
                avg_roi_column: avg_net_roi,  # Store as number
                "Rounds Played": stats["RoundsPlayed"]
            })

    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values(avg_roi_column, ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
        # Format as percentage after sorting
        df[avg_roi_column] = df[avg_roi_column].apply(lambda x: f"{x:.2f}%")
    return df

