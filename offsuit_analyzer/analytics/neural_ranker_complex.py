import torch
import torch.nn as nn
import torch.optim as optim
import random
import pandas as pd
from typing import List, Dict, Tuple
from offsuit_analyzer.datamodel import Round

# ----------------------------
# Neural Model
# ----------------------------
class LatentRoundRanker(nn.Module):
    """
    Neural network for learning latent player features from tournament results.
    Allows AI to discover patterns without predefined assumptions.
    """
    def __init__(self, num_players: int, embed_dim: int = 16, latent_dim: int = 8):
        super().__init__()
        # Each player has a learnable embedding
        self.embedding = nn.Embedding(num_players, embed_dim)
        # Map embedding to latent features (multi-dimensional)
        self.latent = nn.Linear(embed_dim, latent_dim)
        # Map latent features to a score used for ranking
        self.scorer = nn.Linear(latent_dim, 1)

    def forward(self, player_ids: torch.Tensor) -> torch.Tensor:
        embeds = self.embedding(player_ids)
        latent_feats = torch.tanh(self.latent(embeds))  # non-linear latent features
        scores = self.scorer(latent_feats).squeeze(-1)
        return scores

# ----------------------------
# Loss Function
# ----------------------------
def plackett_luce_loss(scores: torch.Tensor) -> torch.Tensor:
    """
    Plackett-Luce listwise ranking loss for a round.
    """
    exps = torch.exp(scores)
    loss = 0.0
    for i in range(len(scores)):
        denom = exps[i:].sum()
        loss += -torch.log(exps[i] / denom)
    return loss

# ----------------------------
# Helpers
# ----------------------------
def build_player_index(rounds: List[List[str]]) -> Tuple[List[str], Dict[str, int]]:
    players = sorted({p for r in rounds for p in r})
    player_to_id = {p: i for i, p in enumerate(players)}
    return players, player_to_id

def extract_scores(model: nn.Module, players: List[str], num_players: int) -> Dict[str, float]:
    with torch.no_grad():
        all_ids = torch.arange(num_players)
        scores = model(all_ids)
        return {player: float(score) for player, score in zip(players, scores)}

# ----------------------------
# Training
# ----------------------------
def train_ranker(
    model: nn.Module,
    rounds: List[List[str]],
    player_to_id: Dict[str, int],
    epochs: int = 100,
    lr: float = 0.01,
    verbose: bool = False
) -> nn.Module:
    optimizer = optim.Adam(model.parameters(), lr=lr)
    for epoch in range(epochs):
        total_loss = 0.0
        random.shuffle(rounds)
        for r in rounds:
            ids = torch.tensor([player_to_id[p] for p in r])
            optimizer.zero_grad()
            scores = model(ids)
            loss = plackett_luce_loss(scores)
            loss.backward()
            optimizer.step()
            total_loss += loss.item()
        if verbose:
            print(f"Epoch {epoch+1:03d} | avg round loss {total_loss / len(rounds):.4f}")
    return model

# ----------------------------
# Public Interface
# ----------------------------
def build_latent_leaderboard(
    rounds: List[Round],
    epochs: int = 100,
    embed_dim: int = 16,
    latent_dim: int = 8,
    lr: float = 0.01,
    verbose: bool = False
) -> pd.DataFrame:
    # Convert rounds to ranking format
    ranking_rounds = []
    for r in rounds:
        sorted_players = sorted(r.players, key=lambda p: p.points, reverse=True)
        ranking_rounds.append([p.player_name for p in sorted_players])

    # Build player index
    players, player_to_id = build_player_index(ranking_rounds)

    # Create and train model
    model = LatentRoundRanker(len(players), embed_dim=embed_dim, latent_dim=latent_dim)
    model = train_ranker(model, ranking_rounds, player_to_id, epochs, lr, verbose)

    # Extract scores
    player_scores = extract_scores(model, players, len(players))

    # Build DataFrame
    sorted_players = sorted(player_scores.items(), key=lambda x: -x[1])
    data = [{"Rank": i+1, "Player": p, "Latent Score": round(s, 2)}
            for i, (p, s) in enumerate(sorted_players)]
    return pd.DataFrame(data)


def build_filtered_latent_leaderboard(
    rounds: List[Round],
    max_trueskill_uncertainty: float = 5.0,
    epochs: int = 100,
    embed_dim: int = 16,
    latent_dim: int = 8,
    lr: float = 0.01,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Build latent neural ranking leaderboard filtered by TrueSkill uncertainty.
    
    Args:
        rounds: List of Round objects containing tournament results
        max_trueskill_uncertainty: Maximum allowed TrueSkill uncertainty (sigma)
        epochs: Number of training epochs
        embed_dim: Dimension of player embeddings
        latent_dim: Dimension of latent feature space
        lr: Learning rate for training
        verbose: Whether to print training progress
        
    Returns:
        DataFrame with columns: Rank, Player, Latent Score (filtered)
    """
    from offsuit_analyzer.analytics.trueskill_analyzer import build_trueskill_leaderboard
    
    # Get both leaderboards
    df_latent = build_latent_leaderboard(rounds, epochs, embed_dim, latent_dim, lr, verbose)
    df_trueskill = build_trueskill_leaderboard(rounds)
    
    # Get players with acceptable uncertainty
    allowed_players = set(
        df_trueskill[df_trueskill['Uncertainty'] <= max_trueskill_uncertainty]['Name'].tolist()
    )
    
    # Filter latent rankings
    df_filtered = df_latent[df_latent['Player'].isin(allowed_players)].copy()
    
    # Re-rank after filtering
    df_filtered['Rank'] = range(1, len(df_filtered) + 1)
    df_filtered.reset_index(drop=True, inplace=True)
    
    return df_filtered
