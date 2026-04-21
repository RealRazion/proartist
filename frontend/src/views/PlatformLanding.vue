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
        <h2>Plattformen</h2>
        <p>Entdecke alle verfügbaren Tools und Bereiche</p>
      </div>

      <div class="platforms-grid">
        <div
          v-for="platform in visiblePlatforms"
          :key="platform.key"
          class="platform-card"
          role="article"
          :aria-label="`${platform.title} - ${platform.category}`"
          @click="openPlatform(platform.key)"
        >
          <div class="platform-header">
            <div class="platform-icon" aria-hidden="true">{{ platform.icon }}</div>
            <div class="platform-meta">
              <h3>{{ platform.title }}</h3>
              <span class="platform-tag">{{ platform.category }}</span>
            </div>
          </div>
          <p class="platform-description">{{ platform.description }}</p>
          <div class="platform-features">
            <span v-for="feature in platform.features" :key="feature" class="feature-tag">
              {{ feature }}
            </span>
          </div>
          <button 
            class="platform-btn"
            :aria-label="`${platform.buttonLabel}: ${platform.title}`"
            :title="`${platform.buttonLabel}: ${platform.description}`"
          >
            {{ platform.buttonLabel }}
            <svg class="arrow-icon" viewBox="0 0 24 24" aria-hidden="true">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
          </button>
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

const router = useRouter();
const { showToast } = useToast();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const viewMode = ref("default");

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

const platforms = [
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
    roles: ["TEAM", "ARTIST", "PRODUCER", "LOCATION"],
    comingSoon: false,
  },
  {
    key: "contests",
    title: "UNYQ Contests",
    category: "Wettbewerbe",
    description: "Beteilige dich an Contests, Challenges und gewinne Preise für deine Kunst.",
    buttonLabel: "Entdecken",
    icon: "🏆",
    features: ["Contests", "Challenges", "Preise"],
    roles: ["TEAM", "ARTIST", "PRODUCER"],
    comingSoon: true,
  },
  {
    key: "music",
    title: "Music Manager",
    category: "Musik",
    description: "Verwalte deine Songs, Alben und Releases in einem professionellen Music Manager.",
    buttonLabel: "Verwalten",
    icon: "🎵",
    features: ["Songs", "Releases", "Analytics"],
    roles: ["TEAM", "ARTIST", "PRODUCER"],
    comingSoon: false,
  },
  {
    key: "locations",
    title: "Locations",
    category: "Events",
    description: "Finde und verwalte Locations für deine Events und Auftritte.",
    buttonLabel: "Suchen",
    icon: "📍",
    features: ["Locations", "Events", "Buchungen"],
    roles: ["TEAM", "LOCATION", "PRODUCER"],
    comingSoon: true,
  },
  {
    key: "finance",
    title: "Finance Planner",
    category: "Finanzen",
    description: "Plane dein Budget, verwalte Einnahmen und Ausgaben, tilge Schulden effizient.",
    buttonLabel: "Planen",
    icon: "💰",
    features: ["Budget", "Schulden", "Einnahmen"],
    roles: ["TEAM"],
    comingSoon: false,
  },
  {
    key: "content-studio",
    title: "Content Studio",
    category: "Content",
    description: "Erstelle zentral Tipps, News und Plugin Tutorials fÜr alle Nutzerbereiche.",
    buttonLabel: "Erstellen",
    icon: "📝",
    features: ["Tipps", "News", "Tutorials"],
    roles: ["TEAM"],
    comingSoon: false,
  },
  {
    key: "fitness",
    title: "Fitness Tracker",
    category: "Health",
    description: "Tracke Kalorien, schaetze deinen Tagesverbrauch und finde einfache Essensideen fÜr jede Mahlzeit.",
    buttonLabel: "Starten",
    icon: "🏋️",
    features: ["Kcal", "Verbrauch", "Essensideen"],
    roles: ["TEAM", "ARTIST", "PROD", "VIDEO", "MERCH", "MKT", "LOC"],
    comingSoon: false,
  },
  {
    key: "admin",
    title: "Admin Control Hub",
    category: "Verwaltung",
    description: "Zentrales Verwaltungszentrum für alle UNYQ-Plattformen und Nutzer.",
    buttonLabel: "Verwalten",
    icon: "🔧",
    features: ["Nutzer", "Plattformen", "Sicherheit"],
    roles: ["TEAM"],
    comingSoon: false,
  },
];

