<template>
  <div class="tasks">
    <header class="card header">
      <div>
        <h1>Tasks</h1>
        <p class="muted">Verteile Aufgaben, lade Dateien hoch und halte Kommentare fest.</p>
      </div>
      <button class="btn ghost" type="button" @click="refreshTasks" :disabled="loadingTasks">
        {{ loadingTasks ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur fuer Team</h2>
      <p class="muted">Nur Team-Mitglieder koennen Aufgaben verwalten. Bitte wende dich an das Team.</p>
    </section>

    <section v-else class="content single">
      <div class="board card">
        <div class="board-head">
          <div>
            <h2>Task Board</h2>
            <p class="muted small">Filter und neue Aufgaben per Dialog.</p>
          </div>
          <div class="board-actions">
            <button class="btn ghost" type="button" @click="openFilterModal">Filter</button>
            <button class="btn" type="button" @click="openCreateModal" :disabled="creating">Task erstellen</button>
          </div>
        </div>
        <div v-if="taskSummary.total" class="progress-strip">
          <div class="progress-bar">
            <div
              v-for="segment in statusProgress"
              :key="segment.key"
              class="segment"
              :data-status="segment.key"
              :style="{ flex: Math.max(segment.count, 0.2) }"
            ></div>
          </div>
          <div class="legend">
            <span v-for="segment in statusProgress" :key="`legend-${segment.key}`">
              <span class="dot" :data-status="segment.key"></span>
              {{ segment.label }} ({{ segment.count }})
            </span>
          </div>
        </div>
        <div class="columns">
          <div v-for="column in boardColumns" :key="column.key">
            <h3>{{ column.label }}</h3>
            <div v-if="loadingTasks" class="skeleton-column">
              <div class="skeleton-card" v-for="n in 2" :key="`tsk-${column.key}-${n}`"></div>
            </div>
            <template v-else>
              <ul>
                <li
                  v-for="task in column.items"
                  :key="task.id"
                  :class="{ overdue: dueState(task) === 'overdue', soon: dueState(task) === 'soon' }"
                >
                  <div class="title-row">
                    <div>
                      <div class="title">{{ task.title }}</div>
                      <span class="priority" :data-priority="task.priority">
                        {{ priorityLabels[task.priority] }}
                      </span>
                    </div>
                    <button class="btn ghost tiny" type="button" @click="openTask(task)">
                      Details
                    </button>
                  </div>
                  <p class="muted">
                    Projekt: {{ projectMap[task.project]?.title || "-" }}
                  </p>
                  <p class="due" :class="dueState(task)">
                    {{ task.due_date ? `Faellig ${formatDueDate(task.due_date)}` : "Kein Termin" }}
                  </p>
                  <div class="actions">
                    <select class="input" v-model="task.status" @change="updateStatus(task)">
                      <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                    </select>
                    <button class="btn ghost danger tiny" type="button" @click="archiveTask(task)">
                      Archivieren
                    </button>
                  </div>
                </li>
              </ul>
              <p v-if="!column.items.length" class="muted empty">Keine Tasks</p>
            </template>
          </div>
        </div>
      </div>
    </section>

    <section v-if="activeTask" class="card detail-panel">
      <header>
        <div>
          <p class="eyebrow">Ausgewaehlter Task</p>
          <h2>{{ activeTask.title }}</h2>
          <p class="muted">Projekt: {{ projectMap[activeTask.project]?.title || "-" }}</p>
        </div>
        <button class="btn ghost tiny" type="button" @click="activeTaskId = null">Schliessen</button>
      </header>
      <div class="detail-grid">
        <section>
          <h3>Dateianhaenge</h3>
          <p class="muted">Teile Briefings, Referenzen oder Ergebnisse.</p>
          <ul v-if="taskAttachments[activeTask.id]?.length" class="attachment-list">
            <li v-for="file in taskAttachments[activeTask.id]" :key="file.id">
              <a :href="file.file_url" target="_blank" rel="noopener">
                {{ file.label || file.file_name || "Datei" }}
              </a>
              <small class="muted">{{ file.uploaded_by?.name || file.uploaded_by?.username }}</small>
              <button class="iconbtn danger" type="button" @click="removeTaskAttachment(activeTask.id, file.id)">X</button>
            </li>
          </ul>
          <p v-else class="muted">Noch keine Anhaenge.</p>
          <form class="upload-row" @submit.prevent="uploadTaskAttachment(activeTask.id)">
            <input
              class="input"
              v-model.trim="taskAttachmentDraft(activeTask.id).label"
              placeholder="Kurzbeschreibung"
            />
            <label class="file-picker">
              <input type="file" @change="onTaskFile(activeTask.id, $event)" />
              {{
                taskAttachmentDraft(activeTask.id).file
                  ? taskAttachmentDraft(activeTask.id).file.name
                  : "Datei waehlen"
              }}
            </label>
            <button class="btn tiny" type="submit" :disabled="taskAttachmentLoading[activeTask.id]">
              {{ taskAttachmentLoading[activeTask.id] ? "Lade..." : "Hochladen" }}
            </button>
          </form>
        </section>

        <section>
          <h3>Kommentare</h3>
          <p class="muted">Nutze @-Mentions, um Teammitglieder zu informieren.</p>
          <div class="comment-list" v-if="taskComments[activeTask.id]?.length">
            <article v-for="comment in taskComments[activeTask.id]" :key="comment.id">
              <header>
                <strong>{{ comment.author?.name || comment.author?.username }}</strong>
                <span class="muted">{{ formatDate(comment.created_at) }}</span>
              </header>
              <p>{{ comment.body }}</p>
              <div v-if="comment.mention_profiles?.length" class="mentions">
                <span v-for="mention in comment.mention_profiles" :key="mention.id">@{{ mention.name || mention.username }}</span>
              </div>
            </article>
          </div>
          <p v-else class="muted">Noch keine Kommentare.</p>
          <form class="comment-form" @submit.prevent="addComment(activeTask.id)">
            <textarea class="input textarea" v-model.trim="taskCommentDraft(activeTask.id).body" placeholder="Kommentar"></textarea>
            <label>
              Mentions
              <select class="input" v-model="taskCommentDraft(activeTask.id).mentions" multiple size="4">
                <option v-for="profile in teamProfiles" :key="profile.id" :value="profile.id">
                  {{ profile.name }}
                </option>
              </select>
            </label>
            <button class="btn tiny" type="submit" :disabled="commentLoading[activeTask.id]">
              {{ commentLoading[activeTask.id] ? "Speichere..." : "Kommentieren" }}
            </button>
          </form>
        </section>
      </div>
    </section>

    <div v-if="showFilterModal" class="modal-backdrop" @click.self="closeFilterModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Filter</h3>
          <button class="btn ghost tiny" type="button" @click="closeFilterModal">Schliessen</button>
        </div>
        <form class="form" @submit.prevent="applyFilters">
          <label>
            Suche
            <input class="input" v-model.trim="searchTasks" placeholder="Titel oder Projekt" />
          </label>
          <label>
            Projekt
            <select class="input" v-model="filterProject">
              <option value="ALL">Alle</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Status
            <select class="input" v-model="filterStatus">
              <option value="ALL">Alle</option>
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Prioritaet
            <select class="input" v-model="priorityFilter">
              <option value="ALL">Alle</option>
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Sortierung
            <select class="input" v-model="sortOrder">
              <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </label>
          <div class="due-chips">
            <button
              v-for="option in dueFilterOptions"
              :key="option.key"
              type="button"
              class="chip"
              :class="{ active: dueFilter === option.key }"
              @click="dueFilter = option.key"
            >
              {{ option.label }}
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
            <button class="btn ghost" type="button" @click="resetFilters">Zuruecksetzen</button>
            <button class="btn" type="submit">Anwenden</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal-backdrop" @click.self="closeCreateModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Neue Aufgabe</h3>
          <button class="btn ghost tiny" type="button" @click="closeCreateModal" :disabled="creating">Schliessen</button>
        </div>
        <form class="form" @submit.prevent="createTask">
          <label>
            Titel
            <input class="input" v-model.trim="newTask.title" placeholder="z. B. Mix finalisieren" required />
          </label>
          <label>
            Projekt (optional)
            <select class="input" v-model="newTask.project">
              <option value="">Kein Projekt</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Status
            <select class="input" v-model="newTask.status">
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Prioritaet
            <select class="input" v-model="newTask.priority">
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Faellig am
            <input class="input" type="date" v-model="newTask.due_date" />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeCreateModal" :disabled="creating">Abbrechen</button>
            <button class="btn" type="submit" :disabled="creating">
              {{ creating ? "Speichere..." : "Task anlegen" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const projects = ref([]);
const tasks = ref([]);
const projectMap = computed(() =>
  projects.value.reduce((acc, project) => {
    acc[project.id] = project;
    return acc;
  }, {})
);

const loadingTasks = ref(false);
const loadingProjects = ref(false);
const creating = ref(false);
const showCreateModal = ref(false);
const showFilterModal = ref(false);
const showArchived = ref(false);
const showCompleted = ref(false);
const taskSummary = ref({
  total: 0,
  archived: 0,
  active: 0,
  done: 0,
  by_status: {},
});

const newTask = ref({
  title: "",
  project: "",
  status: "OPEN",
  priority: "MEDIUM",
  due_date: "",
});
function resetNewTask() {
  newTask.value = { title: "", project: "", status: "OPEN", priority: "MEDIUM", due_date: "" };
}
const filterProject = ref("ALL");
const filterStatus = ref("ALL");
const priorityFilter = ref("ALL");
const dueFilter = ref("ALL");
const searchTasks = ref("");
const sortOrder = ref("-due_date");
const dueFilterOptions = [
  { key: "ALL", label: "Alle Termine" },
  { key: "overdue", label: "Ueberfaellig" },
  { key: "soon", label: "In 48 Stunden" },
  { key: "scheduled", label: "Spaeter" },
  { key: "none", label: "Ohne Termin" },
];
const sortOptions = [
  { value: "-due_date", label: "Faelligkeit absteigend" },
  { value: "due_date", label: "Faelligkeit aufsteigend" },
  { value: "-priority", label: "Prioritaet hoch zuerst" },
  { value: "priority", label: "Prioritaet niedrig zuerst" },
  { value: "-created_at", label: "Neueste zuerst" },
];

const statusOptions = ["OPEN", "IN_PROGRESS", "REVIEW", "DONE"];
const statusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Fertig",
};
const priorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const priorityLabels = {
  LOW: "Niedrig",
  MEDIUM: "Mittel",
  HIGH: "Hoch",
  CRITICAL: "Kritisch",
};

function resetFilters() {
  searchTasks.value = "";
  filterProject.value = "ALL";
  filterStatus.value = "ALL";
  priorityFilter.value = "ALL";
  dueFilter.value = "ALL";
  showCompleted.value = false;
  showArchived.value = false;
  sortOrder.value = "-due_date";
}

const filteredTasks = computed(() => tasks.value);
const boardColumns = computed(() =>
  statusOptions.map((status) => ({
    key: status,
    label: statusLabels[status],
    items: filteredTasks.value
      .filter((task) => task.status === status)
      .slice()
      .sort((a, b) => compareDueDates(a.due_date, b.due_date)),
  }))
);
const statusProgress = computed(() =>
  statusOptions.map((status) => ({
    key: status,
    label: statusLabels[status],
    count: taskSummary.value.by_status?.[status] || 0,
  }))
);

const teamProfiles = ref([]);
const activeTaskId = ref(null);
const activeTask = computed(() => tasks.value.find((task) => task.id === activeTaskId.value) || null);
const taskAttachments = ref({});
const taskAttachmentLoading = ref({});
const taskComments = ref({});
const commentLoading = ref({});
const attachmentDrafts = ref({});
const commentDrafts = ref({});
let searchDebounce;

function taskAttachmentDraft(taskId) {
  if (!attachmentDrafts.value[taskId]) {
    attachmentDrafts.value[taskId] = { label: "", file: null };
  }
  return attachmentDrafts.value[taskId];
}

function taskCommentDraft(taskId) {
  if (!commentDrafts.value[taskId]) {
    commentDrafts.value[taskId] = { body: "", mentions: [] };
  }
  return commentDrafts.value[taskId];
}

function compareDueDates(a, b) {
  if (!a && !b) return 0;
  if (!a) return 1;
  if (!b) return -1;
  return new Date(a) - new Date(b);
}

function formatDueDate(value) {
  if (!value) return "Kein Termin";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function dueState(task) {
  if (!task.due_date) return "none";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(task.due_date);
  due.setHours(0, 0, 0, 0);
  const diff = (due - today) / (1000 * 60 * 60 * 24);
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "scheduled";
}

function buildDueParams() {
  const today = new Date();
  const params = {};
  const format = (date) => date.toISOString().slice(0, 10);
  if (dueFilter.value === "overdue") {
    params.due_before = format(today);
  } else if (dueFilter.value === "soon") {
    params.due_after = format(today);
    const future = new Date(today);
    future.setDate(future.getDate() + 2);
    params.due_before = format(future);
  } else if (dueFilter.value === "scheduled") {
    const future = new Date(today);
    future.setDate(future.getDate() + 2);
    params.due_after = format(future);
  } else if (dueFilter.value === "none") {
    params.due_state = "none";
  }
  return params;
}

async function loadProjects() {
  if (!isTeam.value) return;
  loadingProjects.value = true;
  try {
    const { data } = await api.get("projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Projekte fuer Tasks konnten nicht geladen werden", err);
    projects.value = [];
  } finally {
    loadingProjects.value = false;
  }
}

async function loadTasks() {
  if (!isTeam.value) return;
  loadingTasks.value = true;
  try {
    const params = {
      include_archived: showArchived.value ? 1 : 0,
      include_done: showCompleted.value ? 1 : 0,
      project: filterProject.value !== "ALL" ? filterProject.value : undefined,
      status: filterStatus.value !== "ALL" ? filterStatus.value : undefined,
      priority: priorityFilter.value !== "ALL" ? priorityFilter.value : undefined,
      search: searchTasks.value.trim() || undefined,
      ordering: sortOrder.value,
      ...buildDueParams(),
    };
    const { data } = await api.get("tasks/", { params });
    tasks.value = data;
    if (activeTaskId.value && !tasks.value.find((task) => task.id === activeTaskId.value)) {
      activeTaskId.value = null;
    }
  } catch (err) {
    console.error("Tasks konnten nicht geladen werden", err);
  } finally {
    loadingTasks.value = false;
  }
}

async function loadTaskSummary() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("tasks/summary/");
    taskSummary.value = {
      total: data.total || 0,
      archived: data.archived || 0,
      active: data.active || 0,
      done: data.done || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    console.error("Task-Statistiken konnten nicht geladen werden", err);
    taskSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {} };
  }
}

async function refreshTasks() {
  await Promise.all([loadTasks(), loadTaskSummary()]);
}

async function createTask() {
  if (!newTask.value.title) return;
  creating.value = true;
  try {
    const payload = { ...newTask.value };
    if (!payload.project) delete payload.project;
    await api.post("tasks/", payload);
    newTask.value = { title: "", project: "", status: "OPEN", priority: "MEDIUM", due_date: "" };
    await refreshTasks();
    showCreateModal.value = false;
  } catch (err) {
    console.error("Task konnte nicht erstellt werden", err);
  } finally {
    creating.value = false;
  }
}

function openCreateModal() {
  showCreateModal.value = true;
}
function closeCreateModal() {
  if (creating.value) return;
  showCreateModal.value = false;
}

function openFilterModal() {
  showFilterModal.value = true;
}
function closeFilterModal() {
  showFilterModal.value = false;
}
function applyFilters() {
  loadTasks();
  closeFilterModal();
}

async function updateStatus(task) {
  try {
    await api.patch(`tasks/${task.id}/`, { status: task.status });
    await loadTaskSummary();
  } catch (err) {
    console.error("Task-Status konnte nicht aktualisiert werden", err);
  }
}

async function archiveTask(task) {
  if (!confirm(`Task "${task.title}" archivieren?`)) return;
  try {
    await api.delete(`tasks/${task.id}/`);
    await refreshTasks();
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
  }
}

async function loadProfiles() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("profiles/");
    teamProfiles.value = data.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    teamProfiles.value = [];
  }
}

