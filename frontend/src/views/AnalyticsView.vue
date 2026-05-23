<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api"

const router = useRouter();
const dashboardStore = useDashboardStore();
const analyticsSummary = ref(null);
const analyticsLoading = ref(false);
const analyticsError = ref("");

const sessions = computed(() => {
  return dashboardStore.timeline.filter((event) => {
    return (
      event.type === "pomodoro" ||
      event.message?.toLowerCase().includes("focus session") ||
      event.message?.toLowerCase().includes("pomodoro")
    );
  });
});

const totalFocusMinutes = computed(() => {
  return analyticsSummary.value?.today?.focusMinutes ?? 0;
});

const totalSessions = computed(() => {
  return analyticsSummary.value?.today?.sessions ?? 0;
});

const deskAbsences = computed(() => {
  return analyticsSummary.value?.today?.deskAbsences ?? 0;
});

const fanActivations = computed(() => {
  return analyticsSummary.value?.today?.fanActivations ?? 0;
});

const averageTemperature = computed(() => {
  return analyticsSummary.value?.today?.averageTemperature ?? "--";
});

const averageHumidity = computed(() => {
  return analyticsSummary.value?.today?.averageHumidity ?? "--";
});

const completedTasks = computed(() => {
  return analyticsSummary.value?.today?.completedTasks ?? 0;
});




const weeklyFocusData = computed(() => {
  const base = [45, 25, 60, 35, 80, 30, totalFocusMinutes.value || 50];
  const max = Math.max(...base, 1);

  return [
    { day: "Mon", value: base[0], height: (base[0] / max) * 100 },
    { day: "Tue", value: base[1], height: (base[1] / max) * 100 },
    { day: "Wed", value: base[2], height: (base[2] / max) * 100 },
    { day: "Thu", value: base[3], height: (base[3] / max) * 100 },
    { day: "Fri", value: base[4], height: (base[4] / max) * 100 },
    { day: "Sat", value: base[5], height: (base[5] / max) * 100 },
    { day: "Sun", value: base[6], height: (base[6] / max) * 100 },
  ];
});

const productivityScore = computed(() => {
  let score = 50;

  if (dashboardStore.pomodoro.running) score += 10;
  if (dashboardStore.sensors.presence) score += 15;
  if (totalSessions.value > 0) score += 15;
  if (deskAbsences.value === 0) score += 10;
  if (dashboardStore.sensors.temperature > dashboardStore.settings.temperatureThreshold) {
    score -= 10;
  }

  return Math.max(0, Math.min(score, 100));
});

const comfortStatus = computed(() => {
  const temperature = dashboardStore.sensors.temperature;
  const threshold = dashboardStore.settings.temperatureThreshold;

  if (temperature === null) return "Waiting for sensor data";
  if (temperature > threshold) return "Room is warm";
  if (temperature < 20) return "Room is cool";

  return "Comfortable";
});

const latestInsights = computed(() => {
  const insights = [];

  if (dashboardStore.sensors.presence) {
    insights.push("Presence is currently detected at the desk.");
  } else {
    insights.push("No presence detected right now.");
  }

  if (dashboardStore.actuators.fan) {
    insights.push("Fan is active, likely improving room comfort.");
  }

  if (dashboardStore.pomodoro.running) {
    insights.push(`Pomodoro is currently in ${dashboardStore.pomodoro.mode} mode.`);
  } else {
    insights.push("No active pomodoro session at the moment.");
  }

  if (dashboardStore.timeline.length === 0) {
    insights.push("Use the simulator to generate activity for richer analytics.");
  }

  return insights;
});

function goToDashboard() {
  router.push("/dashboard");
}

function goBack() {
  router.back();
}

async function fetchAnalyticsSummary() {
  analyticsLoading.value = true;
  analyticsError.value = "";

  try {
    const response = await api.getAnalyticsSummary();
    analyticsSummary.value = response;
  } catch (error) {
    analyticsError.value = error.message || "Failed to load analytics summary.";
  } finally {
    analyticsLoading.value = false;
  }
}

onMounted(() => {
  fetchAnalyticsSummary();
});
</script>

