from flask import Flask, Response, g
from flask_cors import CORS
import time
from .controllers.leaderboard_controller import leaderboard_bp
from .controllers.name_tools_controller import name_tools_bp
from .controllers.admin_controller import admin_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(leaderboard_bp)  
app.register_blueprint(name_tools_bp)
app.register_blueprint(admin_bp)

@app.before_request
def before_api_request():
    g.start_time = time.perf_counter()

@app.after_request
def after_api_request(response):
    if hasattr(g, 'start_time'):
        duration = time.perf_counter() - g.start_time
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
    return response

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')
