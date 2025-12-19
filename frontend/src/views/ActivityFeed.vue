<template>
  <div class="activity">
    <header class="card header">
      <div>
        <h1>Aktivit?ten</h1>
        <p class="muted">Feed f?r Team und Admins mit Status-Updates.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadFeed" :disabled="loading">
        {{ loading ? "Aktualisiere..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Kein Zugriff</h2>
      <p class="muted">Der Aktivit?ts-Feed steht nur Team-Mitgliedern zur Verf?gung.</p>
    </section>

    <section v-else class="card feed">
      <div class="filters">
        <label>
          Schweregrad
          <select class="input" v-model="severityFilter">
            <option value="ALL">Alle</option>
            <option value="SUCCESS">Erfolg</option>
            <option value="INFO">Info</option>
            <option value="WARNING">Hinweis</option>
            <option value="DANGER">Alarm</option>
          </select>
        </label>
        <label>
          Limit
          <select class="input" v-model.number="limit" @change="loadFeed">
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </label>
      </div>
      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-card" v-for="n in 4" :key="`sk-${n}`"></div>
      </div>
      <ul v-else>
        <li v-for="entry in filteredEntries" :key="entry.id" :style="{ borderTopColor: colorFor(entry.severity) }">
          <div class="row">
            <span class="badge" :data-severity="entry.severity">{{ severityLabel(entry.severity) }}</span>
            <span class="time">{{ formatTime(entry.created_at) }}</span>
          </div>
          <h3>{{ entry.title }}</h3>
          <p class="muted">{{ entry.description || "Keine weiteren Details" }}</p>
          <div class="meta">
            <span v-if="entry.actor">Von {{ entry.actor.name || entry.actor.username }}</span>
            <span v-if="entry.project">
              Projekt:
              <strong>{{ entry.project.title }}</strong>
            </span>
            <span v-if="entry.task">
              Task:
              <strong>{{ entry.task.title }}</strong>
            </span>
          </div>
        </li>
      </ul>
      <p v-if="!loading && !filteredEntries.length" class="muted empty">Keine Eintr?ge vorhanden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();
const entries = ref([]);
const loading = ref(false);
const severityFilter = ref("ALL");
const limit = ref(50);

const severityColors = {
  SUCCESS: "#22c55e",
  INFO: "#3b82f6",
  WARNING: "#f97316",
  DANGER: "#ef4444",
};

const filteredEntries = computed(() => {
  if (severityFilter.value === "ALL") return entries.value;
  return entries.value.filter((entry) => entry.severity === severityFilter.value);
});

function colorFor(severity) {
  return severityColors[severity] || "#94a3b8";
}

function severityLabel(severity) {
  return (
    {
      SUCCESS: "Erfolg",
      INFO: "Info",
      WARNING: "Hinweis",
      DANGER: "Alarm",
    }[severity] || severity
  );
}

function formatTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

async function loadFeed() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("activity-feed/", { params: { limit: limit.value } });
    entries.value = data;
  } catch (err) {
    console.error("Feed konnte nicht geladen werden", err);
    entries.value = [];
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  await loadFeed();
});
</script>

<style scoped>
.activity {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.info {
  max-width: 600px;
}
.feed {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.skeleton-list {
  display: grid;
  gap: 10px;
}
.skeleton-card {
  height: 90px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
li {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  padding: 12px;
  border-top-width: 4px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--muted);
}
.badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.2);
}
.badge[data-severity="SUCCESS"] {
  color: #16a34a;
  background: rgba(34, 197, 94, 0.15);
}
.badge[data-severity="INFO"] {
  color: #2563eb;
  background: rgba(59, 130, 246, 0.15);
}
.badge[data-severity="WARNING"] {
  color: #c2410c;
  background: rgba(249, 115, 22, 0.15);
}
.badge[data-severity="DANGER"] {
  color: #b91c1c;
  background: rgba(248, 113, 113, 0.2);
}
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
  color: var(--muted);
}
.empty {
  text-align: center;
  margin: 12px 0 0;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>
