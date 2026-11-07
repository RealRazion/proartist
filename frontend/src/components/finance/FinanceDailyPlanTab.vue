<template>
  <div class="daily-plan-tab">
    <!-- Top Control Panel -->
    <article class="panel controls-panel">
      <div class="controls-top">
        <div>
          <span class="section-kicker">Tag-für-Tag Besitz-Prognose</span>
          <h2>Wieviel Besitz solltest du an welchem Tag haben?</h2>
          <p class="muted small">
            Startet bei deinem aktuellen Kontostand und rechnet für jeden einzelnen Kalendertag alle geplanten Einnahmen, Fixkosten, Abos, Einmalzahlungen und Schuldenraten ein.
          </p>
        </div>

        <div class="horizon-group">
          <button
            v-for="opt in horizonOptions"
            :key="opt.days"
            type="button"
            class="pill-btn"
            :class="{ active: horizonDays === opt.days }"
            @click="horizonDays = opt.days"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <div class="controls-bottom">
        <!-- Mode Toggle: Fixed only vs Including Daily Living Budget -->
        <div class="mode-box">
          <span class="control-lbl">Berechnungs-Modus</span>
          <div class="seg-switch">
            <button
              type="button"
              class="seg-btn"
              :class="{ active: !includeLiving }"
              @click="includeLiving = false"
            >
              📌 Reine Fixkosten &amp; Raten
            </button>
            <button
              type="button"
              class="seg-btn"
              :class="{ active: includeLiving }"
              @click="enableLivingMode"
            >
              🛒 Inkl. Alltags-Tagesbudget
            </button>
          </div>
        </div>

        <div v-if="includeLiving" class="living-budget-inline">
          <div class="field-inline">
            <span class="control-lbl">Geplantes Alltagsbudget (€ / Tag)</span>
            <div class="inline-input-row">
              <input
                v-model="localDailyBudget"
                type="number"
                step="0.50"
                min="0"
                class="input sm-input"
                placeholder="z. B. 15.00"
              />
              <button
                type="button"
                class="btn sm ghost"
                :disabled="savingBudget || !isBudgetDirty"
                @click="persistDailyBudget"
              >
                {{ savingBudget ? "..." : isBudgetDirty ? "Speichern" : "Gespeichert ✓" }}
              </button>
            </div>
          </div>
          <span class="muted tiny">
            Entspricht ca. {{ fmt(Number(localDailyBudget || 0) * 30) }} / Monat für Essen &amp; Alltag
          </span>
        </div>

        <div class="start-date-box">
          <span class="control-lbl">Startdatum</span>
          <div class="inline-input-row">
            <input v-model="startDate" type="date" class="input sm-input" />
            <button
              v-if="startDate !== today"
              type="button"
              class="btn ghost tiny"
              @click="startDate = today"
            >
              Heute
            </button>
          </div>
        </div>
      </div>
    </article>

    <!-- Overdue Debt Alert if any -->
    <div v-if="sim.overdueDebts.length" class="alert-strip warning">
      <div class="alert-copy">
        <strong>⚠️ {{ sim.overdueDebts.length }} überfällige Rate(n) vor Startdatum ({{ fmt(overdueSum) }})</strong>
        <span>
          Diese Raten waren bereits vor dem {{ formatDateDe(startDate) }} fällig. Hake sie unter „Schulden &amp; Raten“ ab oder verschiebe den Termin, damit dein Plan exakt stimmt.
        </span>
      </div>
      <button type="button" class="btn sm ghost" @click="$emit('jump-to-debts')">Zu den Schulden →</button>
    </div>

    <!-- Default due_day hint if user has monthly entries without explicit due_day -->
    <div v-if="defaultDayEntriesCount > 0" class="alert-strip info">
      <div class="alert-copy">
        <strong>💡 Tipp für noch genauere Tageswerte:</strong>
        <span>
          Bei {{ defaultDayEntriesCount }} monatlichen Posten ist noch kein genauer Zahlungstag (1–31) hinterlegt — sie werden aktuell am 1. des Monats gerechnet. Du kannst unter „Buchungen &amp; Alltag“ den exakten Tag eintragen.
        </span>
      </div>
    </div>

    <!-- 4 Key Summary KPIs -->
    <div class="kpi-grid">
      <article class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Start-Besitz ({{ startDate === today ? "Heute" : formatDateShortDe(startDate) }})</span>
          <button type="button" class="link-chip" @click="$emit('open-balance-modal')">✎ Abgleichen</button>
        </div>
        <strong class="kpi-val" :class="{ negative: sim.startingBalance < 0 }">
          {{ fmt(sim.startingBalance) }}
        </strong>
        <span class="muted tiny">Aktueller Anker deines Plans</span>
      </article>

      <article class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Soll-Besitz in {{ horizonDays }} Tagen</span>
          <span class="delta-pill" :class="sim.netChange >= 0 ? 'pos' : 'neg'">
            {{ sim.netChange >= 0 ? "+" : "" }}{{ fmt(sim.netChange) }}
          </span>
        </div>
        <strong class="kpi-val" :class="{ positive: sim.endingBalance > 0, negative: sim.endingBalance < 0 }">
          {{ fmt(sim.endingBalance) }}
        </strong>
        <span class="muted tiny">Geplant am {{ formatDateDe(sim.endDateIso) }}</span>
      </article>

      <article class="kpi-card" :class="{ 'danger-card': sim.minBalance < 0, 'warn-card': sim.minBalance >= 0 && sim.minBalance < 100 }">
        <div class="kpi-top">
          <span class="kpi-label">Tiefster Stand (Engpass-Check)</span>
          <span class="status-dot" :class="sim.minBalance < 0 ? 'red' : sim.minBalance < 100 ? 'amber' : 'green'"></span>
        </div>
        <strong class="kpi-val" :class="{ negative: sim.minBalance < 0 }">
          {{ fmt(sim.minBalance) }}
        </strong>
        <span class="muted tiny">
          Am {{ formatDateDe(sim.minBalanceDate) }}
          <template v-if="sim.daysInNegative > 0"> · {{ sim.daysInNegative }} Tag(e) im Minus</template>
          <template v-else> · Kein Tag im Minus ✓</template>
        </span>
      </article>

      <article class="kpi-card">
        <div class="kpi-top">
          <span class="kpi-label">Getilgte Schulden im Zeitraum</span>
        </div>
        <strong class="kpi-val positive">
          {{ sim.debtReducedBy > 0 ? "−" + fmt(sim.debtReducedBy) : fmt(0) }}
        </strong>
        <span class="muted tiny">
          Restschuld danach: {{ fmt(sim.endingDebt) }}
          <template v-if="sim.debtsPaidOff.length"> · 🎉 {{ sim.debtsPaidOff.length }} abbezahlt!</template>
        </span>
      </article>
    </div>

    <!-- Interactive SVG Balance Curve -->
    <article class="panel chart-panel">
      <div class="chart-head">
        <div>
          <h3>Verlauf deines geplanten Besitzes</h3>
          <span class="muted tiny">Bewege die Maus oder tippe über die Kurve, um jeden einzelnen Tag zu prüfen</span>
        </div>
        <div v-if="hoveredDay" class="hover-readout">
          <span class="hover-date">{{ hoveredDay.weekday }}, {{ formatDateDe(hoveredDay.date) }}</span>
          <strong :class="hoveredDay.endBalance < 0 ? 'neg-txt' : 'pos-txt'">
            Soll-Besitz: {{ fmt(hoveredDay.endBalance) }}
          </strong>
          <span v-if="hoveredDay.delta !== 0" class="muted tiny">
            ({{ hoveredDay.delta > 0 ? "+" : "" }}{{ fmt(hoveredDay.delta) }} an diesem Tag)
          </span>
        </div>
      </div>

      <div
        ref="svgWrapRef"
        class="svg-chart-wrap"
        @mousemove="onChartMouseMove"
        @mouseleave="hoveredIndex = null"
        @touchmove.passive="onChartTouchMove"
      >
        <svg :viewBox="`0 0 ${chartW} ${chartH}`" preserveAspectRatio="none" class="balance-svg">
          <defs>
            <linearGradient id="finAreaGradPos" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#34d399" stop-opacity="0.34" />
              <stop offset="100%" stop-color="#34d399" stop-opacity="0.02" />
            </linearGradient>
            <linearGradient id="finAreaGradWarn" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.28" />
              <stop offset="100%" stop-color="#f87171" stop-opacity="0.16" />
            </linearGradient>
          </defs>

          <!-- Horizontal Grid Lines -->
          <line
            v-for="(g, gi) in chartGridLines"
            :key="`grid-${gi}`"
            :x1="padL"
            :x2="chartW - padR"
            :y1="g.y"
            :y2="g.y"
            class="grid-line"
          />

          <!-- Zero Euro Reference Line -->
          <line
            v-if="zeroLineY !== null"
            :x1="padL"
            :x2="chartW - padR"
            :y1="zeroLineY"
            :y2="zeroLineY"
            class="zero-line"
          />

          <!-- Area Fill -->
          <path
            v-if="areaPathD"
            :d="areaPathD"
            :fill="sim.minBalance < 0 ? 'url(#finAreaGradWarn)' : 'url(#finAreaGradPos)'"
          />

          <!-- Main Curve -->
          <path
            v-if="linePathD"
            :d="linePathD"
            fill="none"
            :stroke="sim.minBalance < 0 ? '#60a5fa' : '#10b981'"
            stroke-width="2.6"
            stroke-linejoin="round"
            stroke-linecap="round"
          />

          <!-- Min Point Marker -->
          <circle
            v-if="minPointCoords"
            :cx="minPointCoords.x"
            :cy="minPointCoords.y"
            r="4.5"
            :fill="sim.minBalance < 0 ? '#ef4444' : '#f59e0b'"
          />

          <!-- Hover Scrubber -->
          <template v-if="hoverCoords">
            <line
              :x1="hoverCoords.x"
              :x2="hoverCoords.x"
              :y1="padT"
              :y2="chartH - padB"
              class="hover-line"
            />
            <circle
              :cx="hoverCoords.x"
              :cy="hoverCoords.y"
              r="5.5"
              :fill="hoveredDay && hoveredDay.endBalance < 0 ? '#ef4444' : '#34d399'"
              stroke="#ffffff"
              stroke-width="2"
            />
          </template>
        </svg>

        <!-- Axis Overlays -->
        <div class="chart-y-labels">
          <span>{{ formatCompactMoney(chartMaxVal, currency) }}</span>
          <span v-if="zeroLineY !== null" class="zero-tag">0 €</span>
          <span>{{ formatCompactMoney(chartMinVal, currency) }}</span>
        </div>
        <div class="chart-x-labels">
          <span>{{ formatDateShortDe(sim.startDateIso) }}</span>
          <span>{{ formatDateShortDe(midDateIso) }}</span>
          <span>{{ formatDateShortDe(sim.endDateIso) }}</span>
        </div>
      </div>
    </article>

    <!-- View Mode Switcher & Filters -->
    <article class="panel ledger-panel">
      <div class="ledger-toolbar">
        <div class="seg-switch">
          <button
            type="button"
            class="seg-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            📋 Tages-Liste
          </button>
          <button
            type="button"
            class="seg-btn"
            :class="{ active: viewMode === 'calendar' }"
            @click="viewMode = 'calendar'"
          >
            🗓️ Monats-Kalender
          </button>
        </div>

        <div v-if="viewMode === 'list'" class="ledger-filters">
          <div class="filter-pills">
            <button
              type="button"
              class="pill-btn sm"
              :class="{ active: listFilter === 'all' }"
              @click="listFilter = 'all'"
            >
              Alle Tage ({{ sim.timeline.length }})
            </button>
            <button
              type="button"
              class="pill-btn sm"
              :class="{ active: listFilter === 'events' }"
              @click="listFilter = 'events'"
            >
              Nur Buchungstage ({{ eventDaysCount }})
            </button>
            <button
              v-if="warningDaysCount > 0"
              type="button"
              class="pill-btn sm warn"
              :class="{ active: listFilter === 'warnings' }"
              @click="listFilter = 'warnings'"
            >
              ⚠️ Engpässe ({{ warningDaysCount }})
            </button>
          </div>

          <select v-if="availableMonths.length > 1" v-model="selectedMonthFilter" class="input month-select">
            <option value="ALL">Alle Monate</option>
            <option v-for="m in availableMonths" :key="m.ym" :value="m.ym">{{ m.label }}</option>
          </select>
        </div>

        <div v-else class="calendar-nav">
          <button
            type="button"
            class="btn ghost sm"
            :disabled="calendarMonthIndex <= 0"
            @click="calendarMonthIndex--"
          >
            ←
          </button>
          <strong class="cal-month-title">{{ currentCalendarMonthLabel }}</strong>
          <button
            type="button"
            class="btn ghost sm"
            :disabled="calendarMonthIndex >= availableMonths.length - 1"
            @click="calendarMonthIndex++"
          >
            →
          </button>
        </div>
      </div>

      <!-- ===== LIST VIEW ===== -->
      <div v-if="viewMode === 'list'" class="day-list">
        <div v-if="!filteredDays.length" class="empty-box">
          <p class="muted">Keine Tage für diesen Filter gefunden.</p>
        </div>

        <div
          v-for="day in filteredDays"
          :key="day.date"
          class="day-row"
          :class="{
            'is-today': day.isToday,
            'is-negative': day.endBalance < 0,
            'is-tight': day.status === 'TIGHT',
            'is-weekend': day.isWeekend && !day.events.length,
          }"
        >
          <div class="day-date-col">
            <div class="day-weekday-line">
              <span class="weekday-tag">{{ day.weekday }}</span>
              <strong class="date-num">{{ formatDateDe(day.date) }}</strong>
              <span v-if="day.isToday" class="today-pill">Heute</span>
            </div>
            <div class="day-sub-badges">
              <span v-if="day.remainingDebt > 0" class="muted tiny">
                Restschuld: {{ fmt(day.remainingDebt) }}
              </span>
              <span
                v-if="(day.isToday || day.manualSpent > 0) && day.dailyBudgetTarget > 0"
                class="daily-budget-status-pill"
                :class="day.dailyBudgetRemaining >= 0 ? 'ok' : 'over'"
              >
                {{
                  day.dailyBudgetRemaining >= 0
                    ? `Noch ${fmt(day.dailyBudgetRemaining)} vom Tagesbudget übrig`
                    : `${fmt(Math.abs(day.dailyBudgetRemaining))} über Tagesbudget`
                }}
              </span>
            </div>
          </div>

          <div class="day-events-col">
            <template v-if="day.events.length || day.livingDeduction > 0">
              <span
                v-for="ev in day.events"
                :key="ev.id"
                class="ev-chip"
                :class="evChipClass(ev)"
              >
                <span class="ev-title">
                  {{ ev.kind === "DAILY_EXPENSE" ? `💸 ${ev.title}` : ev.title }}
                </span>
                <strong>{{ ev.amount > 0 ? "+" : "" }}{{ fmt(ev.amount) }}</strong>
                <span v-if="ev.alreadyInBalance" class="already-tag" title="Bereits im Kontostand abgezogen">✓ gebucht</span>
                <span v-if="ev.paidOffToday" class="paid-off-star">🎉 Abbezahlt!</span>
                <button
                  v-if="ev.kind === 'DAILY_EXPENSE' && ev.sourceId"
                  type="button"
                  class="ev-del-btn"
                  title="Tägliche Ausgabe löschen"
                  @click.stop="$emit('delete-daily-expense', ev.sourceId)"
                >
                  &times;
                </button>
              </span>
              <span v-if="day.livingDeduction > 0" class="ev-chip ev-living">
                <span>{{ day.manualSpent > 0 ? "Rest-Tagesbudget" : "Alltagsbudget" }}</span>
                <strong>−{{ fmt(day.livingDeduction) }}</strong>
              </span>
            </template>
            <span v-else class="muted tiny quiet-day-lbl">Keine Buchungen / Ausgaben</span>
          </div>

          <div class="day-balance-col">
            <span
              v-if="day.delta !== 0"
              class="day-delta"
              :class="day.delta > 0 ? 'pos-txt' : 'neg-txt'"
            >
              {{ day.delta > 0 ? "+" : "" }}{{ fmt(day.delta) }}
            </span>
            <span v-else class="day-delta muted">±0,00 €</span>

            <div class="soll-besitz-box">
              <span class="soll-lbl">Soll-Besitz</span>
              <strong class="soll-val" :class="{ 'neg-txt': day.endBalance < 0, 'pos-txt': day.endBalance > 0 }">
                {{ fmt(day.endBalance) }}
              </strong>
            </div>

            <div class="day-row-actions">
              <button
                type="button"
                class="quick-exp-add"
                title="Tägliche Ausgabe für diesen Tag eintragen"
                @click="$emit('log-daily-expense', day.date)"
              >
                💸 +Ausgabe
              </button>
              <button
                type="button"
                class="quick-day-add"
                title="Feste Buchung oder Einnahme an diesem Tag planen"
                @click="$emit('quick-add-on-date', day.date)"
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- ===== CALENDAR GRID VIEW ===== -->
      <div v-else class="calendar-view-wrap">
        <div class="cal-weekdays">
          <span v-for="wd in ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']" :key="wd">{{ wd }}</span>
        </div>

        <div class="cal-grid">
          <div
            v-for="(cell, idx) in calendarCells"
            :key="`cal-${idx}`"
            class="cal-cell"
            :class="{
              empty: !cell.dayData && !cell.inMonth,
              'out-of-range': cell.inMonth && !cell.dayData,
              selected: selectedCalendarDay && cell.date === selectedCalendarDay.date,
              today: cell.dayData?.isToday,
              negative: cell.dayData && cell.dayData.endBalance < 0,
              tight: cell.dayData && cell.dayData.status === 'TIGHT',
            }"
            @click="cell.dayData && (selectedCalendarDate = cell.date)"
          >
            <template v-if="cell.inMonth">
              <div class="cal-cell-head">
                <span class="cal-day-num">{{ cell.dayNum }}</span>
                <div v-if="cell.dayData?.events?.length" class="cal-dots">
                  <span
                    v-for="(ev, ei) in cell.dayData.events.slice(0, 4)"
                    :key="ei"
                    class="cal-dot"
                    :class="ev.amount > 0 ? 'dot-inc' : ev.kind === 'DEBT' || ev.kind === 'CREDIT' ? 'dot-debt' : 'dot-out'"
                  ></span>
                </div>
              </div>

              <template v-if="cell.dayData">
                <strong
                  class="cal-balance"
                  :class="{ 'neg-txt': cell.dayData.endBalance < 0 }"
                >
                  {{ formatCompactMoney(cell.dayData.endBalance, currency) }}
                </strong>
                <span v-if="cell.dayData.delta !== 0" class="cal-delta muted">
                  {{ cell.dayData.delta > 0 ? "+" : "" }}{{ formatCompactMoney(cell.dayData.delta, currency) }}
                </span>
              </template>
              <span v-else class="muted tiny">Vor Start</span>
            </template>
          </div>
        </div>

        <!-- Selected Day Inspector -->
        <div v-if="selectedCalendarDay" class="cal-inspector">
          <div class="inspector-head">
            <div>
              <span class="section-kicker">{{ selectedCalendarDay.weekday }}, {{ formatDateDe(selectedCalendarDay.date) }}</span>
              <h4>Geplanter Soll-Besitz am Abend: {{ fmt(selectedCalendarDay.endBalance) }}</h4>
            </div>
            <div class="inspector-btn-group">
              <button
                type="button"
                class="btn sm"
                @click="$emit('log-daily-expense', selectedCalendarDay.date)"
              >
                💸 + Tägliche Ausgabe
              </button>
              <button
                type="button"
                class="btn sm ghost"
                @click="$emit('quick-add-on-date', selectedCalendarDay.date)"
              >
                + Feste Buchung
              </button>
            </div>
          </div>

          <div class="inspector-metrics">
            <span>Start am Morgen: <strong>{{ fmt(selectedCalendarDay.startBalance) }}</strong></span>
            <span>Manuell ausgegeben: <strong>{{ fmt(selectedCalendarDay.manualSpent || 0) }}</strong></span>
            <span v-if="selectedCalendarDay.dailyBudgetTarget > 0">
              Vom Tagesbudget übrig:
              <strong :class="selectedCalendarDay.dailyBudgetRemaining >= 0 ? 'pos-txt' : 'neg-txt'">
                {{ fmt(selectedCalendarDay.dailyBudgetRemaining) }}
              </strong>
            </span>
            <span>Offene Schulden: <strong>{{ fmt(selectedCalendarDay.remainingDebt) }}</strong></span>
          </div>

          <div v-if="selectedCalendarDay.events.length || selectedCalendarDay.livingDeduction > 0" class="inspector-events">
            <div v-for="ev in selectedCalendarDay.events" :key="ev.id" class="inspector-ev-row">
              <span>{{ ev.title }} <em v-if="ev.paidOffToday">🎉 Letzte Rate!</em></span>
              <strong :class="ev.amount > 0 ? 'pos-txt' : 'neg-txt'">
                {{ ev.amount > 0 ? "+" : "" }}{{ fmt(ev.amount) }}
              </strong>
            </div>
            <div v-if="selectedCalendarDay.livingDeduction > 0" class="inspector-ev-row">
              <span>Geplantes Alltags-Tagesbudget</span>
              <strong class="neg-txt">−{{ fmt(selectedCalendarDay.livingDeduction) }}</strong>
            </div>
          </div>
          <p v-else class="muted small">An diesem Tag stehen keine festen Buchungen an.</p>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import {
  daysInMonth,
  entryUsesDefaultDay,
  formatCompactMoney,
  formatDateDe,
  formatDateShortDe,
  formatMoney,
  formatMonthYearDe,
  getWeekdayIndexMondayFirst,
  safeIsoDate,
  simulateDailyTimeline,
  toNum,
  todayIso,
} from "../../utils/financeEngine";

