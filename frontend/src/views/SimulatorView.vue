<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api";

const router = useRouter();
const dashboardStore = useDashboardStore();

const eventMessage = ref("");
const customTemperature = ref(27);
const customHumidity = ref(48);

const currentTemperature = computed(() => {
  return dashboardStore.sensors.temperature ?? "--";
});

const currentHumidity = computed(() => {
  return dashboardStore.sensors.humidity ?? "--";
});

const presenceLabel = computed(() => {
  return dashboardStore.sensors.presence ? "Detected" : "Not detected";
});

const fanLabel = computed(() => {
  return dashboardStore.actuators.fan ? "On" : "Off";
});

const deviceLabel = computed(() => {
  if (dashboardStore.device.connected) return "Device online";
  if (dashboardStore.device.mode === "simulator") return "Simulator mode";
  return "Device offline";
});

function showMessage(message) {
  eventMessage.value = message;

  setTimeout(() => {
    if (eventMessage.value === message) {
      eventMessage.value = "";
    }
  }, 2500);
}

function addLocalTimeline(message, type = "simulator") {
  dashboardStore.addTimelineEvent({
    id: Date.now(),
    type,
    message,
    metadata: {
      source: "SimulatorView",
    },
    timestamp: new Date().toISOString(),
  });
}

function simulatePresenceDetected() {
  dashboardStore.applySensorUpdate({
    presence: true,
    lastUpdate: new Date().toISOString(),
  });

  dashboardStore.applyFullState({
    ...dashboardStore.$state,
    device: {
      ...dashboardStore.device,
      connected: true,
      mode: "simulator",
      lastUpdate: new Date().toISOString(),
    },
  });

  addLocalTimeline("Presence detected by simulated ultrasonic sensor");
  showMessage("Presence detected.");
}

function simulatePresenceLost() {
  dashboardStore.applySensorUpdate({
    presence: false,
    lastUpdate: new Date().toISOString(),
  });

  addLocalTimeline("Presence lost during simulated focus session");
  showMessage("Presence lost.");
}

function simulateSensorUpdate() {
  const now = new Date().toISOString();

  dashboardStore.applySensorUpdate({
    temperature: Number(customTemperature.value),
    humidity: Number(customHumidity.value),
    lastUpdate: now,
  });

  dashboardStore.applyFullState({
    ...dashboardStore.$state,
    device: {
      ...dashboardStore.device,
      connected: true,
      mode: "simulator",
      lastUpdate: now,
    },
  });

  addLocalTimeline(
    `Simulated sensor update: ${customTemperature.value}°C, ${customHumidity.value}% humidity`
  );

  showMessage("Sensor values updated.");
}

function simulateTemperatureIncrease() {
  const current = dashboardStore.sensors.temperature ?? 24;
  const nextTemperature = Number((Number(current) + 1.5).toFixed(1));
  const now = new Date().toISOString();

  dashboardStore.applySensorUpdate({
    temperature: nextTemperature,
    humidity: dashboardStore.sensors.humidity ?? 48,
    lastUpdate: now,
  });

  dashboardStore.applyFullState({
    ...dashboardStore.$state,
    device: {
      ...dashboardStore.device,
      connected: true,
      mode: "simulator",
      lastUpdate: now,
    },
  });

  addLocalTimeline(`Temperature increased to ${nextTemperature}°C`);
  showMessage("Temperature increased.");
}

function simulateAutoFanTrigger() {
  dashboardStore.applyActuatorUpdate({
    fan: true,
  });

  addLocalTimeline("Temperature exceeded threshold, auto-fan triggered");
  showMessage("Auto-fan triggered.");
}

function simulateFanOff() {
  dashboardStore.applyActuatorUpdate({
    fan: false,
  });

  addLocalTimeline("Fan turned off by simulator");
  showMessage("Fan turned off.");
}

