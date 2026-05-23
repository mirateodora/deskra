from flask import Blueprint, jsonify

from app.services.device_state import get_device_state

logs_bp = Blueprint("logs", __name__)


@logs_bp.route("/timeline", methods=["GET"])
def get_timeline():
    state = get_device_state()

    timeline = state.get("timeline", [])

    sorted_timeline = sorted(
        timeline,
        key=lambda event: event.get("timestamp", ""),
        reverse=True
    )

    return jsonify({
        "status": "ok",
        "timeline": sorted_timeline
    })

@logs_bp.route("/access", methods=["GET"])
def get_access_logs():
    state = get_device_state()

    access_logs = state.get("accessLogs", [])

    sorted_access_logs = sorted(
        access_logs,
        key=lambda log: log.get("timestamp", ""),
        reverse=True
    )

    return jsonify({
        "status": "ok",
        "accessLogs": sorted_access_logs
    })