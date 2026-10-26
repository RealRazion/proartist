<template>
  <div class="layout" :class="{ 'sidebar-collapsed': collapsed && !isMobile }">
    <aside :class="['sidebar', { collapsed: collapsed && !isMobile, 'mobile-open': mobileOpen && isMobile }]">
      <div class="sidebar-top">
        <div class="brand">
          <span class="brand-mark">UNYQ</span>
          <span class="brand-sub" v-if="!collapsed || isMobile">PROARTIST</span>
          <span v-if="isTeam" class="badge">Team</span>
          <span v-else-if="me" class="badge artist" title="Voller UNYQ Artist Zugang">UNYQ</span>
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
        <!-- SECTION 1: STUDIO -->
        <div class="nav-section-title" v-if="!collapsed || isMobile">
          <span>STUDIO</span>
        </div>
        <router-link
          to="/dashboard"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Studio Dashboard' : null"
        >
          <span class="icon">🏠</span>
          <span class="label">Dashboard</span>
        </router-link>
        <router-link
          to="/promo-queue"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Release & Promo Queue' : null"
        >
          <span class="icon">🚀</span>
          <span class="label">Promo &amp; Releases</span>
        </router-link>
        <router-link
          to="/projects"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Projekte & Releases' : null"
        >
          <span class="icon">📁</span>
          <span class="label">Projekte</span>
        </router-link>
        <router-link
          to="/tasks"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Tasks & To-Dos' : null"
        >
          <span class="icon">🗒️</span>
          <span class="label">Tasks</span>
        </router-link>
        <router-link
          to="/timeline"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Release Timeline' : null"
        >
          <span class="icon">🗓️</span>
          <span class="label">Timeline</span>
        </router-link>

        <!-- SECTION 2: ARENA & COMMUNITY -->
        <div class="nav-section-title" v-if="!collapsed || isMobile">
          <span>ARENA &amp; COMMUNITY</span>
        </div>
        <router-link
          to="/tournaments"
          class="nav-link arena-external-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Zur UNYQ Turnier & Battle Arena' : null"
        >
          <span class="icon">🏆</span>
          <span class="label">UNYQ Arena</span>
          <span class="ext-pill" v-if="!collapsed || isMobile">Öffnen&nbsp;↗</span>
        </router-link>
        <router-link
          to="/profiles"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Artists & Collabs' : null"
        >
          <span class="icon">🎤</span>
          <span class="label">Artists &amp; Collabs</span>
        </router-link>
        <router-link
          v-if="isTeam"
          to="/reviews"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Review & Feedback' : null"
        >
          <span class="icon">✅</span>
          <span class="label">Review Queue</span>
        </router-link>
        <router-link
          to="/chats"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Studio Chat' : null"
        >
          <span class="icon">💬</span>
          <span class="label">Studio Chat</span>
          <small v-if="unreadCount" class="pill">{{ unreadCount }}</small>
        </router-link>

        <!-- SECTION 3: WACHSTUM & APPS -->
        <div class="nav-section-title" v-if="!collapsed || isMobile">
          <span>WACHSTUM &amp; APPS</span>
        </div>
        <router-link
          to="/growpro"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'GrowPro Ziele' : null"
        >
          <span class="icon">🌱</span>
          <span class="label">GrowPro Ziele</span>
        </router-link>
        <router-link
          to="/points"
          class="nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Points & XP' : null"
        >
          <span class="icon">🧮</span>
          <span class="label">Points &amp; XP</span>
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
          v-if="isAdmin"
          to="/platforms/admin/stats-manager"
          class="nav-link admin-nav-link"
          @click="handleNavClick"
          :title="collapsed && !isMobile ? 'Daten- & Stats-Manager' : null"
        >
          <span class="icon">⚙️</span>
          <span class="label">Stats &amp; Reset</span>
        </router-link>

        <div class="apps-quick-dock" v-if="!collapsed || isMobile">
          <router-link to="/platforms" class="app-dock-btn" title="UNYQ Hub">
            <span class="dock-ico">🧭</span>
            <span class="dock-name">Hub</span>
          </router-link>
          <router-link to="/platforms/music" class="app-dock-btn" title="UNYQ Music Player">
            <span class="dock-ico">🎧</span>
            <span class="dock-name">Music</span>
          </router-link>
          <router-link to="/platforms/songs" class="app-dock-btn" title="Songs & Beats Tool">
            <span class="dock-ico">🎵</span>
            <span class="dock-name">Songs</span>
          </router-link>
          <router-link to="/platforms/library" class="app-dock-btn" title="Free Sound Library">
            <span class="dock-ico">📦</span>
            <span class="dock-name">Library</span>
          </router-link>
          <router-link v-if="isTeam" to="/platforms/team-tasks" class="app-dock-btn" title="Team & Tool Tasks">
            <span class="dock-ico">🛠️</span>
            <span class="dock-name">Tools</span>
          </router-link>
          <router-link to="/platforms/forum" class="app-dock-btn" title="Community Forum">
            <span class="dock-ico">💭</span>
            <span class="dock-name">Forum</span>
          </router-link>
          <router-link to="/platforms/finance" class="app-dock-btn" title="Finance & Royalties">
            <span class="dock-ico">💰</span>
            <span class="dock-name">Finance</span>
          </router-link>
          <router-link to="/platforms/extra" class="app-dock-btn" title="Tools & Socials">
            <span class="dock-ico">🌐</span>
            <span class="dock-name">Extra</span>
          </router-link>
        </div>
        <router-link
          v-else
          to="/platforms"
          class="nav-link"
          :title="'UNYQ Hub & Apps'"
        >
          <span class="icon">🧭</span>
        </router-link>
      </nav>

      <!-- Sidebar User Footer -->
      <div class="sidebar-user-footer" @click="router.push('/me')" title="Zu meinem Profil">
        <div class="user-avatar-mini">{{ initial }}</div>
        <div class="user-info-mini" v-if="!collapsed || isMobile">
          <span class="user-name-text">{{ me?.name || me?.username || 'Mein Account' }}</span>
          <span class="user-role-text">{{ isTeam ? 'Team Member' : 'Artist / Producer' }}</span>
        </div>
        <div class="version-action-wrap" v-if="!collapsed || isMobile" @click.stop="openPatchnotes(0)" title="Patchnotes ansehen">
          <span class="version-tag">
            <strong class="ver-bold">{{ parsedVersion.majorMinor }}</strong><span class="ver-thin">{{ parsedVersion.patchRest }}</span>
          </span>
          <span class="pn-click-hint">Patchnotes</span>
        </div>
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
          <router-link
            to="/tournaments"
            class="topbar-arena-jump-btn"
            title="Zur eigenständigen UNYQ Turnier- und Battle-Arena wechseln"
          >
            <span>🏆 Zur Arena ↗</span>
          </router-link>
          <button
            class="topbar-patchnotes-btn"
            type="button"
            @click="openPatchnotes(0)"
            title="Patchnotes anzeigen"
          >
            <span class="v-pill">
              <strong class="ver-bold">{{ parsedVersion.majorMinor }}</strong><span class="ver-thin">{{ parsedVersion.patchRest }}</span>
            </span>
            <span class="pn-text">Patchnotes</span>
          </button>
          <span v-if="platformSlug" class="platform-version">{{ platformSlug }} v{{ platformVersion }}</span>
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
          <div class="notification-dropdown">
            <button
              class="iconbtn top-icon-btn"
              type="button"
              @click.stop="toggleNotificationMenu"
              title="Benachrichtigungen"
            >
              <svg class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
                <path d="M6 8a6 6 0 1 1 12 0v4.5l1.7 2.6A1 1 0 0 1 18.9 17H5.1a1 1 0 0 1-.8-1.9L6 12.5z" />
                <path d="M10 19a2 2 0 0 0 4 0" />
              </svg>
              <span v-if="notificationCount" class="pill toolbar-pill">{{ notificationBadge }}</span>
            </button>

            <!-- Small Notification Popover Dropdown -->
            <div v-if="notificationMenuOpen" class="notification-popover card" @click.stop>
              <div class="notif-popover-head">
                <div class="notif-title-group">
                  <strong>Benachrichtigungen</strong>
                  <span class="notif-count-badge" v-if="notificationCount">{{ notificationCount }}</span>
                </div>
                <div class="notif-head-actions">
                  <button
                    class="btn ghost micro-btn"
                    type="button"
                    v-if="notificationCount"
                    @click="markAllNotificationsRead"
                    :disabled="markingNotifsRead"
                    title="Alle als gelesen markieren"
                  >
                    Gelesen
                  </button>
                  <button
                    class="btn ghost micro-btn expand-btn"
                    type="button"
                    @click="openNotificationModal"
                    title="Als großes Pop-up öffnen"
                  >
                    ⛶ Großformat
                  </button>
                </div>
              </div>

              <!-- Mini List -->
              <div v-if="notificationsLoading" class="notif-loading muted small">
                Lade Benachrichtigungen...
              </div>
              <div v-else-if="!recentNotifications.length" class="notif-empty muted small">
                Keine neuen Benachrichtigungen 🎉
              </div>
              <div v-else class="notif-popover-list">
                <div
                  v-for="item in recentNotifications.slice(0, 5)"
                  :key="item.id"
                  class="notif-mini-item"
                  :class="{ unread: !item.is_read }"
                  @click="handleNotificationClick(item)"
                >
                  <span class="notif-dot" v-if="!item.is_read"></span>
                  <div class="notif-mini-body">
                    <strong class="notif-mini-title">{{ item.title }}</strong>
                    <p class="notif-mini-snippet muted tiny" v-if="item.body">{{ item.body }}</p>
                    <span class="notif-mini-time muted tiny">{{ formatNotifTime(item.created_at) }}</span>
                  </div>
                  <button
                    v-if="!item.is_read"
                    class="notif-check-btn"
                    type="button"
                    @click.stop="markSingleNotificationRead(item)"
                    title="Als gelesen markieren"
                  >
                    ✓
                  </button>
                </div>
              </div>

              <div class="notif-popover-foot">
                <button class="btn btn-sm full-width-btn" type="button" @click="openNotificationModal">
                  Alle Benachrichtigungen anzeigen (Pop-up) ↗
                </button>
              </div>
            </div>
          </div>
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
              <p class="menu-item danger" @click="logout">Logout</p>
            </div>
          </div>
        </div>
      </header>

      <main class="content compact-content" :class="{ 'with-player': isPlayerActive }">
        <router-view :key="routerViewKey" />
      </main>
    </div>

    <!-- Large Notification Modal Popup -->
    <div v-if="showNotificationModal" class="modal-backdrop" @click.self="showNotificationModal = false">
      <div class="modal card notification-modal-wide">
        <div class="modal-head">
          <div class="modal-title-with-badge">
            <span class="notif-modal-icon">🔔</span>
            <div>
              <h3>Benachrichtigungen</h3>
              <p class="muted small">Alle Hinweise zu Projekten, Tasks, Releases und System-Updates.</p>
            </div>
          </div>
          <div class="modal-head-right">
            <button
              class="btn ghost tiny"
              v-if="notificationCount"
              @click="markAllNotificationsRead"
              :disabled="markingNotifsRead"
            >
              Alle als gelesen
            </button>
            <button class="btn ghost tiny close-btn" type="button" @click="showNotificationModal = false">✕</button>
          </div>
        </div>

        <!-- Filter Chips in Modal -->
        <div class="notif-modal-filters">
          <button
            class="chip"
            :class="{ active: notifFilterMode === 'all' }"
            @click="notifFilterMode = 'all'"
          >
            Alle ({{ fullNotifications.length }})
          </button>
          <button
            class="chip"
            :class="{ active: notifFilterMode === 'unread' }"
            @click="notifFilterMode = 'unread'"
          >
            Ungelesen ({{ notificationCount }})
          </button>
        </div>

        <div class="notif-modal-body">
          <div v-if="notificationsLoading" class="muted p-4">Lade Benachrichtigungen...</div>
          <div v-else-if="!filteredFullNotifications.length" class="muted empty-notifs">
            Keine Benachrichtigungen gefunden.
          </div>
          <div v-else class="notif-full-list">
            <div
              v-for="n in filteredFullNotifications"
              :key="n.id"
              class="notif-full-card card"
              :class="{ unread: !n.is_read }"
            >
              <div class="nfc-left">
                <span class="nfc-dot" v-if="!n.is_read"></span>
                <div class="nfc-main">
                  <div class="nfc-header-row">
                    <strong class="nfc-title">{{ n.title }}</strong>
                    <span class="nfc-time muted tiny">{{ formatNotifTime(n.created_at) }}</span>
                  </div>
                  <p class="nfc-body" v-if="n.body">{{ n.body }}</p>
                  <div class="nfc-context-row" v-if="n.project || n.task || n.actor">
                    <span v-if="n.project" class="context-tag">📁 {{ n.project.title || n.project }}</span>
                    <span v-if="n.task" class="context-tag">🗒️ {{ n.task.title || n.task }}</span>
                    <span v-if="n.actor" class="context-tag">👤 {{ n.actor.name || n.actor.username || n.actor }}</span>
                  </div>
                </div>
              </div>
              <div class="nfc-actions">
                <button
                  v-if="!n.is_read"
                  class="btn ghost tiny"
                  type="button"
                  @click="markSingleNotificationRead(n)"
                >
                  Als gelesen
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="sidebar-overlay" v-if="mobileOpen && isMobile" @click="toggleSidebar"></div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import { useRouter, useRoute } from "vue-router";
import GlobalAudioPlayer from "../components/GlobalAudioPlayer.vue";
import { useGlobalAudio } from "../composables/useGlobalAudio";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import { usePlatformVersion } from "../composables/usePlatformVersion";
import { APP_VERSION } from "../config/version";
import { usePatchnotes } from "../composables/usePatchnotes";