const props = defineProps({
  project: { type: Object, default: null },
  entries: { type: Array, default: () => [] },
  debts: { type: Array, default: () => [] },
  dailyExpenses: { type: Array, default: () => [] },
  currency: { type: String, default: "EUR" },
  savingBudget: { type: Boolean, default: false },
});

const emit = defineEmits([
  "open-balance-modal",
  "save-daily-budget",
  "quick-add-on-date",
  "log-daily-expense",
  "delete-daily-expense",
  "jump-to-debts",
]);

const today = todayIso();
const startDate = ref(today);
const horizonDays = ref(90);
const includeLiving = ref(false);
const localDailyBudget = ref("15");
const viewMode = ref("list");
const listFilter = ref("all");
const selectedMonthFilter = ref("ALL");
const calendarMonthIndex = ref(0);
const selectedCalendarDate = ref(today);
const hoveredIndex = ref(null);
const svgWrapRef = ref(null);

const horizonOptions = [
  { days: 30, label: "30 Tage" },
  { days: 90, label: "90 Tage" },
  { days: 180, label: "6 Monate" },
  { days: 365, label: "1 Jahr" },
];

watch(
  () => props.project,
  (proj) => {
    if (!proj) return;
    const saved = toNum(proj.daily_living_budget, 0);
    if (saved > 0) {
      localDailyBudget.value = String(saved);
      includeLiving.value = true;
    } else if (!localDailyBudget.value) {
      localDailyBudget.value = "15";
    }
  },
  { immediate: true }
);

