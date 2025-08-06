from flask import Blueprint, Response
from flask_httpauth import HTTPTokenAuth
from ..services.admin_service import refresh_rounds_database, refresh_legacy_rounds
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
    refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@admin_bp.route('/refreshlegacyrounds', methods=['POST'])
@auth.login_required
def refresh_legacy_rounds_endpoint():
    refresh_legacy_rounds()
    return Response("<h1>Rounds Database Was refreshed for current legacy june months</h1>", mimetype='text/html')
