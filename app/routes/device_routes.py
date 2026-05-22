from flask import Blueprint, jsonify, request
from app.extensions import socketio

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