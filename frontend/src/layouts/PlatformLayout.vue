<template>
  <div class="platform-layout">
    <header class="platform-topbar card">
      <div class="topbar-left">
        <router-link class="brand-link" :to="{ name: 'platforms' }">
          <span class="brand-mark">UNYQ</span>
          <span class="brand-pill">Hub</span>
        </router-link>
        <div class="page-copy">
          <p class="page-kicker">{{ pageKicker }}</p>
          <h1>{{ pageTitle }}</h1>
        </div>
      </div>

      <div class="topbar-actions">
        <button
          class="btn ghost tiny nav-btn"
          type="button"
          @click="router.push({ name: route.name === 'platforms' ? 'dashboard' : 'platforms' })"
        >
          {{ route.name === "platforms" ? "Zum Dashboard" : "Zum Hub" }}
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

    <main class="platform-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const route = useRoute();
const { profile: me, fetchProfile, clearProfile } = useCurrentProfile();

const open = ref(false);
const theme = ref("light");

const pageMeta = {
  platforms: { title: "UNYQ Hub", kicker: "Plattformen und Tools" },
  "platform-contests": { title: "Contests", kicker: "Wettbewerbe und Chancen" },
  "platform-music": { title: "Music Manager", kicker: "Musikplanung und Releases" },
  "platform-locations": { title: "Locations", kicker: "Orte, Events und Buchungen" },
  "platform-finance": { title: "Finance", kicker: "Finanzprojekt anlegen" },
  finance: { title: "Finanzplaner", kicker: "Budget, Schulden und Monatsbild" },
  "platform-fitness": { title: "Fitness", kicker: "Tracker und Essensideen" },
  fitness: { title: "Fitness Tracker", kicker: "Kalorien und Tagesprofil" },
};

const pageMetaCurrent = computed(() => pageMeta[route.name] || { title: "UNYQ", kicker: "Plattform" });
const pageTitle = computed(() => pageMetaCurrent.value.title);
const pageKicker = computed(() => pageMetaCurrent.value.kicker);
const initial = computed(() => {
  const source = me.value?.name || me.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});
const themeLabel = computed(() => (theme.value === "dark" ? "Dark" : "Light"));

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
    if (storedTheme) {
      theme.value = storedTheme;
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
  background: rgba(8, 19, 47, 0.82);
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  font-weight: 700;
  white-space: nowrap;
}

.brand-pill {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(47, 99, 255, 0.12);
  color: var(--brand);
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.page-copy {
  min-width: 0;
}

.page-kicker {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--brand);
}

.page-copy h1 {
  margin: 2px 0 0;
  font-size: clamp(20px, 2.4vw, 26px);
  line-height: 1.1;
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

@media (max-width: 720px) {
  .platform-topbar {
    padding: 12px 16px;
    flex-direction: column;
    align-items: stretch;
  }

  .topbar-left,
  .topbar-actions {
    width: 100%;
  }

  .topbar-left {
    flex-direction: column;
    align-items: flex-start;
  }

  .topbar-actions {
    justify-content: flex-end;
  }

  .platform-content {
    padding: 16px;
  }
}
</style>
