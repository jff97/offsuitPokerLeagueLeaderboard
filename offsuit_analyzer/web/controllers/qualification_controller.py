"""Qualification API controller - exposes tournament qualifier endpoints."""
from flask import Blueprint, request, jsonify, Response
import json
from ..decorators import require_admin_password
from ..services import qualification_service

qualification_bp = Blueprint('qualification', __name__, url_prefix='/api/qualification')


@qualification_bp.route('/tournament-qualifiers', methods=['GET'])
def get_tournament_qualifiers():
    """
    Get tournament qualifiers for this month's league season.
    
    Returns top 3 point holders from each bar, with players taking their
    best placement if they qualify at multiple bars.
    
    Exclusions are managed via the /api/qualification/unavailable-players endpoint.
    
    Returns:
        JSON object with bar names as keys and arrays of qualifiers as values.
        Each qualifier has: player_name, placement (1-3), total_points
    """
    qualified_players = qualification_service.get_tournament_qualifiers()
    return jsonify(qualified_players.to_dict())


@qualification_bp.route('/unavailable-players', methods=['GET'])
@require_admin_password
def get_unavailable_players():
    """
    Get the list of players currently excluded from qualification this month.
    
    Requires admin password.
    
    Returns:
        JSON array of player names currently excluded from qualification
        401 Unauthorized if password is invalid
    """
    try:
        # Get excluded players
        excluded = qualification_service.get_unavailable_players()
        return Response(
            json.dumps(sorted(list(excluded))),
            status=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype="application/json"
        )


@qualification_bp.route('/unavailable-players', methods=['POST'])
@require_admin_password
def update_unavailable_players():
    """
    Update the list of excluded players for this month.
    
    This is a full sync operation: the provided list becomes the complete
    set of excluded players. Anyone not in the list is un-excluded.
    
    Requires admin password.
    
    Request body:
    {
        "password": "<admin password>",
        "unavailable_players": ["alice", "bob", ...]
    }
    
    Returns:
        JSON with status and updated list on success
        401 Unauthorized if password is invalid
    """
    try:
        data = request.get_json()
        
        # Validate request has JSON
        if not data:
            return Response(
                json.dumps({"error": "Request body must be valid JSON"}),
                status=400,
                mimetype="application/json"
            )
        
        # Get the new exclusion list
        unavailable_players = data.get('unavailable_players', [])
        if not isinstance(unavailable_players, list):
            return Response(
                json.dumps({"error": "unavailable_players must be a list"}),
                status=400,
                mimetype="application/json"
            )
        
        # Update unavailable players and refresh frontend
        qualification_service.update_unavailable_players(unavailable_players)
        
        return Response(
            json.dumps({
                "status": "ok",
                "unavailable_players": sorted(unavailable_players)
            }),
            status=200,
            mimetype="application/json"
        )
    
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype="application/json"
        )
