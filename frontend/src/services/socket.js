import { io } from "socket.io-client";
import { useDashboardStore } from "@/stores/dashboardStore";

const SOCKET_URL = "http://localhost:5000";

const socket = io(SOCKET_URL, {
  transports: ["websocket", "polling"],
  autoConnect: true,
});



function getStore() {
  return useDashboardStore();
}

socket.on("connect", () => {
  console.log("✅ Connected to Flask-SocketIO:", socket.id);

  const store = getStore();
  store.setSocketConnected(true);
});

socket.on("disconnect", () => {
  console.log("❌ Disconnected from Flask-SocketIO");

  const store = getStore();
  store.setSocketConnected(false);
});

socket.on("connect_error", (error) => {
  console.error("Socket connection error:", error.message);

  const store = getStore();
  store.setSocketConnected(false);
});

socket.on("test_event", (data) => {
  console.log("Received test_event:", data);
});

socket.on("state_update", (data) => {
  console.log("Received state_update:", data);

  const store = getStore();
  store.applyFullState(data);
});

socket.on("sensor_update", (data) => {
  console.log("Received sensor_update:", data);

  const store = getStore();
  store.applySensorUpdate(data);
});

socket.on("actuator_update", (data) => {
  console.log("Received actuator_update:", data);

  const store = getStore();
  store.applyActuatorUpdate(data);
});

socket.on("auth_update", (data) => {
  console.log("Received auth_update:", data);

  const store = getStore();
  store.applyAuthUpdate(data);
});

socket.on("pomodoro_update", (data) => {
  console.log("Received pomodoro_update:", data);

  const store = getStore();
  store.applyPomodoroUpdate(data);
});

socket.on("settings_update", (data) => {
  console.log("Received settings_update:", data);

  const store = getStore();
  store.applySettingsUpdate(data);
});

socket.on("timeline_update", (data) => {
  console.log("Received timeline_update:", data);

  const store = getStore();
  store.addTimelineEvent(data);
});

socket.on("access_log_update", (data) => {
  console.log("Received access_log_update:", data);

  const store = getStore();
  store.addAccessLog(data);
});

socket.on("login_success", (data) => {
  console.log("Received login_success:", data);

  const store = getStore();

  if (data.auth) {
    store.applyAuthUpdate(data.auth);
  } else {
    store.applyAuthUpdate({
      locked: false,
      currentUser: data.user,
      loginMethod: "face_id",
    });
  }

  if (data.timelineEvent) {
    store.addTimelineEvent(data.timelineEvent);
  }

  if (data.accessLog) {
    store.addAccessLog(data.accessLog);
  }

  window.location.href = "/dashboard";
});

socket.on("login_failed", (data) => {
  console.log("Received login_failed:", data);

  const store = getStore();

  if (data.timelineEvent) {
    store.addTimelineEvent(data.timelineEvent);
  }

  if (data.accessLog) {
    store.addAccessLog(data.accessLog);
  }

  alert(data.reason || "Face login failed. Please try again or use manual login.");
});

socket.on("fan_update", (data) => {
  console.log("Received fan_update:", data);

  const store = getStore();
  store.applyActuatorUpdate(data);
});

socket.on("led_update", (data) => {
  console.log("Received led_update:", data);

  const store = getStore();
  store.applyActuatorUpdate(data);
});

socket.on("focus_session_ended", (data) => {
  console.log("Received focus_session_ended:", data);

  const store = getStore();

  if (data.pomodoro) {
    store.applyPomodoroUpdate(data.pomodoro);
  }

  if (data.timelineEvent) {
    store.addTimelineEvent(data.timelineEvent);
  }

  store.setPomodoroEndModal(true);
});

socket.on("tasks_update", (tasks) => {
  console.log("Received tasks_update:", tasks);

  const store = getStore();
  store.setTasks(tasks);
});

export default socket;
