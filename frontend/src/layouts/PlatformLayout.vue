<template>
  <div class="platform-layout">
    <header v-if="showTopbar" class="platform-topbar card">
      <div class="topbar-left">
        <!-- Clean Brand Title (redundant Hub button removed) -->
        <span class="brand-title-clean">UNYQ</span>

        <!-- Version Number: first two parts bold, rest in thin font -->
        <div class="header-version-badge" :title="'UNYQ Version ' + (APP_VERSION || '2.11.0.7-beta')">
          <strong class="ver-bold">{{ parsedVersion.majorMinor }}</strong><span class="ver-thin">{{ parsedVersion.patchRest }}</span>
        </div>

        <!-- Clickable Text 'Patchnotes' -->
        <button
          type="button"
          class="patchnotes-link-btn"
          @click="openPatchnotes(0)"
          title="Patchnotes anzeigen"
        >
          Patchnotes
        </button>

        <!-- Subpage Context if not on main Hub -->
        <div v-if="route.name !== 'platforms'" class="subpage-context">
          <span class="subpage-slash">/</span>
          <span class="subpage-label">{{ pageTitle }}</span>
        </div>
      </div>

      <div class="topbar-actions">
        <!-- Return to Hub button: only displayed when outside main Hub -->
        <button
          v-if="route.name !== 'platforms'"
          class="btn ghost tiny nav-btn"
          type="button"
          @click="router.push({ name: 'platforms' })"
        >
          Zum Hub
        </button>
        <button class="iconbtn top-icon-btn" type="button" @click="toggleTheme" :title="`Theme: ${themeLabel}`">
          <svg v-if="theme === 'dark'" class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
            <path d="M21 12.79A9 9 0 1 1 11.21 3a7 7 0 0 0 9.79 9.79z" />
          </svg>
          <svg v-else class="toolbar-svg" viewBox="0 0 24 24" aria-hidden="true">
            <circle cx="12" cy="12" r="4.2" />
            <path d="M12 2.5v2.2M12 19.3v2.2M4.9 4.9l1.6 1.6M17.5 17.5l1.6 1.6M2.5 12h2.2M19.3 12h2.2M4.9 19.1l1.6-1.6M17.5 6.5l1.6-1.6" />
          </svg>
        </button>
        <div class="profile" :class="{ open }">
          <button class="avatar" type="button" @click="open = !open">
            {{ initial }}
          </button>
          <div v-if="open" class="menu card">
            <p class="menu-name">{{ me?.name || me?.username }}</p>
            <p class="menu-item" @click="goToProfile">Profil</p>
            <p class="menu-item" @click="router.push({ name: 'dashboard' })">Dashboard</p>
            <p class="menu-item danger" @click="logout">Logout</p>
          </div>
        </div>
      </div>
    </header>

    <main class="platform-content" :class="{ 'hub-content': route.name === 'platforms', 'no-frame': !showTopbar }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { usePlatformVersion } from "../composables/usePlatformVersion";
import { usePatchnotes } from "../composables/usePatchnotes";

const router = useRouter();
const route = useRoute();
const { profile: me, fetchProfile, clearProfile } = useCurrentProfile();
const routeRef = computed(() => route);
const { platformSlug, platformVersion } = usePlatformVersion(routeRef);
const { openPatchnotes, parsedVersion, currentVersion: APP_VERSION } = usePatchnotes();

const open = ref(false);
const theme = ref(typeof window !== "undefined" && localStorage.getItem("theme") === "light" ? "light" : "dark");

const pageMeta = {
  platforms: { title: "UNYQ Hub", kicker: "Plattformen und Tools" },
  "platform-proartist": { title: "UNYQ ProArtist", kicker: "Kreativ-Workspace" },
  "platform-finance": { title: "UNYQ Finance", kicker: "Finanz-Management" },
  finance: { title: "UNYQ Finanzplaner", kicker: "Budget, Schulden und Monatsbild" },
  "platform-earn": { title: "UNYQ Earn", kicker: "Partner & Affiliate Program" },
  "platform-designs": { title: "UNYQ Designs", kicker: "Merchandise & Drops" },
  "platform-music": { title: "UNYQ Music", kicker: "Exklusiver Music Player" },
  "platform-library": { title: "UNYQ Library", kicker: "Open Source Sound Bank" },
  "platform-forum": { title: "UNYQ Forum", kicker: "Community & Diskussionen" },
  "platform-extra": { title: "UNYQ Extra", kicker: "Plattformen & Socials" },
  "platform-contests": { title: "Contests", kicker: "Wettbewerbe und Chancen" },
  "platform-locations": { title: "Locations", kicker: "Orte, Events und Buchungen" },
  "platform-content-studio": { title: "Content Studio", kicker: "Tipps, News und Tutorials" },
  "platform-content-schedule": { title: "ACH Content Schedule", kicker: "Content-Planung" },
  "content-schedule": { title: "ACH Planer", kicker: "Wochenplan Drag & Drop" },
  "platform-plugin-guides": { title: "Plugin Guide", kicker: "Workflows, Tutorials und Setups" },
  "platform-api-center": { title: "API Platform", kicker: "Integrationen und Automationen" },
  "platform-fitness": { title: "Fitness", kicker: "Tracker und Essensideen" },
  fitness: { title: "Fitness Tracker", kicker: "Kalorien und Tagesprofil" },
  "platform-todo": { title: "Todo", kicker: "Todos mit optionalem Datum" },
  "manage-platforms": { title: "Manage Platforms", kicker: "Status und Zugriff steuern" },
  "admin-platform": { title: "Admin Platform", kicker: "Kontrollzentrum" },
};

