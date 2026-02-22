<template>
  <div class="dashboard">
    <section class="card spotlight" v-if="dashboardSlides.length">
      <div class="spotlight-head">
        <div>
          <p class="eyebrow">Dringend</p>
          <h2>Fristen & Updates</h2>
          <p class="muted small">Deine naechsten Aufgaben und GrowPro Updates im Blick.</p>
        </div>
      </div>
      <div class="slide" :class="activeSlide?.tone" :data-status="activeSlide?.status">
        <div class="slide-top">
          <div v-if="activeSlide?.tone === 'warning'" class="warn-icon">!</div>
          <div>
            <h3>{{ activeSlide?.title }}</h3>
            <p class="muted">{{ activeSlide?.message }}</p>
          </div>
        </div>
        <ul v-if="activeSlide?.items?.length" class="slide-list">
          <li v-for="item in activeSlide.items" :key="item.key">
            <span>{{ item.title }}</span>
            <span class="badge">{{ item.date }}</span>
          </li>
        </ul>
        <div v-if="activeSlide?.cta" class="slide-actions">
          <button class="btn ghost" type="button" @click="handleSlideCta(activeSlide)">
            {{ activeSlide.cta.label }}
          </button>
        </div>
      </div>
      <div class="spotlight-footer">
        <div class="slide-dots">
          <button
            v-for="(slide, index) in dashboardSlides"
            :key="slide.key"
            class="dot"
            :class="{ active: index === slideIndex }"
            type="button"
            @click="goToSlide(index)"
          ></button>
        </div>
        <div class="spotlight-nav">
          <button class="nav-btn" type="button" @click="prevSlide" :disabled="!hasPrevSlide">
            &lt;
          </button>
          <button class="nav-btn" type="button" @click="nextSlide" :disabled="!hasNextSlide">
            &gt;
          </button>
        </div>
      </div>
    </section>

    <div v-if="isTeam" class="actions-bar">
      <div class="actions">
        <button class="btn" type="button" @click="openTaskModal">Task erstellen</button>
        <button class="btn ghost" type="button" @click="openUserModal">Benutzer anlegen</button>
      </div>
    </div>

    <section v-if="isTeam" class="card overview">
      <div class="overview-head">
        <div>
          <h2>Ueberblick</h2>
          <p class="muted">Schneller Status fuer Projekte, Tasks und Requests.</p>
        </div>
        <div class="overview-actions">
          <button class="btn ghost tiny" type="button" @click="refresh" :disabled="loading">Neu laden</button>
          <button class="btn ghost tiny" type="button" @click="goTo('analytics')">Analytics oeffnen</button>
        </div>
      </div>
      <div class="overview-grid">
        <div class="stat">
          <span class="label">Projekte aktiv</span>
          <strong>{{ projectSummary.active }}</strong>
          <small class="muted">Archiviert {{ projectSummary.archived }}</small>
        </div>
        <div class="stat">
          <span class="label">Offene Tasks</span>
          <strong>{{ activeTasksTotal }}</strong>
          <small class="muted">Ueberfaellig {{ overdueTasks.length }}</small>
        </div>
        <div class="stat">
          <span class="label">Requests offen</span>
          <strong>{{ teamRequests.length }}</strong>
          <small class="muted">Heute priorisieren</small>
        </div>
        <div class="stat">
          <span class="label">GrowPro faellig</span>
          <strong>{{ growProDueSoon }}</strong>
          <small class="muted">Ueberfaellig {{ growProOverdue }}</small>
        </div>
      </div>
      <div class="overview-strip">
        <span class="strip-item">Tasks aktiv <strong>{{ activeTasksTotal }}</strong></span>
        <span class="strip-item">Projekte aktiv <strong>{{ projectSummary.active }}</strong></span>
        <span class="strip-item">GrowPro offen <strong>{{ growProGoals.length }}</strong></span>
      </div>
    </section>

    <section v-if="isTeam" class="grid">
      <div class="card focus">
        <div class="section-head">
          <h2>Tasks Fokus</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Zum Board</button>
        </div>
        <div class="task-columns">
          <div>
            <h3>Ueberfaellig</h3>
            <ul v-if="topOverdueTasks.length" class="list">
              <li v-for="task in topOverdueTasks" :key="`overdue-${task.id}`">
                <div class="row">
                  <strong>{{ task.title }}</strong>
                  <span class="badge danger">{{ formatTaskDate(task.due_date) }}</span>
                </div>
                <small class="muted">{{ taskProjectLabel(task) }}</small>
              </li>
            </ul>
            <p v-else class="muted small">Keine ueberfaelligen Tasks.</p>
          </div>
          <div>
            <h3>Aktiv</h3>
            <ul v-if="topActiveTasks.length" class="list">
              <li v-for="task in topActiveTasks" :key="`active-${task.id}`">
                <div class="row">
                  <strong>{{ task.title }}</strong>
                  <span class="badge">{{ task.due_date ? formatTaskDate(task.due_date) : "Kein Termin" }}</span>
                </div>
                <small class="muted">{{ taskProjectLabel(task) }}</small>
              </li>
            </ul>
            <p v-else class="muted small">Keine aktiven Tasks.</p>
          </div>
        </div>
      </div>

      <div class="card focus">
        <div class="section-head">
          <h2>Requests</h2>
          <button class="btn ghost tiny" type="button" @click="loadTeamRequests" :disabled="loadingRequests">
            {{ loadingRequests ? "Lade..." : "Neu laden" }}
          </button>
        </div>
        <ul v-if="topRequests.length" class="list">
          <li v-for="request in topRequests" :key="request.id">
            <div class="row">
              <div class="flex-1">
                <strong>{{ requestTypeLabel(request.req_type) }}</strong>
                <p class="muted small">{{ request.sender_name }} -> {{ request.receiver_name }}</p>
                <p v-if="request.message" class="muted small">{{ request.message }}</p>
              </div>
              <div class="request-actions">
                <button class="btn ghost tiny" type="button" @click="respondRequest(request.id, 'accept')">
                  Annehmen
                </button>
                <button class="btn ghost danger tiny" type="button" @click="respondRequest(request.id, 'decline')">
                  Ablehnen
                </button>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="muted small">Keine offenen Requests.</p>
      </div>
    </section>

    <section v-if="!isTeam" class="card onboarding">
      <h2>Dein Start</h2>
      <p class="muted">Die wichtigsten Schritte, damit du schnell gefunden wirst.</p>
      <ul class="list">
        <li v-for="item in onboarding" :key="item.label" class="row">
          <span class="check">{{ item.done ? "OK" : "-" }}</span>
          <div class="flex-1">
            <strong>{{ item.label }}</strong>
            <p class="muted small">{{ item.hint }}</p>
          </div>
          <button v-if="item.cta" class="btn ghost tiny" type="button" @click="item.cta.action">
            {{ item.cta.label }}
          </button>
        </li>
      </ul>
    </section>

    <section v-if="!isTeam" class="card project-overview">
      <div class="section-head">
        <h2>Meine Projekte</h2>
        <button class="btn ghost tiny" type="button" @click="goTo('projects')">Alle Projekte</button>
      </div>
      <ul v-if="projects.length" class="list">
        <li v-for="project in projects.slice(0, 6)" :key="project.id">
          <div class="row">
            <router-link class="project-link" :to="{ name: 'project-detail', params: { projectId: project.id } }">
              <strong>{{ project.title }}</strong>
            </router-link>
            <span class="badge">{{ statusLabel(project.status) }}</span>
          </div>
          <p class="muted small">{{ project.description || "Keine Beschreibung vorhanden." }}</p>
        </li>
      </ul>
      <p v-else class="muted small">Noch keine Projekte.</p>
    </section>

    <div v-if="taskModalOpen" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Task erstellen</h3>
          <button class="btn ghost tiny" type="button" @click="closeTaskModal" :disabled="taskSaving">
            Schliessen
          </button>
        </div>
        <form class="form" @submit.prevent="submitTask">
          <label>
            Titel
            <input class="input" v-model.trim="taskForm.title" placeholder="Tasktitel" required />
          </label>
          <label>
            Projekt
            <select class="input" v-model="taskForm.projectId">
              <option value="">Kein Projekt</option>
              <option v-for="project in projectOptions" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Faellig am
            <input class="input" type="date" v-model="taskForm.dueDate" />
          </label>
          <label>
            Prioritaet
            <select class="input" v-model="taskForm.priority">
              <option v-for="opt in taskPriorityOptions" :key="opt" :value="opt">
                {{ taskPriorityLabels[opt] }}
              </option>
            </select>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">
              {{ taskSaving ? "Speichere..." : "Erstellen" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="userModalOpen" class="modal-backdrop" @click.self="closeUserModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Benutzer anlegen</h3>
          <button class="btn ghost tiny" type="button" @click="closeUserModal" :disabled="userSaving">
            Schliessen
          </button>
        </div>
        <form class="form" @submit.prevent="submitUserInvite">
          <label>
            E-Mail
            <input class="input" type="email" v-model.trim="userForm.email" placeholder="name@firma.de" required />
          </label>
          <label>
            Name (optional)
            <input class="input" v-model.trim="userForm.name" placeholder="Vorname Nachname" />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeUserModal" :disabled="userSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="userSaving">
              {{ userSaving ? "Sende..." : "Einladung senden" }}
            </button>
          </div>
        </form>
        <div v-if="inviteLink" class="invite-link">
          <p class="muted small">Einladungslink (falls E-Mail nicht ankommt):</p>
          <div class="invite-row">
            <input class="input" readonly :value="inviteLink" />
            <button class="btn ghost tiny" type="button" @click="copyInviteLink">Kopieren</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const examples = ref([]);
const projects = ref([]);
const projectSummary = ref({ total: 0, archived: 0, active: 0, done: 0, by_status: {} });

const overdueTasks = ref([]);
const activeTasks = ref([]);
const activeTasksTotal = ref(0);
const reviewTasks = ref([]);
const loadingReviewTasks = ref(false);
const teamRequests = ref([]);
const loadingRequests = ref(false);
const growProGoals = ref([]);
const loading = ref(false);
const userTasks = ref([]);
const loadingUserTasks = ref(false);

const slideIndex = ref(0);

const taskModalOpen = ref(false);
const taskSaving = ref(false);
const taskForm = ref(getDefaultTaskForm());
const projectOptions = ref([]);
const loadingProjectOptions = ref(false);

const userModalOpen = ref(false);
const userSaving = ref(false);
const userForm = ref({ email: "", name: "" });
const inviteLink = ref("");

const hasRoles = computed(() => (me.value?.roles || []).length > 0);
const hasExample = computed(() => examples.value.length > 0);

const onboarding = computed(() => [
  {
    label: "Profilinformationen vervollstaendigen",
    hint: "Name, Genre, Stadt und Social Links helfen beim Matching.",
    done: Boolean(me.value?.name && me.value?.city),
    cta: { label: "Profil bearbeiten", action: () => goTo("me") },
  },
  {
    label: "Rollen auswaehlen",
    hint: "Waehle aus, welche Rolle du im Netzwerk einnehmen moechtest.",
    done: hasRoles.value,
    cta: hasRoles.value ? null : { label: "Rollen waehlen", action: () => goTo("me") },
  },
  {
    label: "Mindestens ein Beispiel teilen",
    hint: "Fuege einen Track, ein Video oder ein Dokument hinzu.",
    done: hasExample.value,
    cta: hasExample.value ? null : { label: "Beispiel hochladen", action: () => goTo("me") },
  },
]);

const statusLabelMap = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Abgeschlossen",
  ON_HOLD: "Pausiert",
  OPEN: "Offen",
  ACCEPTED: "Angenommen",
  DECLINED: "Abgelehnt",
};

const requestTypeLabels = { COLLAB: "Collab", BOOK: "Booking", OTHER: "Andere" };

const taskPriorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const taskPriorityLabels = {
  LOW: "Niedrig",
  MEDIUM: "Mittel",
  HIGH: "Hoch",
  CRITICAL: "Kritisch",
};

const growProDueSoon = computed(() => {
  const now = Date.now();
  const oneDay = 24 * 60 * 60 * 1000;
  return (growProGoals.value || []).filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    const diff = due - now;
    return diff >= 0 && diff < oneDay;
  }).length;
});

