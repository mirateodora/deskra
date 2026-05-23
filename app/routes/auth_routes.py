from pathlib import Path

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from deepface import DeepFace
from sqlalchemy import func

from app.extensions import db
from app.models import User, UserSettings
from app.services.device_state import (
    update_auth_state,
    add_timeline_event,
    add_access_log,
)
from app.services.socket_service import emit_socket_event
from app.services.face_service import (
    get_uploaded_face_file,
    save_uploaded_face_temporarily,
    delete_temp_face_file,
)


auth_bp = Blueprint("auth", __name__)


BASE_DIR = Path(__file__).resolve().parents[2]
REGISTERED_FACES_DIR = BASE_DIR / "registered_faces"

ALLOWED_UPLOAD_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
ALLOWED_FACE_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp"}


DEFAULT_USERS = [
    {
        "name": "Alex",
        "pin": "1234",
        "focusLedColor": "#d66b5d",
        "breakLedColor": "#65b891",
        "faceImagePath": None,
    },
    {
        "name": "GuestTest",
        "pin": "0000",
        "focusLedColor": "#8fb5ff",
        "breakLedColor": "#65b891",
        "faceImagePath": None,
    },
    {
        "name": "Maria",
        "pin": "5678",
        "focusLedColor": "#d66b5d",
        "breakLedColor": "#65b891",
        "faceImagePath": "registered_faces/user_3_maria.png",
    },
]


def seed_default_users_if_needed():
    """
    Temporary dev seed.

    This keeps your old test users available after moving from FAKE_USERS
    to database users. Later you can replace this with a proper seed command.
    """
    for default_user in DEFAULT_USERS:
        existing_user = User.query.filter(
            func.lower(User.name) == default_user["name"].lower()
        ).first()

        if existing_user:
            continue

        user = User(
            name=default_user["name"],
            pin=default_user["pin"],
            focus_led_color=default_user["focusLedColor"],
            break_led_color=default_user["breakLedColor"],
            face_image_path=default_user["faceImagePath"],
        )

        db.session.add(user)
        db.session.flush()

        settings = UserSettings(
            user_id=user.id,
            temperature_threshold=26.0,
            default_focus_minutes=25,
            default_break_minutes=5,
            default_led_color=default_user["focusLedColor"],
            focus_led_color=default_user["focusLedColor"],
            break_led_color=default_user["breakLedColor"],
            music_enabled=False,
        )

        db.session.add(settings)

    db.session.commit()


def allowed_face_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_UPLOAD_EXTENSIONS
    )


def safe_user_from_db_user(user):
    return user.to_dict()


def find_user_by_name_and_pin(name, pin):
    return User.query.filter(
        func.lower(User.name) == name.lower(),
        User.pin == pin,
    ).first()


def save_face_image(file, user_id, name):
    if not file or file.filename == "":
        return None

    if not allowed_face_file(file.filename):
        return None

    REGISTERED_FACES_DIR.mkdir(exist_ok=True)

    extension = file.filename.rsplit(".", 1)[1].lower()
    safe_name = secure_filename(name.lower().replace(" ", "_"))
    filename = f"user_{user_id}_{safe_name}.{extension}"

    file_path = REGISTERED_FACES_DIR / filename
    file.save(str(file_path))

    return str(file_path.relative_to(BASE_DIR))


def get_registered_face_files():
    REGISTERED_FACES_DIR.mkdir(exist_ok=True)

    return [
        file_path
        for file_path in REGISTERED_FACES_DIR.iterdir()
        if file_path.is_file() and file_path.suffix.lower() in ALLOWED_FACE_SUFFIXES
    ]


def find_user_by_face_filename(face_file_path):
    """
    Expected filename format:
    user_3_maria.png

    Meaning:
    user_<user_id>_<user_name>.<extension>
    """
    stem = face_file_path.stem.strip().lower()
    parts = stem.split("_", 2)

    if len(parts) != 3 or parts[0] != "user":
        return None

    try:
        user_id = int(parts[1])
    except ValueError:
        return None

    face_name = parts[2].replace("_", " ").strip().lower()

    user = db.session.get(User, user_id)

    if not user:
        return None

    if user.name.strip().lower() != face_name:
        return None

    return user


@auth_bp.route("/manual-login", methods=["POST"])
def manual_login():
    seed_default_users_if_needed()

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
                "source": "manual_login_route",
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Name and PIN are required",
        }), 400

    matched_user = find_user_by_name_and_pin(name, pin)

    if not matched_user:
        access_log = add_access_log(
            user={
                "name": name,
            },
            method="manual_pin",
            success=False,
            message=f"Manual PIN login failed for {name}",
            metadata={
                "source": "manual_login_route",
                "reason": "invalid_credentials",
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Invalid name or PIN",
        }), 401

    safe_user = safe_user_from_db_user(matched_user)

    auth_state = update_auth_state(
        locked=False,
        current_user=safe_user,
        login_method="manual_pin",
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message=f"Manual login successful for {name}",
        metadata={
            "user": safe_user,
            "method": "manual_pin",
            "source": "manual_login_route",
        },
    )

    access_log = add_access_log(
        user=safe_user,
        method="manual_pin",
        success=True,
        message=f"Manual PIN login successful for {name}",
        metadata={
            "source": "manual_login_route",
        },
    )

    emit_socket_event("auth_update", auth_state)
    emit_socket_event("timeline_update", timeline_event)
    emit_socket_event("access_log_update", access_log)

    return jsonify({
        "success": True,
        "message": "Manual login successful",
        "user": safe_user,
        "auth": auth_state,
        "timelineEvent": timeline_event,
        "accessLog": access_log,
    })


