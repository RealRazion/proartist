import { createRouter, createWebHistory } from "vue-router";

const Home = () => import("../views/Home.vue");
const Login = () => import("../views/Login.vue");
const Register = () => import("../views/Register.vue");
const SetPassword = () => import("../views/SetPassword.vue");
const Dashboard = () => import("../views/Dashboard.vue");
const Analytics = () => import("../views/Analytics.vue");
const Profiles = () => import("../views/Profiles.vue");
const Projects = () => import("../views/Projects.vue");
const ProjectDetail = () => import("../views/ProjectDetail.vue");
const Tasks = () => import("../views/Tasks.vue");
const FinishedTasksPage = () => import("../views/FinishedTasksPage.vue");
const Chats = () => import("../views/Chats.vue");
const MyProfile = () => import("../views/MyProfile.vue");
const News = () => import("../views/News.vue");
const ActivityFeed = () => import("../views/ActivityFeed.vue");
const Notifications = () => import("../views/Notifications.vue");
const Admin = () => import("../views/Admin.vue");
const GrowPro = () => import("../views/GrowPro.vue");
const Songs = () => import("../views/Songs.vue");
const Timeline = () => import("../views/Timeline.vue");
const PluginGuides = () => import("../views/PluginGuides.vue");
const ReviewQueue = () => import("../views/ReviewQueue.vue");
const Points = () => import("../views/Points.vue");
const ApiCenter = () => import("../views/ApiCenter.vue");
const PlatformLanding = () => import("../views/PlatformLanding.vue");
const AdminPlatform = () => import("../views/AdminPlatform.vue");
const ContestLanding = () => import("../views/ContestLanding.vue");
const MusicLanding = () => import("../views/MusicLanding.vue");
const LocationsLanding = () => import("../views/LocationsLanding.vue");
const FinanceLanding = () => import("../views/FinanceLanding.vue");
const FinanceTool = () => import("../views/FinanceTool.vue");
const FitnessLanding = () => import("../views/FitnessLanding.vue");
const FitnessTool = () => import("../views/FitnessTool.vue");
const ContentStudio = () => import("../views/ContentStudio.vue");
const ContentScheduleLanding = () => import("../views/ContentScheduleLanding.vue");
const ContentScheduleTool = () => import("../views/ContentScheduleTool.vue");
const SearchView = () => import("../views/SearchView.vue");
const MainLayout = () => import("../layouts/MainLayout.vue");
const PlatformLayout = () => import("../layouts/PlatformLayout.vue");

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
      { path: "tasks/finished", name: "tasks-finished", component: FinishedTasksPage, meta: { requiresAuth: true } },
      { path: "reviews", name: "reviews", component: ReviewQueue, alias: "/reviews", meta: { requiresAuth: true } },
      { path: "timeline", name: "timeline", component: Timeline, alias: "/timeline", meta: { requiresAuth: true } },
      { path: "news", name: "news", component: News, alias: "/news", meta: { requiresAuth: true } },
      { path: "guides", name: "guides", component: PluginGuides, alias: "/guides", meta: { requiresAuth: true } },
      { path: "activity", name: "activity", component: ActivityFeed, alias: "/activity", meta: { requiresAuth: true } },
      { path: "notifications", name: "notifications", component: Notifications, alias: "/notifications", meta: { requiresAuth: true } },
      { path: "admin", name: "admin", component: Admin, alias: "/admin", meta: { requiresAuth: true } },
      { path: "points", name: "points", component: Points, alias: "/points", meta: { requiresAuth: true } },
      { path: "api-center", name: "api-center", component: ApiCenter, alias: "/api-center", meta: { requiresAuth: true } },
      { path: "growpro", name: "growpro", component: GrowPro, alias: "/growpro", meta: { requiresAuth: true } },
      { path: "songs", name: "songs", component: Songs, alias: "/songs", meta: { requiresAuth: true } },
      { path: "team/roles", redirect: { name: "admin" } },
      { path: "chats", name: "chats", component: Chats, alias: "/chats", meta: { requiresAuth: true } },
      { path: "search", name: "search", component: SearchView, alias: "/search", meta: { requiresAuth: true } },
      { path: "me", name: "me", component: MyProfile, alias: "/me", meta: { requiresAuth: true } },
    ],
  },
  {
    path: "/platforms",
    component: PlatformLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "platforms", component: PlatformLanding, meta: { requiresAuth: true } },
      { path: "contests", name: "platform-contests", component: ContestLanding, meta: { requiresAuth: true } },
      { path: "music", name: "platform-music", component: MusicLanding, meta: { requiresAuth: true } },
      { path: "locations", name: "platform-locations", component: LocationsLanding, meta: { requiresAuth: true } },
      { path: "finance", name: "platform-finance", component: FinanceLanding, meta: { requiresAuth: true } },
      { path: "finance/planner/:projectId?", name: "finance", component: FinanceTool, meta: { requiresAuth: true } },
      { path: "content-studio", name: "platform-content-studio", component: ContentStudio, meta: { requiresAuth: true } },
      { path: "content-schedule", name: "platform-content-schedule", component: ContentScheduleLanding, meta: { requiresAuth: true } },
      { path: "content-schedule/planner", name: "content-schedule", component: ContentScheduleTool, meta: { requiresAuth: true } },
      { path: "fitness", name: "platform-fitness", component: FitnessLanding, meta: { requiresAuth: true } },
      { path: "fitness/tracker", name: "fitness", component: FitnessTool, meta: { requiresAuth: true } },
      { path: "admin", name: "admin-platform", component: AdminPlatform, meta: { requiresAuth: true } },
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
    next({ name: "platforms" });
    return;
  }
  next();
});

export default router;
