<template>
  <div class="finance-tool">
    <section v-if="loading && !project" class="status-card loading-card">
      <h1>Finanzplaner</h1>
      <p class="muted">Lade Finanzprojekt...</p>
    </section>

    <section v-else-if="!projects.length" class="status-card empty-card">
      <h1>Kein Finanzprojekt vorhanden</h1>
      <p class="muted">Lege zuerst ein Finanzprojekt an.</p>
      <button class="btn" type="button" @click="router.push({ name: 'platform-finance' })">Zum Einstieg</button>
    </section>

    <template v-else>
      <header class="topbar-card">
        <div class="topbar-meta">
          <p class="eyebrow">Finanzplaner</p>
          <h1>{{ project?.title || "Finanzprojekt" }}</h1>
        </div>
        <div class="topbar-actions">
          <button class="btn ghost" type="button" @click="refreshCurrent" :disabled="loading">Aktualisieren</button>
          <button class="btn ghost" type="button" @click="showProjectSettingsModal = true">Einstellungen</button>
        </div>
      </header>

      <section v-if="errorMessage || successMessage" class="feedback-bar">
        <div v-if="errorMessage" class="feedback-pill error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="feedback-pill success">{{ successMessage }}</div>
      </section>

      <div class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="tab-pill"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          {{ tab.label }}
        </button>
      </div>

      <!-- ÜBERSICHT -->
      <section v-show="activeTab === 'overview'" class="overview-page">
        <div class="month-nav-bar">
          <button type="button" class="month-nav-btn" @click="shiftMonth(-1)">←</button>
          <span class="month-nav-label">{{ monthFormatted }}</span>
          <button type="button" class="month-nav-btn" @click="shiftMonth(1)">→</button>
        </div>

        <!-- Income input card -->
        <article class="panel income-card">
          <div class="panel-head panel-head-space">
            <div>
              <h2>Einnahmen</h2>
              <p class="muted">Trage deine Einnahmen für {{ monthFormatted }} ein.</p>
            </div>
          </div>
          <div class="income-input-row">
            <input
              v-model="incomeInput"
              class="input income-input"
              type="number"
              step="0.01"
              min="0"
              placeholder="0,00"
              @keyup.enter="saveIncome"
            />
            <button class="btn" type="button" @click="saveIncome" :disabled="savingIncome">
              {{ savingIncome ? "Speichere..." : "Speichern" }}
            </button>
          </div>
          <p v-if="incomeEntries.length > 1" class="muted small">
            Mehrere Einnahmequellen vorhanden – gesamt: {{ formatCurrency(overview.monthly_income) }}
          </p>
        </article>

        <!-- Calculation summary -->
        <article class="panel summary-card">
          <h2>Monatsrechnung</h2>
          <div class="calc-rows">
            <div class="calc-row income-row">
              <span>Einnahmen</span>
              <strong class="positive">+ {{ formatCurrency(overview.monthly_income) }}</strong>
            </div>
            <div class="calc-row debt-row">
              <span>Schulden (monatl.)</span>
              <strong class="negative">− {{ formatCurrency(monthlyDebtTotal) }}</strong>
            </div>
            <div class="calc-row sub-row">
              <span>Abos (monatl.)</span>
              <strong class="negative">− {{ formatCurrency(monthlySubscriptionTotal) }}</strong>
            </div>
            <div class="calc-divider"></div>
            <div class="calc-row result-row">
              <span>Verbleibend</span>
              <strong :class="remaining >= 0 ? 'positive' : 'negative'">
                {{ formatCurrency(remaining) }}
              </strong>
            </div>
          </div>
        </article>

        <!-- Quick overview stats -->
        <div class="stat-grid">
          <article class="stat-card">
            <span class="stat-label">Aktive Abos</span>
            <strong>{{ activeSubscriptionCount }}</strong>
          </article>
          <article class="stat-card">
            <span class="stat-label">Offene Restschuld</span>
            <strong>{{ formatCurrency(overview.total_debt || 0) }}</strong>
          </article>
          <article class="stat-card">
            <span class="stat-label">Monatl. Schulden</span>
            <strong>{{ formatCurrency(monthlyDebtTotal) }}</strong>
          </article>
          <article class="stat-card">
            <span class="stat-label">Monatl. Abos</span>
            <strong>{{ formatCurrency(monthlySubscriptionTotal) }}</strong>
          </article>
        </div>
      </section>

      <!-- SCHULDEN -->
      <section v-show="activeTab === 'debts'" class="debts-page">
        <DebtTracker :projectId="selectedProjectId" />
      </section>

      <!-- ABOS -->
      <section v-show="activeTab === 'subscriptions'" class="subscriptions-page">
        <article class="panel">
          <div class="panel-head panel-head-space">
            <div>
              <h2>Abos</h2>
              <p class="muted">Wiederkehrende Dienste und Mitgliedschaften.</p>
            </div>
            <button class="btn" type="button" @click="openCreateSubscriptionModal">Abo hinzufügen</button>
          </div>

          <div class="sub-summary">
            <div>
              <span class="stat-label">Aktiv</span>
              <strong>{{ activeSubscriptionCount }}</strong>
            </div>
            <div>
              <span class="stat-label">Monatlich gesamt</span>
              <strong>{{ formatCurrency(monthlySubscriptionTotal) }}</strong>
            </div>
          </div>

          <div v-if="subscriptionEntries.length" class="entry-list">
            <article
              v-for="entry in subscriptionEntries"
              :key="entry.id"
              class="entry-row"
              :class="{ inactive: !entry.is_active }"
            >
              <div class="entry-main">
                <strong>{{ entry.title }}</strong>
                <p class="muted small">
                  {{ frequencyLabels[entry.frequency] }}
                  <template v-if="entry.category"> · {{ entry.category }}</template>
                </p>
                <p v-if="entry.notes" class="muted small">{{ entry.notes }}</p>
              </div>
              <div class="entry-side">
                <strong>{{ formatCurrency(entry.monthly_amount || entry.amount) }}/Mon.</strong>
                <div class="entry-actions">
                  <button class="btn ghost sm" type="button" @click="editEntry(entry)">Bearbeiten</button>
                  <button class="btn ghost sm" type="button" @click="toggleEntry(entry)">
                    {{ entry.is_active ? "Pausieren" : "Aktivieren" }}
                  </button>
                  <button class="btn ghost sm danger" type="button" @click="removeEntry(entry)">Löschen</button>
                </div>
              </div>
            </article>
          </div>
          <div v-else class="empty-state">
            <p class="muted">Noch keine Abos hinterlegt.</p>
            <button class="btn" type="button" @click="openCreateSubscriptionModal">Erstes Abo hinzufügen</button>
          </div>
        </article>
      </section>
    </template>

    <!-- Project Settings Modal -->
    <div v-if="showProjectSettingsModal" class="modal-overlay" @click="showProjectSettingsModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>Projekteinstellungen</h3>
          <button class="modal-close" type="button" @click="showProjectSettingsModal = false">&times;</button>
        </div>
        <div class="modal-body">
          <form class="stack-form" @submit.prevent="saveProjectFromModal">
            <label>
              Titel
              <input v-model.trim="projectForm.title" class="input" />
            </label>
            <label>
              Währung
              <select v-model="projectForm.currency" class="input">
                <option value="EUR">EUR</option>
                <option value="USD">USD</option>
                <option value="CHF">CHF</option>
              </select>
            </label>
            <label>
              Notiz
              <textarea v-model.trim="projectForm.description" class="input textarea" rows="3"></textarea>
            </label>
            <div class="modal-actions">
              <button class="btn ghost" type="button" @click="showProjectSettingsModal = false">Abbrechen</button>
              <button class="btn" type="submit" :disabled="savingProject">
                {{ savingProject ? "Speichere..." : "Speichern" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Subscription Modal -->
    <div v-if="showSubscriptionModal" class="modal-overlay" @click="closeSubscriptionModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ editingEntryId ? "Abo bearbeiten" : "Neues Abo" }}</h3>
          <button class="modal-close" type="button" @click="closeSubscriptionModal">&times;</button>
        </div>
        <div class="modal-body">
          <form class="stack-form" @submit.prevent="saveEntry">
            <label>
              Titel
              <input v-model.trim="entryForm.title" class="input" placeholder="z. B. Netflix" required />
            </label>
            <div class="grid two">
              <label>
                Betrag
                <input v-model="entryForm.amount" class="input" type="number" step="0.01" min="0" required />
              </label>
              <label>
                Rhythmus
                <select v-model="entryForm.frequency" class="input">
                  <option v-for="(label, key) in frequencyLabels" :key="key" :value="key">{{ label }}</option>
                </select>
              </label>
            </div>
            <label>
              Kategorie
              <input v-model.trim="entryForm.category" class="input" placeholder="z. B. Streaming" />
            </label>
            <label>
              Notiz
              <textarea v-model.trim="entryForm.notes" class="input textarea" rows="2" placeholder="optional"></textarea>
            </label>
            <label class="toggle">
              <input v-model="entryForm.is_active" type="checkbox" />
              Aktiv
            </label>
            <div class="modal-actions">
              <button class="btn ghost" type="button" @click="closeSubscriptionModal">Abbrechen</button>
              <button class="btn" type="submit" :disabled="savingEntry">
                {{ savingEntry ? "Speichere..." : editingEntryId ? "Speichern" : "Anlegen" }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import DebtTracker from "../components/DebtTracker.vue";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const savingProject = ref(false);
const savingEntry = ref(false);
const savingIncome = ref(false);
const projects = ref([]);
const project = ref(null);
const selectedProjectId = ref(null);
const activeTab = ref("overview");
const errorMessage = ref("");
const successMessage = ref("");
const showProjectSettingsModal = ref(false);
const showSubscriptionModal = ref(false);
const editingEntryId = ref(null);
const incomeInput = ref("");
const selectedMonth = ref(new Date().toISOString().slice(0, 7));

const tabs = [
  { key: "overview", label: "Übersicht" },
  { key: "debts", label: "Schulden" },
  { key: "subscriptions", label: "Abos" },
];

const frequencyLabels = {
  MONTHLY: "Monatlich",
  WEEKLY: "Wöchentlich",
  YEARLY: "Jährlich",
  ONCE: "Einmalig",
};

const projectForm = ref({ title: "", description: "", currency: "EUR" });

function buildEntryForm(data = {}) {
  return {
    title: data.title || "",
    category: data.category || "",
    amount: data.amount ?? "",
    frequency: data.frequency || "MONTHLY",
    notes: data.notes || "",
    is_active: data.is_active ?? true,
  };
}

const entryForm = ref(buildEntryForm());

const overview = computed(() => project.value?.overview || {});
const currency = computed(() => project.value?.currency || "EUR");
const entries = computed(() => project.value?.entries || []);

const incomeEntries = computed(() =>
  entries.value.filter((e) => e.entry_type === "INCOME" && e.is_active !== false)
);

const subscriptionEntries = computed(() =>
  entries.value.filter((e) => e.entry_type === "SUBSCRIPTION")
);

const activeSubscriptionCount = computed(() =>
  subscriptionEntries.value.filter((e) => e.is_active !== false).length
);

const monthlySubscriptionTotal = computed(() => {
  const fromOverview = Number(overview.value.monthly_subscriptions || 0);
  if (fromOverview > 0) return fromOverview;
  return subscriptionEntries.value
    .filter((e) => e.is_active !== false)
    .reduce((sum, e) => sum + Number(e.monthly_amount || e.amount || 0), 0);
});

const monthlyDebtTotal = computed(() => Number(overview.value.monthly_debt_tracker || overview.value.monthly_debt || 0));

const remaining = computed(() =>
  Number(overview.value.monthly_income || 0) - monthlyDebtTotal.value - monthlySubscriptionTotal.value
);

const monthFormatted = computed(() => {
  const [y, m] = selectedMonth.value.split("-");
  return new Date(Number(y), Number(m) - 1, 1).toLocaleDateString("de-DE", { month: "long", year: "numeric" });
});

function shiftMonth(delta) {
  const [y, m] = selectedMonth.value.split("-").map(Number);
  const d = new Date(y, m - 1 + delta, 1);
  selectedMonth.value = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
}

function formatCurrency(value) {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: currency.value,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function toAmount(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function setError(message) {
  errorMessage.value = message;
  successMessage.value = "";
}

function setSuccess(message) {
  successMessage.value = message;
  errorMessage.value = "";
}

function getApiErrorMessage(error, fallback) {
  const data = error?.response?.data;
  if (typeof data === "string" && data.trim()) return data;
  if (data?.detail) return data.detail;
  if (data && typeof data === "object") {
    const msg = Object.entries(data)
      .map(([f, v]) => `${f}: ${Array.isArray(v) ? v.join(", ") : v}`)
      .join(" | ");
    if (msg) return msg;
  }
  return fallback;
}

async function loadProjects() {
  try {
    const { data } = await api.get("finance-projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    projects.value = [];
    setError(getApiErrorMessage(error, "Finanzprojekte konnten nicht geladen werden."));
    throw error;
  }
}

async function loadProjectDetail(projectId) {
  if (!projectId) return;
  loading.value = true;
  try {
    const { data } = await api.get(`finance-projects/${projectId}/`, {
      params: { month: selectedMonth.value },
    });
    project.value = data;
    selectedProjectId.value = data.id;
    projectForm.value = { title: data.title || "", description: data.description || "", currency: data.currency || "EUR" };
    // Pre-fill income input with current monthly income
    const rawEntries = Array.isArray(data.entries) ? data.entries : [];
    const mainIncome = rawEntries.find((e) => e.entry_type === "INCOME" && e.is_active !== false);
    incomeInput.value = mainIncome ? String(mainIncome.amount) : "";
    errorMessage.value = "";
    successMessage.value = "";
  } catch (error) {
    project.value = null;
    setError(getApiErrorMessage(error, "Finanzprojekt konnte nicht geladen werden."));
    throw error;
  } finally {
    loading.value = false;
  }
}

async function syncProjectSelection() {
  try {
    await loadProjects();
    if (!projects.value.length) {
      project.value = null;
      selectedProjectId.value = null;
      return;
    }
    const routeProjectId = Number(route.params.projectId || 0);
    const nextId = projects.value.some((p) => p.id === routeProjectId)
      ? routeProjectId
      : selectedProjectId.value || projects.value[0].id;
    if (!routeProjectId || routeProjectId !== nextId) {
      await router.replace({ name: "finance", params: { projectId: nextId } });
    }
    await loadProjectDetail(nextId);
  } catch {
    // errors surfaced via setError
  }
}

async function refreshCurrent() {
  if (selectedProjectId.value) {
    await loadProjectDetail(selectedProjectId.value);
  }
}

async function saveProjectFromModal() {
  if (!selectedProjectId.value) return;
  savingProject.value = true;
  try {
    await api.patch(`finance-projects/${selectedProjectId.value}/`, projectForm.value);
    await refreshCurrent();
    showProjectSettingsModal.value = false;
    setSuccess("Einstellungen gespeichert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Einstellungen konnten nicht gespeichert werden."));
  } finally {
    savingProject.value = false;
  }
}

async function saveIncome() {
  if (!selectedProjectId.value) return;
  const amount = toAmount(incomeInput.value);
  savingIncome.value = true;
  try {
    const existingEntry = incomeEntries.value[0];
    if (existingEntry) {
      await api.patch(`finance-entries/${existingEntry.id}/`, { amount });
    } else {
      await api.post("finance-entries/", {
        project: selectedProjectId.value,
        title: "Einnahmen",
        entry_type: "INCOME",
        frequency: "MONTHLY",
        amount,
        is_active: true,
      });
    }
    await refreshCurrent();
    setSuccess("Einnahmen gespeichert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Einnahmen konnten nicht gespeichert werden."));
  } finally {
    savingIncome.value = false;
  }
}

function openCreateSubscriptionModal() {
  editingEntryId.value = null;
  entryForm.value = buildEntryForm({ entry_type: "SUBSCRIPTION", frequency: "MONTHLY", category: "Abo" });
  showSubscriptionModal.value = true;
}

function editEntry(entry) {
  editingEntryId.value = entry.id;
  entryForm.value = buildEntryForm(entry);
  showSubscriptionModal.value = true;
}

function closeSubscriptionModal() {
  showSubscriptionModal.value = false;
  editingEntryId.value = null;
  entryForm.value = buildEntryForm();
}

async function saveEntry() {
  if (!selectedProjectId.value) return;
  savingEntry.value = true;
  try {
    const wasEditing = Boolean(editingEntryId.value);
    const payload = {
      project: selectedProjectId.value,
      title: entryForm.value.title,
      category: entryForm.value.category,
      entry_type: "SUBSCRIPTION",
      amount: toAmount(entryForm.value.amount),
      frequency: entryForm.value.frequency,
      notes: entryForm.value.notes,
      is_active: entryForm.value.is_active,
    };
    if (editingEntryId.value) {
      await api.patch(`finance-entries/${editingEntryId.value}/`, payload);
    } else {
      await api.post("finance-entries/", payload);
    }
    closeSubscriptionModal();
    await refreshCurrent();
    setSuccess(wasEditing ? "Abo gespeichert." : "Abo angelegt.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Abo konnte nicht gespeichert werden."));
  } finally {
    savingEntry.value = false;
  }
}

async function toggleEntry(entry) {
  try {
    await api.patch(`finance-entries/${entry.id}/`, { is_active: !entry.is_active });
    await refreshCurrent();
    setSuccess(entry.is_active ? "Abo pausiert." : "Abo aktiviert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Status konnte nicht geändert werden."));
  }
}

async function removeEntry(entry) {
  if (!window.confirm(`Abo "${entry.title}" wirklich löschen?`)) return;
  try {
    await api.delete(`finance-entries/${entry.id}/`);
    if (editingEntryId.value === entry.id) closeSubscriptionModal();
    await refreshCurrent();
    setSuccess(`Abo "${entry.title}" gelöscht.`);
  } catch (error) {
    setError(getApiErrorMessage(error, "Abo konnte nicht gelöscht werden."));
  }
}

watch(
  () => route.params.projectId,
  async (projectId, prev) => {
    const nextId = Number(projectId || 0);
    if (!nextId || nextId === Number(prev || 0)) return;
    try {
      await loadProjectDetail(nextId);
    } catch {
      await syncProjectSelection();
    }
  }
);

watch(
  () => selectedMonth.value,
  async (next, prev) => {
    if (next !== prev && selectedProjectId.value) {
      await loadProjectDetail(selectedProjectId.value);
    }
  }
);

onMounted(syncProjectSelection);
</script>

<style scoped>
.finance-tool {
  display: grid;
  gap: 16px;
}

.status-card {
  display: grid;
  gap: 12px;
  padding: 32px;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--card);
  text-align: center;
}

.topbar-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 18px 22px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--card);
  flex-wrap: wrap;
}