@auth_bp.route("/register", methods=["POST"])
def register():
    seed_default_users_if_needed()

    if request.content_type and request.content_type.startswith("multipart/form-data"):
        data = request.form
        face_file = request.files.get("faceImage")
    else:
        data = request.get_json() or {}
        face_file = None

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
                "source": "register_route",
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Name and PIN are required",
        }), 400

    if len(pin) < 4:
        access_log = add_access_log(
            user={
                "name": name,
            },
            method="register",
            success=False,
            message=f"Registration failed for {name}: PIN too short",
            metadata={
                "source": "register_route",
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "PIN must have at least 4 digits",
        }), 400

    existing_user = User.query.filter(
        func.lower(User.name) == name.lower()
    ).first()

    if existing_user:
        return jsonify({
            "success": False,
            "message": "User already exists",
        }), 409

    new_user = User(
        name=name,
        pin=pin,
        focus_led_color=focus_led_color,
        break_led_color=break_led_color,
    )

    db.session.add(new_user)
    db.session.flush()

    face_image_path = save_face_image(
        face_file,
        new_user.id,
        name,
    )

    new_user.face_image_path = face_image_path

    user_settings = UserSettings(
        user_id=new_user.id,
        temperature_threshold=temperature_threshold,
        default_focus_minutes=focus_minutes,
        default_break_minutes=break_minutes,
        default_led_color=focus_led_color,
        focus_led_color=focus_led_color,
        break_led_color=break_led_color,
        music_enabled=False,
    )

    db.session.add(user_settings)
    db.session.commit()

    safe_user = safe_user_from_db_user(new_user)

    auth_state = update_auth_state(
        locked=False,
        current_user=safe_user,
        login_method="register",
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message=f"New user registered: {name}",
        metadata={
            "user": safe_user,
            "method": "register",
            "source": "register_route",
        },
    )

    access_log = add_access_log(
        user=safe_user,
        method="register",
        success=True,
        message=f"Registration successful for {name}",
        metadata={
            "source": "register_route",
        },
    )

    settings_payload = {
        "focusLedColor": focus_led_color,
        "breakLedColor": break_led_color,
        "defaultFocusMinutes": focus_minutes,
        "defaultBreakMinutes": break_minutes,
        "temperatureThreshold": temperature_threshold,
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
        "accessLog": access_log,
    }), 201


