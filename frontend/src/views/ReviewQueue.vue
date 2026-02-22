<template>
  <div class="reviews">
    <header class="card hero">
      <div>
        <p class="eyebrow">Review</p>
        <h1>Review Queue</h1>
        <p class="muted">Tasks, die im Review sind oder noch bestaetigt werden muessen.</p>
      </div>
      <button class="btn ghost" type="button" @click="refresh" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur fuer Team</h2>
      <p class="muted">Review-Queues sind nur fuer Team-Mitglieder sichtbar.</p>
    </section>

    <section v-if="isTeam" class="filters card">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="filters.search" placeholder="Task oder Projekt" />
        </label>
        <label>
          Frist
          <select class="input" v-model="filters.due">
            <option value="ALL">Alle</option>
            <option value="overdue">Ueberfaellig</option>
            <option value="soon">Faellig (2 Tage)</option>
            <option value="ok">Im Plan</option>
          </select>
        </label>
        <label class="toggle">
          <input type="checkbox" v-model="filters.onlyMine" />
          Nur meine Tasks
        </label>
      </div>
    </section>

    <section v-if="isTeam" class="grid">
      <article class="card panel">
        <div class="panel-head">
          <div>
            <h2>Review faellig</h2>
            <p class="muted small">Status REVIEW</p>
          </div>
          <span class="pill">{{ reviewTasks.length }}</span>
        </div>
        <div class="bulk-actions" v-if="filteredReviewTasks.length">
          <label class="toggle">
            <input type="checkbox" :checked="allReviewSelected" @change="toggleAllReview($event)" />
            Alle markieren
          </label>
          <div class="bulk-buttons">
            <button class="btn tiny" type="button" @click="bulkReviewed" :disabled="!selectedReviewIds.length">
              Markiert als reviewed
            </button>
            <button class="btn ghost tiny danger" type="button" @click="bulkNotReviewed" :disabled="!selectedReviewIds.length">
              Markiert als nicht reviewed
            </button>
          </div>
        </div>
        <ul v-if="filteredReviewTasks.length" class="task-list">
          <li v-for="task in filteredReviewTasks" :key="task.id" class="task-item">
            <div class="task-main">
              <label class="check">
                <input type="checkbox" :value="task.id" v-model="selectedReviewIds" />
              </label>
              <div>
                <strong>{{ task.title }}</strong>
                <p class="muted small">
                  {{ task.project_title || "Kein Projekt" }}
                  <span class="dot">·</span>
                  {{ task.due_date ? formatDate(task.due_date) : "Kein Termin" }}
                </p>
                <p class="muted tiny">Verantwortlich: {{ formatAssignees(task) }}</p>
              </div>
              <span class="badge" :data-status="dueStatus(task)">{{ dueStatusLabel(task) }}</span>
            </div>
            <div class="task-actions">
              <button class="btn tiny" type="button" @click="markReviewed(task)">Reviewed</button>
              <button class="btn ghost tiny danger" type="button" @click="markNotReviewed(task)">Nicht reviewed</button>
              <button class="btn ghost tiny" type="button" @click="goToTask(task)">Zur Task</button>
            </div>
          </li>
        </ul>
        <p v-else class="muted small">Aktuell keine Review-Tasks.</p>
      </article>

      <article class="card panel">
        <div class="panel-head">
          <div>
            <h2>Nicht reviewed</h2>
            <p class="muted small">DONE + NOT_REVIEWED</p>
          </div>
          <span class="pill warning">{{ pendingReviewTasks.length }}</span>
        </div>
        <div class="bulk-actions" v-if="filteredPendingTasks.length">
          <label class="toggle">
            <input type="checkbox" :checked="allPendingSelected" @change="toggleAllPending($event)" />
            Alle markieren
          </label>
          <div class="bulk-buttons">
            <button class="btn tiny" type="button" @click="bulkReviewed" :disabled="!selectedPendingIds.length">
              Markiert als reviewed
            </button>
          </div>
        </div>
        <ul v-if="filteredPendingTasks.length" class="task-list">
          <li v-for="task in filteredPendingTasks" :key="task.id" class="task-item">
            <div class="task-main">
              <label class="check">
                <input type="checkbox" :value="task.id" v-model="selectedPendingIds" />
              </label>
              <div>
                <strong>{{ task.title }}</strong>
                <p class="muted small">
                  {{ task.project_title || "Kein Projekt" }}
                  <span class="dot">·</span>
                  {{ task.due_date ? formatDate(task.due_date) : "Kein Termin" }}
                </p>
                <p class="muted tiny">Verantwortlich: {{ formatAssignees(task) }}</p>
              </div>
              <span class="badge danger">Nicht reviewed</span>
            </div>
            <div class="task-actions">
              <button class="btn tiny" type="button" @click="markReviewed(task)">Reviewed</button>
              <button class="btn ghost tiny" type="button" @click="goToTask(task)">Zur Task</button>
            </div>
          </li>
        </ul>
        <p v-else class="muted small">Keine offenen Review-Bestaetigungen.</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, profile: me } = useCurrentProfile();
const { showToast } = useToast();
const router = useRouter();

const reviewTasks = ref([]);
const pendingReviewTasks = ref([]);
const loading = ref(false);
const filters = ref({ search: "", due: "ALL", onlyMine: false });
const selectedReviewIds = ref([]);
const selectedPendingIds = ref([]);

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value));
}

function formatAssignees(task) {
  if (!task?.assignees?.length) return "Niemand";
  return task.assignees.map((p) => p.name || p.username).join(", ");
}

function dueStatus(task) {
  if (!task?.due_date) return "ok";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(task.due_date);
  due.setHours(0, 0, 0, 0);
  const diff = (due - today) / (1000 * 60 * 60 * 24);
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "ok";
}

