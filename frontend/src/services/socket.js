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

export default socket;
