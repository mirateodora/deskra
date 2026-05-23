from flask import Flask
from flask_cors import CORS

from app.extensions import socketio
from app.routes.device_routes import device_bp
from app.routes.auth_routes import auth_bp
from app.routes.simulator_routes import simulator_bp
from app.routes.settings_routes import settings_bp
from app.routes.pomodoro_routes import pomodoro_bp
from app.routes.tasks_routes import tasks_bp
from app.routes.logs_routes import logs_bp
from app.routes.analytics_routes import analytics_bp

def create_app():
    app = Flask(__name__)

    CORS(app, origins=["http://localhost:5173"])

    socketio.init_app(app, cors_allowed_origins=["http://localhost:5173"])

    app.register_blueprint(device_bp, url_prefix="/api/device")
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(simulator_bp, url_prefix="/api/simulator")
    app.register_blueprint(settings_bp, url_prefix="/api/settings")
    app.register_blueprint(pomodoro_bp, url_prefix="/api/pomodoro")
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(logs_bp, url_prefix="/api/logs")
    app.register_blueprint(analytics_bp, url_prefix="/api/analytics")

    @app.route("/api/health")
    def health():
        return {
            "status": "ok",
            "message": "Flask backend is running"
        }

    return app