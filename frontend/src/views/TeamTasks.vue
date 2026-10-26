<template>
  <div class="team-tasks-page">
    <header class="page-head card">
      <div class="head-top">
        <div class="head-title">
          <div class="head-icon">🛠️</div>
          <div>
            <h2>Team &amp; Tooling Tasks</h2>
            <p class="muted small">
              Interne Entwicklungs-Aufgaben, Feature-Roadmap, Bugfixes und Plattform-Infrastruktur.
            </p>
          </div>
        </div>
        <div class="head-actions">
          <button class="btn ghost" type="button" @click="fetchTasks" :disabled="loading">
            <span :class="{ spinning: loading }">↻</span>
            <span>Aktualisieren</span>
          </button>
          <button class="btn primary-btn" type="button" @click="openCreateModal">
            <span>+</span>
            <span>Neuer Team-Task</span>
          </button>
        </div>
      </div>

      <!-- Quick KPI Stats -->
      <div class="kpis-bar">
        <div class="kpi-box">
          <span class="muted small">Gesamt Team-Tasks</span>
          <strong>{{ tasks.length }}</strong>
        </div>
        <div class="kpi-box highlight">
          <span class="muted small">Offen / In Arbeit</span>
          <strong>{{ pendingCount }}</strong>
        </div>
        <div class="kpi-box warning" v-if="dueSoonCount > 0">
          <span class="muted small">Bald fällig</span>
          <strong>{{ dueSoonCount }}</strong>
        </div>
        <div class="kpi-box success">
          <span class="muted small">Erledigt</span>
          <strong>{{ doneCount }}</strong>
        </div>
      </div>
    </header>

    <!-- Filter & View Switcher -->
    <div class="controls-bar card">
      <div class="search-wrap">
        <input
          class="input"
          v-model.trim="searchQuery"
          placeholder="Team-Tasks durchsuchen (Titel, Beschreibung)..."
        />
      </div>

      <div class="view-toggles">
        <div class="pill-group">
          <button
            class="pill-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            📋 Liste
          </button>
          <button
            class="pill-btn"
            :class="{ active: viewMode === 'board' }"
            @click="viewMode = 'board'"
          >
            📊 Board
          </button>
        </div>

        <select class="input select-filter" v-model="statusFilter">
          <option value="ALL">Alle Status</option>
          <option value="OPEN">Offen</option>
          <option value="IN_PROGRESS">In Bearbeitung</option>
          <option value="REVIEW">Review</option>
          <option value="DONE">Erledigt</option>
        </select>

        <select class="input select-filter" v-model="priorityFilter">
          <option value="ALL">Alle Prioritäten</option>
          <option value="CRITICAL">🔥 Kritisch</option>
          <option value="HIGH">⚡ Hoch</option>
          <option value="MEDIUM">Normal</option>
          <option value="LOW">Niedrig</option>
        </select>
      </div>
    </div>

    <!-- Quick Add Inline Bar -->
    <form class="quick-add-bar card" @submit.prevent="quickAddTask">
      <span class="quick-plus">+</span>
      <input
        class="quick-input"
        v-model.trim="quickTitle"
        placeholder="Schnell neuen Team-Task anlegen (z.B. API-Rate-Limit fixen, Design-Tokens anpassen)..."
        :disabled="saving"
      />
      <select class="quick-prio" v-model="quickPrio">
        <option value="MEDIUM">Mittel</option>
        <option value="HIGH">Hoch</option>
        <option value="CRITICAL">Kritisch</option>
        <option value="LOW">Niedrig</option>
      </select>
      <button class="btn tiny" type="submit" :disabled="!quickTitle || saving">
        {{ saving ? '...' : 'Anlegen' }}
      </button>
    </form>

    <!-- LIST VIEW -->
    <div v-if="viewMode === 'list'" class="tasks-container">
      <div class="task-list" v-if="filteredTasks.length">
        <article
          v-for="task in filteredTasks"
          :key="task.id"
          class="team-task-row card"
          :class="{ completed: task.status === 'DONE' }"
        >
          <label class="check-container">
            <input
              type="checkbox"
              :checked="task.status === 'DONE'"
              @change="toggleTaskDone(task)"
            />
            <span class="checkmark"></span>
          </label>

          <div class="row-main" @click="openEditModal(task)">
            <div class="row-meta">
              <span class="prio-tag" :data-prio="task.priority">{{ priorityLabel(task.priority) }}</span>
              <span class="status-tag" :data-status="task.status">{{ statusLabel(task.status) }}</span>
              <span class="due-tag" v-if="task.due_date" :class="dueState(task.due_date)">
                📅 {{ formatDate(task.due_date) }}
              </span>
              <span class="assignee-tag" v-if="task.assignees && task.assignees.length">
                👤 {{ task.assignees.map(a => a.name).join(', ') }}
              </span>
            </div>

            <h4 class="task-title" :class="{ strike: task.status === 'DONE' }">
              {{ task.title }}
            </h4>

            <p class="task-desc muted small" v-if="task.description">
              {{ task.description }}
            </p>
          </div>

          <div class="row-actions">
            <button class="btn ghost tiny" type="button" @click="openEditModal(task)">
              Details
            </button>
            <button class="btn ghost danger tiny" type="button" @click="deleteTask(task)">
              ✕
            </button>
          </div>
        </article>
      </div>

      <div class="empty-box card" v-else>
        <p class="muted">Keine Team-Tasks für diese Filterkriterien vorhanden.</p>
      </div>
    </div>

    <!-- BOARD VIEW -->
    <div v-else-if="viewMode === 'board'" class="kanban-grid">
      <div
        v-for="col in kanbanColumns"
        :key="col.status"
        class="kanban-col card"
      >
        <div class="col-head">
          <div class="col-title">
            <span class="col-dot" :data-status="col.status"></span>
            <strong>{{ col.label }}</strong>
          </div>
          <span class="col-count">{{ col.tasks.length }}</span>
        </div>

        <div class="col-items">
          <article
            v-for="task in col.tasks"
            :key="task.id"
            class="board-card"
            @click="openEditModal(task)"
          >
            <div class="card-prio-row">
              <span class="prio-tag" :data-prio="task.priority">{{ priorityLabel(task.priority) }}</span>
              <span class="due-mini" v-if="task.due_date" :class="dueState(task.due_date)">
                {{ formatDate(task.due_date) }}
              </span>
            </div>

            <h5 class="card-title">{{ task.title }}</h5>

            <p class="card-desc muted small" v-if="task.description">
              {{ task.description.slice(0, 90) }}{{ task.description.length > 90 ? '...' : '' }}
            </p>

            <div class="card-footer">
              <span class="assignee-mini" v-if="task.assignees && task.assignees.length">
                {{ task.assignees[0].name }}
              </span>
              <button
                class="btn ghost tiny status-move-btn"
                type="button"
                @click.stop="advanceStatus(task)"
                :title="'Nächster Status'"
              >
                {{ nextStatusLabel(task.status) }} →
              </button>
            </div>
          </article>
        </div>
      </div>
    </div>

    <!-- CREATE / EDIT MODAL -->
    <div class="modal-backdrop" v-if="showModal" @click.self="showModal = false">
      <div class="modal card task-modal-box">
        <div class="modal-head">
          <h3>{{ editingTaskId ? 'Team-Task bearbeiten' : 'Neuen Team-Task anlegen' }}</h3>
          <button class="btn ghost tiny" type="button" @click="showModal = false">✕</button>
        </div>

        <form class="modal-form" @submit.prevent="saveModalTask">
          <label class="form-field">
            <span>Titel *</span>
            <input
              class="input"
              v-model.trim="modalForm.title"
              placeholder="z. B. WebSocket Reconnect Timeout optimieren"
              required
            />
          </label>

          <label class="form-field">
            <span>Details &amp; Beschreibung (Notizen, Links, Anforderungen)</span>
            <textarea
              class="input textarea"
              rows="4"
              v-model="modalForm.description"
              placeholder="Füge hier technische Details, URLs, Checklisten oder Reproduktionsschritte ein..."
            ></textarea>
          </label>

          <div class="form-grid-2">
            <label class="form-field">
              <span>Status</span>
              <select class="input" v-model="modalForm.status">
                <option value="OPEN">Offen</option>
                <option value="IN_PROGRESS">In Bearbeitung</option>
                <option value="REVIEW">Review</option>
                <option value="DONE">Erledigt</option>
              </select>
            </label>

            <label class="form-field">
              <span>Priorität</span>
              <select class="input" v-model="modalForm.priority">
                <option value="LOW">Niedrig</option>
                <option value="MEDIUM">Mittel</option>
                <option value="HIGH">Hoch</option>
                <option value="CRITICAL">Kritisch</option>
              </select>
            </label>
          </div>

          <div class="form-grid-2">
            <label class="form-field">
              <span>Fälligkeitsdatum</span>
              <input class="input" type="date" v-model="modalForm.due_date" />
            </label>

            <label class="form-field" v-if="teamProfiles.length">
              <span>Zuständiges Team-Mitglied</span>
              <select class="input" v-model="modalForm.assignee_id">
                <option value="">Keiner zugewiesen</option>
                <option v-for="p in teamProfiles" :key="p.id" :value="p.id">
                  {{ p.name }}
                </option>
              </select>
            </label>
          </div>

          <div class="modal-foot">
            <button
              class="btn ghost danger"
              type="button"
              v-if="editingTaskId"
              @click="deleteTask({ id: editingTaskId })"
            >
              Löschen
            </button>
            <div class="right-buttons">
              <button class="btn ghost" type="button" @click="showModal = false">Abbrechen</button>
              <button class="btn primary-btn" type="submit" :disabled="saving">
                {{ saving ? 'Speichert...' : (editingTaskId ? 'Änderungen speichern' : 'Task anlegen') }}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { showToast } = useToast();
