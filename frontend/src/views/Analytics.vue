<template>
  <div class="analytics">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />

    <header class="card header">
      <div>
        <p class="eyebrow">Team</p>
        <h1>Analytics</h1>
        <p class="muted">Zahlen, Engpaesse und Trends auf einen Blick.</p>
      </div>
      <div class="header-actions">
        <button class="btn ghost" type="button" @click="loadAll" :disabled="loading">
          {{ loading ? "Lade..." : "Neu laden" }}
        </button>
        <button class="btn ghost" type="button" @click="sendTaskReminders" :disabled="remindersSending">
          {{ remindersSending ? "Sende..." : "Reminder senden" }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Kein Zugriff</h2>
      <p class="muted">Analytics sind nur fuer Team-Mitglieder sichtbar.</p>
    </section>

    <template v-else>
      <section class="kpi-grid">
        <div class="card kpi">
          <span class="label">Tasks aktiv</span>
          <strong>{{ formatNumber(analytics.active_tasks) }}</strong>
          <small class="muted">Ueberfaellig {{ formatNumber(analytics.overdue_tasks) }}</small>
        </div>
        <div class="card kpi">
          <span class="label">Tasks faellig (7 Tage)</span>
          <strong>{{ formatNumber(analytics.due_soon_tasks) }}</strong>
          <small class="muted">Erledigt 7 Tage {{ formatNumber(analytics.completed_last_7_days) }}</small>
        </div>
        <div class="card kpi">
          <span class="label">Projekte aktiv</span>
          <strong>{{ formatNumber(projectSummary.active) }}</strong>
          <small class="muted">Gesamt {{ formatNumber(projectSummary.total) }}</small>
        </div>
        <div class="card kpi">
          <span class="label">Requests offen</span>
          <strong>{{ formatNumber(stats.open_requests) }}</strong>
          <small class="muted">Heute priorisieren</small>
        </div>
        <div class="card kpi">
          <span class="label">Team Mitglieder</span>
          <strong>{{ formatNumber(adminOverview.team_members) }}</strong>
          <small class="muted">Neue Nutzer {{ formatNumber(adminOverview.new_users_last_7_days) }}</small>
        </div>
        <div class="card kpi">
          <span class="label">GrowPro aktiv</span>
          <strong>{{ formatNumber(growproSummary.active) }}</strong>
          <small class="muted">Done {{ formatNumber(growproSummary.done) }}</small>
        </div>
      </section>

      <section class="grid">
        <div class="card panel">
          <div class="section-head">
            <h2>Tasks</h2>
            <span class="pill">Gesamt {{ formatNumber(taskSummary.total) }}</span>
          </div>
          <div class="breakdown">
            <div v-for="item in taskStatusItems" :key="`task-${item.key}`" class="break-item">
              <div class="row">
                <span>{{ item.label }}</span>
                <strong>{{ formatNumber(item.count) }}</strong>
              </div>
              <div class="bar">
                <span :style="{ width: item.pct + '%' }"></span>
              </div>
            </div>
          </div>
          <div class="subhead">Typen</div>
          <div class="mini-grid">
            <div v-for="item in taskTypeItems" :key="`type-${item.key}`" class="mini">
              <span class="label">{{ item.label }}</span>
              <strong>{{ formatNumber(item.count) }}</strong>
            </div>
          </div>
          <div class="subhead">Ueberfaellig</div>
          <ul v-if="overdueTasks.length" class="list">
            <li v-for="task in overdueTasks.slice(0, 6)" :key="`overdue-${task.id}`">
              <div class="row">
                <strong>{{ task.title }}</strong>
                <span class="badge danger">{{ formatDate(task.due_date) }}</span>
              </div>
              <p class="muted small">{{ task.project_title || `Projekt #${task.project}` }}</p>
            </li>
          </ul>
          <p v-else class="muted small">Keine ueberfaelligen Tasks.</p>
        </div>

        <div class="card panel">
          <div class="section-head">
            <h2>Projekte</h2>
            <span class="pill">Gesamt {{ formatNumber(projectSummary.total) }}</span>
          </div>
          <div class="breakdown">
            <div v-for="item in projectStatusItems" :key="`proj-${item.key}`" class="break-item">
              <div class="row">
                <span>{{ item.label }}</span>
                <strong>{{ formatNumber(item.count) }}</strong>
              </div>
              <div class="bar">
                <span :style="{ width: item.pct + '%' }"></span>
              </div>
            </div>
          </div>
          <div class="subhead">Naechste Deadlines</div>
          <ul v-if="upcomingTasks.length" class="list">
            <li v-for="task in upcomingTasks.slice(0, 6)" :key="`upcoming-${task.id}`">
              <div class="row">
                <strong>{{ task.title }}</strong>
                <span class="badge">{{ formatDate(task.due_date) }}</span>
              </div>
              <p class="muted small">{{ task.project_title || `Projekt #${task.project}` }}</p>
            </li>
          </ul>
          <p v-else class="muted small">Keine faelligen Tasks in den naechsten Tagen.</p>
        </div>

        <div class="card panel">
          <div class="section-head">
            <h2>GrowPro</h2>
            <span class="pill">Gesamt {{ formatNumber(growproSummary.total) }}</span>
          </div>
          <div class="breakdown">
            <div v-for="item in growproStatusItems" :key="`grow-${item.key}`" class="break-item">
              <div class="row">
                <span>{{ item.label }}</span>
                <strong>{{ formatNumber(item.count) }}</strong>
              </div>
              <div class="bar">
                <span :style="{ width: item.pct + '%' }"></span>
              </div>
            </div>
          </div>
          <div class="mini-grid">
            <div class="mini">
              <span class="label">Faellig (24h)</span>
              <strong>{{ formatNumber(growproDueSoon) }}</strong>
            </div>
            <div class="mini">
              <span class="label">Ueberfaellig</span>
              <strong>{{ formatNumber(growproOverdue) }}</strong>
            </div>
          </div>
        </div>

        <div class="card panel">
          <div class="section-head">
            <h2>Team & Rollen</h2>
            <span class="pill">User {{ formatNumber(adminOverview.total_users) }}</span>
          </div>
          <div class="mini-grid">
            <div class="mini">
              <span class="label">Team</span>
              <strong>{{ formatNumber(adminOverview.team_members) }}</strong>
            </div>
            <div class="mini">
              <span class="label">Gesperrt</span>
              <strong>{{ formatNumber(adminOverview.locked_users) }}</strong>
            </div>
            <div class="mini">
              <span class="label">Neue Nutzer</span>
              <strong>{{ formatNumber(adminOverview.new_users_last_7_days) }}</strong>
            </div>
          </div>
          <div class="subhead">Rollen</div>
          <div class="breakdown compact">
            <div v-for="item in roleItems" :key="`role-${item.key}`" class="break-item">
              <div class="row">
                <span>{{ item.label }}</span>
                <strong>{{ formatNumber(item.count) }}</strong>
              </div>
              <div class="bar">
                <span :style="{ width: item.pct + '%' }"></span>
              </div>
            </div>
          </div>
        </div>

        <div class="card panel">
          <div class="section-head">
            <h2>Requests & Finanzen</h2>
            <span class="pill">Offen {{ formatNumber(stats.open_requests) }}</span>
          </div>
          <div class="mini-grid">
            <div class="mini">
              <span class="label">Vertraege aktiv</span>
              <strong>{{ formatNumber(stats.active_contracts) }}</strong>
            </div>
            <div class="mini">
              <span class="label">Zahlungen offen</span>
              <strong>{{ formatNumber(stats.due_payments) }}</strong>
            </div>
          </div>
          <div class="subhead">Offene Requests</div>
          <ul v-if="openRequests.length" class="list">
            <li v-for="req in openRequests.slice(0, 5)" :key="`req-${req.id}`">
              <div class="row">
                <strong>{{ requestTypeLabel(req.req_type) }}</strong>
                <span class="pill subtle">{{ req.status }}</span>
              </div>
              <p class="muted small">{{ req.sender_name }} -> {{ req.receiver_name }}</p>
            </li>
          </ul>
          <p v-else class="muted small">Keine offenen Requests.</p>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { toast, showToast, hideToast } = useToast();
const { isTeam, fetchProfile } = useCurrentProfile();

const loading = ref(false);
const remindersSending = ref(false);

const analytics = ref({ active_tasks: 0, overdue_tasks: 0, due_soon_tasks: 0, completed_last_7_days: 0 });
const taskSummary = ref({ total: 0, active: 0, done: 0, archived: 0, by_status: {}, by_type: {} });
const projectSummary = ref({ total: 0, active: 0, done: 0, archived: 0, by_status: {} });
const growproSummary = ref({ total: 0, active: 0, done: 0, archived: 0, by_status: {} });
const adminOverview = ref({ total_users: 0, locked_users: 0, team_members: 0, new_users_last_7_days: 0, active_projects: 0, overdue_tasks: 0 });
const stats = ref({ roles: {}, open_requests: 0, active_contracts: 0, due_payments: 0 });

const overdueTasks = ref([]);
const upcomingTasks = ref([]);
const openRequests = ref([]);
const growproGoals = ref([]);

const taskStatusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Erledigt",
};
const taskTypeLabels = { INTERNAL: "Intern", EXTERNAL: "Extern" };
const projectStatusLabels = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  ON_HOLD: "Pausiert",
  DONE: "Abgeschlossen",
};
const growproStatusLabels = {
  ACTIVE: "Aktiv",
  ON_HOLD: "Pausiert",
  DONE: "Erledigt",
  ARCHIVED: "Archiviert",
};
const roleLabels = {
  TEAM: "Team",
  ARTIST: "Artist",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merch",
  MKT: "Marketing",
  LOC: "Location",
};

