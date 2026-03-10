<template>
  <div class="layout" :class="{ 'sidebar-collapsed': collapsed && !isMobile }">
    <aside :class="['sidebar', { collapsed: collapsed && !isMobile, 'mobile-open': mobileOpen && isMobile }]">
      <div class="sidebar-top">
        <div class="brand">
          <span class="brand-mark">ProArtist</span>
          <span v-if="isTeam" class="badge">Team</span>
          <span v-else-if="me" class="badge artist">Artist</span>
        </div>
        <button
          class="collapse-toggle"
          type="button"
          @click="toggleSidebar"
          :aria-label="collapsed && !isMobile ? 'Sidebar öffnen' : 'Sidebar schließen'"
        >
          <span v-if="collapsed && !isMobile">»</span>
          <span v-else>«</span>
        </button>
      </div>

      <nav>
        <router-link
          to="/dashboard"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Dashboard' : null"
        >
          <span class="icon">🏠</span>
          <span class="label">Dashboard</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/analytics"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Analytics' : null"
        >
          <span class="icon">📊</span>
          <span class="label">Analytics</span>
        </router-link>
        <router-link
          to="/profiles"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Profiles' : null"
        >
          <span class="icon">🎤</span>
          <span class="label">Profiles</span>
        </router-link>
        <router-link
          to="/chats"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Chats' : null"
        >
          <span class="icon">💬</span>
          <span class="label">Chats</span>
          <small v-if="unreadCount" class="pill">{{ unreadCount }}</small>
        </router-link>
        <router-link
          to="/news"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'News' : null"
        >
          <span class="icon">📰</span>
          <span class="label">News</span>
        </router-link>
        <router-link
          to="/guides"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Guides' : null"
        >
          <span class="icon">🔌</span>
          <span class="label">Plugin Guides</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/projects"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Projekte' : null"
        >
          <span class="icon">📁</span>
          <span class="label">Projekte</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/tasks"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Tasks' : null"
        >
          <span class="icon">🗒️</span>
          <span class="label">Tasks</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/reviews"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Review' : null"
        >
          <span class="icon">✅</span>
          <span class="label">Review</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/timeline"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Timeline' : null"
        >
          <span class="icon">🗓️</span>
          <span class="label">Timeline</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/activity"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Aktivität' : null"
        >
          <span class="icon">🕒</span>
          <span class="label">Aktivität</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/admin"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Admin' : null"
        >
          <span class="icon">⚙</span>
          <span class="label">Admin</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/points"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Points' : null"
        >
          <span class="icon">🧮</span>
          <span class="label">Points</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/api-center"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'API' : null"
        >
          <span class="icon">🔑</span>
          <span class="label">API</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/growpro"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'GrowPro' : null"
        >
          <span class="icon">📈</span>
          <span class="label">GrowPro</span>
        </router-link>
        <router-link
          to="/me"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Mein Profil' : null"
        >
          <span class="icon">👤</span>
          <span class="label">Mein Profil</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">
        <span class="version">v{{ APP_VERSION }}</span>
      </div>
    </aside>

    <div class="main">
      <header class="topbar card topbar-flat">
        <button class="iconbtn mobile-toggle" type="button" @click="toggleSidebar" v-if="isMobile">
          ☰
        </button>
        <div class="search">
          <input
            class="input search-input"
            placeholder="Suche Künstler, Producer oder Projekte…"
            v-model="search"
            @keyup.enter="performSearch"
          />
          <button class="btn ghost tiny search-btn" type="button" @click="performSearch">
            Suchen
          </button>
        </div>
        <div class="right">
          <button class="iconbtn top-icon-btn" type="button" @click="toggleTheme" :title="`Theme: ${themeLabel}`">
            <svg
              v-if="theme === 'dark'"
              class="toolbar-svg"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z" />
            </svg>
            <svg
              v-else
              class="toolbar-svg"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="4.2" />
              <path d="M12 2.5v2.2M12 19.3v2.2M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" />
            </svg>
          </button>
          <button
            class="iconbtn top-icon-btn"
            type="button"
            @click="notify('Request-Ansicht folgt bald')"
            title="Offene Requests"
          >
            <svg class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
              <rect x="3" y="5" width="18" height="14" rx="2.4" />
              <path d="m4.5 7.5 7.5 6 7.5-6" />
            </svg>
            <span v-if="openRequests" class="pill toolbar-pill">{{ openRequests }}</span>
          </button>
          <button class="iconbtn top-icon-btn" type="button" @click="goToChats" title="Chats öffnen">
            <svg class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M20 15a3 3 0 0 1-3 3H9l-5 3v-3a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h13a3 3 0 0 1 3 3z" />
            </svg>
            <span v-if="unreadCount" class="pill toolbar-pill">{{ unreadCount }}</span>
          </button>
          <div class="profile" :class="{ open }">
            <button class="avatar" type="button" @click="open = !open">
              {{ initial }}
            </button>
            <div v-if="open" class="menu card">
              <p class="menu-name">{{ me?.name || me?.username }}</p>
              <p class="menu-item" @click="goToProfile">Profil</p>
              <p class="menu-item" @click="notify('Einstellungen folgen bald')">Einstellungen</p>
              <p class="menu-item danger" @click="logout">Logout</p>
            </div>
          </div>
        </div>
      </header>

      <section class="page-toolbar card">
        <div class="page-heading">
          <p class="page-kicker">{{ pageKicker }}</p>
          <h1>{{ pageTitle }}</h1>
        </div>
        <div class="page-actions">
          <button class="btn ghost tiny" type="button" @click="refreshCurrentPage">
            Neu laden
          </button>
          <button class="btn tiny" type="button" @click="runSecondaryAction">
            {{ secondaryAction.label }}
          </button>
        </div>
      </section>

      <main class="content compact-content">
        <router-view :key="routerViewKey" />
      </main>
    </div>

    <div class="sidebar-overlay" v-if="mobileOpen && isMobile" @click="toggleSidebar"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import { APP_VERSION } from "../config/version";

