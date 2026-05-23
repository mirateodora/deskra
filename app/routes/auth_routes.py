from flask import Blueprint, jsonify, request
from app.services.device_state import update_auth_state, add_timeline_event, add_access_log
from app.services.socket_service import emit_socket_event

FAKE_USERS = [
    {
        "id": 1,
        "name": "Alex",
        "pin": "1234",
        "focusLedColor": "#d66b5d",
        "breakLedColor": "#65b891"
    },
    {
        "id": 2,
        "name": "GuestTest",
        "pin": "0000",
        "focusLedColor": "#8fb5ff",
        "breakLedColor": "#65b891"
    }
]


def find_fake_user(name, pin):
    for user in FAKE_USERS:
        if user["name"].lower() == name.lower() and user["pin"] == pin:
            return user

    return None

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/manual-login", methods=["POST"])
def manual_login():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    pin = data.get("pin", "").strip()

    if not name or not pin:
        access_log = add_access_log(
            user=None,
            method="manual_pin",
            success=False,
            message="Manual login failed: missing name or PIN",
            metadata={
                "source": "manual_login_route"
            }
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Name and PIN are required"
        }), 400

    matched_user = find_fake_user(name, pin)

    if not matched_user:
        access_log = add_access_log(
            user={
                "name": name
            },
            method="manual_pin",
            success=False,
            message=f"Manual PIN login failed for {name}",
            metadata={
                "source": "manual_login_route",
                "reason": "invalid_credentials"
            }
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Invalid name or PIN"
        }), 401

    fake_user = {
        "id": matched_user["id"],
        "name": matched_user["name"],
        "focusLedColor": matched_user["focusLedColor"],
        "breakLedColor": matched_user["breakLedColor"]
    }

    auth_state = update_auth_state(
        locked=False,
        current_user=fake_user,
        login_method="manual_pin"
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message=f"Manual login successful for {name}",
        metadata={
            "user": fake_user,
            "method": "manual_pin",
            "source": "manual_login_route"
        }
    )

    access_log = add_access_log(
        user=fake_user,
        method="manual_pin",
        success=True,
        message=f"Manual PIN login successful for {name}",
        metadata={
            "source": "manual_login_route"
        }
    )

    emit_socket_event("auth_update", auth_state)
    emit_socket_event("timeline_update", timeline_event)
    emit_socket_event("access_log_update", access_log)

    return jsonify({
        "success": True,
        "message": "Manual login successful",
        "user": fake_user,
        "auth": auth_state,
        "timelineEvent": timeline_event,
        "accessLog": access_log
    })

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    name = data.get("name", "").strip()
    pin = data.get("pin", "").strip()
    focus_led_color = data.get("focusLedColor", "#d66b5d")
    break_led_color = data.get("breakLedColor", "#65b891")
    focus_minutes = int(data.get("focusMinutes", 25))
    break_minutes = int(data.get("breakMinutes", 5))
    temperature_threshold = float(data.get("temperatureThreshold", 26))

    if not name or not pin:
        access_log = add_access_log(
            user=None,
            method="register",
            success=False,
            message="Registration failed: missing name or PIN",
            metadata={
                "source": "register_route"
            }
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Name and PIN are required"
        }), 400

    if len(pin) < 4:
        access_log = add_access_log(
            user={
                "name": name
            },
            method="register",
            success=False,
            message=f"Registration failed for {name}: PIN too short",
            metadata={
                "source": "register_route"
            }
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "PIN must have at least 4 digits"
        }), 400

    new_user = {
        "id": len(FAKE_USERS) + 1,
        "name": name,
        "pin": pin,
        "focusLedColor": focus_led_color,
        "breakLedColor": break_led_color
    }

    FAKE_USERS.append(new_user)

    safe_user = {
        "id": new_user["id"],
        "name": new_user["name"],
        "focusLedColor": new_user["focusLedColor"],
        "breakLedColor": new_user["breakLedColor"]
    }

    auth_state = update_auth_state(
        locked=False,
        current_user=safe_user,
        login_method="register"
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message=f"New user registered: {name}",
        metadata={
            "user": safe_user,
            "method": "register",
            "source": "register_route"
        }
    )

    access_log = add_access_log(
        user=safe_user,
        method="register",
        success=True,
        message=f"Registration successful for {name}",
        metadata={
            "source": "register_route"
        }
    )

    settings_payload = {
        "focusLedColor": focus_led_color,
        "breakLedColor": break_led_color,
        "defaultFocusMinutes": focus_minutes,
        "defaultBreakMinutes": break_minutes,
        "temperatureThreshold": temperature_threshold
    }

    emit_socket_event("auth_update", auth_state)
    emit_socket_event("settings_update", settings_payload)
    emit_socket_event("timeline_update", timeline_event)
    emit_socket_event("access_log_update", access_log)

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": safe_user,
        "auth": auth_state,
        "settings": settings_payload,
        "timelineEvent": timeline_event,
        "accessLog": access_log
    }), 201

@auth_bp.route("/test", methods=["GET"])
def test_auth():
    return jsonify({
        "status": "ok",
        "message": "Auth routes are working"
    })

@auth_bp.route("/fake-face-success", methods=["POST", "GET"])
def fake_face_success():
    fake_user = {
        "id": 1,
        "name": "Simulated User",
        "focusLedColor": "#d66b5d",
        "breakLedColor": "#65b891"
    }

    auth_state = update_auth_state(
        locked=False,
        current_user=fake_user,
        login_method="face_id"
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message="Zero-touch login successful by simulated Face ID",
        metadata={
            "user": fake_user,
            "method": "face_id",
            "source": "fake_backend_route"
        }
    )

    access_log = add_access_log(
        user=fake_user,
        method="face_id",
        success=True,
        message="Simulated Face ID login successful",
        metadata={
            "source": "fake_backend_route"
        }
    )

    emit_socket_event("login_success", {
        "user": fake_user,
        "auth": auth_state,
        "timelineEvent": timeline_event,
        "accessLog": access_log
    })

    return jsonify({
        "status": "ok",
        "message": "Fake face login success triggered",
        "user": fake_user
    })

@auth_bp.route("/fake-face-failure", methods=["POST", "GET"])
def fake_face_failure():
    timeline_event = add_timeline_event(
        event_type="auth",
        message="Face ID failed, manual login required",
        metadata={
            "method": "face_id",
            "source": "fake_backend_route"
        }
    )

    access_log = add_access_log(
        user=None,
        method="face_id",
        success=False,
        message="Simulated Face ID login failed",
        metadata={
            "source": "fake_backend_route"
        }
    )

    emit_socket_event("login_failed", {
        "reason": "No matching face found",
        "timelineEvent": timeline_event,
        "accessLog": access_log
    })

    return jsonify({
        "status": "ok",
        "message": "Fake face login failure triggered",
        "reason": "No matching face found"
    })