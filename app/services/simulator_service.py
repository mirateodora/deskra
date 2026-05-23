import random

from app.services.device_state import (
    get_device_state,
    update_sensors,
    update_fan_state,
    update_pomodoro_state,
    set_device_connected,
    add_timeline_event
)

from app.services.socket_service import (
    emit_sensor_update,
    emit_actuator_update,
    emit_pomodoro_update,
    emit_timeline_update,
    emit_state_update
)


def simulate_sensor_values():
    temperature = round(random.uniform(22.0, 29.0), 1)
    humidity = random.randint(35, 65)

    sensor_data = update_sensors(
        temperature=temperature,
        humidity=humidity
    )

    set_device_connected(True)

    emit_sensor_update(sensor_data)

    timeline_event = add_timeline_event(
        event_type="simulator",
        message=f"Simulator updated sensors: {temperature}°C, {humidity}% humidity",
        metadata={
            "temperature": temperature,
            "humidity": humidity
        }
    )

    emit_timeline_update(timeline_event)

    return sensor_data


def simulate_presence_detected():
    sensor_data = update_sensors(presence=True)

    set_device_connected(True)

    emit_sensor_update(sensor_data)

    timeline_event = add_timeline_event(
        event_type="sensor",
        message="Presence detected by simulated ultrasonic sensor",
        metadata={
            "source": "simulator"
        }
    )

    emit_timeline_update(timeline_event)

    return sensor_data


def simulate_presence_lost():
    sensor_data = update_sensors(presence=False)

    set_device_connected(True)

    emit_sensor_update(sensor_data)

    timeline_event = add_timeline_event(
        event_type="sensor",
        message="Presence lost by simulated ultrasonic sensor",
        metadata={
            "source": "simulator"
        }
    )

    emit_timeline_update(timeline_event)

    return sensor_data


def simulate_temperature_increase():
    state = get_device_state()
    current_temperature = state["sensors"]["temperature"]

    if current_temperature is None:
        current_temperature = 24.0

    next_temperature = round(float(current_temperature) + 1.5, 1)

    sensor_data = update_sensors(
        temperature=next_temperature,
        humidity=state["sensors"]["humidity"] or 48
    )

    set_device_connected(True)

    emit_sensor_update(sensor_data)

    timeline_event = add_timeline_event(
        event_type="sensor",
        message=f"Temperature increased to {next_temperature}°C",
        metadata={
            "source": "simulator",
            "temperature": next_temperature
        }
    )

    emit_timeline_update(timeline_event)

    return sensor_data


def simulate_fan_on():
    actuator_data = update_fan_state(True)

    timeline_event = add_timeline_event(
        event_type="actuator",
        message="Fan turned on by simulator",
        metadata={
            "source": "simulator"
        }
    )

    emit_actuator_update(actuator_data)
    emit_timeline_update(timeline_event)

    return actuator_data


def simulate_fan_off():
    actuator_data = update_fan_state(False)

    timeline_event = add_timeline_event(
        event_type="actuator",
        message="Fan turned off by simulator",
        metadata={
            "source": "simulator"
        }
    )

    emit_actuator_update(actuator_data)
    emit_timeline_update(timeline_event)

    return actuator_data


def simulate_pomodoro_focus():
    state = get_device_state()

    pomodoro_data = update_pomodoro_state(
        running=True,
        mode="focus",
        remaining_seconds=state["pomodoro"]["focusMinutes"] * 60
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Focus session started by simulator",
        metadata={
            "source": "simulator"
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return pomodoro_data


def simulate_pomodoro_break():
    state = get_device_state()

    pomodoro_data = update_pomodoro_state(
        running=True,
        mode="break",
        remaining_seconds=state["pomodoro"]["breakMinutes"] * 60
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Break session started by simulator",
        metadata={
            "source": "simulator"
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return pomodoro_data


def simulate_pomodoro_finished():
    state = get_device_state()

    pomodoro_data = update_pomodoro_state(
        running=False,
        mode="idle",
        remaining_seconds=state["pomodoro"]["focusMinutes"] * 60
    )

    timeline_event = add_timeline_event(
        event_type="pomodoro",
        message="Pomodoro session finished by simulator",
        metadata={
            "source": "simulator"
        }
    )

    emit_pomodoro_update(pomodoro_data)
    emit_timeline_update(timeline_event)

    return pomodoro_data


def simulate_device_disconnect():
    device_data = set_device_connected(False)

    timeline_event = add_timeline_event(
        event_type="device",
        message="Simulated ESP32 disconnected",
        metadata={
            "source": "simulator"
        }
    )

    emit_timeline_update(timeline_event)
    emit_state_update(get_device_state())

    return device_data