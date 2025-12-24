import torch
import torch.nn as nn
import torch.optim as optim
import random
import pandas as pd
from typing import List, Dict, Callable, Tuple
from offsuit_analyzer.datamodel import Round

# ----------------------------
# Neural Model
# ----------------------------
class MultiRewardRanker(nn.Module):
    """Neural network to learn player skills with adaptive reward weights."""
    def __init__(self, num_players: int, embed_dim: int = 16, latent_dim: int = 8, reward_names: List[str] = None):
        super().__init__()
        self.embedding = nn.Embedding(num_players, embed_dim)
        self.latent = nn.Linear(embed_dim, latent_dim)
        self.scorer = nn.Linear(latent_dim, 1)

        # Adaptive reward weights (learnable)
        self.reward_weights = nn.ParameterDict()
        if reward_names is None:
            reward_names = ['plackett_luce', 'upset', 'stability']  # removed 'interaction'
        for r in reward_names:
            self.reward_weights[r] = nn.Parameter(torch.tensor(1.0))

    def forward(self, player_ids: torch.Tensor) -> torch.Tensor:
        embeds = self.embedding(player_ids)
        latent_feats = torch.tanh(self.latent(embeds))
        scores = self.scorer(latent_feats).squeeze(-1)
        return scores

# ----------------------------
# Reward Functions
# ----------------------------
def plackett_luce_loss(scores: torch.Tensor) -> torch.Tensor:
    exps = torch.exp(scores)
    loss = torch.tensor(0.0, device=scores.device)
    for i in range(len(scores)):
        denom = exps[i:].sum()
        loss = loss + (-torch.log(exps[i] / denom))
    return loss

def upset_reward(scores: torch.Tensor) -> torch.Tensor:
    reward = torch.tensor(0.0, device=scores.device)
    for i in range(len(scores)):
        for j in range(i+1, len(scores)):
            reward = reward + torch.relu(scores[j] - scores[i])
    return reward / (len(scores) + 1e-6)

def stability_penalty(scores_history: Dict[int, List[float]], device: torch.device = torch.device('cpu')) -> torch.Tensor:
    penalty = torch.tensor(0.0, device=device)
    for scores in scores_history.values():
        if len(scores) > 1:
            score_tensor = torch.tensor(scores, device=device)
            mean = torch.mean(score_tensor)
            penalty = penalty + torch.mean((score_tensor - mean) ** 2)
    return penalty

def interaction_reward(scores: torch.Tensor) -> torch.Tensor:
    reward = torch.tensor(0.0, device=scores.device)
    for i in range(len(scores)):
        for j in range(i+1, len(scores)):
            reward = reward + (scores[i] - scores[j]) ** 2
    return reward / len(scores)

# ----------------------------
# Helpers
# ----------------------------
def build_player_index(rounds: List[List[str]]) -> Tuple[List[str], Dict[str, int]]:
    players = sorted({p for r in rounds for p in r})
    player_to_id = {p: i for i, p in enumerate(players)}
    return players, player_to_id

def extract_scores(model: nn.Module, players: List[str]) -> Dict[str, float]:
    device = next(model.parameters()).device
    with torch.no_grad():
        all_ids = torch.arange(len(players)).to(device)
        scores = model(all_ids)
        return {player: float(score) for player, score in zip(players, scores)}

