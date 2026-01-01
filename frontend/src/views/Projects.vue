<template>
  <div class="projects">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
    <header class="card header">
      <div>
        <h1>Projekte</h1>
        <p class="muted">Plane Releases, Kampagnen oder Events im Team.</p>
      </div>
      <div class="header-actions">
        <button class="btn ghost" type="button" @click="refreshProjects" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
        <button class="btn ghost" type="button" @click="exportProjects" :disabled="exportingCsv || loading">
          {{ exportingCsv ? "Exportiere..." : "CSV Export" }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">
        Projekte können nur von Team-Mitgliedern verwaltet werden. Falls du Zugriff brauchst, kontaktiere dein Team.
      </p>
    </section>

    <section v-else class="stack">
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
        <div class="list-head">
          <div>
            <h2>Aktuelle Projekte</h2>
            <p class="muted" v-if="projectPagination.count">
              {{ projects.length }} von {{ projectPagination.count }} geladen
            </p>
          </div>
          <div class="list-actions">
            <button class="btn ghost" type="button" @click="openFilterModal">Filter</button>
            <button class="btn" type="button" @click="openCreateModal">Projekt anlegen</button>
          </div>
        </div>
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 3" :key="`sk-${n}`"></div>
        </div>
        <div v-else-if="!filteredProjects.length" class="muted empty">Keine Projekte passend zum Filter.</div>
        <ul v-else class="project-grid">
          <li
            v-for="project in filteredProjects"
            :key="project.id"
            class="project-card"
            :class="{ archived: project.is_archived }"
          >
            <div class="meta">
              <div class="title-block">
                <h3>{{ project.title }}</h3>
                <span class="status" :data-status="project.status">
                  {{ statusLabels[project.status] || project.status }}
                </span>
                <span v-if="project.is_archived" class="badge archived">Archiviert</span>
              </div>
              <div class="meta-actions">
                <label class="inline-select">
                  Status
                  <select class="input" v-model="project.status" @change="updateProjectStatus(project)">
                    <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                  </select>
                </label>
                <span class="created">{{ formatDate(project.created_at) }}</span>
                <button class="btn ghost sm" type="button" @click="openProject(project.id)">Öffnen</button>
                <button class="btn ghost sm" type="button" @click="startEditProject(project)">Bearbeiten</button>
              </div>
            </div>
            <p class="muted description">{{ project.description || "Keine Beschreibung hinterlegt." }}</p>
            <div class="participants">
              <span class="label">Teilnehmer:</span>
              <span v-if="project.participants?.length" class="names">
                {{ project.participants.map((p) => p.name || p.username).join(", ") }}
              </span>
              <span v-else class="names muted">Noch keine Personen zugeordnet</span>
            </div>
            <div class="owners">
              <span class="label">Team:</span>
              <span v-if="project.owners?.length" class="names">
                {{ project.owners.map((p) => p.name || p.username).join(", ") }}
              </span>
              <span v-else class="names muted">Noch kein Team zugeordnet</span>
            </div>
          </li>
        </ul>
        <div ref="projectSentinel" class="sentinel" v-if="hasMoreProjects"></div>
        <p v-if="loadingMore" class="muted loading-more">Lade weitere Projekte...</p>
      </div>
    </section>

    <div v-if="showFilterModal" class="modal-backdrop" @click.self="closeFilterModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Filter</h3>
          <button class="btn ghost tiny" type="button" @click="closeFilterModal">Schließen</button>
        </div>
        <form class="form" @submit.prevent="applyFilters">
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
              Filter zurücksetzen
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
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="resetFilters">Reset</button>
            <button class="btn" type="submit">Anwenden</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="projectModalVisible" class="modal-backdrop" @click.self="closeProjectModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>{{ projectModalMode === "create" ? "Neues Projekt" : "Projekt bearbeiten" }}</h3>
          <button class="btn ghost tiny" type="button" @click="closeProjectModal" :disabled="projectSaving">Schließen</button>
        </div>
        <form class="form" @submit.prevent="submitProjectForm">
          <label>
            Titel
            <input class="input" v-model.trim="projectForm.title" placeholder="z. B. Album Release" required />
          </label>
          <label>
            Beschreibung
            <textarea class="input textarea" v-model.trim="projectForm.description" placeholder="Kurzbeschreibung"></textarea>
          </label>
          <label>
            Status
            <select class="input" v-model="projectForm.status">
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Betroffene Nutzer
            <select class="input" v-model="projectForm.participant_ids" multiple size="8">
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Mehrfachauswahl mit Strg/Command möglich.</small>
          </label>
          <label>
            Verantwortliche Teammitglieder
            <select class="input" v-model="projectForm.owner_ids" multiple size="6">
              <option v-for="profile in teamProfiles" :key="`team-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Nur Team-Mitglieder werden angezeigt.</small>
          </label>
          <div v-if="projectModalMode === 'edit'" class="danger-zone">
            <p class="muted">Projekt archivieren oder endgültig löschen.</p>
            <div class="danger-buttons">
              <button class="btn ghost danger" type="button" @click="archiveCurrentProject" :disabled="projectSaving">
                Archivieren
              </button>
              <button class="btn danger" type="button" @click="deleteCurrentProject" :disabled="projectSaving">
                Löschen
              </button>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeProjectModal" :disabled="projectSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="projectSaving">
              {{
                projectSaving
                  ? "Speichere..."
                  : projectModalMode === "create"
                    ? "Projekt anlegen"
                    : "Speichern"
              }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useRealtimeUpdates } from "../composables/useRealtimeUpdates";

const router = useRouter();
const { isTeam, fetchProfile } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();
const { connect: connectRealtime } = useRealtimeUpdates(handleRealtimeEvent);

const projects = ref([]);
const profiles = ref([]);
const projectSummary = ref({ total: 0, archived: 0, active: 0, done: 0, by_status: {} });
const loading = ref(false);
const loadingMore = ref(false);
const exportingCsv = ref(false);
const showFilterModal = ref(false);
const showArchived = ref(true);
const showCompleted = ref(false);
const search = ref("");
const filterStatus = ref("ALL");
const filterMember = ref("ALL");
const projectPagination = ref({ next: null, previous: null, count: 0 });
const projectSentinel = ref(null);
const projectModalVisible = ref(false);
const projectModalMode = ref("create");
const projectSaving = ref(false);
const projectForm = ref(getDefaultProjectForm());
const editingProjectId = ref(null);
let observer;
let searchDebounce;
let summaryRefreshTimer = null;

const statusOptions = ["PLANNED", "IN_PROGRESS", "ON_HOLD", "DONE"];
const statusLabels = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  ON_HOLD: "Pausiert",
  DONE: "Abgeschlossen",
};