const activeRole = computed(() => {
  if (viewMode.value !== "default") return viewMode.value;
  if (isTeam.value) return "TEAM";
  const role = (me.value?.roles || []).find((roleItem) => roleItem.key !== "TEAM");
  return role?.key || "ARTIST";
});

const visiblePlatforms = computed(() => {
  const currentRole = activeRole.value;
  return platforms.filter((platform) => platform.roles.includes(currentRole));
});

function openPlatform(platform) {
  const mapping = {
    dashboard: "/app/dashboard",
    contests: "/platforms/contests",
    music: "/platforms/music",
    locations: "/platforms/locations",
    finance: "/platforms/finance",
    "content-studio": "/platforms/content-studio",
    fitness: "/platforms/fitness",
    admin: "/platforms/admin",
  };
  const path = mapping[platform];
  if (path) {
    router.push(path);
    return;
  }
  showToast("Diese Plattform wird bald verfügbar sein", "info");
}

async function loadStats() {
  if (!isTeam.value) return;
  try {
    const [adminRes, tasksRes, eventsRes] = await Promise.all([
      api.get("admin/overview/"),
      api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS,REVIEW" } }),
      api.get("events/", { params: { upcoming: true, limit: 10 } }),
    ]);
    stats.value = {
      totalUsers: adminRes.data.total_users || 0,
      activeProjects: adminRes.data.active_projects || 0,
      pendingTasks: tasksRes.data.length || 0,
      upcomingEvents: eventsRes.data.length || 0,
    };
  } catch (err) {
    console.error("Stats konnten nicht geladen werden", err);
    // Fallback to zeros
    stats.value = { totalUsers: 0, activeProjects: 0, pendingTasks: 0, upcomingEvents: 0 };
  }
}

onMounted(async () => {
  await fetchProfile();
  await loadStats();
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
  padding: 60px 20px;
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
  padding: 60px 20px;
  background: var(--bg);
}

.section-header {
  max-width: 1200px;
  margin: 0 auto 40px;
  text-align: center;
}

.section-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  margin: 0 0 10px;
  color: var(--text);
}

.section-header p {
  font-size: 1.1rem;
  color: var(--muted);
  margin: 0;
}

.platforms-grid {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 30px;
}

.platform-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 32px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: var(--shadow-soft);
  position: relative;
  overflow: hidden;
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
  gap: 16px;
  margin-bottom: 16px;
}

.platform-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  border-radius: 16px;
  display: grid;
  place-items: center;
  font-size: 1.5rem;
  box-shadow: var(--shadow-soft);
}

.platform-meta h3 {
  margin: 0 0 4px;
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text);
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

.platform-description {
  color: var(--muted);
  line-height: 1.6;
  margin: 0 0 20px;
  font-size: 1rem;
}

.platform-features {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 24px;
}

.feature-tag {
  background: var(--bg-soft);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 500;
}

.platform-btn {
  width: 100%;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: white;
  border: none;
  padding: 14px 20px;
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
  max-width: 1200px;
  margin: 0 auto;
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
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 24px;
  }

  .section-header h2 {
    font-size: 1.8rem;
  }

  .hero-title {
    font-size: clamp(1.8rem, 5vw, 2.5rem);
  }
}

@media (max-width: 768px) {
  .hero-section {
    padding: 40px 16px;
  }

  .hero-content {
    grid-template-columns: 1fr;
    text-align: center;
    gap: 24px;
  }

  .hero-visual {
    height: 200px;
    opacity: 0.5;
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
    gap: 16px;
  }

  .platform-card {
    padding: 20px;
  }

  .section-header h2 {
    font-size: 1.5rem;
  }

  .section-header p {
    font-size: 1rem;
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
</style>
