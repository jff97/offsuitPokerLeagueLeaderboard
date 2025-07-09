import sys
import os
import threading
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
#legacy method
from src.tester import percentile_leaderboard_by_month_method, placement_leaderboard_by_month_method
#new round granular methods
from src.tester import get_placement_leaderboard_from_rounds, get_percentile_leaderboard_from_rounds, get_percentile_leaderboard_from_rounds_no_round_limit, refresh_rounds_database
from src.tester import log_time, get_all_logs_to_display_for_api, delete_logs
from src.timed_daily_events import DailyTimeScheduler
from flask import Flask, Response

app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/percentileleaderboardmonths')
def monthspercentile():
    csv_string = percentile_leaderboard_by_month_method()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/placementleaderboardmonths')
def monthsplacement():
    csv_string = placement_leaderboard_by_month_method()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')


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



# Example task
def task_event():
    log_time()

# Background thread to start scheduler
def start_scheduler():
    times = ["17:00", "02:30"]
    DailyTimeScheduler(times, task_event)
    
@app.route('/getlogs')
def get_logs():
    log_string = get_all_logs_to_display_for_api()
    return Response(f"<pre>{log_string}</pre>", mimetype='text/html')

@app.route('/deletelogs')
def delete_logs_endpoint():
    delete_logs()
    return Response(f"<pre>Logs deleted</pre>", mimetype='text/html')

if __name__ == '__main__':
    log_time()
    threading.Thread(target=start_scheduler, daemon=True).start()
    app.run(debug=True)