const router = useRouter();
const route = useRoute();
const { openPatchnotes, parsedVersion } = usePatchnotes();
const routeRef = computed(() => route);
const { currentTrack, isPlayerEnabled } = useGlobalAudio();
const isPlayerActive = computed(() => isPlayerEnabled.value && !!currentTrack.value);

const {
  profile: me,
  isTeam,
  isAdmin,
  workspaceMode,
  isContestOnly,
  isUnyqArtist,
  setWorkspaceMode,
  fetchProfile,
  clearProfile,
} = useCurrentProfile();

function toggleWorkspace(mode) {
  setWorkspaceMode(mode);
  showToast(
    mode === "CONTEST_ONLY"
      ? "🏆 Nur Turniere & Battles aktiv (Fokus-Modus)"
      : "⭐ UNYQ Artist Modus aktiv (Volles Studio)",
    "info"
  );
  if (mode === "CONTEST_ONLY" && ["dashboard", "projects", "tasks", "timeline", "songs", "growpro"].includes(route.name)) {
    router.push({ name: "tournaments" });
  }
}

const open = ref(false);
const search = ref("");
const unreadCount = ref(0);
const notificationCount = ref(0);
const theme = ref(typeof window !== "undefined" && localStorage.getItem("theme") === "light" ? "light" : "dark");
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

