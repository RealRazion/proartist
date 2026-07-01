<template>
  <div class="finance-tool">
    <!-- Loading state -->
    <section v-if="loading && !project" class="status-card">
      <p class="muted">Lade Finanzplaner...</p>
    </section>

    <!-- No project state -->
    <section v-else-if="!projects.length" class="status-card">
      <h2>Kein Finanzprojekt vorhanden</h2>
      <p class="muted">Lege zuerst ein Finanzprojekt an.</p>
      <button class="btn" type="button" @click="router.push({ name: 'platform-finance' })">Zum Einstieg</button>
    </section>

    <!-- Main interface -->
    <template v-else>
      <header class="topbar">
        <div class="topbar-left">
          <p class="eyebrow">Finanzplaner</p>
          <h1>{{ project?.title || "Finanzprojekt" }}</h1>
        </div>
        <button class="btn ghost sm" type="button" @click="router.push({ name: 'platform-finance' })">← Übersicht</button>
      </header>

      <!-- Feedback -->
      <section v-if="errorMessage || successMessage" class="feedback-bar">
        <div v-if="errorMessage" class="feedback-pill error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="feedback-pill success">{{ successMessage }}</div>
      </section>

      <!-- Tab navigation -->
      <nav class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab.id"
          class="tab-pill"
          :class="{ active: activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.label }}
        </button>
      </nav>

      <!-- ===== ÜBERSICHT ===== -->
      <section v-show="activeTab === 'overview'" class="tab-content">
        <!-- Summary banner -->
        <article class="summary-banner">
          <div class="summary-row">
            <span class="summary-label">Einnahmen</span>
            <span class="summary-amount income">{{ fmt(totalIncome) }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">− Schulden</span>
            <span class="summary-amount">{{ fmt(totalDebtPayments) }}</span>
          </div>
          <div class="summary-row">
            <span class="summary-label">− Abos</span>
            <span class="summary-amount">{{ fmt(totalSubscriptions) }}</span>
          </div>
          <div class="summary-divider"></div>
          <div class="summary-row highlight">
            <span class="summary-label">Verbleibend</span>
            <span class="summary-amount" :class="remaining >= 0 ? 'income' : 'danger'">{{ fmt(remaining) }}</span>
          </div>
        </article>

        <!-- Income entries -->
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Einnahmen</h2>
              <p class="muted small">Monatliche Einkommensquellen</p>
            </div>
            <button class="btn ghost sm" type="button" @click="openIncomeModal()">+ Hinzufügen</button>
          </div>

          <div v-if="incomeEntries.length" class="entry-list">
            <div v-for="entry in incomeEntries" :key="entry.id" class="entry-row">
              <div class="entry-info">
                <strong>{{ entry.title }}</strong>
              </div>
              <div class="entry-right">
                <span class="amount">{{ fmt(entry.monthly_amount || entry.amount) }}</span>
                <button class="icon-btn" title="Bearbeiten" @click="openIncomeModal(entry)">✎</button>
                <button class="icon-btn danger" title="Löschen" @click="deleteIncome(entry)">✕</button>
              </div>
            </div>
          </div>
          <p v-else class="muted small empty-hint">Noch keine Einnahmen eingetragen.</p>
        </article>
      </section>

      <!-- ===== SCHULDEN ===== -->
      <section v-show="activeTab === 'debts'" class="tab-content">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Schulden</h2>
              <p class="muted small">Aktive Schulden und Ratenzahlungen</p>
            </div>
            <button class="btn ghost sm" type="button" @click="openDebtModal()">+ Schuld hinzufügen</button>
          </div>

          <div v-if="debts.length" class="entry-list">
            <div v-for="debt in debts" :key="debt.id" class="debt-row" :class="{ 'paid-off': debt.is_fully_paid }">
              <div class="debt-main">
                <div class="debt-title-line">
                  <strong>{{ debt.name }}</strong>
                  <span class="badge" :class="debt.status === 'PAID_OFF' ? 'badge-done' : debt.status === 'PAUSED' ? 'badge-paused' : 'badge-active'">
                    {{ debtStatusLabel(debt.status) }}
                  </span>
                </div>
                <div class="debt-meta">
                  <span>Gesamt: {{ fmt(debt.total_amount) }}</span>
                  <span>Bezahlt: {{ fmt(debt.amount_paid) }}</span>
                  <span>Restschuld: {{ fmt(debt.remaining_amount) }}</span>
                </div>
                <div class="progress-bar-wrap">
                  <div class="progress-bar" :style="{ width: debtProgress(debt) + '%' }"></div>
                </div>
              </div>
              <div class="debt-right">
                <div class="debt-rate">
                  <span class="muted small">Monatlich</span>
                  <strong>{{ fmt(debt.monthly_payment) }}</strong>
                </div>
                <div class="debt-actions">
                  <button class="icon-btn" title="Bearbeiten" @click="openDebtModal(debt)">✎</button>
                  <button class="icon-btn danger" title="Löschen" @click="deleteDebt(debt)">✕</button>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="muted small empty-hint">Noch keine Schulden eingetragen.</p>

          <!-- Debt total -->
          <div v-if="debts.length" class="section-total">
            <span>Monatliche Schuldenrate gesamt</span>
            <strong>{{ fmt(totalDebtPayments) }}</strong>
          </div>
        </article>
      </section>

      <!-- ===== ABOS ===== -->
      <section v-show="activeTab === 'subscriptions'" class="tab-content">
        <article class="panel">
          <div class="panel-head">
            <div>
              <h2>Abos</h2>
              <p class="muted small">Laufende monatliche Abonnements</p>
            </div>
            <button class="btn ghost sm" type="button" @click="openSubModal()">+ Abo hinzufügen</button>
          </div>

          <div v-if="subscriptions.length" class="entry-list">
            <div v-for="sub in subscriptions" :key="sub.id" class="entry-row">
              <div class="entry-info">
                <strong>{{ sub.title }}</strong>
                <span v-if="sub.notes" class="muted small">{{ sub.notes }}</span>
              </div>
              <div class="entry-right">
                <span class="amount">{{ fmt(sub.monthly_amount || sub.amount) }}</span>
                <button class="icon-btn" title="Bearbeiten" @click="openSubModal(sub)">✎</button>
                <button class="icon-btn danger" title="Löschen" @click="deleteSub(sub)">✕</button>
              </div>
            </div>
          </div>
          <p v-else class="muted small empty-hint">Noch keine Abos eingetragen.</p>

          <!-- Subscription total -->
          <div v-if="subscriptions.length" class="section-total">
            <span>Abos gesamt pro Monat</span>
            <strong>{{ fmt(totalSubscriptions) }}</strong>
          </div>
        </article>
      </section>
    </template>

    <!-- ===== INCOME MODAL ===== -->
    <div v-if="showIncomeModal" class="modal-overlay" @click.self="showIncomeModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ incomeForm.id ? 'Einnahme bearbeiten' : 'Einnahme hinzufügen' }}</h3>
          <button class="modal-close" @click="showIncomeModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="saveIncome">
          <label>
            Bezeichnung
            <input v-model.trim="incomeForm.title" class="input" placeholder="z. B. Gehalt, Freelance" required />
          </label>
          <label>
            Monatlicher Betrag (€)
            <input v-model="incomeForm.amount" class="input" type="number" step="0.01" min="0" placeholder="0.00" required />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showIncomeModal = false">Abbrechen</button>
            <button class="btn" type="submit" :disabled="saving">{{ saving ? 'Speichern...' : 'Speichern' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== DEBT MODAL ===== -->
    <div v-if="showDebtModal" class="modal-overlay" @click.self="showDebtModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ debtForm.id ? 'Schuld bearbeiten' : 'Schuld hinzufügen' }}</h3>
          <button class="modal-close" @click="showDebtModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="saveDebt">
          <label>
            Bezeichnung
            <input v-model.trim="debtForm.name" class="input" placeholder="z. B. Klarna, Darlehen" required />
          </label>
          <div class="form-grid">
            <label>
              Gesamtbetrag (€)
              <input v-model="debtForm.total_amount" class="input" type="number" step="0.01" min="0" placeholder="0.00" required />
            </label>
            <label>
              Bereits bezahlt (€)
              <input v-model="debtForm.amount_paid" class="input" type="number" step="0.01" min="0" placeholder="0.00" />
            </label>
          </div>
          <label>
            Monatliche Rate (€)
            <input v-model="debtForm.monthly_payment" class="input" type="number" step="0.01" min="0" placeholder="0.00" />
          </label>
          <label>
            Status
            <select v-model="debtForm.status" class="input">
              <option value="ACTIVE">Aktiv</option>
              <option value="PAUSED">Pausiert</option>
              <option value="PAID_OFF">Abbezahlt</option>
            </select>
          </label>
          <label>
            Notiz
            <textarea v-model="debtForm.notes" class="input textarea" rows="2" placeholder="Optional"></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showDebtModal = false">Abbrechen</button>
            <button class="btn" type="submit" :disabled="saving">{{ saving ? 'Speichern...' : 'Speichern' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== SUBSCRIPTION MODAL ===== -->
    <div v-if="showSubModal" class="modal-overlay" @click.self="showSubModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ subForm.id ? 'Abo bearbeiten' : 'Abo hinzufügen' }}</h3>
          <button class="modal-close" @click="showSubModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="saveSub">
          <label>
            Bezeichnung
            <input v-model.trim="subForm.title" class="input" placeholder="z. B. Netflix, Spotify" required />
          </label>
          <label>
            Monatlicher Betrag (€)
            <input v-model="subForm.amount" class="input" type="number" step="0.01" min="0" placeholder="0.00" required />
          </label>
          <label>
            Notiz
            <textarea v-model="subForm.notes" class="input textarea" rows="2" placeholder="Optional"></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showSubModal = false">Abbrechen</button>
            <button class="btn" type="submit" :disabled="saving">{{ saving ? 'Speichern...' : 'Speichern' }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const route = useRoute();
const router = useRouter();

// ── State ──────────────────────────────────────────────────────────────────
const loading = ref(false);
const saving = ref(false);
const projects = ref([]);
const project = ref(null);
const incomeEntries = ref([]);
const subscriptions = ref([]);
const debts = ref([]);
const errorMessage = ref("");
const successMessage = ref("");

const activeTab = ref("overview");
const tabs = [
  { id: "overview", label: "Übersicht" },
  { id: "debts", label: "Schulden" },
  { id: "subscriptions", label: "Abos" },
];

// ── Modal state ────────────────────────────────────────────────────────────
const showIncomeModal = ref(false);
const incomeForm = ref({ id: null, title: "", amount: "" });

const showDebtModal = ref(false);
const debtForm = ref({ id: null, name: "", total_amount: "", amount_paid: "0", monthly_payment: "", status: "ACTIVE", notes: "" });

const showSubModal = ref(false);
const subForm = ref({ id: null, title: "", amount: "", notes: "" });

// ── Computed ───────────────────────────────────────────────────────────────
const totalIncome = computed(() =>
  incomeEntries.value.reduce((sum, e) => sum + Number(e.monthly_amount || e.amount || 0), 0)
);

const totalDebtPayments = computed(() =>
  debts.value
    .filter((d) => d.status === "ACTIVE" && !d.is_fully_paid)
    .reduce((sum, d) => sum + Number(d.monthly_payment || 0), 0)
);

const totalSubscriptions = computed(() =>
  subscriptions.value.reduce((sum, s) => sum + Number(s.monthly_amount || s.amount || 0), 0)
);

const remaining = computed(() => totalIncome.value - totalDebtPayments.value - totalSubscriptions.value);

const currency = computed(() => project.value?.currency || "EUR");

// ── Helpers ────────────────────────────────────────────────────────────────
function fmt(value) {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: currency.value,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function toAmount(value) {
  const n = Number.parseFloat(value);
  return Number.isFinite(n) ? n : 0;
}

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}

function debtProgress(debt) {
  const total = Number(debt.total_amount || 0);
  if (total <= 0) return 0;
  return Math.min(100, Math.round((Number(debt.amount_paid || 0) / total) * 100));
}

function debtStatusLabel(status) {
  return { ACTIVE: "Aktiv", PAID_OFF: "Abbezahlt", PAUSED: "Pausiert" }[status] || status;
}

function setError(msg) {
  errorMessage.value = msg;
  successMessage.value = "";
}

function setSuccess(msg) {
  successMessage.value = msg;
  errorMessage.value = "";
  setTimeout(() => { successMessage.value = ""; }, 3000);
}

function apiError(err, fallback) {
  const d = err?.response?.data;
  if (typeof d === "string" && d.trim()) return d;
  if (d?.detail) return d.detail;
  if (d && typeof d === "object") {
    const msg = Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join(" | ");
    if (msg) return msg;
  }
  return fallback;
}

function normalise(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

// ── Data loading ───────────────────────────────────────────────────────────
async function loadProjects() {
  try {
    const { data } = await api.get("finance-projects/");
    projects.value = normalise(data);
  } catch {
    projects.value = [];
  }
}

async function loadProject(id) {
  try {
    const { data } = await api.get(`finance-projects/${id}/`);
    project.value = data;
  } catch (err) {
    setError(apiError(err, "Projekt konnte nicht geladen werden."));
  }
}

async function loadEntries(projectId) {
  try {
    const { data } = await api.get(`finance-entries/?project=${projectId}&active=false`);
    const all = normalise(data);
    incomeEntries.value = all.filter((e) => e.entry_type === "INCOME" && e.is_active);
    subscriptions.value = all.filter((e) => e.entry_type === "SUBSCRIPTION" && e.is_active);
  } catch {
    incomeEntries.value = [];
    subscriptions.value = [];
  }
}

async function loadDebts(projectId) {
  try {
    const { data } = await api.get(`debts/?project=${projectId}`);
    debts.value = normalise(data);
  } catch {
    debts.value = [];
  }
}

async function loadAll(projectId) {
  loading.value = true;
  try {
    await Promise.all([loadProject(projectId), loadEntries(projectId), loadDebts(projectId)]);
  } finally {
    loading.value = false;
  }
}

// ── Income CRUD ────────────────────────────────────────────────────────────
function openIncomeModal(entry = null) {
  if (entry) {
    incomeForm.value = { id: entry.id, title: entry.title, amount: entry.amount };
  } else {
    incomeForm.value = { id: null, title: "", amount: "" };
  }
  errorMessage.value = "";
  showIncomeModal.value = true;
}

async function saveIncome() {
  if (!project.value) return;
  saving.value = true;
  try {
    const payload = {
      project: project.value.id,
      title: incomeForm.value.title,
      entry_type: "INCOME",
      amount: toAmount(incomeForm.value.amount),
      frequency: "MONTHLY",
    };
    if (incomeForm.value.id) {
      await api.patch(`finance-entries/${incomeForm.value.id}/`, payload);
    } else {
      await api.post("finance-entries/", payload);
    }
    showIncomeModal.value = false;
    setSuccess("Einnahme gespeichert.");
    await loadEntries(project.value.id);
  } catch (err) {
    setError(apiError(err, "Einnahme konnte nicht gespeichert werden."));
  } finally {
    saving.value = false;
  }
}

async function deleteIncome(entry) {
  if (!confirm(`Einnahme "${entry.title}" löschen?`)) return;
  try {
    await api.delete(`finance-entries/${entry.id}/`);
    setSuccess("Einnahme gelöscht.");
    await loadEntries(project.value.id);
  } catch (err) {
    setError(apiError(err, "Einnahme konnte nicht gelöscht werden."));
  }
}

// ── Debt CRUD ──────────────────────────────────────────────────────────────
function openDebtModal(debt = null) {
  if (debt) {
    debtForm.value = {
      id: debt.id,
      name: debt.name,
      total_amount: debt.total_amount,
      amount_paid: debt.amount_paid,
      monthly_payment: debt.monthly_payment || "",
      status: debt.status,
      notes: debt.notes || "",
    };
  } else {
    debtForm.value = { id: null, name: "", total_amount: "", amount_paid: "0", monthly_payment: "", status: "ACTIVE", notes: "" };
  }
  errorMessage.value = "";
  showDebtModal.value = true;
}

async function saveDebt() {
  if (!project.value) return;
  saving.value = true;
  try {
    const payload = {
      project: project.value.id,
      name: debtForm.value.name,
      total_amount: toAmount(debtForm.value.total_amount),
      amount_paid: toAmount(debtForm.value.amount_paid),
      monthly_payment: debtForm.value.monthly_payment !== "" ? toAmount(debtForm.value.monthly_payment) : null,
      status: debtForm.value.status,
      notes: debtForm.value.notes,
      start_date: todayStr(),
      debt_kind: "DEBT",
      payment_type: "INSTALLMENT",
    };
    if (debtForm.value.id) {
      await api.patch(`debts/${debtForm.value.id}/`, payload);
    } else {
      await api.post("debts/", payload);
    }
    showDebtModal.value = false;
    setSuccess("Schuld gespeichert.");
    await loadDebts(project.value.id);
  } catch (err) {
    setError(apiError(err, "Schuld konnte nicht gespeichert werden."));
  } finally {
    saving.value = false;
  }
}

async function deleteDebt(debt) {
  if (!confirm(`Schuld "${debt.name}" löschen?`)) return;
  try {
    await api.delete(`debts/${debt.id}/`);
    setSuccess("Schuld gelöscht.");
    await loadDebts(project.value.id);
  } catch (err) {
    setError(apiError(err, "Schuld konnte nicht gelöscht werden."));
  }
}

// ── Subscription CRUD ──────────────────────────────────────────────────────
function openSubModal(sub = null) {
  if (sub) {
    subForm.value = { id: sub.id, title: sub.title, amount: sub.amount, notes: sub.notes || "" };
  } else {
    subForm.value = { id: null, title: "", amount: "", notes: "" };
  }
  errorMessage.value = "";
  showSubModal.value = true;
}

async function saveSub() {
  if (!project.value) return;
  saving.value = true;
  try {
    const payload = {
      project: project.value.id,
      title: subForm.value.title,
      entry_type: "SUBSCRIPTION",
      amount: toAmount(subForm.value.amount),
      frequency: "MONTHLY",
      notes: subForm.value.notes,
    };
    if (subForm.value.id) {
      await api.patch(`finance-entries/${subForm.value.id}/`, payload);
    } else {
      await api.post("finance-entries/", payload);
    }
    showSubModal.value = false;
    setSuccess("Abo gespeichert.");
    await loadEntries(project.value.id);
  } catch (err) {
    setError(apiError(err, "Abo konnte nicht gespeichert werden."));
  } finally {
    saving.value = false;
  }
}

async function deleteSub(sub) {
  if (!confirm(`Abo "${sub.title}" löschen?`)) return;
  try {
    await api.delete(`finance-entries/${sub.id}/`);
    setSuccess("Abo gelöscht.");
    await loadEntries(project.value.id);
  } catch (err) {
    setError(apiError(err, "Abo konnte nicht gelöscht werden."));
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
onMounted(async () => {
  await loadProjects();
  if (!projects.value.length) return;

  const routeId = Number(route.params.projectId || 0);
  const targetId =
    projects.value.some((p) => p.id === routeId)
      ? routeId
      : projects.value[0].id;

  if (!routeId || routeId !== targetId) {
    await router.replace({ name: "finance", params: { projectId: targetId } });
  }

  await loadAll(targetId);
});
</script>

<style scoped>
.finance-tool {
  display: grid;
  gap: 16px;
  --clr-income: #22c55e;
  --clr-danger: #ef4444;
  --clr-progress: var(--brand, #2f63ff);
}

/* ── Status card ── */
.status-card {
  display: grid;
  gap: 12px;
  justify-items: center;
  text-align: center;
  padding: 48px 24px;
  background: var(--card);
  border-radius: 18px;
  border: 1px solid var(--border);
}

/* ── Topbar ── */
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  padding: 18px 20px;
  background: var(--card);
  border-radius: 18px;
  border: 1px solid var(--border);
}

.topbar-left {
  display: grid;
  gap: 4px;
}

.topbar-left h1 {
  margin: 0;
  font-size: 1.4rem;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--brand, #2f63ff);
  font-weight: 700;
}

/* ── Feedback ── */
.feedback-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feedback-pill {
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.feedback-pill.error {
  background: color-mix(in srgb, var(--clr-danger) 12%, var(--surface));
  border-color: color-mix(in srgb, var(--clr-danger) 24%, var(--border));
  color: color-mix(in srgb, var(--clr-danger) 70%, var(--text));
}

.feedback-pill.success {
  background: color-mix(in srgb, var(--clr-income) 12%, var(--surface));
  border-color: color-mix(in srgb, var(--clr-income) 24%, var(--border));
  color: color-mix(in srgb, var(--clr-income) 70%, var(--text));
}

/* ── Tabs ── */
.tab-nav {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tab-pill {
  padding: 10px 20px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  cursor: pointer;
  font-weight: 600;
  font-size: 14px;
  color: var(--text);
  transition: background 0.15s, border-color 0.15s;
}

.tab-pill:hover {
  background: var(--card);
}

.tab-pill.active {
  background: var(--brand, #2f63ff);
  border-color: var(--brand, #2f63ff);
  color: #fff;
}

/* ── Tab content ── */
.tab-content {
  display: grid;
  gap: 16px;
}

/* ── Summary banner ── */
.summary-banner {
  display: grid;
  gap: 12px;
  padding: 22px 24px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--card);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.summary-label {
  font-size: 15px;
  color: var(--muted);
}

.summary-amount {
  font-size: 18px;
  font-weight: 700;
}

.summary-amount.income {
  color: var(--clr-income);
}

.summary-amount.danger {
  color: var(--clr-danger);
}

.summary-divider {
  height: 1px;
  background: var(--border);
  margin: 4px 0;
}

.summary-row.highlight .summary-label {
  font-size: 16px;
  font-weight: 600;
  color: var(--text);
}

.summary-row.highlight .summary-amount {
  font-size: 22px;
}

/* ── Panel ── */
.panel {
  display: grid;
  gap: 16px;
  padding: 20px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--card);
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.panel-head h2 {
  margin: 0;
}

/* ── Entry list ── */
.entry-list {
  display: grid;
  gap: 8px;
}

.entry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.entry-info {
  display: grid;
  gap: 2px;
}

.entry-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.amount {
  font-weight: 700;
  font-size: 15px;
}

/* ── Debt row ── */
.debt-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.debt-row.paid-off {
  opacity: 0.6;
}

.debt-main {
  flex: 1;
  display: grid;
  gap: 6px;
  min-width: 0;
}

.debt-title-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.debt-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
  color: var(--muted);
}

.progress-bar-wrap {
  height: 6px;
  border-radius: 999px;
  background: var(--border);
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  border-radius: 999px;
  background: var(--clr-progress);
  transition: width 0.3s ease;
}

.debt-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.debt-rate {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.debt-actions {
  display: flex;
  gap: 4px;
}

/* ── Section total ── */
.section-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-size: 14px;
  font-weight: 600;
}

/* ── Badges ── */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.badge-active {
  background: color-mix(in srgb, var(--brand, #2f63ff) 14%, var(--surface));
  color: var(--brand, #2f63ff);
}

.badge-done {
  background: color-mix(in srgb, var(--clr-income) 14%, var(--surface));
  color: var(--clr-income);
}

.badge-paused {
  background: color-mix(in srgb, #f59e0b 14%, var(--surface));
  color: #f59e0b;
}

/* ── Icon buttons ── */
.icon-btn {
  padding: 5px 8px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  color: var(--muted);
  line-height: 1;
  transition: background 0.15s, color 0.15s;
}

.icon-btn:hover {
  background: var(--card);
  color: var(--text);
}

.icon-btn.danger:hover {
  background: color-mix(in srgb, var(--clr-danger) 12%, var(--surface));
  color: var(--clr-danger);
  border-color: color-mix(in srgb, var(--clr-danger) 26%, var(--border));
}

/* ── Modals ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.5);
  z-index: 50;
  padding: 16px;
}

.modal-box {
  width: min(480px, 100%);
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
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  border: none;
  background: transparent;
  font-size: 22px;
  cursor: pointer;
  color: var(--muted);
  line-height: 1;
  padding: 2px 6px;
}

.modal-form {
  display: grid;
  gap: 14px;
  padding: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.textarea {
  min-height: 70px;
  resize: vertical;
}

.empty-hint {
  padding: 8px 0;
}

/* ── Misc ── */
.small { font-size: 13px; }

.sm {
  padding: 8px 14px;
  font-size: 14px;
}

@media (max-width: 600px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .debt-row {
    flex-direction: column;
  }

  .debt-right {
    align-items: flex-start;
    flex-direction: row;
    flex-wrap: wrap;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .summary-amount {
    font-size: 16px;
  }

  .summary-row.highlight .summary-amount {
    font-size: 20px;
  }
}
</style>
