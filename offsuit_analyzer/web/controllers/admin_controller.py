from flask import Blueprint, Response
from ..services.admin_service import refresh_rounds_database, refresh_legacy_rounds

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/refreshrounds')
def refresh_rounds():
    refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@admin_bp.route('/refreshlegacyrounds')
def refresh_legacy_rounds_endpoint():
    refresh_legacy_rounds()
    return Response("<h1>Rounds Database Was refreshed for current legacy june months</h1>", mimetype='text/html')
