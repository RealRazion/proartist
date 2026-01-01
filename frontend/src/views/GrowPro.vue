<template>
  <div class="growpro">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
    <header class="card header">
      <div>
        <p class="eyebrow">Team</p>
        <h1>GrowPro Ziele</h1>
        <p class="muted">
          Ziele f&uuml;r die n&auml;chsten 3 Monate, mit schnellen Updates. F&auml;lligkeiten im Blick.
        </p>
      </div>
      <button class="btn ghost" type="button" @click="loadGoals()" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>


    <section v-if="isTeam" class="card form">
      <h2>Neues Ziel anlegen</h2>
      <div class="form-grid">
        <label>
          K&uuml;nstler
          <select class="input" v-model="form.profile_id">
            <option value="">Profil w&auml;hlen</option>
            <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </label>
        <label>
          Titel
          <input class="input" v-model.trim="form.title" placeholder="z.B. Monatliche H&ouml;rer" />
        </label>
        <label>
          Einheit
          <input class="input" v-model.trim="form.unit" placeholder="H&ouml;rer / Streams / %" />
        </label>
        <label>
          Zielwert
          <input class="input" type="number" v-model.number="form.target_value" />
        </label>
        <label>
          Startwert
          <input class="input" type="number" v-model.number="form.current_value" />
        </label>
        <label>
          F&auml;llig am
          <input class="input" type="date" v-model="form.due_date" />
        </label>
        <label>
          Status
          <select class="input" v-model="form.status">
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
      </div>
      <div class="form-actions">
        <button class="btn" type="button" @click="createGoal" :disabled="creating">
          {{ creating ? "Speichere..." : "Ziel speichern" }}
        </button>
        <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
      </div>
    </section>

    <div class="filters-toggle">
      <button class="btn ghost" type="button" @click="toggleFilters">
        {{ showFilters ? "Filter ausblenden" : "Filter anzeigen" }}
      </button>
    </div>

    <section v-if="showFilters" class="card filters">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="search" placeholder="Titel suchen..." @keyup.enter="applyFilters" />
        </label>
        <label>
          Status
          <select class="input" v-model="filterStatus" @change="applyFilters">
            <option value="ALL">Alle</option>
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
        <label>
          F&auml;lligkeit
          <select class="input" v-model="dueFilter" @change="applyFilters">
            <option value="ALL">Alle</option>
            <option value="SOON">&lt; 24h</option>
            <option value="OVERDUE">&Uuml;berf&auml;llig</option>
            <option value="STALE">&gt;72h ohne Update</option>
          </select>
        </label>
        <label>
          Sortierung
          <select class="input" v-model="sort" @change="applyFilters">
            <option value="due_date">F&auml;lligkeit aufsteigend</option>
            <option value="-due_date">F&auml;lligkeit absteigend</option>
            <option value="-last_logged_at">Letztes Update (neueste)</option>
            <option value="-updated_at">Zuletzt ge&auml;ndert</option>
            <option value="-created_at">Neueste zuerst</option>
          </select>
        </label>
        <label v-if="isTeam">
          K&uuml;nstler
          <select class="input" v-model="filterProfile" @change="applyFilters">
            <option value="ALL">Alle</option>
            <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </label>
      </div>
      <div class="filter-actions">
        <button class="btn ghost tiny" type="button" @click="applyFilters">Filter anwenden</button>
      </div>
    </section>

    <section class="goals">
      <div v-if="!filteredGoals.length && !loading" class="card muted empty">Keine Ziele vorhanden.</div>
      <div v-else class="goal-grid">
        <article
          v-for="goal in filteredGoals"
          :key="goal.id"
          class="card goal"
          :data-due="dueState(goal)"
        >
          <div class="goal-head">
            <div>
              <p class="muted small">{{ goal.profile?.name || goal.profile?.username || "Unbekannt" }}</p>
              <h3>{{ goal.title }}</h3>
            </div>
            <span class="pill" :data-status="goal.status">{{ statusLabels[goal.status] || goal.status }}</span>
          </div>
          <div class="stats">
            <div>
              <p class="label">Aktuell</p>
              <strong>{{ formatNumber(goal.current_value) }}{{ goal.unit ? " " + goal.unit : "" }}</strong>
            </div>
            <div>
              <p class="label">Ziel</p>
              <strong>{{ formatNumber(goal.target_value) }}{{ goal.unit ? " " + goal.unit : "" }}</strong>
            </div>
            <div>
              <p class="label">F&auml;llig</p>
              <strong>{{ formatDate(goal.due_date) || "-" }}</strong>
            </div>
          </div>
          <div class="meta-row">
            <p class="muted">Letztes Update: {{ formatDateTime(goal.last_logged_at) || "Noch keines" }}</p>
            <span v-if="dueState(goal) === 'OVERDUE'" class="badge danger">&Uuml;berf&auml;llig</span>
            <span v-else-if="dueState(goal) === 'SOON'" class="badge warn">&lt;24h</span>
            <span v-else-if="dueState(goal) === 'STALE'" class="badge warn">>72h ohne Update</span>
          </div>
          <div v-if="canManageGoal(goal)" class="goal-actions">
            <button class="btn ghost tiny" type="button" @click="openEdit(goal)">Bearbeiten</button>
            <button class="btn ghost tiny danger" type="button" @click="deleteGoal(goal)">L&ouml;schen</button>
          </div>
          <div class="log-row">
            <input
              class="input"
              type="number"
              :placeholder="formatNumber(goal.current_value)"
              v-model.number="logDraft(goal.id).value"
            />
            <input
              class="input"
              placeholder="Notiz"
              v-model.trim="logDraft(goal.id).note"
            />
            <button class="btn ghost tiny" type="button" @click="logValue(goal)" :disabled="logging[goal.id]">
              {{ logging[goal.id] ? "Speichere..." : "Update" }}
            </button>
          </div>
          <div class="updates" v-if="goal.updates?.length">
            <p class="small muted">Letzte Eintr&auml;ge:</p>
            <ul>
              <li v-for="update in goal.updates.slice(0, 3)" :key="update.id">
                <span>{{ formatNumber(update.value) }}</span>
                <small>{{ formatDateTime(update.created_at) }}</small>
              </li>
            </ul>
          </div>
        </article>
      </div>
    </section>

    <div v-if="editModalOpen" class="modal-backdrop" @click.self="closeEdit">
      <div class="modal card">
        <div class="modal-head">
          <h3>Ziel bearbeiten</h3>
          <button class="btn ghost tiny" type="button" @click="closeEdit" :disabled="savingEdit">
            Schliessen
          </button>
        </div>
        <form class="form" @submit.prevent="saveEdit">
          <div class="form-grid">
            <label v-if="isTeam">
              K&uuml;nstler
              <select class="input" v-model="editForm.profile_id">
                <option value="">Profil w&auml;hlen</option>
                <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
              </select>
            </label>
            <label>
              Titel
              <input class="input" v-model.trim="editForm.title" placeholder="z.B. Monatliche H&ouml;rer" />
            </label>
            <label>
              Einheit
              <input class="input" v-model.trim="editForm.unit" placeholder="H&ouml;rer / Streams / %" />
            </label>
            <label>
              Zielwert
              <input class="input" type="number" v-model.number="editForm.target_value" />
            </label>
            <label>
              Startwert
              <input class="input" type="number" v-model.number="editForm.current_value" />
            </label>
            <label>
              F&auml;llig am
              <input class="input" type="date" v-model="editForm.due_date" />
            </label>
            <label>
              Status
              <select class="input" v-model="editForm.status">
                <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
              </select>
            </label>
          </div>
          <div class="form-actions">
            <button class="btn ghost" type="button" @click="closeEdit" :disabled="savingEdit">Abbrechen</button>
            <button class="btn" type="submit" :disabled="savingEdit">
              {{ savingEdit ? "Speichere..." : "Speichern" }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <div class="pagination" v-if="pageCount > 1">
      <button class="btn ghost tiny" type="button" :disabled="page === 1 || loading" @click="changePage(-1)">Zur&uuml;ck</button>
      <span>Seite {{ page }} / {{ pageCount }}</span>
      <button class="btn ghost tiny" type="button" :disabled="page === pageCount || loading" @click="changePage(1)">Weiter</button>
    </div>

    <section v-if="isTeam" class="card activity">
      <div class="activity-head">
        <h2>Aktivit&auml;t</h2>
        <button class="btn ghost tiny" type="button" @click="loadActivity" :disabled="loadingActivity">
          {{ loadingActivity ? "Lade..." : "Neu laden" }}
        </button>
      </div>
      <ul v-if="activities.length">
        <li v-for="item in activities" :key="item.id">
          <div class="row">
            <strong>{{ item.title }}</strong>
            <span class="pill subtle">{{ formatDateTime(item.created_at) }}</span>
          </div>
          <p class="muted small">{{ item.description || item.event_type }}</p>
        </li>
      </ul>
      <p v-else class="muted small">Keine Aktivit&auml;ten vorhanden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";

const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();

const goals = ref([]);
const profiles = ref([]);
const activities = ref([]);
const loading = ref(false);
const creating = ref(false);
const logging = ref({});
const loadingActivity = ref(false);
const showFilters = ref(false);
const editModalOpen = ref(false);
const savingEdit = ref(false);
const editForm = ref({
  id: null,
  profile_id: "",
  title: "",
  unit: "",
  target_value: 0,
  current_value: 0,
  due_date: "",
  status: "ACTIVE",
});

const message = ref("");
const messageType = ref("info");

const filterStatus = ref("ALL");
const filterProfile = ref("ALL");
const dueFilter = ref("ALL");
const search = ref("");
const sort = ref("due_date");

const statusOptions = ["ACTIVE", "ON_HOLD", "DONE", "ARCHIVED"];
const statusLabels = {
  ACTIVE: "Aktiv",
  ON_HOLD: "Pausiert",
  DONE: "Erledigt",
  ARCHIVED: "Archiviert",
};

const form = ref({
  profile_id: "",
  title: "",
  description: "",
  unit: "",
  target_value: 0,
  current_value: 0,
  due_date: "",
  status: "ACTIVE",
});

const logDrafts = ref({});
const page = ref(1);
const pageSize = ref(9);
const total = ref(0);

const sortedGoals = computed(() => goals.value);

const filteredGoals = computed(() =>
  sortedGoals.value.filter((goal) => {
    const term = search.value.trim().toLowerCase();
    const matchesText =
      !term ||
      goal.title.toLowerCase().includes(term) ||
      (goal.description || "").toLowerCase().includes(term);
    const matchesStatus = filterStatus.value === "ALL" || goal.status === filterStatus.value;
    const matchesProfile = filterProfile.value === "ALL" || String(goal.profile?.id) === String(filterProfile.value);
    const due = dueState(goal);
    const matchesDue =
      dueFilter.value === "ALL" ||
      (dueFilter.value === "SOON" && due === "SOON") ||
      (dueFilter.value === "OVERDUE" && due === "OVERDUE") ||
      (dueFilter.value === "STALE" && due === "STALE");
    return matchesText && matchesStatus && matchesProfile && matchesDue;
  })
);

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

function logDraft(id) {
  if (!logDrafts.value[id]) {
    logDrafts.value[id] = { value: "", note: "" };
  }
  return logDrafts.value[id];
}

function dueState(goal) {
  if (!goal || ["DONE", "ARCHIVED"].includes(goal.status)) return "OK";
  const now = Date.now();
  const dueDate = goal.due_date ? new Date(goal.due_date).getTime() : null;
  const lastLogged = goal.last_logged_at ? new Date(goal.last_logged_at).getTime() : null;
  if (dueDate && dueDate < now) return "OVERDUE";
  if (dueDate && dueDate - now < 24 * 60 * 60 * 1000) return "SOON";
  if (!lastLogged || (now - lastLogged) / (1000 * 60 * 60) > 72) return "STALE";
  return "OK";
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function formatNumber(value) {
  if (value === null || value === undefined || value === "") return "";
  const num = Number(value);
  if (Number.isNaN(num)) return String(value);
  if (Number.isInteger(num)) return String(num);
  return String(num);
}

function canManageGoal(goal) {
  if (!goal) return false;
  if (isTeam.value) return true;
  return String(goal.profile?.id) === String(me.value?.id);
}

function openEdit(goal) {
  if (!canManageGoal(goal)) return;
  editForm.value = {
    id: goal.id,
    profile_id: goal.profile?.id || "",
    title: goal.title || "",
    unit: goal.unit || "",
    target_value: Number(goal.target_value || 0),
    current_value: Number(goal.current_value || 0),
    due_date: goal.due_date || "",
    status: goal.status || "ACTIVE",
  };
  editModalOpen.value = true;
}

function closeEdit() {
  if (savingEdit.value) return;
  editModalOpen.value = false;
}

async function saveEdit() {
  if (!editForm.value.title) {
    showMessage("Titel ist erforderlich.", "error");
    return;
  }
  if (isTeam.value && !editForm.value.profile_id) {
    showMessage("Kuenstler ist erforderlich.", "error");
    return;
  }
  savingEdit.value = true;
  try {
    const payload = {
      title: editForm.value.title.trim(),
      unit: (editForm.value.unit || "").trim(),
      target_value: Number(editForm.value.target_value || 0),
      current_value: Number(editForm.value.current_value || 0),
      due_date: editForm.value.due_date || null,
      status: editForm.value.status,
    };
    if (isTeam.value) {
      payload.profile_id = editForm.value.profile_id;
    }
    await api.patch(`growpro/${editForm.value.id}/`, payload);
    editModalOpen.value = false;
    await loadGoals();
    showToast("Ziel gespeichert", "success");
  } catch (err) {
    console.error("Ziel konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Speichern", "error");
    showToast("Fehler beim Speichern", "error");
  } finally {
    savingEdit.value = false;
  }
}

async function deleteGoal(goal) {
  if (!canManageGoal(goal)) return;
  if (!window.confirm(`Ziel \"${goal.title}\" loeschen?`)) return;
  try {
    await api.delete(`growpro/${goal.id}/`);
    await loadGoals();
    showToast("Ziel geloescht", "success");
  } catch (err) {
    console.error("Ziel konnte nicht geloescht werden", err);
    showToast("Loeschen fehlgeschlagen", "error");
  }
}

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
  if (text) {
    setTimeout(() => (message.value = ""), 2500);
  }
}

async function loadProfiles() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("profiles/", { params: { page_size: 200 } });
    profiles.value = (data || []).map((p) => ({ id: p.id, name: p.name || p.username }));
  } catch (err) {
    profiles.value = [];
  }
}

