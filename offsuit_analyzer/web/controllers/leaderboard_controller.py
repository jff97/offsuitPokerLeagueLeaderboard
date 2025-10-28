from flask import Blueprint, Response, request
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

@leaderboard_bp.route('/network-graph')
def network_graph():
    """
    Generate and return a player network graph visualization.
    Shows player connections colored by TrueSkill ratings.
    Query parameter: player_name - highlights the specified player in blue
    """
    searched_player_name = request.args.get('player_name')
    img_buffer = leaderboard_service.get_network_graph_image(searched_player_name)
    
    return Response(
        img_buffer.getvalue(),
        mimetype='image/png',
        headers={
            'Content-Disposition': 'inline; filename="player_network.png"',
            'Cache-Control': 'public, max-age=3600'  # Cache for 1 hour
        }
    )

@leaderboard_bp.route('/community-disconnectedness')
def community_disconnectedness():
    disconnectedness_df = leaderboard_service.get_community_disconnectedness_analysis()
    return disconnectedness_df.to_json(orient="records")