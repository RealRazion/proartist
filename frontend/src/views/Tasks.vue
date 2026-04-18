<template>
  <div class="tasks">
    <header class="card header">
      <div>
        <h1>Tasks</h1>
        <p class="muted">Verteile Aufgaben, lade Dateien hoch und halte Kommentare fest.</p>
        <p class="muted small">Wähle "Erledigt" und bestätige dann, ob die Aufgabe geprüft wurde.</p>
      </div>
      <div class="board-actions">
        <button class="btn ghost" type="button" @click="exportCalendar" :disabled="calendarExporting">
          {{ calendarExporting ? "Exportiere..." : "Kalender Export" }}
        </button>
        <button class="btn ghost" type="button" @click="refreshTasks" :disabled="loadingTasks">
          {{ loadingTasks ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Nur Team-Mitglieder können Aufgaben verwalten. Bitte wende dich an das Team.</p>
    </section>

    <section v-else class="workspace" :class="{ 'has-detail': Boolean(activeTask) }">
      <div class="board card">
        <div class="board-head">
          <div>
            <h2>Task Board</h2>
            <p class="muted small">Filter und neue Aufgaben per Dialog.</p>
          </div>
          <div class="board-actions">
            <button class="btn ghost" type="button" @click="openFilterModal">Filter</button>
            <button class="btn" type="button" @click="openTaskModal" :disabled="taskSaving">Task erstellen</button>
          </div>
        </div>
        <p class="muted board-hint">Archivierte Tasks blendest du über die Filter wieder ein.</p>
        <div class="board-type-chips">
          <button
            v-for="type in boardTypeOptions"
            :key="type"
            class="chip"
            :class="{ active: boardTypeFilter === type }"
            type="button"
            @click="setBoardType(type)"
          >
            {{ boardTypeLabels[type] }}
          </button>
        </div>
        <div class="kpi-row" v-if="taskSummary.total">
          <div class="kpi">
            <span>Gesamt</span>
            <strong>{{ taskSummary.total }}</strong>
          </div>
          <div class="kpi">
            <span>Aktiv</span>
            <strong>{{ taskSummary.active }}</strong>
          </div>
          <div class="kpi warning">
            <span>Review</span>
            <strong>{{ taskSummary.by_status?.REVIEW || 0 }}</strong>
          </div>
          <div class="kpi success">
            <span>Done</span>
            <strong>{{ taskSummary.done }}</strong>
          </div>
        </div>
        <div v-if="taskSummary.total" class="progress-list">
          <div v-for="segment in statusProgress" :key="segment.key" class="progress-item">
            <div class="progress-head">
              <span>
                <span class="dot" :data-status="segment.key"></span>
                {{ segment.label }}
              </span>
              <strong>{{ segment.count }}</strong>
            </div>
            <div class="progress-track" :data-status="segment.key">
              <span class="progress-fill" :style="{ width: `${segment.percent}%` }"></span>
            </div>
          </div>
        </div>
        <div class="columns">
          <div v-for="column in boardColumns" :key="column.key">
            <h3>{{ column.label }}</h3>
            <div v-if="loadingTasks" class="skeleton-column">
              <div class="skeleton-card" v-for="n in 2" :key="`tsk-${column.key}-${n}`"></div>
            </div>
            <template v-else>
              <ul>
                <li
                  v-for="task in column.items"
                  :key="task.id"
                  class="task-card"
                  :class="{ overdue: dueState(task) === 'overdue', soon: dueState(task) === 'soon' }"
                  :data-status="task.status"
                >
                  <div class="title-row">
                    <div>
                      <div class="title">{{ task.title }}</div>
                      <div class="pill-row">
                        <span class="priority" :data-priority="task.priority">
                          {{ priorityLabels[task.priority] }}
                        </span>
                        <span class="task-type" :data-type="task.task_type">
                          {{ taskTypeLabels[task.task_type] || task.task_type }}
                        </span>
                        <span v-if="task.recurrence_pattern && task.recurrence_pattern !== 'NONE'" class="task-type recurrence">
                          {{ recurrenceLabel(task) }}
                        </span>
                        <span
                          v-if="task.review_status"
                          class="review-chip"
                          :data-review="task.review_status"
                        >
                          {{ reviewStatusLabels[task.review_status] || task.review_status }}
                        </span>
                      </div>
                    </div>
                    <div class="card-buttons">
                      <button class="btn ghost tiny" type="button" @click="openTask(task)">
                        Details
                      </button>
                      <button class="btn ghost tiny" type="button" @click="startEditTask(task)">
                        Bearbeiten
                      </button>
                    </div>
                  </div>
                  <p class="muted">
                    Projekt: {{ task.project ? projectMap[task.project]?.title || "-" : "Kein Projekt" }}
                  </p>
                  <p class="muted small-text">
                    Verantwortlich: {{ formatAssignees(task) }}
                  </p>
                  <p class="muted small-text">
                    Betroffene: {{ formatStakeholders(task) }}
                  </p>
                  <p class="due" :class="dueState(task)">
                    {{ task.due_date ? `Fällig ${formatDueDate(task.due_date)}` : "Kein Termin" }}
                  </p>
                  <div class="actions">
                    <select class="input" v-model="task.status" @change="onStatusChange(task, $event)">
                      <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
                    </select>
                    <button class="btn ghost danger tiny" type="button" @click="archiveTask(task)">
                      Archivieren
                    </button>
                  </div>
                  <div v-if="canResolveReview(task)" class="review-actions">
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
              <p v-if="!column.items.length" class="muted empty">Keine Tasks</p>
            </template>
          </div>
        </div>
        <div ref="taskSentinel" class="sentinel" v-if="hasMoreTasks"></div>
        <p v-if="loadingMoreTasks" class="muted loading-more">Lade weitere Tasks...</p>
      </div>
      <section v-if="finishedTaskSummary.visible" class="card finished-summary">
        <div class="finished-summary-body">
          <div>
            <h3>Fertige Tasks</h3>
            <p class="muted">Es gibt {{ finishedTaskSummary.count }} erledigte Tasks. Sie können fertig erledigte Aufgaben separat anzeigen und bei Bedarf zurücksetzen.</p>
          </div>
          <button class="btn" type="button" @click="openFinishedTasks">
            Fertige Tasks ansehen
          </button>
        </div>
      </section>
      <section v-if="activeTask" class="card detail-panel">
        <header class="detail-head">
          <div>
            <p class="eyebrow">Ausgewählter Task</p>
            <h2>{{ activeTask.title }}</h2>
            <div class="detail-pills">
              <span class="status-chip" :data-status="activeTask.status">{{ statusLabels[activeTask.status] }}</span>
              <span class="priority-chip" :data-priority="activeTask.priority">{{ priorityLabels[activeTask.priority] }}</span>
              <span class="type-chip" :data-type="activeTask.task_type">{{ taskTypeLabels[activeTask.task_type] }}</span>
              <span v-if="activeTask.recurrence_pattern && activeTask.recurrence_pattern !== 'NONE'" class="type-chip recurrence">
                {{ recurrenceLabel(activeTask) }}
              </span>
              <span
                v-if="activeTask.review_status"
                class="review-chip"
                :data-review="activeTask.review_status"
              >
                {{ reviewStatusLabels[activeTask.review_status] || activeTask.review_status }}
              </span>
              <span v-if="activeTask.is_archived" class="archive-chip">Archiviert</span>
            </div>
            <p class="muted">
              Projekt: {{ activeTask.project ? projectMap[activeTask.project]?.title || "-" : "Kein Projekt" }}
            </p>
          </div>
          <div class="detail-actions">
            <button class="btn ghost tiny" type="button" @click="startEditTask(activeTask)">Bearbeiten</button>
            <button
              class="btn ghost tiny"
              type="button"
              @click="archiveTask(activeTask)"
              :disabled="activeTask.is_archived"
            >
              Archivieren
            </button>
            <button class="btn ghost tiny" type="button" @click="activeTaskId = null">Schließen</button>
          </div>
        </header>
        <div class="detail-grid">
          <section class="info-panel">
            <h3>Übersicht</h3>
            <dl class="info-grid">
              <div>
                <dt>Status</dt>
                <dd>{{ statusLabels[activeTask.status] }}</dd>
              </div>
              <div>
                <dt>Review</dt>
                <dd>{{ reviewStatusLabels[activeTask.review_status] || activeTask.review_status || "-" }}</dd>
              </div>
              <div>
                <dt>Fällig</dt>
                <dd>{{ activeTask.due_date ? formatDueDate(activeTask.due_date) : "Kein Termin" }}</dd>
              </div>
              <div>
                <dt>Priorität</dt>
                <dd>{{ priorityLabels[activeTask.priority] }}</dd>
              </div>
              <div>
                <dt>Wiederholung</dt>
                <dd>{{ recurrenceLabel(activeTask) }}</dd>
              </div>
              <div>
                <dt>Erstellt</dt>
                <dd>{{ formatDate(activeTask.created_at) }}</dd>
              </div>
              <div>
                <dt>Erstellt von</dt>
                <dd>{{ formatUser(activeTask.created_by) }}</dd>
              </div>
              <div>
                <dt>Letzte Änderung</dt>
                <dd>{{ formatUser(activeTask.updated_by) }}</dd>
              </div>
            </dl>
            <div v-if="canResolveReview(activeTask)" class="review-actions">
              <button
                class="btn tiny"
                type="button"
                @click="setTaskReviewStatus(activeTask, true)"
                :disabled="reviewActionSaving[activeTask.id]"
              >
                {{ reviewActionSaving[activeTask.id] ? "Speichere..." : "Als geprüft markieren" }}
              </button>
              <button
                v-if="activeTask.status === 'REVIEW'"
                class="btn ghost tiny danger"
                type="button"
                @click="setTaskReviewStatus(activeTask, false)"
                :disabled="reviewActionSaving[activeTask.id]"
              >
                Als nicht geprüft markieren
              </button>
            </div>
            <div class="chip-section">
              <span class="label">Verantwortlich</span>
              <div class="chip-list" v-if="activeTask.assignees?.length">
                <span class="chip" v-for="person in activeTask.assignees" :key="person.id">
                  {{ person.name || person.username }}
                </span>
              </div>
              <p v-else class="muted small">Noch niemand zugewiesen</p>
            </div>
            <div class="chip-section">
              <span class="label">Betroffene</span>
              <div class="chip-list" v-if="activeTask.stakeholders?.length">
                <span class="chip" v-for="person in activeTask.stakeholders" :key="`stake-${person.id}`">
                  {{ person.name || person.username }}
                </span>
              </div>
              <p v-else class="muted small">Keine Stakeholder hinterlegt</p>
            </div>
          </section>

          <AttachmentPanel
            entity-type="task"
            :entity-id="activeTask.id"
            title="Dateianhänge"
            description="Teile Briefings, Referenzen oder Ergebnisse."
          />

          <section class="comments-panel">
            <h3>Kommentare</h3>
            <p class="muted">Nutze @-Mentions, um Teammitglieder zu informieren.</p>
            <div class="comment-list" v-if="taskComments[activeTask.id]?.length">
              <article v-for="comment in taskComments[activeTask.id]" :key="comment.id">
                <header>
                  <strong>{{ comment.author?.name || comment.author?.username }}</strong>
                  <span class="muted">{{ formatDate(comment.created_at) }}</span>
                </header>
                <p>{{ comment.body }}</p>
                <div v-if="comment.mention_profiles?.length" class="mentions">
                  <span v-for="mention in comment.mention_profiles" :key="mention.id">@{{ mention.name || mention.username }}</span>
                </div>
              </article>
            </div>
            <p v-else class="muted">Noch keine Kommentare.</p>
            <form class="comment-form" @submit.prevent="addComment(activeTask.id)">
              <textarea class="input textarea" v-model.trim="taskCommentDraft(activeTask.id).body" placeholder="Kommentar"></textarea>
              <label>
                Mentions
                <select class="input" v-model="taskCommentDraft(activeTask.id).mentions" multiple size="4">
                  <option v-for="profile in teamProfiles" :key="profile.id" :value="profile.id">
                    {{ profile.name }}
                  </option>
                </select>
              </label>
              <button class="btn tiny" type="submit" :disabled="commentLoading[activeTask.id]">
                {{ commentLoading[activeTask.id] ? "Speichere..." : "Kommentieren" }}
              </button>
            </form>
          </section>
        </div>
      </section>
    </section>

    <FinishedTasksCard :finishedCount="finishedTasksCount" :finishedTasks="finishedTasksList" v-if="isTeam" />

    <div v-if="showFilterModal" class="modal-backdrop" @click.self="closeFilterModal">
      <div class="modal card wide">
        <div class="modal-head">
          <h3>Filter</h3>
          <button class="btn ghost tiny" type="button" @click="closeFilterModal">Schließen</button>
        </div>
        <form class="form" @submit.prevent="applyFilters">
          <label>
            Suche
            <input class="input" v-model.trim="searchTasks" placeholder="Titel oder Projekt" />
          </label>
          <label>
            Projekt
            <select class="input" v-model="filterProject">
              <option value="ALL">Alle</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Status
            <select class="input" v-model="filterStatus">
              <option value="ALL">Alle</option>
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Priorität
            <select class="input" v-model="priorityFilter">
              <option value="ALL">Alle</option>
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Task-Typ
            <select class="input" v-model="taskTypeFilter">
              <option value="ALL">Alle</option>
              <option v-for="opt in taskTypeOptions" :key="opt" :value="opt">
                {{ taskTypeLabels[opt] }}
              </option>
            </select>
          </label>
          <label>
            Sortierung
            <select class="input" v-model="sortOrder">
              <option v-for="opt in sortOptions" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
            </select>
          </label>
          <div class="due-chips">
            <button
              v-for="option in dueFilterOptions"
              :key="option.key"
              type="button"
              class="chip"
              :class="{ active: dueFilter === option.key }"
              @click="dueFilter = option.key"
            >
              {{ option.label }}
            </button>
          </div>
          <div class="visibility">
            <label class="toggle">
              <input type="checkbox" v-model="showCompleted" />
              Abgeschlossene anzeigen
            </label>
            <label class="toggle">
              <input type="checkbox" v-model="showArchived" />
              Archivierte anzeigen
            </label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="resetFilters">Zurücksetzen</button>
            <button class="btn" type="submit">Anwenden</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="taskModalVisible" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card wide task-modal">
        <div class="modal-head">
          <h3>{{ taskModalMode === "create" ? "Neue Aufgabe" : "Task bearbeiten" }}</h3>
          <button class="btn ghost tiny" type="button" @click="closeTaskModal" :disabled="taskSaving">Schließen</button>
        </div>
        <form class="form form-grid" @submit.prevent="submitTaskForm">
          <label>
            Titel
            <input class="input" v-model.trim="taskForm.title" placeholder="z. B. Mix finalisieren" required />
          </label>
          <label>
            Projekt (optional)
            <select class="input" v-model="taskForm.project">
              <option value="">Kein Projekt</option>
              <option v-for="project in projects" :key="project.id" :value="project.id">
                {{ project.title }}
              </option>
            </select>
          </label>
          <label>
            Task-Typ
            <select class="input" v-model="taskForm.task_type">
              <option v-for="opt in taskTypeOptions" :key="opt" :value="opt">
                {{ taskTypeLabels[opt] }}
              </option>
            </select>
          </label>
          <label>
            Status
            <select class="input" v-model="taskForm.status">
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Priorität
            <select class="input" v-model="taskForm.priority">
              <option v-for="opt in priorityOptions" :key="opt" :value="opt">{{ priorityLabels[opt] }}</option>
            </select>
          </label>
          <label class="full">
            Verantwortliche (Team)
            <select class="input" v-model="taskForm.assignee_ids" multiple size="6">
              <option v-for="profile in teamProfiles" :key="`assignee-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Mehrfachauswahl mit Strg/Command möglich.</small>
          </label>
          <label class="full">
            Betroffene Nutzer
            <select class="input" v-model="taskForm.stakeholder_ids" multiple size="6">
              <option v-for="profile in profiles" :key="`stake-${profile.id}`" :value="profile.id">
                {{ profile.name }}
              </option>
            </select>
            <small class="hint muted">Mehrfachauswahl mit Strg/Command möglich.</small>
          </label>
          <label>
            Fällig am
            <input class="input" type="date" v-model="taskForm.due_date" />
          </label>
          <label>
            Wiederholung
            <select class="input" v-model="taskForm.recurrence_pattern">
              <option v-for="opt in recurrenceOptions" :key="opt" :value="opt">
                {{ recurrenceLabels[opt] }}
              </option>
            </select>
          </label>
          <label v-if="taskForm.recurrence_pattern !== 'NONE'">
            Intervall
            <input class="input" type="number" min="1" step="1" v-model.number="taskForm.recurrence_interval" />
          </label>
          <div v-if="taskModalMode === 'edit'" class="danger-zone full">
            <p class="muted">Task archivieren oder komplett löschen.</p>
            <div class="danger-buttons">
              <button class="btn ghost danger" type="button" @click="archiveCurrentTask" :disabled="taskSaving">
                Archivieren
              </button>
              <button class="btn danger" type="button" @click="deleteCurrentTask" :disabled="taskSaving">
                Löschen
              </button>
            </div>
          </div>
          <div class="modal-actions full">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">
              {{
                taskSaving
                  ? "Speichere..."
                  : taskModalMode === "create"
                    ? "Task anlegen"
                    : "Speichern"
              }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="reviewModalVisible" class="modal-backdrop" @click.self="cancelReviewDecision">
      <div class="modal card review-modal">
        <div class="modal-head">
          <h3>Review abgeschlossen?</h3>
          <button class="btn ghost tiny" type="button" @click="cancelReviewDecision">Schließen</button>
        </div>
        <div class="modal-body">
          <div v-if="reviewTarget" class="review-summary">
            <strong>{{ reviewTarget.title }}</strong>
            <p class="muted small">
              {{ reviewTarget.project_title || "Kein Projekt" }}
              <span class="dot">·</span>
              {{ reviewTarget.due_date ? formatDueDate(reviewTarget.due_date) : "Kein Termin" }}
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
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import AttachmentPanel from "../components/AttachmentPanel.vue";
import FinishedTasksCard from "../components/FinishedTasksCard.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useRealtimeUpdates } from "../composables/useRealtimeUpdates";

const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();
const { connect: connectRealtime } = useRealtimeUpdates(handleRealtimeEvent);
const route = useRoute();
const router = useRouter();

const projects = ref([]);
const tasks = ref([]);
const projectMap = computed(() =>
  projects.value.reduce((acc, project) => {
    acc[project.id] = project;
    return acc;
  }, {})
);

const loadingTasks = ref(false);
const loadingMoreTasks = ref(false);
const loadingProjects = ref(false);
const showFilterModal = ref(false);
const showArchived = ref(false);
const showCompleted = ref(false);
const taskSummary = ref({
  total: 0,
  archived: 0,
  active: 0,
  done: 0,
  by_status: {},
  by_type: {},
});
const taskPagination = ref({ next: null, previous: null, count: 0 });
const taskSentinel = ref(null);
const hasMoreTasks = computed(() => Boolean(taskPagination.value.next));

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

function getDefaultTaskForm() {
  return {
    title: "",
    project: "",
    status: "OPEN",
    priority: "MEDIUM",
    assignee_ids: [],
    stakeholder_ids: [],
    due_date: "",
    task_type: "EXTERNAL",
    recurrence_pattern: "NONE",
    recurrence_interval: 1,
  };
}
const filterProject = ref("ALL");
const filterStatus = ref("ALL");
const priorityFilter = ref("ALL");
const dueFilter = ref("ALL");
const taskTypeFilter = ref("ALL");
const searchTasks = ref("");
const sortOrder = ref("-due_date");
const dueFilterOptions = [
  { key: "ALL", label: "Alle Termine" },
  { key: "overdue", label: "Überfällig" },
  { key: "soon", label: "In 48 Stunden" },
  { key: "scheduled", label: "Später" },
  { key: "none", label: "Ohne Termin" },
];
const sortOptions = [
  { value: "-due_date", label: "Fälligkeit absteigend" },
  { value: "due_date", label: "Fälligkeit aufsteigend" },
  { value: "-priority", label: "Priorität hoch zuerst" },
  { value: "priority", label: "Priorität niedrig zuerst" },
  { value: "-created_at", label: "Neueste zuerst" },
];

const statusOptions = ["OPEN", "IN_PROGRESS", "REVIEW", "DONE"];
const statusLabels = {
  OPEN: "Offen",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Fertig",
};
const reviewStatusLabels = {
  REVIEWED: "Geprüft",
  NOT_REVIEWED: "Nicht geprüft",
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
  WEEKLY: "WÖchentlich",
  MONTHLY: "Monatlich",
};
const boardTypeOptions = ["ALL", ...taskTypeOptions];
const boardTypeLabels = {
  ALL: "Alle Tasks",
  INTERNAL: "Intern",
  EXTERNAL: "Extern",
};
const priorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const priorityLabels = {
  LOW: "Niedrig",
  MEDIUM: "Mittel",
  HIGH: "Hoch",
  CRITICAL: "Kritisch",
};

function recurrenceLabel(task) {
  if (!task?.recurrence_pattern || task.recurrence_pattern === "NONE") return "Keine";
  const base = recurrenceLabels[task.recurrence_pattern] || task.recurrence_pattern;
  const interval = Number(task.recurrence_interval || 1);
  return interval > 1 ? `${base} x${interval}` : base;
}
const boardTypeFilter = ref("ALL");
const isFinishedView = computed(() => route.name === "tasks-finished");

function openFinishedTasks() {
  router.push({ name: "tasks-finished" });
}
function setBoardType(value) {
  boardTypeFilter.value = value;
  taskTypeFilter.value = value === "ALL" ? "ALL" : value;
  loadTasks();
}

function resetFilters() {
  searchTasks.value = "";
  filterProject.value = "ALL";
  filterStatus.value = "ALL";
  priorityFilter.value = "ALL";
  dueFilter.value = "ALL";
  taskTypeFilter.value = "ALL";
  showCompleted.value = false;
  showArchived.value = false;
  sortOrder.value = "-due_date";
  loadTasks();
}

const visibleTasks = computed(() => {
  if (boardTypeFilter.value === "ALL") {
    return tasks.value;
  }
  return tasks.value.filter((task) => task.task_type === boardTypeFilter.value);
});
const boardColumns = computed(() =>
  statusOptions.map((status) => ({
    key: status,
    label: statusLabels[status],
    items: visibleTasks.value
      .filter((task) => task.status === status)
      .slice()
      .sort(compareTasks),
  }))
);

const finishedTaskSummary = computed(() => ({
  count: taskSummary.value.done || 0,
  visible: !isFinishedView.value && (taskSummary.value.done || 0) > 0,
}));

const finishedTasksCount = computed(() => taskSummary.value.done || 0);

const finishedTasksList = computed(() =>
  tasks.value
    .filter(t => t.status === "DONE")
    .sort((a, b) => new Date(b.completed_at || 0) - new Date(a.completed_at || 0))
    .slice(0, 6)
);

const statusProgress = computed(() =>
  statusOptions.map((status) => {
    const count = taskSummary.value.by_status?.[status] || 0;
    const total = Math.max(taskSummary.value.total || 0, 1);
    return {
      key: status,
      label: statusLabels[status],
      count,
      percent: Math.max(0, Math.min(100, Math.round((count / total) * 100))),
    };
  })
);

function handleRealtimeEvent(event) {
  if (event?.entity !== "task" || !event.data) return;
  const action = event.action || "updated";
  const data = event.data;
  if (action === "deleted") {
    removeTaskById(data.id);
    scheduleTaskSummaryRefresh();
    return;
  }
  if (!taskMatchesFilters(data)) {
    removeTaskById(data.id);
    scheduleTaskSummaryRefresh();
    return;
  }
  upsertTask(data);
  scheduleTaskSummaryRefresh();
}

function upsertTask(taskData) {
  const idx = tasks.value.findIndex((task) => task.id === taskData.id);
  if (idx === -1) {
    tasks.value = [taskData, ...tasks.value];
  } else {
    const updated = [...tasks.value];
    updated.splice(idx, 1, taskData);
    tasks.value = updated;
  }
  if (activeTaskId.value === taskData.id) {
    activeTaskId.value = taskData.id;
  }
}

function syncStatusSnapshot(list) {
  const next = { ...statusSnapshot.value };
  list.forEach((task) => {
    next[task.id] = task.status;
  });
  statusSnapshot.value = next;
}

function removeTaskById(taskId) {
  const idx = tasks.value.findIndex((task) => task.id === taskId);
  if (idx === -1) return;
  const updated = [...tasks.value];
  updated.splice(idx, 1);
  tasks.value = updated;
  if (activeTaskId.value === taskId) {
    activeTaskId.value = null;
  }
}

function taskMatchesFilters(task) {
  if (!showArchived.value && task.is_archived) return false;
  if (!showCompleted.value && task.status === "DONE" && filterStatus.value !== "DONE") return false;
  if (filterProject.value !== "ALL" && String(task.project || "") !== String(filterProject.value)) return false;
  if (filterStatus.value !== "ALL" && task.status !== filterStatus.value) return false;
  if (priorityFilter.value !== "ALL" && task.priority !== priorityFilter.value) return false;
  if (taskTypeFilter.value !== "ALL" && task.task_type !== taskTypeFilter.value) return false;
  if (dueFilter.value !== "ALL") {
    if (dueFilter.value === "none" && task.due_date) return false;
    if (dueFilter.value !== "none" && dueState(task) !== dueFilter.value) return false;
  }
  const term = searchTasks.value.trim().toLowerCase();
  if (term) {
    const projectTitle = task.project_title || projectMap.value[task.project]?.title || "";
    const haystack = `${task.title || ""} ${projectTitle}`.toLowerCase();
    if (!haystack.includes(term)) return false;
  }
  return true;
}

let taskSummaryRefreshTimer = null;

function scheduleTaskSummaryRefresh() {
  if (taskSummaryRefreshTimer) return;
  taskSummaryRefreshTimer = setTimeout(async () => {
    taskSummaryRefreshTimer = null;
    await loadTaskSummary();
  }, 800);
}

const profiles = ref([]);
const teamProfiles = computed(() =>
  profiles.value.filter((profile) =>
    (profile.roles || []).some((role) => role.key === "TEAM")
  )
);
const activeTaskId = ref(null);
const activeTask = computed(() => tasks.value.find((task) => task.id === activeTaskId.value) || null);
const taskComments = ref({});
const commentLoading = ref({});
const commentDrafts = ref({});
let taskObserver;
let searchDebounce;

function setupTaskObserver() {
  if (taskObserver) taskObserver.disconnect();
  if (!taskSentinel.value) return;
  taskObserver = new IntersectionObserver((entries) => {
    if (entries[0].isIntersecting && taskPagination.value.next && !loadingMoreTasks.value) {
      loadTasks({ append: true, pageUrl: taskPagination.value.next });
    }
  });
  taskObserver.observe(taskSentinel.value);
}

function taskCommentDraft(taskId) {
  if (!commentDrafts.value[taskId]) {
    commentDrafts.value[taskId] = { body: "", mentions: [] };
  }
  return commentDrafts.value[taskId];
}

function normalizeListPayload(payload) {
  if (Array.isArray(payload)) {
    return { items: payload, next: null, previous: null, count: payload.length };
  }
  const data = payload || {};
  const items = Array.isArray(data.results) ? data.results : [];
  return {
    items,
    next: data.next || null,
    previous: data.previous || null,
    count: data.count ?? items.length,
  };
}

function mergeUniqueTasks(list) {
  const map = new Map();
  list.forEach((task) => {
    if (!task?.id) return;
    map.set(task.id, task);
  });
  return Array.from(map.values());
}

function compareDueDates(a, b) {
  if (!a && !b) return 0;
  if (!a) return 1;
  if (!b) return -1;
  return new Date(a) - new Date(b);
}

function priorityRank(priority) {
  return { CRITICAL: 0, HIGH: 1, MEDIUM: 2, LOW: 3 }[priority] ?? 4;
}

function compareTasks(a, b) {
  const dueComparison = compareDueDates(a?.due_date, b?.due_date);
  if (dueComparison !== 0) return dueComparison;
  const prioComparison = priorityRank(a?.priority) - priorityRank(b?.priority);
  if (prioComparison !== 0) return prioComparison;
  const aCreated = new Date(a?.created_at || 0).getTime();
  const bCreated = new Date(b?.created_at || 0).getTime();
  return bCreated - aCreated;
}

function formatDueDate(value) {
  if (!value) return "Kein Termin";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function formatStakeholders(task) {
  if (!task?.stakeholders?.length) return "Keine";
  return task.stakeholders.map((profile) => profile.name || profile.username).join(", ");
}

function formatAssignees(task) {
  if (!task?.assignees?.length) return "Nicht zugewiesen";
  return task.assignees.map((profile) => profile.name || profile.username).join(", ");
}

function formatUser(user) {
  if (!user) return "-";
  return user.name || user.username || "-";
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

function dueState(task) {
  if (!task.due_date) return "none";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(task.due_date);
  due.setHours(0, 0, 0, 0);
  const diff = (due - today) / (1000 * 60 * 60 * 24);
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "scheduled";
}

function buildDueParams() {
  const today = new Date();
  const params = {};
  const format = (date) => date.toISOString().slice(0, 10);
  if (dueFilter.value === "overdue") {
    params.due_before = format(today);
  } else if (dueFilter.value === "soon") {
    params.due_after = format(today);
    const future = new Date(today);
    future.setDate(future.getDate() + 2);
    params.due_before = format(future);
  } else if (dueFilter.value === "scheduled") {
    const future = new Date(today);
    future.setDate(future.getDate() + 2);
    params.due_after = format(future);
  } else if (dueFilter.value === "none") {
    params.due_state = "none";
  }
  return params;
}

async function loadProjects() {
  if (!isTeam.value) return;
  loadingProjects.value = true;
  try {
    const { data } = await api.get("projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Projekte für Tasks konnten nicht geladen werden", err);
    projects.value = [];
    showToast("Projekte konnten nicht geladen werden", "error");
  } finally {
    loadingProjects.value = false;
  }
}

function buildTaskParams() {
  return {
    include_archived: showArchived.value ? 1 : 0,
    include_done: showCompleted.value || filterStatus.value === "DONE" ? 1 : 0,
    project: filterProject.value !== "ALL" ? filterProject.value : undefined,
    status: filterStatus.value !== "ALL" ? filterStatus.value : undefined,
    priority: priorityFilter.value !== "ALL" ? priorityFilter.value : undefined,
    task_type: taskTypeFilter.value !== "ALL" ? taskTypeFilter.value : undefined,
    search: searchTasks.value.trim() || undefined,
    ordering: sortOrder.value,
    ...buildDueParams(),
  };
}

async function loadTasks({ append = false, pageUrl = null } = {}) {
  if (!isTeam.value) return;
  if (append && !taskPagination.value.next && !pageUrl) return;
  const target = append ? loadingMoreTasks : loadingTasks;
  if (target.value) return;
  const requestId = Date.now() + Math.random();
  loadTasks._lastRequestId = requestId;
  target.value = true;
  try {
    const params = pageUrl ? undefined : buildTaskParams();
    const url = pageUrl || "tasks/";
    const { data } = await api.get(url, { params });
    if (loadTasks._lastRequestId !== requestId) return;
    const normalized = normalizeListPayload(data);
    tasks.value = append
      ? mergeUniqueTasks(tasks.value.concat(normalized.items))
      : normalized.items;
    taskPagination.value = {
      next: normalized.next,
      previous: normalized.previous,
      count: normalized.count,
    };
    if (activeTaskId.value && !tasks.value.find((task) => task.id === activeTaskId.value)) {
      activeTaskId.value = null;
    }
    maybeOpenTaskFromQuery();
    if (!append) {
      await nextTick();
      setupTaskObserver();
    }
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

async function loadTaskSummary() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("tasks/summary/");
    taskSummary.value = {
      total: data.total || 0,
      archived: data.archived || 0,
      active: data.active || 0,
      done: data.done || 0,
      by_status: data.by_status || {},
      by_type: data.by_type || {},
    };
  } catch (err) {
    console.error("Task-Statistiken konnten nicht geladen werden", err);
    taskSummary.value = { total: 0, archived: 0, active: 0, done: 0, by_status: {}, by_type: {} };
    showToast("Task-Statistiken konnten nicht geladen werden", "error");
  }
}

async function refreshTasks() {
  await Promise.all([loadTasks(), loadTaskSummary()]);
}

watch(
  [() => route.name, () => isTeam.value],
  async ([name, team]) => {
    if (!team) return;
    if (name === "tasks-finished") {
      showCompleted.value = true;
      filterStatus.value = "DONE";
    } else if (name === "tasks") {
      if (filterStatus.value === "DONE") {
        filterStatus.value = "ALL";
      }
      showCompleted.value = false;
    }
    await Promise.all([loadTasks(), loadTaskSummary()]);
  },
  { immediate: true }
);

async function exportCalendar() {
  if (calendarExporting.value) return;
  calendarExporting.value = true;
  try {
    const { data } = await api.get("tasks/calendar-export/", {
      params: {
        project: filterProject.value !== "ALL" ? filterProject.value : undefined,
        include_archived: showArchived.value ? 1 : 0,
        include_done: showCompleted.value ? 1 : 0,
      },
      responseType: "blob",
    });
    const blob = new Blob([data], { type: "text/calendar;charset=utf-8" });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "tasks.ics";
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

async function submitTaskForm() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  const payload = {
    title: taskForm.value.title.trim(),
    status: taskForm.value.status,
    priority: taskForm.value.priority,
    task_type: taskForm.value.task_type,
    stakeholder_ids: taskForm.value.stakeholder_ids,
    assignee_ids: taskForm.value.assignee_ids,
    recurrence_pattern: taskForm.value.recurrence_pattern,
    recurrence_interval: taskForm.value.recurrence_pattern === "NONE" ? 1 : Number(taskForm.value.recurrence_interval || 1),
  };
  if (taskForm.value.project) {
    payload.project = taskForm.value.project;
  }
  if (taskForm.value.due_date) {
    payload.due_date = taskForm.value.due_date;
  } else {
    payload.due_date = null;
  }
  try {
    if (taskModalMode.value === "edit" && editingTaskId.value) {
      await api.patch(`tasks/${editingTaskId.value}/`, payload);
      showToast("Task aktualisiert", "success");
    } else {
      await api.post("tasks/", payload);
      showToast("Task angelegt", "success");
    }
    await refreshTasks();
    taskModalVisible.value = false;
  } catch (err) {
    console.error("Task konnte nicht gespeichert werden", err);
    const errorDetail = err.response?.data?.detail || err.message || "Unbekannter Fehler";
    showToast(`Task konnte nicht gespeichert werden: ${errorDetail}`, "error");
  } finally {
    taskSaving.value = false;
  }
}

function openTaskModal() {
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
  taskModalMode.value = "edit";
  editingTaskId.value = task.id;
  taskForm.value = {
    title: task.title,
    project: task.project || "",
    status: task.status,
    priority: task.priority,
    assignee_ids: task.assignees?.map((p) => p.id) || [],
    stakeholder_ids: task.stakeholders?.map((p) => p.id) || [],
    due_date: task.due_date || "",
    task_type: task.task_type || "EXTERNAL",
    recurrence_pattern: task.recurrence_pattern || "NONE",
    recurrence_interval: task.recurrence_interval || 1,
  };
  taskModalVisible.value = true;
}

async function archiveCurrentTask() {
  if (!editingTaskId.value) return;
  if (!confirm(`Task "${taskForm.value.title}" archivieren?`)) return;
  taskSaving.value = true;
  try {
    await api.post(`tasks/${editingTaskId.value}/archive/`);
    await refreshTasks();
    taskModalVisible.value = false;
    showToast("Task archiviert", "success");
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
    showToast("Task konnte nicht archiviert werden", "error");
  } finally {
    taskSaving.value = false;
  }
}

async function deleteCurrentTask() {
  if (!editingTaskId.value) return;
  if (!confirm(`Task "${taskForm.value.title}" endgültig löschen?`)) return;
  taskSaving.value = true;
  try {
    try {
      await api.post(`tasks/${editingTaskId.value}/delete/`);
    } catch (err) {
      await api.delete(`tasks/${editingTaskId.value}/`);
    }
    await refreshTasks();
    taskModalVisible.value = false;
    showToast("Task gelöscht", "success");
  } catch (err) {
    console.error("Task konnte nicht gelöscht werden", err);
    showToast("Task konnte nicht gelöscht werden", "error");
  } finally {
    taskSaving.value = false;
  }
}

function openFilterModal() {
  showFilterModal.value = true;
}
function closeFilterModal() {
  showFilterModal.value = false;
}
async function applyFilters() {
  await Promise.all([loadTasks(), loadTaskSummary()]);
  closeFilterModal();
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

function canResolveReview(task) {
  return Boolean(task && (task.status === "REVIEW" || (task.status === "DONE" && task.review_status === "NOT_REVIEWED")));
}

async function applyStatusChange(task, newStatus, reviewStatus, previousStatus) {
  const fallbackStatus = previousStatus ?? statusSnapshot.value[task.id] ?? task.status;
  const payload = { status: newStatus };
  if (reviewStatus) {
    payload.review_status = reviewStatus;
  }
  let patchSucceeded = false;
  try {
    await api.patch(`tasks/${task.id}/`, payload);
    patchSucceeded = true;
    statusSnapshot.value = { ...statusSnapshot.value, [task.id]: newStatus };
    task.status = newStatus;
    if (reviewStatus) {
      task.review_status = reviewStatus;
    } else if (newStatus !== "DONE") {
      task.review_status = null;
    }
    if (newStatus === "DONE") {
      showCompleted.value = true;
    }
  } catch (err) {
    console.error("Task-Status konnte nicht aktualisiert werden", err);
    task.status = fallbackStatus;
    const errorDetail = err.response?.data?.detail || err.message || "Unbekannter Fehler";
    showToast(`Status konnte nicht aktualisiert werden: ${errorDetail}`, "error");
    return false;
  }

  await Promise.all([loadTasks(), loadTaskSummary()]);
  showToast("Status aktualisiert", "success");
  return patchSucceeded;
}

async function onStatusChange(task, event) {
  const nextStatus = event?.target?.value || task.status;
  const previousStatus = statusSnapshot.value[task.id] || task.status;
  if (nextStatus === "DONE" && previousStatus !== "DONE") {
    openReviewModal(task, previousStatus);
    return;
  }
  await applyStatusChange(task, nextStatus, null, previousStatus);
}

async function confirmReviewDecision(reviewed) {
  if (!reviewTarget.value) return;
  const task = reviewTarget.value;
  const reviewStatus = reviewed ? "REVIEWED" : "NOT_REVIEWED";
  const success = await applyStatusChange(task, "DONE", reviewStatus, reviewPreviousStatus.value);
  // Always close modal after decision, even on error to prevent modal from staying stuck
  closeReviewModal();
}

async function setTaskReviewStatus(task, reviewed) {
  if (!task?.id || reviewActionSaving.value[task.id]) return;
  reviewActionSaving.value = { ...reviewActionSaving.value, [task.id]: true };
  try {
    const previousStatus = statusSnapshot.value[task.id] ?? task.status;
    await applyStatusChange(task, "DONE", reviewed ? "REVIEWED" : "NOT_REVIEWED", previousStatus);
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
    await refreshTasks();
    showToast("Task archiviert", "success");
  } catch (err) {
    console.error("Task konnte nicht archiviert werden", err);
    showToast("Task konnte nicht archiviert werden", "error");
  }
}

async function loadProfiles() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("profiles/");
    const list = Array.isArray(data) ? data : data?.results || [];
    profiles.value = list.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
      username: profile.username,
      roles: profile.roles || [],
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    profiles.value = [];
  }
}

function openTask(task) {
  activeTaskId.value = task.id;
  ensureTaskComments(task.id);
}

function maybeOpenTaskFromQuery() {
  if (!isTeam.value) return;
  const rawId = route.query.taskId;
  const taskId = Number(rawId);
  if (!taskId || Number.isNaN(taskId)) return;
  if (activeTaskId.value === taskId) return;
  const match = tasks.value.find((task) => task.id === taskId);
  if (match) {
    openTask(match);
  }
}

async function ensureTaskComments(taskId, force = false) {
  if (!force && taskComments.value[taskId]) return;
  commentLoading.value[taskId] = true;
  try {
    const { data } = await api.get("task-comments/", { params: { task: taskId } });
    taskComments.value = { ...taskComments.value, [taskId]: data };
  } catch (err) {
    console.error("Kommentare konnten nicht geladen werden", err);
  } finally {
    commentLoading.value[taskId] = false;
  }
}

async function addComment(taskId) {
  const draft = taskCommentDraft(taskId);
  if (!draft.body.trim()) return;
  commentLoading.value[taskId] = true;
  try {
    await api.post("task-comments/", {
      task: taskId,
      body: draft.body.trim(),
      mentions: draft.mentions,
    });
    draft.body = "";
    draft.mentions = [];
    await ensureTaskComments(taskId, true);
    showToast("Kommentar gespeichert", "success");
  } catch (err) {
    console.error("Kommentar konnte nicht gespeichert werden", err);
    showToast("Kommentar konnte nicht gespeichert werden", "error");
  } finally {
    commentLoading.value[taskId] = false;
  }
}

watch(
  () => taskTypeFilter.value,
  (value) => {
    const mapped = value === "ALL" ? "ALL" : value;
    if (boardTypeFilter.value !== mapped) {
      boardTypeFilter.value = mapped;
    }
  },
  { immediate: true }
);

watch(
  () => searchTasks.value,
  () => {
    if (!isTeam.value) return;
    if (searchDebounce) clearTimeout(searchDebounce);
    searchDebounce = setTimeout(() => loadTasks(), 300);
  }
);

watch(
  () => tasks.value,
  (list) => {
    syncStatusSnapshot(list);
  },
  { immediate: true }
);

watch(
  () => route.query.taskId,
  () => {
    if (!tasks.value.length) return;
    maybeOpenTaskFromQuery();
  }
);

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await Promise.all([loadProjects(), loadProfiles()]);
    connectRealtime();
  }
});

onBeforeUnmount(() => {
  if (taskObserver) taskObserver.disconnect();
  if (searchDebounce) clearTimeout(searchDebounce);
  if (taskSummaryRefreshTimer) clearTimeout(taskSummaryRefreshTimer);
});
</script>

<style scoped>
.tasks {
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
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.info {
  max-width: 600px;
}
.workspace {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 20px;
}
.workspace.has-detail {
  grid-template-columns: minmax(0, 2.1fr) minmax(320px, 1fr);
  align-items: flex-start;
}
.board {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.finished-summary {
  border: 1px solid rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.06);
  padding: 18px 20px;
}
.finished-summary-body {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.finished-summary-body h3 {
  margin: 0;
}
.finished-summary-body p {
  margin: 0;
  color: var(--muted);
  max-width: 48rem;
}
.board-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}
.board-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.board-hint {
  font-size: 13px;
  margin-top: -8px;
}
.board-type-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.board-type-chips .chip {
  border: 1px solid rgba(148, 163, 184, 0.55);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.board-type-chips .chip.active {
  border-color: var(--brand);
  color: var(--brand);
}
.kpi-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 10px;
}
.kpi {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: rgba(15, 23, 42, 0.03);
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.kpi span {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.kpi strong {
  font-size: 22px;
  line-height: 1;
}
.kpi.warning {
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.1);
}
.kpi.success {
  border-color: rgba(16, 185, 129, 0.4);
  background: rgba(16, 185, 129, 0.1);
}
.progress-list {
  display: grid;
  gap: 8px;
}
.progress-item {
  display: grid;
  gap: 6px;
}
.progress-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}
.progress-head strong {
  font-size: 12px;
  color: var(--muted);
}
.progress-track {
  width: 100%;
  height: 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(148, 163, 184, 0.18);
  overflow: hidden;
}
.progress-fill {
  display: block;
  height: 100%;
  border-radius: inherit;
  width: 0;
  transition: width 0.25s ease;
}
.progress-track[data-status="OPEN"] .progress-fill {
  background: var(--status-open);
}
.progress-track[data-status="IN_PROGRESS"] .progress-fill {
  background: var(--status-in-progress);
}
.progress-track[data-status="REVIEW"] .progress-fill {
  background: var(--status-review);
}
.progress-track[data-status="DONE"] .progress-fill {
  background: var(--status-done);
}
.dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 999px;
  margin-right: 4px;
}
.dot[data-status="OPEN"] {
  background: var(--status-open);
}
.dot[data-status="IN_PROGRESS"] {
  background: var(--status-in-progress);
}
.dot[data-status="REVIEW"] {
  background: var(--status-review);
}
.dot[data-status="DONE"] {
  background: var(--status-done);
}
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(260px, 1fr));
  gap: 18px;
  width: 100%;
  align-items: flex-start;
}
.columns ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.empty {
  text-align: center;
  padding: 12px 0;
}
.task-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 0;
  background: var(--card);
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.06);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}
.task-card::before {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  top: 0;
  height: 4px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.5);
}
.task-card[data-status="OPEN"]::before {
  background: #f59e0b;
}
.task-card[data-status="IN_PROGRESS"]::before {
  background: #3b82f6;
}
.task-card[data-status="REVIEW"]::before {
  background: #a855f7;
}
.task-card[data-status="DONE"]::before {
  background: #10b981;
}
.task-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(15, 23, 42, 0.09);
}
.task-card.overdue {
  border-color: #dc2626;
}
.task-card.soon {
  border-color: #f97316;
}
.title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.title-row .title {
  font-size: 16px;
  font-weight: 600;
}
.pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 4px;
}
.priority,
.task-type {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.priority {
  background: rgba(99, 102, 241, 0.16);
  color: #4c1d95;
}
.priority[data-priority="HIGH"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.priority[data-priority="CRITICAL"] {
  background: rgba(239, 68, 68, 0.26);
  color: #7f1d1d;
}
.priority[data-priority="LOW"] {
  background: rgba(34, 197, 94, 0.18);
  color: #15803d;
}
.task-type {
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}
.task-type[data-type="INTERNAL"] {
  background: rgba(248, 113, 113, 0.22);
  color: #b91c1c;
}
.task-type.recurrence,
.type-chip.recurrence {
  background: rgba(16, 185, 129, 0.16);
  color: #047857;
}
.card-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: flex-end;
}
.small-text {
  font-size: 13px;
}
.due {
  font-size: 13px;
}
.due.overdue {
  color: #dc2626;
}
.due.soon {
  color: #ea580c;
}
.actions {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
  align-items: center;
  margin-top: auto;
}
.actions .input {
  width: 100%;
}
.review-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.skeleton-column {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skeleton-card {
  height: 90px;
  border-radius: 14px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.detail-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.detail-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.detail-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.detail-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 8px 0;
}
.status-chip,
.priority-chip,
.type-chip,
.archive-chip,
.review-chip {
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.status-chip {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}
.status-chip[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.16);
  color: #ea580c;
}
.status-chip[data-status="DONE"] {
  background: rgba(16, 185, 129, 0.16);
  color: #059669;
}
.priority-chip[data-priority="HIGH"],
.priority-chip[data-priority="CRITICAL"] {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.priority-chip[data-priority="MEDIUM"] {
  background: rgba(251, 191, 36, 0.2);
  color: #92400e;
}
.priority-chip[data-priority="LOW"] {
  background: rgba(52, 211, 153, 0.16);
  color: #047857;
}
.type-chip {
  background: rgba(59, 130, 246, 0.16);
  color: #1d4ed8;
}
.type-chip[data-type="INTERNAL"] {
  background: rgba(248, 113, 113, 0.22);
  color: #b91c1c;
}
.archive-chip {
  background: rgba(15, 23, 42, 0.12);
  color: #111827;
}
.review-chip {
  background: rgba(15, 23, 42, 0.12);
  color: #1f2937;
}
.review-chip[data-review="REVIEWED"] {
  background: rgba(16, 185, 129, 0.16);
  color: #059669;
}
.review-chip[data-review="NOT_REVIEWED"] {
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
.eyebrow {
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.12em;
  color: var(--muted);
  margin: 0;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 18px;
}
.info-panel {
  padding: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  border-radius: 12px;
  background: rgba(248, 250, 252, 0.7);
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.info-grid dt {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.info-grid dd {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
}
.chip-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.chip-list {
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
.comments-panel {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.comment-list {
  list-style: none;
  padding: 0;
  margin: 0 0 10px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
select[multiple] {
  min-height: 150px;
}
.comment-list article {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.comment-list header {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  color: var(--muted);
}
.mentions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
}
.mentions span {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
  border-radius: 999px;
  padding: 2px 8px;
}
.comment-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}
.iconbtn {
  border: none;
  background: transparent;
  cursor: pointer;
}
.iconbtn.danger {
  color: #dc2626;
}
.due-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.due-chips .chip {
  border: 1px solid rgba(148, 163, 184, 0.5);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.due-chips .chip.active {
  border-color: #2563eb;
  color: #2563eb;
}
.visibility {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 500;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
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
  background: var(--modal-bg);
  box-shadow: var(--modal-shadow);
}
.modal.wide {
  max-width: 920px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 16px;
}
.form-grid .full {
  grid-column: 1 / -1;
}
.form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 14px;
  font-weight: 600;
}
.form .hint {
  font-size: 12px;
  font-weight: 400;
}
.textarea {
  min-height: 110px;
  resize: vertical;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
:global(.dark) .tasks .card {
  background: var(--card);
  border-color: var(--border);
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.35);
}
:global(.dark) .tasks .task-card {
  background: rgba(15, 23, 42, 0.6);
  border-color: var(--border);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
}
:global(.dark) .tasks .kpi {
  background: rgba(15, 23, 42, 0.45);
}
:global(.dark) .tasks .progress-track {
  background: rgba(148, 163, 184, 0.12);
}
:global(.dark) .tasks .modal {
  background: var(--card);
  box-shadow: 0 40px 80px rgba(0, 0, 0, 0.55);
}
:global(.dark) .tasks .info-panel {
  background: rgba(15, 23, 42, 0.6);
  border-color: var(--border);
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}
.danger-zone {
  border: 1px dashed rgba(220, 38, 38, 0.4);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  background: rgba(248, 113, 113, 0.08);
}
.danger-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sentinel {
  width: 100%;
  height: 1px;
}
.loading-more {
  text-align: center;
  font-size: 13px;
  color: var(--muted);
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
@media (max-width: 1100px) {
  .workspace.has-detail {
    grid-template-columns: minmax(0, 1fr);
  }
  .columns {
    grid-template-columns: repeat(2, minmax(240px, 1fr));
  }
}
@media (max-width: 720px) {
  .columns {
    grid-template-columns: 1fr;
  }
  .modal {
    padding: 18px;
  }
  .form-grid {
    grid-template-columns: 1fr;
  }
  .actions {
    grid-template-columns: 1fr;
  }
  .actions .btn,
  .actions .input {
    width: 100%;
  }
}
</style>
