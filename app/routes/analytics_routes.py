from datetime import datetime, timedelta

from flask import Blueprint, jsonify

from app.services.device_state import get_device_state

analytics_bp = Blueprint("analytics", __name__)


def parse_time(value):
    if not value:
        return None

    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def average(values):
    clean_values = [value for value in values if value is not None]

    if not clean_values:
        return None

    return round(sum(clean_values) / len(clean_values), 1)


def get_events_for_period(items, start_time):
    filtered = []

    for item in items:
        item_time = parse_time(item.get("timestamp") or item.get("createdAt"))

        if item_time and item_time >= start_time:
            filtered.append(item)

    return filtered


@analytics_bp.route("/summary", methods=["GET"])
def analytics_summary():
    state = get_device_state()

    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)

    timeline = state.get("timeline", [])
    sensor_readings = state.get("sensorReadings", [])
    pomodoro_sessions = state.get("pomodoroSessions", [])
    tasks = state.get("tasks", [])

    today_timeline = get_events_for_period(timeline, today_start)
    week_timeline = get_events_for_period(timeline, week_start)

    today_readings = get_events_for_period(sensor_readings, today_start)
    week_readings = get_events_for_period(sensor_readings, week_start)

    today_sessions = get_events_for_period(pomodoro_sessions, today_start)
    week_sessions = get_events_for_period(pomodoro_sessions, week_start)

    completed_tasks = [
        task for task in tasks
        if task.get("completed")
    ]

    today_completed_tasks = get_events_for_period(completed_tasks, today_start)
    week_completed_tasks = get_events_for_period(completed_tasks, week_start)

    today_focus_minutes = sum(
        session.get("focusMinutes", 0)
        for session in today_sessions
    )

    week_focus_minutes = sum(
        session.get("focusMinutes", 0)
        for session in week_sessions
    )

    today_desk_absences = sum(
        session.get("deskAbsenceCount", 0)
        for session in today_sessions
    )

    week_desk_absences = sum(
        session.get("deskAbsenceCount", 0)
        for session in week_sessions
    )

    today_fan_activations = len([
        event for event in today_timeline
        if event.get("type") == "actuator"
        and "fan" in event.get("message", "").lower()
        and (
            "on" in event.get("message", "").lower()
            or "triggered" in event.get("message", "").lower()
        )
    ])

    week_fan_activations = len([
        event for event in week_timeline
        if event.get("type") == "actuator"
        and "fan" in event.get("message", "").lower()
        and (
            "on" in event.get("message", "").lower()
            or "triggered" in event.get("message", "").lower()
        )
    ])

    today_average_temperature = average([
        reading.get("temperature")
        for reading in today_readings
    ])

    week_average_temperature = average([
        reading.get("temperature")
        for reading in week_readings
    ])

    today_average_humidity = average([
        reading.get("humidity")
        for reading in today_readings
    ])

    week_average_humidity = average([
        reading.get("humidity")
        for reading in week_readings
    ])

    return jsonify({
        "status": "ok",
        "today": {
            "focusMinutes": today_focus_minutes,
            "sessions": len(today_sessions),
            "deskAbsences": today_desk_absences,
            "fanActivations": today_fan_activations,
            "averageTemperature": today_average_temperature,
            "averageHumidity": today_average_humidity,
            "completedTasks": len(today_completed_tasks)
        },
        "week": {
            "focusMinutes": week_focus_minutes,
            "sessions": len(week_sessions),
            "deskAbsences": week_desk_absences,
            "fanActivations": week_fan_activations,
            "averageTemperature": week_average_temperature,
            "averageHumidity": week_average_humidity,
            "completedTasks": len(week_completed_tasks)
        }
    })