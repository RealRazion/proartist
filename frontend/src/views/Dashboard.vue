<template>
  <div class="dashboard">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />

    <section class="card hero">
      <div>
        <p class="eyebrow">{{ isTeam ? "Team" : `Hi ${greetingName}` }}</p>
        <h1>{{ isTeam ? "Team Dashboard" : "Willkommen zurück" }}</h1>
        <p class="muted">
          {{ isTeam ? "Der wichtigste Stand in wenigen Sekunden." : "Schneller Überblick über dein Profil und deine Projekte." }}
        </p>
      </div>
      <div class="hero-actions">
        <template v-if="isTeam">
          <button class="btn" type="button" @click="goTo('projects')">Projekte</button>
          <button class="btn ghost" type="button" @click="goTo('tasks')">Task Board</button>
        </template>
        <template v-else>
          <button class="btn" type="button" @click="goTo('profiles')">Profile entdecken</button>
          <button class="btn ghost" type="button" @click="goTo('projects')">Meine Projekte</button>
        </template>
        <button class="btn ghost" type="button" @click="refresh">Aktualisieren</button>
      </div>
    </section>

    <section v-if="isTeam" class="card overview">
      <div class="section-head">
        <h2>Überblick</h2>
        <button class="btn ghost tiny" type="button" @click="refresh" :disabled="loading">Neu laden</button>
      </div>
      <div class="overview-grid">
        <div class="stat">
          <span class="label">Projekte aktiv</span>
          <strong>{{ projectSummary.active }}</strong>
          <small class="muted">Archiviert {{ projectSummary.archived }}</small>
        </div>
        <div class="stat">
          <span class="label">Überfällige Tasks</span>
          <strong>{{ overdueTasks.length }}</strong>
          <small class="muted">Nächste 7 Tage {{ upcomingTasks.length }}</small>
        </div>
        <div class="stat">
          <span class="label">Requests offen</span>
          <strong>{{ teamRequests.length }}</strong>
          <small class="muted">Heute priorisieren</small>
        </div>
        <div class="stat">
          <span class="label">GrowPro fällig</span>
          <strong>{{ growProDueSoon }}</strong>
          <small class="muted">Überfällig {{ growProOverdue }}</small>
        </div>
      </div>
    </section>

    <section v-if="isTeam" class="grid">
      <div class="card focus">
        <div class="section-head">
          <h2>Tasks Fokus</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Zum Board</button>
        </div>
        <div class="task-columns">
          <div>
            <h3>Überfällig</h3>
            <ul v-if="topOverdueTasks.length" class="list">
              <li v-for="task in topOverdueTasks" :key="`overdue-${task.id}`">
                <div class="row">
                  <strong>{{ task.title }}</strong>
                  <span class="badge danger">{{ formatTaskDate(task.due_date) }}</span>
                </div>
                <small class="muted">{{ taskProjectLabel(task) }}</small>
              </li>
            </ul>
            <p v-else class="muted small">Keine überfälligen Tasks.</p>
          </div>
          <div>
            <h3>Nächste 7 Tage</h3>
            <ul v-if="topUpcomingTasks.length" class="list">
              <li v-for="task in topUpcomingTasks" :key="`upcoming-${task.id}`">
                <div class="row">
                  <strong>{{ task.title }}</strong>
                  <span class="badge">{{ formatTaskDate(task.due_date) }}</span>
                </div>
                <small class="muted">{{ taskProjectLabel(task) }}</small>
              </li>
            </ul>
            <p v-else class="muted small">Keine anstehenden Aufgaben.</p>
          </div>
        </div>
      </div>

      <div class="card focus">
        <div class="section-head">
          <h2>Requests</h2>
          <button class="btn ghost tiny" type="button" @click="loadTeamRequests" :disabled="loadingRequests">
            {{ loadingRequests ? "Lade..." : "Neu laden" }}
          </button>
        </div>
        <ul v-if="topRequests.length" class="list">
          <li v-for="request in topRequests" :key="request.id">
            <div class="row">
              <div class="flex-1">
                <strong>{{ requestTypeLabel(request.req_type) }}</strong>
                <p class="muted small">{{ request.sender_name }} → {{ request.receiver_name }}</p>
                <p v-if="request.message" class="muted small">{{ request.message }}</p>
              </div>
              <div class="request-actions">
                <button class="btn ghost tiny" type="button" @click="respondRequest(request.id, 'accept')">
                  Annehmen
                </button>
                <button class="btn ghost danger tiny" type="button" @click="respondRequest(request.id, 'decline')">
                  Ablehnen
                </button>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="muted small">Keine offenen Requests.</p>
      </div>

      <div class="card focus">
        <div class="section-head">
          <h2>Aktivitäten</h2>
          <button class="btn ghost tiny" type="button" @click="loadActivity" :disabled="loadingActivity">
            {{ loadingActivity ? "Lade..." : "Neu laden" }}
          </button>
        </div>
        <ul v-if="topActivities.length" class="list">
          <li v-for="item in topActivities" :key="item.id">
            <div class="row">
              <span class="badge activity-type">{{ activityIcon(item.event_type) }}</span>
              <div class="flex-1">
                <strong>{{ item.title }}</strong>
                <p class="muted small">{{ item.description || item.event_type }}</p>
              </div>
              <small class="muted">{{ formatDateTime(item.created_at) }}</small>
            </div>
          </li>
        </ul>
        <p v-else class="muted small">Keine Aktivitäten vorhanden.</p>
      </div>
    </section>

    <section v-if="!isTeam" class="card onboarding">
      <h2>Dein Start</h2>
      <p class="muted">Die wichtigsten Schritte, damit du schnell gefunden wirst.</p>
      <ul class="list">
        <li v-for="item in onboarding" :key="item.label" class="row">
          <span class="check">{{ item.done ? "✓" : "•" }}</span>
          <div class="flex-1">
            <strong>{{ item.label }}</strong>
            <p class="muted small">{{ item.hint }}</p>
          </div>
          <button v-if="item.cta" class="btn ghost tiny" type="button" @click="item.cta.action">
            {{ item.cta.label }}
          </button>
        </li>
      </ul>
    </section>

    <section v-if="!isTeam" class="card project-overview">
      <div class="section-head">
        <h2>Meine Projekte</h2>
        <button class="btn ghost tiny" type="button" @click="goTo('projects')">Alle Projekte</button>
      </div>
      <ul v-if="projects.length" class="list">
        <li v-for="project in projects.slice(0, 6)" :key="project.id">
          <div class="row">
            <router-link class="project-link" :to="{ name: 'project-detail', params: { projectId: project.id } }">
              <strong>{{ project.title }}</strong>
            </router-link>
            <span class="badge">{{ statusLabel(project.status) }}</span>
          </div>
          <p class="muted small">{{ project.description || "Keine Beschreibung vorhanden." }}</p>
        </li>
      </ul>
      <p v-else class="muted small">Noch keine Projekte.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();

