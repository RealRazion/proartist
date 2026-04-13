<template>
  <section class="card finished-tasks-card">
    <div class="card-head">
      <div>
        <p class="eyebrow">Archiv</p>
        <h3>Erledigte Tasks</h3>
        <p class="muted small">{{ finishedCount }} abgeschlossene Aufgaben</p>
      </div>
      <div class="card-actions">
        <span class="badge">{{ finishedCount }}</span>
        <button class="btn ghost" type="button" @click="navigateToFinished" :disabled="finishedCount === 0">
          Alle anzeigen
        </button>
      </div>
    </div>
    <div v-if="finishedCount === 0" class="empty-state">
      <p class="muted">Noch keine erledigten Tasks</p>
    </div>
    <div v-else class="task-grid">
      <div v-for="task in recentFinished" :key="task.id" class="task-card-small">
        <strong>{{ task.title }}</strong>
        <p class="muted small">
          {{ task.project_title || "Kein Projekt" }}
          <span class="dot">·</span>
          {{ task.completed_at ? formatDate(task.completed_at) : "Kein Datum" }}
        </p>
        <p class="muted tiny" v-if="task.review_status">
          Review: {{ reviewStatusLabel(task.review_status) }}
        </p>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from "vue";
import { useRouter } from "vue-router";

const props = defineProps({
  finishedCount: {
    type: Number,
    default: 0,
  },
  finishedTasks: {
    type: Array,
    default: () => [],
  },
});

const router = useRouter();

const recentFinished = computed(() => {
  return props.finishedTasks.slice(0, 6);
});

const reviewStatusLabel = (status) => {
  const labels = {
    REVIEWED: "Geprüft ✓",
    NOT_REVIEWED: "Nicht geprüft",
  };
  return labels[status] || status;
};

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("de-DE", { month: "short", day: "numeric", year: "numeric" });
}

function navigateToFinished() {
  router.push("/tasks/finished");
}
</script>

<style scoped>
.finished-tasks-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(59, 130, 246, 0.05));
  border: 1px solid rgba(16, 185, 129, 0.1);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.card-head > div {
  flex: 1;
}

.card-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-shrink: 0;
}

.card-actions .badge {
  font-size: 14px;
  padding: 4px 12px;
  background: rgba(16, 185, 129, 0.15);
  color: #059669;
  border-radius: 999px;
}

.empty-state {
  padding: 32px 16px;
  text-align: center;
  color: var(--color-muted);
}

.task-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
}

.task-card-small {
  padding: 12px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.task-card-small strong {
  font-size: 14px;
  line-height: 1.3;
  word-break: break-word;
}

.task-card-small .muted {
  font-size: 12px;
}

.task-card-small .dot {
  margin: 0 4px;
}

@media (max-width: 768px) {
  .task-grid {
    grid-template-columns: 1fr;
  }

  .card-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .card-actions {
    width: 100%;
  }
}
</style>
