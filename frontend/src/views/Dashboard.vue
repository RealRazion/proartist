<template>
  <div class="dashboard">
    <section class="card welcome">
      <div>
        <p class="eyebrow">Hi {{ greetingName }}</p>
        <h1>Willkommen zurück bei ProArtist</h1>
        <p class="muted">
          {{ isTeam ? "Behalte Team, Projekte und Requests im Blick." : "Mach dein Profil sichtbar und starte neue Kollaborationen." }}
        </p>
      </div>
      <button class="btn ghost" type="button" @click="refresh">
        Aktualisieren
      </button>
    </section>

    <section v-if="isTeam" class="kpi-grid">
      <div class="card kpi" v-for="kpi in teamKpis" :key="kpi.label">
        <div class="kpi-icon">{{ kpi.icon }}</div>
        <div>
          <p class="kpi-label">{{ kpi.label }}</p>
          <strong class="kpi-value">{{ kpi.value }}</strong>
        </div>
      </div>
    </section>

    <section v-else class="card checklist">
      <h2>Onboarding</h2>
      <p class="muted">Vervollständige dein Profil, damit andere dich schneller finden.</p>
      <ul>
        <li v-for="item in onboarding" :key="item.label">
          <span class="check">{{ item.done ? "✅" : "⬜" }}</span>
          <div>
            <p>{{ item.label }}</p>
            <small class="muted">{{ item.hint }}</small>
          </div>
          <button v-if="item.cta" class="btn ghost" type="button" @click="item.cta.action">
            {{ item.cta.label }}
          </button>
        </li>
      </ul>
    </section>

    <section v-if="!isTeam && projects.length" class="card project-overview">
      <h2>Meine Projekte</h2>
      <ul>
        <li v-for="project in projects" :key="project.id">
          <div class="project-title">
            <strong>{{ project.title }}</strong>
            <span class="status-pill" :data-status="project.status">{{ statusLabel(project.status) }}</span>
          </div>
          <p class="muted">{{ project.description || "Keine Beschreibung vorhanden." }}</p>
        </li>
      </ul>
      <p v-if="!projects.length" class="muted empty">Noch keine Projekte.</p>
    </section>

    <section class="card quick-actions">
      <h2>Schnellaktionen</h2>
      <div class="actions">
        <button class="btn" type="button" @click="goTo('profiles')">Profile entdecken</button>
        <button class="btn ghost" type="button" @click="goTo('chats')">Chat öffnen</button>
        <button v-if="isTeam" class="btn ghost" type="button" @click="goTo('projects')">Neues Projekt</button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const stats = ref({
  roles: {},
  open_requests: 0,
  active_contracts: 0,
  due_payments: 0,
});
const examples = ref([]);
const projects = ref([]);
const loading = ref(false);

const greetingName = computed(() => me.value?.name || me.value?.username || "Artist");
const hasRoles = computed(() => (me.value?.roles || []).length > 0);
const hasExample = computed(() => examples.value.length > 0);

const onboarding = computed(() => [
  {
    label: "Profilinformationen vervollständigen",
    hint: "Name, Genre, Stadt und Social Links helfen beim Matching.",
    done: Boolean(me.value?.name && me.value?.city),
    cta: { label: "Profil bearbeiten", action: () => goTo("me") },
  },
  {
    label: "Rollen auswählen",
    hint: "Wähle aus, welche Rolle du im Netzwerk einnehmen möchtest.",
    done: hasRoles.value,
    cta: hasRoles.value ? null : { label: "Rollen wählen", action: () => goTo("me") },
  },
  {
    label: "Mindestens ein Beispiel teilen",
    hint: "Füge einen Track, ein Video oder ein Dokument hinzu.",
    done: hasExample.value,
    cta: hasExample.value ? null : { label: "Beispiel hochladen", action: () => goTo("me") },
  },
]);

const teamKpis = computed(() => [
  { icon: "🎤", label: "Artists", value: stats.value.roles.ARTIST || 0 },
  { icon: "🎚️", label: "Producer", value: stats.value.roles.PROD || 0 },
  { icon: "📝", label: "Aktive Verträge", value: stats.value.active_contracts || 0 },
  { icon: "💸", label: "Offene Zahlungen", value: stats.value.due_payments || 0 },
  { icon: "📨", label: "Offene Anfragen", value: stats.value.open_requests || 0 },
]);

function goTo(name) {
  router.push({ name });
}

async function loadExamples() {
  if (!me.value?.id) return;
  try {
    const { data } = await api.get("examples/", { params: { profile: me.value.id } });
    examples.value = data.filter((item) => item.profile === me.value.id);
  } catch (err) {
    console.error("Beispiele konnten nicht geladen werden", err);
    examples.value = [];
  }
}

async function loadStats() {
  try {
    const { data } = await api.get("stats/");
    stats.value = data;
  } catch (err) {
    console.error("Statistiken konnten nicht geladen werden", err);
  }
}

async function loadProjects() {
  try {
    const { data } = await api.get("projects/");
    projects.value = data;
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    projects.value = [];
  }
}

async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);
    const loaders = [loadStats(), loadExamples()];
    if (!isTeam.value) loaders.push(loadProjects());
    await Promise.all(loaders);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  const loaders = [loadStats(), loadExamples()];
  if (!isTeam.value) loaders.push(loadProjects());
  await Promise.all(loaders);
});

function statusLabel(status) {
  const map = {
    PLANNED: "Geplant",
    IN_PROGRESS: "In Arbeit",
    REVIEW: "Review",
    DONE: "Abgeschlossen",
    ON_HOLD: "Pausiert",
  };
  return map[status] || status;
}
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 20px;
  width: 100%;
}
.welcome {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
}
.welcome .muted {
  margin: 8px 0 0;
}
.eyebrow {
  margin: 0;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--brand);
  font-weight: 600;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.kpi {
  display: flex;
  align-items: center;
  gap: 16px;
}
.kpi-icon {
  width: 46px;
  height: 46px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 22px;
}
.kpi-label {
  margin: 0;
  color: var(--muted);
}
.kpi-value {
  font-size: 1.6rem;
}
.checklist ul {
  list-style: none;
  padding: 0;
  margin: 16px 0 0;
  display: grid;
  gap: 12px;
}
.checklist li {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 12px;
  align-items: center;
}
.check {
  font-size: 20px;
}
.quick-actions .actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 12px;
}
.project-overview ul {
  list-style: none;
  padding: 0;
  margin: 12px 0 0;
  display: grid;
  gap: 12px;
}
.project-overview li {
  border: 1px solid rgba(75, 91, 255, 0.12);
  border-radius: 12px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.project-title {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: space-between;
}
.status-pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.04em;
  background: rgba(75, 91, 255, 0.18);
  color: var(--brand);
}
.status-pill[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.16);
  color: #ea580c;
}
.status-pill[data-status="DONE"] {
  background: rgba(52, 211, 153, 0.16);
  color: #059669;
}
.status-pill[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
.project-overview .empty {
  margin: 0;
}

@media (max-width: 760px) {
  .welcome {
    flex-direction: column;
    align-items: flex-start;
  }
  .checklist li {
    grid-template-columns: auto 1fr;
    gap: 10px;
  }
  .checklist li .btn {
    grid-column: span 2;
    justify-self: flex-start;
  }
}
</style>
