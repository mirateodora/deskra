<script setup>
import { onMounted } from "vue";
import { useDashboardStore } from "@/stores/dashboardStore";

const dashboardStore = useDashboardStore();

onMounted(() => {
  dashboardStore.fetchInitialState();
});
</script>

<template>
  <router-view />
</template>
