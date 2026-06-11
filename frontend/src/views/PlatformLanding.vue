<template>
  <div class="platform-hub">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Willkommen im UNYQ Hub</h1>
          <p class="hero-subtitle">
            Dein zentraler Zugang zu allen UNYQ-Plattformen. Entdecke Tools und Funktionen, die auf deine Rolle zugeschnitten sind.
          </p>
          <div v-if="isTeam" class="audience-switch">
            <button
              v-for="mode in audienceModes"
              :key="mode.key"
              type="button"
              class="audience-chip"
              :class="{ active: viewMode === mode.key }"
              @click="setAudienceMode(mode.key)"
            >
              {{ mode.label }}
            </button>
          </div>
        </div>
        <div class="hero-visual">
          <div class="floating-icons">
            <div class="icon-float icon-1">🎵</div>
            <div class="icon-float icon-2">🏆</div>
            <div class="icon-float icon-3">📍</div>
            <div class="icon-float icon-4">💰</div>
            <div class="icon-float icon-5">📊</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Platforms Grid -->
    <section class="platforms-section">
      <div class="section-header">
        <div class="section-header-left">
          <h2>Plattformen</h2>
          <p>Klick zum Öffnen — ziehe Karten zum Umsortieren.</p>
        </div>
        <button
          class="btn ghost edit-order-btn"
          type="button"
          :class="{ active: editMode }"
          @click="editMode = !editMode"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" class="sort-icon"><path d="M4 6h16M4 12h16M4 18h16"/></svg>
          {{ editMode ? 'Fertig' : 'Reihenfolge ändern' }}
        </button>
      </div>

      <div class="platforms-grid">
        <div
          v-for="platform in orderedPlatforms"
          :key="platform.key"
          class="platform-card"
          role="article"
          :aria-label="`${platform.title} - ${platform.category}`"
          :draggable="editMode"
          :class="{ 'is-dragging': draggedKey === platform.key, 'drag-over': dragOverKey === platform.key, 'edit-active': editMode }"
          @dragstart="onDragStart($event, platform.key)"
          @dragover="onDragOver($event, platform.key)"
          @dragleave="dragOverKey = null"
          @drop="onDrop($event, platform.key)"
          @dragend="onDragEnd"
          @click="!editMode && openPlatform(platform.key, platform)"
        >
          <div v-if="editMode" class="drag-handle" aria-hidden="true">
            <svg viewBox="0 0 24 24"><path d="M9 5a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm6 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2zM9 11a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm6 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2zM9 17a1 1 0 1 0 0 2 1 1 0 0 0 0-2zm6 0a1 1 0 1 0 0 2 1 1 0 0 0 0-2z"/></svg>
          </div>
          <div class="platform-header">
            <div class="platform-icon" aria-hidden="true">{{ platform.icon }}</div>
            <div class="platform-meta">
              <h3>{{ platform.title }}</h3>
              <div class="platform-tags">
                <span class="platform-tag">{{ platform.category }}</span>
                <span class="platform-tag version">v{{ platform.version || '0.1' }}</span>
                <span
                  class="platform-tag status"
                  :class="`status-${platform.status || 'live'}`"
                >
                  {{ platformStatusLabel(platform.status) }}
                </span>
                <span v-if="platform.key === 'dashboard' && unreadNotifications" class="platform-tag notif-badge">
                  🔔 {{ unreadNotificationBadge }}
                </span>
                <span v-if="platform.key === 'dashboard' && hubBadges.overdueTasks" class="platform-tag badge-danger">
                  🔴 {{ hubBadges.overdueTasks }} überfällig
                </span>
                <span v-if="platform.key === 'dashboard' && hubBadges.pendingReviews" class="platform-tag badge-warning">
                  👀 {{ hubBadges.pendingReviews }} Review
                </span>
                <span v-if="platform.key === 'dashboard' && hubBadges.staleGrowpro" class="platform-tag badge-danger">
                  ⏰ {{ hubBadges.staleGrowpro }} GrowPro stale
                </span>
              </div>
            </div>
          </div>
          <p class="platform-description">{{ platform.description }}</p>
          <p v-if="platform.status_note" class="platform-note">{{ platform.status_note }}</p>
          <button
            v-if="!editMode"
            class="platform-btn"
            :aria-label="`${platform.buttonLabel}: ${platform.title}`"
            @click.stop="openPlatform(platform.key, platform)"
          >
            {{ platform.buttonLabel }}
            <svg class="arrow-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
          <div v-else class="edit-hint">Ziehen zum Umsortieren</div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section" v-if="isTeam">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ totalUsers }}</div>
          <div class="stat-label">Aktive Nutzer</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ activeProjects }}</div>
          <div class="stat-label">Laufende Projekte</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ pendingTasks }}</div>
          <div class="stat-label">Offene Tasks</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ upcomingEvents }}</div>
          <div class="stat-label">Bevorstehende Events</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import api from "../api";
