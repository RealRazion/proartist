<template>
  <div class="entries-tab">
    <!-- Top Quick Actions & Sub-Navigation -->
    <article class="panel top-bar-panel">
      <div class="tb-head">
        <div>
          <span class="section-kicker">Plan-Grundlage &amp; Alltag</span>
          <h2>Einnahmen, Fixkosten, Abos &amp; Ausgaben</h2>
          <p class="muted small">
            Hinterlege bei monatlichen Posten den genauen Zahlungstag (1–31), damit dein Tag-für-Tag-Plan auf den Tag genau rechnet.
          </p>
        </div>

        <div class="quick-create-btns">
          <button type="button" class="btn sm" @click="openEntryModal(null, 'INCOME')">+ Einnahme</button>
          <button type="button" class="btn ghost sm" @click="openEntryModal(null, 'FIXED')">+ Fixkosten</button>
          <button type="button" class="btn ghost sm" @click="openEntryModal(null, 'SUBSCRIPTION')">+ Abo</button>
          <button type="button" class="btn ghost sm" @click="openEntryModal(null, 'ONCE_PAYMENT')">+ Einmalzahlung</button>
        </div>
      </div>

      <div class="sub-pills">
        <button
          v-for="tab in subTabs"
          :key="tab.id"
          type="button"
          class="pill-btn"
          :class="{ active: activeSub === tab.id }"
          @click="activeSub = tab.id"
        >
          {{ tab.label }}
        </button>
      </div>
    </article>

    <!-- ===== DAILY EXPENSES (ALLTAGSAUSGABEN IST-TAGEBUCH) ===== -->
    <template v-if="activeSub === 'daily'">
      <article class="panel daily-exp-panel">
        <div class="daily-summary-strip">
          <div>
            <span class="muted tiny">Ausgegeben in diesem Monat</span>
            <strong class="big-stat">{{ fmt(currentMonthDailySum) }}</strong>
          </div>
          <div v-if="monthlyPlannedLiving > 0">
            <span class="muted tiny">Geplantes Monats-Alltagsbudget</span>
            <strong class="big-stat">{{ fmt(monthlyPlannedLiving) }}</strong>
          </div>
          <div v-if="monthlyPlannedLiving > 0">
            <span class="muted tiny">Noch im Monatsbudget übrig</span>
            <strong class="big-stat" :class="monthlyPlannedLiving - currentMonthDailySum >= 0 ? 'pos-txt' : 'neg-txt'">
              {{ fmt(monthlyPlannedLiving - currentMonthDailySum) }}
            </strong>
          </div>
        </div>

        <form class="quick-expense-form" @submit.prevent="submitDailyExpense">
          <input v-model="expForm.date" type="date" class="input" required />
          <input v-model.trim="expForm.title" class="input" placeholder="Wofür? (z. B. Supermarkt, Kaffee, Tanken)" required />
          <select v-model="expForm.category" class="input">
            <option value="Lebensmittel">Lebensmittel</option>
            <option value="Essen & Trinken">Essen &amp; Trinken</option>
            <option value="Mobilität">Mobilität</option>
            <option value="Freizeit">Freizeit</option>
            <option value="Musik & Studio">Musik &amp; Studio</option>
            <option value="Sonstiges">Sonstiges</option>
          </select>
          <input v-model="expForm.amount" type="number" step="0.01" min="0.01" class="input" placeholder="Betrag (€)" required />
          <button type="submit" class="btn sm" :disabled="saving">{{ saving ? "..." : "+ Eintragen" }}</button>
        </form>

        <label class="sync-bal-check">
          <input v-model="expForm.deductBalance" type="checkbox" />
          <span class="muted tiny">Betrag beim Eintragen direkt vom aktuellen Kontostand abziehen</span>
        </label>

        <div v-if="dailyExpenses.length" class="entry-stack">
          <div v-for="exp in dailyExpenses" :key="exp.id" class="entry-row">
            <div class="er-left">
              <strong>{{ exp.title }}</strong>
              <span class="muted tiny">{{ formatDateDe(exp.date) }}{{ exp.category ? ` · ${exp.category}` : "" }}</span>
            </div>
            <div class="er-right">
              <strong class="neg-txt">−{{ fmt(exp.amount) }}</strong>
              <button type="button" class="icon-btn danger" title="Löschen" @click="deleteDailyExpense(exp)">✕</button>
            </div>
          </div>
        </div>
        <p v-else class="muted small">Noch keine Alltagsausgaben in diesem Zeitraum erfasst.</p>
      </article>
    </template>

    <!-- ===== RECURRING & PLANNED ENTRIES ===== -->
    <template v-else>
      <div class="sections-stack">
        <article
          v-for="sec in visibleSections"
          :key="sec.id"
          class="panel section-card"
        >
          <div class="sec-head">
            <div>
              <h3>{{ sec.title }}</h3>
              <span class="muted tiny">{{ sec.subtitle }}</span>
            </div>
            <div class="sec-head-right">
              <strong :class="sec.isIncome ? 'pos-txt' : ''">
                {{ sec.isIncome ? "+" : "−" }}{{ fmt(sec.total) }}{{ sec.unitLabel }}
              </strong>
              <button type="button" class="btn ghost sm" @click="openEntryModal(null, sec.presetKey)">
                + Hinzufügen
              </button>
            </div>
          </div>

          <div v-if="sec.items.length" class="entry-stack">
            <div
              v-for="item in sec.items"
              :key="item.id"
              class="entry-row"
              :class="{ paused: item.is_active === false }"
            >
              <div class="er-left">
                <div class="er-title-line">
                  <strong>{{ item.title }}</strong>
                  <span class="sched-tag" :class="{ 'default-hint': isDefaultDay(item) }">
                    {{ scheduleLabel(item) }}
                  </span>
                  <span v-if="item.category" class="cat-tag">{{ item.category }}</span>
                  <span v-if="item.is_active === false" class="paused-tag">Pausiert</span>
                </div>
                <span v-if="item.notes" class="muted tiny">{{ item.notes }}</span>
              </div>

              <div class="er-right">
                <div class="amt-col">
                  <strong :class="item.entry_type === 'INCOME' ? 'pos-txt' : 'neg-txt'">
                    {{ item.entry_type === "INCOME" ? "+" : "−" }}{{ fmt(item.amount) }}
                  </strong>
                  <span v-if="item.frequency !== 'MONTHLY' && item.frequency !== 'ONCE'" class="muted tiny">
                    ≈ {{ fmt(item.monthly_amount) }}/M.
                  </span>
                </div>

                <button
                  type="button"
                  class="icon-btn"
                  :title="item.is_active === false ? 'Aktivieren' : 'Pausieren'"
                  @click="toggleActive(item)"
                >
                  {{ item.is_active === false ? "▶" : "⏸" }}
                </button>
                <button type="button" class="icon-btn" title="Bearbeiten" @click="openEntryModal(item)">✎</button>
                <button type="button" class="icon-btn danger" title="Löschen" @click="deleteEntry(item)">✕</button>
              </div>
            </div>
          </div>
          <p v-else class="muted small empty-p">Noch keine Einträge in diesem Bereich.</p>
        </article>
      </div>
    </template>

    <!-- ===== ENTRY MODAL ===== -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ form.id ? "Posten bearbeiten" : "Neuen Posten eintragen" }}</h3>
          <button type="button" class="modal-close" @click="showModal = false">&times;</button>
        </div>

        <form class="modal-form" @submit.prevent="saveEntry">
          <div class="two-col">
            <label>
              Art des Postens
              <select v-model="form.entry_type" class="input">
                <option value="INCOME">💰 Einnahme (Gehalt, Nebenjob, GEMA...)</option>
                <option value="FIXED">🏠 Fixkosten (Miete, Strom, Vertrag...)</option>
                <option value="SUBSCRIPTION">🔄 Abo (Spotify, Netflix, Software...)</option>
                <option value="SAVING">🎯 Feste Sparrate</option>
                <option value="VARIABLE">📌 Geplante Ausgabe / Sonstiges</option>
              </select>
            </label>

            <label>
              Rhythmus
              <select v-model="form.frequency" class="input">
                <option value="MONTHLY">Monatlich</option>
                <option value="ONCE">Einmalig (festes Datum)</option>
                <option value="WEEKLY">Wöchentlich</option>
                <option value="YEARLY">Jährlich</option>
              </select>
            </label>
          </div>

          <label>
            Bezeichnung
            <input v-model.trim="form.title" class="input" placeholder="z. B. Gehalt, Miete, Spotify, Steuer" required />
          </label>

          <div class="two-col">
            <label>
              Betrag (€)
              <input v-model="form.amount" type="number" step="0.01" min="0.01" class="input" placeholder="0.00" required />
            </label>

            <label v-if="form.frequency === 'MONTHLY'">
              Tag im Monat (1–31)
              <input
                v-model="form.due_day"
                type="number"
                min="1"
                max="31"
                class="input"
                placeholder="z. B. 1 oder 28"
                required
              />
            </label>

            <label v-else>
              {{ form.frequency === "ONCE" ? "Fälligkeitsdatum" : "Start- / Stichtagsdatum" }}
              <input v-model="form.due_date" type="date" class="input" required />
            </label>
          </div>

          <div class="two-col">
            <label>
              Kategorie (optional)
              <input v-model.trim="form.category" class="input" placeholder="z. B. Wohnen, Musik, Streaming" />
            </label>
            <label v-if="form.frequency === 'MONTHLY'">
              Frühestes Startdatum (optional)
              <input v-model="form.due_date" type="date" class="input" />
            </label>
          </div>

          <label>
            Notiz (optional)
            <input v-model.trim="form.notes" class="input" placeholder="Optional" />
          </label>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showModal = false">Abbrechen</button>
            <button type="submit" class="btn" :disabled="saving">{{ saving ? "Speichere..." : "Speichern" }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import api from "../../api";
import {
  currentMonthIso,
  entryUsesDefaultDay,
  formatDateDe,
  formatMoney,
  round2,
  toNum,
  todayIso,
} from "../../utils/financeEngine";

const props = defineProps({
  project: { type: Object, default: null },
  entries: { type: Array, default: () => [] },
  dailyExpenses: { type: Array, default: () => [] },
  currency: { type: String, default: "EUR" },
});

const emit = defineEmits(["refresh", "adjust-balance", "notify"]);

const today = todayIso();
const saving = ref(false);
const activeSub = ref("all");

const subTabs = [
  { id: "all", label: "📋 Alle festen Posten" },
  { id: "income", label: "💰 Einnahmen" },
  { id: "fixed", label: "🏠 Fixkosten" },
  { id: "subs", label: "🔄 Abos" },
  { id: "once", label: "📌 Einmalzahlungen" },
  { id: "daily", label: "🧾 Alltagsausgaben (Ist)" },
];

function fmt(val) {
  return formatMoney(val, props.currency);
}

function isDefaultDay(entry) {
  return entryUsesDefaultDay(entry);
}

function scheduleLabel(entry) {
  if (entry.frequency === "ONCE") {
    return entry.due_date ? `Einmalig am ${formatDateDe(entry.due_date)}` : "Einmalig";
  }
  if (entry.frequency === "MONTHLY") {
    if (entry.due_day) return `Monatlich am ${entry.due_day}.`;
    if (entry.due_date) return `Monatlich ab ${formatDateDe(entry.due_date)}`;
    return "Monatlich am 1. (Standard)";
  }
  if (entry.frequency === "WEEKLY") {
    return entry.due_date ? `Wöchentlich (ab ${formatDateDe(entry.due_date)})` : "Wöchentlich";
  }
  if (entry.frequency === "YEARLY") {
    return entry.due_date ? `Jährlich (${formatDateDe(entry.due_date)})` : "Jährlich";
  }
  return entry.frequency;
}

function sumMonthly(list) {
  return round2(
    list
      .filter((e) => e.is_active !== false)
      .reduce((s, e) => s + toNum(e.monthly_amount ?? e.amount), 0)
  );
}

const allSections = computed(() => {
  const list = props.entries || [];
  const incomes = list.filter((e) => e.entry_type === "INCOME" && e.frequency !== "ONCE");
  const fixed = list.filter((e) => ["FIXED", "VARIABLE", "SAVING"].includes(e.entry_type) && e.frequency !== "ONCE");
  const subs = list.filter((e) => e.entry_type === "SUBSCRIPTION" && e.frequency !== "ONCE");
  const once = list
    .filter((e) => e.frequency === "ONCE")
    .sort((a, b) => (a.due_date || "").localeCompare(b.due_date || ""));

  return [
    {
      id: "income",
      title: "💰 Regelmäßige Einnahmen",
      subtitle: "Gehalt, Nebenjob, GEMA/Tantiemen, Unterhalt etc.",
      items: incomes,
      total: sumMonthly(incomes),
      unitLabel: " / Monat",
      isIncome: true,
      presetKey: "INCOME",
    },
    {
      id: "fixed",
      title: "🏠 Fixkosten & feste Sparraten",
      subtitle: "Miete, Strom, Handy, Internet, Versicherungen",
      items: fixed,
      total: sumMonthly(fixed),
      unitLabel: " / Monat",
      isIncome: false,
      presetKey: "FIXED",
    },
    {
      id: "subs",
      title: "🔄 Abonnements",
      subtitle: "Streaming, Cloud, Plugins, Fitnessstudio",
      items: subs,
      total: sumMonthly(subs),
      unitLabel: " / Monat",
      isIncome: false,
      presetKey: "SUBSCRIPTION",
    },
    {
      id: "once",
      title: "📌 Geplante Einmalzahlungen & Sonderposten",
      subtitle: "Zukünftige Rechnungen, Nachzahlungen oder einmalige Zuflüsse mit festem Datum",
      items: once,
      total: round2(once.filter((e) => e.is_active !== false && e.entry_type !== "INCOME").reduce((s, e) => s + toNum(e.amount), 0)),
      unitLabel: " offen geplant",
      isIncome: false,
      presetKey: "ONCE_PAYMENT",
    },
  ];
});

const visibleSections = computed(() => {
  if (activeSub.value === "all") return allSections.value;
  return allSections.value.filter((s) => s.id === activeSub.value);
});

// ── Entry CRUD Modal ───────────────────────────────────────────────────────
const showModal = ref(false);
const form = ref({
  id: null,
  title: "",
  entry_type: "FIXED",
  frequency: "MONTHLY",
  amount: "",
  due_day: "1",
  due_date: "",
  category: "",
  notes: "",
});

function openEntryModal(entry = null, presetKey = "FIXED") {
  if (entry) {
    form.value = {
      id: entry.id,
      title: entry.title,
      entry_type: entry.entry_type || "FIXED",
      frequency: entry.frequency || "MONTHLY",
      amount: String(entry.amount),
      due_day: entry.due_day ? String(entry.due_day) : "1",
      due_date: entry.due_date || "",
      category: entry.category || "",
      notes: entry.notes || "",
    };
  } else if (presetKey === "ONCE_PAYMENT") {
    form.value = {
      id: null,
      title: "",
      entry_type: "FIXED",
      frequency: "ONCE",
      amount: "",
      due_day: "",
      due_date: today,
      category: "",
      notes: "",
    };
  } else {
    form.value = {
      id: null,
      title: "",
      entry_type: presetKey || "FIXED",
      frequency: "MONTHLY",
      amount: "",
      due_day: "1",
      due_date: "",
      category: "",
      notes: "",
    };
  }
  showModal.value = true;
}

function openEntryModalWithPreset({ date = today, title = "", amount = "", entry_type = "FIXED", frequency = "ONCE" } = {}) {
  form.value = {
    id: null,
    title,
    entry_type,
    frequency,
    amount: amount ? String(amount) : "",
    due_day: "1",
    due_date: date || today,
    category: "",
    notes: "",
  };
  showModal.value = true;
}

defineExpose({ openEntryModalWithPreset });

async function saveEntry() {
  if (!props.project) return;
  saving.value = true;
  try {
    const isMonthly = form.value.frequency === "MONTHLY";
    const payload = {
      project: props.project.id,
      title: form.value.title,
      entry_type: form.value.entry_type,
      frequency: form.value.frequency,
      amount: round2(toNum(form.value.amount)),
      due_day: isMonthly ? Math.min(31, Math.max(1, Number(form.value.due_day || 1))) : null,
      due_date: form.value.due_date || null,
      category: form.value.category,
      notes: form.value.notes,
      is_active: true,
    };
    if (form.value.id) {
      await api.patch(`finance-entries/${form.value.id}/`, payload);
    } else {
      await api.post("finance-entries/", payload);
    }
    showModal.value = false;
    emit("notify", { type: "success", text: "Posten gespeichert." });
    emit("refresh");
  } catch (err) {
    emit("notify", { type: "error", text: err?.response?.data?.detail || "Posten konnte nicht gespeichert werden." });
  } finally {
    saving.value = false;
  }
}

async function toggleActive(item) {
  try {
    await api.patch(`finance-entries/${item.id}/`, {
      is_active: item.is_active === false,
    });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Status konnte nicht geändert werden." });
  }
}

async function deleteEntry(item) {
  if (!confirm(`„${item.title}“ löschen?`)) return;
  try {
    await api.delete(`finance-entries/${item.id}/`);
    emit("notify", { type: "success", text: "Posten gelöscht." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Löschen fehlgeschlagen." });
  }
}

// ── Daily Expenses CRUD ────────────────────────────────────────────────────
const expForm = ref({
  date: today,
  title: "",
  category: "Lebensmittel",
  amount: "",
  deductBalance: true,
});

const currentYm = currentMonthIso();
const currentMonthDailySum = computed(() =>
  (props.dailyExpenses || [])
    .filter((d) => (d.date || "").startsWith(currentYm))
    .reduce((s, d) => s + toNum(d.amount), 0)
);

const monthlyPlannedLiving = computed(() =>
  round2(toNum(props.project?.daily_living_budget, 0) * 30)
);

async function submitDailyExpense() {
  if (!props.project) return;
  saving.value = true;
  try {
    const amt = round2(toNum(expForm.value.amount));
    await api.post("daily-expenses/", {
      project: props.project.id,
      date: expForm.value.date || today,
      title: expForm.value.title,
      category: expForm.value.category,
      amount: amt,
    });
    if (expForm.value.deductBalance && amt > 0) {
      emit("adjust-balance", -amt);
    }
    expForm.value.title = "";
    expForm.value.amount = "";
    emit("notify", { type: "success", text: "Ausgabe eingetragen." });
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Ausgabe konnte nicht gespeichert werden (evtl. identischer Doppeleintrag)." });
  } finally {
    saving.value = false;
  }
}

async function deleteDailyExpense(exp) {
  if (!confirm(`Ausgabe „${exp.title}“ löschen?`)) return;
  try {
    await api.delete(`daily-expenses/${exp.id}/`);
    emit("refresh");
  } catch {
    emit("notify", { type: "error", text: "Konnte nicht gelöscht werden." });
  }
}
</script>

<style scoped>
.entries-tab {
  display: grid;
  gap: 16px;
}

.panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
}

.section-kicker {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand);
  margin-bottom: 4px;
}

.top-bar-panel {
  display: grid;
  gap: 14px;
}

.tb-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}

