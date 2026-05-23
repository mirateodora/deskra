<script setup>
defineProps({
  icon: {
    type: String,
    default: "📡",
  },
  label: {
    type: String,
    required: true,
  },
  value: {
    type: [String, Number],
    default: "--",
  },
  status: {
    type: String,
    default: "",
  },
  variant: {
    type: String,
    default: "green",
  },
});
</script>

<template>
  <article class="sensor-card">
    <div class="sensor-icon" :class="variant">
      {{ icon }}
    </div>

    <div class="sensor-content">
      <p>{{ label }}</p>
      <h2>{{ value }}</h2>
      <small v-if="status">{{ status }}</small>
    </div>
  </article>
</template>

<style scoped>
.sensor-card {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 20px;
  border-radius: 24px;
  background: #fffaf3;
  box-shadow: 0 14px 36px rgba(85, 67, 50, 0.11);
  border: 1px solid rgba(120, 88, 56, 0.08);
}

.sensor-icon {
  width: 52px;
  height: 52px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: 18px;
  font-size: 23px;
}

.sensor-icon.warm {
  background: #ffe9d6;
}

.sensor-icon.blue {
  background: #e6f0ff;
}

.sensor-icon.green {
  background: #e4f0ea;
}

.sensor-icon.amber {
  background: #fff0cf;
}

.sensor-icon.red {
  background: #ffe7e1;
}

.sensor-icon.neutral {
  background: #f7efe5;
}

.sensor-content p {
  margin: 0 0 4px;
  color: #8b735f;
  font-size: 14px;
  font-weight: 800;
}

.sensor-content h2 {
  margin: 0;
  font-size: 26px;
  letter-spacing: -0.04em;
  color: #1f2a37;
}

.sensor-content small {
  display: block;
  margin-top: 4px;
  color: #8b735f;
  font-size: 12px;
  font-weight: 700;
}
</style>