import {
  fetchManagedPlatformAccessState,
  mapAccessStateRows,
} from "../services/managedPlatforms";

const router = useRouter();
const { showToast } = useToast();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const viewMode = ref("default");
const editMode = ref(false);
const draggedKey = ref(null);
const dragOverKey = ref(null);
const unreadNotifications = ref(0);
const hubBadges = ref({ openTasks: 0, overdueTasks: 0, pendingReviews: 0, staleGrowpro: 0 });

function loadSavedOrder() {
  try {
    const raw = localStorage.getItem("unyq_platform_order");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}
const platformOrder = ref(loadSavedOrder());
const accessStateBySlug = ref({});
const HUB_AUDIENCE_KEY = "unyq_hub_audience_mode";

const audienceModes = [
  { key: "default", label: "Team/Admin Modus" },
  { key: "MEMBER", label: "Normal User Modus" },
  { key: "ARTIST", label: "Artist Vorschau" },
];

function setAudienceMode(mode) {
  viewMode.value = mode;
  try {
    localStorage.setItem(HUB_AUDIENCE_KEY, mode);
  } catch {
    // ignore storage errors
  }
}

// Real stats from API
const stats = ref({
  totalUsers: 0,
  activeProjects: 0,
  pendingTasks: 0,
  upcomingEvents: 0,
});

const totalUsers = computed(() => stats.value.totalUsers);
const activeProjects = computed(() => stats.value.activeProjects);
const pendingTasks = computed(() => stats.value.pendingTasks);
const upcomingEvents = computed(() => stats.value.upcomingEvents);
const unreadNotificationBadge = computed(() => (unreadNotifications.value > 99 ? "99+" : String(unreadNotifications.value)));

function asList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
}

