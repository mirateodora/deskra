<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api";

const router = useRouter();
const dashboardStore = useDashboardStore();

const userName = computed(() => {
  return dashboardStore.auth.currentUser?.name || "Guest";
});

const isGuest = computed(() => {
  return !dashboardStore.auth.currentUser;
});

const connectionLabel = computed(() => {
  return dashboardStore.socketConnected ? "Backend connected" : "Backend disconnected";
});

const deviceLabel = computed(() => {
  if (dashboardStore.device.connected) return "Device online";
  if (dashboardStore.device.mode === "simulator") return "Simulator mode";
  return "Device offline";
});

const temperatureDisplay = computed(() => {
  return dashboardStore.sensors.temperature !== null
    ? `${dashboardStore.sensors.temperature}°C`
    : "--°C";
});

const humidityDisplay = computed(() => {
  return dashboardStore.sensors.humidity !== null
    ? `${dashboardStore.sensors.humidity}%`
    : "--%";
});

const presenceDisplay = computed(() => {
  return dashboardStore.sensors.presence ? "Detected" : "Not detected";
});

const fanDisplay = computed(() => {
  return dashboardStore.actuators.fan ? "On" : "Off";
});

const pomodoroModeLabel = computed(() => {
  const mode = dashboardStore.pomodoro.mode;

  if (mode === "focus") return "Focus time";
  if (mode === "break") return "Break time";
  if (mode === "paused") return "Paused";

  return "Idle";
});

const pomodoroProgressDegrees = computed(() => {
  const mode = dashboardStore.pomodoro.mode;
  const remaining = dashboardStore.pomodoro.remainingSeconds || 0;

  let totalSeconds = dashboardStore.pomodoro.focusMinutes * 60;

  if (mode === "break") {
    totalSeconds = dashboardStore.pomodoro.breakMinutes * 60;
  }

  if (!totalSeconds || mode === "idle") {
    return 360;
  }

  const progress = remaining / totalSeconds;

  return Math.max(0, Math.min(360, progress * 360));
});

const timerCircleStyle = computed(() => {
  return {
    background: `
      radial-gradient(circle, #fffaf3 52%, transparent 54%),
      conic-gradient(
        #2f6f5e 0deg,
        #65b891 ${pomodoroProgressDegrees.value}deg,
        #eadcc9 ${pomodoroProgressDegrees.value}deg,
        #eadcc9 360deg
      )
    `,
  };
});

const latestTimeline = computed(() => {
  return [...dashboardStore.timeline]
    .sort((a, b) => {
      const timeA = new Date(a.timestamp).getTime() || 0;
      const timeB = new Date(b.timestamp).getTime() || 0;

      return timeB - timeA;
    })
    .slice(0, 5);
});

const latestCommand = computed(() => {
  return dashboardStore.commands.length
    ? dashboardStore.commands[0]
    : null;
});

const selectedFocusMinutes = ref(dashboardStore.pomodoro.focusMinutes || 25);
const selectedBreakMinutes = ref(dashboardStore.pomodoro.breakMinutes || 5);
const sessionTask = ref("");
const sessionNotes = ref("");
const sessionProductive = ref(true);
const sessionRating = ref(4);
const newTaskTitle = ref("");
const editingTaskId = ref(null);
const editingTaskTitle = ref("");

function goHome() {
  router.push("/");
}

function goToSettings() {
  router.push("/settings");
}

function goToAnalytics() {
  router.push("/analytics");
}

function goToLogs() {
  router.push("/access-logs");
}

function goToSimulator() {
  router.push("/simulator");
}

async function toggleFan() {
  const nextState = !dashboardStore.actuators.fan;

  try {
    const response = await api.setFan(nextState);

    dashboardStore.applyActuatorUpdate(response.actuators);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to toggle fan:", error);
  }
}

async function changeLedColor(event) {
  const color = event.target.value;

  try {
    const response = await api.setLedColor(color);

    dashboardStore.applyActuatorUpdate(response.actuators);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to change LED:", error);
  }
}

