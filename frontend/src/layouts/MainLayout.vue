<template>
  <div class="layout" :class="{ 'sidebar-collapsed': collapsed && !isMobile }">
    <aside :class="['sidebar', { collapsed: collapsed && !isMobile, 'mobile-open': mobileOpen && isMobile }]">
      <div class="sidebar-top">
        <div class="brand">
          <span class="brand-mark">UNYQ</span>
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
          to="/platforms"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Hub' : null"
        >
          <span class="icon">🧭</span>
          <span class="label">Hub</span>
        </router-link>
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
          to="/notifications"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Benachrichtigungen' : null"
        >
          <span class="icon">🔔</span>
          <span class="label">Notifications</span>
          <small v-if="notificationCount" class="pill">{{ notificationCount }}</small>
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
            @click="router.push({ name: 'notifications' })"
            title="Benachrichtigungen"
          >
            <svg class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M6 8a6 6 0 1 1 12 0v4.5l1.7 2.6A1 1 0 0 1 18.9 17H5.1a1 1 0 0 1-.8-1.9L6 12.5z" />
              <path d="M10 19a2 2 0 0 0 4 0" />
            </svg>
            <span v-if="notificationCount" class="pill toolbar-pill">{{ notificationCount }}</span>
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
          <div class="chat-dropdown">
            <button class="iconbtn top-icon-btn" type="button" @click.stop="toggleChatMenu" title="Chats öffnen">
              <svg class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M20 15a3 3 0 0 1-3 3H9l-5 3v-3a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3h13a3 3 0 0 1 3 3z" />
              </svg>
              <span v-if="unreadCount" class="pill toolbar-pill">{{ unreadCount }}</span>
            </button>
            <div v-if="chatOpen" class="chat-menu card">
              <div class="chat-menu-head">
                <strong>Chat starten</strong>
                <button class="btn ghost tiny" type="button" @click="openAllChats">Alle Chats</button>
              </div>
              <div v-if="chatLoading" class="muted small">Lade Kontakte...</div>
              <div v-else>
                <button
                  v-for="profile in chatContacts"
                  :key="profile.id"
                  class="menu-item"
                  type="button"
                  @click="openChatWith(profile.id)"
                >
                  {{ profile.name || profile.username }}
                </button>
                <p v-if="!chatContacts.length && !chatLoading" class="muted small">Keine Chat-Kontakte gefunden.</p>
              </div>
              <p v-if="chatError" class="muted danger small">{{ chatError }}</p>
            </div>
          </div>
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
const notificationCount = ref(0);
const theme = ref("light");
const loadingUnread = ref(false);
const collapsed = ref(false);
const mobileOpen = ref(false);
const isMobile = ref(false);
const openRequests = ref(0);
const chatOpen = ref(false);
const chatContacts = ref([]);
const chatLoading = ref(false);
const chatError = ref(null);
const { showToast } = useToast();
const viewRefreshKey = ref(0);

let unreadInterval = null;
let notificationInterval = null;

const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});

const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));
const routerViewKey = computed(() => `${route.fullPath}::${viewRefreshKey.value}`);
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

function toggleChatMenu() {
  chatOpen.value = !chatOpen.value;
  if (chatOpen.value && !chatContacts.value.length) {
    loadChatContacts();
  }
}

function openAllChats() {
  chatOpen.value = false;
  router.push({ name: "chats" });
}

async function openChatWith(profileId) {
  chatOpen.value = false;
  try {
    const { data } = await api.post("threads/ensure/", { profile_id: profileId });
    router.push({ name: "chats", query: { thread: data.id } });
  } catch (err) {
    console.error("Chat konnte nicht geöffnet werden", err);
    showToast("Chat konnte nicht geöffnet werden", "error");
  }
}

async function loadChatContacts() {
  chatLoading.value = true;
  chatError.value = null;
  try {
    const { data } = await api.get("profiles/", { params: { page_size: 100, ordering: "name" } });
    const payload = Array.isArray(data) ? data : data.results || [];
    chatContacts.value = payload.filter((profile) => profile.id !== me.value?.id).slice(0, 10);
  } catch (err) {
    console.error("Chat-Kontakte konnten nicht geladen werden", err);
    chatError.value = "Chat-Kontakte konnten nicht geladen werden";
  } finally {
    chatLoading.value = false;
  }
}

function goToProfile() {
  router.push({ name: "me" });
  open.value = false;
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

async function loadNotificationCount() {
  try {
    const { data } = await api.get("notifications/unread-count/");
    notificationCount.value = data?.unread || 0;
  } catch (err) {
    console.error("Konnte Notification-Count nicht laden", err);
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
  await loadNotificationCount();
  unreadInterval = setInterval(loadUnread, 15000);
  notificationInterval = setInterval(loadNotificationCount, 15000);
});

onBeforeUnmount(() => {
  if (unreadInterval) clearInterval(unreadInterval);
  if (notificationInterval) clearInterval(notificationInterval);
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
.chat-dropdown {
  position: relative;
}
.chat-menu {
  position: absolute;
  right: 0;
  top: 48px;
  min-width: 240px;
  z-index: 20;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 12px;
}
.chat-menu-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.chat-menu .menu-item {
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  color: inherit;
  padding: 10px 12px;
  border-radius: 12px;
  cursor: pointer;
}
.chat-menu .menu-item:hover {
  background: rgba(15, 23, 42, 0.05);
}</style>
