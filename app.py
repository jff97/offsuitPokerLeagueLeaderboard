from flask import Flask, Response, jsonify
from src.nonsense import get_nonsense
from src.db_handler import increment_hit_count

app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/getNonsense')
def get_nonsense_route():
    return Response(get_nonsense(), mimetype='text/html')

@app.route("/hitcount")
def hello_endpoint():
    hits = increment_hit_count()
    return jsonify({"hits": hits})

if __name__ == '__main__':
    app.run(debug=True)

