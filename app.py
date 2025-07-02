from flask import Flask, Response
from src.nonsense import get_nonsense

app = Flask(__name__)

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')

@app.route('/getNonsense')
def get_nonsense_route():
    return Response(get_nonsense(), mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)

