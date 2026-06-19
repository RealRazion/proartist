<template>
  <div class="dashboard">

    <!-- Hero -->
    <header class="card hero">
      <div class="hero-text">
        <p class="eyebrow">{{ isTeam ? "Team Operations" : "Workspace" }}</p>
        <h1>{{ greeting }}{{ displayName ? `, ${displayName}` : "" }}</h1>
        <p class="hero-subline" :class="{ 'has-issues': heroHasIssues }">{{ heroSubline }}</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="refresh" :disabled="loading">{{ loading ? "Lade..." : "Aktualisieren" }}</button>
        <template v-if="isTeam">
          <button class="btn" type="button" @click="openTaskModal">+ Task</button>
          <button class="btn ghost" type="button" @click="openUserModal">Einladen</button>
        </template>
        <template v-else>
          <button class="btn ghost" type="button" @click="goTo('me')">Mein Profil</button>
          <button class="btn ghost" type="button" @click="goTo('projects')">Projekte</button>
        </template>
      </div>
    </header>

    <!-- TEAM VIEW -->
    <template v-if="isTeam">

      <!-- Alles OK -->
      <section class="card ok-banner" v-if="!loading && totalAttentionCount === 0">
        <span class="ok-check">✓</span>
        <div>
          <strong>Alles im grünen Bereich</strong>
          <p class="muted">Keine überfälligen Tasks, offenen Reviews, Requests oder fälligen GrowPro-Ziele.</p>
        </div>
        <button class="btn ghost" type="button" @click="goTo('tasks')">Task Board →</button>
      </section>

      <!-- Handlungsbedarf -->
      <section class="card section" v-if="totalAttentionCount">
        <div class="section-head">
          <h2>Braucht deine Aufmerksamkeit <span class="count-badge">{{ totalAttentionCount }}</span></h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Task Board →</button>
        </div>
        <p class="attention-hint">Du hast {{ totalAttentionCount }} Angelegenheiten, die deine Aufmerksamkeit brauchen!</p>
        <ul class="item-list">
          <li v-for="item in urgentItems" :key="item.key" :data-urgency="item.urgency">
            <div class="item-body">
              <span class="cat-tag" :data-cat="item.cat">{{ item.catLabel }}</span>
              <strong class="item-title">{{ item.title }}</strong>
              <span class="item-sub">{{ item.sub }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="item.tone">{{ item.toneLabel }}</span>
              <button
                v-for="action in item.actions"
                :key="action.text"
                :class="['btn', 'tiny', action.ghost !== false ? 'ghost' : '', action.danger ? 'danger' : '']"
                type="button"
                @click="action.fn()"
                :disabled="action.disabled"
              >{{ action.text }}</button>
            </div>
          </li>
        </ul>
      </section>

      <!-- Diese Woche fällig -->
      <section class="card section" v-if="thisWeekItems.length">
        <div class="section-head">
          <h2>Diese Woche fällig</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Alle Tasks →</button>
        </div>
        <ul class="item-list compact">
          <li v-for="item in thisWeekItems" :key="item.key">
            <div class="item-body">
              <strong class="item-title">{{ item.title }}</strong>
              <span class="item-sub">{{ item.sub }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="item.tone">{{ item.dateLabel }}</span>
              <button class="btn ghost tiny" type="button" @click="goToRoute(item.route)">Öffnen</button>
            </div>
          </li>
        </ul>
      </section>

      <!-- GrowPro-Handlungsbedarf (nur wenn relevant) -->
      <section class="card section" v-if="growproAttentionItems.length">
        <div class="section-head">
          <h2>GrowPro: Update nötig</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('growpro')">Alle Ziele →</button>
        </div>
        <ul class="item-list compact">
          <li v-for="goal in growproAttentionItems" :key="goal.id">
            <div class="item-body">
              <strong class="item-title">{{ goal.title }}</strong>
              <span class="item-sub">{{ goal.due_date ? `Frist: ${formatDate(goal.due_date)}` : "Kein Fälligkeitsdatum" }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="isGrowproStale(goal) ? 'soon' : dueState(goal.due_date)">
                {{ isGrowproStale(goal) ? "Update fehlt" : dueLabel(goal.due_date) }}
              </span>
              <button class="btn ghost tiny" type="button" @click="goTo('growpro')">Öffnen</button>
            </div>
          </li>
        </ul>
      </section>

    </template>

    <!-- ARTIST VIEW -->
    <template v-else>

      <!-- Erste Schritte (nur solange nicht abgeschlossen) -->
      <section class="card section" v-if="onboardingIncomplete">
        <div class="section-head">
          <h2>Erste Schritte</h2>
          <span class="muted">{{ onboarding.filter(i => i.done).length }}/{{ onboarding.length }} erledigt</span>
        </div>
        <ul class="item-list">
          <li v-for="item in onboarding" :key="item.key" :class="{ done: item.done }">
            <div class="item-body">
              <span class="step-check">{{ item.done ? "✓" : "○" }}</span>
              <strong class="item-title">{{ item.label }}</strong>
              <span class="item-sub">{{ item.hint }}</span>
            </div>
            <div class="item-actions">
              <button v-if="item.cta && !item.done" class="btn ghost tiny" type="button" @click="item.cta()">Jetzt →</button>
            </div>
          </li>
        </ul>
      </section>

      <!-- Meine Projekte -->
      <section class="card section">
        <div class="section-head">
          <h2>Meine Projekte</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('projects')">Alle anzeigen →</button>
        </div>
        <ul v-if="projects.length" class="project-grid">
          <li
            v-for="project in projects.slice(0, 6)"
            :key="project.id"
            class="project-card"
            @click="goToProject(project.id)"
          >
            <div class="project-dot" :data-status="project.status"></div>
            <div class="project-info">
              <strong>{{ project.title }}</strong>
              <span class="item-sub">{{ statusLabel(project.status) }}</span>
            </div>
            <span class="project-arrow">→</span>
          </li>
        </ul>
        <div class="empty-hint" v-else>
          <p class="muted">Noch keine Projekte vorhanden.</p>
          <button class="btn" type="button" @click="goTo('projects')">Projekt anlegen</button>
        </div>
      </section>

      <!-- GrowPro Ziele -->
      <section class="card section" v-if="growpro.length">
        <div class="section-head">
          <h2>GrowPro Ziele</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('growpro')">Alle →</button>
        </div>
        <ul class="item-list compact">
          <li v-for="goal in growpro.slice(0, 5)" :key="goal.id">
            <div class="item-body">
              <strong class="item-title">{{ goal.title }}</strong>
              <span class="item-sub">{{ goal.due_date ? `Frist: ${formatDate(goal.due_date)}` : "Laufendes Ziel" }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="isGrowproStale(goal) ? 'soon' : (goal.due_date ? dueState(goal.due_date) : 'ok')">
                {{ isGrowproStale(goal) ? "Update fällig" : (goal.due_date ? dueLabel(goal.due_date) : "Aktiv") }}
              </span>
            </div>
          </li>
        </ul>
      </section>

    </template>

    <!-- Modals -->
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
const tasks = ref([]);
const reviewTasks = ref([]);
const pendingReviews = ref([]);
const requests = ref([]);
const growpro = ref([]);
const projects = ref([]);
const examples = ref([]);
const reviewSaving = ref({});

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
const requestTypes = { COLLAB: "Collab-Anfrage", BOOK: "Booking-Anfrage", OTHER: "Anfrage" };
const statusMap = { PLANNED: "Geplant", IN_PROGRESS: "In Arbeit", REVIEW: "Review", DONE: "Abgeschlossen", ON_HOLD: "Pausiert" };

// Greetings & Hero
const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 11) return "Guten Morgen";
  if (h < 18) return "Guten Tag";
  return "Guten Abend";
});

const displayName = computed(() => (me.value?.name || me.value?.username || "").trim().split(" ")[0] || "");

const heroHasIssues = computed(() => {
  if (!isTeam.value) return false;
  return tasks.value.some(t => dueState(t.due_date) === "overdue") ||
    pendingReviews.value.length > 0 ||
    requests.value.length > 0 ||
    growproAttentionItems.value.length > 0;
});

const heroSubline = computed(() => {
  if (!isTeam.value) return "Dein Profil, Projekte und GrowPro-Ziele auf einen Blick.";
  const overdue = tasks.value.filter(t => dueState(t.due_date) === "overdue").length;
  const reviewCount = new Set([...reviewTasks.value, ...pendingReviews.value].map(t => t.id)).size;
  const reqCount = requests.value.length;
  const growproDue = growproAttentionItems.value.length;
  const parts = [];
  if (overdue > 0) parts.push(`${overdue} Task${overdue > 1 ? "s" : ""} überfällig`);
  if (reviewCount > 0) parts.push(`${reviewCount} warten auf Review`);
  if (reqCount > 0) parts.push(`${reqCount} offene${reqCount !== 1 ? "" : "r"} Request`);
  if (growproDue > 0) parts.push(`${growproDue} GrowPro fällig`);
  return parts.length ? parts.join(" · ") : "Alles im grünen Bereich. Weiter so!";
});

const totalAttentionCount = computed(() => urgentItems.value.length + growproAttentionItems.value.length);

// Urgent items (team)
const urgentItems = computed(() => {
  const items = [];

  // 1) Überfällige Tasks (zuerst)
  tasks.value
    .filter(t => dueState(t.due_date) === "overdue")
    .slice(0, 6)
    .forEach(task => {
      items.push({
        key: `overdue-${task.id}`,
        cat: "overdue",
        catLabel: "Überfällig",
        urgency: "high",
        title: task.title,
        sub: task.project_title || "Kein Projekt",
        tone: "overdue",
        toneLabel: formatDate(task.due_date),
        actions: [{ text: "Öffnen", ghost: true, fn: () => openTask(task) }],
      });
    });

  // 2) Tasks die reviewed werden müssen
  const reviewSet = new Map();
  [...reviewTasks.value, ...pendingReviews.value].forEach(t => {
    if (!reviewSet.has(t.id)) reviewSet.set(t.id, t);
  });
  [...reviewSet.values()].slice(0, 5).forEach(task => {
    items.push({
      key: `review-${task.id}`,
      cat: "review",
      catLabel: "Review",
      urgency: "medium",
      title: task.title,
      sub: task.project_title || "Kein Projekt",
      tone: "soon",
      toneLabel: "Warten auf Freigabe",
      actions: [
        { text: "Öffnen", ghost: true, fn: () => openTask(task) },
        {
          text: reviewSaving.value[task.id] ? "..." : "Als geprüft markieren",
          ghost: false,
          fn: () => markReviewed(task),
          disabled: !!reviewSaving.value[task.id],
        },
      ],
    });
  });

  // 3) Offene Requests
  requests.value.slice(0, 4).forEach(req => {
    items.push({
      key: `req-${req.id}`,
      cat: "request",
      catLabel: "Request",
      urgency: "low",
      title: requestTypeLabel(req.req_type),
      sub: `${req.sender_name} → ${req.receiver_name}`,
      tone: "info",
      toneLabel: "Offen",
      actions: [
        { text: "Annehmen", ghost: false, fn: () => respondRequest(req.id, "accept") },
        { text: "Ablehnen", ghost: true, danger: true, fn: () => respondRequest(req.id, "decline") },
      ],
    });
  });

  return items;
});

// Diese Woche fällig (team)
const thisWeekItems = computed(() => {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const in7 = new Date(today); in7.setDate(today.getDate() + 7);

  return tasks.value
    .filter(t => {
      const d = parseDate(t.due_date);
      return d && d >= today && d <= in7;
    })
    .sort((a, b) => parseDate(a.due_date) - parseDate(b.due_date))
    .slice(0, 8)
    .map(t => ({
      key: `week-${t.id}`,
      title: t.title,
      sub: t.project_title || "Kein Projekt",
      tone: dueState(t.due_date),
      dateLabel: formatDate(t.due_date),
      route: t.project
        ? { name: "project-detail", params: { projectId: t.project }, query: { taskId: t.id } }
        : { name: "tasks", query: { taskId: t.id } },
    }));
});

// GrowPro Handlungsbedarf (team)
const growproAttentionItems = computed(() =>
  growpro.value
    .filter(g => isGrowproStale(g) || ["overdue", "soon"].includes(dueState(g.due_date)))
    .slice(0, 6)
);

// Onboarding (artist)
const onboarding = computed(() => {
  const hasRoles = (me.value?.roles || []).length > 0;
  const hasExample = examples.value.length > 0;
  return [
    { key: "profile", label: "Profil vervollständigen", hint: "Name, Genre, Stadt und Socials eintragen.", done: Boolean(me.value?.name && me.value?.city), cta: () => goTo("me") },
    { key: "roles", label: "Rollen hinterlegen", hint: "Bestimmt deine Sichtbarkeit im Team.", done: hasRoles, cta: () => goTo("me") },
    { key: "example", label: "Beispiel hochladen", hint: "Track, Video oder Referenz teilen.", done: hasExample, cta: () => goTo("me") },
  ];
});

const onboardingIncomplete = computed(() => onboarding.value.some(i => !i.done));

// Helpers
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

function dueState(value) {
  const d = parseDate(value);
  if (!d) return "none";
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const target = new Date(d); target.setHours(0, 0, 0, 0);
  const diff = Math.round((target - start) / 86400000);
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "ok";
}

function dueLabel(value) {
  if (!value) return "Kein Termin";
  const state = dueState(value);
  if (state === "overdue") return "Überfällig";
  if (state === "soon") return "Bald fällig";
  return formatDate(value);
}

function growproUpdateDeadline(goal) {
  const base = parseDate(goal?.last_logged_at || goal?.created_at);
  return base ? new Date(base.getTime() + 72 * 3600 * 1000) : null;
}

function isGrowproStale(goal) {
  if (!goal || ["DONE", "ARCHIVED"].includes(goal.status)) return false;
  const dl = growproUpdateDeadline(goal);
  return dl ? dl.getTime() < Date.now() : false;
}

function priorityLabel(priority) { return priorityMap[priority] || priority || "-"; }
function requestTypeLabel(type) { return requestTypes[type] || type || "Request"; }
function statusLabel(status) { return statusMap[status] || status || "-"; }

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

// Data loading
async function loadTeamData() {
  const [tasksRes, reviewRes, pendingRes, reqRes, gpRes] = await Promise.all([
    api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS,REVIEW", include_done: 0, include_archived: 0, ordering: "due_date", page_size: 200 } }).catch(() => ({ data: [] })),
    api.get("tasks/", { params: { status: "REVIEW", include_done: 0, include_archived: 0, ordering: "due_date", page_size: 100 } }).catch(() => ({ data: [] })),
    api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", include_done: 1, include_archived: 0, ordering: "-completed_at", page_size: 100 } }).catch(() => ({ data: [] })),
    api.get("requests/team-open/").catch(() => ({ data: [] })),
    api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 150, ordering: "due_date" } }).catch(() => ({ data: [] })),
  ]);
  tasks.value = normalizeList(tasksRes.data);
  reviewTasks.value = normalizeList(reviewRes.data);
  pendingReviews.value = normalizeList(pendingRes.data);
  requests.value = normalizeList(reqRes.data);
  growpro.value = normalizeList(gpRes.data);
}

