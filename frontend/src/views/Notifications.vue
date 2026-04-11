<template>
  <div class="notifications">
    <header class="card hero">
      <div>
        <p class="eyebrow">Inbox</p>
        <h1>Benachrichtigungen</h1>
        <p class="muted">Interne Hinweise zu Task-Zuweisungen, Erwaehnungen und Projekt-Updates.</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="loadNotifications" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
        <button class="btn" type="button" @click="markAllRead" :disabled="markingAll || !unreadCount">
          {{ markingAll ? "Speichere..." : "Alle als gelesen" }}
        </button>
      </div>
    </header>

    <section class="card filters">
      <div class="chip-row">
        <button
          v-for="option in filterOptions"
          :key="option.key"
          class="chip"
          :class="{ active: filterMode === option.key }"
          type="button"
          @click="filterMode = option.key"
        >
          {{ option.label }}
        </button>
      </div>
      <div class="stats">
        <span class="badge warning">Ungelesen: {{ unreadCount }}</span>
        <span class="badge">Gesamt: {{ notifications.length }}</span>
      </div>
    </section>

    <section class="list">
      <article v-if="loading" class="card muted">Lade Benachrichtigungen...</article>
      <article v-else-if="!filteredNotifications.length" class="card muted">Keine Benachrichtigungen vorhanden.</article>
      <article
        v-for="notification in filteredNotifications"
        :key="notification.id"
        class="card item"
        :class="{ unread: !notification.is_read }"
      >
        <div class="item-head">
          <div>
            <p class="type">{{ typeLabel(notification.notification_type) }}</p>
            <h2>{{ notification.title }}</h2>
            <p class="muted">{{ notification.body || "Ohne Zusatztext" }}</p>
          </div>
          <div class="item-meta">
            <span class="badge" :data-tone="toneFor(notification.severity)">{{ severityLabel(notification.severity) }}</span>
            <span class="muted small">{{ formatDate(notification.created_at) }}</span>
          </div>
        </div>
        <div class="item-foot">
          <div class="context">
            <span v-if="notification.project" class="muted small">Projekt: {{ notification.project.title }}</span>
            <span v-if="notification.task" class="muted small">Task: {{ notification.task.title }}</span>
            <span v-if="notification.actor" class="muted small">Von: {{ notification.actor.name || notification.actor.username }}</span>
          </div>
          <div class="actions">
            <button v-if="notification.task || notification.project" class="btn ghost tiny" type="button" @click="openNotification(notification)">
              Oeffnen
            </button>
            <button
              v-if="!notification.is_read"
              class="btn tiny"
              type="button"
              @click="markRead(notification)"
              :disabled="Boolean(saving[notification.id])"
            >
              {{ saving[notification.id] ? "..." : "Als gelesen" }}
            </button>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { showToast } = useToast();

const notifications = ref([]);
const loading = ref(false);
const markingAll = ref(false);
const filterMode = ref("unread");
const saving = ref({});

const filterOptions = [
  { key: "unread", label: "Ungelesen" },
  { key: "all", label: "Alle" },
];

const filteredNotifications = computed(() => {
  if (filterMode.value === "all") return notifications.value;
  return notifications.value.filter((entry) => !entry.is_read);
});

const unreadCount = computed(() => notifications.value.filter((entry) => !entry.is_read).length);

function formatDate(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function typeLabel(type) {
  const labels = {
    task_assigned: "Task",
    task_mentioned: "Erwaehnung",
    task_recurring_generated: "Wiederholung",
    project_created: "Projekt",
    project_status_updated: "Projekt-Update",
    task_reminder_due_soon: "Reminder",
    task_reminder_overdue: "Reminder",
    automation_notification: "Automation",
  };
  return labels[type] || "Hinweis";
}

function toneFor(severity) {
  if (severity === "DANGER") return "danger";
  if (severity === "WARNING") return "warning";
  if (severity === "SUCCESS") return "ok";
  return "info";
}

function severityLabel(severity) {
  const labels = { INFO: "Info", SUCCESS: "Erfolg", WARNING: "Hinweis", DANGER: "Wichtig" };
  return labels[severity] || severity || "Info";
}

async function loadNotifications() {
  loading.value = true;
  try {
    const { data } = await api.get("notifications/", { params: { page_size: 100 } });
    notifications.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Benachrichtigungen konnten nicht geladen werden", err);
    showToast("Benachrichtigungen konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function markRead(notification) {
  if (!notification?.id || saving.value[notification.id]) return;
  saving.value = { ...saving.value, [notification.id]: true };
  try {
    const { data } = await api.patch(`notifications/${notification.id}/`, { is_read: true });
    notifications.value = notifications.value.map((entry) => (entry.id === notification.id ? data : entry));
  } catch (err) {
    console.error("Benachrichtigung konnte nicht aktualisiert werden", err);
    showToast("Benachrichtigung konnte nicht aktualisiert werden", "error");
  } finally {
    saving.value = { ...saving.value, [notification.id]: false };
  }
}

async function markAllRead() {
  if (!unreadCount.value || markingAll.value) return;
  markingAll.value = true;
  try {
    await api.post("notifications/mark-all-read/");
    notifications.value = notifications.value.map((entry) => ({
      ...entry,
      is_read: true,
      read_at: entry.read_at || new Date().toISOString(),
    }));
    showToast("Alle Benachrichtigungen wurden als gelesen markiert", "success");
  } catch (err) {
    console.error("Benachrichtigungen konnten nicht aktualisiert werden", err);
    showToast("Benachrichtigungen konnten nicht aktualisiert werden", "error");
  } finally {
    markingAll.value = false;
  }
}

function openNotification(notification) {
  if (notification.task) {
    if (notification.project) {
      router.push({ name: "project-detail", params: { projectId: notification.project.id }, query: { taskId: notification.task.id } });
      return;
    }
    router.push({ name: "tasks", query: { taskId: notification.task.id } });
    return;
  }
  if (notification.project) {
    router.push({ name: "project-detail", params: { projectId: notification.project.id } });
  }
}

onMounted(loadNotifications);
</script>

<style scoped>
.notifications {
  display: grid;
  gap: 16px;
}
.hero {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.hero-actions,
.actions,
.stats,
.chip-row,
.item-meta,
.item-foot,
.context {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.filters {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.chip {
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 6px 12px;
  background: var(--surface);
  color: var(--text);
  font-size: 12px;
  font-weight: 600;
}
.chip.active {
  border-color: var(--brand);
  color: var(--brand);
}
.list {
  display: grid;
  gap: 12px;
}
.item {
  display: grid;
  gap: 12px;
  border-left: 4px solid transparent;
}
.item.unread {
  border-left-color: var(--brand);
}
.item-head,
.item-foot {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.item h2 {
  margin: 4px 0 6px;
  font-size: 18px;
}
.type,
.eyebrow,
.small {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.badge[data-tone="danger"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.badge[data-tone="warning"],
.badge.warning {
  background: rgba(245, 158, 11, 0.18);
  color: #b45309;
}
.badge[data-tone="ok"] {
  background: rgba(34, 197, 94, 0.18);
  color: #15803d;
}
.badge[data-tone="info"],
.badge {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}
@media (max-width: 720px) {
  .filters,
  .item-head,
  .item-foot,
  .hero {
    flex-direction: column;
  }
  .hero-actions .btn,
  .actions .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
