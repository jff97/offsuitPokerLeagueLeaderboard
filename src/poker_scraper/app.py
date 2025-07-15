from flask import Flask, Response
from . import api_service

app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/placementleaderboard')
def placement():
    csv_string = api_service.get_placement_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/percentileleaderboard')
def percentile():
    csv_string = api_service.get_percentile_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/roileaderboard')
def roi():
    csv_string = api_service.get_roi_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/trueskillleaderboard')
def trueskill():
    csv_string = api_service.get_trueskill_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/percentileleaderboardnoroundlimit')
def percentile_no_round_limit():
    csv_string = api_service.get_percentile_leaderboard_from_rounds_no_round_limit()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/refreshroundsdb')
def refresh_rounds():
    api_service.refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@app.route('/getlogs')
def get_logs():
    log_string = api_service.get_all_logs_to_display_for_api()
    return Response(f"<pre>{log_string}</pre>", mimetype='text/html')

@app.route('/deletelogs')
def delete_logs_endpoint():
    """Delete all log entries."""
    api_service.delete_logs()
    return Response(f"<pre>Logs deleted</pre>", mimetype='text/html')

@app.route('/getwarnings')
def get_warnings():
    """Get all warnings formatted for display."""
    warnings_string = api_service.get_all_warnings_to_display_for_api()
    return Response(f"<pre>{warnings_string}</pre>", mimetype='text/html')

@app.route('/deletewarnings')
def delete_warnings_endpoint():
    """Delete all warning entries."""
    api_service.delete_warnings()
    return Response(f"<pre>Warnings deleted</pre>", mimetype='text/html')