.tb-head h2 {
  margin: 0 0 4px;
  font-size: 1.22rem;
}

.tb-head p { margin: 0; max-width: 65ch; }

.quick-create-btns,
.sub-pills {
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

.sections-stack {
  display: grid;
  gap: 16px;
}

.section-card,
.daily-exp-panel {
  display: grid;
  gap: 14px;
}

.sec-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.sec-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

.sec-head-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.entry-stack {
  display: grid;
  gap: 8px;
}

.entry-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 11px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.entry-row.paused {
  opacity: 0.55;
}

.er-left {
  display: grid;
  gap: 2px;
}

.er-title-line {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 7px;
}

.sched-tag,
.cat-tag,
.paused-tag {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 11px;
  color: var(--muted);
}

.sched-tag.default-hint {
  border-color: rgba(96, 165, 250, 0.35);
  color: #60a5fa;
}

.er-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.amt-col {
  display: grid;
  justify-items: end;
  margin-right: 4px;
  font-variant-numeric: tabular-nums;
}

.icon-btn {
  width: 30px;
  height: 30px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  cursor: pointer;
}

.icon-btn:hover {
  border-color: var(--brand);
  color: var(--brand);
}

.icon-btn.danger:hover {
  border-color: #ef4444;
  color: #ef4444;
}

/* Daily Expenses */
.daily-summary-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.daily-summary-strip > div {
  display: grid;
  gap: 3px;
}

.big-stat {
  font-size: 1.3rem;
  font-weight: 800;
}

.quick-expense-form {
  display: grid;
  grid-template-columns: 150px 1.5fr 1fr 130px auto;
  gap: 8px;
}

.sync-bal-check {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.empty-p { margin: 0; }

/* Modal */
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pos-txt { color: #22c55e; }
.neg-txt { color: #ef4444; }
.tiny { font-size: 12px; }
.small { font-size: 13.5px; }

@media (max-width: 860px) {
  .quick-expense-form,
  .two-col {
    grid-template-columns: 1fr;
  }
  .entry-row {
    flex-direction: column;
    align-items: stretch;
  }
  .er-right {
    justify-content: flex-end;
  }
}
</style>