const notificationMenuOpen = ref(false);
const showNotificationModal = ref(false);
const recentNotifications = ref([]);
const fullNotifications = ref([]);
const notificationsLoading = ref(false);
const markingNotifsRead = ref(false);
const notifFilterMode = ref("all");

const filteredFullNotifications = computed(() => {
  if (notifFilterMode.value === "unread") {
    return fullNotifications.value.filter((n) => !n.is_read);
  }
  return fullNotifications.value;
});

function toggleNotificationMenu() {
  notificationMenuOpen.value = !notificationMenuOpen.value;
  if (notificationMenuOpen.value) {
    chatOpen.value = false;
    open.value = false;
    fetchNotificationsPreview();
  }
}

function openNotificationModal() {
  notificationMenuOpen.value = false;
  showNotificationModal.value = true;
  fetchAllNotifications();
}

function formatNotifTime(dateStr) {
  if (!dateStr) return "";
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = now - d;
    const diffMins = Math.floor(diffMs / 60000);
    if (diffMins < 1) return "Gerade eben";
    if (diffMins < 60) return `Vor ${diffMins}m`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `Vor ${diffHours}h`;
    return d.toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
  } catch {
    return "";
  }
}

async function fetchNotificationsPreview() {
  notificationsLoading.value = true;
  try {
    const { data } = await api.get("notifications/", { params: { page_size: 6 } });
    recentNotifications.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Konnte Benachrichtigungen nicht laden", err);
  } finally {
    notificationsLoading.value = false;
  }
}

