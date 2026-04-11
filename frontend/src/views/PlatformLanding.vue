<template>
  <div class="platform-landing">
    <header class="hero card">
      <div class="hero-copy">
        <p class="tag">UNYQ Hub</p>
        <h1>Der neue Einstiegspunkt für deine UNYQ-Welten</h1>
        <p class="lead">
          Starte hier in die verschiedenen UNYQ-Plattformen. Je nach Rolle werden nur die passenden Bereiche angezeigt.
        </p>
      </div>
      <div v-if="isTeam" class="preview-panel card">
        <strong>Team-Perspektive</strong>
        <p class="muted">Als Team-Mitglied kannst du hier den Hub in anderen Rollen ansehen.</p>
        <div class="role-pills">
          <button
            v-for="option in previewOptions"
            :key="option.key"
            type="button"
            class="pill"
            :class="{ active: viewMode === option.key }"
            @click="setViewMode(option.key)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </header>

    <section class="platform-grid">
      <article
        v-for="card in visibleCards"
        :key="card.key"
        :class="['platform-card', `platform-card--${card.key}`, 'card']"
      >
        <div class="platform-head">
          <div class="platform-icon" :class="`platform-icon--${card.key}`">
            {{ card.icon }}
          </div>
          <span class="card-label">{{ card.title }}</span>
        </div>
        <div>
          <h2>{{ card.heading }}</h2>
          <p>{{ card.description }}</p>
        </div>
        <button class="btn" type="button" @click="openPlatform(card.key)">
          {{ card.buttonLabel }}
        </button>
      </article>
    </section>

    <footer class="platform-note card">
      <p>
        Der Hub ist dein zentraler Ausgangspunkt. Für Team-Mitglieder gibt es eine Vorschau auf andere Rollen,
        damit du den gleichen Einstieg wie ein Artist oder Producer sehen kannst.
      </p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const { showToast } = useToast();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const viewMode = ref("default");
const previewOptions = [
  { key: "default", label: "Eigene Ansicht" },
  { key: "ARTIST", label: "Als Artist" },
  { key: "PRODUCER", label: "Als Producer" },
  { key: "LOCATION", label: "Als Location" },
];

const cards = [
  {
    key: "dashboard",
    title: "Dashboard",
    heading: "Dein persönlicher Hub",
    description: "Ein anpassbares Dashboard für deine Rolle – Team oder Artist.",
    buttonLabel: "Zum Dashboard",
    icon: "📊",
    roles: ["TEAM", "ARTIST", "PRODUCER", "LOCATION"],
  },
  {
    key: "contests",
    title: "UNYQ Contests",
    heading: "Wettbewerbe & Challenges",
    description: "Bewerbe dich für Auftritte, Challenges und Team-Aktionen.",
    buttonLabel: "Zur Contest-Plattform",
    icon: "🏆",
    roles: ["TEAM", "ARTIST", "PRODUCER"],
  },
  {
    key: "music",
    title: "UNYQ Music Manager",
    heading: "Musikprojekte & Releases",
    description: "Verwalte Songs, Projekte und Releases in einer klaren Musikübersicht.",
    buttonLabel: "Zum Music Manager",
    icon: "🎵",
    roles: ["TEAM", "ARTIST", "PRODUCER"],
  },
  {
    key: "locations",
    title: "UNYQ Locations",
    heading: "Locations & Events",
    description: "Verwalte Orte, Termine und Veranstaltungsoptionen für dein Team.",
    buttonLabel: "Zu Locations",
    icon: "📍",
    roles: ["TEAM", "LOCATION", "PRODUCER"],
  },
];

const activeRole = computed(() => {
  if (viewMode.value !== "default") return viewMode.value;
  if (isTeam.value) return "TEAM";
  const role = (me.value?.roles || []).find((roleItem) => roleItem.key !== "TEAM");
  return role?.key || "ARTIST";
});