const growProOverdue = computed(() => {
  const now = Date.now();
  return (growProGoals.value || []).filter((goal) => {
    if (!goal.due_date) return false;
    if (["DONE", "ARCHIVED"].includes(goal.status)) return false;
    const due = new Date(goal.due_date).getTime();
    return due < now;
  }).length;
});

const topOverdueTasks = computed(() => overdueTasks.value.slice(0, 4));
const topActiveTasks = computed(() => activeTasks.value.slice(0, 4));
const topRequests = computed(() => teamRequests.value.slice(0, 5));

const taskCandidates = computed(() => {
  const base = isTeam.value ? [...overdueTasks.value, ...activeTasks.value] : userTasks.value;
  return base.filter((task) => task?.due_date && !["DONE", "ARCHIVED"].includes(task.status));
});

const userTaskCandidates = computed(() => {
  if (!me.value?.id) return taskCandidates.value;
  const assigned = taskCandidates.value.filter(isTaskAssignedToMe);
  if (assigned.length) return assigned;
  const stakeholder = taskCandidates.value.filter(isTaskStakeholderForMe);
  if (stakeholder.length) return stakeholder;
  return taskCandidates.value;
});

const userOverdueTasks = computed(() =>
  userTaskCandidates.value
    .filter((task) => isTaskOverdue(task))
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
);

