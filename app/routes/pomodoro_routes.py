from flask import Blueprint, jsonify, request
from app.services.pomodoro_service import start_backend_timer

from app.services.device_state import (
    get_device_state,
    update_pomodoro_state,
    add_timeline_event,
    add_command,
    add_pomodoro_session
)

from app.services.socket_service import (
    emit_pomodoro_update,
    emit_timeline_update
)

pomodoro_bp = Blueprint("pomodoro", __name__)


@pomodoro_bp.route("/state", methods=["GET"])
def get_pomodoro_state():
    state = get_device_state()

    return jsonify({
        "status": "ok",
        "pomodoro": state["pomodoro"]
    })


@pomodoro_bp.route("/start", methods=["POST"])
def start_pomodoro():
    data = request.get_json() or {}
    state = get_device_state()

    focus_minutes = int(data.get(
        "focusMinutes",
        state["settings"].get("defaultFocusMinutes", 25)
    ))

    break_minutes = int(data.get(
        "breakMinutes",
        state["settings"].get("defaultBreakMinutes", 5)
    ))

    selected_task = data.get("selectedTask")

    pomodoro_data = update_pomodoro_state(
        running=True,
        mode="focus",
        remaining_seconds=focus_minutes * 60,
        focus_minutes=focus_minutes,
        break_minutes=break_minutes,
        selected_task=selected_task
    )

    command = add_command(
        command_type="START_POMODORO",
        value=True,
        payload={
            "focusMinutes": focus_minutes,
            "breakMinutes": break_minutes,
            "selectedTask": selected_task,
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message=f"Focus session started{f': {selected_task}' if selected_task else ''}",
        metadata={
            "focusMinutes": focus_minutes,
            "breakMinutes": break_minutes,
            "selectedTask": selected_task,
            "commandId": command["id"]
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    start_backend_timer()

    return jsonify({
        "status": "ok",
        "message": "Pomodoro started",
        "pomodoro": pomodoro_data,
        "command": command,
        "timelineEvent": timeline_event
    })


@pomodoro_bp.route("/pause", methods=["POST"])
def pause_pomodoro():
    state = get_device_state()
    current = state["pomodoro"]

    if not current["running"]:
        return jsonify({
            "status": "error",
            "message": "No running pomodoro to pause"
        }), 400

    pomodoro_data = update_pomodoro_state(
        running=False,
        mode="paused"
    )

    command = add_command(
        command_type="PAUSE_POMODORO",
        value=True,
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Pomodoro paused",
        metadata={
            "commandId": command["id"]
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Pomodoro paused",
        "pomodoro": pomodoro_data,
        "command": command,
        "timelineEvent": timeline_event
    })


@pomodoro_bp.route("/resume", methods=["POST"])
def resume_pomodoro():
    state = get_device_state()
    current = state["pomodoro"]

    if current["mode"] != "paused":
        return jsonify({
            "status": "error",
            "message": "Pomodoro is not paused"
        }), 400

    pomodoro_data = update_pomodoro_state(
        running=True,
        mode="focus"
    )

    command = add_command(
        command_type="RESUME_POMODORO",
        value=True,
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Pomodoro resumed",
        metadata={
            "commandId": command["id"]
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    start_backend_timer()

    return jsonify({
        "status": "ok",
        "message": "Pomodoro resumed",
        "pomodoro": pomodoro_data,
        "command": command,
        "timelineEvent": timeline_event
    })


@pomodoro_bp.route("/stop", methods=["POST"])
def stop_pomodoro():
    state = get_device_state()
    current = state["pomodoro"]

    pomodoro_data = update_pomodoro_state(
        running=False,
        mode="idle",
        remaining_seconds=current["focusMinutes"] * 60,
        ended_at=None
    )

    command = add_command(
        command_type="STOP_POMODORO",
        value=True,
        payload={
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Pomodoro stopped",
        metadata={
            "commandId": command["id"]
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Pomodoro stopped",
        "pomodoro": pomodoro_data,
        "command": command,
        "timelineEvent": timeline_event
    })


@pomodoro_bp.route("/complete", methods=["POST"])
def complete_pomodoro():
    data = request.get_json() or {}
    state = get_device_state()
    current = state["pomodoro"]

    notes = data.get("notes", "")
    completed_task = data.get("task", current.get("selectedTask"))

    pomodoro_data = update_pomodoro_state(
        running=False,
        mode="idle",
        remaining_seconds=current["focusMinutes"] * 60,
        ended_at=None
    )

    command = add_command(
        command_type="COMPLETE_POMODORO",
        value=True,
        payload={
            "task": completed_task,
            "notes": notes,
            "source": "dashboard"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message=f"Pomodoro completed{f': {completed_task}' if completed_task else ''}",
        metadata={
            "task": completed_task,
            "notes": notes,
            "focusMinutes": current["focusMinutes"],
            "breakMinutes": current["breakMinutes"],
            "deskAbsenceCount": current["deskAbsenceCount"],
            "commandId": command["id"]
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Pomodoro completed",
        "pomodoro": pomodoro_data,
        "command": command,
        "timelineEvent": timeline_event
    })

@pomodoro_bp.route("/session-ended", methods=["POST"])
def session_ended():
    data = request.get_json() or {}

    task = data.get("task", "")
    notes = data.get("notes", "")
    productive = data.get("productive", False)
    rating = data.get("rating")

    session = add_pomodoro_session(
        task=task,
        notes=notes,
        productive=productive,
        rating=rating,
        metadata={
            "source": "session_end_modal"
        }
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message=f"Pomodoro session saved{f': {task}' if task else ''}",
        metadata={
            "sessionId": session["id"],
            "task": task,
            "productive": productive,
            "rating": rating
        }
    )

    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Pomodoro session summary saved",
        "session": session,
        "timelineEvent": timeline_event
    })