<template>
  <div class="debt-tracker">
    <section v-if="actionableDebts.length" class="card due-section">
      <div class="section-head compact">
        <div>
          <h2>Jetzt pruefen</h2>
          <p class="muted">Faellige und ueberfaellige Schulden brauchen eine Rueckmeldung.</p>
        </div>
      </div>

      <div class="due-list">
        <article
          v-for="debt in actionableDebts"
          :key="`due-${debt.id}`"
          :class="['due-item', `due-${getDueState(debt).toLowerCase()}`]"
        >
          <div class="due-copy">
            <strong>{{ debt.name }}</strong>
            <p class="muted small">{{ getDueHeadline(debt) }}</p>
          </div>
          <button class="btn sm" type="button" @click="showPaymentModal(debt)">Bezahlt?</button>
        </article>
      </div>
    </section>

    <section class="card debts-section">
      <div class="section-head">
        <div>
          <h2>Schulden verwalten</h2>
          <p class="muted">
            Einfacher Ueberblick mit Restschuld, naechster Faelligkeit und klarer Aktion.
          </p>
        </div>
        <div class="section-actions">
          <button class="btn ghost" type="button" @click="showKlarnaCalculator = true">
            Schuldenrechner
          </button>
          <button class="btn" type="button" @click="showAddDebtModal = true">
            + Schuld hinzufuegen
          </button>
        </div>
      </div>

      <div v-if="debts.length" class="debts-grid">
        <article
          v-for="debt in debts"
          :key="debt.id"
          :class="['debt-card', `debt-${getDueState(debt).toLowerCase()}`]"
        >
          <div class="debt-header">
            <div>
              <h3>{{ debt.name }}</h3>
              <p class="muted small">Gestartet: {{ formatDate(debt.start_date) }}</p>
              <p class="muted small">{{ formatPaymentType(debt.payment_type) }}</p>
            </div>
            <div class="debt-badges">
              <span :class="['status-badge', `status-${debt.status.toLowerCase()}`]">
                {{ formatStatus(debt.status) }}
              </span>
              <span :class="['due-badge', `due-${getDueState(debt).toLowerCase()}`]">
                {{ getDueLabel(debt) }}
              </span>
            </div>
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
              <span class="stat-label">{{ paymentAmountLabel(debt) }}</span>
              <strong>{{ formatCurrency(debt.scheduled_payment_amount) }}</strong>
            </div>
          </div>

          <div class="debt-meta">
            <p class="muted small">{{ getDueHeadline(debt) }}</p>
            <p
              v-if="debt.payment_type === 'INSTALLMENT' && !debt.is_fully_paid && debt.months_remaining > 0"
              class="muted small"
            >
              Noch ca. <strong>{{ debt.months_remaining }} Monat{{ debt.months_remaining !== 1 ? 'e' : '' }}</strong>
              bis zur Tilgung
            </p>
            <p v-else-if="debt.is_fully_paid" class="success-text small">
              Abbezahlt am {{ formatDate(debt.paid_off_date) }}
            </p>
          </div>

          <div class="debt-actions">
            <button class="btn sm ghost" type="button" @click="editDebt(debt)">Bearbeiten</button>
            <button
              v-if="debt.status === 'ACTIVE' && !debt.is_fully_paid"
              class="btn sm ghost"
              type="button"
              @click="showPaymentModal(debt)"
            >
              {{ getDueState(debt) === 'UPCOMING' ? 'Zahlung planen' : 'Bezahlt?' }}
            </button>
            <button class="btn sm ghost danger" type="button" @click="removeDebt(debt)">Loeschen</button>
          </div>
        </article>
      </div>
      <p v-else class="muted empty-hint">Noch keine Schulden eingetragen.</p>
    </section>

    <section v-if="debts.length" class="card monthly-section">
      <div class="section-head compact">
        <div>
          <h2>Monatsprognose</h2>
          <p class="muted">Die Prognose zieht jede faellige Rate von der Restschuld ab.</p>
        </div>
      </div>

      <div class="month-breakdown">
        <div v-for="month in nextMonthsBreakdown" :key="month.month" class="month-card">
          <h4>{{ formatMonthLabel(month.month) }}</h4>
          <template v-if="month.entries.length">
            <p class="month-kpi">
              <span>Faellig in dem Monat</span>
              <strong>{{ formatCurrency(month.amount_due_total) }}</strong>
            </p>
            <p class="month-kpi">
              <span>Danach noch offen</span>
              <strong>{{ formatCurrency(month.remaining_total_after) }}</strong>
            </p>

            <ul class="month-entries">
              <li v-for="entry in month.entries" :key="entry.entry_id" class="month-entry">
                <div>
                  <span>{{ entry.name }}</span>
                  <p class="muted tiny">Faellig: {{ formatDate(entry.due_date) }}</p>
                </div>
                <div class="month-entry-values">
                  <strong>{{ formatCurrency(entry.amount) }}</strong>
                  <span class="muted tiny">Rest danach: {{ formatCurrency(entry.remaining_after) }}</span>
                </div>
              </li>
            </ul>
          </template>
          <p v-else class="muted small">Keine Zahlungen eingeplant.</p>
        </div>
      </div>
    </section>

    <div v-if="showAddDebtModal" class="modal-overlay" @click="closeAddDebtModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ editingDebtId ? 'Schuld bearbeiten' : 'Neue Schuld hinzufuegen' }}</h2>
          <button class="btn close-btn" type="button" @click="closeAddDebtModal">x</button>
        </div>

        <form class="modal-form" @submit.prevent="saveDebt">
          <label>
            Name
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
              Zahlungstag im Monat
              <input v-model="debtForm.due_day" class="input" type="number" min="1" max="31" required />
            </label>
          </div>

          <p v-else class="muted small">
            Ein Fixbetrag ist komplett ab seinem Faelligkeitstermin offen.
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
              {{ savingDebt ? 'Speichere...' : editingDebtId ? 'Speichern' : 'Hinzufuegen' }}
            </button>
            <button class="btn ghost" type="button" @click="closeAddDebtModal">Abbrechen</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showPaymentRecordingModal" class="modal-overlay" @click="closePaymentModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>Faelligkeit pruefen: {{ selectedDebtForPayment?.name }}</h2>
          <button class="btn close-btn" type="button" @click="closePaymentModal">x</button>
        </div>

        <form class="modal-form" @submit.prevent="recordPayment">
          <div v-if="selectedDebtForPayment" class="decision-summary">
            <p class="decision-kpi">
              <span>Aktuell faellig</span>
              <strong>{{ formatCurrency(selectedDebtForPayment.scheduled_payment_amount) }}</strong>
            </p>
            <p class="decision-kpi">
              <span>Faelligkeit</span>
              <strong>{{ formatDate(getNextDueDate(selectedDebtForPayment)) }}</strong>
            </p>
          </div>

          <label>
            Wurde das bezahlt?
            <select v-model="paymentForm.decision" class="input">
              <option value="paid">Ja, bezahlt</option>
              <option value="missed">Nein, noch offen</option>
            </select>
          </label>

          <template v-if="paymentForm.decision === 'paid'">
            <div class="grid two">
              <label>
                Betrag
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
                Bezahlt am
                <input v-model="paymentForm.date" class="input" type="date" required />
              </label>
            </div>
            <p class="muted small">
              Wenn der Betrag die aktuelle Faelligkeit komplett deckt, springt die naechste Rate automatisch weiter.
            </p>
          </template>

          <template v-else>
            <label>
              Neuer Faelligkeitstermin (optional)
              <input v-model="paymentForm.reschedule_date" class="input" type="date" />
            </label>
            <p class="muted small">
              Leer lassen, wenn die Schuld sichtbar ueberfaellig bleiben soll.
            </p>
          </template>

          <label>
            Notiz (optional)
            <textarea v-model.trim="paymentForm.notes" class="input textarea" rows="2"></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn" type="submit" :disabled="savingPayment">
              {{ savingPayment ? 'Speichere...' : 'Speichern' }}
            </button>
            <button class="btn ghost" type="button" @click="closePaymentModal">Abbrechen</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showKlarnaCalculator" class="modal-overlay" @click="closeKlarnaCalculator">
      <div class="modal-content klarna-calc" @click.stop>
        <div class="modal-header">
          <h2>Schuldenrechner</h2>
          <button class="btn close-btn" type="button" @click="closeKlarnaCalculator">x</button>
        </div>

        <div class="klarna-quick-entry">
          <p class="muted small">Schnelle Erfassung fuer mehrere Raten-Schulden.</p>

          <div class="quick-entry-form">
            <input
              v-model.trim="klarnaQuickEntry.name"
              class="input quick-input"
              placeholder="Name"
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
              {{ savingKlarna ? '...' : 'Hinzufuegen' }}
            </button>
          </div>

          <div v-if="klarnaEntries.length" class="klarna-entries-list">
            <h4>Uebersicht</h4>
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
                {{ formatCurrency(klarnaEntries.reduce((sum, entry) => sum + Number(entry.total_amount || 0), 0)) }}
              </p>
              <p>
                <strong>Gesamtrate pro Monat:</strong>
                {{ formatCurrency(klarnaEntries.reduce((sum, entry) => sum + Number(entry.monthly_payment || 0), 0)) }}
              </p>
            </div>

            <button class="btn primary" type="button" @click="saveAllKlarnaEntries">
              Alle hinzufuegen
            </button>
          </div>
        </div>
      </div>
    </div>
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

