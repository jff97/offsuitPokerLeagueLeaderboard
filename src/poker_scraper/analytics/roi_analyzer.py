import math
import pandas as pd
from collections import defaultdict
from typing import List, Dict, Any
from ..datamodel import Round, PlayerScore


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


def _rank_players_in_each_round(rounds: List[Round]) -> List[Dict[str, Any]]:
    """
    Rank players in each round by points and assign placement (handle ties).
    Return list of dicts with Player, RoundID, BarName, Placement, and PlayerCount.
    """
    ranked_results = []

    for round_obj in rounds:
        players_sorted = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        point_to_place = {}
        for idx, player in enumerate(players_sorted):
            if player.points not in point_to_place:
                point_to_place[player.points] = idx + 1

        for player in players_sorted:
            placement = point_to_place[player.points]
            ranked_results.append({
                "Player": player.player_name,
                "RoundID": round_obj.round_id,
                "BarName": round_obj.bar_name,
                "Placement": placement,
                "PlayerCount": len(players_sorted)
            })

    return ranked_results


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


def build_roi_leaderboard(
    rounds: List[Round],
    payout_percent: float = 0.18,
    steepness: float = 1.1,
    min_rounds_required: int = 14
) -> pd.DataFrame:
    """
    Build a leaderboard showing each player's average net ROI across rounds.
    ROI is based on share of prize pool versus 1 unit buy-in.
    Output ROI is displayed as a percentage.
    """
    ranked_results = _rank_players_in_each_round(rounds)
    player_totals = defaultdict(lambda: {"TotalNetROI": 0.0, "RoundsPlayed": 0})

    for result in ranked_results:
        net_roi = _calculate_net_roi(result["Placement"], result["PlayerCount"], payout_percent, steepness)
        player = result["Player"]
        player_totals[player]["TotalNetROI"] += net_roi
        player_totals[player]["RoundsPlayed"] += 1

    records = []
    for player, stats in player_totals.items():
        if stats["RoundsPlayed"] >= min_rounds_required:
            avg_net_roi = stats["TotalNetROI"] / stats["RoundsPlayed"]
            records.append({
                "Player": player,
                "AVG ROI per Round (%)": round(avg_net_roi * 100, 2),
                "RoundsPlayed": stats["RoundsPlayed"]
                
            })

    df = pd.DataFrame(records)
    if df.empty:
        df = pd.DataFrame([["No players met the minimum round requirement"]], columns=["Message"])
    else:
        df.sort_values(by="AVG ROI per Round (%)", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)

    return df

