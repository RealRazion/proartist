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

    <section v-else class="grid">
      <article class="card panel">
        <div class="panel-head">
          <div>
            <h2>Review faellig</h2>
            <p class="muted small">Status REVIEW</p>
          </div>
          <span class="pill">{{ reviewTasks.length }}</span>
        </div>
        <ul v-if="reviewTasks.length" class="task-list">
          <li v-for="task in reviewTasks" :key="task.id" class="task-item">
            <div class="task-main">
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
        <ul v-if="pendingReviewTasks.length" class="task-list">
          <li v-for="task in pendingReviewTasks" :key="task.id" class="task-item">
            <div class="task-main">
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
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();
const { showToast } = useToast();
const router = useRouter();

const reviewTasks = ref([]);
const pendingReviewTasks = ref([]);
const loading = ref(false);

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
.task-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
}
</style>