const { profile: currentProfile } = useCurrentProfile();

const tasks = ref([]);
const teamProfiles = ref([]);
const loading = ref(false);
const saving = ref(false);
const viewMode = ref("list"); // 'list' | 'board'
const statusFilter = ref("ALL");
const priorityFilter = ref("ALL");
const searchQuery = ref("");

const quickTitle = ref("");
const quickPrio = ref("MEDIUM");

const showModal = ref(false);
const editingTaskId = ref(null);
const modalForm = ref({
  title: "",
  description: "",
  status: "OPEN",
  priority: "MEDIUM",
  due_date: "",
  assignee_id: "",
});

const pendingCount = computed(() => {
  return tasks.value.filter((t) => t.status !== "DONE").length;
});

const doneCount = computed(() => {
  return tasks.value.filter((t) => t.status === "DONE").length;
});

const dueSoonCount = computed(() => {
  const today = new Date().toISOString().slice(0, 10);
  return tasks.value.filter((t) => t.status !== "DONE" && t.due_date && t.due_date <= today).length;
});

const filteredTasks = computed(() => {
  return tasks.value.filter((t) => {
    if (statusFilter.value !== "ALL" && t.status !== statusFilter.value) return false;
    if (priorityFilter.value !== "ALL" && t.priority !== priorityFilter.value) return false;
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase();
      const matchTitle = t.title && t.title.toLowerCase().includes(q);
      const matchDesc = t.description && t.description.toLowerCase().includes(q);
      if (!matchTitle && !matchDesc) return false;
    }
    return true;
  });
});