async function loadArtistData() {
  const [projectsRes, examplesRes, gpRes] = await Promise.all([
    api.get("projects/", { params: { include_archived: 0, page_size: 50 } }).catch(() => ({ data: [] })),
    me.value?.id ? api.get("examples/", { params: { profile: me.value.id } }).catch(() => ({ data: [] })) : Promise.resolve({ data: [] }),
    api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } }).catch(() => ({ data: [] })),
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

onMounted(refresh);

// Actions
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
    .then(({ data }) => { projectOptions.value = normalizeList(data).map(p => ({ id: p.id, title: p.title })); })
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
</script>

<style scoped>
.dashboard { display: grid; gap: 20px; }

/* Hero */
.hero { display: grid; grid-template-columns: 1.5fr 1fr; gap: 16px; align-items: start; background: linear-gradient(120deg, rgba(47,99,255,0.14), rgba(6,182,212,0.08)); }
.hero-text { display: grid; gap: 6px; }
.eyebrow { margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.12em; color: var(--brand); font-weight: 700; }
.hero h1 { margin: 0; font-size: clamp(22px, 3vw, 32px); line-height: 1.2; }
.hero-subline { margin: 0; color: var(--muted); font-size: 14px; }
.hero-subline.has-issues { color: var(--status-overdue, #ef4444); font-weight: 500; }
.hero-actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; align-items: start; padding-top: 4px; }

/* Sections */
.section { display: grid; gap: 14px; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 8px; }
.section-head h2 { margin: 0; font-size: 17px; font-weight: 600; display: flex; align-items: center; gap: 8px; }
.count-badge { display: inline-flex; align-items: center; justify-content: center; background: var(--brand); color: #fff; border-radius: 999px; font-size: 11px; font-weight: 700; min-width: 20px; height: 20px; padding: 0 6px; }
.attention-hint { margin: -4px 0 2px; font-size: 13px; color: var(--muted); }

/* OK Banner */
.ok-banner { display: flex; align-items: center; gap: 16px; padding: 16px 20px; background: rgba(34,197,94,0.08); border-color: rgba(34,197,94,0.3); }
.ok-check { font-size: 20px; color: var(--status-ok, #22c55e); flex-shrink: 0; }
.ok-banner > div { flex: 1; }
.ok-banner strong { display: block; margin-bottom: 2px; }

/* Item List */
.item-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.item-list li { display: flex; justify-content: space-between; align-items: center; gap: 12px; border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; background: var(--surface); transition: border-color 0.15s; }
.item-list li[data-urgency="high"] { border-left: 3px solid rgba(239,68,68,0.7); }
.item-list li[data-urgency="medium"] { border-left: 3px solid rgba(245,158,11,0.7); }
.item-list li.done { opacity: 0.5; }
.item-list.compact li { padding: 9px 14px; }
.item-body { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
.item-title { font-weight: 600; font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-sub { font-size: 12px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-actions { display: flex; align-items: center; gap: 6px; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }

/* Category tag */
.cat-tag { font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; padding: 2px 6px; border-radius: 4px; width: fit-content; }
.cat-tag[data-cat="overdue"] { background: rgba(239,68,68,0.15); color: #ef4444; }
.cat-tag[data-cat="review"] { background: rgba(245,158,11,0.15); color: #f59e0b; }
.cat-tag[data-cat="request"] { background: rgba(59,130,246,0.15); color: #3b82f6; }

/* Step check (onboarding) */
.step-check { font-size: 16px; color: var(--status-ok, #22c55e); flex-shrink: 0; align-self: start; margin-top: 1px; }

/* Badges */
.badge { border: 1px solid var(--border); border-radius: 999px; padding: 3px 9px; font-size: 11px; white-space: nowrap; background: rgba(59,130,246,0.12); color: var(--status-in-progress, #3b82f6); }
.badge[data-tone="overdue"] { background: rgba(239,68,68,0.15); color: var(--status-overdue, #ef4444); border-color: rgba(239,68,68,0.3); }
.badge[data-tone="soon"] { background: rgba(245,158,11,0.15); color: var(--status-soon, #f59e0b); border-color: rgba(245,158,11,0.3); }
.badge[data-tone="ok"] { background: rgba(34,197,94,0.13); color: var(--status-ok, #22c55e); border-color: rgba(34,197,94,0.3); }
.badge[data-tone="info"] { background: rgba(59,130,246,0.12); color: #3b82f6; }

/* Project grid (artist) */
.project-grid { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
.project-card { display: flex; align-items: center; gap: 12px; border: 1px solid var(--border); border-radius: 12px; padding: 12px 14px; background: var(--surface); cursor: pointer; transition: border-color 0.15s, background 0.15s; }
.project-card:hover { border-color: var(--brand); background: rgba(47,99,255,0.05); }
.project-dot { width: 10px; height: 10px; border-radius: 50%; background: var(--muted); flex-shrink: 0; }
.project-dot[data-status="IN_PROGRESS"] { background: #3b82f6; }
.project-dot[data-status="REVIEW"] { background: #f59e0b; }
.project-dot[data-status="DONE"] { background: #22c55e; }
.project-dot[data-status="PLANNED"] { background: #94a3b8; }
.project-dot[data-status="ON_HOLD"] { background: #f97316; }
.project-info { flex: 1; min-width: 0; display: grid; gap: 2px; }
.project-info strong { font-size: 14px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.project-arrow { color: var(--muted); font-size: 14px; flex-shrink: 0; }
.empty-hint { display: flex; flex-direction: column; align-items: flex-start; gap: 10px; }

/* Buttons */
.tiny { padding: 6px 10px; font-size: 12px; }
.btn.danger { color: #b91c1c; border-color: rgba(239,68,68,0.4); }

/* Modals */
.modal-backdrop { position: fixed; inset: 0; background: var(--modal-overlay); display: flex; align-items: center; justify-content: center; z-index: 50; padding: 16px; }
.modal { width: min(520px, 100%); max-height: 90vh; overflow: auto; display: grid; gap: 10px; background: var(--modal-bg); border: 1px solid var(--border); box-shadow: var(--modal-shadow); border-radius: 24px; padding: 24px; }
.form { display: grid; gap: 10px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 8px; }
.invite-link { border-top: 1px solid var(--border); padding-top: 12px; display: grid; gap: 8px; }

/* Responsive */
@media (max-width: 1100px) { .hero { grid-template-columns: 1fr; } .hero-actions { justify-content: flex-start; } }
@media (max-width: 780px) {
  .project-grid { grid-template-columns: 1fr; }
  .item-list li { flex-direction: column; align-items: flex-start; }
  .item-actions { justify-content: flex-start; }
  .modal-actions { flex-direction: column; }
}
</style>