const statusChipOptions = ["ALL", ...statusOptions];
const hasActiveFilters = computed(
  () =>
    filterStatus.value !== "ALL" ||
    filterMember.value !== "ALL" ||
    Boolean(search.value.trim())
);
const filteredProjects = computed(() => projects.value);
const statusSummary = computed(() =>
  statusOptions.map((key) => ({
    key,
    label: statusLabels[key],
    count: projectSummary.value.by_status?.[key] || 0,
  }))
);
const summaryTotals = computed(() => ({
  total: projectSummary.value.total || 0,
  archived: projectSummary.value.archived || 0,
  active: projectSummary.value.active || 0,
  done: projectSummary.value.done || 0,
}));
const hasMoreProjects = computed(() => Boolean(projectPagination.value.next));
const teamProfiles = computed(() =>
  profiles.value.filter((profile) =>
    (profile.roles || []).some((role) => role.key === "TEAM")
  )
);

function getDefaultProjectForm() {
  return {
    title: "",
    description: "",
    status: "PLANNED",
    participant_ids: [],
    owner_ids: [],
  };
}

function buildProjectParams() {
  return {
    include_archived: showArchived.value ? 1 : 0,
    include_done: showCompleted.value ? 1 : 0,
    search: search.value.trim() || undefined,
    status: filterStatus.value !== "ALL" ? filterStatus.value : undefined,
    participant: filterMember.value !== "ALL" ? filterMember.value : undefined,
  };
}

function computeProjectSummary(list) {
  const summary = {
    total: list.length,
    archived: list.filter((p) => p.is_archived).length,
    active: list.filter((p) => !p.is_archived).length,
    done: list.filter((p) => p.status === "DONE").length,
    by_status: {},
  };
  statusOptions.forEach((key) => {
    summary.by_status[key] = list.filter((p) => p.status === key && !p.is_archived).length;
  });
  return summary;
}

