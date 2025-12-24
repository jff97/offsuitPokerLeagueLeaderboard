import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
from typing import List, Dict, Tuple
from offsuit_analyzer.datamodel import Round

# ----------------------------
# Graph Neural Network Model
# ----------------------------
class GraphPlayerRanker(nn.Module):
    """
    Graph neural network that processes all rounds simultaneously.
    Uses player interaction graph to learn transitive rankings.
    """
    def __init__(self, num_players: int, embed_dim: int = 32, hidden_dim: int = 16):
        super().__init__()
        self.num_players = num_players
        
        # Initial player embeddings
        self.player_embedding = nn.Embedding(num_players, embed_dim)
        
        # Graph convolution layers (message passing)
        self.graph_conv1 = nn.Linear(embed_dim, hidden_dim)
        self.graph_conv2 = nn.Linear(hidden_dim, hidden_dim)
        
        # Final scoring layer
        self.scorer = nn.Linear(hidden_dim, 1)
        
    def forward(self, adjacency_matrix: torch.Tensor) -> torch.Tensor:
        """
        Forward pass using graph structure.
        adjacency_matrix: [num_players, num_players] weighted by interactions
        Returns: [num_players] skill scores
        """
        # Get initial embeddings for all players
        player_ids = torch.arange(self.num_players, device=adjacency_matrix.device)
        x = self.player_embedding(player_ids)  # [num_players, embed_dim]
        
        # Graph convolution 1: aggregate neighbor information
        # Normalize adjacency matrix by degree
        degree = adjacency_matrix.sum(dim=1, keepdim=True) + 1e-6
        norm_adj = adjacency_matrix / degree
        
        # Message passing: aggregate features from neighbors
        x = torch.matmul(norm_adj, x)  # [num_players, embed_dim]
        x = torch.relu(self.graph_conv1(x))  # [num_players, hidden_dim]
        
        # Graph convolution 2
        x = torch.matmul(norm_adj, x)
        x = torch.relu(self.graph_conv2(x))  # [num_players, hidden_dim]
        
        # Final scoring
        scores = self.scorer(x).squeeze(-1)  # [num_players]
        return scores


# ----------------------------
# Data Processing
# ----------------------------
def build_interaction_graph(rounds: List[Round]) -> Tuple[torch.Tensor, List[str], Dict[str, int]]:
    """
    Build adjacency matrix from all rounds simultaneously.
    Players who compete together get weighted connections.
    """
    # Get all unique players
    all_players = sorted({p.player_name for r in rounds for p in r.players})
    player_to_id = {name: idx for idx, name in enumerate(all_players)}
    num_players = len(all_players)
    
    # Initialize adjacency matrix: [num_players, num_players]
    # Entry [i,j] = weight of interaction between player i and j
    adjacency = torch.zeros((num_players, num_players))
    
    # Build adjacency from co-occurrences and relative performance
    for round_obj in rounds:
        round_players = [(p.player_name, p.points) for p in round_obj.players]
        
        # Add edges between all players in this round
        for i, (name_i, points_i) in enumerate(round_players):
            player_i = player_to_id[name_i]
            
            for j, (name_j, points_j) in enumerate(round_players):
                if i == j:
                    continue
                    
                player_j = player_to_id[name_j]
                
                # Weight edge by relative performance
                # If player_i beat player_j, add positive weight
                if points_i > points_j:
                    adjacency[player_i, player_j] += 1.0
                elif points_i < points_j:
                    adjacency[player_i, player_j] += 0.5  # Weaker signal for losses
                else:
                    adjacency[player_i, player_j] += 0.7  # Ties
    
    return adjacency, all_players, player_to_id


def build_ranking_matrix(rounds: List[Round], player_to_id: Dict[str, int]) -> torch.Tensor:
    """
    Build matrix of all round rankings for Plackett-Luce loss.
    Returns: [num_rounds, max_players_per_round] tensor of player IDs
    """
    num_players = len(player_to_id)
    
    # Store rankings: list of (round_size, player_ids_in_order)
    round_rankings = []
    
    for round_obj in rounds:
        # Sort players by points (descending)
        sorted_players = sorted(round_obj.players, key=lambda p: p.points, reverse=True)
        player_ids = [player_to_id[p.player_name] for p in sorted_players]
        round_rankings.append(player_ids)
    
    # Pad to max length
    max_len = max(len(r) for r in round_rankings)
    padded_rankings = []
    masks = []
    
    for ranking in round_rankings:
        padded = ranking + [-1] * (max_len - len(ranking))  # -1 for padding
        mask = [1] * len(ranking) + [0] * (max_len - len(ranking))
        padded_rankings.append(padded)
        masks.append(mask)
    
    return torch.tensor(padded_rankings), torch.tensor(masks, dtype=torch.bool)


