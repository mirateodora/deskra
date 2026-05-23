from app.services.device_state import (
    get_device_state,
    update_fan_state,
    add_timeline_event,
    add_command
)

from app.services.socket_service import (
    emit_actuator_update,
    emit_timeline_update,
    emit_socket_event
)


def evaluate_auto_fan():
    """
    Compares current temperature with threshold.
    Turns fan on/off automatically if manual override is not active.
    """

    state = get_device_state()

    temperature = state["sensors"].get("temperature")
    threshold = state["settings"].get("temperatureThreshold")
    fan_is_on = state["actuators"].get("fan")
    manual_override = state["actuators"].get("manualFanOverride", False)

    if temperature is None or threshold is None:
        return None

    if manual_override:
        return {
            "status": "skipped",
            "reason": "manual_override_active",
            "temperature": temperature,
            "threshold": threshold,
            "fan": fan_is_on
        }

    temperature = float(temperature)
    threshold = float(threshold)

    if temperature > threshold and not fan_is_on:
        actuator_data = update_fan_state(True)

        command = add_command(
            command_type="SET_FAN",
            value=True,
            payload={
                "source": "auto_fan",
                "temperature": temperature,
                "threshold": threshold
            }
        )

        timeline_event = add_timeline_event(
            event_type="actuator",
            message=f"Auto-fan triggered: {temperature}°C exceeded {threshold}°C",
            metadata={
                "temperature": temperature,
                "threshold": threshold,
                "commandId": command["id"]
            }
        )

        emit_actuator_update(actuator_data)
        emit_socket_event("fan_update", actuator_data)
        emit_timeline_update(timeline_event)

        return {
            "status": "fan_on",
            "actuators": actuator_data,
            "command": command,
            "timelineEvent": timeline_event
        }

    if temperature <= threshold and fan_is_on:
        actuator_data = update_fan_state(False)

        command = add_command(
            command_type="SET_FAN",
            value=False,
            payload={
                "source": "auto_fan",
                "temperature": temperature,
                "threshold": threshold
            }
        )

        timeline_event = add_timeline_event(
            event_type="actuator",
            message=f"Auto-fan turned off: {temperature}°C is below {threshold}°C",
            metadata={
                "temperature": temperature,
                "threshold": threshold,
                "commandId": command["id"]
            }
        )

        emit_actuator_update(actuator_data)
        emit_socket_event("fan_update", actuator_data)
        emit_timeline_update(timeline_event)

        return {
            "status": "fan_off",
            "actuators": actuator_data,
            "command": command,
            "timelineEvent": timeline_event
        }

    return {
        "status": "no_change",
        "temperature": temperature,
        "threshold": threshold,
        "fan": fan_is_on
    }