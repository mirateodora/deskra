<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";
import { useDashboardStore } from "@/stores/dashboardStore";

const router = useRouter();
const dashboardStore = useDashboardStore();

const backendStatus = computed(() => {
  return dashboardStore.socketConnected ? "Connected" : "Disconnected";
});

const deviceStatus = computed(() => {
  return dashboardStore.device.connected
    ? "Device online"
    : dashboardStore.device.mode === "simulator"
      ? "Simulator mode"
      : "Device offline";
});

function goToLogin() {
  router.push("/login");
}

function goToRegister() {
  router.push("/register");
}

function checkCamera() {
  alert("Camera check placeholder. Later this will open ESP32-CAM preview/status.");
}

function continueAsGuest() {
  router.push("/dashboard");
}
</script>

<template>
  <main class="locked-page">
    <section class="locked-shell">
      <div class="brand">
        <div class="logo-badge">
          <span>☕</span>
        </div>

        <div>
          <h1>Deskra</h1>
          <p>Your smart focus desk companion</p>
        </div>
      </div>

      <section class="hero-card">
        <div class="illustration-card">
          <div class="sun"></div>

          <div class="desk-scene">
            <div class="lamp">
              <div class="lamp-head"></div>
              <div class="lamp-arm"></div>
              <div class="lamp-base"></div>
            </div>

            <div class="monitor">
              <div class="monitor-screen">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div class="monitor-stand"></div>
            </div>

            <div class="plant">
              <div class="leaf leaf-one"></div>
              <div class="leaf leaf-two"></div>
              <div class="pot"></div>
            </div>
          </div>
        </div>

        <div class="content-card">
          <div class="lock-icon">🔒</div>

          <p class="eyebrow">Workspace locked</p>

          <h2>Waiting for Face ID...</h2>

          <p class="description">
            Take a seat at your desk and Deskra will unlock your productivity dashboard
            automatically when your face is recognized.
          </p>

          <div class="status-grid">
            <div class="status-pill">
              <span
                class="dot"
                :class="{ online: dashboardStore.socketConnected }"
              ></span>
              Backend: {{ backendStatus }}
            </div>

            <div class="status-pill">
              <span
                class="dot"
                :class="{ online: dashboardStore.device.connected }"
              ></span>
              {{ deviceStatus }}
            </div>

            <div class="status-pill">
              <span class="dot waiting"></span>
              Face ID: Waiting
            </div>
          </div>

          <div class="actions">
            <button class="primary-btn" @click="goToLogin">
              Manual Login
            </button>

            <button class="secondary-btn" @click="goToRegister">
              Register
            </button>
          </div>

          <button class="camera-btn" @click="checkCamera">
            Check Camera
          </button>

          <button class="guest-btn" @click="continueAsGuest">
            Continue as Guest
          </button>
        </div>
      </section>
    </section>
  </main>
</template>

<style scoped>
.locked-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  background:
    radial-gradient(circle at top left, rgba(255, 204, 128, 0.35), transparent 32%),
    radial-gradient(circle at bottom right, rgba(95, 158, 160, 0.22), transparent 34%),
    linear-gradient(135deg, #f8efe3 0%, #f3e7d5 45%, #e9dfd2 100%);
  color: #24313f;
}

.locked-shell {
  width: min(1080px, 100%);
}

.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 24px;
}

.logo-badge {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  background: #fff8ee;
  box-shadow: 0 14px 40px rgba(75, 60, 45, 0.12);
  font-size: 24px;
}

