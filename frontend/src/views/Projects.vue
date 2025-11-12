<template>
  <div class="projects">
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
      <h2>Zugriff nur fuer Team</h2>
      <p class="muted">
        Projekte koennen nur von Team-Mitgliedern verwaltet werden. Falls du Zugriff brauchst, kontaktiere dein Team.
      </p>
    </section>

    <section v-else class="grid">
      <form class="card form" @submit.prevent="createProject">
        <h2>Neues Projekt</h2>
        <label>
          Titel
          <input class="input" v-model.trim="newProject.title" placeholder="z. B. Album Release" required />
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
          Team / Artists
          <select class="input" v-model="newProject.participant_ids" multiple size="6">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
              {{ profile.name }}
            </option>
          </select>
          <small class="hint muted">Mehrfachauswahl mit Strg/Command moeglich.</small>
        </label>
        <button class="btn" type="submit" :disabled="creating">
          {{ creating ? "Speichere..." : "Projekt anlegen" }}
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
        <div class="list-head">
          <h2>Aktuelle Projekte</h2>
          <p class="muted" v-if="projectPagination.count">
            {{ projects.length }} von {{ projectPagination.count }} geladen
          </p>
        </div>
        <div v-if="loading" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 3" :key="`sk-${n}`"></div>
        </div>
        <div v-else-if="!filteredProjects.length" class="muted empty">Keine Projekte passend zum Filter.</div>
        <ul v-else>
          <li v-for="project in filteredProjects" :key="project.id">
            <div class="meta">
              <div class="title-block">
                <h3>{{ project.title }}</h3>
                <span class="status" :data-status="project.status">
                  {{ statusLabels[project.status] || project.status }}
                </span>
                <span v-if="project.is_archived" class="badge archived">Archiviert</span>
              </div>
              <div class="meta-actions">
                <span class="created">{{ formatDate(project.created_at) }}</span>
                <button class="btn ghost sm" type="button" @click="toggleProjectDetails(project.id)">
                  {{ openProjectId === project.id ? "Details schliessen" : "Details" }}
                </button>
                <button class="btn ghost danger sm" type="button" @click="archiveProject(project)">Archivieren</button>
              </div>
            </div>
            <p class="muted description">{{ project.description || "Keine Beschreibung hinterlegt." }}</p>
            <div class="participants">
              <span class="label">Teilnehmer:</span>
              <span v-if="project.participants?.length" class="names">
                {{ project.participants.map((p) => p.name).join(", ") }}
              </span>
              <span v-else class="names muted">Noch keine Personen zugeordnet</span>
            </div>
            <div v-if="openProjectId === project.id" class="project-extra">
              <section class="attachments">
                <header>
                  <h4>Dateianhaenge</h4>
                  <button class="btn ghost tiny" type="button" @click="ensureProjectAttachments(project.id, true)">
                    Neu laden
                  </button>
                </header>
                <ul v-if="projectAttachmentsMap[project.id]?.length" class="attachment-list">
                  <li v-for="file in projectAttachmentsMap[project.id]" :key="file.id">
                    <a :href="file.file_url" target="_blank" rel="noopener">
                      {{ file.label || file.file_name || "Datei" }}
                    </a>
                    <small class="muted">von {{ file.uploaded_by?.name || file.uploaded_by?.username }}</small>
                    <button class="iconbtn danger" type="button" @click="removeProjectAttachment(project.id, file.id)">
                      ✕
                    </button>
                  </li>
                </ul>
                <p v-else-if="attachmentsLoading[project.id]" class="muted">Lade Anhaenge...</p>
                <p v-else class="muted">Keine Anhaenge</p>
                <form class="upload-row" @submit.prevent="uploadProjectAttachment(project.id)">
                  <input
                    class="input"
                    v-model.trim="attachmentDraft(project.id).label"
                    placeholder="Kurzbeschreibung"
                  />
                  <label class="file-picker">
                    <input type="file" @change="onProjectFile(project.id, $event)" />
                    {{ attachmentDraft(project.id).file ? attachmentDraft(project.id).file.name : "Datei waehlen" }}
                  </label>
                  <button class="btn tiny" type="submit" :disabled="attachmentsLoading[project.id]">
                    {{ attachmentsLoading[project.id] ? "Lade..." : "Hochladen" }}
                  </button>
                </form>
              </section>
            </div>
          </li>
        </ul>
        <div ref="projectSentinel" class="sentinel" v-if="hasMoreProjects"></div>
        <p v-if="loadingMore" class="muted loading-more">Lade weitere Projekte...</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

const projects = ref([]);
const profiles = ref([]);
const projectSummary = ref({ total: 0, archived: 0, active: 0, done: 0, by_status: {} });
const loading = ref(false);
const loadingMore = ref(false);
const creating = ref(false);
const exportingCsv = ref(false);
const showArchived = ref(false);
const showCompleted = ref(false);
const search = ref("");
const filterStatus = ref("ALL");
const filterMember = ref("ALL");
const projectPagination = ref({ next: null, previous: null, count: 0 });
const projectSentinel = ref(null);
const projectAttachmentsMap = ref({});
const attachmentDrafts = ref({});
const attachmentsLoading = ref({});
const openProjectId = ref(null);
let observer;
let searchDebounce;

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

const newProject = ref({
  title: "",
  description: "",
  status: "PLANNED",
  participant_ids: [],
});