async function fetchAllNotifications() {
  notificationsLoading.value = true;
  try {
    const { data } = await api.get("notifications/", { params: { page_size: 100 } });
    fullNotifications.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error(err);
  } finally {
    notificationsLoading.value = false;
  }
}

async function markSingleNotificationRead(n) {
  if (!n?.id || n.is_read) return;
  n.is_read = true;
  if (notificationCount.value > 0) notificationCount.value--;
  try {
    await api.patch(`notifications/${n.id}/`, { is_read: true });
  } catch (err) {
    console.error(err);
  }
}

async function markAllNotificationsRead() {
  if (markingNotifsRead.value) return;
  markingNotifsRead.value = true;
  try {
    await api.post("notifications/mark-all-read/");
    notificationCount.value = 0;
    recentNotifications.value.forEach((n) => (n.is_read = true));
    fullNotifications.value.forEach((n) => (n.is_read = true));
    showToast("Alle Benachrichtigungen als gelesen markiert", "success");
  } catch (err) {
    console.error(err);
  } finally {
    markingNotifsRead.value = false;
  }
}

function handleNotificationClick(item) {
  markSingleNotificationRead(item);
  notificationMenuOpen.value = false;
  if (item.task) {
    router.push({ name: "tasks" });
  } else if (item.project) {
    router.push({ name: "projects" });
  }
}