const userUpcomingTasks = computed(() =>
  userTaskCandidates.value
    .filter((task) => !isTaskOverdue(task))
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
);

const nextUserTask = computed(() => userUpcomingTasks.value[0] || null);

const reviewUrgentTasks = computed(() => reviewTasks.value.filter((task) => reviewUrgency(task) !== "ok"));
const reviewNextTask = computed(() =>
  reviewTasks.value
    .filter((task) => task?.due_date)
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
    .find(Boolean)
);

const relevantGrowProGoals = computed(() => {
  if (!me.value?.id) return growProGoals.value || [];
  if (isTeam.value) return growProGoals.value || [];
  return (growProGoals.value || []).filter((goal) => String(goal.profile?.id) === String(me.value.id));
});

const growProStaleGoals = computed(() =>
  relevantGrowProGoals.value.filter((goal) => isGrowProStale(goal))
);

const growProUpcomingGoals = computed(() => {
  const now = new Date();
  return relevantGrowProGoals.value
    .filter((goal) => !["DONE", "ARCHIVED"].includes(goal.status))
    .map((goal) => ({
      goal,
      deadline: growProUpdateDeadline(goal),
    }))
    .filter((entry) => entry.deadline && entry.deadline >= now && !isGrowProStale(entry.goal))
    .sort((a, b) => a.deadline.getTime() - b.deadline.getTime())
    .slice(0, 3);
});