async function loadGoals(resetPage = false) {
  if (resetPage) page.value = 1;
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ordering: sort.value,
    };
    if (filterStatus.value !== "ALL") params.status = filterStatus.value;
    if (filterProfile.value !== "ALL") params.profile = filterProfile.value;
    if (search.value.trim()) params.search = search.value.trim();
    const { data } = await api.get("growpro/", { params });
    const payload = data || {};
    const items = Array.isArray(payload) ? payload : payload.results || [];
    goals.value = items;
    total.value = payload.count || items.length;
  } catch (err) {
    console.error("GrowPro konnte nicht geladen werden", err);
    goals.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

async function createGoal() {
  if (!form.value.title || (!form.value.profile_id && isTeam.value)) {
    showMessage("Titel und Kuenstler sind erforderlich.", "error");
    return;
  }
  creating.value = true;
  showMessage("");
  try {
    const payload = {
      ...form.value,
      metric: form.value.title.trim() || "Ziel",
    };
    await api.post("growpro/", payload);
    form.value = {
      profile_id: "",
      title: "",
      description: "",
      unit: "",
      target_value: 0,
      current_value: 0,
      due_date: "",
      status: "ACTIVE",
    };
    await loadGoals(true);
    showMessage("Ziel angelegt", "success");
    showToast("Ziel angelegt", "success");
  } catch (err) {
    console.error("Ziel konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Speichern", "error");
    showToast("Fehler beim Speichern", "error");
  } finally {
    creating.value = false;
  }
}

async function logValue(goal) {
  const draft = logDraft(goal.id);
  if (draft.value === "" || draft.value === null || Number.isNaN(Number(draft.value))) {
    showMessage("Bitte einen Wert eintragen.", "error");
    return;
  }
  logging.value = { ...logging.value, [goal.id]: true };
  try {
    await api.post(`growpro/${goal.id}/log/`, {
      value: draft.value,
      note: draft.note,
    });
    draft.value = "";
    draft.note = "";
    await loadGoals();
    showToast("Update gespeichert", "success");
  } catch (err) {
    console.error("Update konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Update", "error");
    showToast("Fehler beim Update", "error");
  } finally {
    logging.value = { ...logging.value, [goal.id]: false };
  }
}

async function loadActivity() {
  if (!isTeam.value) {
    activities.value = [];
    return;
  }
  loadingActivity.value = true;
  try {
    const { data } = await api.get("activity/", {
      params: { limit: 40, types: "growpro_created,growpro_updated,growpro_logged" },
    });
    activities.value = data || [];
  } catch (err) {
    activities.value = [];
  } finally {
    loadingActivity.value = false;
  }
}

function changePage(delta) {
  const next = page.value + delta;
  if (next < 1 || next > pageCount.value) return;
  page.value = next;
  loadGoals();
}

function toggleFilters() {
  showFilters.value = !showFilters.value;
}

function applyFilters() {
  loadGoals(true);
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProfiles(), loadGoals(), loadActivity()]);
});
</script>

