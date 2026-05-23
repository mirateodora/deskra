<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api";

const router = useRouter();
const dashboardStore = useDashboardStore();

const name = ref("");
const pin = ref("");
const confirmPin = ref("");
const focusLedColor = ref("#d66b5d");
const breakLedColor = ref("#65b891");
const focusMinutes = ref(25);
const breakMinutes = ref(5);
const temperatureThreshold = ref(26);
const faceImageName = ref("");

const loading = ref(false);
const errorMessage = ref("");

function handleFaceImageUpload(event) {
  const file = event.target.files?.[0];

  if (!file) {
    faceImageName.value = "";
    return;
  }

  faceImageName.value = file.name;
}

async function handleRegister() {
  errorMessage.value = "";

  if (!name.value.trim()) {
    errorMessage.value = "Please enter your name.";
    return;
  }

  if (!pin.value.trim()) {
    errorMessage.value = "Please create a PIN.";
    return;
  }

  if (pin.value.length < 4) {
    errorMessage.value = "PIN should have at least 4 digits.";
    return;
  }

  if (pin.value !== confirmPin.value) {
    errorMessage.value = "PINs do not match.";
    return;
  }

  loading.value = true;

  try {
    const response = await api.registerUser({
      name: name.value.trim(),
      pin: pin.value.trim(),
      focusLedColor: focusLedColor.value,
      breakLedColor: breakLedColor.value,
      focusMinutes: Number(focusMinutes.value),
      breakMinutes: Number(breakMinutes.value),
      temperatureThreshold: Number(temperatureThreshold.value),
      faceImageName: faceImageName.value,
    });

    dashboardStore.applyAuthUpdate(response.auth);

    if (response.settings) {
      dashboardStore.applySettingsUpdate(response.settings);
    }

    if (response.user?.focusLedColor) {
      dashboardStore.applyActuatorUpdate({
        ledColor: response.user.focusLedColor,
      });
    }

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.accessLog) {
      dashboardStore.addAccessLog(response.accessLog);
    }

    dashboardStore.applyPomodoroUpdate({
      focusMinutes: Number(focusMinutes.value),
      breakMinutes: Number(breakMinutes.value),
      remainingSeconds: Number(focusMinutes.value) * 60,
    });

    router.push("/dashboard");
  } catch (error) {
    errorMessage.value = error.message || "Registration failed. Please try again.";
  } finally {
    loading.value = false;
  }
}
function goBack() {
  router.push("/");
}
</script>

<template>
  <main class="register-page">
    <section class="register-shell">
      <button class="back-btn" @click="goBack">
        ← Back
      </button>

      <section class="register-card">
        <div class="left-panel">
          <div class="brand-row">
            <div class="logo-badge">🌱</div>
            <div>
              <h1>Deskra</h1>
              <p>Build your focus profile</p>
            </div>
          </div>

          <div class="cozy-illustration">
            <div class="glow"></div>

            <div class="profile-card">
              <div class="avatar">
                <span>🙂</span>
              </div>

              <div class="profile-lines">
                <div class="line long"></div>
                <div class="line medium"></div>
                <div class="line short"></div>
              </div>
            </div>

            <div class="color-dots">
              <span :style="{ background: focusLedColor }"></span>
              <span :style="{ background: breakLedColor }"></span>
              <span style="background: #f8c471"></span>
            </div>

            <div class="plant">
              <div class="leaf leaf-one"></div>
              <div class="leaf leaf-two"></div>
              <div class="pot"></div>
            </div>
          </div>

          <p class="side-note">
            Personalize your desk before your first focus session: choose your focus light,
            break light, timer rhythm, room comfort, and future Face ID setup.
          </p>
        </div>

        <div class="form-panel">
          <p class="eyebrow">New profile</p>

          <h2>Create your workspace</h2>

          <p class="description">
            Set up your Deskra profile so the dashboard can adapt to your focus style.
          </p>

          <form @submit.prevent="handleRegister">
            <div class="form-grid">
              <label class="full-width">
                Name
                <input
                  v-model="name"
                  type="text"
                  placeholder="e.g. Alex"
                  autocomplete="name"
                />
              </label>

              <label>
                PIN
                <input
                  v-model="pin"
                  type="password"
                  placeholder="Create PIN"
                  autocomplete="new-password"
                  maxlength="8"
                />
              </label>

              <label>
                Confirm PIN
                <input
                  v-model="confirmPin"
                  type="password"
                  placeholder="Repeat PIN"
                  autocomplete="new-password"
                  maxlength="8"
                />
              </label>

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

              <label class="full-width">
                Temp threshold
                <input
                  v-model="temperatureThreshold"
                  type="number"
                  min="15"
                  max="40"
                  step="0.5"
                />
              </label>

              <label class="full-width">
                Face picture
                <div class="upload-box">
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleFaceImageUpload"
                  />
                  <div>
                    <strong>
                      {{ faceImageName || "Upload a face picture" }}
                    </strong>
                    <p>Placeholder for future Face ID registration.</p>
                  </div>
                </div>
              </label>
            </div>

            <p v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </p>

            <button class="primary-btn" type="submit" :disabled="loading">
              {{ loading ? "Creating..." : "Create Profile" }}
            </button>
          </form>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  padding: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.35), transparent 32%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.22), transparent 34%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.register-shell {
  width: min(1120px, 100%);
}