.topbar-meta {
  display: grid;
  gap: 2px;
}

.topbar-meta h1 {
  margin: 0;
  font-size: 22px;
}

.topbar-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--brand);
  font-weight: 700;
}

.feedback-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feedback-pill {
  padding: 10px 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  font-size: 14px;
  font-weight: 500;
}

.feedback-pill.error {
  background: color-mix(in srgb, var(--status-overdue) 12%, var(--surface));
  border-color: color-mix(in srgb, var(--status-overdue) 24%, var(--border));
  color: color-mix(in srgb, var(--status-overdue) 80%, var(--text));
}

.feedback-pill.success {
  background: color-mix(in srgb, var(--status-done) 12%, var(--surface));
  border-color: color-mix(in srgb, var(--status-done) 24%, var(--border));
  color: color-mix(in srgb, var(--status-done) 80%, var(--text));
}

.tab-nav {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tab-pill {
  padding: 9px 18px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}

.tab-pill:hover {
  background: var(--card);
}

.tab-pill.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
}

/* Overview */
.overview-page,
.subscriptions-page,
.debts-page {
  display: grid;
  gap: 16px;
}

.month-nav-bar {
  display: flex;
  align-items: center;
  gap: 12px;
}

.month-nav-btn {
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 10px;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 16px;
  color: var(--text);
}