const isBudgetDirty = computed(() => {
  const saved = toNum(props.project?.daily_living_budget, 0);
  return Math.abs(toNum(localDailyBudget.value, 0) - saved) > 0.005;
});

function enableLivingMode() {
  includeLiving.value = true;
  if (toNum(localDailyBudget.value, 0) <= 0) {
    const saved = toNum(props.project?.daily_living_budget, 0);
    localDailyBudget.value = saved > 0 ? String(saved) : "15";
  }
}

function persistDailyBudget() {
  emit("save-daily-budget", Math.max(0, toNum(localDailyBudget.value, 0)));
}

function fmt(value) {
  return formatMoney(value, props.currency);
}

const sim = computed(() =>
  simulateDailyTimeline({
    startDateIso: startDate.value || today,
    days: horizonDays.value,
    startingBalance: toNum(props.project?.current_balance, 0),
    dispoLimit: toNum(props.project?.dispo_limit, 0),
    dispoUsed: toNum(props.project?.dispo_used, 0),
    emergencyBuffer: toNum(props.project?.emergency_buffer_target, 0),
    entries: props.entries,
    debts: props.debts,
    dailyExpenses: props.dailyExpenses,
    includeDailyBudget: includeLiving.value,
    dailyLivingBudget: toNum(localDailyBudget.value, 0),
  })
);