# ----------------------------
# Plackett-Luce Loss (Matrix Form)
# ----------------------------
def plackett_luce_loss_batch(scores: torch.Tensor, rankings: torch.Tensor, masks: torch.Tensor) -> torch.Tensor:
    """
    Compute Plackett-Luce loss over all rounds simultaneously.
    
    Args:
        scores: [num_players] predicted skill scores
        rankings: [num_rounds, max_len] player IDs in finish order
        masks: [num_rounds, max_len] valid positions (1) vs padding (0)
    
    Returns:
        Scalar loss
    """
    num_rounds, max_len = rankings.shape
    total_loss = torch.tensor(0.0, device=scores.device)
    
    for round_idx in range(num_rounds):
        round_ranking = rankings[round_idx]
        round_mask = masks[round_idx]
        valid_len = round_mask.sum().item()
        
        # Get scores for this round's players
        valid_ids = round_ranking[:valid_len]
        round_scores = scores[valid_ids]
        
        # Plackett-Luce for this round
        exps = torch.exp(round_scores)
        for i in range(valid_len):
            denom = exps[i:].sum()
            total_loss = total_loss + (-torch.log(exps[i] / (denom + 1e-10)))
    
    return total_loss / num_rounds


# ----------------------------
# Training
# ----------------------------
def train_graph_ranker(
    model: nn.Module,
    adjacency: torch.Tensor,
    rankings: torch.Tensor,
    masks: torch.Tensor,
    epochs: int = 50,
    lr: float = 0.01,
    device: torch.device = torch.device('cpu'),
    verbose: bool = True
) -> nn.Module:
    """
    Train the graph ranker using all data simultaneously.
    No round-by-round iteration - processes everything as matrices.
    """
    model = model.to(device)
    adjacency = adjacency.to(device)
    rankings = rankings.to(device)
    masks = masks.to(device)
    
    optimizer = optim.Adam(model.parameters(), lr=lr)
    
    print(f"Training graph ranker with {rankings.shape[0]} rounds, {model.num_players} players")
    print(f"Using device: {device}")
    
    for epoch in range(epochs):
        optimizer.zero_grad()
        
        # Single forward pass through graph for all players
        scores = model(adjacency)  # [num_players]
        
        # Compute loss over all rounds simultaneously
        loss = plackett_luce_loss_batch(scores, rankings, masks)
        
        loss.backward()
        optimizer.step()
        
        if verbose:
            print(f"Epoch {epoch+1:03d}/{epochs} | loss: {loss.item():.4f}")
    
    return model


# ----------------------------
# Public Interface
# ----------------------------
def build_graph_neural_leaderboard(
    rounds: List[Round],
    embed_dim: int = 32,
    hidden_dim: int = 16,
    epochs: int = 50,
    lr: float = 0.01,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Build leaderboard using graph neural network.
    Processes all rounds simultaneously as a matrix.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    # Build graph structure from all rounds
    adjacency, players, player_to_id = build_interaction_graph(rounds)
    rankings, masks = build_ranking_matrix(rounds, player_to_id)
    
    # Create and train model
    model = GraphPlayerRanker(len(players), embed_dim, hidden_dim)
    model = train_graph_ranker(model, adjacency, rankings, masks, epochs, lr, device, verbose)
    
    # Extract final scores
    model.eval()
    with torch.no_grad():
        adjacency = adjacency.to(device)
        final_scores = model(adjacency).cpu()
    
    # Build leaderboard
    player_scores = {players[i]: float(final_scores[i]) for i in range(len(players))}
    sorted_players = sorted(player_scores.items(), key=lambda x: -x[1])
    
    data = [{"Rank": i+1, "Player": name, "Graph Score": round(score, 2)}
            for i, (name, score) in enumerate(sorted_players)]
    
    return pd.DataFrame(data)


def build_filtered_graph_neural_leaderboard(
    rounds: List[Round],
    max_trueskill_uncertainty: float = 4.0,
    embed_dim: int = 32,
    hidden_dim: int = 16,
    epochs: int = 50,
    lr: float = 0.01,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Build graph neural leaderboard filtered by TrueSkill uncertainty.
    """
    from offsuit_analyzer.analytics.trueskill_analyzer import build_trueskill_leaderboard
    
    df_graph = build_graph_neural_leaderboard(rounds, embed_dim, hidden_dim, epochs, lr, verbose)
    df_trueskill = build_trueskill_leaderboard(rounds)
    
    allowed_players = set(
        df_trueskill[df_trueskill['Uncertainty'] <= max_trueskill_uncertainty]['Name'].tolist()
    )
    
    df_filtered = df_graph[df_graph['Player'].isin(allowed_players)].copy()
    df_filtered['Rank'] = range(1, len(df_filtered) + 1)
    df_filtered.reset_index(drop=True, inplace=True)
    
    return df_filtered