let unreadInterval = null;
let notificationInterval = null;

const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});

const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));
const routerViewKey = computed(() => `${route.fullPath}::${viewRefreshKey.value}`);
const notificationBadge = computed(() => {
  const unread = Number(notificationCount.value || 0);
  return unread > 99 ? "99+" : String(unread);
});
function notify(msg) {
  showToast(msg);
}

function applyTheme() {
  const root = document.documentElement;
  const isDark = theme.value !== "light";
  root.classList.toggle("dark", isDark);
  root.classList.toggle("light", !isDark);
  root.style.colorScheme = isDark ? "only dark" : "only light";
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
  if (!localStorage.getItem("access")) {
    unreadCount.value = 0;
    return;
  }
  if (loadingUnread.value) return;
  loadingUnread.value = true;
  try {
    const { data } = await api.get("threads/");
    const threads = Array.isArray(data) ? data : data?.results || [];
    const messages = threads.flatMap((thread) => (Array.isArray(thread?.messages) ? thread.messages : []));
    const myId = me.value?.id;
    unreadCount.value = messages.filter((m) => !m.read && m.sender !== myId).length;
  } catch (err) {
    if (err?.response?.status === 401) {
      unreadCount.value = 0;
      return;
    }
    console.error("Konnte Threads nicht laden", err);
  } finally {
    loadingUnread.value = false;
  }
}

async function loadNotificationCount() {
  try {
    if (!localStorage.getItem("access")) {
      notificationCount.value = 0;
      return;
    }
    const { data } = await api.get("notifications/unread-count/");
    notificationCount.value = data?.unread || 0;
  } catch (err) {
    if (err?.response?.status === 401) {
      notificationCount.value = 0;
      return;
    }
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
    chatOpen.value = false;
    notificationMenuOpen.value = false;
    if (isMobile.value) {
      mobileOpen.value = false;
      if (typeof document !== "undefined") {
        document.body.style.overflow = "";
      }
    }
  }
);

function handleWindowClick() {
  open.value = false;
  chatOpen.value = false;
  notificationMenuOpen.value = false;
}

onMounted(async () => {
  if (typeof window !== "undefined") {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "light" || storedTheme === "dark") {
      theme.value = storedTheme;
    } else {
      theme.value = "dark";
    }
    collapsed.value = localStorage.getItem("layout:sidebar") === "collapsed";
  }
  applyTheme();
  updateViewport();
  if (typeof window !== "undefined") {
    window.addEventListener("resize", updateViewport);
    window.addEventListener("click", handleWindowClick);
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
    window.removeEventListener("click", handleWindowClick);
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
.platform-version {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--card) 86%, var(--brand) 14%);
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
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
}

