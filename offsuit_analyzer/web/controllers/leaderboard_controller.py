from flask import Blueprint, Response, request
from ..services.leaderboard_service import (
    get_percentile_leaderboard,
    get_roi_leaderboard,
    get_trueskill_leaderboard,
    get_first_place_leaderboard,
    get_itm_percentage_leaderboard,
    get_network_graph_image
)

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/percentile')
def percentile():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    percentile_leaderboard_dataframe = get_percentile_leaderboard(min_rounds_required)
    
    return percentile_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/percentile/html')
def percentile_html():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    percentile_leaderboard_dataframe = get_percentile_leaderboard(min_rounds_required)
    return Response(f"<pre>{percentile_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/roi')
def roi():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    roi_leaderboard_dataframe = get_roi_leaderboard(min_rounds_required)
    return roi_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/roi/html')
def roi_html():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    roi_leaderboard_dataframe = get_roi_leaderboard(min_rounds_required)
    return Response(f"<pre>{roi_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/trueskill')
def trueskill():
    trueskill_leaderboard_dataframe = get_trueskill_leaderboard()
    return trueskill_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/trueskill/html')
def trueskil_html():
    trueskill_leaderboard_dataframe = get_trueskill_leaderboard()
    html_from_dataframe = trueskill_leaderboard_dataframe.to_string(index=False)
    return Response(f"<pre>{html_from_dataframe}</pre>", mimetype='text/html')

@leaderboard_bp.route('/firstplace')
def firstplace():
    first_place_leaderboard_dataframe = get_first_place_leaderboard()
    return first_place_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/firstplace/html')
def firstplace_html():
    first_place_leaderboard_dataframe = get_first_place_leaderboard()
    return Response(f"<pre>{first_place_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/itmpercent')
def itmpercent():
    top_percentile_leaderboard_dataframe = get_itm_percentage_leaderboard()
    return top_percentile_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/itmpercent/html')
def itmpercent_html():
    top_percentile_leaderboard_dataframe = get_itm_percentage_leaderboard()
    return Response(f"<pre>{top_percentile_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

@leaderboard_bp.route('/network-graph')
def network_graph():
    """
    Generate and return a player network graph visualization.
    Shows player connections colored by TrueSkill ratings.
    Query parameter: player_name - highlights the specified player in blue
    """
    searched_player_name = request.args.get('player_name')
    img_buffer = get_network_graph_image(searched_player_name)
    
    return Response(
        img_buffer.getvalue(),
        mimetype='image/png',
        headers={
            'Content-Disposition': 'inline; filename="player_network.png"',
            'Cache-Control': 'public, max-age=3600'  # Cache for 1 hour
        }
    )
