<template>
  <div class="growpro">
    <header class="card header">
      <div>
        <p class="eyebrow">Team</p>
        <h1>GrowPro Ziele</h1>
        <p class="muted">
          Ziele für die nächsten 3 Monate, schnell aktualisiert. Älteste Updates zuerst.
        </p>
      </div>
      <button class="btn ghost" type="button" @click="loadGoals" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section class="card filters">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="search" placeholder="Titel oder Kennzahl..." />
        </label>
        <label>
          Status
          <select class="input" v-model="filterStatus" @change="loadGoals">
            <option value="ALL">Alle</option>
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
        <label v-if="isTeam">
          Künstler
          <select class="input" v-model="filterProfile" @change="loadGoals">
            <option value="ALL">Alle</option>
            <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </label>
      </div>
    </section>

    <section v-if="isTeam" class="card form">
      <h2>Neues Ziel anlegen</h2>
      <div class="form-grid">
        <label>
          Künstler
          <select class="input" v-model="form.profile_id">
            <option value="">Wähle Profil</option>
            <option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.name }}</option>
          </select>
        </label>
        <label>
          Titel
          <input class="input" v-model.trim="form.title" placeholder="z.B. Monatliche Hörer" />
        </label>
        <label>
          Kennzahl
          <input class="input" v-model.trim="form.metric" placeholder="Monatliche Hörer, Streams..." />
        </label>
        <label>
          Einheit
          <input class="input" v-model.trim="form.unit" placeholder="Hörer / Streams / %" />
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
          Fällig am
          <input class="input" type="date" v-model="form.due_date" />
        </label>
        <label>
          Status
          <select class="input" v-model="form.status">
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
      </div>
      <button class="btn" type="button" @click="createGoal" :disabled="creating">
        {{ creating ? "Speichere..." : "Ziel speichern" }}
      </button>
      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
    </section>

    <section class="goals">
      <div v-if="!filteredGoals.length && !loading" class="card muted empty">Keine Ziele vorhanden.</div>
      <div v-else class="goal-grid">
        <article v-for="goal in filteredGoals" :key="goal.id" class="card goal">
          <div class="goal-head">
            <div>
              <p class="muted small">{{ goal.profile?.name || goal.profile?.username || "Unbekannt" }}</p>
              <h3>{{ goal.title }}</h3>
              <p class="muted">{{ goal.metric }} ({{ goal.unit || "-" }})</p>
            </div>
            <span class="pill" :data-status="goal.status">{{ statusLabels[goal.status] || goal.status }}</span>
          </div>
          <div class="stats">
            <div>
              <p class="label">Aktuell</p>
              <strong>{{ goal.current_value }}</strong>
            </div>
            <div>
              <p class="label">Ziel</p>
              <strong>{{ goal.target_value }}</strong>
            </div>
            <div>
              <p class="label">Fällig</p>
              <strong>{{ formatDate(goal.due_date) || "-" }}</strong>
            </div>
          </div>
          <p class="muted">Letztes Update: {{ formatDateTime(goal.last_logged_at) || "Noch keines" }}</p>
          <div v-if="stale(goal)" class="badge warn">>72h ohne Update</div>
          <div class="log-row">
            <input
              class="input"
              type="number"
              :placeholder="goal.current_value"
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
            <p class="small muted">Letzte Einträge:</p>
            <ul>
              <li v-for="update in goal.updates.slice(0, 3)" :key="update.id">
                <span>{{ update.value }}</span>
                <small>{{ formatDateTime(update.created_at) }}</small>
              </li>
            </ul>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

const goals = ref([]);
const profiles = ref([]);
const loading = ref(false);
const creating = ref(false);
const logging = ref({});
const message = ref("");
const messageType = ref("info");

const filterStatus = ref("ALL");
const filterProfile = ref("ALL");
const search = ref("");

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
  metric: "",
  unit: "",
  target_value: 0,
  current_value: 0,
  due_date: "",
  status: "ACTIVE",
});

const logDrafts = ref({});

const sortedGoals = computed(() =>
  goals.value
    .slice()
    .sort((a, b) => {
      const aDue = a.due_date ? new Date(a.due_date).getTime() : Infinity;
      const bDue = b.due_date ? new Date(b.due_date).getTime() : Infinity;
      return aDue - bDue;
    })
);

const filteredGoals = computed(() =>
  sortedGoals.value.filter((goal) => {
    const term = search.value.trim().toLowerCase();
    const matchesText =
      !term ||
      goal.title.toLowerCase().includes(term) ||
      (goal.metric || "").toLowerCase().includes(term);
    return matchesText;
  })
);

function logDraft(id) {
  if (!logDrafts.value[id]) {
    logDrafts.value[id] = { value: "", note: "" };
  }
  return logDrafts.value[id];
}

function stale(goal) {
  if (!goal.last_logged_at) return true;
  const last = new Date(goal.last_logged_at).getTime();
  const now = Date.now();
  const diffHours = (now - last) / (1000 * 60 * 60);
  return diffHours > 72;
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit" }).format(new Date(value));
}

function formatDateTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
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
    const { data } = await api.get("profiles/");
    profiles.value = data.map((p) => ({ id: p.id, name: p.name || p.username }));
  } catch (err) {
    profiles.value = [];
  }
}

async function loadGoals() {
  loading.value = true;
  try {
    const params = {};
    if (filterStatus.value !== "ALL") params.status = filterStatus.value;
    if (filterProfile.value !== "ALL") params.profile = filterProfile.value;
    const { data } = await api.get("growpro/", { params });
    goals.value = data || [];
  } catch (err) {
    console.error("GrowPro konnte nicht geladen werden", err);
    goals.value = [];
  } finally {
    loading.value = false;
  }
}

async function createGoal() {
  if (!form.value.title || !form.value.metric || !form.value.profile_id) {
    showMessage("Titel, Kennzahl und Künstler sind erforderlich.", "error");
    return;
  }
  creating.value = true;
  showMessage("");
  try {
    await api.post("growpro/", form.value);
    form.value = {
      profile_id: "",
      title: "",
      description: "",
      metric: "",
      unit: "",
      target_value: 0,
      current_value: 0,
      due_date: "",
      status: "ACTIVE",
    };
    await loadGoals();
    showMessage("Ziel angelegt", "success");
  } catch (err) {
    console.error("Ziel konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Speichern", "error");
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
  } catch (err) {
    console.error("Update konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Update", "error");
  } finally {
    logging.value = { ...logging.value, [goal.id]: false };
  }
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProfiles(), loadGoals()]);
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
.badge.warn {
  background: rgba(248, 113, 113, 0.15);
  color: #b91c1c;
  padding: 4px 8px;
  border-radius: 8px;
  font-size: 12px;
  width: fit-content;
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