<style scoped>
.growpro {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: var(--brand);
  margin: 0 0 6px;
}
.filters-toggle {
  display: flex;
  justify-content: flex-end;
}
.filter-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}
.filters .filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.feedback {
  margin: 0;
  font-size: 14px;
}
.feedback.error {
  color: #dc2626;
}
.feedback.success {
  color: #16a34a;
}
.goals {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.goal-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 12px;
}
.goal {
  display: flex;
  flex-direction: column;
  gap: 10px;
  border-top: 4px solid transparent;
}
.goal[data-due="OVERDUE"] {
  border-top-color: rgba(239, 68, 68, 0.7);
}
.goal[data-due="SOON"] {
  border-top-color: rgba(59, 130, 246, 0.6);
}
.goal[data-due="STALE"] {
  border-top-color: rgba(234, 179, 8, 0.7);
}
.goal-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}
.pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(75, 91, 255, 0.18);
}
.pill[data-status="ON_HOLD"] {
  background: rgba(249, 115, 22, 0.16);
  color: #c2410c;
}
.pill[data-status="DONE"] {
  background: rgba(52, 211, 153, 0.16);
  color: #0f766e;
}
.pill[data-status="ARCHIVED"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
.stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.stats .label {
  font-size: 12px;
  color: var(--muted);
  margin: 0 0 2px;
}
.badge {
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
  width: fit-content;
}
.badge.warn {
  background: rgba(234, 179, 8, 0.18);
  color: #a16207;
}
.badge.danger {
  background: rgba(248, 113, 113, 0.15);
  color: #b91c1c;
}
.log-row {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
  align-items: center;
}
.updates ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 6px;
}
.updates li {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}
.small {
  font-size: 13px;
}
.empty {
  text-align: center;
}
.muted.empty {
  padding: 12px 0;
}
.meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.goal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.btn.ghost.danger {
  border-color: rgba(220, 38, 38, 0.4);
  color: #dc2626;
}
.btn.ghost.danger:hover {
  border-color: rgba(185, 28, 28, 0.7);
  color: #b91c1c;
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
  width: min(640px, 100%);
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 24px;
  padding: 24px;
  background: linear-gradient(130deg, rgba(255, 255, 255, 0.98), rgba(241, 245, 249, 0.92));
  box-shadow: 0 35px 80px rgba(15, 23, 42, 0.35);
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
}
:global(.dark) .growpro .modal {
  background: var(--card);
  box-shadow: 0 35px 80px rgba(0, 0, 0, 0.55);
}
.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}
.activity ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}
.activity-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.pill.subtle {
  background: rgba(15, 23, 42, 0.06);
  color: #475569;
}
@media (min-width: 1200px) {
  .goal-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 720px) {
  .log-row {
    grid-template-columns: 1fr;
  }
}
</style>
