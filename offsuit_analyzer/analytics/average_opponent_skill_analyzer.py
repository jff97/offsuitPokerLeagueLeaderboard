"""Analyzer for average opponent skill level by player."""
from collections import defaultdict
from typing import List, Dict, Tuple
import pandas as pd
from offsuit_analyzer.datamodel import Round
from . import trueskill_analyzer


def _calculate_final_ratings(rounds: List[Round]) -> Dict[str, float]:
    """
    Calculate final TrueSkill ratings for all players.
    
    Args:
        rounds: List of Round objects to analyze
        
    Returns:
        Dict mapping player_name to conservative skill score (mu - 3*sigma)
    """
    processed_rounds = trueskill_analyzer.prepare_round_data(rounds)
    engine = trueskill_analyzer.TrueSkillEngine()
    engine.process_multiple_rounds(processed_rounds)
    
    return {
        name: rating.mu - 3 * rating.sigma 
        for name, rating in engine.ratings.items()
    }


def _collect_opponent_data(
    rounds: List[Round], 
    final_ratings: Dict[str, float]
) -> Tuple[Dict[str, List[float]], Dict[str, int]]:
    """
    Collect opponent skills and game counts for each player.
    
    Args:
        rounds: List of Round objects to analyze
        final_ratings: Dict mapping player_name to conservative skill score
        
    Returns:
        Tuple of:
        - player_opponent_skills: Dict mapping player to list of opponent skills faced
        - player_round_count: Dict mapping player to number of games played
    """
    player_opponent_skills: Dict[str, List[float]] = defaultdict(list)
    player_round_count: Dict[str, int] = defaultdict(int)
    
    for round_obj in rounds:
        if not round_obj.players or len(round_obj.players) < 2:
            continue
            
        # For each player in this round, add all other players' skills as opponents
        for i, player in enumerate(round_obj.players):
            opponents = [p.player_name for j, p in enumerate(round_obj.players) if i != j]
            for opponent_name in opponents:
                if opponent_name in final_ratings:
                    player_opponent_skills[player.player_name].append(final_ratings[opponent_name])
            # Count this as one game for this player
            player_round_count[player.player_name] += 1
    
    return player_opponent_skills, player_round_count


def _build_leaderboard_records(
    player_opponent_skills: Dict[str, List[float]], 
    player_round_count: Dict[str, int],
    min_rounds_required: int
) -> List[Dict]:
    """
    Build leaderboard records from opponent data.
    
    Args:
        player_opponent_skills: Dict mapping player to list of opponent skills
        player_round_count: Dict mapping player to number of rounds played
        min_rounds_required: Minimum rounds required to be included
        
    Returns:
        List of dicts with player leaderboard data
    """
    records = []
    for player_name, opponent_skills in player_opponent_skills.items():
        rounds_played = player_round_count[player_name]
        if opponent_skills and rounds_played >= min_rounds_required:
            avg_skill = sum(opponent_skills) / len(opponent_skills)
            records.append({
                "Player": player_name,
                "Avg Opponent Skill": round(avg_skill, 2),
                "Rounds Played": rounds_played,
            })
    return records


def _format_leaderboard(records: List[Dict]) -> pd.DataFrame:
    """
    Format and sort leaderboard records.
    
    Args:
        records: List of dicts with player leaderboard data
        
    Returns:
        DataFrame sorted by average opponent skill with implicit ranking
    """
    df = pd.DataFrame(records)
    if not df.empty:
        df.sort_values("Avg Opponent Skill", ascending=False, inplace=True)
        df.reset_index(drop=True, inplace=True)
    return df


def build_average_opponent_skill_leaderboard(rounds: List[Round], min_rounds_required: int) -> pd.DataFrame:
    """
    Build a leaderboard showing each player's average opponent skill level.
    
    Uses current (final) TrueSkill ratings for all players, applying the
    conservative score calculation (mu - 3*sigma) for each opponent faced.
    
    Args:
        rounds: List of Round objects to analyze
        min_rounds_required: Minimum number of games required to be included in leaderboard
        
    Returns:
        DataFrame with columns:
        - Player: Player name
        - Avg Opponent Skill: Average conservative skill of opponents faced
        - Rounds Played: Number of rounds the player participated in
    """
    final_ratings = _calculate_final_ratings(rounds)
    player_opponent_skills, player_round_count = _collect_opponent_data(rounds, final_ratings)
    records = _build_leaderboard_records(player_opponent_skills, player_round_count, min_rounds_required)
    return _format_leaderboard(records)