function simulateFaceLoginSuccess() {
  const fakeUser = {
    id: 1,
    name: "Simulated User",
    focusLedColor: "#d66b5d",
    breakLedColor: "#65b891",
  };

  dashboardStore.applyAuthUpdate({
    locked: false,
    currentUser: fakeUser,
    loginMethod: "face_id_simulated",
  });

  dashboardStore.addAccessLog({
    id: Date.now(),
    user: fakeUser,
    method: "face_id",
    success: true,
    message: "Simulated Face ID login successful",
    metadata: {
      source: "SimulatorView",
    },
    timestamp: new Date().toISOString(),
  });

  addLocalTimeline("Zero-touch login successful by simulated Face ID", "auth");
  showMessage("Face login success.");
}

function simulateFaceLoginFailure() {
  dashboardStore.addAccessLog({
    id: Date.now(),
    user: null,
    method: "face_id",
    success: false,
    message: "Simulated Face ID login failed",
    metadata: {
      source: "SimulatorView",
    },
    timestamp: new Date().toISOString(),
  });

  addLocalTimeline("Face ID failed, manual login required", "auth");
  showMessage("Face login failed.");
}

function simulatePomodoroStarted() {
  dashboardStore.applyPomodoroUpdate({
    running: true,
    mode: "focus",
    remainingSeconds: dashboardStore.pomodoro.focusMinutes * 60,
    startedAt: new Date().toISOString(),
    endedAt: null,
  });

  dashboardStore.applyActuatorUpdate({
    ledColor:
      dashboardStore.settings.focusLedColor ||
      dashboardStore.auth.currentUser?.focusLedColor ||
      "#d66b5d",
  });

  addLocalTimeline("Focus session started by simulator", "pomodoro");
  showMessage("Pomodoro focus started.");
}

function simulateBreakStarted() {
  dashboardStore.applyPomodoroUpdate({
    running: true,
    mode: "break",
    remainingSeconds: dashboardStore.pomodoro.breakMinutes * 60,
  });

  dashboardStore.applyActuatorUpdate({
    ledColor:
      dashboardStore.settings.breakLedColor ||
      dashboardStore.auth.currentUser?.breakLedColor ||
      "#65b891",
  });

  addLocalTimeline("Break session started by simulator", "pomodoro");
  showMessage("Break started.");
}

function simulatePomodoroFinished() {
  dashboardStore.applyPomodoroUpdate({
    running: false,
    mode: "idle",
    remainingSeconds: dashboardStore.pomodoro.focusMinutes * 60,
    endedAt: new Date().toISOString(),
  });

  addLocalTimeline("Pomodoro session finished by simulator", "pomodoro");
  showMessage("Pomodoro finished.");
}

function simulateDeviceDisconnected() {
  dashboardStore.applyFullState({
    ...dashboardStore.$state,
    device: {
      ...dashboardStore.device,
      connected: false,
      lastUpdate: dashboardStore.device.lastUpdate,
    },
  });

  addLocalTimeline("Simulated ESP32 disconnected", "device");
  showMessage("Device disconnected.");
}

async function triggerBackendSocketTest() {
  try {
    await api.testSocketEmit();
    showMessage("Backend socket test triggered. Check console.");
  } catch (error) {
    showMessage("Backend socket test failed.");
  }
}

function goToDashboard() {
  router.push("/dashboard");
}

function goBack() {
  router.push("/");
}
</script>

