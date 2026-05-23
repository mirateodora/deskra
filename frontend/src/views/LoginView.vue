<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";
import api from "@/services/api";

const router = useRouter();
const dashboardStore = useDashboardStore();

const name = ref("");
const pin = ref("");
const loading = ref(false);
const errorMessage = ref("");

async function handleLogin() {
  errorMessage.value = "";

  if (!name.value.trim() || !pin.value.trim()) {
    errorMessage.value = "Please enter your name and PIN.";
    return;
  }

  loading.value = true;

  try {
    const response = await api.manualLogin({
      name: name.value.trim(),
      pin: pin.value.trim(),
    });

    dashboardStore.applyAuthUpdate(response.auth);

    if (response.timelineEvent) {
      dashboardStore.addTimelineEvent(response.timelineEvent);
    }

    if (response.accessLog) {
      dashboardStore.addAccessLog(response.accessLog);
    }

    router.push("/dashboard");
  } catch (error) {
    dashboardStore.applyAuthUpdate({
      locked: true,
      currentUser: null,
      loginMethod: null,
    });

    errorMessage.value = error.message || "Invalid name or PIN.";
  } finally {
    loading.value = false;
  }
}

function goBack() {
  router.push("/");
}

function goToRegister() {
  router.push("/register");
}

function continueAsGuest() {
  router.push("/dashboard");
}
</script>

<template>
  <main class="login-page">
    <section class="login-shell">
      <button class="back-btn" @click="goBack">
        ← Back
      </button>

      <section class="login-card">
        <div class="left-panel">
          <div class="brand-row">
            <div class="logo-badge">☕</div>
            <div>
              <h1>Deskra</h1>
              <p>Manual access</p>
            </div>
          </div>

          <div class="cozy-illustration">
            <div class="glow"></div>

            <div class="notebook">
              <div class="line long"></div>
              <div class="line medium"></div>
              <div class="line short"></div>
            </div>

            <div class="mug">
              <div class="mug-body"></div>
              <div class="mug-handle"></div>
              <div class="steam steam-one"></div>
              <div class="steam steam-two"></div>
            </div>

            <div class="plant">
              <div class="leaf leaf-one"></div>
              <div class="leaf leaf-two"></div>
              <div class="pot"></div>
            </div>
          </div>

          <p class="side-note">
            Use your PIN when Face ID is unavailable. Your cozy focus setup is one step away.
          </p>
        </div>

        <div class="form-panel">
          <p class="eyebrow">Fallback login</p>

          <h2>Welcome back</h2>

          <p class="description">
            Enter your name and PIN to unlock the dashboard and continue your focus session.
          </p>

          <form @submit.prevent="handleLogin">
            <label>
              Name
              <input
                v-model="name"
                type="text"
                placeholder="e.g. Alex"
                autocomplete="username"
              />
            </label>

            <label>
              PIN
              <input
                v-model="pin"
                type="password"
                placeholder="Enter your PIN"
                autocomplete="current-password"
                maxlength="8"
              />
            </label>

            <p v-if="errorMessage" class="error-message">
              {{ errorMessage }}
            </p>

            <button class="primary-btn" type="submit" :disabled="loading">
              {{ loading ? "Unlocking..." : "Unlock Dashboard" }}
            </button>
          </form>

          <div class="divider">
            <span></span>
            <p>or</p>
            <span></span>
          </div>

          <div class="secondary-actions">
            <button class="secondary-btn" @click="goToRegister">
              Create Account
            </button>

            <button class="guest-btn" @click="continueAsGuest">
              Continue as Guest
            </button>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.login-page {
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

.login-shell {
  width: min(1040px, 100%);
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

.login-card {
  display: grid;
  grid-template-columns: 0.95fr 1.05fr;
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
  min-height: 560px;
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
  top: 48%;
  width: 78%;
  height: 330px;
  transform: translate(-50%, -50%);
}

.glow {
  position: absolute;
  top: 30px;
  left: 50%;
  width: 190px;
  height: 190px;
  border-radius: 50%;
  transform: translateX(-50%);
  background: rgba(248, 196, 113, 0.28);
  box-shadow: 0 0 110px rgba(248, 196, 113, 0.48);
}

.notebook {
  position: absolute;
  left: 50%;
  bottom: 40px;
  width: 260px;
  height: 175px;
  transform: translateX(-50%) rotate(-4deg);
  border-radius: 24px;
  background: #fff4df;
  box-shadow: 0 24px 40px rgba(0, 0, 0, 0.22);
  padding: 42px 32px;
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
  width: 72%;
  background: #f8c471;
}

.line.short {
  width: 48%;
  background: #8fb5ff;
}

.mug {
  position: absolute;
  left: 34px;
  bottom: 34px;
  width: 95px;
  height: 110px;
}

.mug-body {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 72px;
  height: 76px;
  border-radius: 12px 12px 24px 24px;
  background: #d98c58;
}

.mug-handle {
  position: absolute;
  right: 0;
  bottom: 22px;
  width: 34px;
  height: 38px;
  border: 8px solid #d98c58;
  border-left: none;
  border-radius: 0 999px 999px 0;
}

.steam {
  position: absolute;
  width: 10px;
  height: 42px;
  border-radius: 999px;
  background: rgba(255, 244, 223, 0.6);
  top: 0;
}

.steam-one {
  left: 18px;
}

.steam-two {
  left: 42px;
  top: 8px;
}

.plant {
  position: absolute;
  right: 24px;
  bottom: 42px;
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
  padding: 46px;
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
  font-size: 44px;
  line-height: 1.05;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.description {
  margin: 18px 0 30px;
  color: #6c5f53;
  font-size: 18px;
  line-height: 1.8;
}

form {
  display: grid;
  gap: 18px;
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
  padding: 16px 18px;
  border: 1px solid #eadcc9;
  border-radius: 16px;
  background: #fffdf9;
  color: #24313f;
  font-size: 17px;
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

input:focus {
  border-color: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
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
  margin-top: 4px;
  padding: 17px 20px;
  border-radius: 16px;
  font-size: 17px;
  color: #fffaf3;
  background: #2f6f5e;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.25);
}

.divider {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 12px;
  margin: 26px 0;
}

.divider span {
  height: 1px;
  background: #eadcc9;
}

.divider p {
  margin: 0;
  color: #9a8774;
  font-size: 14px;
  font-weight: 700;
}

.secondary-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.secondary-btn,
.guest-btn {
  padding: 15px 18px;
  border-radius: 16px;
  font-size: 16px;
}

.secondary-btn {
  color: #2f6f5e;
  background: #e4f0ea;
}

.guest-btn {
  color: #8b735f;
  background: #f7efe5;
}

.guest-btn:hover {
  color: #2f6f5e;
}

@media (max-width: 900px) {
  .login-page {
    padding: 18px;
    align-items: flex-start;
  }

  .login-card {
    grid-template-columns: 1fr;
  }

  .left-panel {
    min-height: 360px;
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

@media (max-width: 540px) {
  .login-card {
    padding: 14px;
    border-radius: 26px;
  }

  .left-panel,
  .form-panel {
    border-radius: 22px;
  }

  .secondary-actions {
    grid-template-columns: 1fr;
  }

  .brand-row h1 {
    font-size: 28px;
  }
}
</style>
