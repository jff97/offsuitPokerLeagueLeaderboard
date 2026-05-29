from flask import Blueprint, Response, request, jsonify
from flask_httpauth import HTTPTokenAuth
import json
from ..services import admin_service 
from offsuit_analyzer.config import config

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')
auth = HTTPTokenAuth(scheme='Bearer')


@auth.verify_token
def verify_token(token):
    """Called automatically by @auth.login_required decorator to validate tokens"""
    return token == config.ADMIN_AUTH_TOKEN

@admin_bp.route('/refreshrounds', methods=['POST'])
@auth.login_required
def refresh_rounds():
    admin_service.refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@admin_bp.route('/emailroundbackup', methods=['POST'])
@auth.login_required
def email_round_backup():
    admin_service.email_json_rounds_to_admin()
    return Response("<h1>Json file backup was email to admin.</h1>", mimetype='text/html')

@admin_bp.route('/emailbarlist', methods=['POST'])
@auth.login_required
def email_bar_list():
    admin_service.email_bar_list_to_admin()
    return Response("<h1>Bar list report was emailed to admin.</h1>", mimetype='text/html')

@admin_bp.route('/refreshlegacyrounds', methods=['POST'])
@auth.login_required
def refresh_legacy_rounds_endpoint():
    admin_service.refresh_legacy_rounds()
    return Response("<h1>Rounds Database Was refreshed for current legacy june months</h1>", mimetype='text/html')


@admin_bp.route('/checknameclashes', methods=['POST'])
@auth.login_required
def check_name_clashes():
    """Endpoint to run name clash detection."""
    admin_service.run_name_clash_detection()
    return Response("<h1>Name clash detection has been run</h1>", mimetype='text/html')


@admin_bp.route('/season-calendar', methods=['GET'])
def get_season_calendar_endpoint():
    try:
        year_param = request.args.get("year")
        if not year_param:
            raise ValueError("Year query parameter is required")
        
        year = int(year_param)
        calendar = admin_service.get_season_calendar(year)
        response_data = calendar.to_dict() if calendar else {}
        return Response(json.dumps(response_data), status=200, mimetype="application/json")
    except ValueError as e:
        return Response(json.dumps({"error": str(e)}), status=400, mimetype="application/json")


@admin_bp.route('/season-calendar', methods=['POST'])
def upsert_season_calendar():
    try:
        data = request.get_json()

        if data.pop('password', None) != config.OFFSUIT_ADMIN_PASSWORD:
            return Response(json.dumps({"error": "Invalid password"}), status=401, mimetype="application/json")

        admin_service.upsert_season_calendar(data)
        return Response(json.dumps({"status": "ok"}), status=200, mimetype="application/json")
    except ValueError as e:
        return Response(json.dumps({"error": str(e)}), status=400, mimetype="application/json")


@admin_bp.route('/trigger-frontend-update', methods=['POST'])
def trigger_frontend_update():
    """
    Trigger the frontend leaderboards refresh workflow on GitHub.
    
    This endpoint dispatches a GitHub workflow that updates the frontend leaderboard caches.
    The GitHub PAT token is kept secure on the backend only.
    
    Request body:
    {
        "password": "<admin password>"
    }
    
    Returns:
        JSON with status and workflow information on success
        401 Unauthorized if password is invalid
        500 Internal Server Error if GitHub API call fails
    """
    try:
        data = request.get_json()
        
        # Validate request has JSON
        if not data:
            return jsonify({"status": "error", "message": "Request body must be valid JSON"}), 400
        
        # Validate password
        if data.get('password') != config.OFFSUIT_ADMIN_PASSWORD:
            return jsonify({"status": "error", "message": "Invalid password"}), 401
        
        # Trigger the GitHub workflow
        success, message, status_code = admin_service.trigger_frontend_update()
        
        if success:
            return jsonify({
                "status": "success",
                "message": message,
                "workflow_id": "refresh_leaderboards"
            }), status_code
        else:
            return jsonify({
                "status": "error",
                "message": message
            }), status_code
            
    except Exception as e:
        print(f'Error in trigger_frontend_update endpoint: {str(e)}')
        return jsonify({
            "status": "error",
            "message": "Failed to dispatch workflow"
        }), 500
