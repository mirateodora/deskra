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

<style>
* {
  box-sizing: border-box;
}

html,
body,
#app {
  width: 100%;
  min-height: 100vh;
  margin: 0;
  padding: 0;
}


button,
input,
select,
textarea {
  font: inherit;
}
</style>