function todayIso() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

function dateToIsoLocal(dateValue) {
  return `${dateValue.getFullYear()}-${String(dateValue.getMonth() + 1).padStart(2, '0')}-${String(dateValue.getDate()).padStart(2, '0')}`;
}

function buildDebtForm(data = {}) {
  return {
    name: data.name || '',
    payment_type: data.payment_type || 'INSTALLMENT',
    total_amount: data.total_amount ?? '',
    amount_paid: data.amount_paid ?? 0,
    monthly_payment: data.monthly_payment ?? '',
    due_day: data.due_day ?? '',
    status: data.status || 'ACTIVE',
    start_date: data.start_date || todayIso(),
    notes: data.notes || '',
  };
}

function buildPaymentForm(debt = null) {
  const dueAmount = debt ? Number(debt.scheduled_payment_amount || 0) : 0;
  return {
    decision: 'paid',
    amount: dueAmount > 0 ? dueAmount.toFixed(2) : '',
    date: todayIso(),
    reschedule_date: '',
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

function parseAmount(value) {
  return Number.parseFloat(value || 0);
}

function addMonthsWithDay(dateValue, monthsToAdd, day) {
  const baseDate = new Date(dateValue);
  if (Number.isNaN(baseDate.getTime())) {
    return null;
  }

  const targetDate = new Date(Date.UTC(baseDate.getUTCFullYear(), baseDate.getUTCMonth() + monthsToAdd, 1));
  const lastDay = new Date(Date.UTC(targetDate.getUTCFullYear(), targetDate.getUTCMonth() + 1, 0)).getUTCDate();
  targetDate.setUTCDate(Math.min(Number(day || baseDate.getUTCDate()), lastDay));
  return targetDate.toISOString().slice(0, 10);
}

function resolveInstallmentDueDate(debt) {
  if (!debt.due_day) {
    return null;
  }

  const today = new Date(todayIso());
  const startDate = debt.start_date ? new Date(debt.start_date) : today;
  const reference = startDate > today ? startDate : today;
  const lastDay = new Date(reference.getFullYear(), reference.getMonth() + 1, 0).getDate();
  const candidate = new Date(
    reference.getFullYear(),
    reference.getMonth(),
    Math.min(Number(debt.due_day), lastDay),
  );

  if (candidate < reference) {
    return addMonthsWithDay(dateToIsoLocal(candidate), 1, debt.due_day);
  }
  return dateToIsoLocal(candidate);
}

function getNextDueDate(debt) {
  if (!debt || debt.status !== 'ACTIVE' || debt.is_fully_paid) {
    return null;
  }
  if (debt.next_due_date) {
    return debt.next_due_date;
  }
  if (debt.payment_type === 'FIXED_AMOUNT') {
    return debt.start_date || null;
  }
  return resolveInstallmentDueDate(debt);
}

function getDueState(debt) {
  if (debt?.due_state) {
    return debt.due_state;
  }
  if (!debt || debt.is_fully_paid || debt.status === 'PAID_OFF') {
    return 'PAID_OFF';
  }
  if (debt.status === 'PAUSED') {
    return 'PAUSED';
  }

  const nextDueDate = getNextDueDate(debt);
  if (!nextDueDate) {
    return 'SCHEDULED';
  }
  if (nextDueDate < todayIso()) {
    return 'OVERDUE';
  }
  if (nextDueDate === todayIso()) {
    return 'DUE_TODAY';
  }
  return 'UPCOMING';
}

const actionableDebts = computed(() =>
  debts.value.filter((debt) => ['OVERDUE', 'DUE_TODAY'].includes(getDueState(debt)))
);

const nextMonthsBreakdown = computed(() => {
  const months = [];
  const cursor = new Date(todayIso());
  cursor.setDate(1);

  const simulatedDebts = debts.value
    .filter((debt) => debt.status === 'ACTIVE' && !debt.is_fully_paid)
    .map((debt) => ({
      id: debt.id,
      name: debt.name,
      payment_type: debt.payment_type,
      due_day: debt.due_day,
      scheduled_payment_amount: parseAmount(debt.scheduled_payment_amount),
      remaining_amount: parseAmount(debt.remaining_amount),
      next_due_date: getNextDueDate(debt),
    }));

  for (let i = 0; i < 6; i += 1) {
    const monthStart = new Date(Date.UTC(cursor.getFullYear(), cursor.getMonth() + i, 1));
    const monthEnd = new Date(Date.UTC(monthStart.getUTCFullYear(), monthStart.getUTCMonth() + 1, 0));
    const entries = [];
    let amountDueTotal = 0;

    simulatedDebts.forEach((debt) => {
      while (debt.next_due_date && debt.remaining_amount > 0 && debt.next_due_date <= monthEnd.toISOString().slice(0, 10)) {
        const dueAmount = debt.payment_type === 'FIXED_AMOUNT'
          ? debt.remaining_amount
          : Math.min(debt.remaining_amount, debt.scheduled_payment_amount);

        if (dueAmount <= 0) {
          break;
        }

        debt.remaining_amount = Math.max(0, debt.remaining_amount - dueAmount);
        amountDueTotal += dueAmount;
        entries.push({
          entry_id: `${debt.id}-${debt.next_due_date}`,
          debt_id: debt.id,
          name: debt.name,
          amount: dueAmount,
          due_date: debt.next_due_date,
          remaining_after: debt.remaining_amount,
        });

        if (debt.payment_type === 'INSTALLMENT' && debt.remaining_amount > 0) {
          debt.next_due_date = addMonthsWithDay(debt.next_due_date, 1, debt.due_day);
        } else {
          debt.next_due_date = null;
        }
      }
    });

    months.push({
      month: monthStart.toISOString().slice(0, 7),
      entries,
      amount_due_total: amountDueTotal,
      remaining_total_after: simulatedDebts.reduce((sum, debt) => sum + debt.remaining_amount, 0),
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
  if (!value) {
    return 'Kein Datum';
  }
  return new Intl.DateTimeFormat('de-DE', { dateStyle: 'medium' }).format(new Date(value));
}

function formatMonthLabel(monthStr) {
  return new Intl.DateTimeFormat('de-DE', { year: 'numeric', month: 'long' }).format(new Date(`${monthStr}-01`));
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

function paymentAmountLabel(debt) {
  return debt.payment_type === 'INSTALLMENT' ? 'Aktuelle Rate' : 'Aktuell faellig';
}

function getDueLabel(debt) {
  const labels = {
    OVERDUE: 'Ueberfaellig',
    DUE_TODAY: 'Heute faellig',
    UPCOMING: 'Geplant',
    PAID_OFF: 'Erledigt',
    PAUSED: 'Pausiert',
    SCHEDULED: 'Ohne Termin',
  };
  return labels[getDueState(debt)] || 'Geplant';
}

function getDueHeadline(debt) {
  const nextDueDate = getNextDueDate(debt);
  const state = getDueState(debt);

  if (state === 'PAID_OFF') {
    return `Abbezahlt am ${formatDate(debt.paid_off_date)}`;
  }
  if (state === 'PAUSED') {
    return 'Diese Schuld ist pausiert.';
  }
  if (!nextDueDate) {
    return 'Noch kein Faelligkeitstermin gesetzt.';
  }
  if (state === 'OVERDUE') {
    return `Seit ${formatDate(nextDueDate)} ueberfaellig.`;
  }
  if (state === 'DUE_TODAY') {
    return 'Heute ist die Zahlung faellig.';
  }
  return `Naechste Faelligkeit: ${formatDate(nextDueDate)}`;
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
  const totalAmount = parseAmount(amount);
  const paymentAmount = parseAmount(payment);
  if (paymentAmount <= 0) {
    return 0;
  }
  return Math.ceil(totalAmount / paymentAmount);
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
    !debtForm.value.start_date ||
    (isInstallment && (!debtForm.value.monthly_payment || !debtForm.value.due_day))
  ) {
    alert('Bitte alle erforderlichen Felder ausfuellen.');
    return;
  }

  savingDebt.value = true;
  try {
    const payload = {
      ...debtForm.value,
      project: props.projectId,
      total_amount: parseAmount(debtForm.value.total_amount),
      amount_paid: parseAmount(debtForm.value.amount_paid),
      monthly_payment: isInstallment ? parseAmount(debtForm.value.monthly_payment) : null,
      due_day: isInstallment ? Number.parseInt(debtForm.value.due_day, 10) : null,
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
  if (!window.confirm(`Schuld "${debt.name}" wirklich loeschen?`)) {
    return;
  }

  try {
    await api.delete(`debts/${debt.id}/`);
    await loadDebts();
  } catch (error) {
    alert(getApiErrorMessage(error, 'Fehler beim Loeschen.'));
  }
}

function showPaymentModal(debt) {
  selectedDebtForPayment.value = debt;
  paymentForm.value = buildPaymentForm(debt);
  showPaymentRecordingModal.value = true;
}

function closePaymentModal() {
  showPaymentRecordingModal.value = false;
  selectedDebtForPayment.value = null;
  paymentForm.value = buildPaymentForm();
}

function appendDebtNote(existingNotes, newLine) {
  return [existingNotes?.trim(), newLine.trim()].filter(Boolean).join('\n');
}

function buildPaymentNote(debt) {
  if (paymentForm.value.decision === 'paid') {
    const paidAmount = parseAmount(paymentForm.value.amount).toFixed(2);
    const detail = paymentForm.value.notes ? ` ${paymentForm.value.notes}` : '';
    return `${paymentForm.value.date}: Faelligkeit bezahlt (${paidAmount} EUR).${detail}`;
  }

  const rescheduleText = paymentForm.value.reschedule_date
    ? ` Verschoben auf ${paymentForm.value.reschedule_date}.`
    : ' Bleibt ueberfaellig.';
  const detail = paymentForm.value.notes ? ` ${paymentForm.value.notes}` : '';
  return `${todayIso()}: Faelligkeit fuer ${debt.name} nicht bezahlt.${rescheduleText}${detail}`;
}

async function recordPayment() {
  const debt = selectedDebtForPayment.value;
  if (!debt) {
    return;
  }

  const currentDueAmount = parseAmount(debt.scheduled_payment_amount);
  const currentAmountPaid = parseAmount(debt.amount_paid);
  const totalAmount = parseAmount(debt.total_amount);
  const nextDueDate = getNextDueDate(debt);

  const payload = {
    notes: appendDebtNote(debt.notes || '', buildPaymentNote(debt)),
  };

  if (paymentForm.value.decision === 'paid') {
    const paymentAmount = parseAmount(paymentForm.value.amount);
    if (paymentAmount <= 0) {
      alert('Bitte einen Zahlungsbetrag angeben.');
      return;
    }

    const newAmountPaid = Math.min(currentAmountPaid + paymentAmount, totalAmount);
    const coversCurrentDue = paymentAmount + 0.009 >= currentDueAmount;

    payload.amount_paid = newAmountPaid;
    payload.status = newAmountPaid >= totalAmount ? 'PAID_OFF' : 'ACTIVE';
    payload.paid_off_date = newAmountPaid >= totalAmount ? paymentForm.value.date : null;

    if (newAmountPaid >= totalAmount) {
      payload.next_due_date = null;
    } else if (debt.payment_type === 'INSTALLMENT' && coversCurrentDue && nextDueDate) {
      payload.next_due_date = addMonthsWithDay(nextDueDate, 1, debt.due_day);
    } else {
      payload.next_due_date = nextDueDate;
    }
  } else {
    payload.status = 'ACTIVE';
    payload.paid_off_date = null;
    payload.next_due_date = paymentForm.value.reschedule_date || nextDueDate;
    // If payment is missed, increase total amount by the due amount to simulate growing debt
    payload.total_amount = totalAmount + currentDueAmount;
  }

  savingPayment.value = true;
  try {
    await api.patch(`debts/${debt.id}/`, payload);
    closePaymentModal();
    await loadDebts();
  } catch (error) {
    alert(getApiErrorMessage(error, 'Faelligkeit konnte nicht aktualisiert werden.'));
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
    alert('Bitte alle Felder ausfuellen.');
    return;
  }

  klarnaEntries.value.push({
    ...entry,
    total_amount: parseAmount(entry.total_amount),
    monthly_payment: parseAmount(entry.monthly_payment),
    due_day: Number.parseInt(entry.due_day, 10),
  });
  klarnaQuickEntry.value = buildKlarnaQuickEntry();
}

function removeKlarnaEntry(index) {
  klarnaEntries.value.splice(index, 1);
}

async function saveAllKlarnaEntries() {
  if (!klarnaEntries.value.length) {
    alert('Keine Eintraege zum Speichern.');
    return;
  }

  savingKlarna.value = true;
  try {
    for (const entry of klarnaEntries.value) {
      await api.post('debts/', {
        ...entry,
        project: props.projectId,
        status: 'ACTIVE',
        start_date: todayIso(),
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

.due-section,
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
  margin-bottom: 4px;
}

.section-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.due-list {
  display: grid;
  gap: 10px;
}

.due-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.due-item.due-overdue {
  border-color: rgba(220, 38, 38, 0.28);
  background: rgba(220, 38, 38, 0.08);
}

.due-item.due-due_today {
  border-color: rgba(217, 119, 6, 0.28);
  background: rgba(217, 119, 6, 0.08);
}

.due-copy {
  display: grid;
  gap: 4px;
}

.due-copy p {
  margin: 0;
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

.debt-card.debt-overdue {
  border-color: rgba(220, 38, 38, 0.32);
  box-shadow: 0 0 0 1px rgba(220, 38, 38, 0.08);
}

.debt-card.debt-due_today {
  border-color: rgba(217, 119, 6, 0.32);
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

.debt-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.status-badge,
.due-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
}

.status-badge {
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

.due-badge.due-overdue {
  background: rgba(220, 38, 38, 0.12);
  color: #b91c1c;
}

.due-badge.due-due_today {
  background: rgba(217, 119, 6, 0.14);
  color: #b45309;
}

.due-badge.due-upcoming,
.due-badge.due-scheduled {
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
}

.due-badge.due-paid_off {
  background: rgba(34, 197, 94, 0.12);
  color: #166534;
}

.due-badge.due-paused {
  background: rgba(148, 163, 184, 0.16);
  color: var(--muted);
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
  border-radius: 999px;
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
  border-radius: 12px;
  background: rgba(47, 99, 255, 0.04);
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

.stat strong.paid-off,
.success-text {
  color: #16a34a;
}

.debt-meta {
  display: grid;
  gap: 4px;
}

.debt-meta p {
  margin: 0;
}

.debt-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.debt-actions .btn {
  flex: 1;
  min-width: 104px;
}

.empty-hint {
  text-align: center;
  padding: 20px;
  margin: 0;
}

.month-breakdown {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.month-card {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  display: grid;
  gap: 10px;
}

.month-card h4 {
  margin: 0;
  font-size: 15px;
}

.month-kpi {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
}

.month-kpi span {
  color: var(--muted);
}

.month-entries {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.month-entry {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}

.month-entry:first-child {
  border-top: none;
  padding-top: 0;
}

.month-entry p {
  margin: 0;
}

.month-entry-values {
  display: grid;
  gap: 2px;
  text-align: right;
}

.tiny {
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
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
  max-width: 520px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  display: grid;
  grid-template-rows: auto 1fr;
}

.modal-content.klarna-calc {
  max-width: 640px;
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

.modal-form,
.klarna-quick-entry {
  padding: 20px;
  display: grid;
  gap: 14px;
}

.decision-summary {
  display: grid;
  gap: 8px;
  padding: 14px;
  border-radius: 12px;
  background: rgba(47, 99, 255, 0.05);
}

.decision-kpi {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.decision-kpi span {
  color: var(--muted);
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

.input:focus,
.quick-input:focus {
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

.quick-entry-form {
  display: grid;
  gap: 8px;
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
  border-radius: 8px;
  display: grid;
  gap: 4px;
  background: rgba(47, 99, 255, 0.04);
}

.klarna-totals p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 768px) {
  .section-head,
  .due-item,
  .month-entry {
    flex-direction: column;
    align-items: stretch;
  }

  .section-actions,
  .debt-actions,
  .modal-actions {
    flex-direction: column;
  }

  .debts-grid,
  .month-breakdown,
  .grid.two {
    grid-template-columns: 1fr;
  }

  .debt-stats {
    grid-template-columns: repeat(2, 1fr);
  }

  .modal-content {
    max-width: 100%;
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