const overdueSum = computed(() =>
  sim.value.overdueDebts.reduce((s, d) => s + toNum(d.amount), 0)
);

const defaultDayEntriesCount = computed(
  () => (props.entries || []).filter((e) => e.is_active !== false && entryUsesDefaultDay(e)).length
);

const eventDaysCount = computed(
  () => sim.value.timeline.filter((d) => d.events.length > 0).length
);

const warningDaysCount = computed(
  () => sim.value.timeline.filter((d) => d.endBalance < 0 || d.status === "TIGHT").length
);

const availableMonths = computed(() => {
  const seen = new Set();
  const list = [];
  for (const d of sim.value.timeline) {
    if (!seen.has(d.monthKey)) {
      seen.add(d.monthKey);
      list.push({ ym: d.monthKey, label: formatMonthYearDe(d.monthKey, false) });
    }
  }
  return list;
});

watch(availableMonths, (months) => {
  if (calendarMonthIndex.value >= months.length) {
    calendarMonthIndex.value = Math.max(0, months.length - 1);
  }
  if (selectedMonthFilter.value !== "ALL" && !months.some((m) => m.ym === selectedMonthFilter.value)) {
    selectedMonthFilter.value = "ALL";
  }
});

const filteredDays = computed(() => {
  return sim.value.timeline.filter((d) => {
    if (selectedMonthFilter.value !== "ALL" && d.monthKey !== selectedMonthFilter.value) {
      return false;
    }
    if (listFilter.value === "events") return d.events.length > 0;
    if (listFilter.value === "warnings") return d.endBalance < 0 || d.status === "TIGHT";
    return true;
  });
});

