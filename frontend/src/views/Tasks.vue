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
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Nur Team-Mitglieder können Aufgaben verwalten. Bitte wende dich an das Team.</p>
    </section>

    <section v-else class="workspace" :class="{ 'has-detail': Boolean(activeTask) }">
      <div class="board card">
        <div class="board-head">
          <div>
            <h2>Task Board</h2>
            <p class="muted small">Filter und neue Aufgaben per Dialog.</p>
          </div>
          <div class="board-actions">
            <button class="btn ghost" type="button" @click="openFilterModal">Filter</button>
            <button class="btn" type="button" @click="openTaskModal" :disabled="taskSaving">Task erstellen</button>
          </div>
        </div>
        <p class="muted board-hint">Archivierte Tasks blendest du über die Filter wieder ein.</p>
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
                  class="task-card"
                  :class="{ overdue: dueState(task) === 'overdue', soon: dueState(task) === 'soon' }"
                >
                  <div class="title-row">
                    <div>
                      <div class="title">{{ task.title }}</div>
                      <div class="pill-row">
                        <span class="priority" :data-priority="task.priority">
                          {{ priorityLabels[task.priority] }}
                        </span>
                        <span class="task-type" :data-type="task.task_type">
                          {{ taskTypeLabels[task.task_type] || task.task_type }}
                        </span>
                      </div>
                    </div>
                    <div class="card-buttons">
                      <button class="btn ghost tiny" type="button" @click="openTask(task)">
                        Details
                      </button>
                      <button class="btn ghost tiny" type="button" @click="startEditTask(task)">
                        Bearbeiten
                      </button>
                    </div>
                  </div>
                  <p class="muted">
                    Projekt: {{ task.project ? projectMap[task.project]?.title || "-" : "Kein Projekt" }}
                  </p>
                  <p class="muted small-text">
                    Verantwortlich: {{ formatAssignees(task) }}
                  </p>
                  <p class="muted small-text">
                    Betroffene: {{ formatStakeholders(task) }}
                  </p>
                  <p class="due" :class="dueState(task)">
                    {{ task.due_date ? `Fällig ${formatDueDate(task.due_date)}` : "Kein Termin" }}
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
      <section v-if="activeTask" class="card detail-panel">
        <header>
          <div>
            <p class="eyebrow">Ausgewählter Task</p>
            <h2>{{ activeTask.title }}</h2>
            <p class="muted">
              Projekt: {{ activeTask.project ? projectMap[activeTask.project]?.title || "-" : "Kein Projekt" }}
            </p>
            <div class="detail-meta">
              <div>
                <span class="label">Typ</span>
                <strong>{{ taskTypeLabels[activeTask.task_type] || activeTask.task_type }}</strong>
              </div>
              <div>
                <span class="label">Verantwortlich</span>
                <strong>{{ formatAssignees(activeTask) }}</strong>
              </div>
              <div>
                <span class="label">Betroffene</span>
                <span>{{ formatStakeholders(activeTask) }}</span>
              </div>
              <div>
                <span class="label">Fällig</span>
                <span>{{ activeTask.due_date ? formatDueDate(activeTask.due_date) : "Kein Termin" }}</span>
              </div>
            </div>
          </div>
          <button class="btn ghost tiny" type="button" @click="activeTaskId = null">Schließen</button>
        </header>
        <div class="detail-grid">
          <section>
            <h3>Dateianhänge</h3>
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
            <p v-else class="muted">Noch keine Anhänge.</p>
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
                    : "Datei wählen"
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
            Priorität
            <select class="input" v-model="priorityFilter">
              <option value="ALL">Alle</option>
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Task-Typ
            <select class="input" v-model="taskTypeFilter">
              <option value="ALL">Alle</option>
              <option v-for="opt in taskTypeOptions" :key="opt" :value="opt">
                {{ taskTypeLabels[opt] }}
              </option>
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
            <button class="btn ghost" type="button" @click="resetFilters">Zurücksetzen</button>
            <button class="btn" type="submit">Anwenden</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="taskModalVisible" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>{{ taskModalMode === "create" ? "Neue Aufgabe" : "Task bearbeiten" }}</h3>
          <button class="btn ghost tiny" type="button" @click="closeTaskModal" :disabled="taskSaving">Schließen</button>
        </div>
        <form class="form" @submit.prevent="submitTaskForm">
          <label>
            Titel
            <input class="input" v-model.trim="taskForm.title" placeholder="z. B. Mix finalisieren" required />
          </label>
          <label>
            Projekt (optional)
            <select class="input" v-model="taskForm.project">
              <option value="">Kein Projekt</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Task-Typ
            <select class="input" v-model="taskForm.task_type">
              <option v-for="opt in taskTypeOptions" :key="opt" :value="opt">
                {{ taskTypeLabels[opt] }}
              </option>
            </select>
          </label>
          <label>
            Status
            <select class="input" v-model="taskForm.status">
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Priorität
            <select class="input" v-model="taskForm.priority">
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Verantwortliche (Team)
            <select class="input" v-model="taskForm.assignee_ids" multiple size="6">
              <option v-for="profile in teamProfiles" :key="`assignee-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Mehrfachauswahl mit Strg/Command möglich.</small>
          </label>
          <label>
            Betroffene Nutzer
            <select class="input" v-model="taskForm.stakeholder_ids" multiple size="6">
              <option v-for="profile in profiles" :key="`stake-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Mehrfachauswahl mit Strg/Command möglich.</small>
          </label>
          <label>
            Fällig am
            <input class="input" type="date" v-model="taskForm.due_date" />
          </label>
          <div v-if="taskModalMode === 'edit'" class="danger-zone">
            <p class="muted">Task archivieren oder komplett löschen.</p>
            <div class="danger-buttons">
              <button class="btn ghost danger" type="button" @click="archiveCurrentTask" :disabled="taskSaving">
                Archivieren
              </button>
              <button class="btn danger" type="button" @click="deleteCurrentTask" :disabled="taskSaving">
                Löschen
              </button>
            </div>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">
              {{
                taskSaving
                  ? "Speichere..."
                  : taskModalMode === "create"
                    ? "Task anlegen"
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
const showFilterModal = ref(false);
const showArchived = ref(false);
const showCompleted = ref(false);
const taskSummary = ref({
  total: 0,
  archived: 0,
  active: 0,
  done: 0,
  by_status: {},
  by_type: {},
});

const taskModalVisible = ref(false);
const taskModalMode = ref("create");
const taskSaving = ref(false);
const editingTaskId = ref(null);
const taskForm = ref(getDefaultTaskForm());

function getDefaultTaskForm() {
  return {
    title: "",
    project: "",
    status: "OPEN",
    priority: "MEDIUM",
    assignee_ids: [],
    stakeholder_ids: [],
    due_date: "",
    task_type: "EXTERNAL",
  };
}
const filterProject = ref("ALL");
const filterStatus = ref("ALL");
const priorityFilter = ref("ALL");
const dueFilter = ref("ALL");
const taskTypeFilter = ref("ALL");
const searchTasks = ref("");
const sortOrder = ref("-due_date");
const dueFilterOptions = [
  { key: "ALL", label: "Alle Termine" },
  { key: "overdue", label: "Überfällig" },
  { key: "soon", label: "In 48 Stunden" },
  { key: "scheduled", label: "Später" },
  { key: "none", label: "Ohne Termin" },
];
const sortOptions = [
  { value: "-due_date", label: "Fälligkeit absteigend" },
  { value: "due_date", label: "Fälligkeit aufsteigend" },
  { value: "-priority", label: "Priorität hoch zuerst" },
  { value: "priority", label: "Priorität niedrig zuerst" },
  { value: "-created_at", label: "Neueste zuerst" },
];

const statusOptions = ["OPEN", "IN_PROGRESS", "REVIEW", "DONE"];
const statusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Fertig",
};
const taskTypeOptions = ["INTERNAL", "EXTERNAL"];
const taskTypeLabels = {
  INTERNAL: "Intern",
  EXTERNAL: "Extern",
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
  taskTypeFilter.value = "ALL";
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

const profiles = ref([]);
const teamProfiles = computed(() =>
  profiles.value.filter((profile) =>
    (profile.roles || []).some((role) => role.key === "TEAM")
  )
);
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

function formatStakeholders(task) {
  if (!task?.stakeholders?.length) return "Keine";
  return task.stakeholders.map((profile) => profile.name || profile.username).join(", ");
}

function formatAssignees(task) {
  if (!task?.assignees?.length) return "Nicht zugewiesen";
  return task.assignees.map((profile) => profile.name || profile.username).join(", ");
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
    console.error("Projekte für Tasks konnten nicht geladen werden", err);
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
      task_type: taskTypeFilter.value !== "ALL" ? taskTypeFilter.value : undefined,
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
      by_type: data.by_type || {},
    };
  } catch (err) {
    console.error("Task-Statistiken konnten nicht geladen werden", err);
    taskSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {}, by_type: {} };
  }
}

