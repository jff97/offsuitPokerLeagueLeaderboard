"""Authentication decorators for admin endpoints."""
from functools import wraps
from flask import request, Response, jsonify
from offsuit_analyzer.config import config
import json


def require_admin_password(f):
    """
    Decorator to require admin password for protected endpoints.
    
    Password can be provided in:
    - Request JSON body: {"password": "..."}
    - Query parameter: ?password=...
    
    Returns 401 Unauthorized if password is invalid or missing.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
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

        # Let errors from the wrapped endpoint propagate to the global handler so they get logged
        return f(*args, **kwargs)

    return decorated_function