// ── SVG Chart Geometry ─────────────────────────────────────────────────────
const chartW = 920;
const chartH = 220;
const padL = 12;
const padR = 12;
const padT = 18;
const padB = 20;

const chartBounds = computed(() => {
  const vals = sim.value.timeline.map((d) => d.endBalance);
  vals.push(sim.value.startingBalance);
  let minV = Math.min(...vals, 0);
  let maxV = Math.max(...vals, 100);
  if (Math.abs(maxV - minV) < 50) {
    maxV += 50;
    minV -= 20;
  }
  const pad = (maxV - minV) * 0.08;
  return { min: minV - pad, max: maxV + pad };
});

const chartMinVal = computed(() => chartBounds.value.min);
const chartMaxVal = computed(() => chartBounds.value.max);

function xForIndex(idx) {
  const total = Math.max(1, sim.value.timeline.length - 1);
  return padL + (idx / total) * (chartW - padL - padR);
}

function yForValue(val) {
  const { min, max } = chartBounds.value;
  const ratio = (val - min) / Math.max(1, max - min);
  return chartH - padB - ratio * (chartH - padT - padB);
}

const chartPoints = computed(() =>
  sim.value.timeline.map((d, idx) => ({
    x: xForIndex(idx),
    y: yForValue(d.endBalance),
    day: d,
  }))
);

