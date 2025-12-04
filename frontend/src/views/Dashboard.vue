<template>
  <div class="dashboard">
    <section v-if="isTeam" class="card team-hero">
      <div>
        <p class="eyebrow">Team</p>
        <h1>Team Dashboard</h1>
        <p class="muted">Schneller Überblick über Todos, Projekte und Anfragen.</p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="goTo('projects')">Projekt anlegen</button>
        <button class="btn ghost" type="button" @click="goTo('tasks')">Task Board</button>
        <button class="btn ghost" type="button" @click="goTo('profiles')">Profile scannen</button>
        <button class="btn ghost" type="button" @click="refresh">Aktualisieren</button>
      </div>
    </section>

    <section v-else class="card welcome">
      <div>
        <p class="eyebrow">Hi {{ greetingName }}</p>
        <h1>Willkommen zurück bei ProArtist</h1>
        <p class="muted">
          Mach dein Profil sichtbar und starte neue Kollaborationen.
        </p>
      </div>
      <button class="btn ghost" type="button" @click="refresh">Aktualisieren</button>
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

    <section v-if="!isTeam" class="card quick-actions">
      <h2>Schnellaktionen</h2>
      <div class="actions">
        <button class="btn" type="button" @click="goTo('profiles')">Profile entdecken</button>
        <button class="btn ghost" type="button" @click="goTo('chats')">Chat öffnen</button>
        <button class="btn ghost" type="button" @click="goTo('projects')">Neues Projekt</button>
      </div>
    </section>

    <section v-if="isTeam" class="card deadlines">
      <div class="deadlines-head">
        <div>
          <h2>Fristen im Blick</h2>
          <p class="muted">Überfällige und anstehende Tasks sortiert nach Fälligkeit.</p>
        </div>
        <div class="head-actions">
          <button class="btn ghost tiny" type="button" @click="loadOverdueTasks" :disabled="loadingOverdue">
            {{ loadingOverdue ? "Aktualisiere..." : "Überfällig laden" }}
          </button>
          <button class="btn ghost tiny" type="button" @click="loadUpcomingTasks" :disabled="loadingUpcoming">
            {{ loadingUpcoming ? "Aktualisiere..." : "Nächste Woche laden" }}
          </button>
        </div>
      </div>
      <div class="deadlines-grid">
        <div class="deadline-column">
          <header>
            <h3>Überfällig</h3>
            <small>{{ overdueTasks.length }} Tasks</small>
          </header>
          <ul v-if="overdueTasks.length">
            <li v-for="task in overdueTasks" :key="`overdue-${task.id}`">
              <div class="row">
                <strong>{{ task.title }}</strong>
                <span class="badge danger">{{ formatTaskDate(task.due_date) }}</span>
              </div>
              <p class="muted">{{ taskProjectLabel(task) }}</p>
            </li>
          </ul>
          <p v-else class="muted empty">Keine überfälligen Tasks 🎉</p>
        </div>
        <div class="deadline-column">
          <header>
            <h3>Nächste Woche</h3>
            <small>{{ upcomingTasks.length }} Tasks</small>
          </header>
          <ul v-if="upcomingTasks.length">
            <li v-for="task in upcomingTasks" :key="`upcoming-${task.id}`">
              <div class="row">
                <strong>{{ task.title }}</strong>
                <span class="badge">{{ formatTaskDate(task.due_date) }}</span>
              </div>
              <p class="muted">{{ taskProjectLabel(task) }}</p>
            </li>
          </ul>
          <p v-else class="muted empty">Keine anstehenden Aufgaben.</p>
        </div>
      </div>
    </section>

    <section v-if="isTeam" class="card requests-card">
      <div class="requests-head">
        <div>
          <h2>Offene Anfragen</h2>
          <p class="muted">Neueste Requests aus dem Netzwerk.</p>
        </div>
        <button class="btn ghost tiny" type="button" @click="loadTeamRequests" :disabled="loadingRequests">
          {{ loadingRequests ? "Aktualisiere..." : "Neu laden" }}
        </button>
      </div>
      <ul v-if="teamRequests.length">
        <li v-for="request in teamRequests" :key="request.id">
          <div class="row">
            <strong>{{ request.sender_name }}</strong>
            <span class="pill">{{ requestTypeLabel(request.req_type) }}</span>
          </div>
          <p class="muted">An {{ request.receiver_name }} · {{ statusLabelMap[request.status] }}</p>
          <p class="message">{{ request.message || "Keine Nachricht hinterlegt." }}</p>
          <div class="request-actions">
            <button class="btn tiny" type="button" @click="respondRequest(request.id, 'accept')" :disabled="request.status !== 'OPEN'">Annehmen</button>
            <button class="btn ghost tiny" type="button" @click="respondRequest(request.id, 'decline')" :disabled="request.status !== 'OPEN'">Ablehnen</button>
          </div>
        </li>
      </ul>
      <p v-else class="muted empty">Keine offenen Anfragen.</p>
    </section>

    <section v-if="isTeam" class="card activity">
      <div class="activity-head">
        <div>
          <h2>Aktivitäten</h2>
          <p class="muted">Gefiltert nach Typ.</p>
        </div>
        <div class="activity-controls">
          <select class="input" v-model="activityFilter" @change="loadActivity">
            <option value="all">Alle</option>
            <option value="song_created,song_updated,song_version_created">Songs</option>
            <option value="growpro_created,growpro_updated,growpro_logged">GrowPro</option>
            <option value="task_overdue,task_status_updated,task_created">Tasks</option>
            <option value="request_accepted,request_declined">Requests</option>
          </select>
          <button class="btn ghost tiny" type="button" @click="loadActivity" :disabled="loadingActivity">
            {{ loadingActivity ? "Lade..." : "Neu laden" }}
          </button>
        </div>
      </div>
      <ul v-if="activities.length">
        <li v-for="item in activities" :key="item.id">
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
    </section>

    <section v-if="newsPosts.length" class="card news-preview">
      <div class="news-head">
        <h2>Neuigkeiten</h2>
        <router-link class="btn ghost tiny" to="/news">Alle News</router-link>
      </div>
      <ul>
        <li v-for="post in newsPosts" :key="post.id">
          <strong>{{ post.title }}</strong>
          <p class="muted">{{ previewBody(post.body) }}</p>
        </li>
      </ul>
    </section>

    <section v-if="isTeam" class="card quick-team">
      <div class="quick-head">
        <div>
          <h2>Quick Actions</h2>
          <p class="muted">GrowPro-Update oder Song-Version direkt hier.</p>
        </div>
        <p v-if="quickMessage" :class="['feedback', quickMessageType]">{{ quickMessage }}</p>
      </div>
      <div class="quick-grid">
        <div class="quick-block">
          <h3>GrowPro Update</h3>
          <label>
            Ziel
            <select class="input" v-model="quickGoalId">
              <option value="">Wählen</option>
              <option v-for="goal in growProGoals" :key="goal.id" :value="goal.id">
                {{ goal.title }} ({{ goal.profile?.name || goal.profile?.username || "?" }})
              </option>
            </select>
          </label>
          <div class="inline-fields">
            <input class="input" type="number" v-model.number="quickGoalValue" placeholder="Wert" />
            <input class="input" v-model.trim="quickGoalNote" placeholder="Notiz" />
          </div>
          <button class="btn tiny" type="button" @click="submitQuickGoal" :disabled="savingQuickGoal">
            {{ savingQuickGoal ? "Speichere..." : "Update speichern" }}
          </button>
        </div>
        <div class="quick-block">
          <h3>Song-Version</h3>
          <label>
            Song
            <select class="input" v-model="quickSongId">
              <option value="">Wählen</option>
              <option v-for="song in teamSongs" :key="song.id" :value="song.id">
                {{ song.title }}
              </option>
            </select>
          </label>
          <label class="file-picker">
            <input type="file" @change="onQuickFile($event)" />
            {{ quickFile ? quickFile.name : "Datei wählen" }}
          </label>
          <input class="input" v-model.trim="quickVersionNote" placeholder="Notiz" />
          <div class="flags">
            <label><input type="checkbox" v-model="quickFlags.mix" /> Mix</label>
            <label><input type="checkbox" v-model="quickFlags.master" /> Master</label>
            <label><input type="checkbox" v-model="quickFlags.final" /> Final</label>
          </div>
          <button class="btn tiny" type="button" @click="submitQuickVersion" :disabled="savingQuickVersion">
            {{ savingQuickVersion ? "Lädt..." : "Version hochladen" }}
          </button>
        </div>
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
const overdueTasks = ref([]);
const loadingOverdue = ref(false);
const upcomingTasks = ref([]);
const loadingUpcoming = ref(false);
const teamRequests = ref([]);
const loadingRequests = ref(false);
const growProGoals = ref([]);
const loadingGrowPro = ref(false);
const teamSongs = ref([]);
const newsPosts = ref([]);
const loading = ref(false);
const quickGoalId = ref("");
const quickGoalValue = ref("");
const quickGoalNote = ref("");
const quickSongId = ref("");
const quickFile = ref(null);
const quickVersionNote = ref("");
const quickFlags = ref({ mix: false, master: false, final: false });
const savingQuickGoal = ref(false);
const savingQuickVersion = ref(false);
const quickMessage = ref("");
const quickMessageType = ref("info");
const activities = ref([]);
const loadingActivity = ref(false);
const activityFilter = ref("all");

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
  { icon: "⏳", label: "GrowPro <24h", value: growProDueSoon.value },
  { icon: "⚠️", label: "GrowPro überfällig", value: growProOverdue.value },
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