.month-nav-btn:hover {
  background: var(--card);
}

.month-nav-label {
  font-weight: 600;
  font-size: 16px;
}

.panel {
  padding: 20px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--card);
  display: grid;
  gap: 14px;
}

.panel-head {
  display: grid;
  gap: 4px;
}

.panel-head h2 {
  margin: 0;
}

.panel-head-space {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.income-card {
  background: color-mix(in srgb, var(--brand) 6%, var(--card));
  border-color: color-mix(in srgb, var(--brand) 16%, var(--border));
}

.income-input-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.income-input {
  flex: 1;
  font-size: 18px;
  font-weight: 600;
}

/* Calculation */
.calc-rows {
  display: grid;
  gap: 10px;
}

.calc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 15px;
}

.calc-row strong {
  font-size: 16px;
}

.calc-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
}

.result-row {
  font-size: 17px;
  font-weight: 700;
}

.result-row strong {
  font-size: 20px;
}

.positive {
  color: color-mix(in srgb, var(--status-done) 80%, var(--text));
}

.negative {
  color: color-mix(in srgb, var(--status-overdue) 80%, var(--text));
}

/* Stats */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.stat-card {
  padding: 16px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  display: grid;
  gap: 6px;
}

.stat-label {
  font-size: 12px;
  color: var(--muted);
  font-weight: 500;
}

