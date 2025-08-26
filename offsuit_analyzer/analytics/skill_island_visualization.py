import networkx as nx
import matplotlib.pyplot as plt
from itertools import combinations
from typing import List
from offsuit_analyzer.datamodel import Round
from offsuit_analyzer import analytics
import io

# Increase PIL's image size limit to handle large graphs
# Image.MAX_IMAGE_PIXELS = 300000000  # Allow up to 300 million pixels


def build_player_graph(rounds: List[Round]) -> nx.Graph:
    """
    Build a weighted undirected graph from a list of Round objects.
    Nodes = players, edges = times they've played together.
    """
    G = nx.Graph()

    for rnd in rounds:
        players = [p.player_name for p in rnd.players]
        for p1, p2 in combinations(players, 2):
            if G.has_edge(p1, p2):
                G[p1][p2]['weight'] += 1
            else:
                G.add_edge(p1, p2, weight=1)
    return G


def _create_multiline_labels(nodes) -> dict:
    """
    Create multi-line labels by splitting player names.
    Splits on space and puts first name on first line, rest on second line.
    """
    labels = {}
    for node in nodes:
        name_parts = node.split(' ')
        if len(name_parts) > 1:
            # Put first name on first line, last name on second line
            labels[node] = name_parts[0] + '\n' + ' '.join(name_parts[1:])
        else:
            labels[node] = node
    return labels


def _get_player_trueskill_colors(rounds: List[Round], nodes, special_player_name: str) -> List[str]:
    """
    Get colors for players based on their TrueSkill ratings.
    Returns a list of colors corresponding to the skill levels.
    """
    # Get trueskill leaderboard
    trueskill_df = analytics.build_trueskill_leaderboard(rounds)
    
    # Create a mapping of player names to their trueskill ratings
    skill_map = {}
    if not trueskill_df.empty:
        # Look for player name column (could be 'Player' or 'Name')
        name_col = None
        for col in ['Player', 'Name']:
            if col in trueskill_df.columns:
                name_col = col
                break
        
        # Use Adjusted Ranking (conservative) instead of Raw Ranking (unnormalized)
        rating_col = 'Adjusted Ranking' if 'Adjusted Ranking' in trueskill_df.columns else 'Raw Ranking'
        
        if name_col and rating_col:
            for _, row in trueskill_df.iterrows():
                player_name = row[name_col]
                skill_value = row[rating_col]
                skill_map[player_name] = skill_value
    
    # If we have skill data, normalize and color accordingly
    if skill_map:
        skill_values = list(skill_map.values())
        min_skill = min(skill_values)
        max_skill = max(skill_values)
        
        # Create colormap from red (low skill) to green (high skill)
        colormap = plt.cm.RdYlGn
        
        colors = []
        for node in nodes:
            if node in skill_map:
                # Normalize skill value to 0-1 range
                normalized_skill = (skill_map[node] - min_skill) / (max_skill - min_skill) if max_skill != min_skill else 0.5
                color = colormap(normalized_skill)
                if special_player_name is not None and node == special_player_name:
                    color = 'blue'
                colors.append(color)
            else:
                # Default color for players not in trueskill data
                colors.append('lightgray')
        
        return colors
    else:
        # Default to skyblue if no trueskill data available
        return ['skyblue'] * len(nodes)


def _prepare_graph_plot(G: nx.Graph, rounds: List[Round], searched_player_name: str, title: str) -> None:
    """
    Helper function that prepares the graph plot but doesn't show or save it.
    Sets up the figure, layout, colors, labels, and drawing.
    """
    pos = nx.spring_layout(G, weight="weight", k=5.0, iterations=200, seed=42)

    # Square figure canvas - same width and height
    plt.figure(figsize=(48, 48))  # Square canvas
    
    # Get trueskill-based colors
    node_colors = _get_player_trueskill_colors(rounds, G.nodes(), searched_player_name)
    
    # Keep node size the same - they'll look smaller on the bigger canvas
    nx.draw_networkx_nodes(G, pos, node_size=245, node_color=node_colors, edgecolors="black")
    
    # Create multi-line labels by splitting names
    labels = _create_multiline_labels(G.nodes())
    
    # Simple fixed font size
    nx.draw_networkx_labels(G, pos, labels, font_size=4, font_weight="bold")

    # Draw all edges the same width (closeness is handled by layout)
    nx.draw_networkx_edges(G, pos, width=0.5, alpha=0.4, edge_color="gray")

    plt.title(f"{title}\n(Red=Lower Skill, Green=Higher Skill)", fontsize=20)
    plt.axis("off")
    plt.tight_layout()

def visualize_graph(G: nx.Graph, rounds: List[Round], searched_player_name: str, title: str = "Player Interaction Graph") -> None:
    """
    Visualize the player graph using a spring layout and display it.
    """
    _prepare_graph_plot(G, rounds, searched_player_name, title)
    plt.show()

def generate_graph_image_buffer(G: nx.Graph, rounds: List[Round], searched_player_name: str, title: str = "Player Interaction Graph") -> io.BytesIO:
    """
    Generate the player graph visualization as a BytesIO buffer.
    Returns a buffer that can be saved to file or returned from API.
    """
    _prepare_graph_plot(G, rounds, searched_player_name, title)
    
    # Create a BytesIO buffer to hold the image
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=100, bbox_inches='tight')
    img_buffer.seek(0)  # Reset buffer pointer to beginning
    plt.close()  # Close the figure to free memory
    
    return img_buffer

def generate_rounds_image_buffer(rounds: List[Round], searched_player_name: str, title: str) -> io.BytesIO:
    """
    Convenience function: build graph from rounds and generate as BytesIO buffer.
    Returns a buffer that can be saved to file or returned from API.
    """
    G = build_player_graph(rounds)
    return generate_graph_image_buffer(G, rounds, searched_player_name, title)

def plot_rounds(rounds: List[Round], searched_player_name: str, title: str) -> None:
    """
    Convenience function: build and visualize graph from rounds.
    """
    G = build_player_graph(rounds)
    visualize_graph(G, rounds, searched_player_name, title)

if __name__ == "__main__":
    from offsuit_analyzer import persistence
    rounds = persistence.get_all_rounds()
    
    # Generate image buffer
    img_buffer = generate_rounds_image_buffer(rounds, searched_player_name="bob", title="Player Network - TrueSkill Colored")
    
    # Save buffer to file
    with open("player_network_trueskill.png", "wb") as f:
        f.write(img_buffer.getvalue())
    print("Network graph saved as 'player_network_trueskill.png'")
    
    # Also show the interactive plot
    plot_rounds(rounds, searched_player_name="bob", title="Player Network - TrueSkill Colored")
