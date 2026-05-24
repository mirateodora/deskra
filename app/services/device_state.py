import uuid
from datetime import datetime

from app.extensions import db
from app.models import TimelineEvent, AccessLog, PomodoroSession, Task


DEVICE_STATE = {
    "device": {
        "id": "deskra-esp32-001",
        "connected": False,
        "mode": "simulator",
        "lastUpdate": None
    },

    "sensors": {
        "temperature": None,
        "humidity": None,
        "presence": False,
        "lastUpdate": None
    },

    "actuators": {
        "fan": False,
        "ledColor": "#ff0000",
        "manualFanOverride": False
    },

    "auth": {
        "locked": True,
        "currentUser": None,
        "loginMethod": None
    },

    "pomodoro": {
        "running": False,
        "mode": "idle",
        "pausedMode": None,
        "remainingSeconds": 25 * 60,
        "focusMinutes": 25,
        "breakMinutes": 5,
        "selectedTask": None,
        "startedAt": None,
        "endedAt": None,
        "deskAbsenceCount": 0
    },

    "settings": {
        "temperatureThreshold": 26,
        "defaultFocusMinutes": 25,
        "defaultBreakMinutes": 5,
        "defaultLedColor": "#d66b5d",
        "focusLedColor": "#d66b5d",
        "breakLedColor": "#65b891",
        "musicEnabled": False
    },

    # These are now DB-backed through get_timeline_events()
    # and get_access_logs().
    "timeline": [],
    "accessLogs": [],

    "tasks": [],

    "pomodoroSessions": [],

    "commands": [],

    "sensorReadings": [],
}


def now_iso():
    return datetime.now().isoformat()

