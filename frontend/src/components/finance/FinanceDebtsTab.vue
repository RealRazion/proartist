<template>
  <div class="debts-tab">
    <!-- Urgent Due / Overdue Banner -->
    <article v-if="actionableDebts.length" class="panel urgent-panel">
      <div class="urgent-head">
        <div>
          <span class="urgent-kicker">⚡ Jetzt prüfen</span>
          <h3>{{ actionableDebts.length }} fällige oder überfällige Zahlung{{ actionableDebts.length === 1 ? "" : "en" }}</h3>
          <p class="muted small">Bestätige kurz, ob diese Rate bereits abgebucht/bezahlt wurde oder verschoben werden soll.</p>
        </div>
      </div>

      <div class="urgent-list">
        <div v-for="d in actionableDebts" :key="`urg-${d.id}`" class="urgent-row">
          <div>
            <strong>{{ d.name }}</strong>
            <span class="muted small" style="display:block">
              {{ dueStateText(d) }} · Fällig: <strong>{{ fmt(d.scheduled_payment_amount) }}</strong>
            </span>
          </div>
          <div class="urgent-actions">
            <button type="button" class="btn sm" @click="openPaymentModal(d)">Zahlung klären</button>
          </div>
        </div>
      </div>
    </article>

    <!-- Portfolio Summary KPIs -->
    <div class="debt-kpis">
      <article class="kpi-box">
        <span class="kpi-lbl">Offene Gesamtschuld</span>
        <strong class="kpi-num neg-txt">{{ fmt(totalRemaining) }}</strong>
        <span class="muted tiny">{{ activeDebtsCount }} aktive Posten</span>
      </article>

      <article class="kpi-box">
        <span class="kpi-lbl">Monatliche Ratenlast</span>
        <strong class="kpi-num">{{ fmt(totalMonthlyRate) }}</strong>
        <span class="muted tiny">Summe aller geplanten Monatsraten</span>
      </article>

      <article class="kpi-box">
        <span class="kpi-lbl">Bereits getilgt</span>
        <strong class="kpi-num pos-txt">{{ portfolioProgress }} %</strong>
        <div class="mini-prog">
          <span :style="{ width: `${portfolioProgress}%` }"></span>
        </div>
        <span class="muted tiny">{{ fmt(totalPaid) }} von {{ fmt(totalOriginal) }} erledigt</span>
      </article>
    </div>

    <!-- Main Debt List Panel -->
    <article class="panel main-debts-panel">
      <div class="toolbar-row">
        <div class="filter-pills">
          <button
            v-for="f in filterTabs"
            :key="f.id"
            type="button"
            class="pill-btn"
            :class="{ active: activeFilter === f.id }"
            @click="activeFilter = f.id"
          >
            {{ f.label }} ({{ f.count }})
          </button>
        </div>

        <div class="toolbar-actions">
          <button type="button" class="btn ghost sm" @click="showBatchModal = true">
            ⚡ Multi-Raten Schnellerfassung
          </button>
          <button type="button" class="btn sm" @click="openDebtModal()">
            + Schuld / Kredit eintragen
          </button>
        </div>
      </div>

      <div v-if="visibleDebts.length" class="debt-cards-grid">
        <div
          v-for="debt in visibleDebts"
          :key="debt.id"
          class="debt-card"
          :class="{
            'is-paid': debt.is_fully_paid || debt.status === 'PAID_OFF',
            'is-overdue': getDueState(debt) === 'OVERDUE',
            'is-today': getDueState(debt) === 'DUE_TODAY',
          }"
        >
          <div class="dc-head">
            <div>
              <div class="dc-title-row">
                <h3>{{ debt.name }}</h3>
                <span class="kind-tag">{{ debt.debt_kind === "CREDIT" ? "Kredit" : "Schuld" }}</span>
              </div>
              <span class="muted tiny">
                {{ debt.payment_type === "FIXED_AMOUNT" ? "Einmaliger Fixbetrag" : `Ratenzahlung · am ${debt.due_day || 1}. des Monats` }}
              </span>
            </div>

            <span class="due-pill" :class="`st-${getDueState(debt).toLowerCase()}`">
              {{ dueBadgeLabel(debt) }}
            </span>
          </div>

          <div class="dc-prog-wrap">
            <div class="dc-prog-labels">
              <span class="muted tiny">Fortschritt</span>
              <strong>{{ Math.min(100, Math.round(Number(debt.payment_percentage || 0))) }} %</strong>
            </div>
            <div class="dc-prog-bar">
              <span :style="{ width: `${Math.min(100, Number(debt.payment_percentage || 0))}%` }"></span>
            </div>
          </div>

          <div class="dc-metrics">
            <div>
              <span class="muted tiny">Gesamt</span>
              <strong>{{ fmt(debt.total_amount) }}</strong>
            </div>
            <div>
              <span class="muted tiny">Bezahlt</span>
              <strong class="pos-txt">{{ fmt(debt.amount_paid) }}</strong>
            </div>
            <div>
              <span class="muted tiny">Restschuld</span>
              <strong :class="debt.is_fully_paid ? 'pos-txt' : 'neg-txt'">{{ fmt(debt.remaining_amount) }}</strong>
            </div>
            <div>
              <span class="muted tiny">{{ debt.payment_type === "FIXED_AMOUNT" ? "Offen" : "Monatsrate" }}</span>
              <strong>{{ fmt(debt.scheduled_payment_amount || debt.monthly_payment) }}</strong>
            </div>
          </div>

          <div class="dc-submeta muted tiny">
            <span>{{ dueStateText(debt) }}</span>
            <span v-if="debt.payment_type === 'INSTALLMENT' && !debt.is_fully_paid && debt.months_remaining > 0">
              Noch ca. <strong>{{ debt.months_remaining }} Raten</strong>
            </span>
          </div>

          <div v-if="debt.notes" class="dc-notes muted tiny">{{ debt.notes }}</div>

          <div class="dc-actions">
            <button
              v-if="debt.status === 'ACTIVE' && !debt.is_fully_paid"
              type="button"
              class="btn sm"
              @click="openPaymentModal(debt)"
            >
              € Zahlung verbuchen
            </button>
            <button
              v-if="debt.status === 'ACTIVE' && !debt.is_fully_paid && debt.payment_type === 'INSTALLMENT'"
              type="button"
              class="btn ghost sm"
              @click="skipMonthQuick(debt)"
            >
              Monat pausieren
            </button>
            <button type="button" class="btn ghost sm" @click="openDebtModal(debt)">✎</button>
            <button type="button" class="btn ghost sm" title="Letzte Aktion rückgängig (10 Min)" @click="undoLast(debt)">
              ↶ Undo
            </button>
            <button type="button" class="btn ghost danger sm" title="Löschen" @click="deleteDebt(debt)">✕</button>
          </div>
        </div>
      </div>

      <div v-else class="empty-debts">
        <p class="muted">Keine Einträge in dieser Ansicht vorhanden.</p>
        <button type="button" class="btn sm" @click="openDebtModal()">Ersten Eintrag anlegen</button>
      </div>
    </article>

    <!-- Structured Payment History -->
    <article v-if="allPayments.length" class="panel history-panel">
      <div class="lbl-row" @click="showHistory = !showHistory" style="cursor:pointer">
        <div>
          <span class="section-kicker">Zahlungshistorie</span>
          <h3 style="margin:0">Bisher verbuchte Raten &amp; Tilgungen ({{ allPayments.length }})</h3>
        </div>
        <button type="button" class="btn ghost sm">{{ showHistory ? "Einklappen ▲" : "Anzeigen ▼" }}</button>
      </div>

      <div v-if="showHistory" class="history-list">
        <div v-for="p in allPayments" :key="`pay-${p.id}`" class="history-row">
          <div>
            <strong>{{ p.debtName }}</strong>
            <span class="muted tiny" style="display:block">
              {{ formatDateDe(p.payment_date) }}{{ p.notes ? ` · ${p.notes}` : "" }}
            </span>
          </div>
          <div class="history-right">
            <strong class="pos-txt">{{ fmt(p.amount) }}</strong>
            <button type="button" class="btn ghost tiny" @click="deletePayment(p)">Löschen</button>
          </div>
        </div>
      </div>
    </article>

    <!-- ===== ADD / EDIT DEBT MODAL ===== -->
    <div v-if="showDebtModal" class="modal-overlay" @click.self="showDebtModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ debtForm.id ? "Eintrag bearbeiten" : "Schuld oder Kredit eintragen" }}</h3>
          <button type="button" class="modal-close" @click="showDebtModal = false">&times;</button>
        </div>

        <form class="modal-form" @submit.prevent="submitDebt">
          <div class="two-col">
            <label>
              Kategorie
              <select v-model="debtForm.debt_kind" class="input">
                <option value="DEBT">Schuld (Klarna, Rechnung, Privat)</option>
                <option value="CREDIT">Kredit / Darlehen</option>
              </select>
            </label>
            <label>
              Rückzahlungs-Art
              <select v-model="debtForm.payment_type" class="input">
                <option value="INSTALLMENT">Monatliche Ratenzahlung</option>
                <option value="FIXED_AMOUNT">Einmaliger Fixbetrag</option>
              </select>
            </label>
          </div>

          <label>
            Bezeichnung
            <input v-model.trim="debtForm.name" class="input" placeholder="z. B. Klarna Sneaker, PayPal, Privatkredit" required />
          </label>

          <div class="two-col">
            <label>
              Gesamtschuld (€)
              <input v-model="debtForm.total_amount" type="number" step="0.01" min="0.01" class="input" required />
            </label>
            <label>
              Bereits abbezahlt (€)
              <input v-model="debtForm.amount_paid" type="number" step="0.01" min="0" class="input" />
            </label>
          </div>

          <div v-if="debtForm.payment_type === 'INSTALLMENT'" class="two-col">
            <label>
              Monatliche Rate (€)
              <input v-model="debtForm.monthly_payment" type="number" step="0.01" min="0.01" class="input" required />
            </label>
            <label>
              Abbuchungstag im Monat (1–31)
              <input v-model="debtForm.due_day" type="number" min="1" max="31" class="input" placeholder="z. B. 15" required />
            </label>
          </div>

          <div class="two-col">
            <label>
              {{ debtForm.payment_type === "FIXED_AMOUNT" ? "Fälligkeitsdatum" : "Nächste Fälligkeit / Start" }}
              <input v-model="debtForm.next_due_date" type="date" class="input" required />
            </label>
            <label>
              Status
              <select v-model="debtForm.status" class="input">
                <option value="ACTIVE">Aktiv</option>
                <option value="PAUSED">Pausiert</option>
                <option value="PAID_OFF">Abbezahlt</option>
              </select>
            </label>
          </div>

          <label>
            Notiz (optional)
            <textarea v-model.trim="debtForm.notes" class="input" rows="2" placeholder="z. B. Referenznummer oder Vereinbarung"></textarea>
          </label>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showDebtModal = false">Abbrechen</button>
            <button type="submit" class="btn" :disabled="saving">{{ saving ? "Speichere..." : "Speichern" }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== RECORD PAYMENT MODAL ===== -->
    <div v-if="paymentTarget" class="modal-overlay" @click.self="paymentTarget = null">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Zahlung klären: {{ paymentTarget.name }}</h3>
          <button type="button" class="modal-close" @click="paymentTarget = null">&times;</button>
        </div>

        <form class="modal-form" @submit.prevent="submitPayment">
          <label>
            Status dieser Fälligkeit
            <select v-model="payForm.decision" class="input">
              <option value="paid">✓ Bezahlt / Abgebucht</option>
              <option value="skip_month">⏭ Diesen Monat aussetzen (nächster Monat weiter)</option>
              <option value="missed">⏳ Noch offen / neuen Termin setzen</option>
            </select>
          </label>

          <template v-if="payForm.decision === 'paid'">
            <div class="two-col">
              <label>
                Gezahlter Betrag (€)
                <input v-model="payForm.amount" type="number" step="0.01" min="0.01" class="input" required />
              </label>
              <label>
                Datum
                <input v-model="payForm.date" type="date" class="input" required />
              </label>
            </div>

            <label class="checkbox-row">
              <input v-model="payForm.deductFromBalance" type="checkbox" />
              <span>Diesen Betrag auch direkt von meinem aktuellen Kontostand abziehen</span>
            </label>
          </template>

          <template v-else-if="payForm.decision === 'missed'">
            <label>
              Neuer Zahlungstermin (optional)
              <input v-model="payForm.reschedule_date" type="date" class="input" />
            </label>
          </template>

          <label>
            Notiz (optional)
            <input v-model.trim="payForm.notes" class="input" placeholder="z. B. Teilzahlung oder reguläre Rate" />
          </label>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="paymentTarget = null">Abbrechen</button>
            <button type="submit" class="btn" :disabled="saving">{{ saving ? "Verbuche..." : "Bestätigen" }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== MULTI-RATEN BATCH MODAL ===== -->
    <div v-if="showBatchModal" class="modal-overlay" @click.self="showBatchModal = false">
      <div class="modal-box wide">
        <div class="modal-header">
          <h3>⚡ Multi-Raten Schnellerfassung</h3>
          <button type="button" class="modal-close" @click="showBatchModal = false">&times;</button>
        </div>

        <div class="modal-form">
          <p class="muted small" style="margin:0">
            Perfekt für mehrere Klarna-, PayPal- oder Rechnungs-Raten: Tippe Name, offenen Betrag, Monatsrate und Zahlungstag ein und speichere alle auf einmal.
          </p>

          <div class="batch-inputs">
            <input v-model.trim="batchDraft.name" class="input" placeholder="Bezeichnung (z. B. Klarna #1)" @keyup.enter="addBatchRow" />
            <input v-model="batchDraft.total_amount" type="number" step="0.01" class="input" placeholder="Restschuld (€)" @keyup.enter="addBatchRow" />
            <input v-model="batchDraft.monthly_payment" type="number" step="0.01" class="input" placeholder="Rate/Monat (€)" @keyup.enter="addBatchRow" />
            <input v-model="batchDraft.due_day" type="number" min="1" max="31" class="input" placeholder="Tag (1-31)" @keyup.enter="addBatchRow" />
            <button type="button" class="btn sm" @click="addBatchRow">+ Zeile</button>
          </div>

          <div v-if="batchRows.length" class="batch-list">
            <div v-for="(r, idx) in batchRows" :key="idx" class="batch-item">
              <strong>{{ r.name }}</strong>
              <span>Gesamt: {{ fmt(r.total_amount) }}</span>
              <span>Rate: {{ fmt(r.monthly_payment) }}/M.</span>
              <span>am {{ r.due_day }}.</span>
              <button type="button" class="btn ghost danger tiny" @click="batchRows.splice(idx, 1)">✕</button>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showBatchModal = false">Schließen</button>
            <button type="button" class="btn" :disabled="!batchRows.length || saving" @click="saveAllBatchRows">
              {{ saving ? "Speichere..." : `Alle ${batchRows.length} Raten anlegen` }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import api from "../../api";
import {
  formatDateDe,
  formatMoney,
  resolveDebtNextDueDate,
  round2,
  toNum,
  todayIso,
} from "../../utils/financeEngine";

const props = defineProps({
  project: { type: Object, default: null },
  debts: { type: Array, default: () => [] },
  currency: { type: String, default: "EUR" },
});

const emit = defineEmits(["refresh", "adjust-balance", "notify"]);

const today = todayIso();
const saving = ref(false);
const activeFilter = ref("ALL");
const showHistory = ref(false);

function fmt(val) {
  return formatMoney(val, props.currency);
}

function getDueState(debt) {
  if (!debt || debt.is_fully_paid || debt.status === "PAID_OFF") return "PAID_OFF";
  if (debt.status === "PAUSED") return "PAUSED";
  const nextDue = debt.next_due_date || resolveDebtNextDueDate(debt, today);
  if (!nextDue) return "UPCOMING";
  if (nextDue < today) return "OVERDUE";
  if (nextDue === today) return "DUE_TODAY";
  return "UPCOMING";
}

function dueBadgeLabel(debt) {
  const st = getDueState(debt);
  if (st === "PAID_OFF") return "Abbezahlt ✓";
  if (st === "PAUSED") return "Pausiert";
  if (st === "OVERDUE") return "Überfällig";
  if (st === "DUE_TODAY") return "Heute fällig";
  const nextDue = debt.next_due_date || resolveDebtNextDueDate(debt, today);
  return nextDue ? `Fällig ${formatDateDe(nextDue)}` : "Geplant";
}

function dueStateText(debt) {
  const st = getDueState(debt);
  const nextDue = debt.next_due_date || resolveDebtNextDueDate(debt, today);
  if (st === "PAID_OFF") return debt.paid_off_date ? `Erledigt am ${formatDateDe(debt.paid_off_date)}` : "Vollständig getilgt";
  if (st === "PAUSED") return "Zahlung aktuell pausiert";
  if (st === "OVERDUE") return `Seit ${formatDateDe(nextDue)} offen`;
  if (st === "DUE_TODAY") return "Heute zur Zahlung fällig";
  return nextDue ? `Nächster Termin: ${formatDateDe(nextDue)}` : "Aktiv";
}

const activeDebts = computed(() =>
  (props.debts || []).filter((d) => d.status === "ACTIVE" && !d.is_fully_paid)
);

const actionableDebts = computed(() =>
  activeDebts.value.filter((d) => ["OVERDUE", "DUE_TODAY"].includes(getDueState(d)))
);

const activeDebtsCount = computed(() => activeDebts.value.length);

const totalRemaining = computed(() =>
  activeDebts.value.reduce((s, d) => s + toNum(d.remaining_amount), 0)
);

const totalMonthlyRate = computed(() =>
  activeDebts.value.reduce((s, d) => s + toNum(d.scheduled_payment_amount || d.monthly_payment), 0)
);

const totalOriginal = computed(() =>
  (props.debts || []).reduce((s, d) => s + toNum(d.total_amount), 0)
);

const totalPaid = computed(() =>
  (props.debts || []).reduce((s, d) => s + toNum(d.amount_paid), 0)
);

const portfolioProgress = computed(() => {
  if (totalOriginal.value <= 0) return 0;
  return Math.min(100, Math.round((totalPaid.value / totalOriginal.value) * 100));
});

const filterTabs = computed(() => [
  { id: "ALL", label: "Alle aktiven", count: (props.debts || []).filter((d) => !d.is_fully_paid && d.status !== "PAID_OFF").length },
  { id: "DEBT", label: "Schulden & Raten", count: (props.debts || []).filter((d) => d.debt_kind !== "CREDIT" && !d.is_fully_paid).length },
  { id: "CREDIT", label: "Kredite", count: (props.debts || []).filter((d) => d.debt_kind === "CREDIT" && !d.is_fully_paid).length },
  { id: "PAID", label: "Abbezahlt", count: (props.debts || []).filter((d) => d.is_fully_paid || d.status === "PAID_OFF").length },
]);

const visibleDebts = computed(() => {
  const list = props.debts || [];
  if (activeFilter.value === "PAID") {
    return list.filter((d) => d.is_fully_paid || d.status === "PAID_OFF");
  }
  const open = list.filter((d) => !d.is_fully_paid && d.status !== "PAID_OFF");
  if (activeFilter.value === "DEBT") return open.filter((d) => d.debt_kind !== "CREDIT");
  if (activeFilter.value === "CREDIT") return open.filter((d) => d.debt_kind === "CREDIT");
  return open;
});

const allPayments = computed(() => {
  const rows = [];
  for (const d of props.debts || []) {
    for (const p of d.payments || []) {
      rows.push({
        ...p,
        debtId: d.id,
        debtName: d.name,
      });
    }
  }
  return rows.sort((a, b) => (b.payment_date || "").localeCompare(a.payment_date || ""));
});

// ── Debt CRUD Modal ────────────────────────────────────────────────────────
const showDebtModal = ref(false);
const debtForm = ref({
  id: null,
  name: "",
  debt_kind: "DEBT",
  payment_type: "INSTALLMENT",
  total_amount: "",
  amount_paid: "0",
  monthly_payment: "",
  due_day: "1",
  next_due_date: today,
  status: "ACTIVE",
  notes: "",
});

function openDebtModal(debt = null) {
  if (debt) {
    debtForm.value = {
      id: debt.id,
      name: debt.name,
      debt_kind: debt.debt_kind || "DEBT",
      payment_type: debt.payment_type || "INSTALLMENT",
      total_amount: String(debt.total_amount),
      amount_paid: String(debt.amount_paid || 0),
      monthly_payment: debt.monthly_payment ? String(debt.monthly_payment) : "",
      due_day: debt.due_day ? String(debt.due_day) : "1",
      next_due_date: debt.next_due_date || debt.start_date || today,
      status: debt.status || "ACTIVE",
      notes: debt.notes || "",
    };
  } else {
    debtForm.value = {
      id: null,
      name: "",
      debt_kind: "DEBT",
      payment_type: "INSTALLMENT",
      total_amount: "",
      amount_paid: "0",
      monthly_payment: "",
      due_day: String(new Date().getDate()),
      next_due_date: today,
      status: "ACTIVE",
      notes: "",
    };
  }
  showDebtModal.value = true;
}

async function submitDebt() {
  if (!props.project) return;
  saving.value = true;
  try {
    const isInst = debtForm.value.payment_type === "INSTALLMENT";
    const payload = {
      project: props.project.id,
      name: debtForm.value.name,
      debt_kind: debtForm.value.debt_kind,
      payment_type: debtForm.value.payment_type,
      total_amount: round2(toNum(debtForm.value.total_amount)),
      amount_paid: round2(toNum(debtForm.value.amount_paid)),
      monthly_payment: isInst ? round2(toNum(debtForm.value.monthly_payment)) : null,
      due_day: isInst ? Math.min(31, Math.max(1, Number(debtForm.value.due_day || 1))) : null,
      next_due_date: debtForm.value.next_due_date || today,
      start_date: debtForm.value.next_due_date || today,
      status: debtForm.value.status,
      notes: debtForm.value.notes,
    };
    if (debtForm.value.id) {
      await api.patch(`debts/${debtForm.value.id}/`, payload);
    } else {
      await api.post("debts/", payload);
    }
    showDebtModal.value = false;
    emit("notify", { type: "success", text: "Eintrag gespeichert." });
    emit("refresh");
  } catch (err) {
    emit("notify", { type: "error", text: err?.response?.data?.detail || "Speichern fehlgeschlagen." });
  } finally {
    saving.value = false;
  }
}

async function deleteDebt(debt) {
  if (!confirm(`„${debt.name}“ wirklich löschen?`)) return;
  try {
    await api.delete(`debts/${debt.id}/`);
    emit("notify", { type: "success", text: "Eintrag gelöscht." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Konnte nicht gelöscht werden." });
  }
}

// ── Record Payment ─────────────────────────────────────────────────────────
const paymentTarget = ref(null);
const payForm = ref({
  decision: "paid",
  amount: "",
  date: today,
  reschedule_date: "",
  notes: "",
  deductFromBalance: false,
});

function openPaymentModal(debt) {
  paymentTarget.value = debt;
  const due = toNum(debt.scheduled_payment_amount || debt.monthly_payment || debt.remaining_amount);
  payForm.value = {
    decision: "paid",
    amount: due > 0 ? due.toFixed(2) : "",
    date: today,
    reschedule_date: "",
    notes: "",
    deductFromBalance: false,
  };
}

async function submitPayment() {
  if (!paymentTarget.value) return;
  saving.value = true;
  try {
    const amt = round2(toNum(payForm.value.amount));
    await api.post(`debts/${paymentTarget.value.id}/record-payment/`, {
      decision: payForm.value.decision,
      amount: payForm.value.decision === "paid" ? amt : null,
      date: payForm.value.decision === "paid" ? payForm.value.date : null,
      reschedule_date: payForm.value.decision === "missed" ? payForm.value.reschedule_date || null : null,
      notes: payForm.value.notes || "",
    });
    if (payForm.value.decision === "paid" && payForm.value.deductFromBalance && amt > 0) {
      emit("adjust-balance", -amt);
    }
    paymentTarget.value = null;
    emit("notify", { type: "success", text: "Zahlungsstatus aktualisiert." });
    emit("refresh");
  } catch (err) {
    emit("notify", { type: "error", text: err?.response?.data?.detail || "Verbuchen fehlgeschlagen." });
  } finally {
    saving.value = false;
  }
}

async function skipMonthQuick(debt) {
  if (!confirm(`Rate für „${debt.name}“ diesen Monat aussetzen und auf nächsten Monat schieben?`)) return;
  try {
    await api.post(`debts/${debt.id}/record-payment/`, {
      decision: "skip_month",
      notes: "Monat pausiert",
    });
    emit("notify", { type: "success", text: "Rate auf nächsten Monat verschoben." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Aktion fehlgeschlagen." });
  }
}

async function undoLast(debt) {
  try {
    await api.post(`debts/${debt.id}/undo-last/`);
    emit("notify", { type: "success", text: "Letzte Aktion rückgängig gemacht." });
    emit("refresh");
  } catch (err) {
    emit("notify", {
      type: "error",
      text: err?.response?.data?.detail || "Keine Aktion der letzten 10 Minuten zum Rückgängigmachen gefunden.",
    });
  }
}

async function deletePayment(p) {
  if (!confirm(`Zahlung über ${fmt(p.amount)} löschen?`)) return;
  try {
    await api.delete(`debts/${p.debtId}/payment/${p.id}/`);
    emit("notify", { type: "success", text: "Zahlung entfernt." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Zahlung konnte nicht gelöscht werden." });
  }
}

// ── Multi-Raten Batch Entry ────────────────────────────────────────────────
const showBatchModal = ref(false);
const batchDraft = ref({ name: "", total_amount: "", monthly_payment: "", due_day: "15" });
const batchRows = ref([]);

function addBatchRow() {
  const name = batchDraft.value.name.trim();
  const total = round2(toNum(batchDraft.value.total_amount));
  const rate = round2(toNum(batchDraft.value.monthly_payment));
  const day = Math.min(31, Math.max(1, Number(batchDraft.value.due_day || 15)));
  if (!name || total <= 0 || rate <= 0) return;
  batchRows.value.push({ name, total_amount: total, monthly_payment: rate, due_day: day });
  batchDraft.value = { name: "", total_amount: "", monthly_payment: "", due_day: String(day) };
}

async function saveAllBatchRows() {
  if (!props.project || !batchRows.value.length) return;
  saving.value = true;
  try {
    for (const r of batchRows.value) {
      await api.post("debts/", {
        project: props.project.id,
        name: r.name,
        debt_kind: "DEBT",
        payment_type: "INSTALLMENT",
        total_amount: r.total_amount,
        amount_paid: 0,
        monthly_payment: r.monthly_payment,
        due_day: r.due_day,
        start_date: today,
        status: "ACTIVE",
      });
    }
    batchRows.value = [];
    showBatchModal.value = false;
    emit("notify", { type: "success", text: "Alle Raten erfolgreich angelegt." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Fehler beim Anlegen der Raten." });
  } finally {
    saving.value = false;
  }
}
</script>

<style scoped>
.debts-tab {
  display: grid;
  gap: 16px;
}

.panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
}

.urgent-panel {
  border-color: rgba(245, 158, 11, 0.45);
  background: color-mix(in srgb, #f59e0b 8%, var(--card));
  display: grid;
  gap: 14px;
}

.urgent-kicker {
  font-size: 11.5px;
  font-weight: 700;
  color: #fbbf24;
  text-transform: uppercase;
}

.urgent-head h3 { margin: 2px 0 4px; }
.urgent-head p { margin: 0; }

.urgent-list {
  display: grid;
  gap: 8px;
}

.urgent-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--card);
  border: 1px solid var(--border);
}

.debt-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.kpi-box {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 18px;
  display: grid;
  gap: 5px;
}

.kpi-lbl {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--muted);
}

.kpi-num {
  font-size: 1.45rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.mini-prog {
  height: 6px;
  border-radius: 999px;
  background: var(--surface);
  overflow: hidden;
}

.mini-prog span {
  display: block;
  height: 100%;
  background: #22c55e;
}

.main-debts-panel,
.history-panel {
  display: grid;
  gap: 16px;
}

.toolbar-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.filter-pills,
.toolbar-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.pill-btn {
  padding: 7px 13px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.pill-btn.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
}

.debt-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 14px;
}

.debt-card {
  padding: 16px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 12px;
}

.debt-card.is-overdue {
  border-color: rgba(239, 68, 68, 0.5);
}

.debt-card.is-today {
  border-color: rgba(245, 158, 11, 0.5);
}

.debt-card.is-paid {
  opacity: 0.72;
}

.dc-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.dc-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.dc-title-row h3 {
  margin: 0;
  font-size: 1.05rem;
}

.kind-tag {
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 11px;
  color: var(--muted);
}

.due-pill {
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
  white-space: nowrap;
  background: var(--card);
  border: 1px solid var(--border);
}

.due-pill.st-overdue { color: #ef4444; border-color: rgba(239, 68, 68, 0.4); }
.due-pill.st-due_today { color: #f59e0b; border-color: rgba(245, 158, 11, 0.4); }
.due-pill.st-paid_off { color: #22c55e; border-color: rgba(34, 197, 94, 0.4); }

.dc-prog-wrap {
  display: grid;
  gap: 5px;
}

.dc-prog-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
}

.dc-prog-bar {
  height: 7px;
  border-radius: 999px;
  background: var(--card);
  overflow: hidden;
}

.dc-prog-bar span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--brand), #22c55e);
}

.dc-metrics {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  padding: 10px;
  border-radius: 12px;
  background: var(--card);
  font-size: 13px;
}

.dc-metrics > div {
  display: grid;
  gap: 2px;
}

.dc-submeta {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 8px;
}

.dc-notes {
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--card);
}

.dc-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.empty-debts {
  padding: 32px;
  text-align: center;
  display: grid;
  gap: 10px;
  justify-items: center;
}

/* History */
.lbl-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.section-kicker {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand);
  margin-bottom: 3px;
}

.history-list {
  display: grid;
  gap: 8px;
}

.history-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.history-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay, rgba(2, 6, 23, 0.78));
  display: grid;
  place-items: center;
  z-index: 95;
  padding: 16px;
}

.modal-box {
  width: min(500px, 100%);
  max-height: 92vh;
  overflow-y: auto;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
}

.modal-box.wide {
  width: min(680px, 100%);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 { margin: 0; }

.modal-close {
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 22px;
  cursor: pointer;
}

.modal-form {
  display: grid;
  gap: 14px;
  padding: 20px;
}

.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.batch-inputs {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr 0.8fr auto;
  gap: 8px;
}

.batch-list {
  display: grid;
  gap: 6px;
}

.batch-item {
  display: grid;
  grid-template-columns: 1.4fr 1fr 1fr auto auto;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--surface);
  font-size: 13px;
}

.pos-txt { color: #22c55e; }
.neg-txt { color: #ef4444; }
.tiny { font-size: 12px; }
.small { font-size: 13.5px; }

@media (max-width: 720px) {
  .two-col,
  .batch-inputs,
  .batch-item {
    grid-template-columns: 1fr;
  }
}
</style>

