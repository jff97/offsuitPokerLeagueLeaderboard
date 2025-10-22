import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer import analytics
import io

# ===============================
# GRAPH CONSTRUCTION & VISUALIZATION
# ===============================

def build_player_graph(rounds: List[Round]) -> nx.Graph:
    G = nx.Graph()
    for rnd in rounds:
        players = [p.player_name for p in rnd.players]
        for p1, p2 in combinations(players, 2):
            if G.has_edge(p1, p2):
                G[p1][p2]['weight'] += 1
            else:
                G.add_edge(p1, p2, weight=1)
    return G

def generate_graph_image_buffer(rounds: List[Round], searched_player_name: str = None, title: str = "Player Interaction Graph") -> io.BytesIO:
    G = build_player_graph(rounds)
    _prepare_graph_plot(G, rounds, searched_player_name, title)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=115, bbox_inches='tight')
    buf.seek(0)
    plt.close()
    return buf


def _create_multiline_labels(nodes) -> dict:
    labels = {}
    for node in nodes:
        name_parts = node.split(' ')
        labels[node] = name_parts[0] + '\n' + ' '.join(name_parts[1:]) if len(name_parts) > 1 else node
    return labels


def _get_player_trueskill_colors(rounds: List[Round], nodes, special_player_name: str = None) -> list:
    trueskill_df = analytics.build_trueskill_leaderboard(rounds)
    skill_map = {}

    if not trueskill_df.empty:
        name_col = next((c for c in ['Player', 'Name'] if c in trueskill_df.columns), None)
        rating_col = 'Adjusted Ranking' if 'Adjusted Ranking' in trueskill_df.columns else 'Raw Ranking'
        if name_col:
            for _, row in trueskill_df.iterrows():
                skill_map[row[name_col]] = row[rating_col]

    if skill_map:
        vals = list(skill_map.values())
        min_skill, max_skill = min(vals), max(vals)
        colormap = plt.cm.RdYlGn

        colors = []
        for node in nodes:
            if node in skill_map:
                normalized = (skill_map[node] - min_skill) / (max_skill - min_skill) if max_skill != min_skill else 0.5
                color = colormap(normalized)
                if special_player_name and node == special_player_name:
                    color = 'blue'
                colors.append(color)
            else:
                colors.append('lightgray')
        return colors
    else:
        return ['skyblue'] * len(nodes)


def _prepare_graph_plot(G: nx.Graph, rounds: List[Round], searched_player_name: str = None, title: str = "Player Interaction Graph") -> None:
    pos = nx.spring_layout(G, weight="weight", k=5.0, iterations=200, seed=42)
    plt.figure(figsize=(48, 48))
    node_colors = _get_player_trueskill_colors(rounds, G.nodes(), searched_player_name)
    nx.draw_networkx_nodes(G, pos, node_size=245, node_color=node_colors, edgecolors="black")
    labels = _create_multiline_labels(G.nodes())
    nx.draw_networkx_labels(G, pos, labels, font_size=4, font_weight="bold")
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.4, edge_color="gray")
    plt.title(f"{title}\n(Red=Lower Skill, Green=Higher Skill)", fontsize=20)
    plt.axis("off")
    plt.tight_layout()


