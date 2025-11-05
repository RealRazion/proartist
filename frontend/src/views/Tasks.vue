<template>
  <div class="tasks">
    <header class="card header">
      <div>
        <h1>Tasks</h1>
        <p class="muted">Verteile Aufgaben innerhalb deiner Projekte und behalte Fortschritte im Blick.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadTasks" :disabled="loadingTasks">
        {{ loadingTasks ? "Lade…" : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">
        Nur Team-Mitglieder können Aufgaben verwalten. Bitte wende dich an das Team, falls du Zugriff benötigst.
      </p>
    </section>

    <section v-else class="content">
      <form class="card form" @submit.prevent="createTask">
        <h2>Neue Aufgabe</h2>
        <label>
          Titel
          <input class="input" v-model.trim="newTask.title" placeholder="z. B. Mix finalisieren" required />
        </label>
        <label>
          Projekt
          <select class="input" v-model="newTask.project" required>
            <option value="" disabled>Projekt wählen</option>
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
          Fällig am
          <input class="input" type="date" v-model="newTask.due_date" />
        </label>
        <button class="btn" type="submit" :disabled="creating">
          {{ creating ? "Speichere…" : "Task anlegen" }}
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
        <div class="columns">
          <div v-for="column in boardColumns" :key="column.key">
            <h3>{{ column.label }}</h3>
            <ul>
              <li
                v-for="task in column.items"
                :key="task.id"
                :class="{ overdue: dueState(task) === 'overdue', soon: dueState(task) === 'soon' }"
              >
                <div class="title">{{ task.title }}</div>
                <p class="muted">
                  Projekt: {{ projectMap[task.project]?.title || "–" }}
                </p>
                <p class="due" :class="dueState(task)">
                  Fällig: {{ formatDueDate(task.due_date) }}
                </p>
                <select class="input status-select" v-model="task.status" @change="updateStatus(task)">
                  <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                </select>
              </li>
            </ul>
            <p v-if="!column.items.length" class="muted empty">Keine Tasks</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
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

const newTask = ref({
  title: "",
  project: "",
  status: "OPEN",
  due_date: "",
});
const filterProject = ref("ALL");
const filterStatus = ref("ALL");

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
    return matchesProject && matchesStatus;
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

async function loadProjects() {
  if (loadingProjects.value) return;
  loadingProjects.value = true;
  try {
    const { data } = await api.get("projects/");
    projects.value = data;
  } catch (err) {
    console.error("Projekte für Tasks konnten nicht geladen werden", err);
  } finally {
    loadingProjects.value = false;
  }
}

async function loadTasks() {
  if (loadingTasks.value) return;
  loadingTasks.value = true;
  try {
    const { data } = await api.get("tasks/");
    tasks.value = data;
  } catch (err) {
    console.error("Tasks konnten nicht geladen werden", err);
  } finally {
    loadingTasks.value = false;
  }
}

async function createTask() {
  if (!newTask.value.title || !newTask.value.project) return;
  creating.value = true;
  try {
    await api.post("tasks/", newTask.value);
    newTask.value = { title: "", project: "", status: "OPEN", due_date: "" };
    await loadTasks();
  } catch (err) {
    console.error("Task konnte nicht angelegt werden", err);
  } finally {
    creating.value = false;
  }
}

async function updateStatus(task) {
  try {
    await api.patch(`tasks/${task.id}/`, { status: task.status });
  } catch (err) {
    console.error("Task-Status konnte nicht aktualisiert werden", err);
    await loadTasks();
  }
}

function compareDueDates(a, b) {
  if (!a && !b) return 0;
  if (!a) return 1;
  if (!b) return -1;
  return new Date(a) - new Date(b);
}

function formatDueDate(value) {
  if (!value) return "Kein Datum";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "Kein Datum";
  return date.toLocaleDateString();
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
    await Promise.all([loadProjects(), loadTasks()]);
  }
});
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
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
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
</style>
