<template>
  <div class="admin-platform">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">Admin Control Hub</h1>
          <p class="hero-subtitle">
            Zentrales Verwaltungszentrum für alle UNYQ-Plattformen. Verwalte Nutzer, überwache Systeme und steuere Zugriffe.
          </p>
        </div>
        <div class="hero-visual">
          <div class="floating-icons">
            <div class="icon-float icon-1">🔧</div>
            <div class="icon-float icon-2">👥</div>
            <div class="icon-float icon-3">📊</div>
            <div class="icon-float icon-4">🚫</div>
            <div class="icon-float icon-5">✅</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Admin Tools Grid -->
    <section class="tools-section">
      <div class="section-header">
        <h2>Verwaltungstools</h2>
        <p>Direkter Zugriff auf alle administrativen Funktionen</p>
      </div>

      <div class="tools-grid">
        <div
          v-for="tool in adminTools"
          :key="tool.key"
          class="tool-card"
          @click="openTool(tool.key)"
        >
          <div class="tool-header">
            <div class="tool-icon">{{ tool.icon }}</div>
            <div class="tool-meta">
              <h3>{{ tool.title }}</h3>
              <span class="tool-tag">{{ tool.category }}</span>
            </div>
          </div>
          <p class="tool-description">{{ tool.description }}</p>
          <div class="tool-features">
            <span v-for="feature in tool.features" :key="feature" class="feature-tag">
              {{ feature }}
            </span>
          </div>
          <button class="tool-btn">
            {{ tool.buttonLabel }}
            <svg class="arrow-icon" viewBox="0 0 24 24">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
        </div>
      </div>
    </section>

    <!-- System Stats Section -->
    <section class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">{{ systemStats.totalUsers }}</div>
          <div class="stat-label">Gesamt Nutzer</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ systemStats.activeUsers }}</div>
          <div class="stat-label">Aktive Nutzer</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ systemStats.lockedUsers }}</div>
          <div class="stat-label">Gesperrte Nutzer</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ systemStats.pendingRequests }}</div>
          <div class="stat-label">Offene Anfragen</div>
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

const router = useRouter();
const { showToast } = useToast();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const systemStats = ref({
  totalUsers: 0,
  activeUsers: 0,
  lockedUsers: 0,
  pendingRequests: 0,
});

const adminTools = [
  {
    key: "users",
    title: "Nutzer-Management",
    category: "Verwaltung",
    description: "Nutzerkonten verwalten, sperren, entsperren und Rollen zuweisen.",
    buttonLabel: "Verwalten",
    icon: "👥",
    features: ["Sperren", "Rollen", "Profile"],
  },
  {
    key: "platforms",
    title: "Plattform-Kontrolle",
    category: "System",
    description: "Plattformen aktivieren/deaktivieren und Zugriffsrechte steuern.",
    buttonLabel: "Steuern",
    icon: "🌐",
    features: ["Aktivierung", "Zugriffe", "Konfiguration"],
  },
  {
    key: "analytics",
    title: "System Analytics",
    category: "Überwachung",
    description: "Detaillierte Analysen und Berichte über Systemnutzung.",
    buttonLabel: "Überwachen",
    icon: "📊",
    features: ["Berichte", "Metriken", "Trends"],
  },
  {
    key: "security",
    title: "Sicherheits-Center",
    category: "Sicherheit",
    description: "Sicherheitseinstellungen, Logs und Bedrohungsmanagement.",
    buttonLabel: "Sichern",
    icon: "🔒",
    features: ["Logs", "Bedrohungen", "Einstellungen"],
  },
  {
    key: "requests",
    title: "Anfragen-Verwaltung",
    category: "Support",
    description: "Registrierungsanfragen und Support-Tickets bearbeiten.",
    buttonLabel: "Bearbeiten",
    icon: "📝",
    features: ["Anfragen", "Tickets", "Genehmigungen"],
  },
  {
    key: "content",
    title: "Content Studio",
    category: "Kommunikation",
    description: "Tipps, News und Plugin Tutorials zentral erstellen und verwalten.",
    buttonLabel: "Bearbeiten",
    icon: "📝",
    features: ["Tipps", "News", "Tutorials"],
  },
  {
    key: "system",
    title: "System-Einstellungen",
    category: "Konfiguration",
    description: "Globale Systemeinstellungen und Konfigurationen anpassen.",
    buttonLabel: "Konfigurieren",
    icon: "⚙️",
    features: ["Einstellungen", "Konfiguration", "Backups"],
  },
];

