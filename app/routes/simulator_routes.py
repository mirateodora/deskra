from flask import Blueprint, jsonify

from app.services.simulator_service import (
    simulate_sensor_values,
    simulate_presence_detected,
    simulate_presence_lost,
    simulate_temperature_increase,
    simulate_fan_on,
    simulate_fan_off,
    simulate_pomodoro_focus,
    simulate_pomodoro_break,
    simulate_pomodoro_finished,
    simulate_device_disconnect
)

simulator_bp = Blueprint("simulator", __name__)

simulator_running = False


@simulator_bp.route("/start", methods=["POST", "GET"])
def start_simulator():
    global simulator_running

    simulator_running = True
    sensor_data = simulate_sensor_values()

    return jsonify({
        "status": "ok",
        "message": "Simulator started",
        "running": simulator_running,
        "sensors": sensor_data
    })


@simulator_bp.route("/stop", methods=["POST", "GET"])
def stop_simulator():
    global simulator_running

    simulator_running = False
    device_data = simulate_device_disconnect()

    return jsonify({
        "status": "ok",
        "message": "Simulator stopped",
        "running": simulator_running,
        "device": device_data
    })


@simulator_bp.route("/status", methods=["GET"])
def simulator_status():
    return jsonify({
        "status": "ok",
        "running": simulator_running
    })


@simulator_bp.route("/sensors", methods=["POST", "GET"])
def simulator_sensors():
    sensor_data = simulate_sensor_values()

    return jsonify({
        "status": "ok",
        "message": "Fake sensor values generated",
        "sensors": sensor_data
    })


@simulator_bp.route("/presence/detected", methods=["POST", "GET"])
def simulator_presence_detected():
    sensor_data = simulate_presence_detected()

    return jsonify({
        "status": "ok",
        "message": "Fake presence detected",
        "sensors": sensor_data
    })


@simulator_bp.route("/presence/lost", methods=["POST", "GET"])
def simulator_presence_lost():
    sensor_data = simulate_presence_lost()

    return jsonify({
        "status": "ok",
        "message": "Fake presence lost",
        "sensors": sensor_data
    })


@simulator_bp.route("/temperature/increase", methods=["POST", "GET"])
def simulator_temperature_increase():
    sensor_data = simulate_temperature_increase()

    return jsonify({
        "status": "ok",
        "message": "Fake temperature increased",
        "sensors": sensor_data
    })


@simulator_bp.route("/fan/on", methods=["POST", "GET"])
def simulator_fan_on():
    actuator_data = simulate_fan_on()

    return jsonify({
        "status": "ok",
        "message": "Fake fan turned on",
        "actuators": actuator_data
    })


@simulator_bp.route("/fan/off", methods=["POST", "GET"])
def simulator_fan_off():
    actuator_data = simulate_fan_off()

    return jsonify({
        "status": "ok",
        "message": "Fake fan turned off",
        "actuators": actuator_data
    })


@simulator_bp.route("/pomodoro/focus", methods=["POST", "GET"])
def simulator_pomodoro_focus():
    pomodoro_data = simulate_pomodoro_focus()

    return jsonify({
        "status": "ok",
        "message": "Fake focus session started",
        "pomodoro": pomodoro_data
    })


@simulator_bp.route("/pomodoro/break", methods=["POST", "GET"])
def simulator_pomodoro_break():
    pomodoro_data = simulate_pomodoro_break()

    return jsonify({
        "status": "ok",
        "message": "Fake break session started",
        "pomodoro": pomodoro_data
    })


@simulator_bp.route("/pomodoro/finished", methods=["POST", "GET"])
def simulator_pomodoro_finished():
    pomodoro_data = simulate_pomodoro_finished()

    return jsonify({
        "status": "ok",
        "message": "Fake pomodoro finished",
        "pomodoro": pomodoro_data
    })


@simulator_bp.route("/disconnect", methods=["POST", "GET"])
def simulator_disconnect():
    device_data = simulate_device_disconnect()

    return jsonify({
        "status": "ok",
        "message": "Fake ESP32 disconnected",
        "device": device_data
    })