const linePathD = computed(() => {
  const pts = chartPoints.value;
  if (!pts.length) return "";
  return pts.map((p, i) => `${i === 0 ? "M" : "L"}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(" ");
});

const zeroLineY = computed(() => {
  const { min, max } = chartBounds.value;
  if (min <= 0 && max >= 0) return yForValue(0);
  return null;
});

const areaPathD = computed(() => {
  const pts = chartPoints.value;
  if (!pts.length) return "";
  const baseLineY = zeroLineY.value !== null ? zeroLineY.value : chartH - padB;
  const first = pts[0];
  const last = pts[pts.length - 1];
  return `${linePathD.value} L${last.x.toFixed(1)},${baseLineY.toFixed(1)} L${first.x.toFixed(1)},${baseLineY.toFixed(1)} Z`;
});

const chartGridLines = computed(() => {
  const rows = [0.25, 0.5, 0.75];
  return rows.map((r) => ({ y: padT + r * (chartH - padT - padB) }));
});

const minPointCoords = computed(() => {
  const idx = sim.value.timeline.findIndex((d) => d.date === sim.value.minBalanceDate);
  if (idx < 0) return null;
  return chartPoints.value[idx] || null;
});

const midDateIso = computed(() => {
  const mid = Math.floor(sim.value.timeline.length / 2);
  return sim.value.timeline[mid]?.date || sim.value.startDateIso;
});

const hoveredDay = computed(() => {
  if (hoveredIndex.value === null) return null;
  return sim.value.timeline[hoveredIndex.value] || null;
});

const hoverCoords = computed(() => {
  if (hoveredIndex.value === null) return null;
  return chartPoints.value[hoveredIndex.value] || null;
});

function updateHoverFromClientX(clientX) {
  const el = svgWrapRef.value;
  if (!el || !sim.value.timeline.length) return;
  const rect = el.getBoundingClientRect();
  const relX = Math.max(0, Math.min(1, (clientX - rect.left) / Math.max(1, rect.width)));
  const idx = Math.round(relX * (sim.value.timeline.length - 1));
  hoveredIndex.value = idx;
}

function onChartMouseMove(ev) {
  updateHoverFromClientX(ev.clientX);
}

function onChartTouchMove(ev) {
  if (ev.touches && ev.touches[0]) {
    updateHoverFromClientX(ev.touches[0].clientX);
  }
}

// ── Calendar View Helpers ──────────────────────────────────────────────────
const currentCalendarMonthObj = computed(
  () => availableMonths.value[calendarMonthIndex.value] || availableMonths.value[0] || null
);

const currentCalendarMonthLabel = computed(
  () => currentCalendarMonthObj.value?.label || ""
);

const dayLookup = computed(() => {
  const map = new Map();
  for (const d of sim.value.timeline) {
    map.set(d.date, d);
  }
  return map;
});

const calendarCells = computed(() => {
  const mObj = currentCalendarMonthObj.value;
  if (!mObj) return [];
  const year = Number.parseInt(mObj.ym.slice(0, 4), 10);
  const month = Number.parseInt(mObj.ym.slice(5, 7), 10);
  const firstIso = safeIsoDate(year, month, 1);
  const leadingBlanks = getWeekdayIndexMondayFirst(firstIso);
  const totalDays = daysInMonth(year, month);

  const cells = [];
  for (let b = 0; b < leadingBlanks; b++) {
    cells.push({ inMonth: false, dayNum: null, date: null, dayData: null });
  }
  for (let d = 1; d <= totalDays; d++) {
    const iso = safeIsoDate(year, month, d);
    cells.push({
      inMonth: true,
      dayNum: d,
      date: iso,
      dayData: dayLookup.value.get(iso) || null,
    });
  }
  return cells;
});

const selectedCalendarDay = computed(() => {
  if (selectedCalendarDate.value && dayLookup.value.has(selectedCalendarDate.value)) {
    return dayLookup.value.get(selectedCalendarDate.value);
  }
  return sim.value.timeline[0] || null;
});

function evChipClass(ev) {
  if (ev.amount > 0) return "ev-income";
  if (ev.kind === "DAILY_EXPENSE") return "ev-daily-expense";
  if (ev.kind === "DEBT" || ev.kind === "CREDIT") return "ev-debt";
  if (ev.kind === "SAVING") return "ev-saving";
  return "ev-outflow";
}
</script>

<style scoped>
.daily-plan-tab {
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

.controls-panel {
  display: grid;
  gap: 18px;
}

.controls-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}

.controls-top h2 {
  margin: 0 0 4px;
  font-size: 1.25rem;
}

.controls-top p {
  margin: 0;
  max-width: 68ch;
}

.horizon-group {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.pill-btn {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.16s ease;
}

.pill-btn.sm {
  padding: 6px 12px;
  font-size: 12.5px;
}

.pill-btn:hover {
  color: var(--text);
  border-color: var(--brand);
}

.pill-btn.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #ffffff;
}

.pill-btn.warn {
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}

.pill-btn.warn.active {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #ffffff;
}

.controls-bottom {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 18px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}

.control-lbl {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  margin-bottom: 6px;
}

.seg-switch {
  display: inline-flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 4px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.seg-btn {
  padding: 7px 13px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.seg-btn.active {
  background: var(--card);
  color: var(--text);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.16);
}

.living-budget-inline {
  display: grid;
  gap: 4px;
}

.inline-input-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sm-input {
  width: 145px;
  padding: 7px 11px;
  font-size: 13.5px;
}

.start-date-box {
  margin-left: auto;
}

/* Alerts */
.alert-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
  padding: 13px 18px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-size: 13px;
}

.alert-strip.warning {
  border-color: rgba(245, 158, 11, 0.38);
  background: rgba(245, 158, 11, 0.08);
}

.alert-strip.info {
  border-color: rgba(96, 165, 250, 0.3);
  background: rgba(96, 165, 250, 0.07);
}

.alert-copy {
  display: grid;
  gap: 2px;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.kpi-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 18px;
  display: grid;
  gap: 6px;
}

.kpi-card.danger-card {
  border-color: rgba(239, 68, 68, 0.45);
}

.kpi-card.warn-card {
  border-color: rgba(245, 158, 11, 0.4);
}

.kpi-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.kpi-label {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--muted);
}

.kpi-val {
  font-size: 1.45rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.kpi-val.positive,
.pos-txt {
  color: #22c55e;
}

.kpi-val.negative,
.neg-txt {
  color: #ef4444;
}

.link-chip {
  padding: 3px 9px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--brand);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
}

.delta-pill {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}

.delta-pill.pos {
  background: rgba(34, 197, 94, 0.14);
  color: #22c55e;
}

.delta-pill.neg {
  background: rgba(239, 68, 68, 0.14);
  color: #ef4444;
}

.status-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}

.status-dot.green { background: #22c55e; }
.status-dot.amber { background: #f59e0b; }
.status-dot.red { background: #ef4444; }

/* Chart */
.chart-panel {
  display: grid;
  gap: 12px;
}

.chart-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.chart-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

.hover-readout {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 12px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 13px;
}

.hover-date {
  font-weight: 600;
}

.svg-chart-wrap {
  position: relative;
  height: 220px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  overflow: hidden;
  cursor: crosshair;
}

.balance-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.grid-line {
  stroke: var(--border);
  stroke-dasharray: 3 3;
  stroke-width: 1;
}

.zero-line {
  stroke: #ef4444;
  stroke-dasharray: 6 4;
  stroke-width: 1.4;
  opacity: 0.75;
}

.hover-line {
  stroke: var(--brand);
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
}

.chart-y-labels {
  position: absolute;
  top: 8px;
  bottom: 24px;
  left: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  pointer-events: none;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
}

.zero-tag {
  color: #ef4444;
}

.chart-x-labels {
  position: absolute;
  bottom: 5px;
  left: 12px;
  right: 12px;
  display: flex;
  justify-content: space-between;
  pointer-events: none;
  font-size: 11px;
  color: var(--muted);
}

/* Ledger List */
.ledger-panel {
  display: grid;
  gap: 16px;
}

.ledger-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.ledger-filters {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filter-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.month-select {
  width: auto;
  min-width: 165px;
  padding: 6px 34px 6px 12px;
  font-size: 13px;
}

.day-list {
  display: grid;
  gap: 8px;
  max-height: 640px;
  overflow-y: auto;
  padding-right: 4px;
}

.day-row {
  display: grid;
  grid-template-columns: 200px minmax(0, 1fr) auto;
  align-items: center;
  gap: 14px;
  padding: 11px 14px;
  border-radius: 13px;
  background: var(--surface);
  border: 1px solid var(--border);
  transition: border-color 0.15s ease;
}

.day-row:hover {
  border-color: var(--brand);
}

.day-row.is-today {
  border-color: var(--brand);
  box-shadow: inset 3px 0 0 var(--brand);
}

.day-row.is-negative {
  border-color: rgba(239, 68, 68, 0.45);
  background: rgba(239, 68, 68, 0.05);
}

.day-row.is-tight {
  border-color: rgba(245, 158, 11, 0.32);
}

.day-row.is-weekend {
  opacity: 0.86;
}

.day-date-col {
  display: grid;
  gap: 2px;
}

.day-weekday-line {
  display: flex;
  align-items: center;
  gap: 7px;
}

.weekday-tag {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 24px;
  border-radius: 7px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--muted);
}

.date-num {
  font-size: 13.5px;
  font-variant-numeric: tabular-nums;
}

.today-pill {
  padding: 2px 7px;
  border-radius: 999px;
  background: var(--brand);
  color: #fff;
  font-size: 10.5px;
  font-weight: 700;
}

.day-events-col {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.ev-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  border: 1px solid var(--border);
  background: var(--card);
}

.ev-chip.ev-income {
  border-color: rgba(34, 197, 94, 0.35);
  background: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.ev-chip.ev-debt {
  border-color: rgba(168, 85, 247, 0.38);
  background: rgba(168, 85, 247, 0.1);
}

.ev-chip.ev-saving {
  border-color: rgba(56, 189, 248, 0.35);
  background: rgba(56, 189, 248, 0.1);
}

.ev-chip.ev-living {
  opacity: 0.85;
  font-size: 11.5px;
}

.ev-chip.ev-daily-expense {
  border-color: rgba(245, 158, 11, 0.42);
  background: rgba(245, 158, 11, 0.11);
}

.already-tag {
  font-size: 10px;
  padding: 1px 5px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.16);
  color: #22c55e;
  font-weight: 700;
}

.ev-del-btn {
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 14px;
  line-height: 1;
  padding: 0 2px;
  cursor: pointer;
}

.ev-del-btn:hover {
  color: #ef4444;
}

.day-sub-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}

.daily-budget-status-pill {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 999px;
}

.daily-budget-status-pill.ok {
  background: rgba(34, 197, 94, 0.12);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.daily-budget-status-pill.over {
  background: rgba(239, 68, 68, 0.14);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.35);
}

.day-row-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.quick-exp-add {
  padding: 5px 10px;
  border-radius: 8px;
  border: 1px solid rgba(245, 158, 11, 0.38);
  background: rgba(245, 158, 11, 0.1);
  color: var(--text);
  font-size: 11.5px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.15s ease;
}

.quick-exp-add:hover {
  border-color: var(--brand);
  background: color-mix(in srgb, var(--brand) 16%, var(--card));
}

.inspector-btn-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.paid-off-star {
  font-weight: 700;
  color: #22c55e;
}

.day-balance-col {
  display: flex;
  align-items: center;
  gap: 14px;
  justify-self: end;
}

.day-delta {
  font-size: 12.5px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  min-width: 78px;
  text-align: right;
}

.soll-besitz-box {
  display: grid;
  justify-items: end;
  min-width: 108px;
}

.soll-lbl {
  font-size: 10.5px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
}

.soll-val {
  font-size: 14.5px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.quick-day-add {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
}

.quick-day-add:hover {
  border-color: var(--brand);
  color: var(--brand);
}

/* Calendar Grid */
.calendar-nav {
  display: flex;
  align-items: center;
  gap: 10px;
}

.cal-month-title {
  min-width: 150px;
  text-align: center;
}

.calendar-view-wrap {
  display: grid;
  gap: 14px;
}

.cal-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 8px;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
}

.cal-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.cal-cell {
  min-height: 78px;
  padding: 8px 10px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  cursor: pointer;
  transition: all 0.14s ease;
}

.cal-cell.empty {
  background: transparent;
  border-color: transparent;
  cursor: default;
}

.cal-cell.out-of-range {
  opacity: 0.45;
  cursor: default;
}

.cal-cell:not(.empty):not(.out-of-range):hover {
  border-color: var(--brand);
}

.cal-cell.selected {
  border-color: var(--brand);
  box-shadow: 0 0 0 2px var(--ring);
}

.cal-cell.today {
  border-color: #34d399;
}

.cal-cell.negative {
  border-color: rgba(239, 68, 68, 0.5);
  background: rgba(239, 68, 68, 0.07);
}

.cal-cell-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cal-day-num {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
}

.cal-dots {
  display: flex;
  gap: 3px;
}

.cal-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.dot-inc { background: #22c55e; }
.dot-debt { background: #a855f7; }
.dot-out { background: #60a5fa; }

.cal-balance {
  font-size: 13px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.cal-delta {
  font-size: 10.5px;
}

.cal-inspector {
  padding: 16px 18px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 12px;
}

.inspector-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.inspector-head h4 {
  margin: 0;
  font-size: 1.05rem;
}

.inspector-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  font-size: 13px;
  color: var(--muted);
}

.inspector-events {
  display: grid;
  gap: 6px;
}

.inspector-ev-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 13px;
}

.tiny { font-size: 12px; }
.small { font-size: 13.5px; }

@media (max-width: 860px) {
  .day-row {
    grid-template-columns: 1fr;
    gap: 8px;
  }
  .day-balance-col {
    justify-self: stretch;
    justify-content: space-between;
    padding-top: 6px;
    border-top: 1px solid var(--border);
  }
  .start-date-box {
    margin-left: 0;
  }
  .cal-grid {
    gap: 4px;
  }
  .cal-cell {
    min-height: 64px;
    padding: 6px;
  }
  .cal-balance {
    font-size: 11px;
  }
}
</style>