:global(.dark) .chat-menu .menu-item:hover {
  background: rgba(124, 161, 255, 0.16);
}

/* Sidebar Section Headers */
.brand-sub {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.14em;
  color: #3b82f6;
  background: rgba(59, 130, 246, 0.12);
  padding: 2px 6px;
  border-radius: 6px;
}

.nav-section-title {
  padding: 14px 12px 4px;
  font-size: 9.5px;
  font-weight: 800;
  letter-spacing: 0.12em;
  color: var(--muted);
  text-transform: uppercase;
  opacity: 0.75;
}

/* Arena Highlight Link */
.highlight-arena {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.08), rgba(245, 158, 11, 0.08));
  border: 1px solid rgba(245, 158, 11, 0.15);
}
.highlight-arena:hover {
  background: linear-gradient(90deg, rgba(239, 68, 68, 0.14), rgba(245, 158, 11, 0.14));
}

.nav-live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  margin-left: auto;
  box-shadow: 0 0 8px #ef4444;
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.85); }
}

/* UNYQ Ecosystem Mini-Dock */
.apps-quick-dock {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  padding: 4px 6px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.app-dock-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 8px 4px;
  border-radius: 10px;
  background: var(--card);
  text-decoration: none;
  color: inherit;
  font-size: 11px;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.app-dock-btn:hover {
  background: rgba(59, 130, 246, 0.15);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-1px);
}

.dock-ico {
  font-size: 16px;
  margin-bottom: 2px;
}

.dock-name {
  font-size: 10px;
  font-weight: 600;
  color: var(--muted);
}

.app-dock-btn:hover .dock-name {
  color: #fff;
}

/* Sidebar User Footer */
.sidebar-user-footer {
  margin-top: auto;
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
}

.sidebar-user-footer:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.25);
}

.user-avatar-mini {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  color: #fff;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 14px;
}

.user-info-mini {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  flex: 1;
}

.user-name-text {
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role-text {
  font-size: 10.5px;
  color: var(--muted);
}

.version-tag {
  font-size: 10px;
  color: var(--muted);
  opacity: 0.6;
  font-family: monospace;
}

/* Workspace Mode Strip */
.workspace-mode-strip {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.28);
  padding: 4px;
  border-radius: 10px;
  margin: 6px 12px 14px;
  border: 1px solid var(--border);
}

.mode-switch-btn {
  flex: 1;
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 7px;
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.mode-switch-btn:hover {
  color: #fff;
}

.mode-switch-btn.active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.35), rgba(139, 92, 246, 0.35));
  color: #fff;
  border: 1px solid rgba(59, 130, 246, 0.5);
}

.badge.contest {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.content.compact-content.with-player {
  padding-bottom: 84px;
}

.version-action-wrap {
  display: inline-flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.version-action-wrap:hover {
  transform: translateY(-1px);
}

.ver-bold {
  font-weight: 800;
  color: #c7d2fe;
}

.ver-thin {
  font-weight: 300;
  font-size: 11px;
  color: #94a3b8;
  opacity: 0.85;
}

.pn-click-hint {
  font-size: 10px;
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
}

.topbar-patchnotes-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.25);
  color: var(--text);
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s ease;
}

.topbar-patchnotes-btn:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.45);
  transform: translateY(-1px);
}

.topbar-patchnotes-btn .v-pill {
  display: inline-flex;
  align-items: baseline;
  line-height: 1;
}

.topbar-patchnotes-btn .pn-text {
  font-weight: 600;
  color: #818cf8;
  text-decoration: underline;
  text-underline-offset: 2px;
}

:global(.light) .ver-bold {
  color: #4338ca;
}

:global(.light) .ver-thin {
  color: #64748b;
}

:global(.light) .topbar-patchnotes-btn .pn-text {
  color: #4f46e5;
}

.topbar-arena-jump-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.2), rgba(245, 158, 11, 0.25));
  border: 1px solid rgba(234, 179, 8, 0.4);
  color: #fef08a;
  font-size: 12px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.topbar-arena-jump-btn:hover {
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.35), rgba(245, 158, 11, 0.4));
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(234, 179, 8, 0.2);
  color: #fff;
}

