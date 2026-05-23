import { createRouter, createWebHistory } from "vue-router";

import LockedView from "@/views/LockedView.vue";
import LoginView from "@/views/LoginView.vue";
import RegisterView from "@/views/RegisterView.vue";
import DashboardView from "@/views/DashboardView.vue";
import SimulatorView from "@/views/SimulatorView.vue";
import SettingsView from "@/views/SettingsView.vue";
import AccessLogsView from "@/views/AccessLogsView.vue";
import AnalyticsView from "@/views/AnalyticsView.vue";

const routes = [
  {
    path: "/",
    name: "locked",
    component: LockedView,
  },
  {
    path: "/login",
    name: "login",
    component: LoginView,
  },
  {
    path: "/register",
    name: "register",
    component: RegisterView,
  },
  {
    path: "/dashboard",
    name: "dashboard",
    component: DashboardView,
  },
  {
    path: "/simulator",
    name: "simulator",
    component: SimulatorView,
  },
  {
    path: "/settings",
    name: "settings",
    component: SettingsView,
  },
  {
    path: "/access-logs",
    name: "access-logs",
    component: AccessLogsView,
  },
  {
    path: "/analytics",
    name: "analytics",
    component: AnalyticsView,
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