const platforms = [
  // KI-Hinweis:
  // Plattform-Versionen werden durch das Backend automatisch bei funktionalen Aenderungen hochgezaehlt.
  // Nicht manuell im Frontend setzen - nur anzeigen (state.version).
  {
    key: "dashboard",
    title: computed(() => {
      if (isTeam.value) return "ProArtist Team";
      return "ProArtist Artist";
    }),
    category: "Übersicht",
    description: "Dein persönliches Dashboard mit allen wichtigen Informationen und Schnellzugriffen.",
    buttonLabel: "Öffnen",
    icon: "📊",
    features: ["Übersicht", "Schnellzugriffe", "Benachrichtigungen"],
    roles: ["TEAM", "ARTIST", "PROD", "LOC"],
    status: "live",
  },
  {
    key: "contests",
    title: "UNYQ Turnier",
    category: "Wettbewerbe",
    description: "Team erstellt Turniere, Artists bewerben sich oder reichen Runden ein und Battles laufen mit Voting.",
    buttonLabel: "Starten",
    icon: "🏆",
    features: ["Turniere", "Einreichungen", "Voting"],
    roles: ["TEAM", "ARTIST", "PROD"],
    status: "live",
  },
  {
    key: "music",
    title: "Music Manager",
    category: "Musik",
    description: "Verwalte deine Songs, Alben und Releases in einem professionellen Music Manager.",
    buttonLabel: "Verwalten",
    icon: "🎵",
    features: ["Songs", "Releases", "Analytics"],
    roles: ["TEAM", "ARTIST", "PROD"],
    status: "live",
  },
  {
    key: "locations",
    title: "Locations",
    category: "Events",
    description: "Finde und verwalte Locations für deine Events und Auftritte.",
    buttonLabel: "Suchen",
    icon: "📍",
    features: ["Locations", "Events", "Buchungen"],
    roles: ["TEAM", "LOC", "PROD"],
    status: "beta",
  },
  {
    key: "finance",
    title: "Finance Planner",
    category: "Finanzen",
    description: "Plane dein Budget, verwalte Einnahmen und Ausgaben, tilge Schulden effizient.",
    buttonLabel: "Planen",
    icon: "💰",
    features: ["Budget", "Schulden", "Einnahmen"],
    roles: ["TEAM", "MEMBER"],
    status: "live",
  },
  {
    key: "content-studio",
    title: "Content Studio",
    category: "Content",
    description: "Erstelle zentral Tipps, News und Plugin-Tutorials fuer alle Nutzerbereiche.",
    buttonLabel: "Erstellen",
    icon: "📝",
    features: ["Tipps", "News", "Tutorials"],
    roles: ["TEAM", "ARTIST", "PROD", "MEMBER"],
    status: "beta",
  },
  {
    key: "content-schedule",
    title: "Content Schedule",
    category: "Planung",
    description: "Plane deinen Content von Montag bis Sonntag. Lege Content-Serien mit Header, Parts und Links per Drag & Drop an.",
    buttonLabel: "Planen",
    icon: "📅",
    features: ["Wochenplan", "Drag & Drop", "Content-Serien"],
    roles: ["TEAM", "ARTIST", "PROD", "MEMBER"],
    status: "beta",
  },
  {
    key: "fitness",
    title: "Fitness Tracker",
    category: "Health",
    description: "Tracke Kalorien, schaetze deinen Tagesverbrauch und finde einfache Essensideen fuer jede Mahlzeit.",
    buttonLabel: "Starten",
    icon: "🏋️",
    features: ["Kcal", "Verbrauch", "Essensideen"],
    roles: ["TEAM", "ARTIST", "PROD", "VIDEO", "MERCH", "MKT", "LOC", "MEMBER"],
    status: "beta",
  },
  {
    key: "todo",
    title: "Todo",
    category: "Organisation",
    description: "Erstelle Todos mit oder ohne Datum und exportiere einzelne Einträge direkt in deinen Kalender.",
    buttonLabel: "Öffnen",
    icon: "✅",
    features: ["Todos", "Optionales Datum", "Kalender-Button"],
    roles: ["TEAM"],
    version: "0.2",
    status: "live",
  },
  {
    key: "plugin-guides",
    title: "Plugin Guides",
    category: "Wissen",
    description: "Eigene Plattform fuer Plugin-Tutorials, Setup-Guides und Best Practices.",
    buttonLabel: "Öffnen",
    icon: "🔌",
    features: ["Tutorials", "Setups", "Workflow-Docs"],
    roles: ["TEAM", "ARTIST", "PROD", "MEMBER", "LOC"],
    status: "live",
  },
  {
    key: "api-center",
    title: "API Platform",
    category: "Entwicklung",
    description: "Eigene Plattform fuer Integrationen, API-Keys und Automatisierungsregeln.",
    buttonLabel: "Verwalten",
    icon: "🔑",
    features: ["Integrationen", "Automation", "Scopes"],
    roles: ["TEAM"],
    status: "live",
  },
  {
    key: "manage-platforms",
    title: "Platform Control",
    category: "Verwaltung",
    description: "Steuere Verfuegbarkeit, Versionen und Hinweise fuer einzelne Plattformen zentral.",
    buttonLabel: "Steuern",
    icon: "🛠️",
    features: ["Status", "Versionen", "Hinweise"],
    roles: ["TEAM"],
    status: "live",
  },
  {
    key: "admin",
    title: "Admin Control Hub",
    category: "Verwaltung",
    description: "Zentrales Verwaltungszentrum für alle UNYQ-Plattformen, Artist-Vorschau und Nutzer.",
    buttonLabel: "Verwalten",
    icon: "🔧",
    features: ["Nutzer", "Plattformen", "Artist View"],
    roles: ["TEAM"],
    status: "live",
  },
  {
    key: "testing",
    title: "TESTING",
    category: "Intern",
    description: "Interne Tests für Backend-Funktionen wie E-Mail, Notifications und mehr.",
    buttonLabel: "Testen",
    icon: "🧪",
    features: ["E-Mail", "Backend", "Debug"],
    roles: ["TEAM"],
    status: "beta",
  },
];

