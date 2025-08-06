from flask import Blueprint, Response, request
from ..services.leaderboard_service import (
    get_placement_leaderboard,
    get_percentile_leaderboard,
    get_roi_leaderboard,
    get_trueskill_leaderboard
)

leaderboard_bp = Blueprint('leaderboard', __name__, url_prefix='/api/leaderboard')

@leaderboard_bp.route('/placement')
def placement():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    placement_leaderboard_dataframe = get_placement_leaderboard(min_rounds_required)
    return placement_leaderboard_dataframe.to_json(orient="records")

@leaderboard_bp.route('/placement/html')
def placement_html():
    min_rounds_required = int(request.args.get('minrounds') or 0)
    placement_leaderboard_dataframe = get_placement_leaderboard(min_rounds_required)
    return Response(f"<pre>{placement_leaderboard_dataframe.to_string(index=False)}</pre>", mimetype='text/html')

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