function openTool(tool) {
  const mapping = {
    users: "/app/admin",
    platforms: "/platforms/platforms-control",
    analytics: "/app/analytics",
    security: "/platforms/security",
    requests: "/app/admin#requests",
    content: "/platforms/content-studio",
    system: "/platforms/system-settings",
  };
  const path = mapping[tool];
  if (path) {
    router.push(path);
    return;
  }
  showToast("Dieses Tool wird bald verfügbar sein", "info");
}

async function loadSystemStats() {
  try {
    const [adminRes, requestsRes] = await Promise.all([
      api.get("admin/overview/"),
      api.get("registration-requests/"),
    ]);
    systemStats.value = {
      totalUsers: adminRes.data.total_users || 0,
      activeUsers: (adminRes.data.total_users || 0) - (adminRes.data.locked_users || 0),
      lockedUsers: adminRes.data.locked_users || 0,
      pendingRequests: Array.isArray(requestsRes.data) ? requestsRes.data.length : (requestsRes.data.results?.length || 0),
    };
  } catch (err) {
    console.error("System-Stats konnten nicht geladen werden", err);
    systemStats.value = { totalUsers: 0, activeUsers: 0, lockedUsers: 0, pendingRequests: 0 };
  }
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await loadSystemStats();
  }
});
</script>

<style scoped>
.admin-platform {
  min-height: 100vh;
  background: var(--bg);
  color: var(--text);
}

/* Hero Section */
.hero-section {
  padding: 60px 20px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
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
  background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="0.5" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
  opacity: 0.3;
}

.hero-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 40px;
  align-items: center;
  position: relative;
  z-index: 1;
}

.hero-text h1 {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 800;
  margin: 0 0 20px;
  line-height: 1.1;
}

.hero-subtitle {
  font-size: 1.2rem;
  line-height: 1.6;
  opacity: 0.9;
  margin: 0;
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
  font-size: 2rem;
  animation: float 6s ease-in-out infinite;
  opacity: 0.8;
}

.icon-1 { top: 20%; left: 10%; animation-delay: 0s; }
.icon-2 { top: 40%; right: 15%; animation-delay: 1s; }
.icon-3 { bottom: 30%; left: 20%; animation-delay: 2s; }
.icon-4 { top: 10%; right: 10%; animation-delay: 3s; }
.icon-5 { bottom: 20%; right: 20%; animation-delay: 4s; }

@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}

/* Tools Section */
.tools-section {
  padding: 60px 20px;
}

.section-header {
  max-width: 1200px;
  margin: 0 auto 40px;
  text-align: center;
}

.section-header h2 {
  font-size: 2rem;
  font-weight: 700;
  margin: 0 0 8px;
  color: var(--text);
}

.section-header p {
  color: var(--muted);
  font-size: 1.1rem;
}

.tools-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.tool-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  border-color: var(--brand);
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 16px;
}

.tool-icon {
  font-size: 2rem;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--brand-light);
  border-radius: 12px;
  color: var(--brand);
}

.tool-meta h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--text);
}

.tool-tag {
  background: var(--brand);
  color: white;
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.tool-description {
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
}

.tool-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feature-tag {
  background: var(--bg-alt);
  color: var(--text);
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 0.8rem;
  border: 1px solid var(--border);
}

.tool-btn {
  margin-top: auto;
  background: var(--brand);
  color: white;
  border: none;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: background 0.3s ease;
}

.tool-btn:hover {
  background: var(--brand-2);
}

.arrow-icon {
  width: 16px;
  height: 16px;
}

/* Stats Section */
.stats-section {
  padding: 40px 20px;
  background: var(--bg-alt);
}

.stats-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--card-bg);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.stat-number {
  font-size: 2rem;
  font-weight: 800;
  color: var(--brand);
  margin-bottom: 8px;
}

.stat-label {
  color: var(--muted);
  font-weight: 500;
}
</style>