<template>
  <main class="simulator-page">
    <section class="simulator-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Development tools</p>
          <h1>ESP32 Simulator</h1>
          <p class="subtitle">
            Test dashboard behavior before connecting the real hardware.
          </p>
        </div>

        <div class="topbar-actions">
          <button class="soft-btn" @click="goToDashboard">
            Dashboard
          </button>

          <button class="dark-btn" @click="goBack">
            Lock screen
          </button>
        </div>
      </header>

      <section v-if="eventMessage" class="toast">
        {{ eventMessage }}
      </section>

      <section class="status-grid">
        <article class="status-card">
          <span>🌡️</span>
          <p>Temperature</p>
          <h2>{{ currentTemperature }}°C</h2>
        </article>

        <article class="status-card">
          <span>💧</span>
          <p>Humidity</p>
          <h2>{{ currentHumidity }}%</h2>
        </article>

        <article class="status-card">
          <span>🪑</span>
          <p>Presence</p>
          <h2>{{ presenceLabel }}</h2>
        </article>

        <article class="status-card">
          <span>🌀</span>
          <p>Fan</p>
          <h2>{{ fanLabel }}</h2>
        </article>

        <article class="status-card">
          <span>📡</span>
          <p>Device</p>
          <h2>{{ deviceLabel }}</h2>
        </article>

        <article class="status-card">
          <span>🔌</span>
          <p>Socket</p>
          <h2>{{ dashboardStore.socketConnected ? "Connected" : "Disconnected" }}</h2>
        </article>
      </section>

      <section class="simulator-grid">
        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Sensors</p>
              <h2>Environment</h2>
            </div>
          </div>

          <div class="input-grid">
            <label>
              Temperature
              <input
                v-model="customTemperature"
                type="number"
                step="0.5"
              />
            </label>

            <label>
              Humidity
              <input
                v-model="customHumidity"
                type="number"
                step="1"
              />
            </label>
          </div>

          <div class="button-grid">
            <button @click="simulateSensorUpdate">
              Update sensors
            </button>

            <button @click="simulateTemperatureIncrease">
              Increase temperature
            </button>

            <button @click="simulatePresenceDetected">
              Presence detected
            </button>

            <button @click="simulatePresenceLost">
              Presence lost
            </button>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Authentication</p>
              <h2>Face ID</h2>
            </div>
          </div>

          <p class="panel-description">
            Simulate the ESP32-CAM sending a face-recognition result to the backend.
          </p>

          <div class="button-grid">
            <button @click="simulateFaceLoginSuccess">
              Face login success
            </button>

            <button class="danger" @click="simulateFaceLoginFailure">
              Face login failed
            </button>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Actuators</p>
              <h2>Fan and LED</h2>
            </div>
          </div>

          <div class="led-preview-row">
            <div
              class="led-preview"
              :style="{ background: dashboardStore.actuators.ledColor }"
            ></div>

            <div>
              <strong>Current LED</strong>
              <p>{{ dashboardStore.actuators.ledColor }}</p>
            </div>
          </div>

          <div class="button-grid">
            <button @click="simulateAutoFanTrigger">
              Trigger auto-fan
            </button>

            <button @click="simulateFanOff">
              Turn fan off
            </button>
          </div>
        </article>

        <article class="panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Pomodoro</p>
              <h2>Timer states</h2>
            </div>
          </div>

          <p class="timer-preview">
            {{ dashboardStore.formattedRemainingTime }}
          </p>

          <div class="button-grid">
            <button @click="simulatePomodoroStarted">
              Start focus
            </button>

            <button @click="simulateBreakStarted">
              Start break
            </button>

            <button @click="simulatePomodoroFinished">
              Finish session
            </button>
          </div>
        </article>

        <article class="panel wide-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Connection</p>
              <h2>Backend and ESP32 state</h2>
            </div>
          </div>

          <div class="button-grid wide-buttons">
            <button @click="triggerBackendSocketTest">
              Trigger backend socket test
            </button>

            <button class="danger" @click="simulateDeviceDisconnected">
              Simulate ESP32 disconnect
            </button>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<style scoped>
.simulator-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.28), transparent 30%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.2), transparent 32%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.simulator-shell {
  width: min(1240px, 100%);
  margin: 0 auto;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 18px;
  padding: 22px;
  border-radius: 30px;
  background: rgba(255, 250, 242, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.62);
  box-shadow: 0 18px 50px rgba(85, 67, 50, 0.12);
  backdrop-filter: blur(16px);
}

