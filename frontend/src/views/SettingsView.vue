<script setup>
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api"

const router = useRouter();
const dashboardStore = useDashboardStore();

const name = ref("");
const focusLedColor = ref("#d66b5d");
const breakLedColor = ref("#65b891");
const focusMinutes = ref(25);
const breakMinutes = ref(5);
const temperatureThreshold = ref(26);
const musicEnabled = ref(false);

const savedMessage = ref("");

onMounted(() => {
  name.value = dashboardStore.auth.currentUser?.name || "Guest";

  focusLedColor.value =
    dashboardStore.settings.focusLedColor ||
    dashboardStore.auth.currentUser?.focusLedColor ||
    "#d66b5d";

  breakLedColor.value =
    dashboardStore.settings.breakLedColor ||
    dashboardStore.auth.currentUser?.breakLedColor ||
    "#65b891";

  focusMinutes.value =
    dashboardStore.settings.defaultFocusMinutes ||
    dashboardStore.pomodoro.focusMinutes ||
    25;

  breakMinutes.value =
    dashboardStore.settings.defaultBreakMinutes ||
    dashboardStore.pomodoro.breakMinutes ||
    5;

  temperatureThreshold.value =
    dashboardStore.settings.temperatureThreshold || 26;

  musicEnabled.value =
    dashboardStore.settings.musicEnabled || false;
});

async function saveSettings() {
  savedMessage.value = "";

  try {
    const response = await api.updateSettings({
      focusLedColor: focusLedColor.value,
      breakLedColor: breakLedColor.value,
      defaultFocusMinutes: Number(focusMinutes.value),
      defaultBreakMinutes: Number(breakMinutes.value),
      temperatureThreshold: Number(temperatureThreshold.value),
      musicEnabled: Boolean(musicEnabled.value),
    });

    dashboardStore.applySettingsUpdate(response.settings);
    dashboardStore.applyPomodoroUpdate(response.pomodoro);
    dashboardStore.applyAuthUpdate(response.auth);

    if (response.command) {
      dashboardStore.commands.unshift(response.command);
    }

    savedMessage.value = "Settings saved to backend.";

    setTimeout(() => {
      savedMessage.value = "";
    }, 2500);
  } catch (error) {
    savedMessage.value = error.message || "Failed to save settings.";
  }
}

function goToDashboard() {
  router.push("/dashboard");
}

function goBack() {
  router.back();
}
</script>

<template>
  <main class="settings-page">
    <section class="settings-shell">
      <header class="topbar">
        <div>
          <p class="eyebrow">Preferences</p>
          <h1>Settings</h1>
          <p class="subtitle">
            Tune your desk lights, focus rhythm, room comfort, and music behavior.
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

      <section v-if="savedMessage" class="toast">
        {{ savedMessage }}
      </section>

      <section class="settings-grid">
        <article class="panel profile-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Profile</p>
              <h2>User identity</h2>
            </div>
          </div>

          <label>
            Display name
            <input
              v-model="name"
              type="text"
              placeholder="Your name"
              :disabled="!dashboardStore.auth.currentUser"
            />
          </label>

          <p v-if="!dashboardStore.auth.currentUser" class="hint">
            Guest mode is active. Create an account to save personal profile settings later.
          </p>
        </article>

        <article class="panel led-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Lighting</p>
              <h2>Pomodoro LED colors</h2>
            </div>
          </div>

          <div class="color-grid">
            <label>
              Focus LED
              <div class="color-input-row">
                <input
                  v-model="focusLedColor"
                  class="color-input"
                  type="color"
                />
                <span>{{ focusLedColor }}</span>
              </div>
            </label>

            <label>
              Break LED
              <div class="color-input-row">
                <input
                  v-model="breakLedColor"
                  class="color-input"
                  type="color"
                />
                <span>{{ breakLedColor }}</span>
              </div>
            </label>
          </div>

          <div class="led-preview-row">
            <div class="preview-block">
              <div
                class="led-preview"
                :style="{ background: focusLedColor }"
              ></div>
              <strong>Focus</strong>
            </div>

            <div class="preview-block">
              <div
                class="led-preview"
                :style="{ background: breakLedColor }"
              ></div>
              <strong>Break</strong>
            </div>
          </div>
        </article>

        <article class="panel timer-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Timer</p>
              <h2>Pomodoro rhythm</h2>
            </div>
          </div>

          <div class="input-grid">
            <label>
              Focus minutes
              <input
                v-model="focusMinutes"
                type="number"
                min="1"
                max="120"
              />
            </label>

            <label>
              Break minutes
              <input
                v-model="breakMinutes"
                type="number"
                min="1"
                max="60"
              />
            </label>
          </div>

          <div class="timer-preview">
            <div>
              <span>{{ focusMinutes }}</span>
              <p>focus</p>
            </div>

            <div class="divider-dot"></div>

            <div>
              <span>{{ breakMinutes }}</span>
              <p>break</p>
            </div>
          </div>
        </article>

        <article class="panel comfort-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Comfort</p>
              <h2>Room automation</h2>
            </div>
          </div>

          <label>
            Auto-fan temperature threshold
            <input
              v-model="temperatureThreshold"
              type="number"
              min="15"
              max="40"
              step="0.5"
            />
          </label>

          <p class="hint">
            When temperature rises above this value, Deskra can automatically trigger the fan.
          </p>
        </article>

        <article class="panel music-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Focus audio</p>
              <h2>Music behavior</h2>
            </div>
          </div>

          <div class="toggle-row">
            <div>
              <strong>Play music during focus</strong>
              <p>Useful for deep work sessions. The browser will handle playback later.</p>
            </div>

            <label class="switch">
              <input
                v-model="musicEnabled"
                type="checkbox"
              />
              <span></span>
            </label>
          </div>
        </article>

        <article class="panel summary-panel">
          <div class="panel-header">
            <div>
              <p class="eyebrow">Summary</p>
              <h2>Current setup</h2>
            </div>
          </div>

          <div class="summary-list">
            <div>
              <span>Focus LED</span>
              <strong>{{ focusLedColor }}</strong>
            </div>

            <div>
              <span>Break LED</span>
              <strong>{{ breakLedColor }}</strong>
            </div>

            <div>
              <span>Pomodoro</span>
              <strong>{{ focusMinutes }} + {{ breakMinutes }} min</strong>
            </div>

            <div>
              <span>Auto-fan</span>
              <strong>{{ temperatureThreshold }}°C</strong>
            </div>

            <div>
              <span>Music</span>
              <strong>{{ musicEnabled ? "Enabled" : "Disabled" }}</strong>
            </div>
          </div>
        </article>
      </section>

      <section class="save-bar">
        <div>
          <strong>Ready to save?</strong>
          <p>Your dashboard will update immediately.</p>
        </div>

        <button class="save-btn" @click="saveSettings">
          Save Settings
        </button>
      </section>
    </section>
  </main>