const examples = ref([]);
const projects = ref([]);
const projectSummary = ref({ total: 0, archived: 0, active: 0, done: 0, by_status: {} });

const overdueTasks = ref([]);
const upcomingTasks = ref([]);
const teamRequests = ref([]);
const loadingRequests = ref(false);
const growProGoals = ref([]);
const activities = ref([]);
const loadingActivity = ref(false);
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

const statusLabelMap = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Abgeschlossen",
  ON_HOLD: "Pausiert",
  OPEN: "Offen",
  ACCEPTED: "Angenommen",
  DECLINED: "Abgelehnt",
};

const requestTypeLabels = { COLLAB: "Collab", BOOK: "Booking", OTHER: "Andere" };

const growProDueSoon = computed(() => {
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  return (growProGoals.value || []).filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    const diff = due - now;
    return diff >= 0 && diff < oneDay;
  }).length;
});

const growProOverdue = computed(() => {
  const now = Date.now();
  return (growProGoals.value || []).filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    return due < now;
  }).length;
});

const topOverdueTasks = computed(() => overdueTasks.value.slice(0, 4));
const topUpcomingTasks = computed(() => upcomingTasks.value.slice(0, 4));
const topRequests = computed(() => teamRequests.value.slice(0, 5));
const topActivities = computed(() => activities.value.slice(0, 6));

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

async function loadProjects() {
  try {
    const { data } = await api.get("projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    projects.value = [];
  }
}

async function loadProjectSummary() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("projects/summary/");
    projectSummary.value = {
      total: data.total || 0,
      archived: data.archived || 0,
      active: data.active || 0,
      done: data.done || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    projectSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {} };
  }
}

async function loadOverdueTasks() {
  if (!isTeam.value) {
    overdueTasks.value = [];
    return;
  }
  try {
    const { data } = await api.get("tasks/overdue/");
    overdueTasks.value = data || [];
  } catch (err) {
    console.error("Überfällige Tasks konnten nicht geladen werden", err);
    overdueTasks.value = [];
  }
}

