import json
import math
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict


# ============================================================
# CONFIG
# ============================================================

FILE_PATH = r"C:\Users\jicfo\Downloads\20260602_rounds_export\20260602rounds_export.json"

PAYOUT_PERCENT = 0.24
STEPPING = 1.06

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


# ============================================================
# ROI FUNCTION (power law payout)
# ============================================================

def compute_roi(place: int, field_size: int) -> float:

    num_paid = max(1, math.ceil(field_size * PAYOUT_PERCENT))

    if place > num_paid:
        return -1.0

    weights = [
        1.0 / (p ** STEPPING)
        for p in range(1, num_paid + 1)
    ]

    total = sum(weights)
    payouts = [w / total for w in weights]

    payout = payouts[place - 1] * field_size

    return float(payout - 1.0)


# ============================================================
# LOAD DATA
# ============================================================

with open(FILE_PATH, "r", encoding="utf-8") as f:
    tournaments = json.load(f)


# ============================================================
# PLAYER INDEX
# ============================================================

players = set()

for t in tournaments:
    for p in t["players"]:
        players.add(p["player_name"].lower())

player_to_id = {p: i for i, p in enumerate(sorted(players))}
id_to_player = {i: p for p, i in player_to_id.items()}

num_players = len(player_to_id)


# ============================================================
# BUILD PAIRWISE DATASET
# ============================================================

pairs = []

for t in tournaments:

    sorted_players = sorted(
        t["players"],
        key=lambda x: x["points"],
        reverse=True
    )

    field_size = len(sorted_players)

    enriched = []

    for place, p in enumerate(sorted_players, start=1):

        name = p["player_name"].lower()
        roi = compute_roi(place, field_size)

        enriched.append((name, place, roi))

    # pairwise comparisons
    for i in range(len(enriched)):
        for j in range(i + 1, len(enriched)):

            name_i, place_i, roi_i = enriched[i]
            name_j, place_j, roi_j = enriched[j]

            a = player_to_id[name_i]
            b = player_to_id[name_j]

            if place_i < place_j:
                winner, loser = a, b
            else:
                winner, loser = b, a

            roi_diff = abs(roi_i - roi_j)

            pairs.append((winner, loser, roi_diff))


print(f"Total training pairs: {len(pairs):,}")


# ============================================================
# MODEL
# ============================================================

class SkillModel(nn.Module):

    def __init__(self, num_players):
        super().__init__()

        self.skill = nn.Embedding(num_players, 1)

        nn.init.uniform_(self.skill.weight, -0.01, 0.01)

    def forward(self, a, b):
        return (self.skill(a).squeeze() - self.skill(b).squeeze())


model = SkillModel(num_players).to(DEVICE)


# ============================================================
# TRAINING SETUP
# ============================================================

optimizer = torch.optim.Adam(model.parameters(), lr=0.01)


def softplus_loss(logits):
    return F.softplus(-logits)


EPOCHS = 75
BATCH_SIZE = 4096


def get_batch(batch):
    w = torch.tensor([x[0] for x in batch], dtype=torch.long, device=DEVICE)
    l = torch.tensor([x[1] for x in batch], dtype=torch.long, device=DEVICE)
    wt = torch.tensor([x[2] for x in batch], dtype=torch.float32, device=DEVICE)
    return w, l, wt


# ============================================================
# TRAIN LOOP
# ============================================================

for epoch in range(EPOCHS):

    random.shuffle(pairs)

    total_loss = 0.0

    for i in range(0, len(pairs), BATCH_SIZE):

        batch = pairs[i:i + BATCH_SIZE]

        w, l, weight = get_batch(batch)

        logits = model(w, l)

        loss = softplus_loss(logits)

        loss = (loss * weight).sum() / (weight.sum() + 1e-8)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"Epoch {epoch+1}/{EPOCHS} - loss: {total_loss:.4f}")


# ============================================================
# COUNT PLAYER GAMES (FOR FILTERING ONLY AT OUTPUT)
# ============================================================

player_games = defaultdict(int)

for t in tournaments:
    for p in t["players"]:
        name = p["player_name"].lower()
        if name in player_to_id:
            player_games[name] += 1


# ============================================================
# EXTRACT RANKING
# ============================================================

with torch.no_grad():
    skills = model.skill.weight.squeeze().cpu().numpy()

ranking = list(enumerate(skills))
ranking.sort(key=lambda x: x[1], reverse=True)


print("\n=== GLOBAL SKILL RANKING (50+ games only) ===\n")

rank_pos = 1

for pid, score in ranking:

    name = id_to_player[pid]

    if player_games[name] < 80:
        continue

    print(f"{rank_pos:3d}. {name:20s} {score:.4f}")
    rank_pos += 1