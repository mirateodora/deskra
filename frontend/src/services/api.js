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
};

export default api;