function platformStatusLabel(status) {
  const map = {
    live: "Live",
    beta: "Beta",
    preview: "Preview",
    maintenance: "Wartung",
    locked: "Gesperrt",
  };
  return map[status || "live"] || "Live";
}

function platformSlugForKey(key) {
  return key;
}

const activeRole = computed(() => {
  if (viewMode.value !== "default") return viewMode.value;
  if (isTeam.value) return "TEAM";
  const role = (me.value?.roles || []).find((roleItem) => roleItem.key !== "TEAM");
  return role?.key || "ARTIST";
});

const defaultOrder = [
  "dashboard", "todo", "music", "contests", "content-schedule",
  "content-studio", "plugin-guides", "api-center", "finance", "fitness", "locations", "manage-platforms", "admin", "testing",
];

const visiblePlatforms = computed(() => {
  const currentRole = activeRole.value;
  return platforms
    .filter((platform) => platform.roles.includes(currentRole))
    .map((platform) => {
      const slug = platformSlugForKey(platform.key);
      const state = accessStateBySlug.value[slug];
      if (!state) return platform;

      let status = "live";
      if (state.status === "MAINTENANCE") status = "maintenance";
      if (state.status === "LOCKED") status = "locked";

      return {
        ...platform,
        version: state.version || "0.1",
        status,
        is_accessible: state.is_accessible,
        status_note: state.status_note || "",
      };
    });
});

const orderedPlatforms = computed(() => {
  const visible = visiblePlatforms.value;
  const order = platformOrder.value.length ? platformOrder.value : defaultOrder;
  const known = order.filter((key) => visible.some((p) => p.key === key));
  const rest = visible.filter((p) => !known.includes(p.key));
  return [...known.map((key) => visible.find((p) => p.key === key)).filter(Boolean), ...rest];
});

function onDragStart(event, key) {
  draggedKey.value = key;
  event.dataTransfer.effectAllowed = "move";
}

function onDragOver(event, key) {
  event.preventDefault();
  dragOverKey.value = key;
  event.dataTransfer.dropEffect = "move";
}

function onDrop(event, targetKey) {
  event.preventDefault();
  if (!draggedKey.value || draggedKey.value === targetKey) { dragOverKey.value = null; return; }
  const list = [...orderedPlatforms.value];
  const fromIdx = list.findIndex((p) => p.key === draggedKey.value);
  const toIdx = list.findIndex((p) => p.key === targetKey);
  if (fromIdx === -1 || toIdx === -1) return;
  const [moved] = list.splice(fromIdx, 1);
  list.splice(toIdx, 0, moved);
  platformOrder.value = list.map((p) => p.key);
  localStorage.setItem("unyq_platform_order", JSON.stringify(platformOrder.value));
  draggedKey.value = null;
  dragOverKey.value = null;
}

function onDragEnd() {
  draggedKey.value = null;
  dragOverKey.value = null;
}

function openPlatform(platformKey, platformMeta = null) {
  if (platformMeta && platformMeta.is_accessible === false) {
    const hint = platformMeta.status_note || "Diese Plattform ist aktuell nicht verfuegbar.";
    showToast(hint, "warning");
    return;
  }

  const mapping = {
    dashboard: "/app/dashboard",
    contests: "/platforms/contests",
    music: "/platforms/music",
    locations: "/platforms/locations",
    finance: "/platforms/finance",
    "content-studio": "/platforms/content-studio",
    "content-schedule": "/platforms/content-schedule",
    todo: "/platforms/todo",
    "plugin-guides": "/platforms/plugin-guides",
    "api-center": "/platforms/api-center",
    fitness: "/platforms/fitness",
    admin: "/platforms/admin",
    "manage-platforms": "/platforms/manage-platforms",
    testing: "/app/testing",
  };
  const path = mapping[platformKey];
  if (path) {
    router.push(path);
    return;
  }
  showToast("Diese Plattform wird bald verfügbar sein", "info");
}

