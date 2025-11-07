<template>
  <div class="projects">
    <header class="card header">
      <div>
        <h1>Projekte</h1>
        <p class="muted">Plane Releases, Kampagnen oder Events im Team.</p>
      </div>
      <button class="btn ghost" type="button" @click="refreshProjects" :disabled="loading">
        {{ loading ? "Lade…" : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">
        Projekte können nur von Team-Mitgliedern verwaltet werden. Falls du Zugriff brauchst, kontaktiere dein Team.
      </p>
    </section>

    <section v-else class="grid">
      <form class="card form" @submit.prevent="createProject">
        <h2>Neues Projekt</h2>
        <label>
          Titel
          <input class="input" v-model.trim="newProject.title" placeholder="z.?B. Album Release" required />
        </label>
        <label>
          Beschreibung
          <textarea class="input textarea" v-model.trim="newProject.description" placeholder="Kurzbeschreibung"></textarea>
        </label>
        <label>
          Status
          <select class="input" v-model="newProject.status">
            <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
          </select>
        </label>
        <label>
          Team / Künstler
          <select class="input" v-model="newProject.participant_ids" multiple size="6">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
              {{ profile.name }}
            </option>
          </select>
          <small class="hint muted">Mehrfachauswahl mit Strg/Command moeglich.</small>
        </label>
        <button class="btn" type="submit" :disabled="creating">
          {{ creating ? "Speichere…" : "Projekt anlegen" }}
        </button>
      </form>

      <div class="card filters-panel">
        <h2>Filter</h2>
        <div class="filters">
          <label>
            Suche
            <input class="input" v-model.trim="search" placeholder="Titel durchsuchen" />
          </label>
          <label>
            Status
            <select class="input" v-model="filterStatus">
              <option value="ALL">Alle</option>
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Teilnehmer
            <select class="input" v-model="filterMember">
              <option value="ALL">Alle</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.name }}</option>
            </select>
          </label>
        </div>
        <div class="status-chips">
          <button
            v-for="opt in statusChipOptions"
            :key="`chip-${opt}`"
            type="button"
            class="chip"
            :class="{ active: filterStatus === opt }"
            @click="setStatusFilter(opt)"
          >
            {{ opt === "ALL" ? "Alle" : statusLabels[opt] }}
          </button>
          <button v-if="hasActiveFilters" type="button" class="chip clear" @click="resetFilters">
            Filter zuruecksetzen
          </button>
        </div>
        <div class="visibility">
          <label class="toggle">
            <input type="checkbox" v-model="showCompleted" />
            Abgeschlossene anzeigen
          </label>
          <label class="toggle">
            <input type="checkbox" v-model="showArchived" />
            Archivierte anzeigen
          </label>
        </div>
      </div>

      <div v-if="summaryTotals.total" class="card stats">
        <h2>Pipeline</h2>
        <div class="kpis">
          <div class="kpi" v-for="item in statusSummary" :key="item.key">
            <span class="label">{{ item.label }}</span>
            <strong>{{ item.count }}</strong>
          </div>
          <div class="kpi total">
            <span class="label">Gesamt</span>
            <strong>{{ summaryTotals.total }}</strong>
            <small class="muted">Aktiv: {{ summaryTotals.active }}</small>
            <small class="muted">Archiviert: {{ summaryTotals.archived }}</small>
          </div>
        </div>
      </div>

      <div class="card list">
        <h2>Aktuelle Projekte</h2>
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 3" :key="`sk-${n}`"></div>
        </div>
        <div v-else-if="!filteredProjects.length" class="muted empty">Keine Projekte passend zum Filter.</div>
        <ul v-else>
          <li v-for="project in filteredProjects" :key="project.id">
            <div class="meta">
              <h3>{{ project.title }}</h3>
              <span class="status" :data-status="project.status">{{ statusLabels[project.status] || project.status }}</span>
              <span v-if="project.is_archived" class="badge archived">Archiviert</span>
            </div>
            <p class="muted">{{ project.description || "Keine Beschreibung" }}</p>
            <div class="participants" v-if="project.participants?.length">
              <span class="chip" v-for="member in project.participants" :key="member.id">{{ member.name }}</span>
            </div>
            <footer>
              <small class="muted">Erstellt am {{ formatDate(project.created_at) }}</small>
              <div class="actions-row">
                <select class="input status-select" v-model="project.status" @change="updateStatus(project)">
                  <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                </select>
                <button class="btn ghost danger" type="button" @click="archiveProject(project)">
                  Archivieren
                </button>
              </div>
            </footer>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

const projects = ref([]);
const profiles = ref([]);
const loading = ref(false);
const creating = ref(false);
const showArchived = ref(false);
const showCompleted = ref(false);
const projectSummary = ref({
  total: 0,
  archived: 0,
  active: 0,
  done: 0,
  by_status: {},
});

const newProject = ref({
  title: "",
  description: "",
  status: "PLANNED",
  participant_ids: [],
});
const search = ref("");
const filterStatus = ref("ALL");
const filterMember = ref("ALL");

const statusOptions = ["PLANNED", "IN_PROGRESS", "REVIEW", "DONE", "ON_HOLD"];
const statusLabels = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Abgeschlossen",
  ON_HOLD: "Pausiert",
};
const statusChipOptions = ["ALL", ...statusOptions];