const requestTypeLabels = {
  COLLAB: "Collab",
  BOOK: "Booking",
  OTHER: "Andere",
};

function activityIcon(type) {
  if (!type) return "•";
  if (type.startsWith("song")) return "♪";
  if (type.startsWith("growpro")) return "↗";
  if (type.startsWith("task")) return "⏰";
  if (type.startsWith("request")) return "✉";
  return "•";
}

function setQuickMessage(text, type = "info") {
  quickMessage.value = text;
  quickMessageType.value = type;
  if (text) {
    setTimeout(() => (quickMessage.value = ""), 2500);
  }
}

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
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    projects.value = [];
  }
}

async function loadOverdueTasks() {
  if (!isTeam.value) {
    overdueTasks.value = [];
    return;
  }
  loadingOverdue.value = true;
  try {
    const { data } = await api.get("tasks/overdue/");
    overdueTasks.value = data || [];
  } catch (err) {
    console.error("Überfällige Tasks konnten nicht geladen werden", err);
    overdueTasks.value = [];
  } finally {
    loadingOverdue.value = false;
  }
}

async function loadUpcomingTasks() {
  if (!isTeam.value) {
    upcomingTasks.value = [];
    return;
  }
  loadingUpcoming.value = true;
  try {
    const { data } = await api.get("tasks/upcoming/", { params: { days: 7, limit: 6 } });
    upcomingTasks.value = data || [];
  } catch (err) {
    console.error("Anstehende Tasks konnten nicht geladen werden", err);
    upcomingTasks.value = [];
  } finally {
    loadingUpcoming.value = false;
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
    teamRequests.value = data || [];
  } catch (err) {
    console.error("Anfragen konnten nicht geladen werden", err);
    teamRequests.value = [];
  } finally {
    loadingRequests.value = false;
  }
}