function buildProjectParams() {
  return {
    include_archived: showArchived.value ? 1 : 0,
    include_done: showCompleted.value ? 1 : 0,
    search: search.value.trim() || undefined,
    status: filterStatus.value !== "ALL" ? filterStatus.value : undefined,
    participant: filterMember.value !== "ALL" ? filterMember.value : undefined,
  };
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
    if (!append) {
      await nextTick();
      setupObserver();
    }
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
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

function setStatusFilter(value) {
  filterStatus.value = value;
}

function resetFilters() {
  search.value = "";
  filterStatus.value = "ALL";
  filterMember.value = "ALL";
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

function attachmentDraft(projectId) {
  if (!attachmentDrafts.value[projectId]) {
    attachmentDrafts.value[projectId] = { label: "", file: null };
  }
  return attachmentDrafts.value[projectId];
}

async function ensureProjectAttachments(projectId, force = false) {
  if (!force && projectAttachmentsMap.value[projectId]) return;
  attachmentsLoading.value[projectId] = true;
  try {
    const { data } = await api.get("project-attachments/", { params: { project: projectId } });
    projectAttachmentsMap.value = {
      ...projectAttachmentsMap.value,
      [projectId]: data,
    };
  } catch (err) {
    console.error("Anhaenge konnten nicht geladen werden", err);
  } finally {
    attachmentsLoading.value[projectId] = false;
  }
}

function onProjectFile(projectId, event) {
  const draft = attachmentDraft(projectId);
  draft.file = event.target.files?.[0] || null;
}

async function uploadProjectAttachment(projectId) {
  const draft = attachmentDraft(projectId);
  if (!draft.file) return;
  attachmentsLoading.value[projectId] = true;
  try {
    const formData = new FormData();
    formData.append("project", projectId);
    formData.append("label", draft.label);
    formData.append("file", draft.file);
    await api.post("project-attachments/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    draft.label = "";
    draft.file = null;
    await ensureProjectAttachments(projectId, true);
  } catch (err) {
    console.error("Anhang konnte nicht gespeichert werden", err);
  } finally {
    attachmentsLoading.value[projectId] = false;
  }
}

async function removeProjectAttachment(projectId, attachmentId) {
  if (!confirm("Anhang wirklich entfernen?")) return;
  attachmentsLoading.value[projectId] = true;
  try {
    await api.delete(`project-attachments/${attachmentId}/`);
    await ensureProjectAttachments(projectId, true);
  } catch (err) {
    console.error("Anhang konnte nicht geloescht werden", err);
  } finally {
    attachmentsLoading.value[projectId] = false;
  }
}

function toggleProjectDetails(projectId) {
  if (openProjectId.value === projectId) {
    openProjectId.value = null;
    return;
  }
  openProjectId.value = projectId;
  ensureProjectAttachments(projectId);
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
  }
});

onBeforeUnmount(() => {
  if (observer) observer.disconnect();
  if (searchDebounce) clearTimeout(searchDebounce);
});
</script>

<style scoped>
.projects {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.info {
  max-width: 600px;
}
.grid {
  display: grid;
  grid-template-columns: minmax(260px, 320px) minmax(420px, 1fr);
  gap: 18px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.filters-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.status-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.status-chips .chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
}
.status-chips .chip.active {
  border-color: var(--brand);
  color: var(--brand);
}
.status-chips .chip.clear {
  border-color: transparent;
  background: rgba(0, 0, 0, 0.04);
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
  font-weight: 500;
}
.stats {
  grid-column: span 2;
}
.kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}
.kpi {
  border: 1px solid rgba(75, 91, 255, 0.12);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.kpi.total {
  background: rgba(75, 91, 255, 0.06);
}
.list {
  grid-column: span 2;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.list-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.list ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.list li {
  border: 1px solid rgba(75, 91, 255, 0.12);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.title-block {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.meta-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}
.created {
  font-size: 13px;
  color: var(--muted);
}
.status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(75, 91, 255, 0.16);
  color: var(--brand);
}
.status[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.16);
  color: #ea580c;
}
.status[data-status="DONE"] {
  background: rgba(52, 211, 153, 0.16);
  color: #059669;
}
.status[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
.badge.archived {
  background: rgba(15, 23, 42, 0.1);
  color: #475569;
  border-radius: 6px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}
.participants {
  display: flex;
  gap: 6px;
  font-size: 14px;
  flex-wrap: wrap;
}
.participants .label {
  font-weight: 600;
}
.project-extra {
  border-top: 1px dashed var(--border);
  padding-top: 12px;
}
.attachments header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.attachment-list {
  list-style: none;
  margin: 0 0 10px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.attachment-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.attachment-list a {
  font-weight: 600;
  color: var(--brand);
}
.attachment-list .iconbtn {
  margin-left: auto;
}
.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.file-picker {
  border: 1px dashed var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 13px;
  cursor: pointer;
}
.file-picker input {
  display: none;
}
.skeleton-list {
  display: grid;
  gap: 10px;
}
.skeleton-card {
  height: 120px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.sentinel {
  width: 100%;
  height: 4px;
}
.loading-more {
  text-align: center;
  font-size: 13px;
}
.btn.sm {
  padding: 4px 10px;
  font-size: 12px;
}
.btn.tiny {
  padding: 4px 12px;
  font-size: 12px;
}
.btn.ghost.tiny {
  padding: 4px 10px;
}
.iconbtn {
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
}
.iconbtn.danger {
  color: #dc2626;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .stats,
  .list {
    grid-column: span 1;
  }
}
</style>