const filteredProjects = computed(() => {
  const term = search.value.trim().toLowerCase();
  return projects.value.filter((project) => {
    const matchesSearch =
      !term ||
      project.title.toLowerCase().includes(term) ||
      (project.description || "").toLowerCase().includes(term);
    const matchesStatus = filterStatus.value === "ALL" || project.status === filterStatus.value;
    const matchesMember =
      filterMember.value === "ALL" ||
      (project.participants || []).some((p) => String(p.id) === String(filterMember.value));
    return matchesSearch && matchesStatus && matchesMember;
  });
});

const statusSummary = computed(() =>
  statusOptions.map((key) => ({
    key,
    label: statusLabels[key] || key,
    count: projectSummary.value.by_status?.[key] || 0,
  }))
);

const summaryTotals = computed(() => ({
  total: projectSummary.value.total || 0,
  archived: projectSummary.value.archived || 0,
  active: projectSummary.value.active || 0,
  done: projectSummary.value.done || 0,
}));

const hasActiveFilters = computed(
  () =>
    filterStatus.value !== "ALL" ||
    filterMember.value !== "ALL" ||
    Boolean(search.value.trim())
);

function setStatusFilter(value) {
  filterStatus.value = value;
}

function resetFilters() {
  search.value = "";
  filterStatus.value = "ALL";
  filterMember.value = "ALL";
}

async function loadProjects() {
  if (!isTeam.value) return;
  if (loading.value) return;
  loading.value = true;
  try {
    const params = {
      include_archived: showArchived.value ? 1 : 0,
      include_done: showCompleted.value ? 1 : 0,
    };
    const { data } = await api.get("projects/", { params });
    projects.value = data;
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
  } finally {
    loading.value = false;
  }
}

async function loadProfiles() {
  try {
    const { data } = await api.get("profiles/");
    profiles.value = data.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    profiles.value = [];
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
    console.error("Projekt-Statistiken konnten nicht geladen werden", err);
    projectSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {} };
  }
}

async function refreshProjects() {
  await Promise.all([loadProjects(), loadProjectSummary()]);
}

async function createProject() {
  if (!newProject.value.title) return;
  creating.value = true;
  try {
    await api.post("projects/", newProject.value);
    newProject.value = { title: "", description: "", status: "PLANNED", participant_ids: [] };
    await refreshProjects();
  } catch (err) {
    console.error("Projekt konnte nicht erstellt werden", err);
  } finally {
    creating.value = false;
  }
}

async function updateStatus(project) {
  try {
    await api.patch(`projects/${project.id}/`, { status: project.status });
    await loadProjectSummary();
  } catch (err) {
    console.error("Status-Update fehlgeschlagen", err);
  }
}

async function archiveProject(project) {
  if (!confirm(`Projekt "${project.title}" archivieren?`)) return;
  try {
    await api.delete(`projects/${project.id}/`);
    await refreshProjects();
  } catch (err) {
    console.error("Projekt konnte nicht archiviert werden", err);
  }
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE").format(new Date(value));
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await loadProfiles();
    await refreshProjects();
  }
});

watch(
  () => [showArchived.value, showCompleted.value],
  () => {
    if (isTeam.value) {
      loadProjects();
    }
  }
);
</script>

<style scoped>
.projects {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.info {
  max-width: 600px;
}
.grid {
  display: grid;
  grid-template-columns: minmax(260px, 320px) 1fr;
  gap: 18px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
  grid-row: span 3;
}
.filters-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filters {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}
.visibility {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.status-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.status-chips .chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s ease, border 0.2s ease;
}
.status-chips .chip.active {
  background: rgba(112, 130, 255, 0.18);
  border-color: transparent;
  color: #fff;
}
.status-chips .chip.clear {
  border-style: dashed;
}
.stats {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}
.kpi {
  border: 1px solid rgba(75, 91, 255, 0.12);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi .label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.kpi strong {
  font-size: 1.4rem;
}
.kpi.total {
  background: rgba(75, 91, 255, 0.08);
  border-color: transparent;
}
.hint {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
}
.textarea {
  min-height: 90px;
  resize: vertical;
}
.list ul {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
  display: grid;
  gap: 14px;
}
.list li {
  border: 1px solid rgba(75, 91, 255, 0.08);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(75, 91, 255, 0.12);
  color: var(--brand);
}
[data-status="PLANNED"] {
  background: rgba(75, 91, 255, 0.12);
  color: var(--brand);
}
[data-status="DONE"] {
  background: rgba(52, 211, 153, 0.18);
  color: #059669;
}
[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.18);
  color: #ea580c;
}
[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.participants {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.badge {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.06em;
}
.badge.archived {
  background: rgba(15, 23, 42, 0.4);
  color: #94a3b8;
  border: 1px dashed rgba(148, 163, 184, 0.6);
}
.chip {
  background: rgba(112, 130, 255, 0.18);
  color: var(--brand);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}
.status-select {
  max-width: 160px;
}
.actions-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.btn.danger {
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}
.btn.danger:hover:not(:disabled) {
  border-color: rgba(239, 68, 68, 0.7);
  color: #fee2e2;
  background: rgba(239, 68, 68, 0.1);
}
.empty {
  text-align: center;
  padding: 20px 0;
}
.skeleton-list {
  display: grid;
  gap: 12px;
}
.skeleton-card {
  height: 96px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.12) 37%, rgba(255,255,255,0.05) 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .form {
    grid-row: auto;
  }
  footer {
    flex-direction: column;
    align-items: flex-start;
  }
  .status-select {
    width: 100%;
  }
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>




