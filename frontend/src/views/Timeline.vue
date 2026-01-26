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
            </article>
          </div>
        </div>
      </div>
      <p v-if="!loading && !items.length" class="muted empty">Keine Einträge im gewählten Zeitraum.</p>
    </section>
    <section v-else class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Die Timeline steht nur Team-Mitgliedern zur Verfügung.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();

const today = new Date();
const startDate = ref(today.toISOString().slice(0, 10));
const endDate = ref(new Date(today.getTime() + 1000 * 60 * 60 * 24 * 30).toISOString().slice(0, 10));
const viewType = ref("TASKS");
const viewOptions = [
  { key: "TASKS", label: "Tasks" },
  { key: "PROJECTS", label: "Projekte" },
];

const loading = ref(false);
const items = ref([]);

const currentTitle = computed(() => (viewType.value === "TASKS" ? "Task-Kalender" : "Projekt-Zeitachse"));
const dateFormatter = new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" });
const formattedRange = computed(() => `${formatDate(startDate.value)} bis ${formatDate(endDate.value)}`);

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(`${value}T00:00:00`);
  if (Number.isNaN(date.getTime())) return value;
  return dateFormatter.format(date);
}

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
  const list = items.value.filter((item) => item.date === iso);
  return list.map((item) => ({
    id: `${item.type}-${item.raw.id}`,
    title: item.raw.title,
    subtitle: item.raw.project_title || item.raw.description || "Kein Projekt",
    badge: viewType.value === "TASKS" ? item.raw.priority : item.raw.status,
    className: item.type === "task" ? `priority-${item.raw.priority?.toLowerCase()}` : `status-${item.raw.status?.toLowerCase()}`,
  }));
}

async function loadItems() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const params = { start: startDate.value, end: endDate.value };
    const endpoint = viewType.value === "TASKS" ? "tasks/calendar/" : "projects/timeline/";
    const { data } = await api.get(endpoint, { params });
    const results = data?.results || [];
    items.value = (results || []).map((entry) => ({
      type: viewType.value === "TASKS" ? "task" : "project",
      date: viewType.value === "TASKS" ? entry.due_date?.slice(0, 10) : (entry.archived_at || entry.created_at || "").slice(0, 10),
      raw: entry,
    })).filter((item) => Boolean(item.date));
  } catch (err) {
    console.error("Timeline konnte nicht geladen werden", err);
  } finally {
    loading.value = false;
  }
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
  background: rgba(255, 255, 255, 0.92);
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
