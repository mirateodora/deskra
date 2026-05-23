from datetime import datetime

from app.extensions import socketio

from app.services.device_state import (
    get_device_state,
    update_pomodoro_state,
    add_timeline_event,
    add_command
)

from app.services.socket_service import (
    emit_pomodoro_update,
    emit_timeline_update,
    emit_socket_event
)

pomodoro_task_running = False


def start_backend_timer():
    """
    Starts one backend timer loop.
    The loop decreases remainingSeconds while pomodoro is running.
    """

    global pomodoro_task_running

    if pomodoro_task_running:
        return

    pomodoro_task_running = True
    socketio.start_background_task(run_pomodoro_timer)


def run_pomodoro_timer():
    global pomodoro_task_running

    while True:
        socketio.sleep(1)

        state = get_device_state()
        pomodoro = state["pomodoro"]

        if not pomodoro["running"]:
            pomodoro_task_running = False
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
    state = get_device_state()
    pomodoro = state["pomodoro"]

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