async function loadProjects({ append = false, pageUrl = null } = {}) {
  if (!isTeam.value) return;
  if (append && !projectPagination.value.next && !pageUrl) return;
  const targetState = append ? loadingMore : loading;
  if (targetState.value) return;
  targetState.value = true;
  try {
    const params = pageUrl ? undefined : buildProjectParams();
    const url = pageUrl || "projects/";
    const { data } = await api.get(url, { params });
    if (Array.isArray(data)) {
      projects.value = append ? projects.value.concat(data) : data;
      projectPagination.value = { next: null, previous: null, count: data.length };
    } else {
      const results = data.results || [];
      projects.value = append ? projects.value.concat(results) : results;
      projectPagination.value = {
        next: data.next,
        previous: data.previous,
        count: data.count ?? results.length,
      };
    }
    projectSummary.value = computeProjectSummary(projects.value);
    if (!append) {
      await nextTick();
      setupObserver();
    }
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    showToast("Projekte konnten nicht geladen werden", "error");
    if (!append) {
      projects.value = [];
      projectPagination.value = { next: null, previous: null, count: 0 };
    }
  } finally {
    targetState.value = false;
  }
}

async function loadProfiles() {
  try {
    const { data } = await api.get("profiles/");
    profiles.value = data.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
      username: profile.username,
      roles: profile.roles || [],
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    showToast("Profile konnten nicht geladen werden", "error");
    profiles.value = [];
  }
}

async function loadProjectSummary() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("projects/summary/", { params: { include_archived: 0 } });
    projectSummary.value = {
      total: data.total || 0,
      archived: data.archived || 0,
      active: data.active || 0,
      done: data.done || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    console.error("Projekt-Statistiken konnten nicht geladen werden", err);
    showToast("Projekt-Statistiken konnten nicht geladen werden", "error");
    projectSummary.value = computeProjectSummary(projects.value);
  }
}

async function refreshProjects() {
  await Promise.all([loadProjects(), loadProjectSummary()]);
}

function setStatusFilter(value) {
  filterStatus.value = value;
}

function resetFilters() {
  search.value = "";
  filterStatus.value = "ALL";
  filterMember.value = "ALL";
}

function openCreateModal() {
  projectModalMode.value = "create";
  editingProjectId.value = null;
  projectForm.value = { ...getDefaultProjectForm() };
  projectModalVisible.value = true;
}
function closeProjectModal() {
  if (projectSaving.value) return;
  projectModalVisible.value = false;
}
function openFilterModal() {
  showFilterModal.value = true;
}
function closeFilterModal() {
  showFilterModal.value = false;
}
function applyFilters() {
  loadProjects();
  closeFilterModal();
}

function openProject(projectId) {
  router.push({ name: "project-detail", params: { projectId } });
}

function startEditProject(project) {
  projectModalMode.value = "edit";
  editingProjectId.value = project.id;
  projectForm.value = {
    title: project.title,
    description: project.description || "",
    status: project.status,
    participant_ids: project.participants?.map((p) => p.id) || [],
    owner_ids: project.owners?.map((p) => p.id) || [],
  };
  projectModalVisible.value = true;
}

async function submitProjectForm() {
  if (!projectForm.value.title.trim()) return;
  projectSaving.value = true;
  const payload = {
    ...projectForm.value,
    title: projectForm.value.title.trim(),
    description: projectForm.value.description?.trim() || "",
  };
  try {
    if (projectModalMode.value === "edit" && editingProjectId.value) {
      await api.patch(`projects/${editingProjectId.value}/`, payload);
      showToast("Projekt aktualisiert", "success");
    } else {
      await api.post("projects/", payload);
      showToast("Projekt angelegt", "success");
    }
    await refreshProjects();
    projectModalVisible.value = false;
  } catch (err) {
    console.error("Projekt konnte nicht gespeichert werden", err);
    showToast("Projekt konnte nicht gespeichert werden", "error");
  } finally {
    projectSaving.value = false;
  }
}

async function updateProjectStatus(project) {
  try {
    await api.patch(`projects/${project.id}/`, { status: project.status });
    await loadProjectSummary();
    showToast("Status aktualisiert", "success");
  } catch (err) {
    console.error("Projekt-Status konnte nicht aktualisiert werden", err);
    showToast("Status konnte nicht aktualisiert werden", "error");
  }
}

