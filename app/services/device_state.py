from datetime import datetime


DEVICE_STATE = {
    "device": {
        "id": "deskra-esp32-001",
        "connected": False,
        "mode": "simulator",  # simulator or real
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
        "mode": "idle",  # idle, focus, break, paused
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

    "timeline": [],

    "accessLogs": [],

    "tasks": [],

    "pomodoroSessions": [],

    "commands": [],

    "sensorReadings": [],
}

def now_iso():
    return datetime.now().isoformat()

def get_device_state():
    return DEVICE_STATE


def update_device_timestamp():
    now = now_iso()

    DEVICE_STATE["device"]["connected"] = True
    DEVICE_STATE["device"]["lastUpdate"] = now
    DEVICE_STATE["sensors"]["lastUpdate"] = now

    return now

def update_sensors(temperature=None, humidity=None, presence=None):
    """
    Updates temperature, humidity, and presence.
    Used later by ESP32 or simulator.
    """

    if temperature is not None:
        DEVICE_STATE["sensors"]["temperature"] = temperature

    if humidity is not None:
        DEVICE_STATE["sensors"]["humidity"] = humidity

    if presence is not None:
        DEVICE_STATE["sensors"]["presence"] = presence

    update_device_timestamp()

    return DEVICE_STATE["sensors"]


def update_fan_state(state):
    """
    Updates fan state.
    state should be True or False.
    """

    DEVICE_STATE["actuators"]["fan"] = bool(state)

    return DEVICE_STATE["actuators"]


def update_led_color(color):
    """
    Updates LED color.
    Example: #ff0000
    """

    DEVICE_STATE["actuators"]["ledColor"] = color

    return DEVICE_STATE["actuators"]


def update_auth_state(locked=None, current_user=None, login_method=None):
    """
    Updates locked/unlocked state and current user.
    """

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
    desk_absence_count=None
):
    """
    Updates pomodoro state.
    """

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

    return DEVICE_STATE["pomodoro"]


def update_settings(
    temperature_threshold=None,
    default_focus_minutes=None,
    default_break_minutes=None,
    default_led_color=None,
    music_enabled=None
):
    """
    Updates dashboard/user settings.
    """

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
    """
    Useful during development/testing.
    Resets only dynamic values, not default settings.
    """

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
    DEVICE_STATE["pomodoro"]["remainingSeconds"] = DEVICE_STATE["settings"]["defaultFocusMinutes"] * 60
    DEVICE_STATE["pomodoro"]["selectedTask"] = None
    DEVICE_STATE["pomodoro"]["startedAt"] = None
    DEVICE_STATE["pomodoro"]["endedAt"] = None
    DEVICE_STATE["pomodoro"]["deskAbsenceCount"] = 0

    return DEVICE_STATE

def add_timeline_event(event_type, message, metadata=None):
    """
    Adds an event to the dashboard timeline.
    Example:
    09:15 - Focus Session Started: Write API endpoints
    """

    if metadata is None:
        metadata = {}

    event = {
        "id": len(DEVICE_STATE["timeline"]) + 1,
        "type": event_type,
        "message": message,
        "metadata": metadata,
        "timestamp": now_iso()
    }

    DEVICE_STATE["timeline"].insert(0, event)

    return event

def clear_timeline():
    DEVICE_STATE["timeline"] = []
    return DEVICE_STATE["timeline"]

def add_access_log(user=None, method="unknown", success=False, message="", metadata=None):
    """
    Adds an access/login attempt log.

    Examples:
    - Face ID success
    - Face ID failed
    - Manual PIN login success
    - Manual PIN login failed
    """

    if metadata is None:
        metadata = {}

    log = {
        "id": len(DEVICE_STATE["accessLogs"]) + 1,
        "user": user,
        "method": method,
        "success": bool(success),
        "message": message,
        "metadata": metadata,
        "timestamp": now_iso()
    }

    DEVICE_STATE["accessLogs"].insert(0, log)

    return log

def clear_access_logs():
    DEVICE_STATE["accessLogs"] = []
    return DEVICE_STATE["accessLogs"]

def add_command(command_type, value=None, payload=None):
    """
    Adds a command that the ESP32 will later fetch.

    Examples:
    - SET_FAN
    - SET_LED_COLOR
    - START_POMODORO
    - STOP_POMODORO
    - UPDATE_SETTINGS
    """

    if payload is None:
        payload = {}

    command = {
        "id": len(DEVICE_STATE["commands"]) + 1,
        "type": command_type,
        "value": value,
        "payload": payload,
        "status": "pending",
        "createdAt": now_iso()
    }

    DEVICE_STATE["commands"].append(command)

    return command


def get_pending_commands():
    """
    Returns all commands that have not been consumed by ESP32 yet.
    """

    return [
        command for command in DEVICE_STATE["commands"]
        if command["status"] == "pending"
    ]


def consume_pending_commands():
    """
    Returns pending commands and marks them as consumed.

    Later, ESP32 will call this route:
    GET /api/device/commands
    """

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

    session = {
        "id": len(DEVICE_STATE["pomodoroSessions"]) + 1,
        "user": DEVICE_STATE["auth"]["currentUser"],
        "task": task,
        "notes": notes,
        "productive": bool(productive),
        "rating": rating,
        "focusMinutes": DEVICE_STATE["pomodoro"]["focusMinutes"],
        "breakMinutes": DEVICE_STATE["pomodoro"]["breakMinutes"],
        "deskAbsenceCount": DEVICE_STATE["pomodoro"]["deskAbsenceCount"],
        "startedAt": DEVICE_STATE["pomodoro"]["startedAt"],
        "endedAt": now_iso(),
        "metadata": metadata,
        "createdAt": now_iso()
    }

    DEVICE_STATE["pomodoroSessions"].insert(0, session)

    return session


def get_pomodoro_sessions():
    return DEVICE_STATE["pomodoroSessions"]

def get_tasks():
    return DEVICE_STATE["tasks"]


def add_task(title):
    task = {
        "id": len(DEVICE_STATE["tasks"]) + 1,
        "title": title,
        "completed": False,
        "selected": False,
        "createdAt": now_iso(),
        "updatedAt": now_iso()
    }

    DEVICE_STATE["tasks"].insert(0, task)

    return task


def update_task(task_id, title=None, completed=None, selected=None):
    task_id = int(task_id)

    for task in DEVICE_STATE["tasks"]:
        if task["id"] == task_id:
            if title is not None:
                task["title"] = title

            if completed is not None:
                task["completed"] = bool(completed)

            if selected is not None:
                task["selected"] = bool(selected)

                if selected:
                    for other_task in DEVICE_STATE["tasks"]:
                        if other_task["id"] != task_id:
                            other_task["selected"] = False

                    DEVICE_STATE["pomodoro"]["selectedTask"] = task["title"]

            task["updatedAt"] = now_iso()

            return task

    return None


def delete_task(task_id):
    task_id = int(task_id)

    for task in DEVICE_STATE["tasks"]:
        if task["id"] == task_id:
            DEVICE_STATE["tasks"].remove(task)

            if DEVICE_STATE["pomodoro"]["selectedTask"] == task["title"]:
                DEVICE_STATE["pomodoro"]["selectedTask"] = None

            return task

    return None


def get_selected_task():
    for task in DEVICE_STATE["tasks"]:
        if task.get("selected"):
            return task

    return None

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