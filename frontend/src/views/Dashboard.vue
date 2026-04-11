<template>
  <div class="dashboard">
    <header class="card hero">
      <div>
        <p class="eyebrow">{{ isTeam ? "Team Operations" : "Workspace" }}</p>
        <h1>{{ greeting }}{{ displayName ? `, ${displayName}` : "" }}</h1>
        <p class="muted">{{ heroText }}</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="refresh" :disabled="loading">{{ loading ? "Lade..." : "Aktualisieren" }}</button>
        <template v-if="isTeam">
          <button class="btn" type="button" @click="openTaskModal">Task erstellen</button>
          <button class="btn ghost" type="button" @click="openUserModal">Benutzer einladen</button>
          <button class="btn ghost" type="button" @click="goTo('reviews')">Review</button>
          <button class="btn ghost" type="button" @click="goTo('analytics')">Analytics</button>
          <button class="btn ghost" type="button" @click="goTo('platforms')">UNYQ Hub</button>
        </template>
        <template v-else>
          <button class="btn ghost" type="button" @click="goTo('me')">Profil</button>
          <button class="btn ghost" type="button" @click="goTo('projects')">Projekte</button>
          <button class="btn ghost" type="button" @click="goTo('growpro')">GrowPro</button>
          <button class="btn ghost" type="button" @click="goTo('platforms')">UNYQ Hub</button>
        </template>
      </div>
    </header>

    <section v-if="isTeam" class="kpis">
      <article v-for="item in kpis" :key="item.key" class="card kpi" :data-tone="item.tone">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small class="muted">{{ item.hint }}</small>
      </article>
    </section>

    <section v-if="isTeam" class="grid">
      <article v-for="widgetId in widgetOrder" :key="widgetId" class="card panel">
        <div class="panel-head">
          <h2>{{ widgetConfigs[widgetId]?.title }}</h2>
          <button v-if="widgetConfigs[widgetId]?.cta" class="btn ghost tiny" type="button" @click="widgetConfigs[widgetId].cta.action()">{{ widgetConfigs[widgetId].cta.text }}</button>
        </div>
        <ul v-if="widgetConfigs[widgetId]?.content" class="list">
          <li v-for="(item, index) in widgetConfigs[widgetId].content" :key="index">
            <div>
              <strong>{{ item.title }}</strong>
              <p class="muted">{{ item.subtitle }}</p>
            </div>
            <div class="row-actions">
              <span v-for="badge in item.badges" :key="badge.text" class="badge" :data-tone="badge.tone">{{ badge.text }}</span>
              <span v-if="item.badge" class="badge" :data-tone="item.badge.tone">{{ item.badge.text }}</span>
              <button v-if="item.action" class="btn ghost tiny" type="button" @click="item.action()">Öffnen</button>
              <template v-if="item.actions">
                <button v-for="action in item.actions" :key="action.text" :class="['btn', 'tiny', action.danger ? 'danger' : 'ghost']" type="button" @click="action.action()" :disabled="action.disabled">{{ action.text }}</button>
              </template>
            </div>
          </li>
        </ul>
        <p v-else class="muted">{{ widgetConfigs[widgetId]?.emptyText }}</p>
      </article>
    </section>
    <section v-else class="grid artist-grid">
      <article class="card panel">
        <h2>Mein Startstatus</h2>
        <ul class="list">
          <li v-for="item in onboarding" :key="item.key">
            <div>
              <strong>{{ item.label }}</strong>
              <p class="muted">{{ item.hint }}</p>
            </div>
            <div class="row-actions">
              <span class="badge" :data-tone="item.done ? 'ok' : 'soon'">{{ item.done ? "Erledigt" : "Offen" }}</span>
              <button v-if="item.cta" class="btn ghost tiny" type="button" @click="item.cta()">Jetzt</button>
            </div>
          </li>
        </ul>
      </article>

      <article class="card panel">
        <h2>Meine Projekte</h2>
        <ul v-if="projects.length" class="list">
          <li v-for="project in projects.slice(0, 8)" :key="project.id">
            <div>
              <strong>{{ project.title }}</strong>
              <p class="muted">{{ project.description || "Keine Beschreibung" }}</p>
            </div>
            <div class="row-actions">
              <span class="badge">{{ statusLabel(project.status) }}</span>
              <button class="btn ghost tiny" type="button" @click="goToProject(project.id)">Oeffnen</button>
            </div>
          </li>
        </ul>
        <p v-else class="muted">Noch keine Projekte vorhanden.</p>
      </article>
    </section>

    <div v-if="taskModalOpen" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card">
        <h3>Task erstellen</h3>
        <form class="form" @submit.prevent="submitTask">
          <input class="input" v-model.trim="taskForm.title" placeholder="Titel" required />
          <select class="input" v-model="taskForm.projectId">
            <option value="">Kein Projekt</option>
            <option v-for="project in projectOptions" :key="project.id" :value="project.id">{{ project.title }}</option>
          </select>
          <input class="input" type="date" v-model="taskForm.dueDate" />
          <select class="input" v-model="taskForm.priority">
            <option v-for="opt in taskPriorityOptions" :key="opt" :value="opt">{{ priorityLabel(opt) }}</option>
          </select>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">{{ taskSaving ? "Speichere..." : "Erstellen" }}</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="userModalOpen" class="modal-backdrop" @click.self="closeUserModal">
      <div class="modal card">
        <h3>Benutzer einladen</h3>
        <form class="form" @submit.prevent="submitUserInvite">
          <input class="input" type="email" v-model.trim="userForm.email" placeholder="E-Mail" required />
          <input class="input" v-model.trim="userForm.name" placeholder="Name (optional)" />
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeUserModal" :disabled="userSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="userSaving">{{ userSaving ? "Sende..." : "Einladen" }}</button>
          </div>
        </form>
        <div v-if="inviteLink" class="invite-link">
          <input class="input" readonly :value="inviteLink" />
          <button class="btn ghost tiny" type="button" @click="copyInviteLink">Kopieren</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const loading = ref(false);