async function loadAccessState() {
  try {
    const rows = await fetchManagedPlatformAccessState();
    accessStateBySlug.value = mapAccessStateRows(rows);
  } catch (err) {
    accessStateBySlug.value = {};
  }
}

async function loadStats() {
  if (!isTeam.value) return;
  try {
    const [adminRes, tasksRes, eventsRes] = await Promise.all([
      api.get("admin/overview/"),
      api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS,REVIEW" } }),
      api.get("events/", { params: { upcoming: true, limit: 10 } }),
    ]);
    const taskItems = asList(tasksRes.data);
    const eventItems = asList(eventsRes.data);
    stats.value = {
      totalUsers: adminRes.data.total_users || 0,
      activeProjects: adminRes.data.active_projects || 0,
      pendingTasks: taskItems.length || 0,
      upcomingEvents: eventItems.length || 0,
    };
  } catch (err) {
    console.error("Stats konnten nicht geladen werden", err);
    // Fallback to zeros
    stats.value = { totalUsers: 0, activeProjects: 0, pendingTasks: 0, upcomingEvents: 0 };
  }
}

async function loadNotificationCount() {
  try {
    const { data } = await api.get("notifications/unread-count/");
    unreadNotifications.value = Number(data?.unread || 0);
  } catch {
    unreadNotifications.value = 0;
  }
}

async function loadHubBadges() {
  if (!isTeam.value) return;
  try {
    const [tasksRes, reviewRes, growproRes] = await Promise.all([
      api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS", include_archived: 0, page_size: 1 } }).catch(() => null),
      api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", include_done: 1, include_archived: 0, page_size: 1 } }).catch(() => null),
      api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 200 } }).catch(() => null),
    ]);
    const today = new Date().toISOString().slice(0, 10);
    const taskCount = tasksRes?.data?.count ?? (Array.isArray(tasksRes?.data) ? tasksRes.data.length : 0);
    const overdueCount = await api.get("analytics/summary/").then((r) => r.data?.overdue_tasks || 0).catch(() => 0);
    const reviewCount = reviewRes?.data?.count ?? (Array.isArray(reviewRes?.data) ? reviewRes.data.length : 0);
    const growproItems = Array.isArray(growproRes?.data) ? growproRes.data : growproRes?.data?.results || [];
    const now = Date.now();
    const staleCount = growproItems.filter((goal) => {
      const last = goal.last_logged_at ? new Date(goal.last_logged_at).getTime() : null;
      return !last || (now - last) / (1000 * 60 * 60) > 72;
    }).length;
    hubBadges.value = {
      openTasks: Math.min(99, taskCount),
      overdueTasks: Math.min(99, overdueCount),
      pendingReviews: Math.min(99, reviewCount),
      staleGrowpro: Math.min(99, staleCount),
    };
  } catch {
    // silently ignore
  }
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    try {
      const stored = localStorage.getItem(HUB_AUDIENCE_KEY);
      if (stored && audienceModes.some((mode) => mode.key === stored)) {
        viewMode.value = stored;
      }
    } catch {
      // ignore storage errors
    }
  }
  await Promise.all([loadStats(), loadAccessState(), loadNotificationCount(), loadHubBadges()]);
});
</script>

