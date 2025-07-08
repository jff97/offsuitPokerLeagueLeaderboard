import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

#legacy method
from src.tester import percentile_leaderboard_by_month_method, placement_leaderboard_by_month_method

#new round granular methods
from src.tester import get_placement_leaderboard_from_rounds, get_percentile_leaderboard_from_rounds, refresh_rounds_database 

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


@app.route('/placementleaderboardrounds')
def placement():
    csv_string = get_placement_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/percentileleaderboardrounds')
def percentile():
    csv_string = get_percentile_leaderboard_from_rounds()
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

@app.route('/refreshroundsdb')
def refresh_rounds():
    refresh_rounds_database()
    return Response("<h1>Rounds Database Was refreshed for current month</h1>", mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