function openTask(task) {
  activeTaskId.value = task.id;
  ensureTaskAttachments(task.id);
  ensureTaskComments(task.id);
}

async function ensureTaskAttachments(taskId, force = false) {
  if (!force && taskAttachments.value[taskId]) return;
  taskAttachmentLoading.value[taskId] = true;
  try {
    const { data } = await api.get("task-attachments/", { params: { task: taskId } });
    taskAttachments.value = { ...taskAttachments.value, [taskId]: data };
  } catch (err) {
    console.error("Task-Anhaenge konnten nicht geladen werden", err);
  } finally {
    taskAttachmentLoading.value[taskId] = false;
  }
}

function onTaskFile(taskId, event) {
  const draft = taskAttachmentDraft(taskId);
  draft.file = event.target.files?.[0] || null;
}

async function uploadTaskAttachment(taskId) {
  const draft = taskAttachmentDraft(taskId);
  if (!draft.file) return;
  taskAttachmentLoading.value[taskId] = true;
  try {
    const formData = new FormData();
    formData.append("task", taskId);
    formData.append("label", draft.label);
    formData.append("file", draft.file);
    await api.post("task-attachments/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    draft.label = "";
    draft.file = null;
    await ensureTaskAttachments(taskId, true);
  } catch (err) {
    console.error("Task-Anhang konnte nicht gespeichert werden", err);
  } finally {
    taskAttachmentLoading.value[taskId] = false;
  }
}

async function removeTaskAttachment(taskId, attachmentId) {
  if (!confirm("Anhang entfernen?")) return;
  taskAttachmentLoading.value[taskId] = true;
  try {
    await api.delete(`task-attachments/${attachmentId}/`);
    await ensureTaskAttachments(taskId, true);
  } catch (err) {
    console.error("Anhang konnte nicht geloescht werden", err);
  } finally {
    taskAttachmentLoading.value[taskId] = false;
  }
}

async function ensureTaskComments(taskId, force = false) {
  if (!force && taskComments.value[taskId]) return;
  commentLoading.value[taskId] = true;
  try {
    const { data } = await api.get("task-comments/", { params: { task: taskId } });
    taskComments.value = { ...taskComments.value, [taskId]: data };
  } catch (err) {
    console.error("Kommentare konnten nicht geladen werden", err);
  } finally {
    commentLoading.value[taskId] = false;
  }
}

async function addComment(taskId) {
  const draft = taskCommentDraft(taskId);
  if (!draft.body.trim()) return;
  commentLoading.value[taskId] = true;
  try {
    await api.post("task-comments/", {
      task: taskId,
      body: draft.body.trim(),
      mentions: draft.mentions,
    });
    draft.body = "";
    draft.mentions = [];
    await ensureTaskComments(taskId, true);
  } catch (err) {
    console.error("Kommentar konnte nicht gespeichert werden", err);
  } finally {
    commentLoading.value[taskId] = false;
  }
}

watch(
  () => [filterProject.value, filterStatus.value, priorityFilter.value, dueFilter.value, sortOrder.value, showArchived.value, showCompleted.value],
  () => {
    if (!isTeam.value) return;
    loadTasks();
  }
);

watch(
  () => searchTasks.value,
  () => {
    if (!isTeam.value) return;
    if (searchDebounce) clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => loadTasks(), 300);
  }
);

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await Promise.all([loadProjects(), loadProfiles(), refreshTasks()]);
  }
});

