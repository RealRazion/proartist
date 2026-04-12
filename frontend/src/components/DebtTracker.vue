<template>
  <div class="debt-tracker">
    <!-- Debt List Section -->
    <section class="card debts-section">
      <div class="section-head">
        <div>
          <h2>Schulden verwalten</h2>
          <p class="muted">Überwache deine Schulden und sehe den Fortschritt zu Abbezahlung.</p>
        </div>
        <button class="btn" type="button" @click="showAddDebtModal = true">
          + Schulde hinzufügen
        </button>
      </div>

      <div v-if="debts.length" class="debts-grid">
        <article v-for="debt in debts" :key="debt.id" class="debt-card">
          <div class="debt-header">
            <div>
              <h3>{{ debt.name }}</h3>
              <p class="muted small">Gestartet: {{ formatDate(debt.start_date) }}</p>
              <p class="muted small">{{ formatPaymentType(debt.payment_type) }}</p>
            </div>
            <span :class="['status-badge', `status-${debt.status.toLowerCase()}`]">
              {{ formatStatus(debt.status) }}
            </span>
          </div>

          <div class="debt-progress">
            <div class="progress-info">
              <span class="progress-label">Fortschritt</span>
              <span class="progress-percent">{{ debt.payment_percentage }}%</span>
            </div>
            <div class="progress-bar">
              <span :style="{ width: `${debt.payment_percentage}%` }"></span>
            </div>
          </div>

          <div class="debt-stats">
            <div class="stat">
              <span class="stat-label">Gesamtschuld</span>
              <strong>{{ formatCurrency(debt.total_amount) }}</strong>
            </div>
            <div class="stat">
              <span class="stat-label">Bezahlt</span>
              <strong>{{ formatCurrency(debt.amount_paid) }}</strong>
            </div>
            <div class="stat">
              <span class="stat-label">Rest</span>
              <strong :class="{ 'paid-off': debt.is_fully_paid }">
                {{ formatCurrency(debt.remaining_amount) }}
              </strong>
            </div>
            <div class="stat">
              <span class="stat-label">{{ debt.payment_type === 'INSTALLMENT' ? 'Monatliche Rate' : 'Fixbetrag faellig' }}</span>
              <strong>{{ formatCurrency(debt.scheduled_payment_amount) }}</strong>
            </div>
          </div>

          <p v-if="debt.payment_type === 'INSTALLMENT' && !debt.is_fully_paid && debt.months_remaining > 0" class="muted small">
            Noch ca. <strong>{{ debt.months_remaining }} Monat{{ debt.months_remaining !== 1 ? 'e' : '' }}</strong>
            bis zur Tilgung
          </p>
          <p v-else-if="debt.payment_type === 'FIXED_AMOUNT' && !debt.is_fully_paid" class="muted small">
            Offener Fixbetrag mit Faelligkeit ab {{ formatDate(debt.start_date) }}
          </p>
          <p v-else-if="debt.is_fully_paid" class="success-text small">
            ✓ Abbezahlt am {{ formatDate(debt.paid_off_date) }}
          </p>

          <div class="debt-actions">
            <button class="btn sm ghost" type="button" @click="editDebt(debt)">Bearbeiten</button>
            <button class="btn sm ghost" type="button" @click="showPaymentModal(debt)">Zahlung erfassen</button>
            <button class="btn sm ghost danger" type="button" @click="removeDebt(debt)">Löschen</button>
          </div>
        </article>
      </div>
      <p v-else class="muted empty-hint">Noch keine Schulden eingetragen. Prima! 🎉</p>
    </section>

    <!-- Monthly Breakdown -->
    <section v-if="debts.length" class="card monthly-section">
      <div class="section-head compact">
        <h2>Monatliche Übersicht</h2>
      </div>

      <div class="month-breakdown">
        <div v-for="month in nextMonthsBreakdown" :key="month.month" class="month-card">
          <h4>{{ formatMonthLabel(month.month) }}</h4>
          <p v-if="month.entries.length" class="breakdown-text">
            Noch <strong>{{ formatCurrency(month.remaining_total) }}</strong> Schulden
          </p>
          <ul v-if="month.entries.length" class="month-entries">
            <li v-for="entry in month.entries" :key="entry.debt_id" class="month-entry">
              <span>{{ entry.name }}: </span>
              <strong>{{ formatCurrency(entry.amount) }}</strong>
            </li>
          </ul>
          <p v-else class="muted small">Keine Zahlungen fällig</p>
        </div>
      </div>
    </section>

    <!-- Add/Edit Debt Modal -->
    <div v-if="showAddDebtModal" class="modal-overlay" @click="closeAddDebtModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingDebtId ? 'Schulde bearbeiten' : 'Neue Schulde hinzufügen' }}</h2>
          <button class="btn close-btn" type="button" @click="closeAddDebtModal">×</button>
        </div>

        <form class="modal-form" @submit.prevent="saveDebt">
          <label>
            Name (z.B. Klarna, Darlehen)
            <input v-model.trim="debtForm.name" class="input" required />
          </label>

          <label>
            Schuldentyp
            <select v-model="debtForm.payment_type" class="input">
              <option value="INSTALLMENT">Ratenzahlung</option>
              <option value="FIXED_AMOUNT">Fixbetrag</option>
            </select>
          </label>

          <div class="grid two">
            <label>
              Gesamtschuld
              <input
                v-model="debtForm.total_amount"
                class="input"
                type="number"
                step="0.01"
                min="0.01"
                required
              />
            </label>
            <label>
              Bereits bezahlt
              <input
                v-model="debtForm.amount_paid"
                class="input"
                type="number"
                step="0.01"
                min="0"
              />
            </label>
          </div>

          <div v-if="debtForm.payment_type === 'INSTALLMENT'" class="grid two">
            <label>
              Monatliche Rate
              <input
                v-model="debtForm.monthly_payment"
                class="input"
                type="number"
                step="0.01"
                min="0.01"
                required
              />
            </label>
            <label>
              Zahlungstag im Monat (1-31)
              <input v-model="debtForm.due_day" class="input" type="number" min="1" max="31" required />
            </label>
          </div>

          <p v-else class="muted small">
            Bei einem Fixbetrag wird keine monatliche Rate verlangt. Der offene Restbetrag ist ab dem Startdatum faellig.
          </p>

          <div class="grid two">
            <label>
              Startdatum
              <input v-model="debtForm.start_date" class="input" type="date" required />
            </label>
            <label>
              Status
              <select v-model="debtForm.status" class="input">
                <option value="ACTIVE">Aktiv</option>
                <option value="PAID_OFF">Abbezahlt</option>
                <option value="PAUSED">Pausiert</option>
              </select>
            </label>
          </div>

          <label>
            Notizen
            <textarea
              v-model.trim="debtForm.notes"
              class="input textarea"
              rows="2"
              placeholder="optional"
            ></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn" type="submit" :disabled="savingDebt">
              {{ savingDebt ? 'Speichere...' : editingDebtId ? 'Speichern' : 'Hinzufügen' }}
            </button>
            <button class="btn ghost" type="button" @click="closeAddDebtModal">Abbrechen</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Payment Recording Modal -->
    <div v-if="showPaymentRecordingModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Zahlung erfassen für {{ selectedDebtForPayment?.name }}</h2>
          <button class="btn close-btn" type="button" @click="closePaymentModal">×</button>
        </div>

        <form class="modal-form" @submit.prevent="recordPayment">
          <label>
            Zahlungsbetrag
            <input
              v-model="paymentForm.amount"
              class="input"
              type="number"
              step="0.01"
              min="0.01"
              required
            />
          </label>

          <label>
            Datum
            <input v-model="paymentForm.date" class="input" type="date" required />
          </label>

          <label>
            Notiz (optional)
            <textarea v-model.trim="paymentForm.notes" class="input textarea" rows="2"></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn" type="submit" :disabled="savingPayment">
              {{ savingPayment ? 'Speichere...' : 'Zahlung erfassen' }}
            </button>
            <button class="btn ghost" type="button" @click="closePaymentModal">Abbrechen</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Klarna Calculator Modal -->
    <div v-if="showKlarnaCalculator" class="modal-overlay" @click="closeKlarnaCalculator">
      <div class="modal-content klarna-calc" @click.stop>
        <div class="modal-header">
          <h2>Schuldenrechner</h2>
          <button class="btn close-btn" type="button" @click="closeKlarnaCalculator">×</button>
        </div>

        <div class="klarna-quick-entry">
          <p class="muted small">Gib Details ein und drücke Enter für schnelle Einträge</p>

          <div class="quick-entry-form">
            <input
              v-model.trim="klarnaQuickEntry.name"
              class="input quick-input"
              placeholder="Name (z.B. Klarna)"
              @keyup.enter="addKlarnaEntry"
            />
            <input
              v-model="klarnaQuickEntry.total_amount"
              class="input quick-input"
              type="number"
              step="0.01"
              placeholder="Gesamtbetrag"
              @keyup.enter="addKlarnaEntry"
            />
            <input
              v-model="klarnaQuickEntry.monthly_payment"
              class="input quick-input"
              type="number"
              step="0.01"
              placeholder="Monatliche Rate"
              @keyup.enter="addKlarnaEntry"
            />
            <input
              v-model="klarnaQuickEntry.due_day"
              class="input quick-input"
              type="number"
              min="1"
              max="31"
              placeholder="Zahlungstag"
              @keyup.enter="addKlarnaEntry"
            />
            <button class="btn" type="button" @click="addKlarnaEntry" :disabled="savingKlarna">
              {{ savingKlarna ? '...' : 'Hinzufügen' }}
            </button>
          </div>

          <div v-if="klarnaEntries.length" class="klarna-entries-list">
            <h4>Übersicht</h4>
            <table class="klarna-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Betrag</th>
                  <th>Rate</th>
                  <th>Monate</th>
                  <th>Aktion</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(entry, idx) in klarnaEntries" :key="idx">
                  <td>{{ entry.name }}</td>
                  <td>{{ formatCurrency(entry.total_amount) }}</td>
                  <td>{{ formatCurrency(entry.monthly_payment) }}</td>
                  <td>{{ calculateMonths(entry.total_amount, entry.monthly_payment) }}</td>
                  <td>
                    <button class="btn sm danger" type="button" @click="removeKlarnaEntry(idx)">
                      Entfernen
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>

            <div class="klarna-totals">
              <p>
                <strong>Gesamtschuld:</strong>
                {{ formatCurrency(klarnaEntries.reduce((sum, e) => sum + parseFloat(e.total_amount || 0), 0)) }}
              </p>
              <p>
                <strong>Gesamtrate/Monat:</strong>
                {{ formatCurrency(klarnaEntries.reduce((sum, e) => sum + parseFloat(e.monthly_payment || 0), 0)) }}
              </p>
            </div>

            <button class="btn primary" type="button" @click="saveAllKlarnaEntries">
              Alle hinzufügen
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Klarna Calculator Button -->
    <button class="btn klarna-calc-btn" type="button" @click="showKlarnaCalculator = true">
      🧮 Schuldenrechner
    </button>
  </div>
