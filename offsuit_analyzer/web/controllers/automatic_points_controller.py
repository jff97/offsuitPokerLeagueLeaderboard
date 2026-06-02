from flask import Blueprint, jsonify, request, Response
import json
from ..decorators import require_admin_password
from ..services import automatic_points_service

automatic_points_bp = Blueprint('automatic_points', __name__, url_prefix='/api/automatic-points')


@automatic_points_bp.route('/bars', methods=['GET'])
def get_bars():
    """Public endpoint to get list of bars without sensitive tokens."""
    bar_list = automatic_points_service.get_bar_list()
    return jsonify(bar_list)


@automatic_points_bp.route('/add-round', methods=['POST'])
@require_admin_password
def add_round():
    """Add a new round with player scores.
    
    Requires admin password.
    
    Request body:
    {
        "password": "<admin password>",
        "bar_id": "encrypted_bar_id",
        "player_scores": [
            {"name": "Player Name", "score": 100},
            ...
        ]
    }
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
        
        # Get required fields
        bar_id = data.get('bar_id')
        player_scores = data.get('player_scores')
        
        if not bar_id or not player_scores:
            return Response(
                json.dumps({"error": "Missing bar_id or player_scores"}),
                status=400,
                mimetype="application/json"
            )
        
        result = automatic_points_service.add_new_round_from_bar_id(bar_id, player_scores)
        return Response(
            json.dumps(result),
            status=200,
            mimetype="application/json"
        )
    except Exception as e:
        return Response(
            json.dumps({"error": str(e)}),
            status=500,
            mimetype="application/json"
        )