const taskStatusItems = computed(() => buildItems(taskSummary.value.by_status, taskStatusLabels, taskSummary.value.total));
const taskTypeItems = computed(() => buildItems(taskSummary.value.by_type, taskTypeLabels, taskSummary.value.total));
const projectStatusItems = computed(() => buildItems(projectSummary.value.by_status, projectStatusLabels, projectSummary.value.total));
const growproStatusItems = computed(() => buildItems(growproSummary.value.by_status, growproStatusLabels, growproSummary.value.total));
const roleItems = computed(() => buildItems(stats.value.roles, roleLabels, totalRoles.value));

const totalRoles = computed(() => Object.values(stats.value.roles || {}).reduce((sum, v) => sum + v, 0));

const growproDueSoon = computed(() => {
  const now = Date.now();
  const day = 24 * 60 * 60 * 1000;
  return growproGoals.value.filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    return due - now >= 0 && due - now < day;
  }).length;
});

const growproOverdue = computed(() => {
  const now = Date.now();
  return growproGoals.value.filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    return due < now;
  }).length;
});

function buildItems(byMap, labels, total) {
  const items = Object.entries(byMap || {}).map(([key, count]) => ({
    key,
    label: labels[key] || key,
    count,
    pct: total ? Math.round((count / total) * 100) : 0,
  }));
  return items.sort((a, b) => b.count - a.count);
}