const dashboardSlides = computed(() => {
  const slides = [];

  if (userOverdueTasks.value.length) {
    const oldest = userOverdueTasks.value[0];
    slides.push({
      key: "task-overdue",
      tone: "warning",
      status: "overdue",
      title: "Ueberfaellige Tasks",
      message: `Du hast ${userOverdueTasks.value.length} ueberfaellige Tasks. Aelteste Frist: ${formatFullDate(oldest.due_date)} (${oldest.title}).`,
      cta: { label: "Zur Task", route: "tasks" },
    });
  }

  if (isTeam.value && reviewTasks.value.length) {
    const hasOverdue = reviewTasks.value.some((task) => reviewUrgency(task) === "overdue");
    const hasSoon = reviewTasks.value.some((task) => reviewUrgency(task) === "soon");
    const status = hasOverdue ? "overdue" : hasSoon ? "soon" : "ok";
    const tone = status === "ok" ? "info" : "warning";
    const nextReview = reviewNextTask.value;
    slides.push({
      key: "review-queue",
      tone,
      status,
      title: "Review Tasks",
      message: hasOverdue
        ? `Es gibt ueberfaellige Review-Tasks. Naechste Frist: ${nextReview ? formatFullDate(nextReview.due_date) : "Bald"}.`
        : hasSoon
          ? `Review-Tasks sind bald faellig. Naechste Frist: ${nextReview ? formatFullDate(nextReview.due_date) : "Bald"}.`
          : `Es warten ${reviewTasks.value.length} Review-Tasks. Naechste Frist: ${nextReview ? formatFullDate(nextReview.due_date) : "Offen"}.`,
      items: reviewTasks.value.slice(0, 3).map((task) => ({
        key: `review-${task.id}`,
        title: task.title,
        date: task.due_date ? formatFullDate(task.due_date) : "Kein Termin",
      })),
      cta: { label: "Zur Review-Seite", route: "reviews" },
    });
  }

  if (nextUserTask.value) {
    const nextStatus = taskUrgency(nextUserTask.value);
    slides.push({
      key: `task-next-${nextUserTask.value.id}`,
      tone: "info",
      status: nextStatus,
      title: "Naechste Task-Frist",
      message: `Dein naechster faelliger Task ist am ${formatFullDate(nextUserTask.value.due_date)}: ${nextUserTask.value.title}.`,
      cta: { label: "Zur Task", route: "tasks" },
    });
  } else {
    slides.push({
      key: "task-empty",
      tone: "info",
      status: "ok",
      title: "Keine offenen Task-Fristen",
      message: "Aktuell sind keine faelligen Tasks fuer dich hinterlegt.",
      cta: { label: "Zu den Tasks", route: "tasks" },
    });
  }

  if (growProStaleGoals.value.length) {
    slides.push({
      key: "growpro-stale",
      tone: "warning",
      status: "overdue",
      title: "GrowPro Update ueberfaellig",
      message: `${growProStaleGoals.value.length} Ziele sind seit mehr als 72h ohne Update.`,
      cta: { label: "Zu GrowPro", route: "growpro" },
    });
  }

  if (growProUpcomingGoals.value.length) {
    slides.push({
      key: "growpro-upcoming",
      tone: "info",
      status: "ok",
      title: "Naechste GrowPro Updates",
      message: "Die naechsten Update-Fristen fuer deine Ziele.",
      items: growProUpcomingGoals.value.map((entry) => ({
        key: entry.goal.id,
        title: entry.goal.title,
        date: formatFullDate(entry.deadline),
      })),
      cta: { label: "Zu GrowPro", route: "growpro" },
    });
  }

  return slides;
});