.ext-pill {
  margin-left: auto;
  font-size: 10px;
  font-weight: 800;
  color: #fde047;
  background: rgba(234, 179, 8, 0.15);
  border: 1px solid rgba(234, 179, 8, 0.3);
  padding: 2px 7px;
  border-radius: 6px;
  white-space: nowrap !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 3px !important;
  flex-shrink: 0 !important;
  line-height: 1;
}

.arena-external-link {
  background: rgba(234, 179, 8, 0.05);
  border: 1px solid rgba(234, 179, 8, 0.15);
}

.arena-external-link:hover {
  background: rgba(234, 179, 8, 0.12);
  border-color: rgba(234, 179, 8, 0.3);
}

.admin-nav-link {
  color: #fca5a5 !important;
}

.admin-nav-link:hover {
  background: rgba(239, 68, 68, 0.12) !important;
}

/* Notification Popover Dropdown */
.notification-dropdown {
  position: relative;
}

.notification-popover {
  position: absolute;
  right: 0;
  top: 48px;
  width: 350px;
  max-width: 90vw;
  z-index: 50;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-radius: 16px;
  background: var(--card);
  border: 1px solid var(--border);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.35);
  animation: popoverFadeIn 0.18s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes popoverFadeIn {
  from { opacity: 0; transform: translateY(-6px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.notif-popover-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
}

.notif-title-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.notif-count-badge {
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 999px;
}

.notif-head-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.micro-btn {
  padding: 3px 8px;
  font-size: 11px;
}

.expand-btn {
  color: var(--brand);
}

.notif-loading,
.notif-empty {
  padding: 16px 8px;
  text-align: center;
}

.notif-popover-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 280px;
  overflow-y: auto;
}

.notif-mini-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  background: var(--surface);
  cursor: pointer;
  transition: all 0.15s ease;
  position: relative;
}

.notif-mini-item:hover {
  background: rgba(124, 161, 255, 0.12);
  transform: translateX(2px);
}

.notif-mini-item.unread {
  border-left: 3px solid var(--brand);
}

.notif-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--brand);
  margin-top: 5px;
  flex-shrink: 0;
}

.notif-mini-body {
  flex: 1;
  min-width: 0;
}

.notif-mini-title {
  display: block;
  font-size: 12.5px;
  color: var(--text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.notif-mini-snippet {
  margin: 2px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.3;
}

.notif-mini-time {
  font-size: 10px;
  display: block;
  margin-top: 2px;
}

.notif-check-btn {
  background: transparent;
  border: none;
  color: var(--muted);
  cursor: pointer;
  padding: 2px 4px;
  border-radius: 4px;
  font-size: 12px;
  transition: color 0.15s ease;
}

.notif-check-btn:hover {
  color: #10b981;
}

.notif-popover-foot {
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

.full-width-btn {
  width: 100%;
  text-align: center;
  justify-content: center;
  font-size: 12px;
}

/* Large Notification Modal */
.notification-modal-wide {
  width: 720px;
  max-width: 95vw;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  padding: 24px;
  border-radius: 20px;
}

.modal-title-with-badge {
  display: flex;
  align-items: center;
  gap: 12px;
}

.notif-modal-icon {
  font-size: 24px;
}

.modal-head-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.notif-modal-filters {
  display: flex;
  gap: 8px;
  margin: 16px 0 12px;
}

.notif-modal-body {
  flex: 1;
  overflow-y: auto;
  min-height: 200px;
  max-height: 55vh;
  padding-right: 4px;
}

.empty-notifs {
  padding: 36px 0;
  text-align: center;
}

.notif-full-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notif-full-card {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.notif-full-card.unread {
  border-color: rgba(124, 161, 255, 0.4);
  background: rgba(124, 161, 255, 0.05);
}

.nfc-left {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  flex: 1;
}

.nfc-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #3b82f6;
  margin-top: 6px;
  flex-shrink: 0;
}

.nfc-main {
  flex: 1;
}

.nfc-header-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.nfc-title {
  font-size: 14px;
  color: var(--text);
}

.nfc-time {
  font-size: 11px;
}

.nfc-body {
  margin: 6px 0 8px;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.45;
}

.nfc-context-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.context-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.nfc-actions {
  flex-shrink: 0;
}
</style>