</template>

<style scoped>
.settings-page {
  min-height: 100vh;
  padding: 28px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.28), transparent 30%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.2), transparent 32%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.settings-shell {
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

.settings-grid {
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

.panel-header {
  margin-bottom: 18px;
}

.panel-header h2 {
  margin: 0;
  font-size: 27px;
  letter-spacing: -0.04em;
  color: #1f2a37;
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

input:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

input:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.hint {
  margin: 12px 0 0;
  color: #8b735f;
  font-size: 15px;
  line-height: 1.6;
}

.color-grid,
.input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.color-input-row {
  display: grid;
  grid-template-columns: 58px 1fr;
  align-items: center;
  gap: 12px;
  padding: 8px 14px 8px 8px;
  border: 1px solid #eadcc9;
  border-radius: 16px;
  background: #fffdf9;
  color: #6c5f53;
  font-size: 15px;
  font-weight: 800;
}

.color-input {
  height: 44px;
  padding: 0;
  border: none;
  background: transparent;
  cursor: pointer;
}

.led-preview-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
  margin-top: 18px;
}

.preview-block {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border-radius: 18px;
  background: #f7efe5;
}

.led-preview {
  width: 44px;
  height: 44px;
  border-radius: 15px;
  box-shadow: 0 0 0 5px rgba(255, 250, 243, 0.9);
}

.timer-preview {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 14px;
  margin-top: 18px;
  padding: 18px;
  border-radius: 22px;
  background: #f7efe5;
  text-align: center;
}

.timer-preview span {
  display: block;
  color: #1f2a37;
  font-size: 36px;
  font-weight: 900;
  letter-spacing: -0.05em;
}

.timer-preview p {
  margin: 4px 0 0;
  color: #8b735f;
  font-size: 14px;
  font-weight: 800;
}

.divider-dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  background: #f8c471;
  box-shadow: 0 0 0 5px rgba(248, 196, 113, 0.18);
}

.toggle-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 16px;
  border-radius: 20px;
  background: #f7efe5;
}

.toggle-row strong {
  color: #1f2a37;
}

.toggle-row p {
  margin: 6px 0 0;
  color: #8b735f;
  font-size: 15px;
  line-height: 1.5;
}

.switch {
  position: relative;
  width: 62px;
  height: 36px;
  flex: 0 0 auto;
  display: block;
}

.switch input {
  display: none;
}

.switch span {
  position: absolute;
  inset: 0;
  border-radius: 999px;
  background: #eadcc9;
  cursor: pointer;
  transition: background 0.2s ease;
}

.switch span::after {
  content: "";
  position: absolute;
  top: 5px;
  left: 5px;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #fffaf3;
  box-shadow: 0 4px 12px rgba(85, 67, 50, 0.18);
  transition: transform 0.2s ease;
}

.switch input:checked + span {
  background: #65b891;
}

.switch input:checked + span::after {
  transform: translateX(26px);
}

.summary-list {
  display: grid;
  gap: 12px;
}

.summary-list div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  background: #f7efe5;
}

.summary-list span {
  color: #8b735f;
  font-weight: 800;
}

.summary-list strong {
  color: #1f2a37;
}

.save-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-top: 16px;
  padding: 22px;
  border-radius: 28px;
  background: rgba(255, 250, 242, 0.84);
  border: 1px solid rgba(255, 255, 255, 0.62);
  box-shadow: 0 18px 50px rgba(85, 67, 50, 0.12);
}

.save-bar strong {
  color: #1f2a37;
  font-size: 18px;
}

.save-bar p {
  margin: 5px 0 0;
  color: #8b735f;
}

.save-btn {
  padding: 15px 20px;
  border-radius: 16px;
  background: #2f6f5e;
  color: #fffaf3;
  font-size: 16px;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.22);
}

@media (max-width: 880px) {
  .settings-page {
    padding: 18px;
  }

  .topbar,
  .save-bar {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-actions {
    width: 100%;
    flex-direction: column;
    align-items: stretch;
  }

  .soft-btn,
  .dark-btn,
  .save-btn {
    width: 100%;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .color-grid,
  .input-grid,
  .led-preview-row {
    grid-template-columns: 1fr;
  }

  .toggle-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .summary-list div {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