const activeSlide = computed(() => dashboardSlides.value[slideIndex.value] || null);
const hasPrevSlide = computed(() => slideIndex.value > 0);
const hasNextSlide = computed(() => slideIndex.value < dashboardSlides.value.length - 1);

function getDefaultTaskForm() {
  return {
    title: "",
    projectId: "",
    dueDate: "",
    priority: "MEDIUM",
  };
}

function goTo(name) {
  router.push({ name });
}

async function loadExamples() {
  if (!me.value?.id) return;
  try {
    const { data } = await api.get("examples/", { params: { profile: me.value.id } });
    examples.value = data.filter((item) => item.profile === me.value.id);
  } catch (err) {
    console.error("Beispiele konnten nicht geladen werden", err);
    examples.value = [];
  }
}

async function loadProjects() {
  try {
    const { data } = await api.get("projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    projects.value = [];
  }
}

async function loadProjectSummary() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("projects/summary/");
    projectSummary.value = {
      total: data.total || 0,
      archived: data.archived || 0,
      active: data.active || 0,
      done: data.done || 0,
      by_status: data.by_status || {},
    };
  } catch (err) {
    projectSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {} };
  }
}

async function loadOverdueTasks() {
  if (!isTeam.value) {
    overdueTasks.value = [];
    return;
  }
  try {
    const { data } = await api.get("tasks/overdue/");
    overdueTasks.value = data || [];
  } catch (err) {
    console.error("Ueberfaellige Tasks konnten nicht geladen werden", err);
    overdueTasks.value = [];
  }
}

function isTaskOverdue(task) {
  if (!task?.due_date) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(task.due_date) < today;
}

function sortActiveTasks(list) {
  return [...list].sort((a, b) => {
    const aDue = a.due_date ? new Date(a.due_date).getTime() : Number.POSITIVE_INFINITY;
    const bDue = b.due_date ? new Date(b.due_date).getTime() : Number.POSITIVE_INFINITY;
    if (aDue !== bDue) return aDue - bDue;
    const aCreated = new Date(a.created_at || 0).getTime();
    const bCreated = new Date(b.created_at || 0).getTime();
    return bCreated - aCreated;
  });
}

