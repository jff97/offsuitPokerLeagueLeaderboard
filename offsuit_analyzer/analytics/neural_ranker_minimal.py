import torch
import torch.nn as nn
import torch.optim as optim
import random
import json
import pandas as pd
from typing import List, Dict, Tuple
from offsuit_analyzer.datamodel import Round


# ----------------------------
# Neural Model
# ----------------------------
class _RoundRanker(nn.Module):
    """Neural network for learning player rankings from tournament results."""
    
    def __init__(self, num_players: int, embed_dim: int = 16):
        super().__init__()
        self.embedding = nn.Embedding(num_players, embed_dim)
        self.scorer = nn.Linear(embed_dim, 1)

    def forward(self, player_ids: torch.Tensor) -> torch.Tensor:
        embeds = self.embedding(player_ids)
        scores = self.scorer(embeds).squeeze(-1)
        return scores


# ----------------------------
# Private Helper Functions
# ----------------------------
def _convert_rounds_to_ranking_format(rounds: List[Round]) -> List[List[str]]:
    """
    Convert Round objects to ranking format.
    
    Args:
        rounds: List of Round objects
        
    Returns:
        List of player name lists, sorted by points (descending)
    """
    ranking_rounds = []
    for round_obj in rounds:
        sorted_players = sorted(
            round_obj.players,
            key=lambda p: p.points,
            reverse=True
        )
        player_names = [p.player_name for p in sorted_players]
        ranking_rounds.append(player_names)
    return ranking_rounds


def _build_player_index(rounds: List[List[str]]) -> Tuple[List[str], Dict[str, int]]:
    """
    Build player index from rounds data.
    
    Args:
        rounds: List of rounds with player names
        
    Returns:
        Tuple of (sorted player names, player_name -> id mapping)
    """
    players = sorted({p for r in rounds for p in r})
    player_to_id = {p: i for i, p in enumerate(players)}
    return players, player_to_id


def _listwise_loss(scores: torch.Tensor) -> torch.Tensor:
    """
    Compute Plackett-Luce loss for ranking.
    
    Args:
        scores: Predicted scores in order of actual placements
        
    Returns:
        Negative log likelihood loss
    """
    exps = torch.exp(scores)
    loss = 0.0
    for i in range(len(scores)):
        denom = exps[i:].sum()
        loss += -torch.log(exps[i] / denom)
    return loss


def _train_model(
    model: _RoundRanker,
    rounds: List[List[str]],
    player_to_id: Dict[str, int],
    epochs: int = 100,
    learning_rate: float = 0.01,
    verbose: bool = False
) -> _RoundRanker:
    """
    Train the ranking model.
    
    Args:
        model: The neural ranking model
        rounds: List of rounds with player names in ranking order
        player_to_id: Mapping from player names to IDs
        epochs: Number of training epochs
        learning_rate: Learning rate for optimizer
        verbose: Whether to print training progress
        
    Returns:
        Trained model
    """
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    for epoch in range(epochs):
        total_loss = 0.0
        random.shuffle(rounds)
        
        for r in rounds:
            ids = torch.tensor([player_to_id[p] for p in r])
            optimizer.zero_grad()
            scores = model(ids)
            loss = _listwise_loss(scores)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        
        if verbose:
            avg_loss = total_loss / len(rounds)
            print(f"Epoch {epoch+1:03d} | avg round loss {avg_loss:.4f}")
    
    return model


def _extract_player_scores(
    model: _RoundRanker,
    players: List[str],
    num_players: int
) -> Dict[str, float]:
    """
    Extract learned scores for all players.
    
    Args:
        model: Trained ranking model
        players: List of player names
        num_players: Total number of players
        
    Returns:
        Dictionary mapping player names to their scores
    """
    with torch.no_grad():
        all_ids = torch.arange(num_players)
        final_scores = model(all_ids).cpu().detach().numpy()
    
    return {player: float(score) for player, score in zip(players, final_scores)}


# ----------------------------
# Public Interface
# ----------------------------
def build_neural_ranking_leaderboard(
    rounds: List[Round],
    epochs: int = 100,
    embed_dim: int = 16,
    learning_rate: float = 0.01,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Build a leaderboard ranking players using neural network analysis.
    
    Args:
        rounds: List of Round objects containing tournament results
        epochs: Number of training epochs
        embed_dim: Dimension of player embeddings
        learning_rate: Learning rate for training
        verbose: Whether to print training progress
        
    Returns:
        DataFrame with columns: Rank, Player, Neural Score
    """
    # Convert rounds to ranking format
    ranking_rounds = _convert_rounds_to_ranking_format(rounds)
    
    # Build player index
    players, player_to_id = _build_player_index(ranking_rounds)
    
    # Create and train model
    model = _RoundRanker(len(players), embed_dim=embed_dim)
    model = _train_model(model, ranking_rounds, player_to_id, epochs, learning_rate, verbose)
    
    # Extract scores
    player_scores = _extract_player_scores(model, players, len(players))
    
    # Sort by score (descending) and build DataFrame
    sorted_players = sorted(player_scores.items(), key=lambda x: -x[1])
    
    data = []
    for rank, (player, score) in enumerate(sorted_players, start=1):
        data.append({
            "Rank": rank,
            "Player": player,
            "Neural Score": round(score, 2)
        })
    
    return pd.DataFrame(data)


def build_filtered_neural_ranking_leaderboard(
    rounds: List[Round],
    max_trueskill_uncertainty: float = 4.0,
    epochs: int = 100,
    embed_dim: int = 16,
    learning_rate: float = 0.01,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Build neural ranking leaderboard filtered by TrueSkill uncertainty.
    
    Args:
        rounds: List of Round objects containing tournament results
        max_trueskill_uncertainty: Maximum allowed TrueSkill uncertainty (sigma)
        epochs: Number of training epochs
        embed_dim: Dimension of player embeddings
        learning_rate: Learning rate for training
        verbose: Whether to print training progress
        
    Returns:
        DataFrame with columns: Rank, Player, Neural Score (filtered)
    """
    from offsuit_analyzer.analytics.trueskill_analyzer import build_trueskill_leaderboard
    
    # Get both leaderboards
    df_neural = build_neural_ranking_leaderboard(rounds, epochs, embed_dim, learning_rate, verbose)
    df_trueskill = build_trueskill_leaderboard(rounds)
    
    # Get players with acceptable uncertainty
    allowed_players = set(
        df_trueskill[df_trueskill['Uncertainty'] <= max_trueskill_uncertainty]['Name'].tolist()
    )
    
    # Filter neural rankings
    df_filtered = df_neural[df_neural['Player'].isin(allowed_players)].copy()
    
    # Re-rank after filtering
    df_filtered['Rank'] = range(1, len(df_filtered) + 1)
    df_filtered.reset_index(drop=True, inplace=True)
    
    return df_filtered
