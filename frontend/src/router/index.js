import { createRouter, createWebHistory } from "vue-router";
import { useToast } from "../composables/useToast";
import {
  fetchManagedPlatformAccessState,
  mapAccessStateRows,
  routeNameToPlatformSlug,
} from "../services/managedPlatforms";

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
const Chats = () => import("../views/Chats.vue");
const MyProfile = () => import("../views/MyProfile.vue");
const ActivityFeed = () => import("../views/ActivityFeed.vue");
const Notifications = () => import("../views/Notifications.vue");
const GrowPro = () => import("../views/GrowPro.vue");
const Songs = () => import("../views/Songs.vue");
const Timeline = () => import("../views/Timeline.vue");
const PluginGuides = () => import("../views/PluginGuides.vue");
const ReviewQueue = () => import("../views/ReviewQueue.vue");
const Points = () => import("../views/Points.vue");
const ApiCenter = () => import("../views/ApiCenter.vue");
const PlatformLanding = () => import("../views/PlatformLanding.vue");
const AdminPlatform = () => import("../views/AdminPlatform.vue");
const UserRoleManagement = () => import("../views/UserRoleManagement.vue");
const TournamentAnimationLab = () => import("../views/TournamentAnimationLab.vue");
const ContestLanding = () => import("../views/ContestLanding.vue");
const TournamentDetail = () => import("../views/TournamentDetail.vue");
const MusicLanding = () => import("../views/MusicLanding.vue");
const LocationsLanding = () => import("../views/LocationsLanding.vue");
const FinanceLanding = () => import("../views/FinanceLanding.vue");
const FinanceTool = () => import("../views/FinanceTool.vue");
const FitnessLanding = () => import("../views/FitnessLanding.vue");
const FitnessTool = () => import("../views/FitnessTool.vue");
const TodoLanding = () => import("../views/TodoLanding.vue");
const ContentStudio = () => import("../views/ContentStudio.vue");
const ContentScheduleLanding = () => import("../views/ContentScheduleLanding.vue");
const ContentScheduleTool = () => import("../views/ContentScheduleTool.vue");
const ManagePlatforms = () => import("../views/ManagePlatforms.vue");
const SearchView = () => import("../views/SearchView.vue");
const Testing = () => import("../views/Testing.vue");
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
      { path: "tasks/finished", redirect: { name: "tasks" } },
      { path: "reviews", name: "reviews", component: ReviewQueue, alias: "/reviews", meta: { requiresAuth: true } },
      { path: "timeline", name: "timeline", component: Timeline, alias: "/timeline", meta: { requiresAuth: true } },
      { path: "activity", name: "activity", component: ActivityFeed, alias: "/activity", meta: { requiresAuth: true } },
      { path: "notifications", name: "notifications", component: Notifications, alias: "/notifications", meta: { requiresAuth: true } },
      { path: "points", name: "points", component: Points, alias: "/points", meta: { requiresAuth: true } },
      { path: "growpro", name: "growpro", component: GrowPro, alias: "/growpro", meta: { requiresAuth: true } },
      { path: "songs", name: "songs", component: Songs, alias: "/songs", meta: { requiresAuth: true } },
      { path: "team/roles", redirect: { name: "profiles" } },
      { path: "chats", name: "chats", component: Chats, alias: "/chats", meta: { requiresAuth: true } },
      { path: "search", name: "search", component: SearchView, alias: "/search", meta: { requiresAuth: true } },
      { path: "me", name: "me", component: MyProfile, alias: "/me", meta: { requiresAuth: true } },
      { path: "testing", name: "testing", component: Testing, alias: "/testing", meta: { requiresAuth: true } },
    ],
  },
  {
    path: "/platforms",
    component: PlatformLayout,
    meta: { requiresAuth: true },
    children: [
      { path: "", name: "platforms", component: PlatformLanding, meta: { requiresAuth: true } },
      {
        path: "contests",
        name: "platform-contests",
        component: ContestLanding,
        meta: { requiresAuth: true, hidePlatformTopbar: true },
      },
      {
        path: "contests/:tournamentId",
        name: "platform-contest-detail",
        component: TournamentDetail,
        meta: { requiresAuth: true, hidePlatformTopbar: true },
      },
      { path: "music", name: "platform-music", component: MusicLanding, meta: { requiresAuth: true } },
      { path: "locations", name: "platform-locations", component: LocationsLanding, meta: { requiresAuth: true } },
      { path: "finance", name: "platform-finance", component: FinanceLanding, meta: { requiresAuth: true } },
      { path: "finance/planner/:projectId?", name: "finance", component: FinanceTool, meta: { requiresAuth: true } },
      { path: "content-studio", name: "platform-content-studio", component: ContentStudio, meta: { requiresAuth: true } },
      { path: "content-schedule", name: "platform-content-schedule", component: ContentScheduleLanding, meta: { requiresAuth: true } },
      { path: "content-schedule/planner", name: "content-schedule", component: ContentScheduleTool, meta: { requiresAuth: true } },
      { path: "plugin-guides", name: "platform-plugin-guides", component: PluginGuides, meta: { requiresAuth: true } },
      { path: "api-center", name: "platform-api-center", component: ApiCenter, meta: { requiresAuth: true } },
      { path: "fitness", name: "platform-fitness", component: FitnessLanding, meta: { requiresAuth: true } },
      { path: "fitness/tracker", name: "fitness", component: FitnessTool, meta: { requiresAuth: true } },
      { path: "todo", name: "platform-todo", component: TodoLanding, meta: { requiresAuth: true } },
      { path: "admin", name: "admin-platform", component: AdminPlatform, meta: { requiresAuth: true } },
      { path: "admin/user-role-management", name: "admin-user-role-management", component: UserRoleManagement, meta: { requiresAuth: true } },
      { path: "admin/tournament-animations", name: "admin-tournament-animations", component: TournamentAnimationLab, meta: { requiresAuth: true } },
      { path: "manage-platforms", name: "manage-platforms", component: ManagePlatforms, meta: { requiresAuth: true } },
    ],
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];

const router = createRouter({ history: createWebHistory(), routes });
const { showToast } = useToast();

router.beforeEach(async (to, from, next) => {
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

  const targetSlug = routeNameToPlatformSlug(to.name);
  if (token && targetSlug) {
    try {
      const rows = await fetchManagedPlatformAccessState();
      const bySlug = mapAccessStateRows(rows);
      const state = bySlug[targetSlug];
      if (state && state.is_accessible === false) {
        showToast(state.status_note || "Diese Plattform ist aktuell nicht verfuegbar.", "warning");
        next({ name: "platforms" });
        return;
      }
    } catch {
      // If access state cannot be loaded, do not hard block navigation.
    }
  }

  next();
});

export default router;
