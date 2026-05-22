from flask import Blueprint, jsonify, request
from app.extensions import socketio
from app.services.device_state import get_device_state, add_timeline_event, add_access_log, add_command, get_pending_commands, consume_pending_commands
from app.services.socket_service import emit_socket_event
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