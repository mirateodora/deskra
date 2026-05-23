from flask import Blueprint, jsonify, request

from app.services.device_state import (
    get_tasks,
    add_task,
    update_task,
    delete_task,
    add_timeline_event,
    add_command
)

from app.services.socket_service import (
    emit_socket_event,
    emit_timeline_update
)

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("", methods=["GET"])
def list_tasks():
    return jsonify({
        "status": "ok",
        "tasks": get_tasks()
    })


@tasks_bp.route("", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title = data.get("title", "").strip()

    if not title:
        return jsonify({
            "status": "error",
            "message": "Task title is required"
        }), 400

    task = add_task(title)

    timeline_event = add_timeline_event(
        event_type="task",
        message=f"Task created: {title}",
        metadata={
            "taskId": task["id"]
        }
    )

    emit_socket_event("tasks_update", get_tasks())
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Task created",
        "task": task,
        "tasks": get_tasks(),
        "timelineEvent": timeline_event
    }), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
def edit_task(task_id):
    data = request.get_json() or {}

    task = update_task(
        task_id=task_id,
        title=data.get("title"),
        completed=data.get("completed") if "completed" in data else None,
        selected=data.get("selected") if "selected" in data else None
    )

    if not task:
        return jsonify({
            "status": "error",
            "message": "Task not found"
        }), 404

    timeline_message = "Task updated"

    if "completed" in data and data.get("completed"):
        timeline_message = f"Task completed: {task['title']}"

    if "selected" in data and data.get("selected"):
        command = add_command(
            command_type="SET_ACTIVE_TASK",
            value=task["title"],
            payload={
                "taskId": task["id"],
                "title": task["title"],
                "source": "dashboard"
            }
        )

        timeline_message = f"Selected task for pomodoro: {task['title']}"

    timeline_event = add_timeline_event(
        event_type="task",
        message=timeline_message,
        metadata={
            "taskId": task["id"],
            "title": task["title"],
            "completed": task["completed"],
            "selected": task["selected"]
        }
    )

    emit_socket_event("tasks_update", get_tasks())
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Task updated",
        "task": task,
        "tasks": get_tasks(),
        "timelineEvent": timeline_event
    })


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):
    task = delete_task(task_id)

    if not task:
        return jsonify({
            "status": "error",
            "message": "Task not found"
        }), 404

    timeline_event = add_timeline_event(
        event_type="task",
        message=f"Task deleted: {task['title']}",
        metadata={
            "taskId": task["id"]
        }
    )

    emit_socket_event("tasks_update", get_tasks())
    emit_timeline_update(timeline_event)

    return jsonify({
        "status": "ok",
        "message": "Task deleted",
        "task": task,
        "tasks": get_tasks(),
        "timelineEvent": timeline_event
    })