async function respondRequest(id, action) {
  if (!isTeam.value) return;
  const endpoint = action === "accept" ? "accept" : "decline";
  try {
    await api.post(`requests/${id}/${endpoint}/`);
    await loadTeamRequests();
    setQuickMessage(`Request ${action === "accept" ? "angenommen" : "abgelehnt"}`, "success");
  } catch (err) {
    console.error("Request-Aktion fehlgeschlagen", err);
    setQuickMessage("Aktion fehlgeschlagen", "error");
  }
}

async function loadGrowProGoals() {
  if (!isTeam.value) {
    growProGoals.value = [];
    return;
  }
  loadingGrowPro.value = true;
  try {
    const { data } = await api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } });
    const payload = data || {};
    growProGoals.value = Array.isArray(payload) ? payload : payload.results || [];
  } catch (err) {
    console.error("GrowPro konnte nicht geladen werden", err);
    growProGoals.value = [];
  } finally {
    loadingGrowPro.value = false;
  }
}

async function loadTeamSongs() {
  if (!isTeam.value) {
    teamSongs.value = [];
    return;
  }
  try {
    const { data } = await api.get("songs/", { params: { page_size: 50, ordering: "-created_at" } });
    const payload = data || {};
    teamSongs.value = Array.isArray(payload) ? payload : payload.results || [];
  } catch (err) {
    teamSongs.value = [];
  }
}

async function loadNewsPreview() {
  try {
    const { data } = await api.get("news/");
    newsPosts.value = (data || []).slice(0, 3);
  } catch (err) {
    console.error("News konnten nicht geladen werden", err);
    newsPosts.value = [];
  }
}

async function loadActivity() {
  if (!isTeam.value) {
    activities.value = [];
    return;
  }
  loadingActivity.value = true;
  try {
    const params = { limit: 40 };
    if (activityFilter.value !== "all") {
      params.types = activityFilter.value;
    }
    const { data } = await api.get("activity/", { params });
    activities.value = data || [];
  } catch (err) {
    activities.value = [];
  } finally {
    loadingActivity.value = false;
  }
}

function onQuickFile(event) {
  quickFile.value = event.target.files?.[0] || null;
}