const visibleCards = computed(() => {
  const currentRole = activeRole.value;
  return cards.filter((card) => card.roles.includes(currentRole));
});

function setViewMode(mode) {
  viewMode.value = mode;
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("unyq:platform-view-mode", mode);
  }
}

function openPlatform(platform) {
  const mapping = {
    dashboard: "/app/dashboard",
    contests: "/platforms/contests",
    music: "/platforms/music",
    locations: "/platforms/locations",
  };
  const path = mapping[platform];
  if (path) {
    router.push(path);
    return;
  }
  showToast("Diese Plattform wird bald verfügbar sein", "info");
}

onMounted(async () => {
  if (typeof window !== "undefined") {
    const stored = localStorage.getItem("unyq:platform-view-mode");
    if (stored) viewMode.value = stored;
  }
  await fetchProfile();
});
</script>

<style scoped>
.platform-landing {
  max-width: 1080px;
  margin: 0 auto;
  padding: 36px 20px 60px;
}

.hero {
  display: grid;
  gap: 24px;
  grid-template-columns: 1fr;
  padding: 32px;
  background: linear-gradient(135deg, rgba(47, 99, 255, 0.16), rgba(6, 182, 212, 0.12));
  border: 1px solid rgba(47, 99, 255, 0.18);
}

.tag {
  display: inline-flex;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(6, 182, 212, 0.14);
  color: var(--brand);
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 2.6vw, 3rem);
  line-height: 1.05;
}

.lead {
  margin: 0;
  max-width: 720px;
  color: var(--muted);
  line-height: 1.72;
}

.preview-panel {
  padding: 20px 24px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: rgba(255, 255, 255, 0.95);
}

.preview-panel strong {
  display: block;
  margin-bottom: 10px;
  font-size: 16px;
}

.preview-panel .muted {
  margin: 0 0 16px;
  color: var(--muted);
}

.role-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pill {
  border: 1px solid rgba(47, 99, 255, 0.18);
  background: rgba(255, 255, 255, 0.95);
  color: var(--text);
  padding: 10px 16px;
  border-radius: 999px;
  cursor: pointer;
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.pill:hover,
.pill.active {
  border-color: var(--brand);
  background: rgba(47, 99, 255, 0.12);
  transform: translateY(-1px);
}

.platform-grid {
  display: grid;
  gap: 20px;
  margin-top: 28px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.platform-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 280px;
  gap: 20px;
  padding: 28px;
  border: 1px solid rgba(47, 99, 255, 0.14);
  background: rgba(255, 255, 255, 0.92);
}

.platform-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.platform-icon {
  width: 52px;
  height: 52px;
  border-radius: 18px;
  display: grid;
  place-items: center;
  font-size: 22px;
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.35);
}

.platform-icon--contests {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.22), rgba(99, 102, 241, 0.16));
}

.platform-icon--music {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.22), rgba(34, 211, 238, 0.16));
}

.platform-icon--locations {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.22), rgba(52, 211, 153, 0.16));
}

.platform-card--contests {
  background: rgba(47, 99, 255, 0.06);
}

.platform-card--music {
  background: rgba(6, 182, 212, 0.06);
}

.platform-card--locations {
  background: rgba(76, 196, 116, 0.08);
}

.card-label {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--brand);
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.platform-card h2 {
  margin: 0;
  font-size: 1.4rem;
}

.platform-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.65;
}

.platform-card .btn {
  width: 100%;
  justify-content: center;
}

.platform-note {
  margin-top: 24px;
  padding: 22px;
  border: 1px solid rgba(47, 99, 255, 0.12);
  background: rgba(247, 250, 255, 0.9);
}

.platform-note p {
  margin: 0;
  color: var(--muted);
}

@media (max-width: 720px) {
  .platform-landing {
    padding: 24px 16px 40px;
  }

  .hero {
    padding: 24px;
  }

  .platform-card {
    padding: 22px;
  }
}
</style>