function dueStatusLabel(task) {
  const status = dueStatus(task);
  if (status === "overdue") return "Ueberfaellig";
  if (status === "soon") return "Faellig";
  return "Im Plan";
}

const filteredReviewTasks = computed(() => applyFilters(reviewTasks.value));
const filteredPendingTasks = computed(() => applyFilters(pendingReviewTasks.value));

const allReviewSelected = computed(
  () => filteredReviewTasks.value.length > 0 && selectedReviewIds.value.length === filteredReviewTasks.value.length
);
const allPendingSelected = computed(
  () => filteredPendingTasks.value.length > 0 && selectedPendingIds.value.length === filteredPendingTasks.value.length
);

function applyFilters(list) {
  const term = filters.value.search.trim().toLowerCase();
  return list.filter((task) => {
    if (filters.value.onlyMine && me.value?.id) {
      const assignees = task.assignees || [];
      const isMine = assignees.some((person) => String(person.id) === String(me.value.id));
      if (!isMine) return false;
    }
    if (filters.value.due !== "ALL") {
      const status = dueStatus(task);
      if (status !== filters.value.due) return false;
    }
    if (term) {
      const hay = `${task.title || ""} ${task.project_title || ""}`.toLowerCase();
      if (!hay.includes(term)) return false;
    }
    return true;
  });
}

async function loadReviewTasks() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const [reviewRes, pendingRes] = await Promise.all([
      api.get("tasks/", {
        params: {
          status: "REVIEW",
          include_done: 0,
          include_archived: 0,
          ordering: "due_date",
          page_size: 100,
        },
      }),
      api.get("tasks/", {
        params: {
          status: "DONE",
          review_status: "NOT_REVIEWED",
          include_done: 1,
          include_archived: 0,
          ordering: "-completed_at",
          page_size: 100,
        },
      }),
    ]);
    const reviewData = Array.isArray(reviewRes.data) ? reviewRes.data : reviewRes.data.results || [];
    const pendingData = Array.isArray(pendingRes.data) ? pendingRes.data : pendingRes.data.results || [];
    reviewTasks.value = reviewData;
    pendingReviewTasks.value = pendingData;
    selectedReviewIds.value = [];
    selectedPendingIds.value = [];
  } catch (err) {
    console.error("Review-Tasks konnten nicht geladen werden", err);
    showToast("Review-Tasks konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function markReviewed(task) {
  try {
    await api.patch(`tasks/${task.id}/`, { status: "DONE", review_status: "REVIEWED" });
    showToast("Task als reviewed markiert", "success");
    loadReviewTasks();
  } catch (err) {
    console.error("Review konnte nicht gespeichert werden", err);
    showToast("Review konnte nicht gespeichert werden", "error");
  }
}

async function markNotReviewed(task) {
  try {
    await api.patch(`tasks/${task.id}/`, { status: "DONE", review_status: "NOT_REVIEWED" });
    showToast("Task als nicht reviewed markiert", "info");
    loadReviewTasks();
  } catch (err) {
    console.error("Task konnte nicht aktualisiert werden", err);
    showToast("Task konnte nicht aktualisiert werden", "error");
  }
}

async function bulkReviewed() {
  const ids = [...new Set([...selectedReviewIds.value, ...selectedPendingIds.value])];
  if (!ids.length) return;
  await bulkUpdate(ids, { status: "DONE", review_status: "REVIEWED" }, "Auswahl reviewed");
}

async function bulkNotReviewed() {
  if (!selectedReviewIds.value.length) return;
  await bulkUpdate(selectedReviewIds.value, { status: "DONE", review_status: "NOT_REVIEWED" }, "Auswahl nicht reviewed");
}

async function bulkUpdate(ids, payload, successMessage) {
  try {
    await Promise.all(ids.map((id) => api.patch(`tasks/${id}/`, payload)));
    showToast(successMessage, "success");
    loadReviewTasks();
  } catch (err) {
    console.error("Bulk-Update fehlgeschlagen", err);
    showToast("Bulk-Update fehlgeschlagen", "error");
  }
}

function toggleAllReview(event) {
  if (event.target.checked) {
    selectedReviewIds.value = filteredReviewTasks.value.map((task) => task.id);
    return;
  }
  selectedReviewIds.value = [];
}

function toggleAllPending(event) {
  if (event.target.checked) {
    selectedPendingIds.value = filteredPendingTasks.value.map((task) => task.id);
    return;
  }
  selectedPendingIds.value = [];
}

function goToTask(task) {
  if (task.project) {
    router.push({ name: "project-detail", params: { projectId: task.project }, query: { taskId: task.id } });
    return;
  }
  router.push({ name: "tasks", query: { taskId: task.id } });
}

function refresh() {
  loadReviewTasks();
}

onMounted(() => {
  loadReviewTasks();
});
</script>

<style scoped>
.reviews {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.filters {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
}
.filter-row label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.task-item {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--card);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.task-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}
.check {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.task-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.bulk-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  padding: 10px 12px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.03);
}
.bulk-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.btn.tiny {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 10px;
}
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  border: 1px solid var(--border);
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.badge[data-status="soon"] {
  background: rgba(245, 158, 11, 0.18);
  color: #b45309;
}
.badge[data-status="overdue"],
.badge.danger {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.pill.warning {
  background: rgba(248, 113, 113, 0.18);
}
.dot {
  margin: 0 6px;
}
.muted.tiny {
  font-size: 12px;
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
    align-items: stretch;
  }
  .task-main {
    flex-direction: column;
    align-items: flex-start;
  }
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