async function loadActiveTasks() {
  if (!isTeam.value) {
    activeTasks.value = [];
    activeTasksTotal.value = 0;
    return;
  }
  try {
    const { data } = await api.get("tasks/", {
      params: {
        status: "OPEN,IN_PROGRESS,REVIEW",
        include_done: 0,
        include_archived: 0,
        ordering: "due_date",
        page_size: 100,
      },
    });
    const results = Array.isArray(data) ? data : data.results || [];
    const filtered = results.filter((task) => !isTaskOverdue(task));
    const sorted = sortActiveTasks(filtered);
    activeTasks.value = sorted;
    activeTasksTotal.value = sorted.length;
  } catch (err) {
    console.error("Aktive Tasks konnten nicht geladen werden", err);
    activeTasks.value = [];
    activeTasksTotal.value = 0;
  }
}

async function loadReviewTasks() {
  if (!isTeam.value) {
    reviewTasks.value = [];
    return;
  }
  if (loadingReviewTasks.value) return;
  loadingReviewTasks.value = true;
  try {
    const { data } = await api.get("tasks/", {
      params: {
        status: "REVIEW",
        include_done: 0,
        include_archived: 0,
        ordering: "due_date",
        page_size: 100,
      },
    });
    reviewTasks.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Review-Tasks konnten nicht geladen werden", err);
    reviewTasks.value = [];
  } finally {
    loadingReviewTasks.value = false;
  }
}

async function loadUserTasks() {
  if (isTeam.value) {
    userTasks.value = [];
    return;
  }
  if (loadingUserTasks.value) return;
  loadingUserTasks.value = true;
  try {
    const { data } = await api.get("tasks/", {
      params: {
        status: "OPEN,IN_PROGRESS,REVIEW",
        include_done: 0,
        include_archived: 0,
        ordering: "due_date",
        page_size: 50,
      },
    });
    const results = Array.isArray(data) ? data : data.results || [];
    userTasks.value = results;
  } catch (err) {
    console.error("User-Tasks konnten nicht geladen werden", err);
    userTasks.value = [];
  } finally {
    loadingUserTasks.value = false;
  }
}

async function loadTeamRequests() {
  if (!isTeam.value) {
    teamRequests.value = [];
    return;
  }
  loadingRequests.value = true;
  try {
    const { data } = await api.get("requests/team-open/");
    teamRequests.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Anfragen konnten nicht geladen werden", err);
    teamRequests.value = [];
  } finally {
    loadingRequests.value = false;
  }
}

async function loadGrowProGoals() {
  try {
    const { data } = await api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } });
    const payload = data || {};
    growProGoals.value = Array.isArray(payload) ? payload : payload.results || [];
  } catch (err) {
    console.error("GrowPro konnte nicht geladen werden", err);
    growProGoals.value = [];
  }
}

async function loadProjectOptions() {
  if (loadingProjectOptions.value) return;
  loadingProjectOptions.value = true;
  try {
    const { data } = await api.get("projects/", {
      params: { include_archived: 0, include_done: 0, page_size: 100 },
    });
    const results = Array.isArray(data) ? data : data.results || [];
    projectOptions.value = results.map((project) => ({
      id: project.id,
      title: project.title,
    }));
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
    projectOptions.value = [];
  } finally {
    loadingProjectOptions.value = false;
  }
}

function openTaskModal() {
  taskForm.value = getDefaultTaskForm();
  taskModalOpen.value = true;
  loadProjectOptions();
}

function closeTaskModal() {
  if (taskSaving.value) return;
  taskModalOpen.value = false;
}

async function submitTask() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  const payload = {
    title: taskForm.value.title.trim(),
    status: "OPEN",
    priority: taskForm.value.priority,
    task_type: "EXTERNAL",
    due_date: taskForm.value.dueDate || null,
  };
  if (taskForm.value.projectId) {
    payload.project = Number(taskForm.value.projectId);
  }
  try {
    await api.post("tasks/", payload);
    showToast("Task erstellt", "success");
    taskModalOpen.value = false;
    await Promise.all([loadOverdueTasks(), loadActiveTasks(), loadReviewTasks(), loadProjectSummary()]);
  } catch (err) {
    console.error("Task konnte nicht erstellt werden", err);
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

function closeUserModal() {
  if (userSaving.value) return;
  userModalOpen.value = false;
}

async function submitUserInvite() {
  if (!userForm.value.email.trim()) {
    showToast("E-Mail erforderlich", "error");
    return;
  }
  userSaving.value = true;
  inviteLink.value = "";
  try {
    const { data } = await api.post("invite/", {
      email: userForm.value.email.trim(),
      name: userForm.value.name.trim(),
    });
    inviteLink.value = data?.invite_link || "";
    showToast("Einladung gesendet", "success");
  } catch (err) {
    console.error("Einladung fehlgeschlagen", err);
    showToast("Einladung fehlgeschlagen", "error");
  } finally {
    userSaving.value = false;
  }
}

function copyInviteLink() {
  if (!inviteLink.value) return;
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(inviteLink.value);
    showToast("Link kopiert", "success");
    return;
  }
  window.prompt("Link kopieren:", inviteLink.value);
}