async function submitQuickGoal() {
  if (!quickGoalId.value || quickGoalValue.value === "" || quickGoalValue.value === null) {
    setQuickMessage("Ziel und Wert wÇ¤hlen", "error");
    return;
  }
  savingQuickGoal.value = true;
  try {
    await api.post(`growpro/${quickGoalId.value}/log/`, {
      value: quickGoalValue.value,
      note: quickGoalNote.value,
    });
    quickGoalValue.value = "";
    quickGoalNote.value = "";
    await loadGrowProGoals();
    setQuickMessage("Update gespeichert", "success");
  } catch (err) {
    console.error("Quick-GrowPro fehlgeschlagen", err);
    setQuickMessage("Fehler beim Update", "error");
  } finally {
    savingQuickGoal.value = false;
  }
}

async function submitQuickVersion() {
  if (!quickSongId.value || !quickFile.value) {
    setQuickMessage("Song und Datei wÇ¤hlen", "error");
    return;
  }
  savingQuickVersion.value = true;
  try {
    const formData = new FormData();
    formData.append("song", quickSongId.value);
    formData.append("file", quickFile.value);
    formData.append("notes", quickVersionNote.value || "");
    formData.append("is_mix_ready", quickFlags.value.mix ? 1 : 0);
    formData.append("is_master_ready", quickFlags.value.master ? 1 : 0);
    formData.append("is_final", quickFlags.value.final ? 1 : 0);
    await api.post("song-versions/", formData, { headers: { "Content-Type": "multipart/form-data" } });
    quickFile.value = null;
    quickSongId.value = "";
    quickVersionNote.value = "";
    quickFlags.value = { mix: false, master: false, final: false };
    setQuickMessage("Version hochgeladen", "success");
  } catch (err) {
    console.error("Quick-Version fehlgeschlagen", err);
    setQuickMessage("Fehler beim Upload", "error");
  } finally {
    savingQuickVersion.value = false;
  }
}

async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);
    const loaders = [loadStats(), loadExamples(), loadNewsPreview()];
    if (isTeam.value) {
      loaders.push(loadOverdueTasks(), loadUpcomingTasks(), loadTeamRequests(), loadGrowProGoals(), loadTeamSongs(), loadActivity());
    } else {
      loaders.push(loadProjects());
    }
    await Promise.all(loaders);
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  const loaders = [loadStats(), loadExamples(), loadNewsPreview()];
  if (isTeam.value) {
    loaders.push(loadOverdueTasks(), loadUpcomingTasks(), loadTeamRequests(), loadGrowProGoals(), loadTeamSongs(), loadActivity());
  } else {
    loaders.push(loadProjects());
  }
  await Promise.all(loaders);
});

function statusLabel(status) {
  return statusLabelMap[status] || status;
}

function requestTypeLabel(type) {
  return requestTypeLabels[type] || type;
}

function previewBody(text = "") {
  if (!text) return "";
  return text.length > 120 ? `${text.slice(0, 117)}...` : text;
}

function formatTaskDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function taskProjectLabel(task) {
  return task.project_title || `Projekt #${task.project}`;
}

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
</script>

<style scoped>
.dashboard {
  display: grid;
  gap: 20px;
  width: 100%;
}
.welcome,
.team-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  flex-wrap: wrap;
}
.quick-team {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.quick-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}
.quick-block {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.inline-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.file-picker {
  border: 1px dashed var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  font-size: 13px;
  cursor: pointer;
}
.file-picker input {
  display: none;
}
.flags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
}
.feedback {
  margin: 0;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.welcome .muted,
.team-hero .muted {
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
.deadlines-head,
.requests-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.deadlines-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.deadline-column {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.deadline-column header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
}
.deadlines ul,
.requests-card ul {
  list-style: none;
  margin: 12px 0 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.deadlines .row,
.requests-card .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.deadlines .badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.18);
  color: #1d4ed8;
}
.deadlines .badge.danger {
  background: rgba(248, 113, 113, 0.18);
  color: #b91c1c;
}
.deadlines .empty {
  margin: 6px 0 0;
}
.requests-card .pill {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(75, 91, 255, 0.16);
  font-size: 11px;
  font-weight: 600;
}
.requests-card .message {
  margin: 4px 0 0;
  font-size: 13px;
}
.request-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.activity {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.activity-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.activity-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}
.activity ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}
.activity-type {
  background: rgba(15, 23, 42, 0.08);
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
.news-preview .news-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}
.news-preview ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}
@media (max-width: 760px) {
  .welcome,
  .team-hero {
    flex-direction: column;
    align-items: flex-start;
  }
  .hero-actions {
    justify-content: flex-start;
  }
  .checklist li {
    grid-template-columns: auto 1fr;
  }
  .checklist li .btn {
    grid-column: span 2;
    justify-self: flex-start;
  }
}
</style>