<style scoped>
.platform-hub {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

/* Hero Section */
.hero-section {
  padding: clamp(28px, 4vw, 50px) 20px;
  background: linear-gradient(135deg, var(--brand) 0%, var(--brand-2) 100%);
  color: white;
  position: relative;
  overflow: hidden;
}

.hero-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 600"><defs><filter id="blur"><feGaussianBlur in="SourceGraphic" stdDeviation="2"/></filter></defs><path d="M0,100 Q300,50 600,100 T1200,100 L1200,0 L0,0 Z" fill="%233b82f6" opacity="0.15" filter="url(%23blur)"/><path d="M0,150 Q300,80 600,150 T1200,150 L1200,100 Q600,50 0,100 Z" fill="%235b6ef2" opacity="0.12" filter="url(%23blur)"/><path d="M0,200 Q300,120 600,200 T1200,200 L1200,150 Q600,80 0,150 Z" fill="%237c61eb" opacity="0.12" filter="url(%23blur)"/><path d="M0,250 Q300,160 600,250 T1200,250 L1200,200 Q600,120 0,200 Z" fill="%239333ea" opacity="0.12" filter="url(%23blur)"/><path d="M0,300 Q300,200 600,300 T1200,300 L1200,250 Q600,160 0,250 Z" fill="%23a855f7" opacity="0.12" filter="url(%23blur)"/><path d="M0,350 Q300,240 600,350 T1200,350 L1200,300 Q600,200 0,300 Z" fill="%23c084fc" opacity="0.12" filter="url(%23blur)"/><path d="M0,400 Q300,280 600,400 T1200,400 L1200,350 Q600,240 0,350 Z" fill="%23e879f9" opacity="0.12" filter="url(%23blur)"/></svg>');
  background-size: 1200px 600px;
  background-position: 0 0;
  opacity: 0.8;
}

@keyframes stripes-flow {
  0%, 100% {
    background-position: 0 0;
    opacity: 0.8;
  }
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1.25fr 0.75fr;
  gap: 28px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-text h1 {
  font-size: clamp(1.9rem, 4.2vw, 3.2rem);
  font-weight: 800;
  margin: 0 0 14px;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: clamp(1rem, 1.8vw, 1.16rem);
  line-height: 1.5;
  opacity: 0.94;
  margin: 0;
}

.hero-shortcuts {
  margin-top: 14px;
  display: flex;
  gap: 10px;
}

.shortcut-btn {
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border-radius: 999px;
  padding: 7px 14px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: 600;
}

.shortcut-icon {
  font-size: 14px;
  line-height: 1;
}

.audience-switch {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.audience-chip {
  border: 1px solid rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
}

.audience-chip.active {
  background: #fff;
  color: #0f172a;
  border-color: #fff;
}

.hero-visual {
  position: relative;
  height: 300px;
}

.floating-icons {
  position: relative;
  width: 100%;
  height: 100%;
}

.icon-float {
  position: absolute;
  font-size: 3rem;
  animation: float 6s ease-in-out infinite;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2));
}

.icon-1 { top: 10%; left: 10%; animation-delay: 0s; }
.icon-2 { top: 20%; right: 20%; animation-delay: 1s; }
.icon-3 { bottom: 20%; left: 20%; animation-delay: 2s; }
.icon-4 { bottom: 10%; right: 10%; animation-delay: 3s; }
.icon-5 { top: 50%; left: 50%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  25% { transform: translateY(-20px) rotate(5deg); }
  50% { transform: translateY(-10px) rotate(-5deg); }
  75% { transform: translateY(-25px) rotate(3deg); }
}

/* Platforms Section */
.platforms-section {
  padding: 44px 20px 56px;
  background: var(--bg);
}

.section-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.section-header-left h2 {
  font-size: clamp(1.5rem, 2.2vw, 2rem);
  font-weight: 700;
  margin: 0 0 4px;
  color: var(--text);
}

.section-header-left p {
  font-size: 0.9rem;
  color: var(--muted);
  margin: 0;
}

.edit-order-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  white-space: nowrap;
  flex-shrink: 0;
}

.edit-order-btn.active {
  background: color-mix(in srgb, var(--brand) 14%, var(--surface) 86%);
  border-color: var(--brand);
  color: var(--brand);
}

.sort-icon {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}

.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 18px;
}

.platform-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease, opacity 0.2s ease;
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
}

.platform-card.edit-active {
  cursor: grab;
}

.platform-card.edit-active:active {
  cursor: grabbing;
}

.platform-card.is-dragging {
  opacity: 0.45;
  transform: scale(0.97);
}

.platform-card.drag-over {
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--ring);
  transform: scale(1.01);
}

.drag-handle {
  position: absolute;
  top: 12px;
  right: 12px;
  width: 24px;
  height: 24px;
  display: grid;
  place-items: center;
  opacity: 0.4;
  cursor: grab;
}

.drag-handle svg {
  width: 18px;
  height: 18px;
  fill: var(--text);
}