function formatNumber(value) {
  const num = Number(value || 0);
  return new Intl.NumberFormat("de-DE").format(num);
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function requestTypeLabel(type) {
  return { COLLAB: "Collab", BOOK: "Booking", OTHER: "Andere" }[type] || type;
}

async function loadAnalyticsSummary() {
  try {
    const { data } = await api.get("analytics/summary/", { params: { soon_days: 7 } });
    analytics.value = {
      active_tasks: data.active_tasks || 0,
      overdue_tasks: data.overdue_tasks || 0,
      due_soon_tasks: data.due_soon_tasks || 0,
      completed_last_7_days: data.completed_last_7_days || 0,
    };
  } catch (err) {
    analytics.value = { active_tasks: 0, overdue_tasks: 0, due_soon_tasks: 0, completed_last_7_days: 0 };
  }
}

async function loadTaskSummary() {
  try {
    const { data } = await api.get("tasks/summary/");
    taskSummary.value = {
      total: data.total || 0,
      active: data.active || 0,
      done: data.done || 0,
      archived: data.archived || 0,
      by_status: data.by_status || {},
      by_type: data.by_type || {},
    };
  } catch (err) {
    taskSummary.value = { total: 0, active: 0, done: 0, archived: 0, by_status: {}, by_type: {} };
  }
}

async function loadProjectSummary() {
  try {
    const { data } = await api.get("projects/summary/");
    projectSummary.value = {
      total: data.total || 0,
      active: data.active || 0,
      done: data.done || 0,
      archived: data.archived || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    projectSummary.value = { total: 0, active: 0, done: 0, archived: 0, by_status: {} };
  }
}

async function loadGrowProSummary() {
  try {
    const { data } = await api.get("growpro/summary/");
    growproSummary.value = {
      total: data.total || 0,
      active: data.active || 0,
      done: data.done || 0,
      archived: data.archived || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    growproSummary.value = { total: 0, active: 0, done: 0, archived: 0, by_status: {} };
  }
}

async function loadAdminOverview() {
  try {
    const { data } = await api.get("admin/overview/");
    adminOverview.value = {
      total_users: data.total_users || 0,
      locked_users: data.locked_users || 0,
      team_members: data.team_members || 0,
      new_users_last_7_days: data.new_users_last_7_days || 0,
      active_projects: data.active_projects || 0,
      overdue_tasks: data.overdue_tasks || 0,
    };
  } catch (err) {
    adminOverview.value = { total_users: 0, locked_users: 0, team_members: 0, new_users_last_7_days: 0, active_projects: 0, overdue_tasks: 0 };
  }
}

async function loadStats() {
  try {
    const { data } = await api.get("stats/");
    stats.value = {
      roles: data.roles || {},
      open_requests: data.open_requests || 0,
      active_contracts: data.active_contracts || 0,
      due_payments: data.due_payments || 0,
    };
  } catch (err) {
    stats.value = { roles: {}, open_requests: 0, active_contracts: 0, due_payments: 0 };
  }
}

async function loadOverdueTasks() {
  try {
    const { data } = await api.get("tasks/overdue/");
    overdueTasks.value = data || [];
  } catch (err) {
    overdueTasks.value = [];
  }
}

async function loadUpcomingTasks() {
  try {
    const { data } = await api.get("tasks/upcoming/", { params: { days: 7, limit: 8 } });
    upcomingTasks.value = data || [];
  } catch (err) {
    upcomingTasks.value = [];
  }
}

async function loadOpenRequests() {
  try {
    const { data } = await api.get("requests/team-open/");
    openRequests.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    openRequests.value = [];
  }
}

async function loadGrowProGoals() {
  try {
    const { data } = await api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 200, ordering: "due_date" } });
    const payload = data || {};
    growproGoals.value = Array.isArray(payload) ? payload : payload.results || [];
  } catch (err) {
    growproGoals.value = [];
  }
}