# ----------------------------
# Training
# ----------------------------
def train_ranker(
    model: nn.Module,
    ranking_rounds: List[List[str]],
    player_to_id: Dict[str, int],
    reward_fns: Dict[str, Callable],
    epochs: int = 10,
    lr: float = 0.01,
    verbose: bool = True
) -> nn.Module:
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    model = model.to(device)
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scores_history: Dict[int, List[float]] = {i: [] for i in player_to_id.values()}

    reward_names = list(reward_fns.keys())

    for epoch in range(epochs):
        total_loss = 0.0
        random.shuffle(ranking_rounds)

        for r in ranking_rounds:
            ids = torch.tensor([player_to_id[p] for p in r]).to(device)
            optimizer.zero_grad()
            scores = model(ids)

            # Compute rewards separately
            rewards = {}
            rewards['plackett_luce'] = plackett_luce_loss(scores)
            rewards['upset'] = upset_reward(scores)
            # interaction_reward removed - it penalizes score differences, causing all players to tie
            # rewards['interaction'] = interaction_reward(scores)
            rewards['stability'] = stability_penalty(scores_history, device)

            # Normalize rewards to avoid magnitude domination
            normalized_rewards = {}
            for k, v in rewards.items():
                normalized_rewards[k] = v / (v.abs().detach() + 1e-6)

            # Use softmax on weights so they sum to 1 (prevents shrinking to zero)
            weight_keys = list(normalized_rewards.keys())
            weight_tensor = torch.stack([model.reward_weights[k] for k in weight_keys])
            softmax_weights = torch.nn.functional.softmax(weight_tensor, dim=0)
            
            # Weighted sum of rewards
            final_loss = sum(softmax_weights[i] * normalized_rewards[weight_keys[i]] 
                             for i in range(len(weight_keys)))

            final_loss.backward()
            optimizer.step()
            total_loss += final_loss.item()

            # Track history for stability
            for i, pid in enumerate(ids):
                scores_history[int(pid)].append(float(scores[i].detach()))

        if verbose:
            # Show softmax-normalized weights (sum to 1)
            weight_keys = list(model.reward_weights.keys())
            weight_tensor = torch.stack([model.reward_weights[k] for k in weight_keys])
            softmax_weights = torch.nn.functional.softmax(weight_tensor, dim=0)
            weight_snapshot = {k: float(softmax_weights[i].detach()) for i, k in enumerate(weight_keys)}
            print(f"Epoch {epoch+1:03d} | avg batch loss {total_loss/len(ranking_rounds):.4f} | weights: {weight_snapshot}")

    return model

# ----------------------------
# Public Interface
# ----------------------------
def build_adaptive_multi_reward_leaderboard(
    rounds: List[Round],
    embed_dim: int = 16,
    latent_dim: int = 8,
    epochs: int = 10,
    lr: float = 0.01,
    verbose: bool = True
) -> pd.DataFrame:
    ranking_rounds = []
    for r in rounds:
        sorted_players = sorted(r.players, key=lambda p: p.points, reverse=True)
        ranking_rounds.append([p.player_name for p in sorted_players])

    players, player_to_id = build_player_index(ranking_rounds)
    model = MultiRewardRanker(len(players), embed_dim=embed_dim, latent_dim=latent_dim)

    reward_fns = {
        'plackett_luce': plackett_luce_loss,
        'upset': upset_reward,
        'interaction': interaction_reward,
        'stability': stability_penalty
    }

    model = train_ranker(model, ranking_rounds, player_to_id, reward_fns, epochs, lr, verbose)
    player_scores = extract_scores(model, players)

    sorted_players = sorted(player_scores.items(), key=lambda x: -x[1])
    data = [{"Rank": i+1, "Player": p, "Latent Score": round(s, 2)}
            for i, (p, s) in enumerate(sorted_players)]
    return pd.DataFrame(data)


def build_filtered_adaptive_multi_reward_leaderboard(
    rounds: List[Round],
    max_trueskill_uncertainty: float = 4.0,
    embed_dim: int = 16,
    latent_dim: int = 8,
    epochs: int = 10,
    lr: float = 0.01,
    verbose: bool = True
) -> pd.DataFrame:
    """
    Build adaptive multi-reward leaderboard filtered by TrueSkill uncertainty.
    """
    from offsuit_analyzer.analytics.trueskill_analyzer import build_trueskill_leaderboard

    df_adaptive = build_adaptive_multi_reward_leaderboard(rounds, embed_dim, latent_dim, epochs, lr, verbose)
    df_trueskill = build_trueskill_leaderboard(rounds)

    allowed_players = set(
        df_trueskill[df_trueskill['Uncertainty'] <= max_trueskill_uncertainty]['Name'].tolist()
    )
    df_filtered = df_adaptive[df_adaptive['Player'].isin(allowed_players)].copy()
    df_filtered['Rank'] = range(1, len(df_filtered) + 1)
    df_filtered.reset_index(drop=True, inplace=True)
    return df_filtered

