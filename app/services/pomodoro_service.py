from datetime import datetime
import threading
import time

from flask import current_app

from app.services.device_state import (
    DEVICE_STATE,
    update_pomodoro_state,
    add_timeline_event,
    add_command
)

from app.services.socket_service import (
    emit_pomodoro_update,
    emit_timeline_update,
    emit_socket_event
)

_timer_generation = 0
_timer_lock = threading.Lock()


def start_backend_timer():
    """
    Starts a backend timer loop.
    Uses Flask app context so DB-backed timeline/session functions work safely.
    """

    global _timer_generation

    app = current_app._get_current_object()

    with _timer_lock:
        _timer_generation += 1
        my_generation = _timer_generation

    thread = threading.Thread(
        target=run_pomodoro_timer,
        args=(app, my_generation),
        daemon=True
    )

    thread.start()


def run_pomodoro_timer(app, my_generation):
    while True:
        time.sleep(1)

        with _timer_lock:
            if _timer_generation != my_generation:
                break

        with app.app_context():
            pomodoro = DEVICE_STATE["pomodoro"]

            if not pomodoro["running"]:
                break

            remaining = int(pomodoro["remainingSeconds"])

            if remaining > 0:
                updated_pomodoro = update_pomodoro_state(
                    remaining_seconds=remaining - 1
                )

                emit_pomodoro_update(updated_pomodoro)
                continue

            handle_timer_finished()


def handle_timer_finished():
    pomodoro = DEVICE_STATE["pomodoro"]
    current_mode = pomodoro["mode"]

    if current_mode == "focus":
        updated_pomodoro = update_pomodoro_state(
            running=True,
            mode="break",
            remaining_seconds=pomodoro["breakMinutes"] * 60
        )

        command = add_command(
            command_type="START_BREAK",
            value=True,
            payload={
                "source": "backend_timer"
            }
        )

        timeline_event = add_timeline_event(
            event_type="pomodoro",
            message="Break started automatically after focus session",
            metadata={
                "commandId": command["id"]
            }
        )

        emit_pomodoro_update(updated_pomodoro)
        emit_timeline_update(timeline_event)

        emit_socket_event("focus_session_ended", {
            "message": "Focus session ended",
            "pomodoro": updated_pomodoro,
            "timelineEvent": timeline_event
        })

        return

    if current_mode == "break":
        updated_pomodoro = update_pomodoro_state(
            running=False,
            mode="idle",
            remaining_seconds=pomodoro["focusMinutes"] * 60,
            ended_at=datetime.now().isoformat()
        )

        command = add_command(
            command_type="POMODORO_FINISHED",
            value=True,
            payload={
                "source": "backend_timer"
            }
        )

        timeline_event = add_timeline_event(
            event_type="pomodoro",
            message="Pomodoro cycle finished",
            metadata={
                "commandId": command["id"]
            }
        )

        emit_pomodoro_update(updated_pomodoro)
        emit_timeline_update(timeline_event)