.eyebrow {
  margin: 0 0 7px;
  color: #5f9e86;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.topbar h1 {
  margin: 0;
  font-size: 38px;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.subtitle {
  margin: 7px 0 0;
  color: #6c5f53;
  font-size: 16px;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

button {
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-weight: 800;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

button:hover {
  transform: translateY(-2px);
}

.soft-btn,
.dark-btn {
  padding: 12px 16px;
  border-radius: 999px;
}

.soft-btn {
  background: #e4f0ea;
  color: #2f6f5e;
}

.dark-btn {
  background: #2f6f5e;
  color: #fffaf3;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.2);
}

.toast {
  margin-bottom: 18px;
  padding: 15px 18px;
  border-radius: 18px;
  background: #2f6f5e;
  color: #fffaf3;
  font-weight: 800;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.22);
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 14px;
  margin-bottom: 16px;
}

.status-card {
  padding: 18px;
  border-radius: 22px;
  background: #fffaf3;
  box-shadow: 0 14px 36px rgba(85, 67, 50, 0.11);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.status-card span {
  display: block;
  font-size: 24px;
  margin-bottom: 12px;
}

.status-card p {
  margin: 0 0 5px;
  color: #8b735f;
  font-size: 13px;
  font-weight: 900;
}

.status-card h2 {
  margin: 0;
  color: #1f2a37;
  font-size: 20px;
  letter-spacing: -0.04em;
}

.simulator-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.panel {
  padding: 24px;
  border-radius: 28px;
  background: rgba(255, 250, 243, 0.92);
  box-shadow: 0 14px 42px rgba(85, 67, 50, 0.12);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.wide-panel {
  grid-column: 1 / -1;
}

.panel-header {
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0;
  font-size: 27px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.panel-description {
  margin: 0 0 18px;
  color: #6c5f53;
  font-size: 16px;
  line-height: 1.6;
}

.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-bottom: 16px;
}

label {
  display: grid;
  gap: 8px;
  color: #4c423a;
  font-weight: 800;
  font-size: 15px;
}

input {
  width: 100%;
  box-sizing: border-box;
  padding: 15px 16px;
  border: 1px solid #eadcc9;
  border-radius: 16px;
  background: #fffdf9;
  color: #24313f;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.button-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.button-grid button {
  padding: 15px 16px;
  border-radius: 16px;
  background: #e4f0ea;
  color: #2f6f5e;
  font-size: 15px;
}

.button-grid button:hover {
  box-shadow: 0 12px 26px rgba(47, 111, 94, 0.12);
}

.button-grid button.danger {
  background: #ffe7e1;
  color: #a54b3f;
}

.wide-buttons {
  grid-template-columns: repeat(2, 1fr);
}

.led-preview-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 16px;
  border-radius: 18px;
  background: #f7efe5;
  margin-bottom: 16px;
}

.led-preview {
  width: 54px;
  height: 54px;
  border-radius: 18px;
  box-shadow: 0 0 0 6px rgba(255, 250, 243, 0.88);
}

.led-preview-row strong {
  color: #1f2a37;
}

.led-preview-row p {
  margin: 4px 0 0;
  color: #8b735f;
  font-weight: 800;
}

.timer-preview {
  margin: 0 0 18px;
  padding: 20px;
  border-radius: 22px;
  background: #f7efe5;
  color: #1f2a37;
  font-size: 42px;
  font-weight: 900;
  letter-spacing: -0.05em;
  text-align: center;
}

@media (max-width: 1100px) {
  .status-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 820px) {
  .simulator-page {
    padding: 18px;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .soft-btn,
  .dark-btn {
    width: 100%;
  }

  .simulator-grid {
    grid-template-columns: 1fr;
  }

  .wide-panel {
    grid-column: auto;
  }
}

@media (max-width: 620px) {
  .status-grid,
  .input-grid,
  .button-grid,
  .wide-buttons {
    grid-template-columns: 1fr;
  }

  .timer-preview {
    font-size: 34px;
  }
}
</style>
