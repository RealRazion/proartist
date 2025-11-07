<template>
  <div class="tasks">
    <header class="card header">
      <div>
        <h1>Tasks</h1>
        <p class="muted">Verteile Aufgaben innerhalb deiner Projekte und behalte Fortschritte im Blick.</p>
      </div>
      <button class="btn ghost" type="button" @click="refreshTasks" :disabled="loadingTasks">
        {{ loadingTasks ? "Lade�" : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur f�r Team</h2>
      <p class="muted">
        Nur Team-Mitglieder k�nnen Aufgaben verwalten. Bitte wende dich an das Team, falls du Zugriff ben�tigst.
      </p>
    </section>

    <section v-else class="content">
      <form class="card form" @submit.prevent="createTask">
        <h2>Neue Aufgabe</h2>
        <label>
          Titel
          <input class="input" v-model.trim="newTask.title" placeholder="z.?B. Mix finalisieren" required />
        </label>
        <label>
          Projekt
          <select class="input" v-model="newTask.project" required>
            <option value="" disabled>Projekt w�hlen</option>
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
          Faellig am
          <input class="input" type="date" v-model="newTask.due_date" />
        </label>
        <button class="btn" type="submit" :disabled="creating">
          {{ creating ? "Speichere�" : "Task anlegen" }}
        </button>
      </form>

      <div class="card board">
        <h2>Task Board</h2>
        <div class="board-filters">
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
        </div>
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
                  <div class="title">{{ task.title }}</div>
                  <p class="muted">
                    Projekt: {{ projectMap[task.project]?.title || "-" }}
                  </p>
                  <p class="due" :class="dueState(task)">
                    Faellig: {{ formatDueDate(task.due_date) }}
                  </p>
                  <div class="task-actions">
                    <select class="input status-select" v-model="task.status" @change="updateStatus(task)">
                      <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                    </select>
                    <button class="btn ghost danger" type="button" @click="archiveTask(task)">
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

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
  due_date: "",
});
const filterProject = ref("ALL");
const filterStatus = ref("ALL");
const dueFilter = ref("ALL");
const dueFilterOptions = [
  { key: "ALL", label: "Alle Termine" },
  { key: "overdue", label: "Ueberfaellig" },
  { key: "soon", label: "In 48h" },
  { key: "scheduled", label: "Spaeter" },
  { key: "none", label: "Ohne Datum" },
];

const statusOptions = ["OPEN", "IN_PROGRESS", "REVIEW", "DONE"];
const statusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Fertig",
};

const filteredTasks = computed(() => {
  return tasks.value.filter((task) => {
    const matchesProject = filterProject.value === "ALL" || String(task.project) === String(filterProject.value);
    const matchesStatus = filterStatus.value === "ALL" || task.status === filterStatus.value;
    const dueKey = dueState(task);
    const matchesDue = dueFilter.value === "ALL" || dueFilter.value === dueKey;
    return matchesProject && matchesStatus && matchesDue;
  });
});

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

async function loadProjects() {
  if (!isTeam.value) return;
  if (loadingProjects.value) return;
  loadingProjects.value = true;
  try {
    const { data } = await api.get("projects/");
    projects.value = data;
  } catch (err) {
    console.error("Projekte fuer Tasks konnten nicht geladen werden", err);
    projects.value = [];
  } finally {
    loadingProjects.value = false;
  }
}

async function loadTasks() {
  if (!isTeam.value) return;
  if (loadingTasks.value) return;
  loadingTasks.value = true;
  try {
    const params = {
      include_archived: showArchived.value ? 1 : 0,
      include_done: showCompleted.value ? 1 : 0,
    };
    const { data } = await api.get("tasks/", { params });
    tasks.value = data;
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
  if (!newTask.value.title || !newTask.value.project) return;
  creating.value = true;
  try {
    await api.post("tasks/", newTask.value);
    newTask.value = { title: "", project: "", status: "OPEN", due_date: "" };
    await refreshTasks();
  } catch (err) {
    console.error("Task konnte nicht erstellt werden", err);
  } finally {
    creating.value = false;
  }
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

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await loadProjects();
    await refreshTasks();
  }
});

watch(
  () => [showArchived.value, showCompleted.value],
  () => {
    if (isTeam.value) {
      loadTasks();
    }
  }
);
</script>

<style scoped>
.tasks {
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
.content {
  display: grid;
  grid-template-columns: minmax(260px, 320px) 1fr;
  gap: 18px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.board {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.board-filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.visibility {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 13px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.due-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 8px;
}
.due-chips .chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  background: transparent;
  cursor: pointer;
  transition: background 0.2s ease, border 0.2s ease;
}
.due-chips .chip.active {
  background: rgba(220, 38, 38, 0.12);
  border-color: transparent;
  color: #dc2626;
}
.progress-strip {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}
.progress-bar {
  display: flex;
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  background: var(--border);
}
.progress-bar .segment {
  height: 100%;
}
.progress-bar .segment[data-status="OPEN"] {
  background: var(--brand);
}
.progress-bar .segment[data-status="IN_PROGRESS"] {
  background: #f97316;
}
.progress-bar .segment[data-status="REVIEW"] {
  background: #a855f7;
}
.progress-bar .segment[data-status="DONE"] {
  background: #22c55e;
}
.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: var(--muted);
}
.legend .dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 4px;
}
.legend .dot[data-status="OPEN"] {
  background: var(--brand);
}
.legend .dot[data-status="IN_PROGRESS"] {
  background: #f97316;
}
.legend .dot[data-status="REVIEW"] {
  background: #a855f7;
}
.legend .dot[data-status="DONE"] {
  background: #22c55e;
}
.task-actions {
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
.columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}
.columns ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}
.columns li {
  border: 1px solid rgba(75, 91, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  transition: border 0.2s ease, background 0.2s ease;
}
.columns li.overdue {
  border-color: rgba(220, 38, 38, 0.4);
  background: rgba(220, 38, 38, 0.08);
}
.columns li.soon {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.08);
}
.skeleton-column {
  display: grid;
  gap: 10px;
}
.skeleton-card {
  height: 80px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05) 25%, rgba(255,255,255,0.12) 37%, rgba(255,255,255,0.05) 63%);
  background-size: 400% 100%;
  animation: shimmer 1.4s ease infinite;
}
.title {
  font-weight: 600;
}
.status-select {
  font-size: 14px;
}
.due {
  font-size: 12px;
  color: var(--muted);
}
.due.overdue {
  color: #dc2626;
  font-weight: 600;
}
.due.soon {
  color: #f59e0b;
  font-weight: 600;
}
.empty {
  margin-top: 10px;
}

@media (max-width: 960px) {
  .content {
    grid-template-columns: 1fr;
  }
  .board-filters {
    grid-template-columns: 1fr;
  }
}

@keyframes shimmer {
  0% { background-position: -400px 0; }
  100% { background-position: 400px 0; }
}
</style>