.edit-hint {
  font-size: 0.8rem;
  color: var(--muted);
  text-align: center;
  padding: 8px 0;
  border-top: 1px dashed var(--border);
  margin-top: 8px;
}

.platform-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.platform-card:hover::before {
  transform: scaleX(1);
}

.platform-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-strong);
  border-color: var(--brand);
}

.platform-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 6px;
}

.platform-icon {
  width: 52px;
  height: 52px;
  min-width: 52px;
  aspect-ratio: 1 / 1;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  box-shadow: var(--shadow-soft);
}

.platform-meta h3 {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text);
}

.platform-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.platform-tag {
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.platform-tag.version {
  background: color-mix(in srgb, var(--card) 80%, var(--brand) 20%);
  color: var(--text);
}

.platform-tag.status {
  color: #0f172a;
  background: rgba(148, 163, 184, 0.2);
}

.platform-tag.status.status-live {
  color: #065f46;
  background: rgba(16, 185, 129, 0.2);
}

.platform-tag.status.status-beta {
  color: #9a3412;
  background: rgba(251, 146, 60, 0.25);
}

.platform-tag.status.status-preview {
  color: #7f1d1d;
  background: rgba(248, 113, 113, 0.22);
}

.platform-tag.status.status-maintenance {
  color: #92400e;
  background: rgba(251, 191, 36, 0.25);
}

.platform-tag.status.status-locked {
  color: #991b1b;
  background: rgba(239, 68, 68, 0.2);
}

.platform-tag.notif-badge {
  color: #7c2d12;
  background: rgba(251, 146, 60, 0.26);
}

.platform-tag.badge-warning {
  color: #78350f;
  background: rgba(234, 179, 8, 0.22);
}

.platform-tag.badge-danger {
  color: #7f1d1d;
  background: rgba(239, 68, 68, 0.2);
}

.platform-description {
  color: var(--muted);
  line-height: 1.45;
  margin: 0;
  font-size: 0.95rem;
}

.platform-note {
  margin: 0;
  color: #9a3412;
  font-size: 0.84rem;
  line-height: 1.35;
}

.platform-btn {
  margin-top: auto;
  width: 100%;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white;
  border: none;
  padding: 12px 18px;
  border-radius: 12px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.3s ease;
}

.platform-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(47, 99, 255, 0.3);
}

.arrow-icon {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* Stats Section */
.stats-section {
  padding: 40px 20px;
  background: var(--bg-soft);
}

.stats-grid {
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  box-shadow: var(--shadow-soft);
}

.stat-number {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--brand);
  margin-bottom: 8px;
}

.stat-label {
  color: var(--muted);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  font-size: 0.9rem;
}

/* Responsive - Tablet & Mobile */
@media (max-width: 1024px) {
  .platforms-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 14px;
  }

  .hero-title {
    font-size: clamp(1.8rem, 5vw, 2.5rem);
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 28px 16px;
  }

  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 12px;
  }

  .hero-visual {
    display: none;
  }

  .icon-float {
    font-size: 2rem;
    animation: float 8s ease-in-out infinite;
  }

  .platforms-section {
    padding: 40px 16px;
  }

  .platforms-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .platform-card {
    padding: 18px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-number {
    font-size: 2rem;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .hero-section {
    padding: 24px 12px;
  }

  .hero-title {
    font-size: 1.5rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .platform-card {
    padding: 16px;
    border-radius: 12px;
  }

  .platform-header {
    gap: 12px;
  }

  .platform-icon {
    width: 48px;
    height: 48px;
    font-size: 1.2rem;
  }

  .platform-meta h3 {
    font-size: 1.1rem;
  }

  .platform-btn {
    width: 100%;
    padding: 12px 14px;
    font-size: 0.9rem;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .stat-number {
    font-size: 1.5rem;
  }

  .stat-label {
    font-size: 0.8rem;
  }

  .floating-icons {
    display: none;
  }

  .section-header h2 {
    font-size: 1.3rem;
  }
}

/* Touch devices */
@media (hover: none) {
  .platform-card:active {
    transform: translateY(-4px);
    box-shadow: var(--shadow-strong);
  }

  .platform-btn {
    padding: 14px 20px;
  }
}
</style>
