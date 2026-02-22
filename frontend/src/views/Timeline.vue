<template>
  <div class="timeline">
    <header class="card hero">
      <div>
        <p class="eyebrow">Timeline</p>
        <h1>Deadlines & Releases</h1>
        <p class="muted">Plane kommende Tasks und Projekte in einer gemeinsamen Übersicht.</p>
      </div>
      <div class="hero-actions">
        <label>
          Start
          <input class="input" type="date" v-model="startDate" />
        </label>
        <label>
          Ende
          <input class="input" type="date" v-model="endDate" />
        </label>
        <div class="toggle-group">
          <button
            v-for="option in viewOptions"
            :key="option.key"
            type="button"
            class="chip"
            :class="{ active: viewType === option.key }"
            @click="viewType = option.key"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </header>

    <section v-if="isTeam" class="card board">
      <div class="board-head">
        <div>
          <h2>{{ currentTitle }}</h2>
          <p class="muted small">
            Zeitraum {{ formattedRange }}
          </p>
        </div>
        <button class="btn ghost" type="button" @click="loadItems" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
      <div class="filters">
        <div class="filter-group" v-if="showTasks">
          <span class="filter-label">Prioritäten</span>
          <label v-for="opt in priorityOptions" :key="opt.key" class="filter-chip">
            <input type="checkbox" :value="opt.key" v-model="priorityFilters" />
            {{ opt.label }}
          </label>
        </div>
        <div class="filter-group" v-if="showTasks">
          <span class="filter-label">Typ</span>
          <label v-for="opt in taskTypeOptions" :key="opt.key" class="filter-chip">
            <input type="checkbox" :value="opt.key" v-model="taskTypeFilters" />
            {{ opt.label }}
          </label>
        </div>
      </div>

      <div v-if="loading" class="muted">Lade Termine...</div>
      <div v-else class="calendar-grid">
        <div v-for="day in calendarDays" :key="day.iso" class="calendar-day">
          <div class="day-head">
            <strong>{{ day.label }}</strong>
            <span class="muted small">{{ day.weekday }}</span>
          </div>
          <div class="day-items">
            <article
              v-for="item in day.items"
              :key="item.id"
              class="timeline-card"
              :class="item.className"
            >
              <header>
                <h4>{{ item.title }}</h4>
                <span class="badge">{{ item.badge }}</span>
              </header>
              <p class="muted">{{ item.subtitle }}</p>
              <div class="card-actions">
                <button class="btn ghost tiny" type="button" @click="handleItemAction(item)">
                  {{ actionLabel(item) }}
                </button>
              </div>
            </article>
          </div>
        </div>
      </div>
      <p v-if="!loading && !filteredItems.length" class="muted empty">Keine Einträge im gewählten Zeitraum.</p>
    </section>
    <section v-else class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Die Timeline steht nur Team-Mitgliedern zur Verfügung.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();
const router = useRouter();

const today = new Date();
const startDate = ref(today.toISOString().slice(0, 10));
const endDate = ref(new Date(today.getTime() + 1000 * 60 * 60 * 24 * 30).toISOString().slice(0, 10));
const viewType = ref("ALL");
const viewOptions = [
  { key: "ALL", label: "Alles" },
  { key: "TASKS", label: "Tasks" },
  { key: "PROJECTS", label: "Projekte" },
  { key: "GROWPRO", label: "GrowPro" },
];

const loading = ref(false);
const items = ref([]);
const priorityFilters = ref(["CRITICAL", "HIGH", "MEDIUM", "LOW"]);
const taskTypeFilters = ref(["INTERNAL", "EXTERNAL"]);

const priorityOptions = [
  { key: "CRITICAL", label: "Kritisch" },
  { key: "HIGH", label: "Hoch" },
  { key: "MEDIUM", label: "Mittel" },
  { key: "LOW", label: "Niedrig" },
];
const taskTypeOptions = [
  { key: "INTERNAL", label: "Intern" },
  { key: "EXTERNAL", label: "Extern" },
];

