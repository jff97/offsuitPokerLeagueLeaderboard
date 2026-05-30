from flask import Blueprint, Response, request, jsonify
from ..services import leaderboard_service 

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/players-outlasted')
def players_outlasted():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    players_outlasted_dataframe = leaderboard_service.get_players_outlasted_leaderboard(min_rounds_required)
    
    return players_outlasted_dataframe.to_json(orient="records")

@leaderboard_bp.route('/roi')
def roi():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    roi_leaderboard_dataframe = leaderboard_service.get_roi_leaderboard(min_rounds_required)
    return roi_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/trueskill')
def trueskill():
    trueskill_leaderboard_dataframe = leaderboard_service.get_trueskill_leaderboard()
    return trueskill_leaderboard_dataframe.to_json(orient="records")

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
    Query parameter: minrounds - minimum rounds required (default from config)
    """
    min_rounds_required = int(request.args.get('minrounds') or 0)
    distributions = leaderboard_service.get_placement_distributions(min_rounds_required)
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