</template>

<script setup>
import { computed, ref, watch } from 'vue';
import api from '../api';

const props = defineProps({
  projectId: {
    type: Number,
    required: true,
  },
});

const debts = ref([]);
const loading = ref(false);
const savingDebt = ref(false);
const savingPayment = ref(false);
const savingKlarna = ref(false);

const showAddDebtModal = ref(false);
const showPaymentRecordingModal = ref(false);
const showKlarnaCalculator = ref(false);
const editingDebtId = ref(null);
const selectedDebtForPayment = ref(null);

const debtForm = ref(buildDebtForm());
const paymentForm = ref(buildPaymentForm());
const klarnaQuickEntry = ref(buildKlarnaQuickEntry());
const klarnaEntries = ref([]);

function buildDebtForm(data = {}) {
  return {
    name: data.name || '',
    payment_type: data.payment_type || 'INSTALLMENT',
    total_amount: data.total_amount ?? '',
    amount_paid: data.amount_paid ?? 0,
    monthly_payment: data.monthly_payment ?? '',
    due_day: data.due_day ?? '',
    status: data.status || 'ACTIVE',
    start_date: data.start_date || new Date().toISOString().split('T')[0],
    notes: data.notes || '',
  };
}

function buildPaymentForm() {
  return {
    amount: '',
    date: new Date().toISOString().split('T')[0],
    notes: '',
  };
}