const showTasks = computed(() => viewType.value === "ALL" || viewType.value === "TASKS");
const showProjects = computed(() => viewType.value === "ALL" || viewType.value === "PROJECTS");
const showGrowPro = computed(() => viewType.value === "ALL" || viewType.value === "GROWPRO");

const currentTitle = computed(() => {
  if (viewType.value === "TASKS") return "Task-Kalender";
  if (viewType.value === "PROJECTS") return "Projekt-Zeitachse";
  if (viewType.value === "GROWPRO") return "GrowPro Timeline";
  return "Team Timeline";
});
const dateFormatter = new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" });
const formattedRange = computed(() => `${formatDate(startDate.value)} bis ${formatDate(endDate.value)}`);

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return dateFormatter.format(date);
}

function toISODate(value) {
  if (!value) return null;
  if (typeof value === "string") return value.slice(0, 10);
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
}

const filteredItems = computed(() => {
  return items.value.filter((item) => {
    if (item.type === "task") {
      if (!showTasks.value) return false;
      if (priorityFilters.value.length && !priorityFilters.value.includes(item.raw.priority)) return false;
      if (taskTypeFilters.value.length && !taskTypeFilters.value.includes(item.raw.task_type)) return false;
      return true;
    }
    if (item.type === "project") return showProjects.value;
    if (item.type === "growpro" || item.type === "growpro-update") return showGrowPro.value;
    return true;
  });
});

const calendarDays = computed(() => {
  const start = new Date(startDate.value);
  const end = new Date(endDate.value);
  const days = [];
  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const iso = d.toISOString().slice(0, 10);
    days.push({
      iso,
      label: d.getDate().toString().padStart(2, "0") + "." + (d.getMonth() + 1).toString().padStart(2, "0"),
      weekday: d.toLocaleDateString("de-DE", { weekday: "short" }),
      items: enrichItemsForDay(iso),
    });
  }
  return days;
});

function enrichItemsForDay(iso) {
  const list = filteredItems.value.filter((item) => item.date === iso);
  return list.map((item) => buildItemView(item));
}

function buildItemView(item) {
  if (item.type === "task") {
    return {
      id: `${item.type}-${item.raw.id}`,
      title: item.raw.title,
      subtitle: item.raw.project_title || item.raw.description || "Kein Projekt",
      badge: item.raw.priority,
      className: `priority-${item.raw.priority?.toLowerCase()}`,
      type: item.type,
      raw: item.raw,
    };
  }
  if (item.type === "project") {
    return {
      id: `${item.type}-${item.raw.id}`,
      title: item.raw.title,
      subtitle: item.raw.description || "Kein Status gesetzt",
      badge: item.raw.status,
      className: `status-${item.raw.status?.toLowerCase()}`,
      type: item.type,
      raw: item.raw,
    };
  }
  if (item.type === "growpro-update") {
    return {
      id: `${item.type}-${item.raw.id}`,
      title: `GrowPro Update: ${item.raw.title}`,
      subtitle: `Update-Frist (72h) für ${item.raw.metric || "Ziel"}`,
      badge: "Update",
      className: "growpro-update",
      type: item.type,
      raw: item.raw,
    };
  }
  return {
    id: `${item.type}-${item.raw.id}`,
    title: `GrowPro Ziel: ${item.raw.title}`,
    subtitle: item.raw.metric || item.raw.description || "GrowPro Ziel",
    badge: item.raw.status || "Ziel",
    className: `growpro-${item.raw.status?.toLowerCase() || "active"}`,
    type: item.type,
    raw: item.raw,
  };
}