const kanbanColumns = computed(() => {
  const cols = [
    { status: "OPEN", label: "Offen" },
    { status: "IN_PROGRESS", label: "In Bearbeitung" },
    { status: "REVIEW", label: "Review" },
    { status: "DONE", label: "Erledigt" },
  ];

  return cols.map((col) => {
    return {
      ...col,
      tasks: filteredTasks.value.filter((t) => t.status === col.status),
    };
  });
});

async function fetchTasks() {
  loading.value = true;
  try {
    const [taskRes, profRes] = await Promise.all([
      api.get("tasks/?task_type=INTERNAL&include_done=true"),
      api.get("profiles/"),
    ]);

    tasks.value = Array.isArray(taskRes.data) ? taskRes.data : taskRes.data?.results || [];
    teamProfiles.value = Array.isArray(profRes.data) ? profRes.data : profRes.data?.results || [];
  } catch (err) {
    showToast("Fehler beim Laden der Team-Tasks", "error");
  } finally {
    loading.value = false;
  }
}

async function quickAddTask() {
  if (!quickTitle.value) return;
  saving.value = true;
  try {
    const res = await api.post("tasks/", {
      title: quickTitle.value,
      priority: quickPrio.value,
      status: "OPEN",
      task_type: "INTERNAL",
      assignee_ids: currentProfile.value?.id ? [currentProfile.value.id] : [],
    });
    showToast("Team-Task angelegt!", "info");
    quickTitle.value = "";
    tasks.value.unshift(res.data);
  } catch (err) {
    showToast("Fehler beim Erstellen des Tasks", "error");
  } finally {
    saving.value = false;
  }
}