const projectSummary = ref({ total: 0, active: 0, archived: 0 });
const tasks = ref([]);
const reviewTasks = ref([]);
const pendingReviews = ref([]);
const requests = ref([]);
const growpro = ref([]);
const activity = ref([]);
const projects = ref([]);
const examples = ref([]);
const reviewSaving = ref({});

// Widget configuration
const widgetOrder = ref(JSON.parse(localStorage.getItem('dashboardWidgets') || '["priorities", "reviews", "deadlines", "requests"]'));

const taskModalOpen = ref(false);
const taskSaving = ref(false);
const taskForm = ref({ title: "", projectId: "", dueDate: "", priority: "MEDIUM" });
const projectOptions = ref([]);

const userModalOpen = ref(false);
const userSaving = ref(false);
const userForm = ref({ email: "", name: "" });
const inviteLink = ref("");

const taskPriorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const priorityMap = { LOW: "Niedrig", MEDIUM: "Mittel", HIGH: "Hoch", CRITICAL: "Kritisch" };
const requestTypes = { COLLAB: "Collab", BOOK: "Booking", OTHER: "Andere" };
const statusMap = { PLANNED: "Geplant", IN_PROGRESS: "In Arbeit", REVIEW: "Review", DONE: "Abgeschlossen", ON_HOLD: "Pausiert" };
const score = { LOW: 1, MEDIUM: 1, HIGH: 2, CRITICAL: 3 };

const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 11) return "Guten Morgen";
  if (h < 18) return "Guten Tag";
  return "Guten Abend";
});

const displayName = computed(() => (me.value?.name || me.value?.username || "").trim().split(" ")[0] || "");

const overdueCount = computed(() => tasks.value.filter((t) => dueState(t.due_date) === "overdue").length);
const soonCount = computed(() => tasks.value.filter((t) => dueState(t.due_date) === "soon").length);
const staleGrowproCount = computed(() => growpro.value.filter(isGrowproStale).length);

const heroText = computed(() => {
  if (!isTeam.value) return "Halte dein Profil, Projekte und GrowPro-Ziele zentral im Blick.";
  if (overdueCount.value > 0) return `${overdueCount.value} Tasks sind ueberfaellig. Bitte zuerst kritische Punkte stabilisieren.`;
  if (pendingReviews.value.length > 0) return `${pendingReviews.value.length} abgeschlossene Tasks warten auf Review.`;
  return "Operations-Fokus: Prioritaet, Reviews, Fristen, Requests und Aktivitaetsfeed.";
});

