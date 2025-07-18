from flask import Flask, Response
from flask_cors import CORS
from . import api_service
from .leaderboard_controller import leaderboard_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(leaderboard_bp)  

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')


@app.route('/api/refreshrounds')
def refresh_rounds():
    api_service.refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@app.route('/api/getlogs')
def get_logs():
    log_string = api_service.get_all_logs_to_display_for_api()
    return Response(f"<pre>{log_string}</pre>", mimetype='text/html')

@app.route('/api/deletelogs')
def delete_logs_endpoint():
    """Delete all log entries."""
    api_service.delete_logs()
    return Response(f"<pre>Logs deleted</pre>", mimetype='text/html')

@app.route('/api/getwarnings')
def get_warnings():
    """Get all warnings formatted for display."""
    warnings_string = api_service.get_all_warnings_to_display_for_api()
    return Response(f"<pre>{warnings_string}</pre>", mimetype='text/html')

@app.route('/api/deletewarnings')
def delete_warnings_endpoint():
    """Delete all warning entries."""
    api_service.delete_warnings()
    return Response(f"<pre>Warnings deleted</pre>", mimetype='text/html')
