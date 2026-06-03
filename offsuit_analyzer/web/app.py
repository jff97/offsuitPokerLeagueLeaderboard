from flask import Flask, Response, g, request
from flask_cors import CORS
import time
import traceback
import json
from .controllers.leaderboard_controller import leaderboard_bp
from .controllers.name_tools_controller import name_tools_bp
from .controllers.admin_controller import admin_bp
from .controllers.qualification_controller import qualification_bp
from .controllers.automatic_points_controller import automatic_points_bp
from offsuit_analyzer import logging_service

app = Flask(__name__)
CORS(app)

app.register_blueprint(leaderboard_bp)  
app.register_blueprint(name_tools_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(qualification_bp)
app.register_blueprint(automatic_points_bp)

@app.before_request
def before_api_request():
    g.start_time = time.perf_counter()

@app.after_request
def after_api_request(response):
    if hasattr(g, 'start_time'):
        duration = time.perf_counter() - g.start_time
        response.headers["X-Response-Time"] = f"{duration:.4f}s"
    return response


@app.errorhandler(Exception)
def handle_exception(error):
    """Global error handler that logs all uncaught exceptions and returns 500 response."""
    error_message = f"Unhandled exception at {request.method} {request.url}: {traceback.format_exc()}"
    logging_service.log_critical(error_message)
    
    return Response(
        json.dumps({"error": str(error)}),
        status=500,
        mimetype="application/json"
    )

@app.route('/')
def home():
    return Response("<h1>Hello this is the default endpoint for johns api</h1>", mimetype='text/html')