const kpis = computed(() => [
  { key: "tasks", label: "Offene Tasks", value: tasks.value.length, hint: `${overdueCount.value} ueberfaellig · ${soonCount.value} zeitnah`, tone: overdueCount.value ? "danger" : soonCount.value ? "warning" : "ok" },
  { key: "reviews", label: "Review Queue", value: reviewTasks.value.length + pendingReviews.value.length, hint: `${reviewTasks.value.length} REVIEW · ${pendingReviews.value.length} nicht geprueft`, tone: pendingReviews.value.length ? "warning" : "ok" },
  { key: "projects", label: "Aktive Projekte", value: projectSummary.value.active, hint: `Gesamt ${projectSummary.value.total} · Archiviert ${projectSummary.value.archived}`, tone: "info" },
  { key: "requests", label: "Offene Requests", value: requests.value.length, hint: "Schnelle Entscheidungen", tone: requests.value.length ? "warning" : "ok" },
  { key: "growpro", label: "GrowPro Watch", value: growpro.value.length, hint: `${staleGrowproCount.value} stale`, tone: staleGrowproCount.value ? "danger" : "ok" },
]);

const widgetConfigs = computed(() => ({
  priorities: {
    id: "priorities",
    title: "Prioritäten heute",
    cta: { text: "Task Board", action: () => goTo('tasks') },
    content: urgentTasks.value.length ? urgentTasks.value.map(task => ({
      title: task.title,
      subtitle: task.project_title || "Kein Projekt",
      badges: [
        { text: priorityLabel(task.priority), tone: 'info' },
        { text: dueLabel(task.due_date), tone: dueState(task.due_date) }
      ],
      action: () => openTask(task)
    })) : null,
    emptyText: "Keine dringenden Tasks."
  },
  reviews: {
    id: "reviews",
    title: "Review Queue",
    cta: { text: "Alle Reviews", action: () => goTo('reviews') },
    content: reviewList.value.length ? reviewList.value.map(entry => ({
      title: entry.title,
      subtitle: entry.subtitle,
      badges: [{ text: entry.flag, tone: entry.tone }],
      actions: [
        { text: "Zur Task", action: () => openTask(entry.task) },
        { text: reviewSaving.value[entry.task.id] ? "..." : "Geprüft", action: () => markReviewed(entry.task), disabled: reviewSaving.value[entry.task.id] }
      ]
    })) : null,
    emptyText: "Keine offenen Reviews."
  },
  deadlines: {
    id: "deadlines",
    title: "Nächste Fristen",
    cta: { text: "Timeline", action: () => goTo('timeline') },
    content: deadlines.value.length ? deadlines.value.map(entry => ({
      title: entry.title,
      subtitle: entry.subtitle,
      badges: [{ text: entry.dateLabel, tone: entry.tone }],
      action: () => goToRoute(entry.route)
    })) : null,
    emptyText: "Keine Fristen verfügbar."
  },
  requests: {
    id: "requests",
    title: "Requests & Feed",
    cta: { text: "Aktivität", action: () => goTo('activity') },
    content: [
      ...requests.value.slice(0, 4).map(req => ({
        title: requestTypeLabel(req.req_type),
        subtitle: `${req.sender_name} -> ${req.receiver_name}`,
        actions: [
          { text: "Annehmen", action: () => respondRequest(req.id, 'accept') },
          { text: "Ablehnen", action: () => respondRequest(req.id, 'decline'), danger: true }
        ]
      })),
      ...activity.value.slice(0, 4).map(item => ({
        title: item.title,
        subtitle: item.description || "Keine Details",
        badge: { text: formatDateTime(item.created_at), tone: 'info' }
      }))
    ],
    emptyText: "Keine Requests oder Aktivitäten."
  },
  onboarding: {
    id: "onboarding",
    title: "Mein Startstatus",
    content: onboarding.value.map(item => ({
      title: item.label,
      subtitle: item.hint,
      badges: [{ text: item.done ? "Erledigt" : "Offen", tone: item.done ? 'ok' : 'soon' }],
      action: item.cta
    }))
  },
  projects: {
    id: "projects",
    title: "Meine Projekte",
    content: projects.value.length ? projects.value.slice(0, 8).map(project => ({
      title: project.title,
      subtitle: project.description || "Keine Beschreibung",
      badges: [{ text: statusLabel(project.status), tone: 'info' }],
      action: () => goToProject(project.id)
    })) : null,
    emptyText: "Noch keine Projekte vorhanden."
  }
}));

const currentWidgets = computed(() => {
  const configs = widgetConfigs.value;
  if (isTeam.value) {
    return widgetOrder.value.map(id => configs[id]).filter(Boolean);
  } else {
    return ['onboarding', 'projects'].map(id => configs[id]);
  }
});

