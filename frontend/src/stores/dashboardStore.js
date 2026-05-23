import { defineStore } from "pinia";
import api from "@/services/api";

export const useDashboardStore = defineStore("dashboard", {
  state: () => ({
    loading: false,
    error: null,

    socketConnected: false,

    device: {
      id: "deskra-esp32-001",
      connected: false,
      mode: "simulator",
      lastUpdate: null,
    },

    sensors: {
      temperature: null,
      humidity: null,
      presence: false,
      lastUpdate: null,
    },

    actuators: {
      fan: false,
      ledColor: "#ff0000",
    },

    auth: {
      locked: true,
      currentUser: null,
      loginMethod: null,
    },

    pomodoro: {
      running: false,
      mode: "idle",
      remainingSeconds: 25 * 60,
      focusMinutes: 25,
      breakMinutes: 5,
      selectedTask: null,
      startedAt: null,
      endedAt: null,
      deskAbsenceCount: 0,
    },

    settings: {
      temperatureThreshold: 26,
      defaultFocusMinutes: 25,
      defaultBreakMinutes: 5,
      defaultLedColor: "#ff0000",
      musicEnabled: false,
    },

    timeline: [],
    accessLogs: [],
    tasks: [],
    commands: [],
    showPomodoroEndModal: false,
  }),

  getters: {
    isLocked: (state) => state.auth.locked,

    currentUserName: (state) => {
      return state.auth.currentUser?.name || "Guest";
    },

    formattedRemainingTime: (state) => {
      const totalSeconds = state.pomodoro.remainingSeconds || 0;
      const minutes = Math.floor(totalSeconds / 60);
      const seconds = totalSeconds % 60;

      return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
    },
  },

  actions: {
    async fetchInitialState() {
      this.loading = true;
      this.error = null;

      try {
        const state = await api.getDeviceState();
        this.applyFullState(state);
      } catch (error) {
        this.error = error.message || "Failed to fetch device state";
      } finally {
        this.loading = false;
      }
    },

    applyFullState(state) {
      if (!state) return;

      this.device = state.device ?? this.device;
      this.sensors = state.sensors ?? this.sensors;
      this.actuators = state.actuators ?? this.actuators;
      this.auth = state.auth ?? this.auth;
      this.pomodoro = state.pomodoro ?? this.pomodoro;
      this.settings = state.settings ?? this.settings;
      this.timeline = state.timeline ?? this.timeline;
      this.accessLogs = state.accessLogs ?? this.accessLogs;
      this.tasks = state.tasks ?? this.tasks;
      this.commands = state.commands ?? this.commands;
    },

    applySensorUpdate(sensorData) {
      this.sensors = {
        ...this.sensors,
        ...sensorData,
      };
    },

    applyActuatorUpdate(actuatorData) {
      this.actuators = {
        ...this.actuators,
        ...actuatorData,
      };
    },

    applyAuthUpdate(authData) {
      this.auth = {
        ...this.auth,
        ...authData,
      };
    },

    applyPomodoroUpdate(pomodoroData) {
      this.pomodoro = {
        ...this.pomodoro,
        ...pomodoroData,
      };
    },

    applySettingsUpdate(settingsData) {
      this.settings = {
        ...this.settings,
        ...settingsData,
      };
    },

    addTimelineEvent(event) {
      if (!event) return;
      this.timeline.unshift(event);
    },

    addAccessLog(log) {
      if (!log) return;
      this.accessLogs.unshift(log);
    },

    setSocketConnected(status) {
      this.socketConnected = status;
    },

    setPomodoroEndModal(status) {
      this.showPomodoroEndModal = status;
    },

    setTasks(tasks) {
      this.tasks = tasks || [];
    },

    addOrUpdateTask(task) {
      if (!task) return;

      const index = this.tasks.findIndex((item) => item.id === task.id);

      if (index === -1) {
        this.tasks.unshift(task);
      } else {
        this.tasks[index] = task;
      }
    },

    removeTask(taskId) {
      this.tasks = this.tasks.filter((task) => task.id !== taskId);
    },
  },
});
