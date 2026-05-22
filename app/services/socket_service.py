from app.extensions import socketio


def emit_socket_event(event_name, data=None):
    """
    Emits a WebSocket event to all connected Vue clients.
    """

    if data is None:
        data = {}

    socketio.emit(event_name, data)

    return {
        "event": event_name,
        "data": data
    }


def emit_state_update(device_state):
    """
    Emits the full device state.
    Useful when many things changed at once.
    """

    return emit_socket_event("state_update", device_state)


def emit_sensor_update(sensor_data):
    return emit_socket_event("sensor_update", sensor_data)


def emit_actuator_update(actuator_data):
    return emit_socket_event("actuator_update", actuator_data)


def emit_auth_update(auth_data):
    return emit_socket_event("auth_update", auth_data)


def emit_pomodoro_update(pomodoro_data):
    return emit_socket_event("pomodoro_update", pomodoro_data)


def emit_settings_update(settings_data):
    return emit_socket_event("settings_update", settings_data)


def emit_timeline_update(timeline_event):
    return emit_socket_event("timeline_update", timeline_event)


def emit_access_log_update(access_log):
    return emit_socket_event("access_log_update", access_log)