async function respondRequest(id, action) {
  if (!isTeam.value) return;
  const endpoint = action === "accept" ? "accept" : "decline";
  try {
    await api.post(`requests/${id}/${endpoint}/`);
    await loadTeamRequests();
    showToast(action === "accept" ? "Request angenommen" : "Request abgelehnt", "success");
  } catch (err) {
    console.error("Request-Aktion fehlgeschlagen", err);
    showToast("Aktion fehlgeschlagen", "error");
  }
}

async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);
    if (isTeam.value) {
      await Promise.all([
        loadProjectSummary(),
        loadOverdueTasks(),
        loadActiveTasks(),
        loadReviewTasks(),
        loadTeamRequests(),
        loadGrowProGoals(),

      ]);
    } else {
      await Promise.all([loadExamples(), loadProjects(), loadUserTasks(), loadGrowProGoals()]);
    }
  } finally {
    loading.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await Promise.all([
      loadProjectSummary(),
      loadOverdueTasks(),
      loadActiveTasks(),
      loadReviewTasks(),
      loadTeamRequests(),
      loadGrowProGoals(),

    ]);
  } else {
    await Promise.all([loadExamples(), loadProjects(), loadUserTasks(), loadGrowProGoals()]);
  }
});

watch(
  () => dashboardSlides.value.length,
  (length) => {
    if (!length) {
      slideIndex.value = 0;
      return;
    }
    if (slideIndex.value > length - 1) {
      slideIndex.value = length - 1;
    }
  },
  { immediate: true }
);

function normalizeId(value) {
  return String(value ?? "");
}

function isTaskAssignedToMe(task) {
  if (!me.value?.id) return false;
  return (task.assignees || []).some((assignee) => normalizeId(assignee.id) === normalizeId(me.value.id));
}

function isTaskStakeholderForMe(task) {
  if (!me.value?.id) return false;
  return (task.stakeholders || []).some((person) => normalizeId(person.id) === normalizeId(me.value.id));
}

function growProUpdateDeadline(goal) {
  if (!goal) return null;
  const base = goal.last_logged_at || goal.created_at;
  if (!base) return null;
  const baseDate = new Date(base);
  if (Number.isNaN(baseDate.getTime())) return null;
  return new Date(baseDate.getTime() + 72 * 60 * 60 * 1000);
}

function isGrowProStale(goal) {
  if (!goal || ["DONE", "ARCHIVED"].includes(goal.status)) return false;
  const deadline = growProUpdateDeadline(goal);
  if (!deadline) return false;
  return Date.now() > deadline.getTime();
}

function taskUrgency(task) {
  if (!task?.due_date) return "ok";
  const now = Date.now();
  const due = new Date(task.due_date).getTime();
  if (due < now) return "overdue";
  const threeDays = 3 * 24 * 60 * 60 * 1000;
  if (due - now <= threeDays) return "soon";
  return "ok";
}

function reviewUrgency(task) {
  if (!task?.due_date) return "ok";
  const now = Date.now();
  const due = new Date(task.due_date).getTime();
  if (due < now) return "overdue";
  const twoDays = 2 * 24 * 60 * 60 * 1000;
  if (due - now <= twoDays) return "soon";
  return "ok";
}

function prevSlide() {
  if (hasPrevSlide.value) slideIndex.value -= 1;
}

function nextSlide() {
  if (hasNextSlide.value) slideIndex.value += 1;
}

function goToSlide(index) {
  if (index < 0 || index > dashboardSlides.value.length - 1) return;
  slideIndex.value = index;
}

function handleSlideCta(slide) {
  if (!slide?.cta?.route) return;
  goTo(slide.cta.route);
}

