"""Qualification API controller - exposes tournament qualifier endpoints."""
from flask import Blueprint, request, jsonify, Response
import json
from offsuit_analyzer.config import config
from ..services import qualification_service, admin_service
from offsuit_analyzer.persistence import excluded_qualifiers_collection

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
def get_unavailable_players():
    """
    Get the list of players currently excluded from qualification this month.
    
    Query parameters or request body:
    {
        "password": "<admin password>"
    }
    
    Returns:
        JSON array of player names currently excluded from qualification
        401 Unauthorized if password is invalid
    """
    try:
        # Try to get password from JSON body first, then from query parameters
        data = request.get_json(silent=True) or {}
        password = data.get('password') or request.args.get('password')
        
        # Validate password
        if password != config.OFFSUIT_ADMIN_PASSWORD:
            return Response(
                json.dumps({"error": "Invalid password"}),
                status=401,
                mimetype="application/json"
            )
        
        # Get excluded players
        excluded = excluded_qualifiers_collection.get_excluded_players()
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
def update_unavailable_players():
    """
    Update the list of excluded players for this month.
    
    This is a full sync operation: the provided list becomes the complete
    set of excluded players. Anyone not in the list is un-excluded.
    
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
        
        # Validate password
        if data.get('password') != config.OFFSUIT_ADMIN_PASSWORD:
            return Response(
                json.dumps({"error": "Invalid password"}),
                status=401,
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
        
        # Update the collection (this replaces the entire list)
        excluded_qualifiers_collection.set_excluded_players(set(unavailable_players))
        
        # Trigger frontend update to refresh leaderboard caches
        success, message, _ = admin_service.trigger_frontend_update()
        if not success:
            print(f"Warning: Failed to trigger frontend update: {message}")
        
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