async function archiveCurrentProject() {
  if (!editingProjectId.value) return;
  if (!confirm(`Projekt "${projectForm.value.title}" archivieren?`)) return;
  projectSaving.value = true;
  try {
    await api.post(`projects/${editingProjectId.value}/archive/`);
    await refreshProjects();
    projectModalVisible.value = false;
    showToast("Projekt archiviert", "success");
  } catch (err) {
    console.error("Projekt konnte nicht archiviert werden", err);
    showToast("Projekt konnte nicht archiviert werden", "error");
  } finally {
    projectSaving.value = false;
  }
}

async function deleteCurrentProject() {
  if (!editingProjectId.value) return;
  if (!confirm(`Projekt "${projectForm.value.title}" endgültig löschen?`)) return;
  projectSaving.value = true;
  try {
    try {
      await api.post(`projects/${editingProjectId.value}/delete/`);
    } catch (err) {
      // Fallback auf klassisches DELETE, falls das neue Endpoint nicht erreichbar ist
      await api.delete(`projects/${editingProjectId.value}/`);
    }
    await refreshProjects();
    projectModalVisible.value = false;
    showToast("Projekt gelöscht", "success");
  } catch (err) {
    console.error("Projekt konnte nicht gelöscht werden", err);
    showToast("Projekt konnte nicht gelöscht werden", "error");
  } finally {
    projectSaving.value = false;
  }
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE").format(new Date(value));
}

async function exportProjects() {
  if (exportingCsv.value) return;
  exportingCsv.value = true;
  try {
    const { data } = await api.get("projects/export/", {
      params: buildProjectParams(),
      responseType: "blob",
    });
    const blob = new Blob([data], { type: "text/csv;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "projects.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("CSV Export fehlgeschlagen", err);
    showToast("CSV Export fehlgeschlagen", "error");
  } finally {
    exportingCsv.value = false;
  }
}

function setupObserver() {
  if (observer) {
    observer.disconnect();
  }
  if (!projectSentinel.value) return;
  observer = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && projectPagination.value.next && !loadingMore.value) {
      loadProjects({ append: true, pageUrl: projectPagination.value.next });
    }
  });
  observer.observe(projectSentinel.value);
}

function handleRealtimeEvent(event) {
  if (event?.entity !== "project" || !event.data) return;
  const action = event.action || "updated";
  const data = event.data;
  if (action === "deleted") {
    removeProjectById(data.id);
    scheduleSummaryRefresh();
    return;
  }
  if (!projectMatchesFilters(data)) {
    removeProjectById(data.id);
    scheduleSummaryRefresh();
    return;
  }
  upsertProject(data);
  scheduleSummaryRefresh();
}

function upsertProject(projectData) {
  const idx = projects.value.findIndex((project) => project.id === projectData.id);
  if (idx === -1) {
    projects.value = [projectData, ...projects.value];
  } else {
    const updated = [...projects.value];
    updated.splice(idx, 1, projectData);
    projects.value = updated;
  }
  projectSummary.value = computeProjectSummary(projects.value);
}

function removeProjectById(projectId) {
  const idx = projects.value.findIndex((project) => project.id === projectId);
  if (idx === -1) return;
  const updated = [...projects.value];
  updated.splice(idx, 1);
  projects.value = updated;
  projectSummary.value = computeProjectSummary(projects.value);
}

function projectMatchesFilters(project) {
  if (!showArchived.value && project.is_archived) {
    return false;
  }
  if (!showCompleted.value && project.status === "DONE") {
    return false;
  }
  if (filterStatus.value !== "ALL" && project.status !== filterStatus.value) {
    return false;
  }
  if (filterMember.value !== "ALL") {
    const memberId = Number(filterMember.value);
    const participantIds = (project.participants || []).map((p) => p.id);
    if (!participantIds.includes(memberId)) {
      return false;
    }
  }
  const term = search.value.trim().toLowerCase();
  if (term) {
    const haystack = `${project.title || ""} ${project.description || ""}`.toLowerCase();
    if (!haystack.includes(term)) {
      return false;
    }
  }
  return true;
}

function scheduleSummaryRefresh() {
  if (summaryRefreshTimer) return;
  summaryRefreshTimer = setTimeout(async () => {
    summaryRefreshTimer = null;
    await loadProjectSummary();
  }, 800);
}

