const API_BASE_URL = "http://localhost:5000/api";

async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const config = {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "API request failed");
    }

    return data;
  } catch (error) {
    console.error("API error:", error);
    throw error;
  }
}

export const api = {
  healthCheck() {
    return request("/health");
  },

  getDeviceState() {
    return request("/device/state");
  },

  getLatestSensorData() {
    return request("/device/latest");
  },

  testSocketEmit() {
    return request("/device/emit-test");
  },

  testTimeline() {
    return request("/device/timeline-test");
  },

  testAccessLog() {
    return request("/device/access-log-test");
  },

  testCommandQueue() {
    return request("/device/command-test");
  },

  getPendingCommands() {
    return request("/device/commands/pending");
  },

  consumeCommands() {
    return request("/device/commands");
  },

  manualLogin(credentials) {
  return request("/auth/manual-login", {
    method: "POST",
    body: JSON.stringify(credentials),
  });
  },
  registerUser(userData) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify(userData),
  });
  },
  setFan(state) {
    return request("/device/fan", {
      method: "POST",
      body: JSON.stringify({ state }),
    });
  },

  setLedColor(color) {
    return request("/device/led", {
      method: "POST",
      body: JSON.stringify({ color }),
    });
  },

  setTemperatureThreshold(temperatureThreshold) {
    return request("/settings/temperature-threshold", {
      method: "POST",
      body: JSON.stringify({ temperatureThreshold }),
    });
  },

  getPomodoroState() {
  return request("/pomodoro/state");
  },

  startPomodoro(payload) {
    return request("/pomodoro/start", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  pausePomodoro() {
    return request("/pomodoro/pause", {
      method: "POST",
      body: JSON.stringify({}),
    });
  },

  resumePomodoro() {
    return request("/pomodoro/resume", {
      method: "POST",
      body: JSON.stringify({}),
    });
  },

  stopPomodoro() {
    return request("/pomodoro/stop", {
      method: "POST",
      body: JSON.stringify({}),
    });
  },

  completePomodoro(payload = {}) {
    return request("/pomodoro/complete", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  savePomodoroSession(data) {
  return request("/pomodoro/session-ended", {
    method: "POST",
    body: JSON.stringify(data),
  });
},
};

export default api;