<template>
  <main class="analytics-page">
    <section class="analytics-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Focus insights</p>
          <h1>Analytics</h1>
          <p class="subtitle">
            Understand your focus rhythm, desk presence, comfort, and daily productivity.
          </p>
        </div>

        <div class="topbar-actions">
          <button class="soft-btn" @click="goBack">
            Back
          </button>

          <button class="dark-btn" @click="goToDashboard">
            Dashboard
          </button>
        </div>
      </header>

      <div v-if="analyticsLoading" class="analytics-notice">
        Loading analytics summary...
      </div>

      <div v-if="analyticsError" class="analytics-notice error">
        {{ analyticsError }}
      </div>

      <section class="score-card">
        <div>
          <p class="eyebrow">Today</p>
          <h2>Productivity score</h2>
          <p class="score-description">
            A temporary simulated score based on presence, pomodoro activity, comfort, and absences.
          </p>
        </div>

        <div class="score-circle">
          <span>{{ productivityScore }}</span>
          <small>/100</small>
        </div>
      </section>

      <section class="summary-grid">
        <article class="summary-card">
          <span>⏱️</span>
          <p>Focus minutes</p>
          <h2>{{ totalFocusMinutes }}</h2>
        </article>

        <article class="summary-card">
          <span>🍅</span>
          <p>Sessions</p>
          <h2>{{ totalSessions }}</h2>
        </article>

        <article class="summary-card">
          <span>🚶</span>
          <p>Desk absences</p>
          <h2>{{ deskAbsences }}</h2>
        </article>

        <article class="summary-card">
          <span>🌀</span>
          <p>Fan activations</p>
          <h2>{{ fanActivations }}</h2>
        </article>

        <article class="summary-card">
          <span>🌡️</span>
          <p>Avg temperature</p>
          <h2>{{ averageTemperature }}°C</h2>
        </article>

        <article class="summary-card">
          <span>✅</span>
          <p>Completed tasks</p>
          <h2>{{ completedTasks }}</h2>
        </article>
      </section>

      <section class="analytics-grid">
        <article class="panel chart-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Weekly</p>
              <h2>Focus minutes per day</h2>
            </div>
          </div>

          <div class="bar-chart">
            <div
              v-for="item in weeklyFocusData"
              :key="item.day"
              class="bar-column"
            >
              <div class="bar-track">
                <div
                  class="bar-fill"
                  :style="{ height: `${item.height}%` }"
                ></div>
              </div>

              <strong>{{ item.value }}</strong>
              <span>{{ item.day }}</span>
            </div>
          </div>
        </article>

        <article class="panel comfort-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Environment</p>
              <h2>Comfort snapshot</h2>
            </div>
          </div>

          <div class="comfort-list">
            <div>
              <span>Temperature</span>
              <strong>
                {{ dashboardStore.sensors.temperature ?? "--" }}°C
              </strong>
            </div>

            <div>
              <span>Humidity</span>
              <strong>
                {{ dashboardStore.sensors.humidity ?? "--" }}%
              </strong>
            </div>

            <div>
              <span>Threshold</span>
              <strong>
                {{ dashboardStore.settings.temperatureThreshold }}°C
              </strong>
            </div>

            <div>
              <span>Fan state</span>
              <strong>
                {{ dashboardStore.actuators.fan ? "On" : "Off" }}
              </strong>
            </div>
          </div>
        </article>

        <article class="panel insights-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Suggestions</p>
              <h2>Deskra insights</h2>
            </div>
          </div>

          <div class="insights-list">
            <div
              v-for="insight in latestInsights"
              :key="insight"
              class="insight-item"
            >
              <span>✦</span>
              <p>{{ insight }}</p>
            </div>
          </div>
        </article>

        <article class="panel activity-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Activity</p>
              <h2>Recent productivity events</h2>
            </div>
          </div>

          <div v-if="dashboardStore.timeline.length" class="activity-list">
            <div
              v-for="event in dashboardStore.timeline.slice(0, 6)"
              :key="event.id"
              class="activity-item"
            >
              <div class="activity-dot"></div>

              <div>
                <strong>{{ event.message }}</strong>
                <p>{{ event.timestamp }}</p>
              </div>
            </div>
          </div>

          <div v-else class="empty-state">
            <h3>No activity yet</h3>
            <p>
              Use the simulator page to generate sensor, login, and pomodoro events.
            </p>
          </div>
        </article>
      </section>
    </section>
  </main>
</template>

