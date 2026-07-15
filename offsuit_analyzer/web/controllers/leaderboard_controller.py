from flask import Blueprint, Response, request, jsonify
from ..services import leaderboard_service 

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/players-outlasted')
def players_outlasted():
    players_outlasted_dataframe = leaderboard_service.get_players_outlasted_leaderboard()
    
    return players_outlasted_dataframe.to_json(orient="records")

@leaderboard_bp.route('/roi')
def roi():
    min_rounds = request.args.get('min_rounds', type=int, default=None)
    roi_leaderboard_dataframe = leaderboard_service.get_roi_leaderboard(min_rounds=min_rounds)
    return roi_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/trueskill')
def trueskill():
    trueskill_leaderboard_dataframe = leaderboard_service.get_trueskill_leaderboard()
    return trueskill_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/average-opponent-skill')
def average_opponent_skill():
    """
    Get leaderboard showing average opponent skill faced by each player.
    
    Uses current TrueSkill ratings (conservative score: mu - 3*sigma) for all players.
    Calculates the average skill of all opponents a player has faced across all rounds.
    
    Returns:
        JSON array of players with their average opponent skill level
    """
    avg_opponent_skill_dataframe = leaderboard_service.get_average_opponent_skill_leaderboard()
    return avg_opponent_skill_dataframe.to_json(orient="records")

@leaderboard_bp.route('/firstplace')
def firstplace():
    first_place_leaderboard_dataframe = leaderboard_service.get_first_place_leaderboard()
    return first_place_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/itmpercent')
def itmpercent():
    top_percentile_leaderboard_dataframe = leaderboard_service.get_itm_percentage_leaderboard()
    return top_percentile_leaderboard_dataframe.to_json(orient="records")

# DISABLED: Player graph visualization removed for deployment size optimization
# @leaderboard_bp.route('/network-graph')
# def network_graph():
#     """
#     Generate and return a player network graph visualization.
#     Shows player connections colored by TrueSkill ratings.
#     Query parameter: player_name - highlights the specified player in blue
#     """
#     searched_player_name = request.args.get('player_name')
#     img_buffer = leaderboard_service.get_network_graph_image(searched_player_name)
#     
#     return Response(
#         img_buffer.getvalue(),
#         mimetype='image/png',
#         headers={
#             'Content-Disposition': 'inline; filename="player_network.png"',
#             'Cache-Control': 'public, max-age=3600'  # Cache for 1 hour
#         }
#     )

# DISABLED: Community detection removed for deployment size optimization
# @leaderboard_bp.route('/community-disconnectedness')
# def community_disconnectedness():
#     disconnectedness_df = leaderboard_service.get_community_disconnectedness_analysis()
#     return disconnectedness_df.to_json(orient="records")

@leaderboard_bp.route('/placement-distributions')
def placement_distributions():
    """
    Get KDE distribution curves for all players' placement patterns.
    Shows how each player's finishes are distributed across percentiles.
    """
    distributions = leaderboard_service.get_placement_distributions()
    return jsonify(distributions)

@leaderboard_bp.route('/this-months-top-point-players', methods=['GET'])
def this_months_top_point_players_endpoint():
    """
    Endpoint to retrieve the top point players for the current month.
    
    Returns only rounds currently visible in the API (current month).
    No parameters required.
    """
    top_players = leaderboard_service.get_this_months_top_point_players()
    return top_players.to_json(orient="records")

@leaderboard_bp.route('/years-top-point-players', methods=['GET'])
def years_top_point_players_endpoint():
    """
    Endpoint to retrieve the top point players for a specific year.
    
    Query Parameters (required):
        - year: int (e.g., 2025)
    """
    year_param = request.args.get('year')

    if not year_param:
        return jsonify({"error": "Missing required query parameter: year"}), 400
    
    try:
        year = int(year_param)
    except ValueError:
        return jsonify({"error": "year must be a valid integer"}), 400
    
    top_players = leaderboard_service.get_years_top_point_players(year)
    return top_players.to_json(orient="records")

@leaderboard_bp.route('/average-game-size-by-player', methods=['GET'])
def average_game_size_by_player():
    """
    Get the average number of players in games for each unique player.
    
    For each player, calculates the average size (number of players) of all games they participated in.
    
    Returns:
        JSON array of players with their average game size
    """
    result = leaderboard_service.get_average_game_size_by_player()
    return result.to_json(orient="records")

@leaderboard_bp.route('/bar-average-players', methods=['GET'])
def bar_average_players():
    """
    Get the average number of players for each bar.
    
    Filters to bars with more than 4 rounds and excludes bars with 'legacy' in the name.
    
    Returns:
        JSON array of bars with their average player count and rounds played
    """
    result = leaderboard_service.get_bar_average_players_leaderboard()
    return result.to_json(orient="records")

@leaderboard_bp.route('/bar-average-trueskill', methods=['GET'])
def bar_average_trueskill():
    """
    Get the average trueskill score for each bar.
    
    Calculates the average trueskill rating across all player appearances at each bar.
    Filters to bars with more than 4 rounds and excludes bars with 'legacy' in the name.
    
    Returns:
        JSON array of bars with their average trueskill score and rounds played
    """
    result = leaderboard_service.get_bar_average_trueskill_leaderboard()
    return result.to_json(orient="records")