const pageMetaCurrent = computed(() => pageMeta[route.name] || { title: "UNYQ", kicker: "Plattform" });
const pageTitle = computed(() => pageMetaCurrent.value.title);
const pageKicker = computed(() => pageMetaCurrent.value.kicker);
const showTopbar = computed(() => !route.meta?.hidePlatformTopbar);
const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});
const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));

function applyTheme() {
  const root = document.documentElement;
  const isDark = theme.value !== "light";
  root.classList.toggle("dark", isDark);
  root.classList.toggle("light", !isDark);
  localStorage.setItem("theme", isDark ? "dark" : "light");
}

function toggleTheme() {
  theme.value = theme.value === "dark" ? "light" : "dark";
  applyTheme();
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

watch(
  () => route.fullPath,
  () => {
    open.value = false;
  }
);

onMounted(async () => {
  if (typeof window !== "undefined") {
    const storedTheme = localStorage.getItem("theme");
    if (storedTheme === "light" || storedTheme === "dark") {
      theme.value = storedTheme;
    } else {
      theme.value = "dark";
    }
  }
  applyTheme();
  try {
    await fetchProfile();
  } catch (err) {
    if (err?.response?.status === 401) {
      logout();
    }
  }
});
</script>

<style scoped>
.platform-layout {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

.platform-topbar {
  margin: 0;
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-top: none;
  box-shadow: none;
  border-bottom: 1px solid var(--border);
  background: var(--card);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 14px 20px;
  position: sticky;
  top: 0;
  z-index: 30;
  backdrop-filter: blur(10px);
}

:global(.dark) .platform-topbar {
  background: rgba(8, 19, 47, 0.88);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  flex-wrap: wrap;
}

.brand-title-clean {
  font-size: 19px;
  font-weight: 900;
  letter-spacing: 0.05em;
  color: var(--text);
  user-select: none;
}

:global(.dark) .brand-title-clean {
  color: #ffffff;
}

.header-version-badge {
  display: inline-flex;
  align-items: baseline;
  padding: 3px 8px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.28);
  border-radius: 6px;
  font-size: 12.5px;
  line-height: 1;
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
  margin-left: 1px;
}

.patchnotes-link-btn {
  background: none;
  border: none;
  padding: 3px 6px;
  font-size: 12.5px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
  text-decoration-color: rgba(148, 163, 184, 0.45);
  transition: all 0.18s ease;
  white-space: nowrap;
}

.patchnotes-link-btn:hover {
  color: #ffffff;
  text-decoration-color: #818cf8;
}

.subpage-context {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}

.subpage-slash {
  color: #475569;
  font-weight: 300;
}

.subpage-label {
  font-weight: 600;
  color: #cbd5e1;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.nav-btn {
  white-space: nowrap;
}

.top-icon-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  justify-content: center;
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

.platform-content {
  padding: 20px;
}

.platform-content.hub-content {
  padding: 0;
}

.platform-content.no-frame {
  padding: 0;
}

@media (max-width: 720px) {
  .platform-topbar {
    padding: 12px 16px;
    flex-wrap: wrap;
    align-items: center;
    position: static;
    top: auto;
    backdrop-filter: none;
  }

  .topbar-left,
  .topbar-actions {
    width: auto;
  }

  .topbar-left {
    flex: 1 1 100%;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
  }

  .topbar-actions {
    margin-left: auto;
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .platform-content {
    padding: 16px;
  }

  .page-kicker {
    display: none;
  }

  .page-copy h1 {
    font-size: clamp(18px, 5.6vw, 22px);
  }
}

@media (max-width: 560px) {
  .topbar-left {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-actions {
    width: 100%;
    margin-left: 0;
    justify-content: flex-start;
  }

  .nav-btn {
    width: 100%;
  }
}
</style>