<style scoped>
.analytics-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.28), transparent 30%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.2), transparent 32%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.analytics-shell {
  width: min(1180px, 100%);
  margin: 0 auto;
}

.topbar,
.score-card {
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

.subtitle,
.score-description {
  margin: 7px 0 0;
  color: #6c5f53;
  font-size: 16px;
  line-height: 1.6;
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
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

.score-card h2 {
  margin: 0;
  font-size: 30px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.score-circle {
  width: 132px;
  height: 132px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background:
    radial-gradient(circle, #fffaf3 52%, transparent 54%),
    conic-gradient(#2f6f5e 0deg, #65b891 260deg, #eadcc9 260deg);
  box-shadow: inset 0 0 0 8px rgba(255, 250, 243, 0.8);
}

.score-circle span {
  font-size: 38px;
  font-weight: 900;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.score-circle small {
  margin-top: -42px;
  color: #8b735f;
  font-weight: 800;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.summary-card {
  padding: 20px;
  border-radius: 24px;
  background: #fffaf3;
  box-shadow: 0 14px 36px rgba(85, 67, 50, 0.11);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.summary-card span {
  display: block;
  font-size: 26px;
  margin-bottom: 12px;
}

.summary-card p {
  margin: 0 0 5px;
  color: #8b735f;
  font-size: 14px;
  font-weight: 900;
}

.summary-card h2 {
  margin: 0;
  color: #1f2a37;
  font-size: 26px;
  letter-spacing: -0.05em;
}

.analytics-grid {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
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
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0;
  font-size: 27px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.bar-chart {
  height: 320px;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 14px;
  align-items: end;
  padding: 18px;
  border-radius: 22px;
  background: #f7efe5;
}

.bar-column {
  height: 100%;
  display: grid;
  grid-template-rows: 1fr auto auto;
  align-items: end;
  gap: 8px;
  text-align: center;
}

.bar-track {
  height: 100%;
  width: 100%;
  display: flex;
  align-items: end;
  border-radius: 999px;
  background: #fffaf3;
  overflow: hidden;
}

.bar-fill {
  width: 100%;
  min-height: 8%;
  border-radius: 999px 999px 0 0;
  background: linear-gradient(180deg, #65b891, #2f6f5e);
}

.bar-column strong {
  color: #1f2a37;
  font-size: 14px;
}

.bar-column span {
  color: #8b735f;
  font-size: 13px;
  font-weight: 900;
}

.comfort-list {
  display: grid;
  gap: 12px;
}

.comfort-list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  background: #f7efe5;
}

.comfort-list span {
  color: #8b735f;
  font-weight: 800;
}

.comfort-list strong {
  color: #1f2a37;
}

.insights-list {
  display: grid;
  gap: 12px;
}

.insight-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  background: #f7efe5;
}

.insight-item span {
  color: #2f6f5e;
  font-weight: 900;
}

.insight-item p {
  margin: 0;
  color: #4c423a;
  line-height: 1.6;
  font-weight: 700;
}

.activity-list {
  display: grid;
  gap: 12px;
}

.activity-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 13px;
  border-radius: 16px;
  background: #f7efe5;
}

.activity-dot {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  margin-top: 5px;
  background: #f8c471;
  box-shadow: 0 0 0 4px rgba(248, 196, 113, 0.18);
}

.activity-item strong {
  color: #1f2a37;
}

.activity-item p {
  margin: 5px 0 0;
  color: #8b735f;
  font-size: 13px;
}

.empty-state {
  padding: 32px;
  border-radius: 22px;
  background: #f7efe5;
  text-align: center;
}

.empty-state h3 {
  margin: 0 0 8px;
  color: #1f2a37;
  font-size: 22px;
}

.empty-state p {
  margin: 0;
  color: #8b735f;
  line-height: 1.6;
}

.analytics-notice {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 18px;
  background: #e4f0ea;
  color: #2f6f5e;
  font-weight: 900;
}

.analytics-notice.error {
  background: #ffe7e1;
  color: #a54b3f;
}

@media (max-width: 1100px) {
  .summary-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .analytics-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .analytics-page {
    padding: 18px;
  }

  .topbar,
  .score-card {
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

  .score-circle {
    align-self: center;
  }

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .bar-chart {
    gap: 8px;
    padding: 12px;
  }

  .comfort-list div {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