const router = useRouter();
const route = useRoute();

const { profile: me, isTeam, fetchProfile, clearProfile } = useCurrentProfile();

const open = ref(false);
const search = ref("");
const unreadCount = ref(0);
const theme = ref("light");
const loadingUnread = ref(false);
const collapsed = ref(false);
const mobileOpen = ref(false);
const isMobile = ref(false);
const openRequests = ref(0);
const { showToast } = useToast();
const viewRefreshKey = ref(0);

let unreadInterval = null;

const pageMeta = {
  dashboard: { title: "Dashboard", team: "Teamsteuerung auf einen Blick", artist: "Dein zentraler Startpunkt" },
  analytics: { title: "Analytics", team: "Performance und Kennzahlen", artist: "Analyse" },
  profiles: { title: "Profiles", team: "Personen und Rollen", artist: "Netzwerkprofile" },
  chats: { title: "Chats", team: "Direkte Abstimmung im Team", artist: "Direkter Austausch" },
  news: { title: "News", team: "Updates fuer alle Beteiligten", artist: "Aktuelle Team-News" },
  guides: { title: "Plugin Guides", team: "Wissen und Workflows", artist: "Guides und Tipps" },
  projects: { title: "Projekte", team: "Projektplanung und Steuerung", artist: "Deine Projektuebersicht" },
  "project-detail": { title: "Projekt Details", team: "Task- und Projektfokus", artist: "Projektfokus" },
  tasks: { title: "Tasks", team: "Aufgabenmanagement", artist: "Tasks" },
  reviews: { title: "Review Queue", team: "Freigaben und Qualitaetssicherung", artist: "Reviews" },
  timeline: { title: "Timeline", team: "Fristen und Deadlines", artist: "Timeline" },
  activity: { title: "Aktivitaet", team: "Letzte Team-Ereignisse", artist: "Aktivitaetsfeed" },
  admin: { title: "Admin", team: "Benutzer und Systemverwaltung", artist: "Admin" },
  points: { title: "Points", team: "Workload und Scoring", artist: "Points" },
  "api-center": { title: "API Center", team: "Automationen und Integrationen", artist: "API Center" },
  growpro: { title: "GrowPro", team: "Ziele und Fortschritt", artist: "Wachstumsziele" },
  songs: { title: "Songs", team: "Versionen und Releases", artist: "Songs" },
  me: { title: "Mein Profil", team: "Persoenliche Einstellungen", artist: "Persoenliche Einstellungen" },
};

const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});

const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));
const pageMetaCurrent = computed(() => pageMeta[route.name] || { title: "ProArtist", team: "Arbeitsbereich", artist: "Arbeitsbereich" });
const pageTitle = computed(() => pageMetaCurrent.value.title);
const pageKicker = computed(() => (isTeam.value ? pageMetaCurrent.value.team : pageMetaCurrent.value.artist));
const routerViewKey = computed(() => `${route.fullPath}::${viewRefreshKey.value}`);
const secondaryAction = computed(() => {
  if (route.name === "dashboard") {
    return isTeam.value
      ? { label: "Zu Tasks", to: { name: "tasks" } }
      : { label: "Zu Projekten", to: { name: "projects" } };
  }
  if (route.name === "tasks") return { label: "Zur Review Queue", to: { name: "reviews" } };
  if (route.name === "reviews") return { label: "Zur Timeline", to: { name: "timeline" } };
  if (route.name === "project-detail") return { label: "Zu Projekten", to: { name: "projects" } };
  if (route.name === "growpro" && isTeam.value) return { label: "Zu Points", to: { name: "points" } };
  if (route.name === "admin") return { label: "Zu Analytics", to: { name: "analytics" } };
  if (route.name === "api-center") return { label: "Zu Admin", to: { name: "admin" } };
  return { label: "Zum Dashboard", to: { name: "dashboard" } };
});