function openCreateModal() {
  editingTaskId.value = null;
  modalForm.value = {
    title: "",
    description: "",
    status: "OPEN",
    priority: "MEDIUM",
    due_date: "",
    assignee_id: currentProfile.value?.id || "",
  };
  showModal.value = true;
}

function openEditModal(task) {
  editingTaskId.value = task.id;
  modalForm.value = {
    title: task.title,
    description: task.description || "",
    status: task.status,
    priority: task.priority,
    due_date: task.due_date || "",
    assignee_id: task.assignees?.[0]?.id || "",
  };
  showModal.value = true;
}

async function saveModalTask() {
  if (!modalForm.value.title) return;
  saving.value = true;
  try {
    const payload = {
      title: modalForm.value.title,
      description: modalForm.value.description,
      status: modalForm.value.status,
      priority: modalForm.value.priority,
      due_date: modalForm.value.due_date || null,
      task_type: "INTERNAL",
      assignee_ids: modalForm.value.assignee_id ? [modalForm.value.assignee_id] : [],
    };

    if (editingTaskId.value) {
      const res = await api.patch(`tasks/${editingTaskId.value}/`, payload);
      const idx = tasks.value.findIndex((t) => t.id === editingTaskId.value);
      if (idx !== -1) tasks.value[idx] = res.data;
      showToast("Task aktualisiert", "info");
    } else {
      const res = await api.post("tasks/", payload);
      tasks.value.unshift(res.data);
      showToast("Team-Task angelegt", "info");
    }
    showModal.value = false;
  } catch (err) {
    showToast("Fehler beim Speichern", "error");
  } finally {
    saving.value = false;
  }
}

async function toggleTaskDone(task) {
  const nextStatus = task.status === "DONE" ? "OPEN" : "DONE";
  try {
    const res = await api.patch(`tasks/${task.id}/`, { status: nextStatus });
    task.status = res.data.status;
    showToast(task.status === "DONE" ? "✓ Task erledigt!" : "Task wieder geöffnet", "info");
  } catch (err) {
    showToast("Status konnte nicht geändert werden", "error");
  }
}

async function advanceStatus(task) {
  const flow = {
    OPEN: "IN_PROGRESS",
    IN_PROGRESS: "REVIEW",
    REVIEW: "DONE",
    DONE: "OPEN",
  };
  const target = flow[task.status] || "OPEN";
  try {
    const res = await api.patch(`tasks/${task.id}/`, { status: target });
    task.status = res.data.status;
  } catch (err) {
    showToast("Konnte Status nicht weiterschalten", "error");
  }
}

async function deleteTask(task) {
  if (!confirm("Diesen Team-Task wirklich löschen?")) return;
  try {
    await api.delete(`tasks/${task.id}/`);
    tasks.value = tasks.value.filter((t) => t.id !== task.id);
    showToast("Task gelöscht", "info");
    showModal.value = false;
  } catch (err) {
    showToast("Fehler beim Löschen", "error");
  }
}

function priorityLabel(p) {
  const map = { CRITICAL: "Kritisch", HIGH: "Hoch", MEDIUM: "Normal", LOW: "Niedrig" };
  return map[p] || p;
}

function statusLabel(s) {
  const map = { OPEN: "Offen", IN_PROGRESS: "In Arbeit", REVIEW: "Review", DONE: "Erledigt" };
  return map[s] || s;
}

function nextStatusLabel(s) {
  const map = { OPEN: "In Arbeit", IN_PROGRESS: "Review", REVIEW: "Done", DONE: "Reopen" };
  return map[s] || "Weiter";
}

function formatDate(d) {
  if (!d) return "";
  try {
    return new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
  } catch {
    return d;
  }
}

function dueState(d) {
  if (!d) return "";
  const today = new Date().toISOString().slice(0, 10);
  if (d < today) return "overdue";
  if (d === today) return "today";
  return "future";
}

onMounted(() => {
  fetchTasks();
});
</script>

<style scoped>
.team-tasks-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.page-head {
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
}