onBeforeUnmount(() => {
  if (searchDebounce) clearTimeout(searchDebounce);
});
</script>

<style scoped>
.tasks {
  display: flex;
  flex-direction: column;
  gap: 20px;
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
.content {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.content.single {
  width: 100%;
}
.sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.due-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.due-chips .chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
}
.due-chips .chip.active {
  border-color: var(--brand);
  color: var(--brand);
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
.board {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.progress-strip {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.progress-bar {
  display: flex;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.4);
}
.progress-bar .segment {
  height: 10px;
}
.progress-bar .segment[data-status="OPEN"] {
  background: #f59e0b;
}
.progress-bar .segment[data-status="IN_PROGRESS"] {
  background: #3b82f6;
}
.progress-bar .segment[data-status="REVIEW"] {
  background: #a855f7;
}
.progress-bar .segment[data-status="DONE"] {
  background: #10b981;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 14px;
  font-size: 13px;
  color: var(--muted);
}
.legend .dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-right: 4px;
}
.legend .dot[data-status="OPEN"] {
  background: #f59e0b;
}
.legend .dot[data-status="IN_PROGRESS"] {
  background: #3b82f6;
}
.legend .dot[data-status="REVIEW"] {
  background: #a855f7;
}
.legend .dot[data-status="DONE"] {
  background: #10b981;
}
.columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 18px;
  width: 100%;
  align-items: flex-start;
}
.columns ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.columns li {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-height: 160px;
}
.columns li.overdue {
  border-color: #dc2626;
}
.columns li.soon {
  border-color: #f97316;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.priority {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(99, 102, 241, 0.16);
  color: #4c1d95;
}
.priority[data-priority="HIGH"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.priority[data-priority="CRITICAL"] {
  background: rgba(239, 68, 68, 0.25);
  color: #b91c1c;
}
.priority[data-priority="LOW"] {
  background: rgba(34, 197, 94, 0.15);
  color: #15803d;
}
.due {
  font-size: 13px;
}
.due.overdue {
  color: #dc2626;
}
.due.soon {
  color: #ea580c;
}
.actions {
  display: flex;
  gap: 8px;
  align-items: center;
}
.actions .input {
  flex: 1;
}
.skeleton-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skeleton-card {
  height: 90px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-panel header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.eyebrow {
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin: 0;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
.attachment-list,
.comment-list {
  list-style: none;
  padding: 0;
  margin: 0 0 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
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
.comment-list article {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.comment-list header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--muted);
}
.mentions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
}
.mentions span {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
  border-radius: 999px;
  padding: 2px 8px;
}
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}
.iconbtn {
  border: none;
  background: transparent;
  cursor: pointer;
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
  .content {
    gap: 16px;
  }
}

@media (min-width: 1200px) {
  .columns {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

.board-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.board-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 999;
}
.modal {
  max-width: 520px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
</style>





