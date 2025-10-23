from flask import Blueprint, Response
from ..services import name_tools_service 

name_tools_bp = Blueprint('nametools', __name__, url_prefix='/api/nametools')

@name_tools_bp.route('/getwarnings')
def get_warnings():
    """Get all warnings formatted for display."""
    warnings_string = name_tools_service.get_all_warnings_for_display()
    return Response(f"<pre>{warnings_string}</pre>", mimetype='text/html')

@name_tools_bp.route("ambiguousnamestool")
def ambiguous_names():
    return Response(f"<pre>{name_tools_service.get_ambiguous_names()}</pre>", mimetype='text/html')

@name_tools_bp.route("getnameclashes")
def get_name_clashes():
    name_clashes = name_tools_service.get_all_name_clashes()
    return Response(f"<pre>{name_clashes}</pre>", mimetype='text/html')

@name_tools_bp.route("deletenameclashes")
def delete_name_clashes():
    name_tools_service.delete_all_name_clashes()
    return Response(f"<pre>All Name clashes were deleted</pre>", mimetype='text/html')
