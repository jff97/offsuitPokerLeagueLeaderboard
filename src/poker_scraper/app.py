from flask import Flask, Response
from .api_service import (
    get_placement_leaderboard_from_rounds, 
    get_percentile_leaderboard_from_rounds, 
    refresh_rounds_database, 
    get_percentile_leaderboard_from_rounds_no_round_limit,
    get_all_logs_to_display_for_api, 
    delete_logs, 
    get_all_warnings_to_display_for_api, 
    delete_warnings
)

app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/placementleaderboard')
def placement():
    csv_string = get_placement_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/percentileleaderboard')
def percentile():
    csv_string = get_percentile_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/percentileleaderboardnoroundlimit')
def percentile_no_round_limit():
    csv_string = get_percentile_leaderboard_from_rounds_no_round_limit()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/refreshroundsdb')
def refresh_rounds():
    refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

@app.route('/getlogs')
def get_logs():
    log_string = get_all_logs_to_display_for_api()
    return Response(f"<pre>{log_string}</pre>", mimetype='text/html')

@app.route('/deletelogs')
def delete_logs_endpoint():
    """Delete all log entries."""
    delete_logs()
    return Response(f"<pre>Logs deleted</pre>", mimetype='text/html')

@app.route('/getwarnings')
def get_warnings():
    """Get all warnings formatted for display."""
    warnings_string = get_all_warnings_to_display_for_api()
    return Response(f"<pre>{warnings_string}</pre>", mimetype='text/html')

@app.route('/deletewarnings')
def delete_warnings_endpoint():
    """Delete all warning entries."""
    delete_warnings()
    return Response(f"<pre>Warnings deleted</pre>", mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)

def main():
    """Entry point for the poker-scraper command."""
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