async function sendTaskReminders() {
  if (!isTeam.value || remindersSending.value) return;
  remindersSending.value = true;
  try {
    const { data } = await api.post("automation/task-reminders/", {
      days: 3,
      include_overdue: true,
      include_due_soon: true,
    });
    const notified = data?.tasks_notified ?? 0;
    showToast(`Reminder gesendet: ${notified} Tasks`, "success");
  } catch (err) {
    showToast("Reminder konnten nicht gesendet werden", "error");
  } finally {
    remindersSending.value = false;
  }
}

async function loadAll() {
  if (!isTeam.value || loading.value) return;
  loading.value = true;
  await Promise.all([
    loadAnalyticsSummary(),
    loadTaskSummary(),
    loadProjectSummary(),
    loadGrowProSummary(),
    loadAdminOverview(),
    loadStats(),
    loadOverdueTasks(),
    loadUpcomingTasks(),
    loadOpenRequests(),
    loadGrowProGoals(),
  ]);
  loading.value = false;
}

onMounted(async () => {
  await fetchProfile();
  await loadAll();
});
</script>

<style scoped>
.analytics {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: var(--brand);
  margin: 0 0 6px;
}
.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}
.kpi {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.kpi .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.kpi strong {
  font-size: 22px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  background: rgba(99, 102, 241, 0.16);
  color: var(--text);
}
.pill.subtle {
  background: rgba(15, 23, 42, 0.06);
  color: var(--muted);
}
.breakdown {
  display: grid;
  gap: 10px;
}
.breakdown.compact {
  gap: 8px;
}
.break-item .row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.bar {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.2);
  overflow: hidden;
}
.bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
}
.subhead {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.mini-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.mini {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
  background: rgba(99, 102, 241, 0.08);
}
.mini .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}
.row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}
.badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}
.badge.danger {
  background: rgba(248, 113, 113, 0.18);
  color: #b91c1c;
}
.info {
  max-width: 520px;
}
@media (max-width: 720px) {
  .header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