async function loadUpcomingTasks() {
  if (!isTeam.value) {
    upcomingTasks.value = [];
    return;
  }
  try {
    const { data } = await api.get("tasks/upcoming/", { params: { days: 7, limit: 6 } });
    upcomingTasks.value = data || [];
  } catch (err) {
    console.error("Anstehende Tasks konnten nicht geladen werden", err);
    upcomingTasks.value = [];
  }
}

async function loadTeamRequests() {
  if (!isTeam.value) {
    teamRequests.value = [];
    return;
  }
  loadingRequests.value = true;
  try {
    const { data } = await api.get("requests/team-open/");
    teamRequests.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Anfragen konnten nicht geladen werden", err);
    teamRequests.value = [];
  } finally {
    loadingRequests.value = false;
  }
}

async function loadGrowProGoals() {
  if (!isTeam.value) {
    growProGoals.value = [];
    return;
  }
  try {
    const { data } = await api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } });
    const payload = data || {};
    growProGoals.value = Array.isArray(payload) ? payload : payload.results || [];
  } catch (err) {
    console.error("GrowPro konnte nicht geladen werden", err);
    growProGoals.value = [];
  }
}

async function loadActivity() {
  if (!isTeam.value) {
    activities.value = [];
    return;
  }
  loadingActivity.value = true;
  try {
    const { data } = await api.get("activity/", { params: { limit: 12 } });
    activities.value = data || [];
  } catch (err) {
    activities.value = [];
  } finally {
    loadingActivity.value = false;
  }
}

async function respondRequest(id, action) {
  if (!isTeam.value) return;
  const endpoint = action === "accept" ? "accept" : "decline";
  try {
    await api.post(`requests/${id}/${endpoint}/`);
    await loadTeamRequests();
    showToast(action === "accept" ? "Request angenommen" : "Request abgelehnt", "success");
  } catch (err) {
    console.error("Request-Aktion fehlgeschlagen", err);
    showToast("Aktion fehlgeschlagen", "error");
  }
}

async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);
    if (isTeam.value) {
      await Promise.all([
        loadProjectSummary(),
        loadOverdueTasks(),
        loadUpcomingTasks(),
        loadTeamRequests(),
        loadGrowProGoals(),
        loadActivity(),
      ]);
    } else {
      await Promise.all([loadExamples(), loadProjects()]);
    }
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await Promise.all([
      loadProjectSummary(),
      loadOverdueTasks(),
      loadUpcomingTasks(),
      loadTeamRequests(),
      loadGrowProGoals(),
      loadActivity(),
    ]);
  } else {
    await Promise.all([loadExamples(), loadProjects()]);
  }
});

function statusLabel(status) {
  return statusLabelMap[status] || status;
}

function requestTypeLabel(type) {
  return requestTypeLabels[type] || type;
}

function formatTaskDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function taskProjectLabel(task) {
  return task.project_title || `Projekt #${task.project}`;
}

function activityIcon(type) {
  if (!type) return "*";
  if (type.startsWith("song")) return "S";
  if (type.startsWith("growpro")) return "G";
  if (type.startsWith("task")) return "T";
  if (type.startsWith("request")) return "R";
  return "*";
}

function formatDateTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 100%;
}
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.eyebrow {
  margin: 0 0 4px;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.14em;
  color: var(--brand);
  font-weight: 600;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
  margin-top: 10px;
}
.stat {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  background: rgba(255, 255, 255, 0.9);
}
.stat .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.stat strong {
  font-size: 22px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.task-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
  margin-top: 10px;
}
.list {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.flex-1 {
  flex: 1;
}
.badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}
.badge.danger {
  background: rgba(248, 113, 113, 0.18);
  color: #b91c1c;
}
.badge.activity-type {
  background: rgba(15, 23, 42, 0.08);
  color: #0f172a;
}
.request-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.project-link {
  color: inherit;
  text-decoration: none;
}
.project-link:hover {
  text-decoration: underline;
}
.check {
  font-size: 16px;
  width: 18px;
  text-align: center;
}
@media (max-width: 760px) {
  .hero-actions {
    justify-content: flex-start;
  }
  .row {
    flex-direction: column;
    align-items: flex-start;
  }
  .request-actions {
    justify-content: flex-start;
  }
}
</style>