.stat-card strong {
  font-size: 18px;
}

/* Sub summary */
.sub-summary {
  display: flex;
  gap: 24px;
}

.sub-summary > div {
  display: grid;
  gap: 2px;
}

/* Entry list */
.entry-list {
  display: grid;
  gap: 10px;
}

.entry-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.entry-row.inactive {
  opacity: 0.55;
}

.entry-main {
  display: grid;
  gap: 4px;
  flex: 1;
}

.entry-side {
  display: grid;
  gap: 6px;
  text-align: right;
  flex-shrink: 0;
}

.entry-actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

.empty-state {
  display: grid;
  gap: 12px;
  padding: 24px;
  text-align: center;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.45);
  z-index: 50;
  padding: 16px;
}

.modal-content {
  width: min(560px, 100%);
  max-height: 90vh;
  overflow: auto;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--card);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 16px 18px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  border: none;
  background: transparent;
  color: inherit;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}

.modal-body {
  padding: 16px;
}

.stack-form {
  display: grid;
  gap: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.grid {
  display: grid;
  gap: 12px;
}

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.textarea {
  min-height: 80px;
  resize: vertical;
}

.toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.sm {
  padding: 6px 10px;
  font-size: 13px;
}

.danger {
  color: color-mix(in srgb, var(--status-overdue) 80%, var(--text));
}

@media (max-width: 600px) {
  .topbar-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .income-input-row {
    flex-direction: column;
    align-items: stretch;
  }

  .entry-row {
    flex-direction: column;
  }

  .entry-side {
    text-align: left;
  }

  .entry-actions {
    justify-content: flex-start;
  }

  .grid.two {
    grid-template-columns: 1fr;
  }

  .modal-actions {
    flex-direction: column;
  }
}
</style>
