import { createRouter, createWebHistory } from "vue-router";
import DashboardPage from "./pages/DashboardPage.vue";
import ChatPage from "./pages/ChatPage.vue";

const routes = [
  { path: "/", redirect: "/dashboard" },
  { path: "/dashboard", component: DashboardPage },
  { path: "/chat", component: ChatPage }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;