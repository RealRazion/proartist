<template>
  <div class="project-detail">
    <header class="card hero">
      <button class="btn ghost tiny" type="button" @click="goBack">ZurÃ¼ck zu Projekten</button>
      <div class="hero-main">
        <p class="eyebrow">Projekt</p>
        <h1>{{ project?.title || "Projekt" }}</h1>
        <div class="hero-meta">
          <span class="status" :data-status="project?.status">{{ statusLabel(project?.status) }}</span>
          <span v-if="project?.is_archived" class="badge archived">Archiviert</span>
          <span v-if="project?.created_at" class="muted">Erstellt {{ formatDate(project.created_at) }}</span>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="refreshAll" :disabled="loadingProject">
          {{ loadingProject ? "Lade..." : "Aktualisieren" }}
        </button>
        <button v-if="isTeam" class="btn" type="button" @click="editMode = !editMode">
          {{ editMode ? "Bearbeitung schließen" : "Bearbeiten" }}
        </button>
      </div>
      <p class="muted small hero-note">
        Statusänderungen auf Aufgaben werden für Review-Aufgaben automatisch als geprüft oder nicht geprüft verwaltet.
      </p>
    </header>

    <section v-if="projectError" class="card info">
      <h2>Projekt nicht gefunden</h2>
      <p class="muted">{{ projectError }}</p>
      <button class="btn" type="button" @click="goBack">Zur Projektliste</button>
    </section>

    <section v-else-if="loadingProject" class="card loading-card">
      <div class="skeleton-line"></div>
      <div class="skeleton-line short"></div>
      <div class="skeleton-block"></div>
    </section>

    <section v-else class="content-grid">
      <div class="card overview">
        <div class="section-head">
          <div>
            <h2>Ãœberblick</h2>
            <p class="muted small">Status, Team und Kontext auf einen Blick.</p>
          </div>
          <div class="stats">
            <div>
              <span class="label">Tasks</span>
              <strong>{{ taskTotals.total }}</strong>
            </div>
            <div>
              <span class="label">Songs</span>
              <strong>{{ songsPagination.count || songs.length }}</strong>
            </div>
          </div>
        </div>
        <p class="muted description">{{ project?.description || "Keine Beschreibung hinterlegt." }}</p>
        <dl class="facts">
          <div>
            <dt>Status</dt>
            <dd>{{ statusLabel(project?.status) }}</dd>
          </div>
          <div>
            <dt>Erstellt</dt>
            <dd>{{ project?.created_at ? formatDate(project.created_at) : "-" }}</dd>
          </div>
          <div>
            <dt>Archiv</dt>
            <dd>{{ project?.is_archived ? "Archiviert" : "Aktiv" }}</dd>
          </div>
        </dl>
        <div class="people">
          <h3>Teilnehmer</h3>
          <div class="chips" v-if="project?.participants?.length">
            <span class="chip" v-for="person in project.participants" :key="`p-${person.id}`">
              {{ person.name || person.username }}
            </span>
          </div>
          <p v-else class="muted small">Noch keine Teilnehmer.</p>
        </div>
        <div class="people">
          <h3>Team</h3>
          <div class="chips" v-if="project?.owners?.length">
            <span class="chip" v-for="person in project.owners" :key="`o-${person.id}`">
              {{ person.name || person.username }}
            </span>
          </div>
          <p v-else class="muted small">Noch kein Team zugeordnet.</p>
        </div>
        <div class="people">
          <h3>Projektrechte</h3>
          <p class="muted small">{{ participantTaskAccessLabels[project?.participant_task_access] || "Nur Team bearbeitet Tasks" }}</p>
        </div>
      </div>

      <div class="card overview">
        <div class="section-head">
          <div>
            <h2>Project Health</h2>
            <p class="muted small">Offene Punkte, Reviews und naechste Deadline kompakt.</p>
          </div>
          <span class="muted small" v-if="loadingHealth">Aktualisiere...</span>
        </div>
        <div class="stats health-stats">
          <div>
            <span class="label">Offen</span>
            <strong>{{ projectHealth.open_tasks }}</strong>
          </div>
          <div>
            <span class="label">Review</span>
            <strong>{{ projectHealth.review_tasks }}</strong>
          </div>
          <div>
            <span class="label">Ueberfaellig</span>
            <strong>{{ projectHealth.overdue_tasks }}</strong>
          </div>
        </div>
        <p v-if="projectHealth.next_due_task" class="muted small">
          Naechste Frist: {{ projectHealth.next_due_task.title }} am {{ formatDate(projectHealth.next_due_task.due_date) }}
        </p>
        <p v-else class="muted small">Keine naechste Deadline vorhanden.</p>
      </div>

      <form v-if="isTeam && editMode" class="card edit" @submit.prevent="saveProject">
        <div class="section-head">
          <h2>Projekt bearbeiten</h2>
          <button class="btn ghost tiny" type="button" @click="resetProjectDraft" :disabled="savingProject">
            ZurÃ¼cksetzen
          </button>
        </div>
        <label>
          Titel
          <input class="input" v-model.trim="projectDraft.title" placeholder="Projektname" />
        </label>
        <label>
          Beschreibung
          <textarea class="input textarea" v-model.trim="projectDraft.description" placeholder="Projektbeschreibung"></textarea>
        </label>
        <label>
          Status
          <select class="input" v-model="projectDraft.status">
            <option v-for="opt in projectStatusOptions" :key="opt" :value="opt">
              {{ projectStatusLabels[opt] }}
            </option>
          </select>
        </label>
        <label>
          Projektrechte
          <select class="input" v-model="projectDraft.participant_task_access">
            <option v-for="opt in participantTaskAccessOptions" :key="opt" :value="opt">
              {{ participantTaskAccessLabels[opt] }}
            </option>
          </select>
        </label>
        <label>
          Teilnehmer
          <select class="input" v-model="projectDraft.participant_ids" multiple size="7">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.name }}</option>
          </select>
          <small class="hint muted">Mehrfachauswahl mit Strg/Command mÃ¶glich.</small>
        </label>
        <label>
          Verantwortliche Teammitglieder
          <select class="input" v-model="projectDraft.owner_ids" multiple size="6">
            <option v-for="profile in teamProfiles" :key="`team-${profile.id}`" :value="profile.id">
              {{ profile.name }}
            </option>
          </select>
        </label>
        <div class="danger-zone">
          <p class="muted">Projekt archivieren oder endgÃ¼ltig lÃ¶schen.</p>
          <div class="danger-actions">
            <button class="btn ghost danger" type="button" @click="archiveProject" :disabled="savingProject">
              Archivieren
            </button>
            <button class="btn danger" type="button" @click="deleteProject" :disabled="savingProject">
              LÃ¶schen
            </button>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn ghost" type="button" @click="resetProjectDraft" :disabled="savingProject">
            Ã„nderungen verwerfen
          </button>
          <button class="btn" type="submit" :disabled="savingProject || !hasProjectChanges">
            {{ savingProject ? "Speichere..." : "Speichern" }}
          </button>
        </div>
      </form>
    </section>

    <section class="card tasks">
      <div class="section-head">
        <div>
          <h2>Projekt-Tasks</h2>
          <p class="muted small" v-if="taskPagination.count">
            {{ tasks.length }} von {{ taskPagination.count }} geladen
          </p>
        </div>
        <div class="section-actions">
          <button class="btn ghost" type="button" @click="exportCalendar" :disabled="calendarExporting">
            {{ calendarExporting ? "Exportiere..." : "Kalender Export" }}
          </button>
          <button class="btn ghost" type="button" @click="loadTasks" :disabled="loadingTasks">
            {{ loadingTasks ? "Lade..." : "Aktualisieren" }}
          </button>
          <button v-if="canManageTasks" class="btn" type="button" @click="openTaskModal">Task hinzufÃ¼gen</button>
        </div>
      </div>

      <div v-if="!canViewTasks" class="muted">
        Fuer dieses Projekt hast du keinen Task-Zugriff.
      </div>
      <template v-else>
        <div class="task-filters">
          <input class="input" v-model.trim="taskSearch" placeholder="Tasks durchsuchen" />
          <select class="input" v-model="taskStatusFilter">
            <option value="ALL">Alle Status</option>
            <option v-for="opt in taskStatusOptions" :key="opt" :value="opt">{{ taskStatusLabels[opt] }}</option>
          </select>
          <label class="toggle">
            <input type="checkbox" v-model="showCompletedTasks" />
            Abgeschlossene
          </label>
          <label class="toggle">
            <input type="checkbox" v-model="showArchivedTasks" />
            Archivierte
          </label>
        </div>

        <div v-if="loadingTasks" class="skeleton-list">
          <div class="skeleton-card" v-for="n in 3" :key="`tsk-${n}`"></div>
        </div>
        <ul v-else-if="tasks.length" class="task-list">
          <li
            v-for="task in tasks"
            :key="task.id"
            class="task-card"
            :data-task-id="task.id"
            :class="{ highlight: task.id === highlightedTaskId }"
          >
            <div class="task-main">
              <div>
                <strong>{{ task.title }}</strong>
                <p class="muted small">
                  {{ task.due_date ? `FÃ¤llig ${formatDate(task.due_date)}` : "Kein Termin" }}
                  - {{ taskPriorityLabels[task.priority] }}
                  <span v-if="task.recurrence_pattern && task.recurrence_pattern !== 'NONE'" class="review-pill">
                    {{ recurrenceLabel(task) }}
                  </span>
                  <span
                    v-if="task.review_status"
                    class="review-pill"
                    :data-review="task.review_status"
                  >
                    {{ reviewStatusLabels[task.review_status] || task.review_status }}
                  </span>
                </p>
                <p class="muted small">Verantwortlich: {{ formatAssignees(task) }}</p>
                <p v-if="task.created_by || task.updated_by" class="muted tiny">
                  Erstellt: {{ formatUser(task.created_by) }}
                  <span v-if="task.updated_by">Â· Update: {{ formatUser(task.updated_by) }}</span>
                </p>
              </div>
              <div class="task-actions">
                <select class="input tiny" v-model="task.status" @change="onTaskStatusChange(task, $event)" :disabled="!canManageTasks">
                  <option v-for="opt in taskStatusOptions" :key="opt" :value="opt">
                    {{ taskStatusLabels[opt] }}
                  </option>
                </select>
                <button v-if="canManageTasks" class="btn ghost tiny" type="button" @click="startEditTask(task)">Bearbeiten</button>
                <button v-if="canManageTasks" class="btn ghost danger tiny" type="button" @click="archiveTask(task)">Archivieren</button>
              </div>
            </div>
            <div v-if="canManageTasks && canResolveTaskReview(task)" class="task-review-actions">
              <button
                class="btn tiny"
                type="button"
                @click="setTaskReviewStatus(task, true)"
                :disabled="reviewActionSaving[task.id]"
              >
                {{ reviewActionSaving[task.id] ? "Speichere..." : "Als geprüft markieren" }}
              </button>
              <button
                v-if="task.status === 'REVIEW'"
                class="btn ghost tiny danger"
                type="button"
                @click="setTaskReviewStatus(task, false)"
                :disabled="reviewActionSaving[task.id]"
              >
                Als nicht geprüft markieren
              </button>
            </div>
          </li>
        </ul>
        <p v-else class="muted empty">Keine Tasks fÃ¼r dieses Projekt.</p>
        <button v-if="hasMoreTasks" class="btn ghost tiny" type="button" @click="loadMoreTasks" :disabled="loadingMoreTasks">
          {{ loadingMoreTasks ? "Lade..." : "Mehr laden" }}
        </button>
      </template>
    </section>

    <section class="card attachments">
      <AttachmentPanel
        entity-type="project"
        :entity-id="projectId"
        title="DateianhÃ¤nge"
        description="Teile Briefings, Referenzen oder Ergebnisse."
      />
    </section>

    <section class="card songs">
      <div class="section-head">
        <div>
          <h2>VerknÃ¼pfte Songs</h2>
          <p class="muted small" v-if="songsPagination.count">
            {{ songs.length }} von {{ songsPagination.count }} geladen
          </p>
        </div>
        <button class="btn ghost" type="button" @click="loadSongs" :disabled="loadingSongs">
          {{ loadingSongs ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
      <div v-if="loadingSongs" class="skeleton-list">
        <div class="skeleton-card" v-for="n in 2" :key="`song-${n}`"></div>
      </div>
      <ul v-else-if="songs.length" class="song-list">
        <li v-for="song in songs" :key="song.id">
          <div>
            <strong>{{ song.title }}</strong>
            <p class="muted small">{{ songStatusLabels[song.status] || song.status }}</p>
          </div>
          <span class="muted small">{{ formatDate(song.created_at) }}</span>
        </li>
      </ul>
      <p v-else class="muted empty">Noch keine Songs mit diesem Projekt verknÃ¼pft.</p>
      <button v-if="hasMoreSongs" class="btn ghost tiny" type="button" @click="loadMoreSongs" :disabled="loadingMoreSongs">
        {{ loadingMoreSongs ? "Lade..." : "Mehr laden" }}
      </button>
    </section>

    <section v-if="isTeam" class="card activity">
      <div class="section-head">
        <div>
          <h2>Letzte AktivitÃ¤ten</h2>
          <p class="muted small">Projektbezogene Events und Updates.</p>
        </div>
        <button class="btn ghost" type="button" @click="loadActivity" :disabled="loadingActivity">
          {{ loadingActivity ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
      <ul v-if="activities.length" class="activity-list">
        <li v-for="item in activities" :key="item.id">
          <span class="badge">{{ activityIcon(item.event_type) }}</span>
          <div class="activity-body">
            <strong>{{ item.title }}</strong>
            <p class="muted small">{{ item.description || item.event_type }}</p>
          </div>
          <span class="muted small">{{ formatDateTime(item.created_at) }}</span>
        </li>
      </ul>
      <p v-else class="muted empty">Keine AktivitÃ¤ten vorhanden.</p>
    </section>

    <div v-if="taskModalVisible" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card wide task-modal">
        <div class="modal-head">
          <h3>{{ taskModalMode === "create" ? "Task hinzufÃ¼gen" : "Task bearbeiten" }}</h3>
          <button class="btn ghost tiny" type="button" @click="closeTaskModal" :disabled="taskSaving">
            SchlieÃŸen
          </button>
        </div>
        <form class="form form-grid" @submit.prevent="submitTaskForm">
          <label>
            Titel
            <input class="input" v-model.trim="taskForm.title" placeholder="Tasktitel" required />
          </label>
          <label>
            Status
            <select class="input" v-model="taskForm.status">
              <option v-for="opt in taskStatusOptions" :key="opt" :value="opt">{{ taskStatusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            PrioritÃ¤t
            <select class="input" v-model="taskForm.priority">
              <option v-for="opt in taskPriorityOptions" :key="opt" :value="opt">{{ taskPriorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Task-Typ
            <select class="input" v-model="taskForm.task_type">
              <option v-for="opt in taskTypeOptions" :key="opt" :value="opt">{{ taskTypeLabels[opt] }}</option>
            </select>
          </label>
          <label class="full">
            Verantwortliche (Team)
            <select class="input" v-model="taskForm.assignee_ids" multiple size="5">
              <option v-for="profile in teamProfiles" :key="`assignee-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
          </label>
          <label class="full">
            Betroffene Nutzer
            <select class="input" v-model="taskForm.stakeholder_ids" multiple size="5">
              <option v-for="profile in profiles" :key="`stake-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
          </label>
          <label>
            FÃ¤llig am
            <input class="input" type="date" v-model="taskForm.due_date" />
          </label>
          <label>
            Wiederholung
            <select class="input" v-model="taskForm.recurrence_pattern">
              <option v-for="opt in recurrenceOptions" :key="opt" :value="opt">{{ recurrenceLabels[opt] }}</option>
            </select>
          </label>
          <label v-if="taskForm.recurrence_pattern !== 'NONE'">
            Intervall
            <input class="input" type="number" min="1" step="1" v-model.number="taskForm.recurrence_interval" />
          </label>
          <div class="form-actions">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">
              {{ taskSaving ? "Speichere..." : "Speichern" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="reviewModalVisible" class="modal-backdrop" @click.self="cancelReviewDecision">
      <div class="modal card review-modal">
        <div class="modal-head">
          <h3>Review abgeschlossen?</h3>
          <button class="btn ghost tiny" type="button" @click="cancelReviewDecision">SchlieÃŸen</button>
        </div>
        <div class="modal-body">
          <div v-if="reviewTarget" class="review-summary">
            <strong>{{ reviewTarget.title }}</strong>
            <p class="muted small">
              {{ reviewTarget.project_title || project?.title || "Kein Projekt" }}
              <span class="dot">Â·</span>
              {{ reviewTarget.due_date ? formatDate(reviewTarget.due_date) : "Kein Termin" }}
            </p>
            <p class="muted small">Verantwortlich: {{ formatAssignees(reviewTarget) }}</p>
          </div>
          <p class="muted">
            Wurde der Task bereits geprüft? Bei "Nein" wird er als nicht geprüft markiert und
            dem Team-Mitglied mit der geringsten Auslastung zugewiesen.
          </p>
        </div>
        <div class="modal-actions">
          <button class="btn ghost" type="button" @click="cancelReviewDecision">Abbrechen</button>
          <button class="btn" type="button" @click="confirmReviewDecision(true)">Ja, geprüft</button>
          <button class="btn danger" type="button" @click="confirmReviewDecision(false)">Nein</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import AttachmentPanel from "../components/AttachmentPanel.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const route = useRoute();
const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const project = ref(null);
const projectHealth = ref({ open_tasks: 0, done_tasks: 0, review_tasks: 0, overdue_tasks: 0, due_soon_tasks: 0, next_due_task: null });
const projectDraft = ref(getDefaultProjectDraft());
const editMode = ref(true);
const loadingProject = ref(false);
const loadingHealth = ref(false);
const savingProject = ref(false);
const projectError = ref("");

const profiles = ref([]);
const loadingProfiles = ref(false);

const tasks = ref([]);
const taskPagination = ref({ next: null, previous: null, count: 0 });
const loadingTasks = ref(false);
const loadingMoreTasks = ref(false);
const taskStatusFilter = ref("ALL");
const taskSearch = ref("");
const showArchivedTasks = ref(false);
const showCompletedTasks = ref(true);
let taskSearchDebounce = null;
const highlightedTaskId = ref(null);
let highlightTimer = null;

const songs = ref([]);
const songsPagination = ref({ next: null, previous: null, count: 0 });
const loadingSongs = ref(false);
const loadingMoreSongs = ref(false);

const activities = ref([]);
const loadingActivity = ref(false);

const taskModalVisible = ref(false);
const taskModalMode = ref("create");
const taskSaving = ref(false);
const editingTaskId = ref(null);
const taskForm = ref(getDefaultTaskForm());
const reviewModalVisible = ref(false);
const reviewTarget = ref(null);
const reviewPreviousStatus = ref(null);
const statusSnapshot = ref({});
const reviewActionSaving = ref({});
const calendarExporting = ref(false);

const projectStatusOptions = ["PLANNED", "IN_PROGRESS", "ON_HOLD", "DONE"];
const projectStatusLabels = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  ON_HOLD: "Pausiert",
  DONE: "Abgeschlossen",
};
const participantTaskAccessOptions = ["NONE", "COMMENT", "EDIT"];
const participantTaskAccessLabels = {
  NONE: "Nur Team bearbeitet Tasks",
  COMMENT: "Teilnehmer duerfen kommentieren",
  EDIT: "Teilnehmer duerfen Tasks bearbeiten",
};

const taskStatusOptions = ["OPEN", "IN_PROGRESS", "REVIEW", "DONE"];
const taskStatusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Abgeschlossen",
};
const reviewStatusLabels = {
  REVIEWED: "Geprüft",
  NOT_REVIEWED: "Nicht geprüft",
};

const taskPriorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const taskPriorityLabels = {
  LOW: "Niedrig",
  MEDIUM: "Mittel",
  HIGH: "Hoch",
  CRITICAL: "Kritisch",
};

const taskTypeOptions = ["INTERNAL", "EXTERNAL"];
const taskTypeLabels = {
  INTERNAL: "Intern",
  EXTERNAL: "Extern",
};
const recurrenceOptions = ["NONE", "DAILY", "WEEKLY", "MONTHLY"];
const recurrenceLabels = {
  NONE: "Keine",
  DAILY: "Taeglich",
  WEEKLY: "Woechentlich",
  MONTHLY: "Monatlich",
};

const songStatusLabels = {
  ACTIVE: "Aktiv",
  INACTIVE: "Inaktiv",
  ARCHIVED: "Archiviert",
};

const projectId = computed(() => Number(route.params.projectId || 0));
const teamProfiles = computed(() =>
  profiles.value.filter((profile) => (profile.roles || []).some((role) => role.key === "TEAM"))
);
const isProjectParticipant = computed(() =>
  Boolean(project.value?.participants?.some((person) => String(person.id) === String(me.value?.id)))
);
const isProjectOwner = computed(() =>
  Boolean(project.value?.owners?.some((person) => String(person.id) === String(me.value?.id)))
);
const canViewTasks = computed(() => isTeam.value || isProjectParticipant.value || isProjectOwner.value);
const canManageTasks = computed(() =>
  isTeam.value || isProjectOwner.value || (isProjectParticipant.value && project.value?.participant_task_access === "EDIT")
);
const hasMoreTasks = computed(() => Boolean(taskPagination.value.next));
const hasMoreSongs = computed(() => Boolean(songsPagination.value.next));

const taskTotals = computed(() => {
  const summary = { total: taskPagination.value.count || tasks.value.length, byStatus: {} };
  taskStatusOptions.forEach((key) => {
    summary.byStatus[key] = tasks.value.filter((task) => task.status === key).length;
  });
  return summary;
});

const hasProjectChanges = computed(() => {
  if (!project.value) return false;
  const draft = projectDraft.value;
  if (draft.title.trim() !== (project.value.title || "")) return true;
  if ((draft.description || "").trim() !== (project.value.description || "")) return true;
  if (draft.status !== project.value.status) return true;
  if ((draft.participant_task_access || "NONE") !== (project.value.participant_task_access || "NONE")) return true;
  const participants = normalizeIds(draft.participant_ids);
  const owners = normalizeIds(draft.owner_ids);
  const currentParticipants = normalizeIds((project.value.participants || []).map((p) => p.id));
  const currentOwners = normalizeIds((project.value.owners || []).map((p) => p.id));
  return participants !== currentParticipants || owners !== currentOwners;
});

function getDefaultProjectDraft() {
  return {
    title: "",
    description: "",
    status: "PLANNED",
    participant_task_access: "NONE",
    participant_ids: [],
    owner_ids: [],
  };
}

function getDefaultTaskForm() {
  return {
    title: "",
    status: "OPEN",
    priority: "MEDIUM",
    task_type: "EXTERNAL",
    assignee_ids: [],
    stakeholder_ids: [],
    due_date: "",
    recurrence_pattern: "NONE",
    recurrence_interval: 1,
  };
}

function normalizeIds(list) {
  return [...new Set((list || []).map((id) => Number(id)))]
    .filter((id) => !Number.isNaN(id))
    .sort((a, b) => a - b)
    .join(",");
}

function statusLabel(status) {
  return projectStatusLabels[status] || status || "-";
}

function recurrenceLabel(task) {
  if (!task?.recurrence_pattern || task.recurrence_pattern === "NONE") return "Keine";
  const base = recurrenceLabels[task.recurrence_pattern] || task.recurrence_pattern;
  const interval = Number(task.recurrence_interval || 1);
  return interval > 1 ? `${base} x${interval}` : base;
}

function applyProjectDraft(data) {
  projectDraft.value = {
    title: data?.title || "",
    description: data?.description || "",
    status: data?.status || "PLANNED",
    participant_task_access: data?.participant_task_access || "NONE",
    participant_ids: data?.participants?.map((p) => p.id) || [],
    owner_ids: data?.owners?.map((p) => p.id) || [],
  };
}

function resetProjectDraft() {
  applyProjectDraft(project.value);
}

async function loadProject() {
  projectError.value = "";
  if (!projectId.value) {
    projectError.value = "UngÃ¼ltige Projekt-ID.";
    project.value = null;
    return;
  }
  loadingProject.value = true;
  try {
    const { data } = await api.get(`projects/${projectId.value}/`);
    project.value = data;
    applyProjectDraft(data);
  } catch (err) {
    projectError.value = "Das Projekt konnte nicht geladen werden.";
    project.value = null;
  } finally {
    loadingProject.value = false;
  }
}

async function loadProjectHealth() {
  if (!projectId.value) return;
  loadingHealth.value = true;
  try {
    const { data } = await api.get(`projects/${projectId.value}/health/`);
    projectHealth.value = {
      open_tasks: data.open_tasks || 0,
      done_tasks: data.done_tasks || 0,
      review_tasks: data.review_tasks || 0,
      overdue_tasks: data.overdue_tasks || 0,
      due_soon_tasks: data.due_soon_tasks || 0,
      next_due_task: data.next_due_task || null,
    };
  } catch (err) {
    console.error("Project Health konnte nicht geladen werden", err);
  } finally {
    loadingHealth.value = false;
  }
}

async function exportCalendar() {
  if (!projectId.value || calendarExporting.value) return;
  calendarExporting.value = true;
  try {
    const { data } = await api.get("tasks/calendar-export/", {
      params: { project: projectId.value, include_archived: showArchivedTasks.value ? 1 : 0, include_done: 1 },
      responseType: "blob",
    });
    const blob = new Blob([data], { type: "text/calendar;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `project-${projectId.value}.ics`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Kalender Export fehlgeschlagen", err);
    showToast("Kalender Export fehlgeschlagen", "error");
  } finally {
    calendarExporting.value = false;
  }
}

async function saveProject() {
  if (!project.value || !hasProjectChanges.value) return;
  savingProject.value = true;
  const payload = {
    title: projectDraft.value.title.trim(),
    description: projectDraft.value.description?.trim() || "",
    status: projectDraft.value.status,
    participant_task_access: projectDraft.value.participant_task_access,
    participant_ids: projectDraft.value.participant_ids,
    owner_ids: projectDraft.value.owner_ids,
  };
  try {
    const { data } = await api.patch(`projects/${projectId.value}/`, payload);
    project.value = data;
    applyProjectDraft(data);
    showToast("Projekt aktualisiert", "success");
  } catch (err) {
    console.error("Projekt konnte nicht gespeichert werden", err);
    showToast("Projekt konnte nicht gespeichert werden", "error");
  } finally {
    savingProject.value = false;
  }
}

async function archiveProject() {
  if (!project.value) return;
  if (!confirm(`Projekt "${project.value.title}" archivieren?`)) return;
  savingProject.value = true;
  try {
    const { data } = await api.post(`projects/${projectId.value}/archive/`);
    project.value = data;
    applyProjectDraft(data);
    showToast("Projekt archiviert", "success");
  } catch (err) {
    console.error("Projekt konnte nicht archiviert werden", err);
    showToast("Projekt konnte nicht archiviert werden", "error");
  } finally {
    savingProject.value = false;
  }
}

async function deleteProject() {
  if (!project.value) return;
  if (!confirm(`Projekt "${project.value.title}" endgÃ¼ltig lÃ¶schen?`)) return;
  savingProject.value = true;
  try {
    try {
      await api.post(`projects/${projectId.value}/delete/`);
    } catch (err) {
      await api.delete(`projects/${projectId.value}/`);
    }
    showToast("Projekt gelÃ¶scht", "success");
    router.push({ name: "projects" });
  } catch (err) {
    console.error("Projekt konnte nicht gelÃ¶scht werden", err);
    showToast("Projekt konnte nicht gelÃ¶scht werden", "error");
  } finally {
    savingProject.value = false;
  }
}

async function loadProfiles() {
  if (!isTeam.value && !canManageTasks.value) return;
  if (loadingProfiles.value) return;
  loadingProfiles.value = true;
  try {
    const { data } = await api.get("profiles/");
    profiles.value = data.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
      username: profile.username,
      roles: profile.roles || [],
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    profiles.value = [];
  } finally {
    loadingProfiles.value = false;
  }
}

function buildTaskParams() {
  return {
    project: projectId.value,
    status: taskStatusFilter.value !== "ALL" ? taskStatusFilter.value : undefined,
    search: taskSearch.value.trim() || undefined,
    include_archived: showArchivedTasks.value ? 1 : 0,
    include_done: showCompletedTasks.value || taskStatusFilter.value === "DONE" ? 1 : 0,
    ordering: "-due_date",
    page_size: 20,
  };
}

async function loadTasks({ append = false, pageUrl = null } = {}) {
  if (!canViewTasks.value) return;
  const target = append ? loadingMoreTasks : loadingTasks;
  if (target.value) return;
  target.value = true;
  try {
    const params = pageUrl ? undefined : buildTaskParams();
    const url = pageUrl || "tasks/";
    const { data } = await api.get(url, { params });
    if (Array.isArray(data)) {
      tasks.value = append ? tasks.value.concat(data) : data;
      taskPagination.value = { next: null, previous: null, count: data.length };
    } else {
      const results = data.results || [];
      tasks.value = append ? tasks.value.concat(results) : results;
      taskPagination.value = {
        next: data.next,
        previous: data.previous,
        count: data.count ?? results.length,
      };
    }
    maybeHighlightFromQuery();
  } catch (err) {
    console.error("Tasks konnten nicht geladen werden", err);
    showToast("Tasks konnten nicht geladen werden", "error");
    if (!append) {
      tasks.value = [];
      taskPagination.value = { next: null, previous: null, count: 0 };
    }
  } finally {
    target.value = false;
  }
}

function syncStatusSnapshot(list) {
  const next = { ...statusSnapshot.value };
  list.forEach((task) => {
    next[task.id] = task.status;
  });
  statusSnapshot.value = next;
}

function maybeHighlightFromQuery() {
  const taskId = Number(route.query.taskId || 0);
  if (!taskId) return;
  if (!tasks.value.find((task) => task.id === taskId)) return;
  highlightTask(taskId);
}

function highlightTask(taskId) {
  highlightedTaskId.value = taskId;
  nextTick(() => {
    const el = document.querySelector(`[data-task-id="${taskId}"]`);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "center" });
      el.classList.remove("pulse");
      void el.offsetWidth;
      el.classList.add("pulse");
    }
  });
  if (highlightTimer) clearTimeout(highlightTimer);
  highlightTimer = setTimeout(() => {
    highlightedTaskId.value = null;
  }, 3000);
}

function loadMoreTasks() {
  if (!taskPagination.value.next) return;
  loadTasks({ append: true, pageUrl: taskPagination.value.next });
}

function openReviewModal(task, previousStatus) {
  reviewTarget.value = task;
  reviewPreviousStatus.value = previousStatus;
  reviewModalVisible.value = true;
}

function closeReviewModal() {
  reviewTarget.value = null;
  reviewPreviousStatus.value = null;
  reviewModalVisible.value = false;
}

function canResolveTaskReview(task) {
  return Boolean(task && (task.status === "REVIEW" || (task.status === "DONE" && task.review_status === "NOT_REVIEWED")));
}

async function applyTaskStatusChange(task, newStatus, reviewStatus, previousStatus) {
  const fallbackStatus = previousStatus ?? statusSnapshot.value[task.id] ?? task.status;
  const payload = { status: newStatus };
  if (reviewStatus) {
    payload.review_status = reviewStatus;
  }
  try {
    await api.patch(`tasks/${task.id}/`, payload);
    statusSnapshot.value = { ...statusSnapshot.value, [task.id]: newStatus };
    task.status = newStatus;
    if (reviewStatus) {
      task.review_status = reviewStatus;
    } else if (newStatus !== "DONE") {
      task.review_status = null;
    }
    if (newStatus === "DONE") {
      showCompletedTasks.value = true;
    }
    await loadTasks();
    showToast("Task-Status aktualisiert", "success");
    return true;
  } catch (err) {
    console.error("Task-Status konnte nicht aktualisiert werden", err);
    task.status = fallbackStatus;
    showToast("Task-Status konnte nicht aktualisiert werden", "error");
    await loadTasks();
    return false;
  }
}

async function onTaskStatusChange(task, event) {
  const nextStatus = event?.target?.value || task.status;
  const previousStatus = statusSnapshot.value[task.id] || task.status;
  if (nextStatus === "DONE" && previousStatus !== "DONE") {
    openReviewModal(task, previousStatus);
    return;
  }
  await applyTaskStatusChange(task, nextStatus, null, previousStatus);
}

async function confirmReviewDecision(reviewed) {
  if (!reviewTarget.value) return;
  const task = reviewTarget.value;
  const reviewStatus = reviewed ? "REVIEWED" : "NOT_REVIEWED";
  const success = await applyTaskStatusChange(task, "DONE", reviewStatus, reviewPreviousStatus.value);
  if (success) closeReviewModal();
}

async function setTaskReviewStatus(task, reviewed) {
  if (!task?.id || reviewActionSaving.value[task.id]) return;
  reviewActionSaving.value = { ...reviewActionSaving.value, [task.id]: true };
  try {
    const previousStatus = statusSnapshot.value[task.id] ?? task.status;
    await applyTaskStatusChange(task, "DONE", reviewed ? "REVIEWED" : "NOT_REVIEWED", previousStatus);
  } finally {
    reviewActionSaving.value = { ...reviewActionSaving.value, [task.id]: false };
  }
}

async function cancelReviewDecision() {
  if (reviewTarget.value && reviewPreviousStatus.value) {
    reviewTarget.value.status = reviewPreviousStatus.value;
  }
  closeReviewModal();
  await loadTasks();
}

async function archiveTask(task) {
  if (!confirm(`Task "${task.title}" archivieren?`)) return;
  try {
    await api.post(`tasks/${task.id}/archive/`);
    showToast("Task archiviert", "success");
    loadTasks();
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
    showToast("Task konnte nicht archiviert werden", "error");
  }
}

function openTaskModal() {
  if (!canManageTasks.value) return;
  taskModalMode.value = "create";
  editingTaskId.value = null;
  taskForm.value = { ...getDefaultTaskForm() };
  taskModalVisible.value = true;
}

function closeTaskModal() {
  if (taskSaving.value) return;
  taskModalVisible.value = false;
}

function startEditTask(task) {
  if (!canManageTasks.value) return;
  taskModalMode.value = "edit";
  editingTaskId.value = task.id;
  taskForm.value = {
    title: task.title,
    status: task.status,
    priority: task.priority,
    task_type: task.task_type || "EXTERNAL",
    assignee_ids: task.assignees?.map((p) => p.id) || [],
    stakeholder_ids: task.stakeholders?.map((p) => p.id) || [],
    due_date: task.due_date || "",
    recurrence_pattern: task.recurrence_pattern || "NONE",
    recurrence_interval: task.recurrence_interval || 1,
  };
  taskModalVisible.value = true;
}

async function submitTaskForm() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  const payload = {
    title: taskForm.value.title.trim(),
    status: taskForm.value.status,
    priority: taskForm.value.priority,
    task_type: taskForm.value.task_type,
    assignee_ids: taskForm.value.assignee_ids,
    stakeholder_ids: taskForm.value.stakeholder_ids,
    project: projectId.value,
    due_date: taskForm.value.due_date || null,
    recurrence_pattern: taskForm.value.recurrence_pattern,
    recurrence_interval: taskForm.value.recurrence_pattern === "NONE" ? 1 : Number(taskForm.value.recurrence_interval || 1),
  };
  try {
    if (taskModalMode.value === "edit" && editingTaskId.value) {
      await api.patch(`tasks/${editingTaskId.value}/`, payload);
      showToast("Task aktualisiert", "success");
    } else {
      await api.post("tasks/", payload);
      showToast("Task angelegt", "success");
    }
    await loadTasks();
    taskModalVisible.value = false;
  } catch (err) {
    console.error("Task konnte nicht gespeichert werden", err);
    showToast("Task konnte nicht gespeichert werden", "error");
  } finally {
    taskSaving.value = false;
  }
}

async function loadSongs({ append = false, pageUrl = null } = {}) {
  const target = append ? loadingMoreSongs : loadingSongs;
  if (target.value) return;
  target.value = true;
  try {
    const params = pageUrl
      ? undefined
      : { project: projectId.value, page_size: 20, ordering: "-created_at" };
    const url = pageUrl || "songs/";
    const { data } = await api.get(url, { params });
    if (Array.isArray(data)) {
      songs.value = append ? songs.value.concat(data) : data;
      songsPagination.value = { next: null, previous: null, count: data.length };
    } else {
      const results = data.results || [];
      songs.value = append ? songs.value.concat(results) : results;
      songsPagination.value = {
        next: data.next,
        previous: data.previous,
        count: data.count ?? results.length,
      };
    }
  } catch (err) {
    console.error("Songs konnten nicht geladen werden", err);
    if (!append) {
      songs.value = [];
      songsPagination.value = { next: null, previous: null, count: 0 };
    }
  } finally {
    target.value = false;
  }
}

function loadMoreSongs() {
  if (!songsPagination.value.next) return;
  loadSongs({ append: true, pageUrl: songsPagination.value.next });
}

async function loadActivity() {
  if (!isTeam.value) return;
  loadingActivity.value = true;
  try {
    const { data } = await api.get("activity-feed/", { params: { limit: 50 } });
    activities.value = (data || []).filter((item) => item.project?.id === projectId.value);
  } catch (err) {
    activities.value = [];
  } finally {
    loadingActivity.value = false;
  }
}

function activityIcon(type) {
  if (!type) return "*";
  if (type.startsWith("task")) return "T";
  if (type.startsWith("project")) return "P";
  if (type.startsWith("song")) return "S";
  return "*";
}

function formatAssignees(task) {
  if (!task.assignees?.length) return "Niemand";
  return task.assignees.map((p) => p.name || p.username).join(", ");
}

function formatUser(user) {
  if (!user) return "-";
  return user.name || user.username || "-";
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function goBack() {
  router.push({ name: "projects" });
}

async function refreshAll() {
  await loadProject();
  await loadProjectHealth();
  if (canViewTasks.value) {
    await loadTasks();
  }
  if (isTeam.value) {
    await loadActivity();
  }
  if (canManageTasks.value || isTeam.value) {
    await loadProfiles();
  }
  await loadSongs();
}

watch(
  () => projectId.value,
  () => {
    tasks.value = [];
    songs.value = [];
    activities.value = [];
    refreshAll();
  },
  { immediate: true }
);

watch(
  () => [taskStatusFilter.value, showArchivedTasks.value, showCompletedTasks.value],
  () => {
    if (!canViewTasks.value) return;
    loadTasks();
  }
);

watch(
  () => route.query.taskId,
  () => {
    if (!tasks.value.length) return;
    maybeHighlightFromQuery();
  }
);

watch(
  () => taskSearch.value,
  () => {
    if (!canViewTasks.value) return;
    if (taskSearchDebounce) clearTimeout(taskSearchDebounce);
    taskSearchDebounce = setTimeout(() => loadTasks(), 300);
  }
);

watch(
  () => tasks.value,
  (list) => {
    syncStatusSnapshot(list);
  },
  { immediate: true }
);

onMounted(async () => {
  await fetchProfile();
  await refreshAll();
});

onBeforeUnmount(() => {
  if (highlightTimer) clearTimeout(highlightTimer);
});
</script>

<style scoped>
.project-detail {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.card {
  border-radius: 22px;
  border: 1px solid var(--border);
  background: var(--card);
  box-shadow: 0 25px 60px rgba(15, 23, 42, 0.08);
  padding: 22px;
}
.hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 16px;
}
.hero-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.hero-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.eyebrow {
  margin: 0;
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--muted);
}
.status {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: rgba(59, 130, 246, 0.15);
  color: var(--status-in-progress);
}
.status[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.16);
  color: var(--status-open);
}
.status[data-status="DONE"] {
  background: rgba(16, 185, 129, 0.16);
  color: var(--status-done);
}
.status[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: var(--status-overdue);
}
.badge.archived {
  background: rgba(148, 163, 184, 0.2);
  color: var(--text);
  padding: 4px 10px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
}
.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.section-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.stats {
  display: flex;
  gap: 12px;
}
.stats .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.description {
  margin: 10px 0 16px;
}
.facts {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
  margin: 0 0 16px;
}
.facts dt {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.facts dd {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}
.people {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 12px;
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.5);
  padding: 2px 10px;
  font-size: 12px;
}
.edit label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.edit .hint {
  font-size: 12px;
  font-weight: 400;
}
.input,
.textarea {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--card);
  color: var(--text);
  font-size: 14px;
  width: 100%;
}
.textarea {
  min-height: 120px;
  resize: vertical;
}
.danger-zone {
  border: 1px dashed rgba(220, 38, 38, 0.4);
  border-radius: 14px;
  padding: 12px;
  margin-top: 10px;
  background: rgba(248, 113, 113, 0.08);
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.danger-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}
.tasks .task-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin: 12px 0;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
}
.task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.task-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  background: var(--card);
  display: flex;
  flex-direction: column;
}
.task-card.highlight {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.25);
  background: rgba(249, 115, 22, 0.08);
}
.task-card.pulse {
  animation: taskPulse 1.2s ease-in-out 2;
}
.task-main {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.task-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}
.task-review-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.review-pill {
  display: inline-flex;
  align-items: center;
  margin-left: 8px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(15, 23, 42, 0.12);
  color: #1f2937;
}
.review-pill[data-review="REVIEWED"] {
  background: rgba(16, 185, 129, 0.16);
  color: #059669;
}
.review-pill[data-review="NOT_REVIEWED"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.review-summary {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  margin-bottom: 12px;
  background: rgba(15, 23, 42, 0.04);
}
.review-summary .dot {
  margin: 0 6px;
}
.input.tiny {
  padding: 6px 8px;
  font-size: 12px;
}
.song-list,
.activity-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.song-list li,
.activity-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.activity-list li {
  align-items: flex-start;
}
.badge {
  border-radius: 999px;
  padding: 4px 10px;
  background: rgba(148, 163, 184, 0.2);
  font-size: 12px;
  font-weight: 600;
}
.activity-body {
  flex: 1;
}
.loading-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.skeleton-line {
  height: 14px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
.skeleton-line.short {
  width: 45%;
}
.skeleton-block {
  height: 120px;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
.skeleton-list {
  display: grid;
  gap: 12px;
}
.skeleton-card {
  height: 90px;
  border-radius: 16px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.4s linear infinite;
}
.empty {
  text-align: center;
  padding: 12px 0;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 999;
}
.modal {
  max-width: 560px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 26px;
  padding: 24px;
  background: var(--card);
  border: 1px solid var(--border);
  box-shadow: 0 40px 80px rgba(15, 23, 42, 0.35);
}
.modal.wide {
  max-width: 920px;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 14px;
}
.form-grid .full {
  grid-column: 1 / -1;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
@keyframes taskPulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.02);
  }
  100% {
    transform: scale(1);
  }
}
@media (max-width: 720px) {
  .hero {
    align-items: flex-start;
  }
  .content-grid {
    grid-template-columns: 1fr;
  }
  .stats {
    width: 100%;
    justify-content: space-between;
  }
  .task-main {
    flex-direction: column;
    align-items: flex-start;
  }
  .modal {
    padding: 18px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
