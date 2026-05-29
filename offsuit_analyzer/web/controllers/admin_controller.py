from flask import Blueprint, Response, request
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
