<template>
  <div class="layout" :class="{ 'sidebar-collapsed': collapsed && !isMobile }">
    <aside :class="['sidebar', { collapsed: collapsed && !isMobile, 'mobile-open': mobileOpen && isMobile }]">
      <div class="sidebar-top">
        <div class="brand">
          <span class="brand-mark">ProArtist</span>
          <span v-if="isTeam" class="badge">Team</span>
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
          <span class="icon">N</span>
          <span class="label">News</span>
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
          <button class="iconbtn" type="button" @click="toggleTheme" :title="`Theme: ${themeLabel}`">
            {{ themeIcon }}
          </button>
          <button class="iconbtn" type="button" @click="notify('Request-Ansicht folgt bald')" title="Offene Requests">
            📨
            <span v-if="openRequests" class="pill">{{ openRequests }}</span>
          </button>
          <button class="iconbtn" type="button" @click="goToChats" title="Chats öffnen">
            💬
            <span v-if="unreadCount" class="pill">{{ unreadCount }}</span>
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

      <main class="content">
        <router-view />
      </main>
    </div>

    <div class="toast-wrap">
      <div v-for="toast in toasts" :key="toast.id" class="toast">
        {{ toast.msg }}
      </div>
    </div>

    <div class="sidebar-overlay" v-if="mobileOpen && isMobile" @click="toggleSidebar"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const route = useRoute();

const { profile: me, isTeam, fetchProfile, clearProfile } = useCurrentProfile();

const open = ref(false);
const search = ref("");
const unreadCount = ref(0);
const toasts = ref([]);
const theme = ref("light");
const loadingUnread = ref(false);
const collapsed = ref(false);
const mobileOpen = ref(false);
const isMobile = ref(false);
const openRequests = ref(0);

let unreadInterval = null;

const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});

const themeIcon = computed(() => (theme.value === "dark" ? "🌙" : "☀️"));
const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));

function notify(msg) {
  const id = Date.now();
  toasts.value.push({ id, msg });
  setTimeout(() => {
    toasts.value = toasts.value.filter((t) => t.id !== id);
  }, 2500);
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
</style>