def parse_iso_datetime(value):
    if not value:
        return None

    if isinstance(value, datetime):
        return value

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def get_timeline_events(limit=100):
    events = (
        TimelineEvent.query
        .order_by(TimelineEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [event.to_dict() for event in events]


def get_access_logs(limit=100):
    logs = (
        AccessLog.query
        .order_by(AccessLog.timestamp.desc())
        .limit(limit)
        .all()
    )

    return [log.to_dict() for log in logs]


def get_device_state():
    state = {
        **DEVICE_STATE,
        "timeline": get_timeline_events(),
        "accessLogs": get_access_logs(),
        "pomodoroSessions": get_pomodoro_sessions(),
        "tasks": get_tasks(),
    }

    return state


def update_device_timestamp():
    now = now_iso()

    DEVICE_STATE["device"]["connected"] = True
    DEVICE_STATE["device"]["lastUpdate"] = now
    DEVICE_STATE["sensors"]["lastUpdate"] = now

    return now


def update_sensors(temperature=None, humidity=None, presence=None):
    if temperature is not None:
        DEVICE_STATE["sensors"]["temperature"] = temperature

    if humidity is not None:
        DEVICE_STATE["sensors"]["humidity"] = humidity

    if presence is not None:
        DEVICE_STATE["sensors"]["presence"] = presence

    update_device_timestamp()

    return DEVICE_STATE["sensors"]


def update_fan_state(state):
    DEVICE_STATE["actuators"]["fan"] = bool(state)

    return DEVICE_STATE["actuators"]


def update_led_color(color):
    DEVICE_STATE["actuators"]["ledColor"] = color

    return DEVICE_STATE["actuators"]


def update_auth_state(locked=None, current_user=None, login_method=None):
    if locked is not None:
        DEVICE_STATE["auth"]["locked"] = bool(locked)

    if current_user is not None:
        DEVICE_STATE["auth"]["currentUser"] = current_user

    if login_method is not None:
        DEVICE_STATE["auth"]["loginMethod"] = login_method

    return DEVICE_STATE["auth"]


def logout_user():
    DEVICE_STATE["auth"]["locked"] = True
    DEVICE_STATE["auth"]["currentUser"] = None
    DEVICE_STATE["auth"]["loginMethod"] = None

    return DEVICE_STATE["auth"]


def update_pomodoro_state(
    running=None,
    mode=None,
    remaining_seconds=None,
    focus_minutes=None,
    break_minutes=None,
    selected_task=None,
    started_at=None,
    ended_at=None,
    desk_absence_count=None,
    paused_mode=None
):
    if running is not None:
        DEVICE_STATE["pomodoro"]["running"] = bool(running)

    if mode is not None:
        DEVICE_STATE["pomodoro"]["mode"] = mode

    if remaining_seconds is not None:
        DEVICE_STATE["pomodoro"]["remainingSeconds"] = int(remaining_seconds)

    if focus_minutes is not None:
        DEVICE_STATE["pomodoro"]["focusMinutes"] = int(focus_minutes)

    if break_minutes is not None:
        DEVICE_STATE["pomodoro"]["breakMinutes"] = int(break_minutes)

    if selected_task is not None:
        DEVICE_STATE["pomodoro"]["selectedTask"] = selected_task

    if started_at is not None:
        DEVICE_STATE["pomodoro"]["startedAt"] = started_at

    if ended_at is not None:
        DEVICE_STATE["pomodoro"]["endedAt"] = ended_at

    if desk_absence_count is not None:
        DEVICE_STATE["pomodoro"]["deskAbsenceCount"] = int(desk_absence_count)

    if paused_mode is not None:
        DEVICE_STATE["pomodoro"]["pausedMode"] = paused_mode

    return DEVICE_STATE["pomodoro"]


def update_settings(
    temperature_threshold=None,
    default_focus_minutes=None,
    default_break_minutes=None,
    default_led_color=None,
    music_enabled=None
):
    if temperature_threshold is not None:
        DEVICE_STATE["settings"]["temperatureThreshold"] = float(temperature_threshold)

    if default_focus_minutes is not None:
        DEVICE_STATE["settings"]["defaultFocusMinutes"] = int(default_focus_minutes)

    if default_break_minutes is not None:
        DEVICE_STATE["settings"]["defaultBreakMinutes"] = int(default_break_minutes)

    if default_led_color is not None:
        DEVICE_STATE["settings"]["defaultLedColor"] = default_led_color

    if music_enabled is not None:
        DEVICE_STATE["settings"]["musicEnabled"] = bool(music_enabled)

    return DEVICE_STATE["settings"]


def set_device_connected(is_connected):
    DEVICE_STATE["device"]["connected"] = bool(is_connected)

    if is_connected:
        DEVICE_STATE["device"]["lastUpdate"] = now_iso()

    return DEVICE_STATE["device"]


def reset_device_state():
    DEVICE_STATE["device"]["connected"] = False
    DEVICE_STATE["device"]["lastUpdate"] = None

    DEVICE_STATE["sensors"]["temperature"] = None
    DEVICE_STATE["sensors"]["humidity"] = None
    DEVICE_STATE["sensors"]["presence"] = False
    DEVICE_STATE["sensors"]["lastUpdate"] = None

    DEVICE_STATE["actuators"]["fan"] = False
    DEVICE_STATE["actuators"]["ledColor"] = DEVICE_STATE["settings"]["defaultLedColor"]

    DEVICE_STATE["auth"]["locked"] = True
    DEVICE_STATE["auth"]["currentUser"] = None
    DEVICE_STATE["auth"]["loginMethod"] = None

    DEVICE_STATE["pomodoro"]["running"] = False
    DEVICE_STATE["pomodoro"]["mode"] = "idle"
    DEVICE_STATE["pomodoro"]["pausedMode"] = None
    DEVICE_STATE["pomodoro"]["remainingSeconds"] = DEVICE_STATE["settings"]["defaultFocusMinutes"] * 60
    DEVICE_STATE["pomodoro"]["selectedTask"] = None
    DEVICE_STATE["pomodoro"]["startedAt"] = None
    DEVICE_STATE["pomodoro"]["endedAt"] = None
    DEVICE_STATE["pomodoro"]["deskAbsenceCount"] = 0

    return get_device_state()


def add_timeline_event(event_type, message, metadata=None):
    if metadata is None:
        metadata = {}

    event = TimelineEvent(
        type=event_type,
        message=message,
        metadata_json=metadata,
    )

    db.session.add(event)
    db.session.commit()

    return event.to_dict()


def clear_timeline():
    TimelineEvent.query.delete()
    db.session.commit()

    return []


def add_access_log(user=None, method="unknown", success=False, message="", metadata=None):
    if metadata is None:
        metadata = {}

    user_id = None

    if isinstance(user, dict):
        user_id = user.get("id")

    log = AccessLog(
        user_id=user_id,
        user_snapshot=user,
        method=method,
        success=bool(success),
        message=message,
        metadata_json=metadata,
    )

    db.session.add(log)
    db.session.commit()

    return log.to_dict()


def clear_access_logs():
    AccessLog.query.delete()
    db.session.commit()

    return []


def add_command(command_type, value=None, payload=None):
    if payload is None:
        payload = {}

    command = {
        "id": str(uuid.uuid4()),
        "type": command_type,
        "value": value,
        "payload": payload,
        "status": "pending",
        "createdAt": now_iso()
    }

    DEVICE_STATE["commands"].append(command)

    return command


def get_pending_commands():
    return [
        command for command in DEVICE_STATE["commands"]
        if command["status"] == "pending"
    ]


def consume_pending_commands():
    pending_commands = get_pending_commands()

    for command in pending_commands:
        command["status"] = "consumed"
        command["consumedAt"] = now_iso()

    return pending_commands


def clear_commands():
    DEVICE_STATE["commands"] = []
    return DEVICE_STATE["commands"]


def set_manual_fan_override(is_override):
    DEVICE_STATE["actuators"]["manualFanOverride"] = bool(is_override)
    return DEVICE_STATE["actuators"]


def clear_manual_fan_override():
    DEVICE_STATE["actuators"]["manualFanOverride"] = False
    return DEVICE_STATE["actuators"]


def add_pomodoro_session(task=None, notes="", productive=False, rating=None, metadata=None):
    if metadata is None:
        metadata = {}

    current_user = DEVICE_STATE["auth"]["currentUser"]

    user_id = None
    if isinstance(current_user, dict):
        user_id = current_user.get("id")

    session = PomodoroSession(
        user_id=user_id,
        user_snapshot=current_user,
        task=task,
        notes=notes or "",
        productive=bool(productive),
        rating=rating,
        focus_minutes=DEVICE_STATE["pomodoro"]["focusMinutes"],
        break_minutes=DEVICE_STATE["pomodoro"]["breakMinutes"],
        desk_absence_count=DEVICE_STATE["pomodoro"]["deskAbsenceCount"],
        started_at=parse_iso_datetime(DEVICE_STATE["pomodoro"]["startedAt"]),
        ended_at=datetime.now(),
        metadata_json=metadata,
    )

    db.session.add(session)
    db.session.commit()

    return session.to_dict()


def get_pomodoro_sessions(limit=100):
    sessions = (
        PomodoroSession.query
        .order_by(PomodoroSession.created_at.desc())
        .limit(limit)
        .all()
    )

    return [session.to_dict() for session in sessions]

def get_tasks():
    tasks = (
        Task.query
        .order_by(Task.created_at.desc())
        .all()
    )

    return [task.to_dict() for task in tasks]


def add_task(title):
    task = Task(
        title=title,
        completed=False,
        selected=False,
    )

    db.session.add(task)
    db.session.commit()

    return task.to_dict()


def update_task(task_id, title=None, completed=None, selected=None):
    task = db.session.get(Task, int(task_id))

    if not task:
        return None

    if title is not None:
        task.title = title

    if completed is not None:
        task.completed = bool(completed)

    if selected is not None:
        task.selected = bool(selected)

        if selected:
            Task.query.filter(Task.id != task.id).update({
                Task.selected: False
            })

            DEVICE_STATE["pomodoro"]["selectedTask"] = task.title
        else:
            if DEVICE_STATE["pomodoro"]["selectedTask"] == task.title:
                DEVICE_STATE["pomodoro"]["selectedTask"] = None

    db.session.commit()

    return task.to_dict()


def delete_task(task_id):
    task = db.session.get(Task, int(task_id))

    if not task:
        return None

    task_dict = task.to_dict()

    if DEVICE_STATE["pomodoro"]["selectedTask"] == task.title:
        DEVICE_STATE["pomodoro"]["selectedTask"] = None

    db.session.delete(task)
    db.session.commit()

    return task_dict


def get_selected_task():
    task = (
        Task.query
        .filter_by(selected=True)
        .order_by(Task.updated_at.desc())
        .first()
    )

    if not task:
        return None

    return task.to_dict()

def add_sensor_reading(temperature=None, humidity=None, presence=None, metadata=None):
    if metadata is None:
        metadata = {}

    reading = {
        "id": len(DEVICE_STATE["sensorReadings"]) + 1,
        "temperature": temperature,
        "humidity": humidity,
        "presence": presence,
        "timestamp": now_iso(),
        "metadata": metadata
    }

    DEVICE_STATE["sensorReadings"].insert(0, reading)

    return reading


def get_sensor_readings():
    return DEVICE_STATE["sensorReadings"]