const urgentTasks = computed(() =>
  [...tasks.value]
    .filter((task) => dueState(task.due_date) !== "ok" || task.priority === "CRITICAL")
    .sort((a, b) => {
      const rank = { overdue: 0, soon: 1, ok: 2, none: 3 };
      const aRank = rank[dueState(a.due_date)] ?? 3;
      const bRank = rank[dueState(b.due_date)] ?? 3;
      if (aRank !== bRank) return aRank - bRank;
      return (score[b.priority] || 0) - (score[a.priority] || 0);
    })
    .slice(0, 8)
);

const reviewList = computed(() => [
  ...reviewTasks.value.map((task) => ({ key: `review-${task.id}`, task, title: task.title, subtitle: task.project_title || "Kein Projekt", flag: "Review", tone: dueState(task.due_date) })),
  ...pendingReviews.value.map((task) => ({ key: `pending-${task.id}`, task, title: task.title, subtitle: task.project_title || "Kein Projekt", flag: "Nicht geprueft", tone: "warning" })),
].slice(0, 8));

const deadlines = computed(() => {
  const entries = [];
  tasks.value.forEach((task) => {
    if (!task.due_date) return;
    entries.push({
      key: `task-${task.id}`,
      title: task.title,
      subtitle: `Task · ${task.project_title || "Kein Projekt"}`,
      date: parseDate(task.due_date),
      dateLabel: formatDate(task.due_date),
      tone: dueState(task.due_date),
      route: task.project ? { name: "project-detail", params: { projectId: task.project }, query: { taskId: task.id } } : { name: "tasks", query: { taskId: task.id } },
    });
  });
  growpro.value.forEach((goal) => {
    if (goal.due_date) {
      entries.push({ key: `gp-${goal.id}`, title: goal.title, subtitle: "GrowPro Frist", date: parseDate(goal.due_date), dateLabel: formatDate(goal.due_date), tone: dueState(goal.due_date), route: { name: "growpro" } });
    }
    const updateDeadline = growproUpdateDeadline(goal);
    if (updateDeadline) {
      entries.push({ key: `gp-u-${goal.id}`, title: goal.title, subtitle: "GrowPro Update (72h)", date: updateDeadline, dateLabel: formatDate(updateDeadline), tone: dueState(updateDeadline), route: { name: "growpro" } });
    }
  });
  return entries.filter((e) => e.date).sort((a, b) => a.date - b.date).slice(0, 10);
});

const onboarding = computed(() => {
  const hasRoles = (me.value?.roles || []).length > 0;
  const hasExample = examples.value.length > 0;
  return [
    { key: "profile", label: "Profil vervollstaendigen", hint: "Name, Genre, Stadt und Socials pflegen.", done: Boolean(me.value?.name && me.value?.city), cta: () => goTo("me") },
    { key: "roles", label: "Rollen hinterlegen", hint: "Definiert deine Sichtbarkeit im Team.", done: hasRoles, cta: hasRoles ? null : () => goTo("me") },
    { key: "example", label: "Beispiel hochladen", hint: "Track, Video oder Referenz teilen.", done: hasExample, cta: hasExample ? null : () => goTo("me") },
  ];
});

function normalizeList(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

function parseDate(value) {
  const d = value ? new Date(value) : null;
  return d && !Number.isNaN(d.getTime()) ? d : null;
}

function formatDate(value) {
  const d = parseDate(value);
  if (!d) return "-";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }).format(d);
}

function formatDateTime(value) {
  const d = parseDate(value);
  if (!d) return "-";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(d);
}

function dueState(value) {
  const d = parseDate(value);
  if (!d) return "none";
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const target = new Date(d); target.setHours(0, 0, 0, 0);
  const diff = Math.round((target - start) / (1000 * 60 * 60 * 24));
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "ok";
}

function dueLabel(value) {
  if (!value) return "Kein Termin";
  const state = dueState(value);
  if (state === "overdue") return "Ueberfaellig";
  if (state === "soon") return "Faellig bald";
  return "Geplant";
}

function priorityLabel(priority) { return priorityMap[priority] || priority || "-"; }
function requestTypeLabel(type) { return requestTypes[type] || type || "Request"; }
function statusLabel(status) { return statusMap[status] || status || "-"; }

function growproUpdateDeadline(goal) {
  const base = parseDate(goal?.last_logged_at || goal?.created_at);
  return base ? new Date(base.getTime() + 72 * 60 * 60 * 1000) : null;
}