function statusLabel(status) {
  return statusLabelMap[status] || status;
}

function requestTypeLabel(type) {
  return requestTypeLabels[type] || type;
}

function formatTaskDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function formatFullDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }).format(new Date(value));
}

function taskProjectLabel(task) {
  return task.project_title || `Projekt #${task.project}`;
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: none;
}
.actions-bar {
  display: flex;
  justify-content: flex-end;
  width: 100%;
}
.spotlight {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.spotlight-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}
.spotlight .eyebrow {
  margin: 0 0 6px;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: var(--brand);
}
.spotlight .small {
  margin: 0;
  font-size: 13px;
}
.spotlight-nav {
  display: flex;
  gap: 8px;
}
.spotlight-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.slide-dots {
  display: flex;
  gap: 8px;
  align-items: center;
}
.dot {
  width: 10px;
  height: 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: transparent;
  cursor: pointer;
  padding: 0;
}
.dot.active {
  background: var(--brand);
  border-color: var(--brand);
}
.nav-btn {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  border-radius: 10px;
  padding: 6px 10px;
  font-weight: 700;
  cursor: pointer;
}
.nav-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.slide {
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 16px;
  background: rgba(99, 102, 241, 0.12);
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
}
.slide::before {
  content: "";
  display: block;
  height: 4px;
  width: 100%;
  border-radius: 999px;
  background: #22c55e;
}
.slide[data-status="soon"]::before {
  background: #f59e0b;
}
.slide[data-status="overdue"]::before {
  background: #ef4444;
}
.slide.warning {
  border-color: rgba(220, 38, 38, 0.6);
  background: rgba(248, 113, 113, 0.1);
}
.slide-top {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}
.warn-icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  border: 1px solid rgba(220, 38, 38, 0.6);
  color: #b91c1c;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
}
.slide-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.slide-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1px dashed var(--border);
  background: rgba(15, 23, 42, 0.04);
}
.slide-actions {
  display: flex;
  justify-content: flex-end;
}
.overview {
  width: 100%;
}
.overview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.overview-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
  margin-top: 12px;
}
.stat {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  background: var(--card);
}
.stat .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.stat strong {
  font-size: 22px;
}
.overview-strip {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.strip-item {
  border: 1px solid var(--border);
  background: rgba(99, 102, 241, 0.12);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 13px;
  display: inline-flex;
  gap: 6px;
  align-items: center;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 20px;
  align-items: start;
  width: 100%;
}
.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.section-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.task-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
  margin-top: 10px;
}
.list {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.flex-1 {
  flex: 1;
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
.request-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.project-link {
  color: inherit;
  text-decoration: none;
}
.project-link:hover {
  text-decoration: underline;
}
.check {
  font-size: 16px;
  width: 18px;
  text-align: center;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 50;
}
.modal {
  width: min(560px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 24px;
  padding: 24px;
  background: var(--card);
  box-shadow: 0 35px 80px rgba(15, 23, 42, 0.35);
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.input {
  border: 1px solid rgba(148, 163, 184, 0.5);
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--card);
  font-size: 14px;
  width: 100%;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.invite-link {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.invite-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.invite-row .input {
  flex: 1 1 280px;
}
:global(.dark) .dashboard .stat {
  background: rgba(15, 23, 42, 0.6);
}
:global(.dark) .dashboard .slide {
  background: rgba(15, 23, 42, 0.45);
  border-color: var(--border);
}
:global(.dark) .dashboard .slide.warning {
  background: rgba(127, 29, 29, 0.22);
  border-color: rgba(248, 113, 113, 0.5);
}
:global(.dark) .dashboard .slide-list li {
  background: rgba(15, 23, 42, 0.55);
}
:global(.dark) .dashboard .modal {
  background: var(--card);
  box-shadow: 0 35px 80px rgba(0, 0, 0, 0.55);
}
:global(.dark) .dashboard .input {
  background: rgba(15, 23, 42, 0.6);
  border-color: var(--border);
  color: var(--text);
}
@media (max-width: 760px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .row {
    flex-direction: column;
    align-items: flex-start;
  }
  .request-actions {
    justify-content: flex-start;
  }
  .slide-actions .btn {
    width: 100%;
    justify-content: center;
  }
  .spotlight-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