async function startPomodoro() {
  try {
    const response = await api.startPomodoro({
      focusMinutes: Number(selectedFocusMinutes.value),
      breakMinutes: Number(selectedBreakMinutes.value),
      selectedTask:
        dashboardStore.tasks.find((task) => task.selected)?.title ||
        dashboardStore.pomodoro.selectedTask,
    });

    dashboardStore.applyPomodoroUpdate(response.pomodoro);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to start pomodoro:", error);
  }
}

async function pausePomodoro() {
  try {
    const response = await api.pausePomodoro();

    dashboardStore.applyPomodoroUpdate(response.pomodoro);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to pause pomodoro:", error);
  }
}

async function resumePomodoro() {
  try {
    const response = await api.resumePomodoro();

    dashboardStore.applyPomodoroUpdate(response.pomodoro);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to resume pomodoro:", error);
  }
}

async function stopPomodoro() {
  try {
    const response = await api.stopPomodoro();

    dashboardStore.applyPomodoroUpdate(response.pomodoro);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }
  } catch (error) {
    console.error("Failed to stop pomodoro:", error);
  }
}

async function savePomodoroSession() {
  try {
    const response = await api.savePomodoroSession({
      task: sessionTask.value || dashboardStore.pomodoro.selectedTask || "",
      notes: sessionNotes.value,
      productive: sessionProductive.value,
      rating: Number(sessionRating.value),
    });

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    dashboardStore.setPomodoroEndModal(false);

    sessionTask.value = "";
    sessionNotes.value = "";
    sessionProductive.value = true;
    sessionRating.value = 4;
  } catch (error) {
    console.error("Failed to save pomodoro session:", error);
  }
}

function closePomodoroModal() {
  dashboardStore.setPomodoroEndModal(false);
}