async function loadItems() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const params = { start: startDate.value, end: endDate.value };
    const [tasksRes, projectsRes, growRes] = await Promise.all([
      api.get("tasks/calendar/", { params }),
      api.get("projects/timeline/", { params }),
      api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 200 } }),
    ]);
    const taskResults = tasksRes?.data?.results || [];
    const projectResults = projectsRes?.data?.results || [];
    const growPayload = growRes?.data || {};
    const growResults = Array.isArray(growPayload) ? growPayload : growPayload.results || [];
    const mapped = [];
    taskResults.forEach((entry) => {
      const date = entry.due_date ? entry.due_date.slice(0, 10) : null;
      if (date) {
        mapped.push({ type: "task", date, raw: entry });
      }
    });
    projectResults.forEach((entry) => {
      const date = (entry.archived_at || entry.created_at || "").slice(0, 10);
      if (date) {
        mapped.push({ type: "project", date, raw: entry });
      }
    });
    growResults.forEach((goal) => {
      const dueDate = toISODate(goal.due_date);
      if (dueDate) {
        mapped.push({ type: "growpro", date: dueDate, raw: goal });
      }
      const base = goal.last_logged_at || goal.created_at;
      const baseDate = base ? new Date(base) : null;
      if (baseDate && !Number.isNaN(baseDate.getTime())) {
        const deadline = new Date(baseDate.getTime() + 72 * 60 * 60 * 1000);
        const iso = toISODate(deadline);
        if (iso) {
          mapped.push({ type: "growpro-update", date: iso, raw: goal });
        }
      }
    });
    items.value = mapped;
  } catch (err) {
    console.error("Timeline konnte nicht geladen werden", err);
  } finally {
    loading.value = false;
  }
}

function actionLabel(item) {
  if (item.type === "task") {
    return item.raw.project ? "Projekt öffnen" : "Task öffnen";
  }
  if (item.type === "project") return "Projekt öffnen";
  return "GrowPro öffnen";
}

async function handleItemAction(item) {
  if (item.type === "task") {
    if (item.raw.project) {
      await router.push({
        name: "project-detail",
        params: { projectId: item.raw.project },
        query: { taskId: item.raw.id },
      });
      return;
    }
    await router.push({ name: "tasks", query: { taskId: item.raw.id } });
    return;
  }
  if (item.type === "project") {
    await router.push({ name: "project-detail", params: { projectId: item.raw.id } });
    return;
  }
  await router.push({ name: "growpro" });
  await nextTick();
}

watch([startDate, endDate, viewType], () => {
  loadItems();
});

onMounted(() => {
  if (isTeam.value) {
    loadItems();
  }
});
</script>

<style scoped>
.timeline {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: flex-end;
}
.hero-actions label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 13px;
  font-weight: 600;
}
.toggle-group {
  display: flex;
  gap: 8px;
}
.toggle-group .chip {
  border: 1px solid rgba(148, 163, 184, 0.5);
  border-radius: 999px;
  padding: 6px 16px;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.08em;
}
.toggle-group .chip.active {
  border-color: #2563eb;
  color: #2563eb;
}
.board {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.board-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  align-items: center;
}
.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  font-size: 12px;
}
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.calendar-day {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 160px;
}
.day-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}
.day-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.timeline-card {
  border-radius: 10px;
  padding: 10px;
  background: var(--card);
  border: 1px solid rgba(148, 163, 184, 0.4);
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.timeline-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.timeline-card .badge {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  border-radius: 999px;
  padding: 3px 10px;
  border: 1px solid rgba(148, 163, 184, 0.4);
}
.timeline-card.priority-critical {
  border-color: #dc2626;
}
.timeline-card.priority-high {
  border-color: #f97316;
}
.timeline-card.priority-low {
  border-color: #16a34a;
}
.timeline-card.status-done {
  border-color: #16a34a;
}
.timeline-card.growpro-update {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.08);
}
.timeline-card.growpro-active {
  border-color: #6366f1;
}
.timeline-card.growpro-on_hold {
  border-color: #eab308;
}
.card-actions {
  display: flex;
  justify-content: flex-end;
}
.empty {
  text-align: center;
  margin: 0;
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
  }
  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