async function refreshTasks() {
  await Promise.all([loadTasks(), loadTaskSummary()]);
}

async function submitTaskForm() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  const payload = {
    title: taskForm.value.title.trim(),
    status: taskForm.value.status,
    priority: taskForm.value.priority,
    task_type: taskForm.value.task_type,
    stakeholder_ids: taskForm.value.stakeholder_ids,
    assignee_ids: taskForm.value.assignee_ids,
  };
  if (taskForm.value.project) {
    payload.project = taskForm.value.project;
  }
  if (taskForm.value.due_date) {
    payload.due_date = taskForm.value.due_date;
  } else {
    payload.due_date = null;
  }
  try {
    if (taskModalMode.value === "edit" && editingTaskId.value) {
      await api.patch(`tasks/${editingTaskId.value}/`, payload);
    } else {
      await api.post("tasks/", payload);
    }
    await refreshTasks();
    taskModalVisible.value = false;
  } catch (err) {
    console.error("Task konnte nicht gespeichert werden", err);
  } finally {
    taskSaving.value = false;
  }
}

function openTaskModal() {
  taskModalMode.value = "create";
  editingTaskId.value = null;
  taskForm.value = { ...getDefaultTaskForm() };
  taskModalVisible.value = true;
}
function closeTaskModal() {
  if (taskSaving.value) return;
  taskModalVisible.value = false;
}

