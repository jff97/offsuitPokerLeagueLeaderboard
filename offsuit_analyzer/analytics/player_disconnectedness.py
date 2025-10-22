import networkx as nx
import pandas as pd
import numpy as np
from typing import List
import community as community_louvain
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer import analytics


def compute_disconnectedness_leaderboard_df(G: nx.Graph) -> pd.DataFrame:
    def edge_length(u, v, d):
        w = d.get('weight', 1.0)
        return 1.0 / w if w > 0 else 1e9

    nodes = list(G.nodes())
    n = len(nodes)
    farness = {}

    for u in nodes:
        lengths = nx.single_source_dijkstra_path_length(G, u, weight=edge_length)
        if len(lengths) < n:
            big = max(lengths.values()) * 10 if lengths else 1e6
            all_lengths = [lengths.get(v, big) for v in nodes]
        else:
            all_lengths = [lengths[v] for v in nodes]
        farness[u] = sum(all_lengths) / (n - 1)

    vals = np.array(list(farness.values()), dtype=float)
    mn, mx = vals.min(), vals.max()
    norm = {k: 0.0 for k in farness} if mx == mn else {k: (v - mn) / (mx - mn) for k, v in farness.items()}
    df = pd.DataFrame(list(norm.items()), columns=["Player", "Disconnectedness"])
    return df.sort_values("Disconnectedness", ascending=False).reset_index(drop=True)


def compute_community_labels(G: nx.Graph) -> pd.DataFrame:
    partition = community_louvain.best_partition(G, weight='weight', resolution=1.3)
    df = pd.DataFrame(list(partition.items()), columns=['Player', 'CommunityID'])
    return df.sort_values(['CommunityID', 'Player']).reset_index(drop=True)


def add_avg_disconnectedness_to_communities(disconnectedness_df: pd.DataFrame,
                                                   communities_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add average disconnectedness to community dataframe, keep each player's disconnectedness,
    sort communities by highest average disconnectedness, and sort players within each community
    by their disconnectedness descending.

    Args:
        disconnectedness_df: DataFrame with ['Player', 'Disconnectedness']
        communities_df: DataFrame with ['Player', 'CommunityID']

    Returns:
        DataFrame with columns ['Player', 'CommunityID', 'Disconnectedness', 'AvgDisconnectedness']
        sorted as described.
    """
    # Merge disconnectedness into communities
    merged_df = communities_df.merge(disconnectedness_df, on='Player', how='left')
    
    # Compute average disconnectedness per community
    avg_disc = merged_df.groupby('CommunityID')['Disconnectedness'].mean().rename('AvgDisconnectedness')
    merged_df['AvgDisconnectedness'] = merged_df['CommunityID'].map(avg_disc)
    
    # Sort first by community AvgDisconnectedness descending, then by player disconnectedness descending
    merged_df = merged_df.sort_values(['AvgDisconnectedness', 'Disconnectedness'],
                                      ascending=[False, False])
    
    return merged_df[['Player', 'CommunityID', 'Disconnectedness', 'AvgDisconnectedness']]



# ===============================
# TEST FUNCTIONS (RETURN DATA)
# ===============================

def get_player_disconnectedness_df(rounds: List[Round]) -> pd.DataFrame:
    G = analytics.build_player_graph(rounds)
    return compute_disconnectedness_leaderboard_df(G)


def get_community_detection_df(rounds: List[Round]) -> pd.DataFrame:
    G = analytics.build_player_graph(rounds)
    return compute_community_labels(G)

def get_community_avg_disconnectedness_df(rounds: List[Round]) -> pd.DataFrame:
    G = analytics.build_player_graph(rounds)
    disc_df = compute_disconnectedness_leaderboard_df(G)
    comm_df = compute_community_labels(G)
    return add_avg_disconnectedness_to_communities(disc_df, comm_df)

def print_community_disconnectedness_over_time(rounds: List[Round], num_slices: int = 5):
    """
    Print the community average disconnectedness leaderboards for cumulative time subsets.
    
    Each slice includes all previous rounds (cumulative growth).
    """
    if not rounds:
        print("No rounds provided.")
        return

    # --- Sort chronologically ---
    rounds_sorted = sorted(rounds, key=lambda r: r.round_date)
    n = len(rounds_sorted)
    step = max(1, n // num_slices)
    cutoffs = [min(n, step * i) for i in range(1, num_slices + 1)]

    print("\n=== Community Avg Disconnectedness by Cumulative Slice ===")

    for idx, cutoff in enumerate(cutoffs, start=1):
        subset = rounds_sorted[:cutoff]
        if not subset:
            continue

        G = analytics.build_player_graph(subset)
        disc_df = compute_disconnectedness_leaderboard_df(G)
        comm_df = compute_community_labels(G)
        merged_df = add_avg_disconnectedness_to_communities(disc_df, comm_df)

        print(f"\n--- Slice {idx} (First {cutoff} rounds) ---")
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(merged_df)


def top_three_trueskill_rounds_avg(rounds: list[Round]) -> list[dict]:
    """
    Return the top 3 rounds with the highest average Adjusted Ranking (mu - 3*sigma) among all players,
    showing round date, bar name, and the average score.
    """
    trueskill_df = analytics.build_trueskill_leaderboard(rounds)

    # Map player name -> adjusted ranking
    player_adj = {row['Name']: row['Adjusted Ranking'] for _, row in trueskill_df.iterrows()}

    # Compute each round's average Adjusted Ranking
    round_scores = []
    for rnd in rounds:
        estimates = [player_adj.get(p.player_name, float('-inf')) for p in rnd.players]
        if estimates:
            avg_score = sum(estimates) / len(estimates)
            round_scores.append((rnd, avg_score))

    # Sort descending by average score and take top 3
    round_scores.sort(key=lambda x: x[1], reverse=True)
    top3 = round_scores[:3]

    # Return round date, bar name, and average score
    return [
        {"round_date": r[0].round_date, "bar_name": r[0].bar_name, "avg_adjusted_ranking": r[1]}
        for r in top3
    ]



# ===============================
# DRIVER
# ===============================

if __name__ == "__main__":
    from offsuit_analyzer import persistence
    rounds = persistence.get_all_rounds()

    #1
    # print("\nMost Disconnected Players:")
    # disconnected_df = test_disconnectedness(rounds)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(disconnected_df)

    #2
    # print("\nPlayer Communities (Skill Islands):")
    # communities_df = test_community_detection(rounds)
    # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     print(communities_df)

    #3
    print("\nCommunity Avg Disconnectedness:")
    community_avg_df = get_community_avg_disconnectedness_df(rounds)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(community_avg_df)
    
    #4
    #analyze_disconnectedness_drift(rounds)
    
    #5
    #print_community_disconnectedness_over_time(rounds)
    
    #6
    #print(top_three_trueskill_rounds_avg(rounds))
