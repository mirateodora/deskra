from flask import Blueprint, jsonify, request

from app.services.device_state import (
    update_settings,
    add_timeline_event,
    add_command
)

from app.services.socket_service import (
    emit_settings_update,
    emit_timeline_update
)

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/temperature-threshold", methods=["POST"])
def set_temperature_threshold():
    data = request.get_json() or {}

    threshold = data.get("temperatureThreshold")

    if threshold is None:
        return jsonify({
            "status": "error",
            "message": "temperatureThreshold is required"
        }), 400

    settings_data = update_settings(
        temperature_threshold=float(threshold)
    )

    command = add_command(
        command_type="SET_TEMPERATURE_THRESHOLD",
        value=float(threshold),
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="settings",
        message=f"Temperature threshold changed to {threshold}°C",
        metadata={
            "temperatureThreshold": float(threshold),
            "commandId": command["id"]
        }
    )

    emit_settings_update(settings_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Temperature threshold updated",
        "settings": settings_data,
        "command": command,
        "timelineEvent": timeline_event
    })