function buildKlarnaQuickEntry() {
  return {
    name: '',
    payment_type: 'INSTALLMENT',
    total_amount: '',
    monthly_payment: '',
    due_day: '',
  };
}

const nextMonthsBreakdown = computed(() => {
  const months = [];
  const today = new Date();

  for (let i = 0; i < 6; i++) {
    const month = new Date(today.getFullYear(), today.getMonth() + i, 1);
    const monthStr = month.toISOString().slice(0, 7);

    const entries = [];
    let remaining_total = 0;

    debts.value
      .filter((debt) => !debt.is_fully_paid && debt.status === 'ACTIVE')
      .forEach((debt) => {
        const debtStartMonth = String(debt.start_date || '').slice(0, 7);
        const isInstallment = debt.payment_type === 'INSTALLMENT';
        const isDueThisMonth = isInstallment ? debtStartMonth <= monthStr : debtStartMonth === monthStr;

        if (!isDueThisMonth) {
          return;
        }

        entries.push({
          debt_id: debt.id,
          name: debt.name,
          amount: debt.scheduled_payment_amount,
        });
        remaining_total += parseFloat(debt.remaining_amount || 0);
      });

    months.push({
      month: monthStr,
      entries,
      remaining_total,
    });
  }

  return months;
});

function formatCurrency(value) {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR',
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatDate(value) {
  if (!value) return 'Kein Datum';
  return new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium' }).format(new Date(value));
}

function formatMonthLabel(monthStr) {
  const date = new Date(monthStr + '-01');
  return new Intl.DateTimeFormat('de-DE', { year: 'numeric', month: 'long' }).format(date);
}

function formatStatus(status) {
  const labels = {
    ACTIVE: 'Aktiv',
    PAID_OFF: 'Abbezahlt',
    PAUSED: 'Pausiert',
  };
  return labels[status] || status;
}

function formatPaymentType(paymentType) {
  const labels = {
    INSTALLMENT: 'Ratenzahlung',
    FIXED_AMOUNT: 'Fixbetrag',
  };
  return labels[paymentType] || paymentType;
}

function getApiErrorMessage(error, fallbackMessage) {
  const data = error?.response?.data;
  if (typeof data === 'string' && data.trim()) {
    return data;
  }
  if (data && typeof data === 'object') {
    const firstValue = Object.values(data)[0];
    if (Array.isArray(firstValue) && firstValue.length) {
      return String(firstValue[0]);
    }
    if (typeof firstValue === 'string' && firstValue.trim()) {
      return firstValue;
    }
  }
  return fallbackMessage;
}

function calculateMonths(amount, payment) {
  const a = parseFloat(amount || 0);
  const p = parseFloat(payment || 0);
  if (p <= 0) return 0;
  return Math.ceil(a / p);
}

async function loadDebts() {
  loading.value = true;
  try {
    const { data } = await api.get(`debts/?project=${props.projectId}`);
    debts.value = Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    debts.value = [];
    alert(getApiErrorMessage(error, 'Schulden konnten nicht geladen werden.'));
  } finally {
    loading.value = false;
  }
}

function editDebt(debt) {
  editingDebtId.value = debt.id;
  debtForm.value = buildDebtForm(debt);
  showAddDebtModal.value = true;
}

function closeAddDebtModal() {
  showAddDebtModal.value = false;
  editingDebtId.value = null;
  debtForm.value = buildDebtForm();
}

async function saveDebt() {
  const isInstallment = debtForm.value.payment_type === 'INSTALLMENT';
  if (
    !debtForm.value.name ||
    !debtForm.value.total_amount ||
    (isInstallment && (!debtForm.value.monthly_payment || !debtForm.value.due_day))
  ) {
    alert('Bitte alle erforderlichen Felder ausfuellen');
    return;
  }

  savingDebt.value = true;
  try {
    const payload = {
      ...debtForm.value,
      project: props.projectId,
      total_amount: parseFloat(debtForm.value.total_amount),
      amount_paid: parseFloat(debtForm.value.amount_paid || 0),
      monthly_payment: isInstallment ? parseFloat(debtForm.value.monthly_payment) : null,
      due_day: isInstallment ? parseInt(debtForm.value.due_day, 10) : null,
    };

    if (editingDebtId.value) {
      await api.patch(`debts/${editingDebtId.value}/`, payload);
    } else {
      await api.post('debts/', payload);
    }

    closeAddDebtModal();
    await loadDebts();
  } catch (error) {
    alert(getApiErrorMessage(error, 'Schuld konnte nicht gespeichert werden.'));
  } finally {
    savingDebt.value = false;
  }
}

async function removeDebt(debt) {
  if (!window.confirm(`Schulde "${debt.name}" wirklich löschen?`)) {
    return;
  }

  try {
    await api.delete(`debts/${debt.id}/`);
    await loadDebts();
  } catch (err) {
    alert(getApiErrorMessage(err, 'Fehler beim Loeschen'));
  }
}

function showPaymentModal(debt) {
  selectedDebtForPayment.value = debt;
  paymentForm.value = buildPaymentForm();
  showPaymentRecordingModal.value = true;
}

function closePaymentModal() {
  showPaymentRecordingModal.value = false;
  selectedDebtForPayment.value = null;
}

async function recordPayment() {
  if (!paymentForm.value.amount || !selectedDebtForPayment.value) {
    alert('Zahlungsbetrag erforderlich');
    return;
  }

  savingPayment.value = true;
  try {
    const debt = selectedDebtForPayment.value;
    const newAmountPaid = parseFloat(debt.amount_paid) + parseFloat(paymentForm.value.amount);

    await api.patch(`debts/${debt.id}/`, {
      amount_paid: Math.min(newAmountPaid, parseFloat(debt.total_amount)),
      status: newAmountPaid >= parseFloat(debt.total_amount) ? 'PAID_OFF' : 'ACTIVE',
      paid_off_date: newAmountPaid >= parseFloat(debt.total_amount) ? new Date().toISOString().split('T')[0] : null,
    });

    closePaymentModal();
    await loadDebts();
  } catch (error) {
    alert(getApiErrorMessage(error, 'Zahlung konnte nicht gespeichert werden.'));
  } finally {
    savingPayment.value = false;
  }
}

function closeKlarnaCalculator() {
  showKlarnaCalculator.value = false;
  klarnaEntries.value = [];
  klarnaQuickEntry.value = buildKlarnaQuickEntry();
}

function addKlarnaEntry() {
  const entry = klarnaQuickEntry.value;

  if (!entry.name || !entry.total_amount || !entry.monthly_payment || !entry.due_day) {
    alert('Bitte alle Felder ausfuellen');
    return;
  }

  klarnaEntries.value.push({
    ...entry,
    total_amount: parseFloat(entry.total_amount),
    monthly_payment: parseFloat(entry.monthly_payment),
    due_day: parseInt(entry.due_day, 10),
  });

  klarnaQuickEntry.value = buildKlarnaQuickEntry();
}

function removeKlarnaEntry(idx) {
  klarnaEntries.value.splice(idx, 1);
}

async function saveAllKlarnaEntries() {
  if (!klarnaEntries.value.length) {
    alert('Keine Eintraege zum Speichern');
    return;
  }

  savingKlarna.value = true;
  try {
    for (const entry of klarnaEntries.value) {
      await api.post('debts/', {
        ...entry,
        project: props.projectId,
        status: 'ACTIVE',
        start_date: new Date().toISOString().split('T')[0],
        amount_paid: 0,
      });
    }

    closeKlarnaCalculator();
    await loadDebts();
  } catch (error) {
    alert(getApiErrorMessage(error, 'Klarna-Eintraege konnten nicht gespeichert werden.'));
  } finally {
    savingKlarna.value = false;
  }
}

watch(
  () => props.projectId,
  (projectId) => {
    if (!projectId) {
      debts.value = [];
      return;
    }
    loadDebts();
  },
  { immediate: true }
);
</script>

<style scoped>
.debt-tracker {
  display: grid;
  gap: 18px;
}

.debts-section,
.monthly-section {
  display: grid;
  gap: 16px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 18px;
}

.section-head.compact {
  margin-bottom: 10px;
}

.debts-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}