function isGrowproStale(goal) {
  if (!goal || ["DONE", "ARCHIVED"].includes(goal.status)) return false;
  const updateDeadline = growproUpdateDeadline(goal);
  return updateDeadline ? updateDeadline.getTime() < Date.now() : false;
}

function goTo(name, query = null) { router.push(query ? { name, query } : { name }); }
function goToProject(projectId) { router.push({ name: "project-detail", params: { projectId } }); }
function goToRoute(route) { if (route) router.push(route); }

function openTask(task) {
  if (!task) return;
  if (task.project) {
    router.push({ name: "project-detail", params: { projectId: task.project }, query: { taskId: task.id } });
    return;
  }
  router.push({ name: "tasks", query: { taskId: task.id } });
}

async function loadTeamData() {
  const [summaryRes, tasksRes, reviewRes, pendingRes, reqRes, gpRes, actRes] = await Promise.all([
    api.get("projects/summary/").catch(() => ({ data: {} })),
    api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS,REVIEW", include_done: 0, include_archived: 0, ordering: "due_date", page_size: 200 } }).catch(() => ({ data: [] })),
    api.get("tasks/", { params: { status: "REVIEW", include_done: 0, include_archived: 0, ordering: "due_date", page_size: 100 } }).catch(() => ({ data: [] })),
    api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", include_done: 1, include_archived: 0, ordering: "-completed_at", page_size: 100 } }).catch(() => ({ data: [] })),
    api.get("requests/team-open/").catch(() => ({ data: [] })),
    api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 150, ordering: "due_date" } }).catch(() => ({ data: [] })),
    api.get("activity-feed/", { params: { limit: 30 } }).catch(() => ({ data: [] })),
  ]);
  projectSummary.value = { total: summaryRes.data?.total || 0, active: summaryRes.data?.active || 0, archived: summaryRes.data?.archived || 0 };
  tasks.value = normalizeList(tasksRes.data);
  reviewTasks.value = normalizeList(reviewRes.data);
  pendingReviews.value = normalizeList(pendingRes.data);
  requests.value = normalizeList(reqRes.data);
  growpro.value = normalizeList(gpRes.data);
  activity.value = normalizeList(actRes.data);
}

async function loadArtistData() {
  const [projectsRes, examplesRes, gpRes] = await Promise.all([
    api.get("projects/", { params: { include_archived: 0, page_size: 50 } }).catch(() => ({ data: [] })),
    me.value?.id ? api.get("examples/", { params: { profile: me.value.id } }).catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
    api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 150, ordering: "due_date" } }).catch(() => ({ data: [] })),
  ]);
  projects.value = normalizeList(projectsRes.data);
  examples.value = normalizeList(examplesRes.data);
  growpro.value = normalizeList(gpRes.data);
}

async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);
    if (isTeam.value) await loadTeamData();
    else await loadArtistData();
  } finally {
    loading.value = false;
  }
}

async function markReviewed(task) {
  if (!task?.id) return;
  reviewSaving.value = { ...reviewSaving.value, [task.id]: true };
  try {
    await api.patch(`tasks/${task.id}/`, { status: "DONE", review_status: "REVIEWED" });
    showToast("Review gesetzt", "success");
    await loadTeamData();
  } catch {
    showToast("Review konnte nicht gespeichert werden", "error");
  } finally {
    reviewSaving.value = { ...reviewSaving.value, [task.id]: false };
  }
}

async function respondRequest(id, action) {
  try {
    await api.post(`requests/${id}/${action === "accept" ? "accept" : "decline"}/`);
    showToast(action === "accept" ? "Request angenommen" : "Request abgelehnt", "success");
    await loadTeamData();
  } catch {
    showToast("Aktion fehlgeschlagen", "error");
  }
}

function openTaskModal() {
  taskForm.value = { title: "", projectId: "", dueDate: "", priority: "MEDIUM" };
  taskModalOpen.value = true;
  api.get("projects/", { params: { include_archived: 0, include_done: 0, page_size: 100 } })
    .then(({ data }) => { projectOptions.value = normalizeList(data).map((p) => ({ id: p.id, title: p.title })); })
    .catch(() => { projectOptions.value = []; });
}

function closeTaskModal() { if (!taskSaving.value) taskModalOpen.value = false; }

async function submitTask() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  try {
    const payload = { title: taskForm.value.title.trim(), status: "OPEN", priority: taskForm.value.priority, task_type: "EXTERNAL", due_date: taskForm.value.dueDate || null };
    if (taskForm.value.projectId) payload.project = Number(taskForm.value.projectId);
    await api.post("tasks/", payload);
    showToast("Task erstellt", "success");
    taskModalOpen.value = false;
    await loadTeamData();
  } catch {
    showToast("Task konnte nicht erstellt werden", "error");
  } finally {
    taskSaving.value = false;
  }
}