watch(
  () => [filterStatus.value, filterMember.value, showArchived.value, showCompleted.value],
  () => {
    if (!isTeam.value) return;
    loadProjects();
  }
);

watch(
  () => search.value,
  () => {
    if (!isTeam.value) return;
    if (searchDebounce) clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => loadProjects(), 300);
  }
);

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await Promise.all([loadProfiles(), refreshProjects()]);
    connectRealtime();
  }
});

onBeforeUnmount(() => {
  if (observer) observer.disconnect();
  if (searchDebounce) clearTimeout(searchDebounce);
  if (summaryRefreshTimer) clearTimeout(summaryRefreshTimer);
});
</script>

<style scoped>
.projects {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.card {
  border-radius: 22px;
  border: 1px solid var(--border);
  background: var(--card);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
  padding: 22px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}
.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.stack {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.stats {
  background: rgba(99, 102, 241, 0.12);
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 16px;
}
.kpi {
  padding: 16px;
  border-radius: 18px;
  background: var(--card);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.kpi strong {
  font-size: 28px;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.list-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.list-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.project-grid {
  list-style: none;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
  padding: 0;
  margin: 0;
}
.project-card {
  background: var(--card);
  border-radius: 20px;
  border: 1px solid var(--border);
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 240px;
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.project-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 30px 60px rgba(15, 23, 42, 0.14);
}
.project-card.archived {
  border-style: dashed;
  opacity: 0.75;
}
.meta {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.title-block {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.status {
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}
.status[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.16);
  color: #ea580c;
}
.status[data-status="DONE"] {
  background: rgba(16, 185, 129, 0.16);
  color: #059669;
}
.status[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
.meta-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.inline-select {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--muted);
}
.created {
  font-size: 12px;
  color: var(--muted);
}
.description {
  font-size: 14px;
  color: var(--muted);
}
.badge.archived {
  background: rgba(15, 23, 42, 0.1);
  color: #1f2937;
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
}
.participants,
.owners {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 13px;
}
.participants .label,
.owners .label {
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-size: 11px;
  color: var(--muted);
}
.skeleton-list {
  display: grid;
  gap: 12px;
}
.skeleton-card {
  height: 140px;
  border-radius: 18px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.25), rgba(248, 250, 252, 0.6), rgba(148, 163, 184, 0.25));
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
.status-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.status-chips .chip {
  border-radius: 999px;
  padding: 4px 14px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.status-chips .chip.active {
  border-color: #2563eb;
  color: #2563eb;
}
.status-chips .chip.clear {
  border-color: transparent;
  background: rgba(15, 23, 42, 0.05);
}
.visibility {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}
.modal {
  width: min(640px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 24px;
  padding: 24px;
  background: var(--card);
  box-shadow: 0 35px 80px rgba(15, 23, 42, 0.35);
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.form .hint {
  font-size: 12px;
}
.input,
.textarea {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--card);
  font-size: 14px;
  width: 100%;
}
.textarea {
  min-height: 110px;
  resize: vertical;
}
:global(.dark) .projects .card {
  background: var(--card);
  border-color: var(--border);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);
}
:global(.dark) .projects .card.stats {
  background: linear-gradient(120deg, rgba(99, 102, 241, 0.2), rgba(56, 189, 248, 0.12));
}
:global(.dark) .projects .kpi,
:global(.dark) .projects .project-card {
  background: rgba(15, 23, 42, 0.6);
  border-color: var(--border);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
}
:global(.dark) .projects .modal {
  background: var(--card);
  box-shadow: 0 35px 80px rgba(0, 0, 0, 0.55);
}
:global(.dark) .projects .input,
:global(.dark) .projects .textarea {
  background: rgba(15, 23, 42, 0.6);
  border-color: var(--border);
  color: var(--text);
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.danger-zone {
  border: 1px dashed rgba(220, 38, 38, 0.45);
  border-radius: 16px;
  padding: 12px;
  background: rgba(248, 113, 113, 0.08);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.danger-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.empty {
  text-align: center;
  padding: 40px 0;
}
.sentinel {
  width: 100%;
  height: 1px;
}
.loading-more {
  text-align: center;
  font-size: 13px;
  color: var(--muted);
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
@media (max-width: 640px) {
  .project-card {
    min-height: auto;
  }
  .meta-actions {
    flex-direction: column;
    align-items: flex-start;
  }
  .modal {
    padding: 18px;
  }
}
</style>