.debt-card {
  display: grid;
  gap: 12px;
  padding: 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.debt-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.debt-header h3 {
  margin: 0;
  font-size: 16px;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 99px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
}

.status-badge.status-active {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.status-badge.status-paid_off {
  background: rgba(34, 197, 94, 0.12);
  color: #166534;
}

.status-badge.status-paused {
  background: rgba(245, 158, 11, 0.12);
  color: #b45309;
}

.debt-progress {
  display: grid;
  gap: 8px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.progress-label {
  color: var(--muted);
}

.progress-percent {
  font-weight: 600;
  color: var(--brand);
}

.progress-bar {
  height: 12px;
  border-radius: 99px;
  background: rgba(47, 99, 255, 0.1);
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  border-radius: inherit;
  transition: width 0.3s ease;
}

.debt-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  padding: 12px;
  background: rgba(47, 99, 255, 0.04);
  border-radius: 12px;
}

.stat {
  display: grid;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat strong {
  font-size: 14px;
}

.stat strong.paid-off {
  color: #16a34a;
}

.debt-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.debt-actions .btn {
  flex: 1;
  min-width: 100px;
}

.success-text {
  color: #16a34a;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  margin: 0;
}

/* Monthly Breakdown */
.month-breakdown {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.month-card {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.month-card h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.breakdown-text {
  font-size: 13px;
  margin: 0 0 8px 0;
}

.month-entries {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 4px;
}

.month-entry {
  font-size: 13px;
  display: flex;
  justify-content: space-between;
  gap: 8px;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
  backdrop-filter: blur(10px);
}

.modal-content {
  background: var(--modal-bg);
  border-radius: 16px;
  border: 1px solid var(--border);
  box-shadow: var(--modal-shadow);
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: grid;
  grid-template-rows: auto 1fr;
}

.modal-content.klarna-calc {
  max-width: 600px;
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.modal-header h2 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  padding: 4px 10px;
  font-size: 24px;
  line-height: 1;
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
}

.close-btn:hover {
  color: var(--text);
}

.modal-form {
  padding: 20px;
  display: grid;
  gap: 14px;
}

.grid {
  display: grid;
  gap: 12px;
}

.grid.two {
  grid-template-columns: repeat(2, 1fr);
}

.input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text);
  font-size: 14px;
}

.input:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 2px var(--brand-alpha);
}

.textarea {
  min-height: 80px;
  resize: vertical;
}

.modal-actions {
  display: flex;
  gap: 10px;
  padding: 16px 20px 20px;
}

.modal-actions .btn {
  flex: 1;
}

/* Klarna Calculator */
.klarna-quick-entry {
  padding: 20px;
  display: grid;
  gap: 16px;
}

.quick-entry-form {
  display: grid;
  gap: 8px;
}

.quick-input {
  padding: 10px 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--input-bg);
  color: var(--text);
  font-size: 14px;
}

.quick-input:focus {
  outline: none;
  border-color: var(--brand);
}

.klarna-entries-list {
  display: grid;
  gap: 12px;
}

.klarna-entries-list h4 {
  margin: 0;
  font-size: 14px;
}

.klarna-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.klarna-table th,
.klarna-table td {
  padding: 8px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.klarna-table th {
  font-weight: 600;
  background: rgba(47, 99, 255, 0.04);
}

.klarna-table td button {
  padding: 4px 8px;
  font-size: 12px;
}

.klarna-totals {
  padding: 10px;
  background: rgba(47, 99, 255, 0.04);
  border-radius: 8px;
  display: grid;
  gap: 4px;
}

.klarna-totals p {
  margin: 0;
  font-size: 13px;
}

/* Klarna Calculator Button */
.klarna-calc-btn {
  align-self: start;
  margin-top: 10px;
}

@media (max-width: 768px) {
  .debts-grid {
    grid-template-columns: 1fr;
  }

  .debt-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal-content {
    max-width: 100%;
  }

  .grid.two {
    grid-template-columns: 1fr;
  }

  .month-breakdown {
    grid-template-columns: 1fr;
  }
}

:global(.dark) .debt-tracker .input,
:global(.dark) .debt-tracker .quick-input {
  background: var(--input-bg);
}

:global(.dark) .debt-tracker .input:focus,
:global(.dark) .debt-tracker .quick-input:focus {
  background: var(--input-bg-focus);
}
</style>
