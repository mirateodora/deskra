<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";

const router = useRouter();
const dashboardStore = useDashboardStore();

const selectedMethod = ref("all");
const selectedStatus = ref("all");
const searchQuery = ref("");

const filteredLogs = computed(() => {
  return dashboardStore.accessLogs.filter((log) => {
    const matchesMethod =
      selectedMethod.value === "all" || log.method === selectedMethod.value;

    const matchesStatus =
      selectedStatus.value === "all" ||
      (selectedStatus.value === "success" && log.success) ||
      (selectedStatus.value === "failed" && !log.success);

    const userName = log.user?.name || "Unknown";
    const searchableText = `${userName} ${log.method} ${log.message}`.toLowerCase();

    const matchesSearch = searchableText.includes(searchQuery.value.toLowerCase());

    return matchesMethod && matchesStatus && matchesSearch;
  });
});

const totalAttempts = computed(() => dashboardStore.accessLogs.length);

const successCount = computed(() => {
  return dashboardStore.accessLogs.filter((log) => log.success).length;
});

const failedCount = computed(() => {
  return dashboardStore.accessLogs.filter((log) => !log.success).length;
});

const faceIdCount = computed(() => {
  return dashboardStore.accessLogs.filter((log) => log.method === "face_id").length;
});

function formatMethod(method) {
  if (method === "face_id") return "Face ID";
  if (method === "manual_pin") return "Manual PIN";
  if (method === "register") return "Register";

  return method || "Unknown";
}

function formatTime(timestamp) {
  if (!timestamp) return "No timestamp";

  return new Date(timestamp).toLocaleString();
}

function goToDashboard() {
  router.push("/dashboard");
}

function goBack() {
  router.back();
}
</script>

<template>
  <main class="logs-page">
    <section class="logs-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Security history</p>
          <h1>Access Logs</h1>
          <p class="subtitle">
            Review Face ID and manual login attempts for your smart desk.
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

      <section class="summary-grid">
        <article class="summary-card">
          <span>🧾</span>
          <p>Total attempts</p>
          <h2>{{ totalAttempts }}</h2>
        </article>

        <article class="summary-card">
          <span>✅</span>
          <p>Successful</p>
          <h2>{{ successCount }}</h2>
        </article>

        <article class="summary-card">
          <span>⚠️</span>
          <p>Failed</p>
          <h2>{{ failedCount }}</h2>
        </article>

        <article class="summary-card">
          <span>🙂</span>
          <p>Face ID attempts</p>
          <h2>{{ faceIdCount }}</h2>
        </article>
      </section>

      <section class="filters-card">
        <div class="filter-group">
          <label>
            Search
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search user, method, or message..."
            />
          </label>
        </div>

        <div class="filter-group">
          <label>
            Method
            <select v-model="selectedMethod">
              <option value="all">All methods</option>
              <option value="face_id">Face ID</option>
              <option value="manual_pin">Manual PIN</option>
              <option value="register">Register</option>
            </select>
          </label>
        </div>

        <div class="filter-group">
          <label>
            Status
            <select v-model="selectedStatus">
              <option value="all">All statuses</option>
              <option value="success">Successful</option>
              <option value="failed">Failed</option>
            </select>
          </label>
        </div>
      </section>

      <section class="logs-card">
        <div class="logs-header">
          <div>
            <p class="eyebrow">Attempts</p>
            <h2>Login activity</h2>
          </div>

          <span>{{ filteredLogs.length }} shown</span>
        </div>

        <div v-if="filteredLogs.length" class="logs-list">
          <article
            v-for="log in filteredLogs"
            :key="log.id"
            class="log-item"
          >
            <div
              class="status-icon"
              :class="{ success: log.success, failed: !log.success }"
            >
              {{ log.success ? "✓" : "!" }}
            </div>

            <div class="log-content">
              <div class="log-title-row">
                <h3>
                  {{ log.success ? "Access granted" : "Access denied" }}
                </h3>

                <span
                  class="status-badge"
                  :class="{ success: log.success, failed: !log.success }"
                >
                  {{ log.success ? "Success" : "Failed" }}
                </span>
              </div>

              <p class="log-message">
                {{ log.message || "No message provided." }}
              </p>

              <div class="log-meta">
                <span>User: {{ log.user?.name || "Unknown" }}</span>
                <span>Method: {{ formatMethod(log.method) }}</span>
                <span>{{ formatTime(log.timestamp) }}</span>
              </div>
            </div>
          </article>
        </div>

        <div v-else class="empty-state">
          <h3>No access logs found</h3>
          <p>
            Login attempts from Face ID, manual PIN, and registration will appear here.
          </p>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.logs-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.28), transparent 30%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.2), transparent 32%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.logs-shell {
  width: min(1180px, 100%);
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

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
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
  font-size: 30px;
  letter-spacing: -0.05em;
}

.filters-card {
  display: grid;
  grid-template-columns: 1.4fr 0.8fr 0.8fr;
  gap: 14px;
  padding: 20px;
  margin-bottom: 16px;
  border-radius: 28px;
  background: rgba(255, 250, 243, 0.92);
  box-shadow: 0 14px 42px rgba(85, 67, 50, 0.12);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

label {
  display: grid;
  gap: 8px;
  color: #4c423a;
  font-weight: 800;
  font-size: 15px;
}

input,
select {
  width: 100%;
  box-sizing: border-box;
  padding: 15px 16px;
  border: 1px solid #eadcc9;
  border-radius: 16px;
  background: #fffdf9;
  color: #24313f;
  font-size: 16px;
  outline: none;
  font-family: inherit;
}

input:focus,
select:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.logs-card {
  padding: 24px;
  border-radius: 28px;
  background: rgba(255, 250, 243, 0.92);
  box-shadow: 0 14px 42px rgba(85, 67, 50, 0.12);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.logs-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
}

.logs-header h2 {
  margin: 0;
  font-size: 27px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.logs-header span {
  padding: 9px 12px;
  border-radius: 999px;
  background: #e4f0ea;
  color: #2f6f5e;
  font-weight: 900;
  font-size: 13px;
}

.logs-list {
  display: grid;
  gap: 12px;
}

.log-item {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
  padding: 16px;
  border-radius: 20px;
  background: #f7efe5;
}

.status-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 15px;
  font-weight: 900;
  font-size: 20px;
}

.status-icon.success {
  background: #e4f0ea;
  color: #2f6f5e;
}

.status-icon.failed {
  background: #ffe7e1;
  color: #a54b3f;
}

.log-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.log-title-row h3 {
  margin: 0;
  color: #1f2a37;
  font-size: 18px;
}

.status-badge {
  padding: 7px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
}

.status-badge.success {
  background: #e4f0ea;
  color: #2f6f5e;
}

.status-badge.failed {
  background: #ffe7e1;
  color: #a54b3f;
}

.log-message {
  margin: 8px 0 12px;
  color: #6c5f53;
  line-height: 1.6;
}

.log-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.log-meta span {
  padding: 8px 10px;
  border-radius: 999px;
  background: #fffaf3;
  color: #8b735f;
  font-size: 13px;
  font-weight: 800;
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

@media (max-width: 980px) {
  .summary-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .filters-card {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .logs-page {
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

  .summary-grid {
    grid-template-columns: 1fr;
  }

  .log-title-row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