.head-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.head-title {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.head-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.head-title h2 {
  margin: 0;
  font-size: 1.4rem;
  font-weight: 700;
}

.head-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.kpis-bar {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 1rem;
  margin-top: 1.25rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.kpi-box {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.kpi-box strong {
  font-size: 1.35rem;
}

.kpi-box.highlight strong { color: #38bdf8; }
.kpi-box.warning strong { color: #f59e0b; }
.kpi-box.success strong { color: #10b981; }

.controls-bar {
  padding: 0.85rem 1.25rem;
  border-radius: 12px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-wrap {
  flex: 1;
  min-width: 260px;
}

.view-toggles {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.pill-group {
  display: flex;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 8px;
  padding: 2px;
}

.pill-btn {
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--muted, #94a3b8);
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}

.pill-btn.active {
  background: var(--primary, #4f46e5);
  color: #fff;
}

.select-filter {
  padding: 0.35rem 0.75rem;
  border-radius: 8px;
  font-size: 0.82rem;
}

.quick-add-bar {
  padding: 0.6rem 1rem;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.quick-plus {
  font-size: 1.2rem;
  color: #38bdf8;
  font-weight: 700;
}

.quick-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 0.92rem;
  outline: none;
}

.quick-prio {
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 0.78rem;
}

.tasks-container {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.team-task-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.9rem 1.2rem;
  border-radius: 12px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  transition: transform 0.1s, border-color 0.15s;
}

.team-task-row:hover {
  border-color: rgba(99, 102, 241, 0.4);
}

.team-task-row.completed {
  opacity: 0.6;
}

.check-container {
  position: relative;
  width: 22px;
  height: 22px;
  cursor: pointer;
}

.check-container input {
  opacity: 0;
  position: absolute;
}

.checkmark {
  position: absolute;
  inset: 0;
  border-radius: 6px;
  border: 2px solid rgba(255, 255, 255, 0.25);
  background: rgba(255, 255, 255, 0.04);
}

.check-container input:checked ~ .checkmark {
  background: #10b981;
  border-color: #10b981;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 6px;
  top: 2px;
  width: 6px;
  height: 11px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.check-container input:checked ~ .checkmark:after {
  display: block;
}

.row-main {
  flex: 1;
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.row-meta {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  flex-wrap: wrap;
}

.prio-tag {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 6px;
  font-weight: 700;
}

.prio-tag[data-prio="CRITICAL"] { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.prio-tag[data-prio="HIGH"] { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.prio-tag[data-prio="MEDIUM"] { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.prio-tag[data-prio="LOW"] { background: rgba(255, 255, 255, 0.08); color: #94a3b8; }

.status-tag {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
}

.due-tag {
  font-size: 0.72rem;
  padding: 0.1rem 0.45rem;
  border-radius: 6px;
  color: var(--muted, #94a3b8);
}

.due-tag.overdue { color: #ef4444; font-weight: 700; }
.due-tag.today { color: #f59e0b; font-weight: 700; }

.assignee-tag {
  font-size: 0.72rem;
  color: #a5b4fc;
}

.task-title {
  margin: 0;
  font-size: 0.98rem;
  font-weight: 600;
}

.task-title.strike {
  text-decoration: line-through;
}

.task-desc {
  margin: 0;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Kanban Board */
.kanban-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem;
  align-items: flex-start;
}

.kanban-col {
  padding: 1rem;
  border-radius: 14px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.col-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 0.5rem;
}

.col-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.col-dot {
  width: 8px;
  height: 8px;
  border-radius: 999px;
}

.col-dot[data-status="OPEN"] { background: #38bdf8; }
.col-dot[data-status="IN_PROGRESS"] { background: #f59e0b; }
.col-dot[data-status="REVIEW"] { background: #a855f7; }
.col-dot[data-status="DONE"] { background: #10b981; }

.col-count {
  font-size: 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  padding: 0.1rem 0.5rem;
  font-weight: 700;
}

.col-items {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  min-height: 120px;
}

.board-card {
  padding: 0.85rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  transition: transform 0.15s, border-color 0.15s;
}

.board-card:hover {
  border-color: rgba(99, 102, 241, 0.4);
  transform: translateY(-2px);
}

.card-prio-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  margin: 0;
  font-size: 0.92rem;
  font-weight: 600;
}

.card-desc {
  margin: 0;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.35rem;
}

.assignee-mini {
  font-size: 0.72rem;
  color: #a5b4fc;
}

.due-mini {
  font-size: 0.72rem;
}
.due-mini.overdue { color: #ef4444; }

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.task-modal-box {
  width: 100%;
  max-width: 580px;
  border-radius: 16px;
  background: #141821;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 1.5rem;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.modal-head h3 { margin: 0; }

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.modal-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.right-buttons {
  display: flex;
  gap: 0.75rem;
  margin-left: auto;
}

.primary-btn {
  background: #4f46e5 !important;
  color: #fff !important;
}

.spinning {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
