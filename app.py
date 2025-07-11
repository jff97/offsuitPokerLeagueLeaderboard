import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
#new player entry in round granular methods
from src.api_service import get_placement_leaderboard_from_rounds, get_percentile_leaderboard_from_rounds, refresh_rounds_database, get_percentile_leaderboard_from_rounds_no_round_limit
from src.api_service import get_all_logs_to_display_for_api, delete_logs
from flask import Flask, Response

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
    delete_logs()
    return Response(f"<pre>Logs deleted</pre>", mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