function notify(msg) {
  showToast(msg);
}

function applyTheme() {
  const root = document.documentElement;
  const isDark = theme.value === "dark";
  root.classList.toggle("dark", isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
  applyTheme();
}

function goToChats() {
  router.push({ name: "chats" });
}

function goToProfile() {
  router.push({ name: "me" });
  open.value = false;
}

function refreshCurrentPage() {
  viewRefreshKey.value += 1;
}

function runSecondaryAction() {
  const target = secondaryAction.value?.to;
  if (!target) return;
  router.push(target);
}

function logout() {
  localStorage.removeItem("access");
  localStorage.removeItem("refresh");
  clearProfile();
  router.replace({ name: "login" });
}

async function loadUnread() {
  if (loadingUnread.value) return;
  loadingUnread.value = true;
  try {
    const { data } = await api.get("threads/");
    const messages = data.flatMap((thread) => thread.messages || []);
    const myId = me.value?.id;
    unreadCount.value = messages.filter((m) => !m.read && m.sender !== myId).length;
  } catch (err) {
    console.error("Konnte Threads nicht laden", err);
  } finally {
    loadingUnread.value = false;
  }
}

function performSearch() {
  const term = search.value.trim();
  if (!term) {
    notify("Bitte einen Suchbegriff eingeben");
    return;
  }
  router.push({ name: "profiles", query: { q: term } });
}

async function loadStats() {
  try {
    const { data } = await api.get("stats/");
    openRequests.value = data?.open_requests || 0;
  } catch (err) {
    console.error("Konnte Stats nicht laden", err);
  }
}

function updateViewport() {
  if (typeof window === "undefined") return;
  isMobile.value = window.innerWidth < 900;
  if (isMobile.value) {
    collapsed.value = false;
  }
  if (!isMobile.value) {
    mobileOpen.value = false;
    if (typeof document !== "undefined") {
      document.body.style.overflow = "";
    }
  }
}

function toggleSidebar() {
  if (isMobile.value) {
    mobileOpen.value = !mobileOpen.value;
    if (typeof document !== "undefined") {
      document.body.style.overflow = mobileOpen.value ? "hidden" : "";
    }
  } else {
    collapsed.value = !collapsed.value;
    localStorage.setItem("layout:sidebar", collapsed.value ? "collapsed" : "expanded");
  }
}

function handleNavClick() {
  if (isMobile.value) {
    mobileOpen.value = false;
    if (typeof document !== "undefined") {
      document.body.style.overflow = "";
    }
  }
}

watch(
  () => route.fullPath,
  () => {
    open.value = false;
    if (isMobile.value) {
      mobileOpen.value = false;
      if (typeof document !== "undefined") {
        document.body.style.overflow = "";
      }
    }
  }
);

onMounted(async () => {
  if (typeof window !== "undefined") {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme) theme.value = storedTheme;
    collapsed.value = localStorage.getItem("layout:sidebar") === "collapsed";
  }
  applyTheme();
  updateViewport();
  if (typeof window !== "undefined") {
    window.addEventListener("resize", updateViewport);
  }
  try {
    await fetchProfile();
  } catch (err) {
    if (err?.response?.status === 401) {
      logout();
      return;
    }
  }
  await loadStats();
  await loadUnread();
  unreadInterval = setInterval(loadUnread, 15000);
});

onBeforeUnmount(() => {
  if (unreadInterval) clearInterval(unreadInterval);
  if (typeof window !== "undefined") {
    window.removeEventListener("resize", updateViewport);
  }
  if (typeof document !== "undefined") {
    document.body.style.overflow = "";
  }
});
</script>

<style scoped>
.search {
  display: flex;
  align-items: center;
  gap: 8px;
}
.search-input {
  flex: 1;
}
.search-btn {
  white-space: nowrap;
}
.page-toolbar {
  margin: 12px 20px 0;
  padding: 12px 14px;
  border-radius: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  background: linear-gradient(100deg, rgba(47, 99, 255, 0.12), rgba(6, 182, 212, 0.08));
}
.page-heading {
  min-width: 0;
}
.page-kicker {
  margin: 0;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand);
}
.page-heading h1 {
  margin: 2px 0 0;
  font-size: clamp(20px, 2.4vw, 26px);
  line-height: 1.1;
}
.page-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.top-icon-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  justify-content: center;
  position: relative;
  border-radius: 12px;
}
.toolbar-svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.8;
  stroke-linecap: round;
  stroke-linejoin: round;
}
.toolbar-pill {
  position: absolute;
  top: -6px;
  right: -6px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  font-size: 11px;
  line-height: 18px;
}
@media (max-width: 900px) {
  .page-toolbar {
    margin: 10px 16px 0;
  }
}
@media (max-width: 720px) {
  .page-toolbar {
    margin: 8px 16px 0;
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  .page-actions {
    justify-content: stretch;
  }
  .page-actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