@auth_bp.route("/face-login", methods=["POST"])
def face_login():
    seed_default_users_if_needed()

    uploaded_face, upload_error = get_uploaded_face_file(request.files)

    if upload_error:
        access_log = add_access_log(
            user=None,
            method="face_id",
            success=False,
            message=f"Face login failed: {upload_error['message']}",
            metadata={
                "source": "face_login_route",
                "reason": upload_error["reason"],
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            **upload_error,
            "accessLog": access_log,
        }), 400

    registered_faces = get_registered_face_files()

    if not registered_faces:
        access_log = add_access_log(
            user=None,
            method="face_id",
            success=False,
            message="Face login failed: no registered faces found",
            metadata={
                "source": "face_login_route",
                "registeredFacesDir": str(REGISTERED_FACES_DIR),
                "reason": "no_registered_faces",
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "No registered faces found",
            "reason": "no_registered_faces",
            "accessLog": access_log,
        }), 404

    temp_path = None

    try:
        temp_path = save_uploaded_face_temporarily(uploaded_face)

        best_match = None

        for registered_face_path in registered_faces:
            matched_user = find_user_by_face_filename(registered_face_path)

            if not matched_user:
                print(f"Skipping {registered_face_path.name}: no matching user in database")
                continue

            try:
                result = DeepFace.verify(
                    img1_path=temp_path,
                    img2_path=str(registered_face_path),
                    model_name="Facenet",
                    detector_backend="opencv",
                    enforce_detection=False,
                )

                if result.get("verified"):
                    best_match = {
                        "user": matched_user,
                        "registeredFace": registered_face_path.name,
                        "distance": result.get("distance"),
                        "threshold": result.get("threshold"),
                    }
                    break

            except Exception as compare_error:
                print(f"Face comparison failed for {registered_face_path.name}: {compare_error}")

        if not best_match:
            timeline_event = add_timeline_event(
                event_type="auth",
                message="Face ID failed, manual login required",
                metadata={
                    "method": "face_id",
                    "source": "face_login_route",
                    "reason": "no_matching_face",
                },
            )

            access_log = add_access_log(
                user=None,
                method="face_id",
                success=False,
                message="Face ID login failed: no matching face found",
                metadata={
                    "source": "face_login_route",
                    "reason": "no_matching_face",
                },
            )

            emit_socket_event("login_failed", {
                "reason": "No matching face found",
                "timelineEvent": timeline_event,
                "accessLog": access_log,
            })

            emit_socket_event("timeline_update", timeline_event)
            emit_socket_event("access_log_update", access_log)

            return jsonify({
                "success": False,
                "message": "No matching face found",
                "reason": "no_matching_face",
                "timelineEvent": timeline_event,
                "accessLog": access_log,
            }), 401

        safe_user = safe_user_from_db_user(best_match["user"])

        auth_state = update_auth_state(
            locked=False,
            current_user=safe_user,
            login_method="face_id",
        )

        timeline_event = add_timeline_event(
            event_type="auth",
            message=f"Face ID login successful for {safe_user['name']}",
            metadata={
                "user": safe_user,
                "method": "face_id",
                "source": "face_login_route",
                "registeredFace": best_match["registeredFace"],
                "distance": best_match["distance"],
                "threshold": best_match["threshold"],
            },
        )

        access_log = add_access_log(
            user=safe_user,
            method="face_id",
            success=True,
            message=f"Face ID login successful for {safe_user['name']}",
            metadata={
                "source": "face_login_route",
                "registeredFace": best_match["registeredFace"],
                "distance": best_match["distance"],
                "threshold": best_match["threshold"],
            },
        )

        emit_socket_event("auth_update", auth_state)
        emit_socket_event("timeline_update", timeline_event)
        emit_socket_event("access_log_update", access_log)

        emit_socket_event("login_success", {
            "user": safe_user,
            "auth": auth_state,
            "timelineEvent": timeline_event,
            "accessLog": access_log,
        })

        return jsonify({
            "success": True,
            "message": "Face login successful",
            "user": safe_user,
            "auth": auth_state,
            "timelineEvent": timeline_event,
            "accessLog": access_log,
        })

    except Exception as error:
        access_log = add_access_log(
            user=None,
            method="face_id",
            success=False,
            message="Face login failed because of a server error",
            metadata={
                "source": "face_login_route",
                "error": str(error),
            },
        )

        emit_socket_event("access_log_update", access_log)

        return jsonify({
            "success": False,
            "message": "Face login failed because of a server error",
            "error": str(error),
            "accessLog": access_log,
        }), 500

    finally:
        delete_temp_face_file(temp_path)


@auth_bp.route("/test", methods=["GET"])
def test_auth():
    return jsonify({
        "status": "ok",
        "message": "Auth routes are working",
    })


@auth_bp.route("/fake-face-success", methods=["POST", "GET"])
def fake_face_success():
    seed_default_users_if_needed()

    user = User.query.filter(
        func.lower(User.name) == "alex"
    ).first()

    if user:
        fake_user = safe_user_from_db_user(user)
    else:
        fake_user = {
            "id": None,
            "name": "Simulated User",
            "focusLedColor": "#d66b5d",
            "breakLedColor": "#65b891",
            "faceImagePath": None,
        }

    auth_state = update_auth_state(
        locked=False,
        current_user=fake_user,
        login_method="face_id",
    )

    timeline_event = add_timeline_event(
        event_type="auth",
        message="Zero-touch login successful by simulated Face ID",
        metadata={
            "user": fake_user,
            "method": "face_id",
            "source": "fake_backend_route",
        },
    )

    access_log = add_access_log(
        user=fake_user,
        method="face_id",
        success=True,
        message="Simulated Face ID login successful",
        metadata={
            "source": "fake_backend_route",
        },
    )

    emit_socket_event("login_success", {
        "user": fake_user,
        "auth": auth_state,
        "timelineEvent": timeline_event,
        "accessLog": access_log,
    })

    return jsonify({
        "status": "ok",
        "message": "Fake face login success triggered",
        "user": fake_user,
    })


@auth_bp.route("/fake-face-failure", methods=["POST", "GET"])
def fake_face_failure():
    timeline_event = add_timeline_event(
        event_type="auth",
        message="Face ID failed, manual login required",
        metadata={
            "method": "face_id",
            "source": "fake_backend_route",
        },
    )

    access_log = add_access_log(
        user=None,
        method="face_id",
        success=False,
        message="Simulated Face ID login failed",
        metadata={
            "source": "fake_backend_route",
        },
    )

    emit_socket_event("login_failed", {
        "reason": "No matching face found",
        "timelineEvent": timeline_event,
        "accessLog": access_log,
    })

    return jsonify({
        "status": "ok",
        "message": "Fake face login failure triggered",
        "reason": "No matching face found",
    })