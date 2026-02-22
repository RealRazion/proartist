import { createRouter, createWebHistory } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Register from "../views/Register.vue";
import SetPassword from "../views/SetPassword.vue";
import Dashboard from "../views/Dashboard.vue";
import Analytics from "../views/Analytics.vue";
import Profiles from "../views/Profiles.vue";
import Projects from "../views/Projects.vue";
import ProjectDetail from "../views/ProjectDetail.vue";
import Tasks from "../views/Tasks.vue";
import Chats from "../views/Chats.vue";
import MyProfile from "../views/MyProfile.vue";
import News from "../views/News.vue";
import ActivityFeed from "../views/ActivityFeed.vue";
import Admin from "../views/Admin.vue";
import GrowPro from "../views/GrowPro.vue";
import Songs from "../views/Songs.vue";
import Timeline from "../views/Timeline.vue";
import PluginGuides from "../views/PluginGuides.vue";
import ReviewQueue from "../views/ReviewQueue.vue";
import Points from "../views/Points.vue";
import ApiCenter from "../views/ApiCenter.vue";
import MainLayout from "../layouts/MainLayout.vue";

const routes = [
  { path: "/", name: "home", component: Home, meta: { guestOnly: true } },
  { path: "/login", name: "login", component: Login, meta: { guestOnly: true } },
  { path: "/register", name: "register", component: Register, meta: { guestOnly: true } },
  { path: "/set-password", name: "set-password", component: SetPassword, meta: { guestOnly: true } },
  {
    path: "/app",
    component: MainLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "", redirect: { name: "dashboard" } },
      { path: "dashboard", name: "dashboard", component: Dashboard, alias: "/dashboard", meta: { requiresAuth: true } },
      { path: "analytics", name: "analytics", component: Analytics, alias: "/analytics", meta: { requiresAuth: true } },
      { path: "profiles", name: "profiles", component: Profiles, alias: "/profiles", meta: { requiresAuth: true } },
      { path: "projects", name: "projects", component: Projects, alias: "/projects", meta: { requiresAuth: true } },
      {
        path: "projects/:projectId",
        name: "project-detail",
        component: ProjectDetail,
        alias: "/projects/:projectId",
        meta: { requiresAuth: true },
      },
      { path: "tasks", name: "tasks", component: Tasks, alias: "/tasks", meta: { requiresAuth: true } },
      { path: "reviews", name: "reviews", component: ReviewQueue, alias: "/reviews", meta: { requiresAuth: true } },
      { path: "timeline", name: "timeline", component: Timeline, alias: "/timeline", meta: { requiresAuth: true } },
      { path: "news", name: "news", component: News, alias: "/news", meta: { requiresAuth: true } },
      { path: "guides", name: "guides", component: PluginGuides, alias: "/guides", meta: { requiresAuth: true } },
      { path: "activity", name: "activity", component: ActivityFeed, alias: "/activity", meta: { requiresAuth: true } },
      { path: "admin", name: "admin", component: Admin, alias: "/admin", meta: { requiresAuth: true } },
      { path: "points", name: "points", component: Points, alias: "/points", meta: { requiresAuth: true } },
      { path: "api-center", name: "api-center", component: ApiCenter, alias: "/api-center", meta: { requiresAuth: true } },
      { path: "growpro", name: "growpro", component: GrowPro, alias: "/growpro", meta: { requiresAuth: true } },
      { path: "songs", name: "songs", component: Songs, alias: "/songs", meta: { requiresAuth: true } },
      { path: "team/roles", redirect: { name: "admin" } },
      { path: "chats", name: "chats", component: Chats, alias: "/chats", meta: { requiresAuth: true } },
      { path: "me", name: "me", component: MyProfile, alias: "/me", meta: { requiresAuth: true } },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({ history: createWebHistory(), routes });

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("access");
  const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth);
  const guestOnly = to.matched.some((record) => record.meta?.guestOnly);

  if (requiresAuth && !token) {
    next({ name: "login", query: { redirect: to.fullPath } });
    return;
  }
  if (guestOnly && token) {
    next({ name: "dashboard" });
    return;
  }
  next();
});

export default router;
