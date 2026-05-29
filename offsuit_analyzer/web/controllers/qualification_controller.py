"""Qualification API controller - exposes tournament qualifier endpoints."""
from flask import Blueprint, request, jsonify
from ..services import qualification_service

qualification_bp = Blueprint('qualification', __name__, url_prefix='/api/qualification')


@qualification_bp.route('/tournament-qualifiers', methods=['GET'])
def get_tournament_qualifiers():
    """
    Get tournament qualifiers for this month's league season.
    
    Returns top 3 point holders from each bar, with players taking their
    best placement if they qualify at multiple bars.
    
    Query Parameters:
        excluded_players: Comma-separated list of player names to exclude
    
    Returns:
        JSON object with bar names as keys and arrays of qualifiers as values.
        Each qualifier has: player_name, placement (1-3), total_points
    """
    excluded_players_param = request.args.get('excluded_players')
    qualified_players = qualification_service.get_tournament_qualifiers(excluded_players_param)
    return jsonify(qualified_players.to_dict())
