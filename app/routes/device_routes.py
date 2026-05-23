from flask import Blueprint, jsonify, request
from app.extensions import socketio
from app.services.device_state import get_device_state, add_timeline_event, add_access_log, add_command, get_pending_commands, consume_pending_commands, update_sensors, update_fan_state, update_led_color, update_settings, add_sensor_reading
from app.services.socket_service import emit_socket_event, emit_sensor_update, emit_timeline_update, emit_actuator_update, emit_settings_update
from app.services.auto_fan_service import evaluate_auto_fan
from app.services.device_state import set_manual_fan_override, get_selected_task
device_bp = Blueprint("device", __name__)


@device_bp.route("/test", methods=["GET"])
def test_device():
    return jsonify({
        "status": "ok",
        "message": "Device routes are working"
    })


@device_bp.route("/socket-test", methods=["GET"])
def socket_test():
    socketio.emit("test_event", {
        "message": "Hello from Flask-SocketIO"
    })

    return {
        "status": "ok",
        "message": "Socket event emitted"
    }

@device_bp.route("/state", methods=["GET"])
def get_state():
    return get_device_state()

@device_bp.route("/emit-test", methods=["GET"])
def emit_test():
    emit_socket_event("test_event", {
        "message": "Hello from socket_service helper"
    })

    return {
        "status": "ok",
        "message": "Socket helper emitted test_event"
    }

@device_bp.route("/timeline-test", methods=["GET"])
def timeline_test():
    event = add_timeline_event(
        event_type="test",
        message="Timeline helper is working",
        metadata={
            "source": "manual_test"
        }
    )

    return {
        "status": "ok",
        "event": event
    }

@device_bp.route("/access-log-test", methods=["GET"])
def access_log_test():
    log = add_access_log(
        user={
            "id": 1,
            "name": "Test User"
        },
        method="manual_pin",
        success=True,
        message="Access log helper is working",
        metadata={
            "source": "manual_test"
        }
    )

    return {
        "status": "ok",
        "log": log
    }

@device_bp.route("/command-test", methods=["GET"])
def command_test():
    command = add_command(
        command_type="SET_FAN",
        value=True,
        payload={
            "source": "manual_test"
        }
    )

    return {
        "status": "ok",
        "command": command
    }


@device_bp.route("/commands", methods=["GET"])
def get_commands():
    commands = consume_pending_commands()

    return {
        "status": "ok",
        "commands": commands
    }


@device_bp.route("/commands/pending", methods=["GET"])
def pending_commands():
    commands = get_pending_commands()

    return {
        "status": "ok",
        "commands": commands
    }

@device_bp.route("/sensors", methods=["POST"])
def receive_sensor_data():
    data = request.get_json() or {}

    temperature = data.get("temperature")
    humidity = data.get("humidity")
    presence = data.get("presence")

    sensor_data = update_sensors(
        temperature=temperature,
        humidity=humidity,
        presence=presence
    )

    sensor_reading = add_sensor_reading(
        temperature=temperature,
        humidity=humidity,
        presence=presence,
        metadata={
            "source": "device_sensor_route"
        }
    )

    emit_sensor_update(sensor_data)
    auto_fan_result = evaluate_auto_fan()

    if presence is not None:
        if presence:
            timeline_event = add_timeline_event(
                event_type="sensor",
                message="Presence detected by desk sensor",
                metadata={
                    "source": "sensor_update"
                }
            )
        else:
            timeline_event = add_timeline_event(
                event_type="sensor",
                message="Presence lost by desk sensor",
                metadata={
                    "source": "sensor_update"
                }
            )

        emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Sensor data received",
        "sensors": sensor_data,
        "sensorReading": sensor_reading,
        "autoFan": auto_fan_result
    })

@device_bp.route("/fan", methods=["POST"])
def set_fan():
    data = request.get_json() or {}
    state = bool(data.get("state"))

    actuator_data = update_fan_state(state)
    set_manual_fan_override(True)


    command = add_command(
        command_type="SET_FAN",
        value=state,
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="actuator",
        message=f"Fan turned {'on' if state else 'off'} from dashboard",
        metadata={
            "state": state,
            "commandId": command["id"]
        }
    )

    emit_actuator_update(actuator_data)
    emit_socket_event_name = "fan_update"
    from app.services.socket_service import emit_socket_event
    emit_socket_event(emit_socket_event_name, actuator_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": f"Fan turned {'on' if state else 'off'}",
        "actuators": actuator_data,
        "command": command,
        "timelineEvent": timeline_event
    })

@device_bp.route("/led", methods=["POST"])
def set_led():
    data = request.get_json() or {}
    color = data.get("color", "#ff0000")

    actuator_data = update_led_color(color)

    command = add_command(
        command_type="SET_LED_COLOR",
        value=color,
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="actuator",
        message=f"LED color changed to {color} from dashboard",
        metadata={
            "color": color,
            "commandId": command["id"]
        }
    )

    emit_actuator_update(actuator_data)
    from app.services.socket_service import emit_socket_event
    emit_socket_event("led_update", actuator_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "LED color updated",
        "actuators": actuator_data,
        "command": command,
        "timelineEvent": timeline_event
    })

@device_bp.route("/tasks/active", methods=["GET"])
def get_active_task_for_device():
    selected_task = get_selected_task()

    if not selected_task:
        return jsonify({
            "status": "ok",
            "hasTask": False,
            "task": None,
            "message": "No task selected"
        })

    return jsonify({
        "status": "ok",
        "hasTask": True,
        "task": selected_task,
        "message": selected_task["title"]
    })