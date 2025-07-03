import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tester import test2, percentile_leaderboard  # now src is in path so this import works
from flask import Flask, Response, jsonify


app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/test2')
def test():
    return Response(test2())

@app.route('/percentileleaderboard')
def percentile():
    csv_string = percentile_leaderboard()  # make sure this returns a str
    return Response(f"<pre>{csv_string}</pre>", mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)