function openUserModal() {
  userForm.value = { email: "", name: "" };
  inviteLink.value = "";
  userModalOpen.value = true;
}

function closeUserModal() { if (!userSaving.value) userModalOpen.value = false; }

async function submitUserInvite() {
  if (!userForm.value.email.trim()) return;
  userSaving.value = true;
  try {
    const { data } = await api.post("invite/", { email: userForm.value.email.trim(), name: userForm.value.name.trim() });
    inviteLink.value = data?.invite_link || "";
    showToast("Einladung gesendet", "success");
  } catch {
    showToast("Einladung fehlgeschlagen", "error");
  } finally {
    userSaving.value = false;
  }
}

function copyInviteLink() {
  if (!inviteLink.value) return;
  if (navigator?.clipboard?.writeText) navigator.clipboard.writeText(inviteLink.value);
  showToast("Link kopiert", "success");
}

onMounted(refresh);
</script>

<style scoped>
.dashboard { display: grid; gap: 16px; }
.hero { display: grid; grid-template-columns: 1.5fr 1fr; gap: 12px; background: linear-gradient(120deg, rgba(47, 99, 255, 0.16), rgba(6, 182, 212, 0.1)); }
.eyebrow { margin: 0 0 6px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--brand); font-weight: 700; }
.hero h1 { margin: 0; font-size: clamp(24px, 3vw, 34px); }
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; align-items: start; }
.kpis { display: grid; gap: 10px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }
.kpi { display: grid; gap: 6px; }
.kpi span { font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); }
.kpi strong { font-size: 24px; }
.kpi[data-tone="danger"] { border-color: rgba(248, 113, 113, 0.45); background: rgba(248, 113, 113, 0.08); }
.kpi[data-tone="warning"] { border-color: rgba(245, 158, 11, 0.45); background: rgba(245, 158, 11, 0.08); }
.kpi[data-tone="ok"] { border-color: rgba(34, 197, 94, 0.4); background: rgba(34, 197, 94, 0.08); }
.grid { display: grid; gap: 12px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.artist-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.panel { display: grid; gap: 10px; align-content: start; }
.panel-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.panel-head h2 { margin: 0; font-size: 18px; }
.list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.list li { border: 1px solid var(--border); border-radius: 12px; padding: 10px; background: var(--surface); display: flex; justify-content: space-between; gap: 10px; }
.list li[data-tone="overdue"] { border-color: rgba(248, 113, 113, 0.45); }
.list li[data-tone="soon"] { border-color: rgba(245, 158, 11, 0.45); }
.row-actions { display: flex; gap: 6px; flex-wrap: wrap; justify-content: flex-end; align-items: center; }
.badge { border: 1px solid var(--border); border-radius: 999px; padding: 2px 8px; font-size: 11px; background: rgba(59, 130, 246, 0.15); color: var(--status-in-progress); }
.badge[data-tone="overdue"] { background: rgba(248, 113, 113, 0.18); color: var(--status-overdue); }
.badge[data-tone="soon"] { background: rgba(245, 158, 11, 0.18); color: var(--status-soon); }
.badge[data-tone="ok"] { background: rgba(34, 197, 94, 0.16); color: var(--status-ok); }
.tiny { padding: 6px 10px; font-size: 12px; }
.btn.danger { color: #b91c1c; border-color: rgba(248, 113, 113, 0.45); }
.modal-backdrop { position: fixed; inset: 0; background: rgba(2, 6, 23, 0.55); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px; }
.modal { width: min(540px, 100%); max-height: 90vh; overflow: auto; display: grid; gap: 10px; }
.form { display: grid; gap: 10px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
.invite-link { border-top: 1px solid var(--border); padding-top: 10px; display: grid; gap: 8px; }
@media (max-width: 1100px) { .hero { grid-template-columns: 1fr; } .hero-actions { justify-content: flex-start; } }
@media (max-width: 780px) {
  .grid, .artist-grid { grid-template-columns: 1fr; }
  .list li, .panel-head { flex-direction: column; align-items: flex-start; }
  .row-actions { justify-content: flex-start; }
  .hero-actions .btn, .modal-actions .btn { width: 100%; justify-content: center; }
  .modal-actions { flex-direction: column; }
}
</style>
