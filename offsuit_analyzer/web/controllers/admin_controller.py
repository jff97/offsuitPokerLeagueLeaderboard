from flask import Blueprint, Response
from flask_httpauth import HTTPTokenAuth
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
