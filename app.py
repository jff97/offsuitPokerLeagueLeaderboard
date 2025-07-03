import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.tester import test1  # now src is in path so this import works
from flask import Flask, Response, jsonify


app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/test1')
def test():
    return Response(test1())

if __name__ == '__main__':
    app.run(debug=True)