function startEditTask(task) {
  taskModalMode.value = "edit";
  editingTaskId.value = task.id;
  taskForm.value = {
    title: task.title,
    project: task.project || "",
    status: task.status,
    priority: task.priority,
    assignee_ids: task.assignees?.map((p) => p.id) || [],
    stakeholder_ids: task.stakeholders?.map((p) => p.id) || [],
    due_date: task.due_date || "",
    task_type: task.task_type || "EXTERNAL",
  };
  taskModalVisible.value = true;
}

async function archiveCurrentTask() {
  if (!editingTaskId.value) return;
  if (!confirm(`Task "${taskForm.value.title}" archivieren?`)) return;
  taskSaving.value = true;
  try {
    await api.post(`tasks/${editingTaskId.value}/archive/`);
    await refreshTasks();
    taskModalVisible.value = false;
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
  } finally {
    taskSaving.value = false;
  }
}

async function deleteCurrentTask() {
  if (!editingTaskId.value) return;
  if (!confirm(`Task "${taskForm.value.title}" endgültig löschen?`)) return;
  taskSaving.value = true;
  try {
    try {
      await api.post(`tasks/${editingTaskId.value}/delete/`);
    } catch (err) {
      await api.delete(`tasks/${editingTaskId.value}/`);
    }
    await refreshTasks();
    taskModalVisible.value = false;
  } catch (err) {
    console.error("Task konnte nicht gelöscht werden", err);
  } finally {
    taskSaving.value = false;
  }
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
    await api.post(`tasks/${task.id}/archive/`);
    await refreshTasks();
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
  }
}