.brand h1 {
  margin: 0;
  font-size: 34px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.brand p {
  margin: 4px 0 0;
  color: #6c5f53;
  font-size: 15px;
}

.hero-card {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 22px;
  padding: 22px;
  border-radius: 36px;
  background: rgba(255, 250, 242, 0.72);
  backdrop-filter: blur(16px);
  box-shadow: 0 24px 80px rgba(85, 67, 50, 0.16);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.illustration-card,
.content-card {
  min-height: 520px;
  border-radius: 28px;
}

.illustration-card {
  position: relative;
  overflow: hidden;
  background:
    linear-gradient(160deg, rgba(31, 42, 55, 0.96), rgba(57, 72, 87, 0.94)),
    #253140;
}

.sun {
  position: absolute;
  top: 58px;
  right: 72px;
  width: 86px;
  height: 86px;
  border-radius: 50%;
  background: #f8c471;
  box-shadow: 0 0 80px rgba(248, 196, 113, 0.65);
}

.desk-scene {
  position: absolute;
  left: 50%;
  bottom: 68px;
  width: 76%;
  height: 260px;
  transform: translateX(-50%);
  border-bottom: 18px solid #d8a96d;
}

.monitor {
  position: absolute;
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
}

.monitor-screen {
  width: 210px;
  height: 140px;
  border-radius: 18px;
  background: #101827;
  border: 10px solid #fff4df;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.28);
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
}

.monitor-screen span {
  height: 12px;
  border-radius: 999px;
  background: #79d8b2;
}

.monitor-screen span:nth-child(2) {
  width: 70%;
  background: #f8c471;
}

.monitor-screen span:nth-child(3) {
  width: 46%;
  background: #8fb5ff;
}

.monitor-stand {
  width: 70px;
  height: 52px;
  margin: 0 auto;
  background: #fff4df;
  clip-path: polygon(35% 0, 65% 0, 82% 100%, 18% 100%);
}

.lamp {
  position: absolute;
  left: 16px;
  bottom: 18px;
}

.lamp-head {
  width: 76px;
  height: 42px;
  border-radius: 42px 42px 12px 12px;
  background: #f8c471;
  transform: rotate(-20deg);
}

.lamp-arm {
  width: 12px;
  height: 118px;
  background: #fff4df;
  margin-left: 44px;
  transform: rotate(16deg);
  transform-origin: top;
  border-radius: 999px;
}

.lamp-base {
  width: 84px;
  height: 18px;
  border-radius: 999px;
  background: #fff4df;
}

.plant {
  position: absolute;
  right: 20px;
  bottom: 18px;
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

.content-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 44px;
  background: #fffaf3;
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.lock-icon {
  width: 64px;
  height: 64px;
  display: grid;
  place-items: center;
  border-radius: 22px;
  background: #f5eadb;
  font-size: 28px;
  margin-bottom: 22px;
}

.eyebrow {
  margin: 0 0 8px;
  color: #5f9e86;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
}

.content-card h2 {
  margin: 0;
  font-size: 42px;
  line-height: 1.05;
  letter-spacing: -0.05em;
  color: #1f2a37;
}

.description {
  margin: 20px 0 30px;
  color: #6c5f53;
  font-size: 18px;
  line-height: 1.8;
}

.status-grid {
  display: grid;
  gap: 10px;
  margin-bottom: 28px;
}

.status-pill {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 14px;
  border-radius: 16px;
  background: #f7efe5;
  color: #4c423a;
  font-size: 14px;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #d66b5d;
  box-shadow: 0 0 0 4px rgba(214, 107, 93, 0.12);
}

.dot.online {
  background: #65b891;
  box-shadow: 0 0 0 4px rgba(101, 184, 145, 0.16);
}

.dot.waiting {
  background: #f0b35e;
  box-shadow: 0 0 0 4px rgba(240, 179, 94, 0.16);
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

button {
  border: none;
  cursor: pointer;
  font-family: inherit;
  font-weight: 700;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

button:hover {
  transform: translateY(-2px);
}

.primary-btn,
.secondary-btn {
  padding: 17px 20px;
  border-radius: 16px;
  font-size: 17px;
}

.primary-btn {
  color: #fffaf3;
  background: #2f6f5e;
  box-shadow: 0 14px 30px rgba(47, 111, 94, 0.25);
}

.secondary-btn {
  color: #2f6f5e;
  background: #e4f0ea;
}

.camera-btn {
  margin-top: 14px;
  padding: 14px;
  border-radius: 16px;
  background: #f7efe5;
  color: #2f6f5e;
  font-size: 16px;
}

.camera-btn:hover {
  box-shadow: 0 12px 26px rgba(47, 111, 94, 0.12);
}

.guest-btn {
  margin-top: 16px;
  padding: 14px;
  background: transparent;
  color: #8b735f;
  font-size: 16px;
}
.guest-btn:hover {
  color: #2f6f5e;
  box-shadow: none;
}

@media (max-width: 860px) {
  .locked-page {
    padding: 18px;
    align-items: flex-start;
  }

  .hero-card {
    grid-template-columns: 1fr;
  }

  .illustration-card {
    min-height: 300px;
  }

  .content-card {
    min-height: auto;
    padding: 30px;
  }

  .content-card h2 {
    font-size: 34px;
  }
}

@media (max-width: 520px) {
  .actions {
    grid-template-columns: 1fr;
  }

  .brand h1 {
    font-size: 28px;
  }

  .hero-card {
    padding: 14px;
    border-radius: 26px;
  }

  .illustration-card,
  .content-card {
    border-radius: 22px;
  }
}
</style>