.back-btn {
  margin-bottom: 18px;
  border: none;
  background: rgba(255, 250, 243, 0.7);
  color: #6c5f53;
  padding: 12px 16px;
  border-radius: 999px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 12px 30px rgba(85, 67, 50, 0.1);
  transition: transform 0.2s ease, color 0.2s ease;
}

.back-btn:hover {
  transform: translateY(-2px);
  color: #2f6f5e;
}

.register-card {
  display: grid;
  grid-template-columns: 0.9fr 1.1fr;
  gap: 22px;
  padding: 22px;
  border-radius: 36px;
  background: rgba(255, 250, 242, 0.72);
  backdrop-filter: blur(16px);
  box-shadow: 0 24px 80px rgba(85, 67, 50, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.left-panel,
.form-panel {
  min-height: 640px;
  border-radius: 28px;
}

.left-panel {
  position: relative;
  overflow: hidden;
  padding: 34px;
  background:
    linear-gradient(160deg, rgba(31, 42, 55, 0.96), rgba(57, 72, 87, 0.94)),
    #253140;
  color: #fffaf3;
}

.brand-row {
  display: flex;
  align-items: center;
  gap: 14px;
  position: relative;
  z-index: 2;
}

.logo-badge {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: #fff8ee;
  color: #24313f;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.18);
  font-size: 24px;
}

.brand-row h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: -0.04em;
}

.brand-row p {
  margin: 4px 0 0;
  color: #d8cdbf;
  font-size: 16px;
}

.cozy-illustration {
  position: absolute;
  left: 50%;
  top: 46%;
  width: 78%;
  height: 350px;
  transform: translate(-50%, -50%);
}

.glow {
  position: absolute;
  top: 38px;
  left: 50%;
  width: 210px;
  height: 210px;
  border-radius: 50%;
  transform: translateX(-50%);
  background: rgba(248, 196, 113, 0.25);
  box-shadow: 0 0 110px rgba(248, 196, 113, 0.48);
}

.profile-card {
  position: absolute;
  left: 50%;
  bottom: 74px;
  width: 270px;
  height: 190px;
  transform: translateX(-50%) rotate(-3deg);
  border-radius: 28px;
  background: #fff4df;
  box-shadow: 0 24px 44px rgba(0, 0, 0, 0.24);
  padding: 28px;
  display: flex;
  gap: 18px;
  align-items: center;
}

.avatar {
  width: 82px;
  height: 82px;
  flex: 0 0 auto;
  border-radius: 28px;
  background: #e4f0ea;
  display: grid;
  place-items: center;
  font-size: 36px;
}

.profile-lines {
  flex: 1;
}

.line {
  height: 14px;
  border-radius: 999px;
  background: #79d8b2;
  margin-bottom: 18px;
}

.line.long {
  width: 100%;
}

.line.medium {
  width: 74%;
  background: #f8c471;
}

.line.short {
  width: 52%;
  background: #8fb5ff;
}

.color-dots {
  position: absolute;
  left: 52px;
  bottom: 72px;
  display: flex;
  gap: 10px;
}

.color-dots span {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  box-shadow: 0 0 0 5px rgba(255, 250, 243, 0.14);
}

.plant {
  position: absolute;
  right: 22px;
  bottom: 56px;
  width: 86px;
  height: 130px;
}

.leaf {
  position: absolute;
  bottom: 46px;
  width: 48px;
  height: 78px;
  border-radius: 999px 999px 999px 0;
  background: #79d8b2;
}

.leaf-one {
  left: 8px;
  transform: rotate(-32deg);
}

.leaf-two {
  right: 4px;
  transform: rotate(34deg);
  background: #5fb99a;
}

.pot {
  position: absolute;
  bottom: 0;
  left: 18px;
  width: 54px;
  height: 54px;
  border-radius: 8px 8px 18px 18px;
  background: #d98c58;
}

.side-note {
  position: absolute;
  left: 34px;
  right: 34px;
  bottom: 34px;
  margin: 0;
  color: #eadfce;
  font-size: 17px;
  line-height: 1.7;
  z-index: 2;
}

.form-panel {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 42px;
  background: #fffaf3;
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.eyebrow {
  margin: 0 0 8px;
  color: #5f9e86;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 13px;
}

.form-panel h2 {
  margin: 0;
  font-size: 42px;
  line-height: 1.05;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.description {
  margin: 18px 0 28px;
  color: #6c5f53;
  font-size: 18px;
  line-height: 1.7;
}

form {
  display: grid;
  gap: 18px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.full-width {
  grid-column: 1 / -1;
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

.upload-box {
  position: relative;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 14px;
  align-items: center;
  padding: 16px;
  border: 1px dashed #d7c7b2;
  border-radius: 18px;
  background: #fffdf9;
}

.upload-box::before {
  content: "📷";
  width: 48px;
  height: 48px;
  display: grid;
  place-items: center;
  border-radius: 16px;
  background: #f5eadb;
  font-size: 22px;
}

.upload-box input {
  position: absolute;
  inset: 0;
  opacity: 0;
  cursor: pointer;
}

.upload-box strong {
  display: block;
  color: #2f6f5e;
  font-size: 16px;
}

.upload-box p {
  margin: 4px 0 0;
  color: #8b735f;
  font-size: 14px;
  line-height: 1.4;
}

.error-message {
  margin: 0;
  padding: 12px 14px;
  border-radius: 14px;
  background: #ffe7e1;
  color: #a54b3f;
  font-size: 15px;
  font-weight: 700;
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

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
  transform: none;
}

.primary-btn {
  padding: 17px 20px;
  border-radius: 16px;
  font-size: 17px;
  color: #fffaf3;
  background: #2f6f5e;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.25);
}

@media (max-width: 980px) {
  .register-page {
    padding: 18px;
    align-items: flex-start;
  }

  .register-card {
    grid-template-columns: 1fr;
  }

  .left-panel {
    min-height: 380px;
  }

  .form-panel {
    min-height: auto;
    padding: 32px;
  }

  .form-panel h2 {
    font-size: 36px;
  }

  .cozy-illustration {
    height: 260px;
    top: 54%;
  }

  .side-note {
    position: relative;
    left: auto;
    right: auto;
    bottom: auto;
    margin-top: 260px;
  }
}

@media (max-width: 620px) {
  .register-card {
    padding: 14px;
    border-radius: 26px;
  }

  .left-panel,
  .form-panel {
    border-radius: 22px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .full-width {
    grid-column: auto;
  }

  .brand-row h1 {
    font-size: 28px;
  }
}
</style>