async function loadProfiles() {
  if (!isTeam.value) return;
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
    profiles.value = [];
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
    console.error("Task-Anhänge konnten nicht geladen werden", err);
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
    console.error("Anhang konnte nicht gelöscht werden", err);
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
  () => [
    filterProject.value,
    filterStatus.value,
    priorityFilter.value,
    dueFilter.value,
    taskTypeFilter.value,
    sortOrder.value,
    showArchived.value,
    showCompleted.value,
  ],
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
  gap: 24px;
}
.card {
  border-radius: 22px;
  border: 1px solid rgba(15, 23, 42, 0.08);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(241, 245, 249, 0.88));
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
  padding: 22px;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.info {
  max-width: 600px;
}
.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px;
}
.workspace.has-detail {
  grid-template-columns: minmax(0, 2.1fr) minmax(320px, 1fr);
  align-items: flex-start;
}
.board {
  display: flex;
  flex-direction: column;
  gap: 16px;
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
.board-hint {
  font-size: 13px;
  margin-top: -8px;
}
.progress-strip {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.progress-bar {
  display: flex;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.35);
}
.progress-bar .segment {
  height: 12px;
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
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
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
.empty {
  text-align: center;
  padding: 12px 0;
}
.task-card {
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 170px;
  background: rgba(255, 255, 255, 0.9);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease;
}
.task-card:hover {
  transform: translateY(-3px);
}
.task-card.overdue {
  border-color: #dc2626;
}
.task-card.soon {
  border-color: #f97316;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.title-row .title {
  font-size: 17px;
  font-weight: 600;
}
.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.priority,
.task-type {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.priority {
  background: rgba(99, 102, 241, 0.16);
  color: #4c1d95;
}
.priority[data-priority="HIGH"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.priority[data-priority="CRITICAL"] {
  background: rgba(239, 68, 68, 0.26);
  color: #7f1d1d;
}
.priority[data-priority="LOW"] {
  background: rgba(34, 197, 94, 0.18);
  color: #15803d;
}
.task-type {
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}
.task-type[data-type="INTERNAL"] {
  background: rgba(248, 113, 113, 0.22);
  color: #b91c1c;
}
.card-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}
.small-text {
  font-size: 13px;
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
  border-radius: 14px;
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
  align-items: flex-start;
  gap: 12px;
}
.detail-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
  margin-top: 8px;
}
.detail-meta .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  display: block;
}
.detail-meta strong,
.detail-meta span {
  display: block;
  font-size: 13px;
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
  border: 1px dashed rgba(148, 163, 184, 0.7);
  border-radius: 10px;
  padding: 6px 12px;
  font-size: 13px;
  cursor: pointer;
}
.file-picker input {
  display: none;
}
select[multiple] {
  min-height: 150px;
}
.comment-list article {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
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
.due-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.due-chips .chip {
  border: 1px solid rgba(148, 163, 184, 0.5);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.due-chips .chip.active {
  border-color: #2563eb;
  color: #2563eb;
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
  max-width: 560px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 26px;
  padding: 24px;
  background: linear-gradient(140deg, rgba(255, 255, 255, 0.98), rgba(241, 245, 249, 0.92));
  box-shadow: 0 40px 80px rgba(15, 23, 42, 0.35);
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
  font-weight: 400;
}
.textarea {
  min-height: 110px;
  resize: vertical;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}
.danger-zone {
  border: 1px dashed rgba(220, 38, 38, 0.4);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(248, 113, 113, 0.08);
}
.danger-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
@media (max-width: 1100px) {
  .workspace.has-detail {
    grid-template-columns: minmax(0, 1fr);
  }
}
@media (max-width: 720px) {
  .columns {
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  }
  .modal {
    padding: 18px;
  }
}
</style>