function formatTimelineTime(timestamp) {
  if (!timestamp) return "No time";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString([], {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

async function fetchTasks() {
  try {
    const response = await api.getTasks();
    dashboardStore.setTasks(response.tasks);
  } catch (error) {
    console.error("Failed to fetch tasks:", error);
  }
}

async function createTask() {
  const title = newTaskTitle.value.trim();

  if (!title) return;

  try {
    const response = await api.createTask(title);

    dashboardStore.setTasks(response.tasks);

    newTaskTitle.value = "";
  } catch (error) {
    console.error("Failed to create task:", error);
  }
}

function startEditingTask(task) {
  editingTaskId.value = task.id;
  editingTaskTitle.value = task.title;
}

async function saveEditedTask(task) {
  const title = editingTaskTitle.value.trim();

  if (!title) return;

  try {
    const response = await api.updateTask(task.id, {
      title,
    });

    dashboardStore.setTasks(response.tasks);


    editingTaskId.value = null;
    editingTaskTitle.value = "";
  } catch (error) {
    console.error("Failed to edit task:", error);
  }
}

async function toggleTaskComplete(task) {
  try {
    const response = await api.updateTask(task.id, {
      completed: !task.completed,
    });

    dashboardStore.setTasks(response.tasks);

  } catch (error) {
    console.error("Failed to complete task:", error);
  }
}

async function selectTask(task) {
  try {
    const response = await api.updateTask(task.id, {
      selected: true,
    });

    dashboardStore.setTasks(response.tasks);

    dashboardStore.applyPomodoroUpdate({
      selectedTask: task.title,
    });

  } catch (error) {
    console.error("Failed to select task:", error);
  }
}

async function removeTask(task) {
  try {
    const response = await api.deleteTask(task.id);

    dashboardStore.setTasks(response.tasks);

  } catch (error) {
    console.error("Failed to delete task:", error);
  }
}

onMounted(() => {
  fetchTasks();
});
</script>

<template>
  <main class="dashboard-page">
    <section class="dashboard-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Deskra dashboard</p>
          <h1>Welcome, {{ userName }}</h1>
          <p class="subtitle">
            {{ isGuest ? "Guest mode active" : "Your cozy productivity space is ready" }}
          </p>
        </div>

        <div class="topbar-actions">
          <div class="connection-pill">
            <span
              class="dot"
              :class="{ online: dashboardStore.socketConnected }"
            ></span>
            {{ connectionLabel }}
          </div>

          <button @click="goHome">
            Lock
          </button>
        </div>
      </header>

      <section class="quick-grid">
        <article class="stat-card">
          <div class="stat-icon warm">🌡️</div>
          <div>
            <p>Temperature</p>
            <h2>{{ temperatureDisplay }}</h2>
          </div>
        </article>

        <article class="stat-card">
          <div class="stat-icon blue">💧</div>
          <div>
            <p>Humidity</p>
            <h2>{{ humidityDisplay }}</h2>
          </div>
        </article>

        <article class="stat-card">
          <div class="stat-icon green">🪑</div>
          <div>
            <p>Presence</p>
            <h2>{{ presenceDisplay }}</h2>
          </div>
        </article>

        <article class="stat-card">
          <div class="stat-icon amber">🌀</div>
          <div>
            <p>Fan</p>
            <h2>{{ fanDisplay }}</h2>
          </div>
        </article>
      </section>

      <section class="main-grid">
        <article class="panel pomodoro-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Pomodoro</p>
              <h2>{{ pomodoroModeLabel }}</h2>
            </div>

            <span class="mode-badge">
              {{ dashboardStore.pomodoro.running ? "Running" : "Stopped" }}
            </span>
          </div>

          <div class="timer-circle" :style="timerCircleStyle">
            <span>{{ dashboardStore.formattedRemainingTime }}</span>
          </div>

          <div class="pomodoro-selectors">
            <label>
              Focus minutes
              <input
                v-model="selectedFocusMinutes"
                type="number"
                min="1"
                max="120"
                :disabled="dashboardStore.pomodoro.running"
              />
            </label>

            <label>
              Break minutes
              <input
                v-model="selectedBreakMinutes"
                type="number"
                min="1"
                max="60"
                :disabled="dashboardStore.pomodoro.running"
              />
            </label>
          </div>

          <div class="pomodoro-actions">
            <button
              class="pomodoro-btn primary"
              @click="startPomodoro"
              :disabled="dashboardStore.pomodoro.running"
            >
              Start
            </button>

            <button
              class="pomodoro-btn"
              @click="pausePomodoro"
              :disabled="!dashboardStore.pomodoro.running"
            >
              Pause
            </button>

            <button
              class="pomodoro-btn"
              @click="resumePomodoro"
              :disabled="dashboardStore.pomodoro.mode !== 'paused'"
            >
              Resume
            </button>

            <button
              class="pomodoro-btn danger"
              @click="stopPomodoro"
              :disabled="dashboardStore.pomodoro.mode === 'idle'"
            >
              Stop
            </button>
          </div>

          <div class="pomodoro-meta">
            <div>
              <p>Focus</p>
              <strong>{{ dashboardStore.pomodoro.focusMinutes }} min</strong>
            </div>

            <div>
              <p>Break</p>
              <strong>{{ dashboardStore.pomodoro.breakMinutes }} min</strong>
            </div>

            <div>
              <p>Absences</p>
              <strong>{{ dashboardStore.pomodoro.deskAbsenceCount }}</strong>
            </div>
          </div>

          <p class="selected-task">
            Selected task:
            <strong>
              {{ dashboardStore.pomodoro.selectedTask || "No task selected yet" }}
            </strong>
          </p>
        </article>

        <article class="panel controls-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Controls</p>
              <h2>Desk actions</h2>
            </div>
          </div>

          <div class="control-list">
            <div class="control-row">
              <div>
                <strong>Fan override</strong>
                <p>Current state: {{ fanDisplay }}</p>
              </div>

              <button class="small-btn" @click="toggleFan">
                Toggle
              </button>
            </div>

            <div class="control-row">
              <div>
                <strong>LED color</strong>
                <p>{{ dashboardStore.actuators.ledColor }}</p>
              </div>

              <input
                class="dashboard-color-input"
                type="color"
                :value="dashboardStore.actuators.ledColor"
                @change="changeLedColor"
              />
            </div>

            <div class="control-row">
              <div>
                <strong>Auto-fan threshold</strong>
                <p>{{ dashboardStore.settings.temperatureThreshold }}°C</p>
              </div>

              <button class="small-btn muted" @click="goToSettings">
                Edit
              </button>
            </div>
          </div>

          <div class="command-status">
            <strong>Latest command</strong>
            <p v-if="latestCommand">
              {{ latestCommand.type }} → {{ latestCommand.status }}
            </p>
            <p v-else>
              No commands sent yet
            </p>
          </div>
        </article>

        <article class="panel tasks-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Tasks</p>
              <h2>Today’s focus</h2>
            </div>
          </div>

          <div class="task-create-row">
            <input
              v-model="newTaskTitle"
              type="text"
              placeholder="Add a focus task..."
              @keyup.enter="createTask"
            />

            <button class="small-btn" @click="createTask">
              Add
            </button>
          </div>

          <div v-if="dashboardStore.tasks.length" class="task-list">
            <div
              v-for="task in dashboardStore.tasks.slice(0, 5)"
              :key="task.id"
              class="task-item"
              :class="{ completed: task.completed, selected: task.selected }"
            >
              <button
                class="task-check"
                @click="toggleTaskComplete(task)"
              >
                {{ task.completed ? "✓" : "" }}
              </button>

              <div class="task-body">
                <input
                  v-if="editingTaskId === task.id"
                  v-model="editingTaskTitle"
                  class="task-edit-input"
                  @keyup.enter="saveEditedTask(task)"
                />

                <span v-else class="task-title">
                  {{ task.title }}
                </span>

                <small v-if="task.selected">Selected for pomodoro</small>

                <div class="task-actions">
                  <button
                    v-if="editingTaskId === task.id"
                    @click="saveEditedTask(task)"
                  >
                    Save
                  </button>

                  <button
                    v-else
                    @click="startEditingTask(task)"
                  >
                    Edit
                  </button>

                  <button @click="selectTask(task)">
                    Select
                  </button>

                  <button class="danger-text" @click="removeTask(task)">
                    Delete
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <p>No tasks yet.</p>
            <small>Add a task, then select it before starting pomodoro.</small>
          </div>
        </article>

        <article class="panel timeline-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Timeline</p>
              <h2>Latest events</h2>
            </div>
          </div>

          <div v-if="latestTimeline.length" class="timeline-list">
            <div
              v-for="event in latestTimeline"
              :key="event.id"
              class="timeline-item"
            >
              <div class="timeline-dot"></div>

              <div>
                <strong>{{ event.message }}</strong>
                <p>{{ formatTimelineTime(event.timestamp) }}</p>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <p>No timeline events yet.</p>
            <small>Login, sensor, fan, and pomodoro events will appear here.</small>
          </div>
        </article>
      </section>

      <section class="bottom-grid" v-if="!isGuest">
        <button class="nav-card" @click="goToSettings">
          <span>⚙️</span>
          <strong>Settings</strong>
          <small>Customize timer, LED, and comfort rules</small>
        </button>

        <button class="nav-card" @click="goToAnalytics">
          <span>📊</span>
          <strong>Analytics</strong>
          <small>View focus time and desk behavior</small>
        </button>

        <button class="nav-card" @click="goToLogs">
          <span>🧾</span>
          <strong>Access logs</strong>
          <small>Check Face ID and manual login attempts</small>
        </button>

        <button class="nav-card" @click="goToSimulator">
          <span>🧪</span>
          <strong>Simulator</strong>
          <small>Test dashboard without ESP32 hardware</small>
        </button>
      </section>

      <footer class="dashboard-footer">
        <span>{{ deviceLabel }}</span>
        <span>Last update: {{ dashboardStore.device.lastUpdate || "No updates yet" }}</span>
      </footer>
    </section>

    <section
      v-if="dashboardStore.showPomodoroEndModal"
      class="modal-backdrop"
    >
      <div class="session-modal">
        <button class="modal-close" @click="closePomodoroModal">
          ×
        </button>

        <p class="eyebrow">Session complete</p>

        <h2>What did you work on?</h2>

        <p class="modal-description">
          Save a quick summary so your analytics can reflect what happened during this focus block.
        </p>

        <label>
          Task
          <input
            v-model="sessionTask"
            type="text"
            placeholder="e.g. Write API endpoints"
          />
        </label>

        <label>
          Notes
          <textarea
            v-model="sessionNotes"
            rows="4"
            placeholder="What did you finish? Any blockers?"
          ></textarea>
        </label>

        <label>
          Productivity rating
          <select v-model="sessionRating">
            <option :value="1">1 - Low focus</option>
            <option :value="2">2 - Some progress</option>
            <option :value="3">3 - Good</option>
            <option :value="4">4 - Very good</option>
            <option :value="5">5 - Deep work</option>
          </select>
        </label>

        <label class="checkbox-row">
          <input
            v-model="sessionProductive"
            type="checkbox"
          />
          This session was productive
        </label>

        <button class="save-session-btn" @click="savePomodoroSession">
          Save Session
        </button>
      </div>
    </section>
  </main>
</template>

<style scoped>
.dashboard-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.28), transparent 30%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.2), transparent 32%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.dashboard-shell {
  width: min(1240px, 100%);
  margin: 0 auto;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 22px;
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

.connection-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 14px;
  border-radius: 999px;
  background: #fffaf3;
  color: #4c423a;
  font-size: 14px;
  font-weight: 800;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #d66b5d;
  box-shadow: 0 0 0 4px rgba(214, 107, 93, 0.12);
}

.dot.online {
  background: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

button {
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-weight: 800;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

button:hover {
  transform: translateY(-2px);
}

.topbar-actions button {
  padding: 12px 16px;
  border-radius: 999px;
  background: #2f6f5e;
  color: #fffaf3;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.2);
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: 24px;
  background: #fffaf3;
  box-shadow: 0 14px 36px rgba(85, 67, 50, 0.11);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.stat-icon {
  width: 52px;
  height: 52px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 18px;
  font-size: 23px;
}

.stat-icon.warm {
  background: #ffe9d6;
}

.stat-icon.blue {
  background: #e6f0ff;
}

.stat-icon.green {
  background: #e4f0ea;
}

.stat-icon.amber {
  background: #fff0cf;
}

.stat-card p {
  margin: 0 0 4px;
  color: #8b735f;
  font-size: 14px;
  font-weight: 800;
}

.stat-card h2 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.main-grid {
  display: grid;
  grid-template-columns: 1.1fr 0.9fr;
  gap: 16px;
}

.panel {
  padding: 24px;
  border-radius: 28px;
  background: rgba(255, 250, 243, 0.92);
  box-shadow: 0 14px 42px rgba(85, 67, 50, 0.12);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.panel-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 20px;
}

.panel-header h2 {
  margin: 0;
  font-size: 27px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.mode-badge {
  padding: 9px 12px;
  border-radius: 999px;
  background: #e4f0ea;
  color: #2f6f5e;
  font-weight: 900;
  font-size: 13px;
}

.pomodoro-panel {
  min-height: 430px;
}

.timer-circle {
  width: 230px;
  height: 230px;
  display: grid;
  place-items: center;
  margin: 10px auto 26px;
  border-radius: 50%;
  box-shadow: inset 0 0 0 10px rgba(255, 250, 243, 0.8);
}

.timer-circle span {
  font-size: 44px;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.pomodoro-meta {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 11px;
  margin-bottom: 18px;
}

.pomodoro-meta div {
  padding: 14px;
  border-radius: 18px;
  background: #f7efe5;
}

.pomodoro-meta p {
  margin: 0 0 5px;
  color: #8b735f;
  font-size: 13px;
  font-weight: 800;
}

.pomodoro-meta strong {
  font-size: 18px;
  color: #1f2a37;
}

.pomodoro-selectors {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.pomodoro-selectors label {
  display: grid;
  gap: 7px;
  color: #4c423a;
  font-size: 14px;
  font-weight: 900;
}

.pomodoro-selectors input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1px solid #eadcc9;
  border-radius: 14px;
  background: #fffdf9;
  color: #24313f;
  font-size: 15px;
  outline: none;
}

.pomodoro-selectors input:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.pomodoro-selectors input:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.pomodoro-actions {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  margin-bottom: 18px;
}

.pomodoro-btn {
  padding: 12px 14px;
  border-radius: 14px;
  background: #e4f0ea;
  color: #2f6f5e;
  font-size: 14px;
}

.pomodoro-btn.primary {
  background: #2f6f5e;
  color: #fffaf3;
  box-shadow: 0 12px 24px rgba(47, 111, 94, 0.18);
}

.pomodoro-btn.danger {
  background: #ffe7e1;
  color: #a54b3f;
}

.pomodoro-btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
  transform: none;
}

.selected-task {
  margin: 0;
  padding: 14px 16px;
  border-radius: 18px;
  background: #e4f0ea;
  color: #4c423a;
  line-height: 1.5;
}

.controls-panel,
.tasks-panel,
.timeline-panel {
  min-height: 260px;
}

.control-list {
  display: grid;
  gap: 13px;
}

.control-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 15px;
  border-radius: 18px;
  background: #f7efe5;
}

.control-row strong {
  color: #1f2a37;
}

.control-row p {
  margin: 5px 0 0;
  color: #8b735f;
  font-size: 14px;
}

.small-btn {
  padding: 11px 14px;
  border-radius: 14px;
  background: #2f6f5e;
  color: #fffaf3;
}

.small-btn.muted {
  background: #e4f0ea;
  color: #2f6f5e;
}

.dashboard-color-input {
  width: 48px;
  height: 48px;
  padding: 0;
  border: none;
  border-radius: 15px;
  background: transparent;
  cursor: pointer;
}

.command-status {
  margin-top: 14px;
  padding: 15px;
  border-radius: 18px;
  background: #e4f0ea;
}

.command-status strong {
  color: #1f2a37;
}

.command-status p {
  margin: 5px 0 0;
  color: #2f6f5e;
  font-weight: 800;
}

.task-create-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10px;
  margin-bottom: 14px;
}

.task-create-row input,
.task-edit-input {
  width: 100%;
  box-sizing: border-box;
  padding: 12px 14px;
  border: 1px solid #eadcc9;
  border-radius: 14px;
  background: #fffdf9;
  color: #24313f;
  font-size: 15px;
  outline: none;
}

.task-create-row input:focus,
.task-edit-input:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.task-list {
  display: grid;
  gap: 10px;
}

.task-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: flex-start;
  padding: 14px;
  border-radius: 16px;
  background: #f7efe5;
  color: #4c423a;
}

.task-item.completed {
  opacity: 0.65;
}

.task-item.completed .task-title {
  text-decoration: line-through;
}

.task-item.selected {
  background: #e4f0ea;
}

.task-check {
  width: 30px;
  height: 30px;
  border-radius: 10px;
  background: #fffaf3;
  color: #2f6f5e;
  font-weight: 900;
  flex: 0 0 auto;
}

.task-body {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.task-title {
  display: block;
  color: #1f2a37;
  line-height: 1.35;
  word-break: break-word;
  font-weight: 900;
}

.task-body small {
  color: #2f6f5e;
  font-size: 12px;
  font-weight: 800;
}

.task-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.task-actions button {
  padding: 8px 11px;
  border-radius: 10px;
  background: #fffaf3;
  color: #2f6f5e;
  font-size: 12px;
}

.task-actions .danger-text {
  color: #a54b3f;
}

.timeline-list {
  display: grid;
  gap: 12px;
}

.timeline-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 13px;
  border-radius: 16px;
  background: #f7efe5;
}

.timeline-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 5px;
  background: #f8c471;
  box-shadow: 0 0 0 4px rgba(248, 196, 113, 0.18);
}

.timeline-item strong {
  color: #1f2a37;
}

.timeline-item p {
  margin: 5px 0 0;
  color: #8b735f;
  font-size: 13px;
}

.empty-state {
  padding: 22px;
  border-radius: 18px;
  background: #f7efe5;
  color: #6c5f53;
}

.empty-state p {
  margin: 0 0 6px;
  font-weight: 900;
  color: #1f2a37;
}

.empty-state small {
  line-height: 1.5;
}

.bottom-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.nav-card {
  text-align: left;
  padding: 20px;
  border-radius: 24px;
  background: #fffaf3;
  color: #24313f;
  box-shadow: 0 14px 36px rgba(85, 67, 50, 0.11);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.nav-card span {
  display: block;
  font-size: 26px;
  margin-bottom: 12px;
}

.nav-card strong {
  display: block;
  margin-bottom: 7px;
  font-size: 17px;
}

.nav-card small {
  color: #8b735f;
  line-height: 1.5;
}

.dashboard-footer {
  display: flex;
  justify-content: space-between;
  gap: 14px;
  margin-top: 16px;
  padding: 16px 4px;
  color: #7b6a5a;
  font-weight: 800;
  font-size: 14px;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(31, 42, 55, 0.42);
  backdrop-filter: blur(8px);
}

.session-modal {
  position: relative;
  width: min(520px, 100%);
  padding: 30px;
  border-radius: 30px;
  background: #fffaf3;
  box-shadow: 0 30px 90px rgba(31, 42, 55, 0.28);
  border: 1px solid rgba(255, 255, 255, 0.7);
}

.modal-close {
  position: absolute;
  top: 18px;
  right: 18px;
  width: 38px;
  height: 38px;
  border-radius: 14px;
  background: #f7efe5;
  color: #6c5f53;
  font-size: 24px;
  line-height: 1;
}

.session-modal h2 {
  margin: 0;
  font-size: 32px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.modal-description {
  margin: 12px 0 22px;
  color: #6c5f53;
  font-size: 16px;
  line-height: 1.6;
}

.session-modal label {
  display: grid;
  gap: 8px;
  margin-bottom: 16px;
  color: #4c423a;
  font-size: 15px;
  font-weight: 900;
}

.session-modal input,
.session-modal textarea,
.session-modal select {
  width: 100%;
  box-sizing: border-box;
  padding: 14px 16px;
  border: 1px solid #eadcc9;
  border-radius: 16px;
  background: #fffdf9;
  color: #24313f;
  font-size: 16px;
  outline: none;
  font-family: inherit;
}

.session-modal input:focus,
.session-modal textarea:focus,
.session-modal select:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.checkbox-row {
  display: flex !important;
  grid-template-columns: none !important;
  align-items: center;
  gap: 10px !important;
}

.checkbox-row input {
  width: auto;
}

.save-session-btn {
  width: 100%;
  padding: 15px 18px;
  border-radius: 16px;
  background: #2f6f5e;
  color: #fffaf3;
  font-size: 16px;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.22);
}

@media (max-width: 1050px) {
  .quick-grid,
  .bottom-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .main-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 680px) {
  .dashboard-page {
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

  .connection-pill,
  .topbar-actions button {
    justify-content: center;
    width: 100%;
  }

  .quick-grid,
  .bottom-grid,
  .pomodoro-meta,
  .pomodoro-selectors,
  .pomodoro-actions,
  .task-create-row {
    grid-template-columns: 1fr;
  }

  .timer-circle {
    width: 200px;
    height: 200px;
  }

  .timer-circle span {
    font-size: 38px;
  }

  .dashboard-footer {
    flex-direction: column;
  }

  .task-item {
    grid-template-columns: 1fr;
  }
}
</style>
