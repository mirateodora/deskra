from flask import Blueprint, jsonify, request

from app.services.device_state import (
    update_settings,
    add_timeline_event,
    add_command,
    get_device_state,
    update_auth_state,
    update_pomodoro_state
)

from app.services.socket_service import (
    emit_settings_update,
    emit_timeline_update,
    emit_pomodoro_update,
    emit_socket_event
)

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("", methods=["GET"])
def get_settings():
    state = get_device_state()

    return jsonify({
        "status": "ok",
        "settings": state["settings"],
        "auth": state["auth"],
        "pomodoro": state["pomodoro"]
    })


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

@settings_bp.route("", methods=["PUT"])
def update_all_settings():
    data = request.get_json() or {}
    state = get_device_state()

    focus_led_color = data.get(
        "focusLedColor",
        state["settings"].get("focusLedColor", "#d66b5d")
    )

    break_led_color = data.get(
        "breakLedColor",
        state["settings"].get("breakLedColor", "#65b891")
    )

    default_focus_minutes = int(data.get(
        "defaultFocusMinutes",
        state["settings"].get("defaultFocusMinutes", 25)
    ))

    default_break_minutes = int(data.get(
        "defaultBreakMinutes",
        state["settings"].get("defaultBreakMinutes", 5)
    ))

    temperature_threshold = float(data.get(
        "temperatureThreshold",
        state["settings"].get("temperatureThreshold", 26)
    ))

    music_enabled = bool(data.get(
        "musicEnabled",
        state["settings"].get("musicEnabled", False)
    ))

    settings_data = update_settings(
        default_led_color=focus_led_color,
        default_focus_minutes=default_focus_minutes,
        default_break_minutes=default_break_minutes,
        temperature_threshold=temperature_threshold,
        music_enabled=music_enabled
    )

    settings_data["focusLedColor"] = focus_led_color
    settings_data["breakLedColor"] = break_led_color
    pomodoro_data = update_pomodoro_state(
        focus_minutes=default_focus_minutes,
        break_minutes=default_break_minutes,
        remaining_seconds=default_focus_minutes * 60
    )

    current_user = state["auth"].get("currentUser")

    if current_user:
        updated_user = {
            **current_user,
            "focusLedColor": focus_led_color,
            "breakLedColor": break_led_color
        }

        auth_data = update_auth_state(
            locked=state["auth"].get("locked", False),
            current_user=updated_user,
            login_method=state["auth"].get("loginMethod")
        )
    else:
        auth_data = state["auth"]

    command = add_command(
        command_type="UPDATE_SETTINGS",
        value=True,
        payload={
            "focusLedColor": focus_led_color,
            "breakLedColor": break_led_color,
            "defaultFocusMinutes": default_focus_minutes,
            "defaultBreakMinutes": default_break_minutes,
            "temperatureThreshold": temperature_threshold,
            "musicEnabled": music_enabled,
            "source": "settings_page"
        }
    )

    timeline_event = add_timeline_event(
        event_type="settings",
        message="Settings updated from Settings page",
        metadata={
            "commandId": command["id"],
            "source": "settings_page"
        }
    )

    emit_settings_update(settings_data)
    emit_pomodoro_update(pomodoro_data)
    emit_socket_event("auth_update", auth_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Settings updated",
        "settings": settings_data,
        "pomodoro": pomodoro_data,
        "auth": auth_data,
        "command": command,
        "timelineEvent": timeline_event
    })