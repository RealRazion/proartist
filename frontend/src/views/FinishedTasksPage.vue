<template>
  <div class="finished-tasks">
    <header class="card header">
      <div>
        <h1>Erledigte Tasks</h1>
        <p class="muted">Alle abgeschlossenen Aufgaben im Überblick</p>
      </div>
      <div class="board-actions">
        <button class="btn ghost" type="button" @click="refreshTasks" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
        <button class="btn ghost" type="button" @click="$router.back()">Zurück</button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Nur Team-Mitglieder können Tasks sehen. Bitte wende dich an das Team.</p>
    </section>

    <section v-else class="filters card">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="searchQuery" placeholder="Task oder Projekt" />
        </label>
        <label>
          Projekt
          <select class="input" v-model="filterProject">
            <option value="ALL">Alle Projekte</option>
            <option v-for="project in projects" :key="project.id" :value="project.id">
              {{ project.title }}
            </option>
          </select>
        </label>
        <label>
          Sortierung
          <select class="input" v-model="sortOrder">
            <option value="-completed_at">Neuste zuerst</option>
            <option value="completed_at">Älteste zuerst</option>
            <option value="title">Name (A-Z)</option>
            <option value="-title">Name (Z-A)</option>
          </select>
        </label>
      </div>
    </section>

    <section v-if="isTeam && filteredTasks.length === 0" class="card info">
      <p class="muted">Keine erledigten Tasks gefunden.</p>
    </section>

    <section v-else-if="isTeam" class="card task-list-shell">
      <div class="stats-row">
        <div class="stat">
          <span class="label">Gesamt</span>
          <strong>{{ totalCount }}</strong>
        </div>
        <div class="stat">
          <span class="label">Geprüft</span>
          <strong>{{ reviewedCount }}</strong>
        </div>
        <div class="stat warning">
          <span class="label">Nicht geprüft</span>
          <strong>{{ notReviewedCount }}</strong>
        </div>
      </div>

      <div class="task-table">
        <div class="table-head">
          <div class="col-title">Task</div>
          <div class="col-project">Projekt</div>
          <div class="col-review">Review Status</div>
          <div class="col-date">Abgeschlossen am</div>
          <div class="col-actions">Aktionen</div>
        </div>

        <div v-for="task in displayTasks" :key="task.id" class="table-row">
          <div class="col-title">
            <strong>{{ task.title }}</strong>
          </div>
          <div class="col-project">
            <span class="muted small">{{ task.project_title || "-" }}</span>
          </div>
          <div class="col-review">
            <span class="badge" :class="{ 'badge-reviewed': task.review_status === 'REVIEWED' }">
              {{ reviewStatusLabel(task.review_status) }}
            </span>
          </div>
          <div class="col-date">
            <span class="muted small">{{ formatDate(task.completed_at) }}</span>
          </div>
          <div class="col-actions">
            <button class="btn tiny ghost" type="button" @click="navigateToTask(task)">
              Öffnen
            </button>
            <button v-if="task.status === 'DONE'" class="btn tiny ghost danger" type="button" @click="resetTask(task)">
              Zurücksetzen
            </button>
          </div>
        </div>
      </div>

      <div v-if="hasMore" class="pagination">
        <button class="btn ghost" type="button" @click="loadMore" :disabled="loading">
          {{ loading ? "Laden..." : "Mehr anzeigen" }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { isTeam } = useCurrentProfile();
const router = useRouter();
const { showToast } = useToast();

const tasks = ref([]);
const projects = ref([]);
const loading = ref(false);
const searchQuery = ref("");
const filterProject = ref("ALL");
const sortOrder = ref("-completed_at");
const nextPageUrl = ref(null);
const pageSize = ref(50);

onMounted(async () => {
  await Promise.all([loadProjects(), loadTasks()]);
});

async function loadProjects() {
  try {
    const { data } = await api.get("projects/");
    const normalized = data.results || data.items || [];
    projects.value = Array.isArray(normalized) ? normalized : [];
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
  }
}

async function loadTasks() {
  if (!isTeam.value) return;
  if (loading.value) return;
  
  loading.value = true;
  try {
    const params = {
      include_done: 1,
      status: "DONE",
      ordering: sortOrder.value,
      project: filterProject.value !== "ALL" ? filterProject.value : undefined,
      search: searchQuery.value || undefined,
    };
    
    const { data } = await api.get("tasks/", { params });
    const normalized = data.results || data.items || [];
    tasks.value = Array.isArray(normalized) ? normalized : [];
    nextPageUrl.value = data.next || null;
  } catch (err) {
    console.error("Tasks konnten nicht geladen werden", err);
    showToast("Tasks konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function loadMore() {
  if (!nextPageUrl.value || loading.value) return;
  
  loading.value = true;
  try {
    const { data } = await api.get(nextPageUrl.value);
    const normalized = data.results || data.items || [];
    tasks.value = tasks.value.concat(Array.isArray(normalized) ? normalized : []);
    nextPageUrl.value = data.next || null;
  } catch (err) {
    console.error("Mehr Tasks konnten nicht geladen werden", err);
    showToast("Mehr Tasks konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function refreshTasks() {
  tasks.value = [];
  nextPageUrl.value = null;
  await loadTasks();
}

async function resetTask(task) {
  if (!confirm(`Task "${task.title}" zurücksetzen?`)) return;
  
  try {
    await api.patch(`tasks/${task.id}/`, { status: "OPEN" });
    showToast("Task zurückgesetzt", "success");
    tasks.value = tasks.value.filter(t => t.id !== task.id);
  } catch (err) {
    console.error("Task konnte nicht zurückgesetzt werden", err);
    const errorDetail = err.response?.data?.detail || err.message || "Unbekannter Fehler";
    showToast(`Task konnte nicht zurückgesetzt werden: ${errorDetail}`, "error");
  }
}

function navigateToTask(task) {
  if (task.project) {
    router.push({ name: "project-detail", params: { projectId: task.project }, query: { taskId: task.id } });
  } else {
    router.push({ name: "tasks", query: { taskId: task.id } });
  }
}

const filteredTasks = computed(() => {
  return tasks.value.filter(task => {
    if (searchQuery.value && !task.title.toLowerCase().includes(searchQuery.value.toLowerCase())) {
      return false;
    }
    if (filterProject.value !== "ALL" && task.project !== parseInt(filterProject.value)) {
      return false;
    }
    return true;
  });
});

const displayTasks = computed(() => {
  const sorted = [...filteredTasks.value];
  if (sortOrder.value === "-completed_at") {
    return sorted.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at));
  }
  if (sortOrder.value === "completed_at") {
    return sorted.sort((a, b) => new Date(a.completed_at) - new Date(b.completed_at));
  }
  if (sortOrder.value === "title") {
    return sorted.sort((a, b) => a.title.localeCompare(b.title));
  }
  if (sortOrder.value === "-title") {
    return sorted.sort((a, b) => b.title.localeCompare(a.title));
  }
  return sorted;
});

const totalCount = computed(() => tasks.value.length);
const reviewedCount = computed(() => tasks.value.filter(t => t.review_status === "REVIEWED").length);
const notReviewedCount = computed(() => tasks.value.filter(t => t.review_status === "NOT_REVIEWED").length);
const hasMore = computed(() => Boolean(nextPageUrl.value));

const reviewStatusLabel = (status) => {
  const labels = {
    REVIEWED: "Geprüft ✓",
    NOT_REVIEWED: "Nicht geprüft",
  };
  return labels[status] || "-";
};

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("de-DE", { month: "short", day: "numeric", year: "numeric" });
}
</script>

<style scoped>
.finished-tasks {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.board-actions {
  display: flex;
  gap: 8px;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.filter-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-row label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
  min-width: 200px;
}

.filter-row .input {
  padding: 8px 12px;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  font-size: 14px;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.stat {
  padding: 12px;
  background: var(--color-bg-secondary);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat .label {
  font-size: 12px;
  color: var(--color-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat strong {
  font-size: 24px;
  color: var(--status-in-progress);
}

.stat.warning strong {
  color: var(--status-soon);
}

.task-list-shell {
  padding: 16px;
}

.task-table {
  border-collapse: collapse;
  width: 100%;
}

.table-head {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr 1fr;
  gap: 12px;
  padding: 12px;
  background: var(--color-bg-secondary);
  border-radius: 8px 8px 0 0;
  font-weight: 600;
  font-size: 13px;
  border-bottom: 1px solid var(--color-border);
}

.table-row {
  display: grid;
  grid-template-columns: 2fr 1.5fr 1fr 1.5fr 1fr;
  gap: 12px;
  padding: 12px;
  border-bottom: 1px solid var(--color-border);
  align-items: center;
}

.table-row:hover {
  background: var(--color-bg-secondary);
}

.col-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.col-title strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-project,
.col-date {
  font-size: 13px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.col-review {
  text-align: center;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  background: color-mix(in srgb, var(--status-overdue) 16%, transparent);
  color: var(--status-overdue);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.badge-reviewed {
  background: color-mix(in srgb, var(--status-done) 16%, transparent);
  color: var(--status-done);
}

.col-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
}

.col-actions .btn {
  white-space: nowrap;
  font-size: 12px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.info {
  padding: 24px;
  text-align: center;
  color: var(--color-muted);
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }

  .board-actions {
    width: 100%;
  }

  .board-actions button {
    flex: 1;
  }

  .filter-row {
    flex-direction: column;
  }

  .filter-row label {
    min-width: unset;
  }

  .table-head,
  .table-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .col-project,
  .col-date,
  .col-review,
  .col-actions {
    display: none;
  }

  .col-title {
    grid-column: 1;
  }
}
</style>
