<template>
  <div class="longterm-tab">
    <!-- Controls Header -->
    <article class="panel head-panel">
      <div class="head-top">
        <div>
          <span class="section-kicker">Langzeit-Planung &amp; Analyse</span>
          <h2>Dein Weg aus den Schulden ins langfristige Plus</h2>
          <p class="muted small">
            Sobald eine Ratenschuld abbezahlt ist, fällt ihre Monatsrate hier automatisch weg — du siehst exakt, wann dein Cashflow aufatmet und wann du komplett schuldenfrei bist.
          </p>
        </div>

        <div class="horizon-pills">
          <button
            v-for="m in [12, 24, 36]"
            :key="m"
            type="button"
            class="pill-btn"
            :class="{ active: horizonMonths === m }"
            @click="horizonMonths = m"
          >
            {{ m }} Monate
          </button>
        </div>
      </div>

      <div class="head-bottom">
        <div class="strategy-group">
          <span class="ctrl-lbl">Tilgungs-Modus</span>
          <div class="seg-switch">
            <button
              type="button"
              class="seg-btn"
              :class="{ active: strategy === 'CURRENT' }"
              @click="strategy = 'CURRENT'"
            >
              📋 Normaler Ratenplan
            </button>
            <button
              type="button"
              class="seg-btn"
              :class="{ active: strategy === 'SNOWBALL' }"
              @click="strategy = 'SNOWBALL'"
            >
              ❄️ Schneeball-Rollover
            </button>
            <button
              type="button"
              class="seg-btn"
              :class="{ active: strategy === 'PRESSURE' }"
              @click="strategy = 'PRESSURE'"
            >
              ⚡ Ratendruck-Fokus
            </button>
          </div>
        </div>

        <label class="toggle-line">
          <input v-model="includeLiving" type="checkbox" />
          <span class="small">
            Alltagsbudget ({{ fmt(dailyBudget) }}/Tag ≈ {{ fmt(dailyBudget * 30) }}/Monat) abziehen
          </span>
        </label>
      </div>
    </article>

    <!-- 4 Milestone KPI Cards -->
    <div class="milestone-grid">
      <article class="kpi-card">
        <span class="kpi-lbl">🏁 100 % Schuldenfrei</span>
        <strong class="kpi-val pos-txt">
          {{ roadmap.initialDebtTotal <= 0 ? "Bereits auf 0 € 🎉" : roadmap.debtFreeLabel }}
        </strong>
        <span class="muted tiny">
          <template v-if="roadmap.initialDebtTotal <= 0">Keine aktiven Schulden offen</template>
          <template v-else-if="roadmap.monthsUntilDebtFree !== null">
            In {{ roadmap.monthsUntilDebtFree }} Monat{{ roadmap.monthsUntilDebtFree === 1 ? "" : "en" }} (Startschuld: {{ fmt(roadmap.initialDebtTotal) }})
          </template>
          <template v-else>Monatsraten prüfen (aktuell keine Tilgung hinterlegt)</template>
        </span>
      </article>

      <article class="kpi-card">
        <span class="kpi-lbl">⚖️ Netto-Vermögen (Besitz − Schulden)</span>
        <strong class="kpi-val" :class="roadmap.initialNetWorth >= 0 ? 'pos-txt' : 'neg-txt'">
          {{ fmt(roadmap.initialNetWorth) }}
        </strong>
        <span class="muted tiny">
          <template v-if="roadmap.initialNetWorth >= 0">Dein Besitz übersteigt bereits deine Schulden ✓</template>
          <template v-else-if="roadmap.monthsUntilBreakEven !== null">
            Break-Even (≥ 0 €) im <strong>{{ roadmap.breakEvenLabel }}</strong>
          </template>
          <template v-else>Break-Even außerhalb des gewählten Zeitraums</template>
        </span>
      </article>

      <article class="kpi-card">
        <span class="kpi-lbl">💰 Geplanter Besitz in {{ horizonMonths }} Monaten</span>
        <strong class="kpi-val" :class="roadmap.horizonEndBalance >= 0 ? 'pos-txt' : 'neg-txt'">
          {{ fmt(roadmap.horizonEndBalance) }}
        </strong>
        <span class="muted tiny">
          Netto-Vermögen dann: <strong>{{ fmt(roadmap.horizonEndNetWorth) }}</strong>
        </span>
      </article>

      <article class="kpi-card">
        <div class="kpi-row-top">
          <span class="kpi-lbl">🩺 Aktuelle Belastungs-Quoten</span>
          <span class="health-badge" :class="healthInfo.cls">{{ healthInfo.label }}</span>
        </div>
        <div class="ratio-bars">
          <div class="ratio-line">
            <span>Fix &amp; Abos</span>
            <strong>{{ healthInfo.fixedPct }} %</strong>
          </div>
          <div class="ratio-line">
            <span>Schuldenraten</span>
            <strong :class="{ 'neg-txt': healthInfo.debtPct > 25 }">{{ healthInfo.debtPct }} %</strong>
          </div>
          <div class="ratio-line">
            <span>Frei für Alltag &amp; Sparen</span>
            <strong class="pos-txt">{{ healthInfo.freePct }} %</strong>
          </div>
        </div>
      </article>
    </div>

    <!-- Dual Trajectory Chart: Balance vs Remaining Debt -->
    <article class="panel chart-card">
      <div class="chart-header">
        <div>
          <h3>Langzeit-Entwicklung: Geplanter Besitz vs. Restschuld ({{ horizonMonths }} Monate)</h3>
          <div class="legend-row">
            <span class="leg-item"><i class="leg-dot bal"></i> Geplanter Kontostand</span>
            <span class="leg-item"><i class="leg-dot debt"></i> Verbleibende Gesamtschuld</span>
          </div>
        </div>

        <div v-if="hoveredMonth" class="hover-pill">
          <strong>{{ hoveredMonth.fullLabel }}</strong>
          <span class="pos-txt">Besitz: {{ fmt(hoveredMonth.endingBalance) }}</span>
          <span class="debt-txt">Restschuld: {{ fmt(hoveredMonth.remainingDebt) }}</span>
        </div>
      </div>

      <div
        ref="chartWrapRef"
        class="dual-svg-wrap"
        @mousemove="onMouseMove"
        @mouseleave="hoverIdx = null"
      >
        <svg :viewBox="`0 0 ${svgW} ${svgH}`" preserveAspectRatio="none" class="dual-svg">
          <!-- Zero Reference Line -->
          <line
            v-if="zeroY !== null"
            :x1="padX"
            :x2="svgW - padX"
            :y1="zeroY"
            :y2="zeroY"
            class="zero-ref"
          />

          <!-- Debt Curve (dashed purple/red) -->
          <path
            v-if="debtPathD"
            :d="debtPathD"
            fill="none"
            stroke="#c084fc"
            stroke-width="2.5"
            stroke-dasharray="6 4"
          />

          <!-- Balance Curve (solid green/blue) -->
          <path
            v-if="balancePathD"
            :d="balancePathD"
            fill="none"
            stroke="#22c55e"
            stroke-width="3"
            stroke-linejoin="round"
            stroke-linecap="round"
          />

          <!-- Hover Indicator -->
          <template v-if="hoverPoint">
            <line :x1="hoverPoint.x" :x2="hoverPoint.x" :y1="padY" :y2="svgH - padY" class="hover-v" />
            <circle :cx="hoverPoint.x" :cy="hoverPoint.balY" r="5" fill="#22c55e" stroke="#fff" stroke-width="2" />
            <circle :cx="hoverPoint.x" :cy="hoverPoint.debtY" r="5" fill="#c084fc" stroke="#fff" stroke-width="2" />
          </template>
        </svg>

        <div class="y-axis-overlay">
          <span>{{ formatCompactMoney(yBounds.max, currency) }}</span>
          <span>{{ formatCompactMoney(yBounds.min, currency) }}</span>
        </div>
      </div>
    </article>

    <!-- Debt Payoff Milestones Strip -->
    <article v-if="roadmap.payoffSchedule.length" class="panel milestones-panel">
      <div class="sec-head">
        <div>
          <span class="section-kicker">Entschuldungs-Etappen</span>
          <h3>Wann fällt welche Rate weg?</h3>
        </div>
      </div>

      <div class="etappen-grid">
        <div v-for="(item, idx) in roadmap.payoffSchedule" :key="item.id" class="etappe-card">
          <div class="etappe-top">
            <span class="etappe-step">#{{ idx + 1 }}</span>
            <span class="etappe-date">{{ item.paidOffLabel }}</span>
          </div>
          <strong>{{ item.name }}</strong>
          <div class="etappe-meta">
            <span>Rest: {{ fmt(item.initialRemaining) }}</span>
            <span v-if="item.minRate > 0" class="pos-txt">+{{ fmt(item.minRate) }}/Monat frei danach</span>
          </div>
        </div>
      </div>
    </article>

    <!-- Month-by-Month Projection Table -->
    <article class="panel table-panel">
      <div class="sec-head">
        <div>
          <span class="section-kicker">Monats-Matrix</span>
          <h3>Alle {{ horizonMonths }} Monate im Detail</h3>
        </div>
      </div>

      <div class="table-scroll">
        <table class="lt-table">
          <thead>
            <tr>
              <th>Monat</th>
              <th>Einnahmen</th>
              <th>Fix &amp; Abos</th>
              <th v-if="includeLiving">Alltag</th>
              <th>Schuldenraten</th>
              <th>Sparen</th>
              <th>Monats-Saldo</th>
              <th>Restschuld</th>
              <th>Soll-Besitz</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="m in roadmap.months"
              :key="m.monthKey"
              :class="{ 'row-neg': m.endingBalance < 0, 'row-milestone': m.paidOffDebts.length > 0 }"
            >
              <td>
                <div class="m-cell">
                  <strong>{{ m.label }}</strong>
                  <span v-for="dName in m.paidOffDebts" :key="dName" class="free-chip">
                    🎉 {{ dName }} 0 €!
                  </span>
                </div>
              </td>
              <td class="num pos-txt">+{{ fmt(m.income) }}</td>
              <td class="num">−{{ fmt(m.fixedCosts + m.subscriptions + m.plannedOnce) }}</td>
              <td v-if="includeLiving" class="num muted">−{{ fmt(m.livingCosts) }}</td>
              <td class="num debt-txt">
                {{ m.debtPayment > 0 ? "−" + fmt(m.debtPayment) : "0,00 € ✓" }}
              </td>
              <td class="num">{{ m.savingsContribution > 0 ? fmt(m.savingsContribution) : "–" }}</td>
              <td class="num" :class="m.netCashflow >= 0 ? 'pos-txt' : 'neg-txt'">
                <strong>{{ m.netCashflow >= 0 ? "+" : "" }}{{ fmt(m.netCashflow) }}</strong>
              </td>
              <td class="num">{{ fmt(m.remainingDebt) }}</td>
              <td class="num" :class="m.endingBalance >= 0 ? 'pos-txt' : 'neg-txt'">
                <strong>{{ fmt(m.endingBalance) }}</strong>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import {
  formatCompactMoney,
  formatMoney,
  simulateLongTermRoadmap,
  toNum,
} from "../../utils/financeEngine";

const props = defineProps({
  project: { type: Object, default: null },
  entries: { type: Array, default: () => [] },
  debts: { type: Array, default: () => [] },
  savingsGoals: { type: Array, default: () => [] },
  currency: { type: String, default: "EUR" },
});

const horizonMonths = ref(24);
const strategy = ref("CURRENT");
const includeLiving = ref(true);
const hoverIdx = ref(null);
const chartWrapRef = ref(null);

const dailyBudget = computed(() => toNum(props.project?.daily_living_budget, 0));

const currentSavedTotal = computed(() =>
  (props.savingsGoals || []).reduce((s, g) => s + toNum(g.current_amount, 0), 0)
);

function fmt(val) {
  return formatMoney(val, props.currency);
}

const roadmap = computed(() =>
  simulateLongTermRoadmap({
    horizonMonths: horizonMonths.value,
    startingBalance: toNum(props.project?.current_balance, 0),
    startingSavings: currentSavedTotal.value,
    dispoUsed: toNum(props.project?.dispo_used, 0),
    monthlySavingsTarget: toNum(props.project?.monthly_savings_target, 0),
    dailyLivingBudget: dailyBudget.value,
    includeLivingBudget: includeLiving.value && dailyBudget.value > 0,
    entries: props.entries,
    debts: props.debts,
    strategy: strategy.value,
  })
);

const healthInfo = computed(() => {
  const first = roadmap.value.months[0];
  if (!first || first.income <= 0) {
    return { fixedPct: 0, debtPct: 0, freePct: 0, label: "Einnahmen eintragen", cls: "neutral" };
  }
  const inc = first.income;
  const fixed = first.fixedCosts + first.subscriptions;
  const debt = first.debtPayment;
  const fixedPct = Math.round((fixed / inc) * 100);
  const debtPct = Math.round((debt / inc) * 100);
  const freePct = Math.max(0, 100 - fixedPct - debtPct);

  let label = "Stabil";
  let cls = "good";
  if (fixedPct + debtPct >= 85) {
    label = "Hohe Last";
    cls = "danger";
  } else if (debtPct >= 25 || fixedPct + debtPct >= 70) {
    label = "Angespannt";
    cls = "warn";
  }
  return { fixedPct, debtPct, freePct, label, cls };
});

// ── Dual Chart Geometry ────────────────────────────────────────────────────
const svgW = 920;
const svgH = 220;
const padX = 16;
const padY = 18;

const yBounds = computed(() => {
  const vals = [0];
  for (const m of roadmap.value.months) {
    vals.push(m.endingBalance, m.remainingDebt);
  }
  let min = Math.min(...vals);
  let max = Math.max(...vals, 100);
  if (Math.abs(max - min) < 100) max += 100;
  const pad = (max - min) * 0.08;
  return { min: min - pad, max: max + pad };
});

function xAt(i) {
  const n = Math.max(1, roadmap.value.months.length - 1);
  return padX + (i / n) * (svgW - padX * 2);
}

function yAt(v) {
  const { min, max } = yBounds.value;
  return svgH - padY - ((v - min) / Math.max(1, max - min)) * (svgH - padY * 2);
}

const balancePathD = computed(() =>
  roadmap.value.months
    .map((m, i) => `${i === 0 ? "M" : "L"}${xAt(i).toFixed(1)},${yAt(m.endingBalance).toFixed(1)}`)
    .join(" ")
);

const debtPathD = computed(() =>
  roadmap.value.months
    .map((m, i) => `${i === 0 ? "M" : "L"}${xAt(i).toFixed(1)},${yAt(m.remainingDebt).toFixed(1)}`)
    .join(" ")
);

const zeroY = computed(() => {
  const { min, max } = yBounds.value;
  if (min <= 0 && max >= 0) return yAt(0);
  return null;
});

const hoveredMonth = computed(() =>
  hoverIdx.value !== null ? roadmap.value.months[hoverIdx.value] || null : null
);

const hoverPoint = computed(() => {
  if (hoverIdx.value === null || !hoveredMonth.value) return null;
  return {
    x: xAt(hoverIdx.value),
    balY: yAt(hoveredMonth.value.endingBalance),
    debtY: yAt(hoveredMonth.value.remainingDebt),
  };
});

function onMouseMove(ev) {
  const el = chartWrapRef.value;
  if (!el || !roadmap.value.months.length) return;
  const rect = el.getBoundingClientRect();
  const rel = Math.max(0, Math.min(1, (ev.clientX - rect.left) / Math.max(1, rect.width)));
  hoverIdx.value = Math.round(rel * (roadmap.value.months.length - 1));
}
</script>

<style scoped>
.longterm-tab {
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

.head-panel {
  display: grid;
  gap: 16px;
}

.head-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 14px;
}

.head-top h2 {
  margin: 0 0 4px;
  font-size: 1.25rem;
}

.head-top p {
  margin: 0;
  max-width: 68ch;
}

.horizon-pills {
  display: flex;
  gap: 6px;
}

.pill-btn {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
}

.pill-btn.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #ffffff;
}

.head-bottom {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}

.ctrl-lbl {
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
  padding: 7px 12px;
  border-radius: 9px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.seg-btn.active {
  background: var(--card);
  color: var(--text);
}

.toggle-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

/* KPI Milestones */
.milestone-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(225px, 1fr));
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

.kpi-lbl {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--muted);
}

.kpi-val {
  font-size: 1.4rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.kpi-row-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.health-badge {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.health-badge.good { background: rgba(34, 197, 94, 0.14); color: #22c55e; }
.health-badge.warn { background: rgba(245, 158, 11, 0.14); color: #f59e0b; }
.health-badge.danger { background: rgba(239, 68, 68, 0.14); color: #ef4444; }
.health-badge.neutral { background: var(--surface); color: var(--muted); }

.ratio-bars {
  display: grid;
  gap: 4px;
  font-size: 12.5px;
}

.ratio-line {
  display: flex;
  justify-content: space-between;
}

/* Chart */
.chart-card {
  display: grid;
  gap: 12px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.chart-header h3 {
  margin: 0 0 4px;
  font-size: 1.05rem;
}

.legend-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--muted);
}

.leg-item {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.leg-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.leg-dot.bal { background: #22c55e; }
.leg-dot.debt { background: #c084fc; }

.hover-pill {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 12px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 12.5px;
}

.dual-svg-wrap {
  position: relative;
  height: 220px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  overflow: hidden;
  cursor: crosshair;
}

.dual-svg {
  width: 100%;
  height: 100%;
  display: block;
}

.zero-ref {
  stroke: #ef4444;
  stroke-dasharray: 5 4;
  stroke-width: 1.3;
  opacity: 0.65;
}

.hover-v {
  stroke: var(--brand);
  stroke-width: 1.4;
  stroke-dasharray: 4 3;
}

.y-axis-overlay {
  position: absolute;
  top: 8px;
  bottom: 8px;
  left: 10px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
  pointer-events: none;
}

/* Milestones Etappen */
.milestones-panel,
.table-panel {
  display: grid;
  gap: 14px;
}

.sec-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

.etappen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}

.etappe-card {
  padding: 13px 15px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 6px;
}

.etappe-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.etappe-step {
  padding: 2px 7px;
  border-radius: 6px;
  background: var(--card);
  font-weight: 700;
  color: var(--brand);
}

.etappe-date {
  font-weight: 700;
  color: #22c55e;
}

.etappe-meta {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
}

/* Table */
.table-scroll {
  overflow-x: auto;
}

.lt-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.lt-table th {
  text-align: left;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  color: var(--muted);
  font-size: 11.5px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}

.lt-table td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  white-space: nowrap;
}

.lt-table td.num,
.lt-table th:not(:first-child) {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.lt-table tr.row-neg {
  background: rgba(239, 68, 68, 0.05);
}

.lt-table tr.row-milestone {
  background: rgba(34, 197, 94, 0.05);
}

.m-cell {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.free-chip {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.14);
  color: #22c55e;
  font-size: 11px;
  font-weight: 700;
}

.pos-txt { color: #22c55e; }
.neg-txt { color: #ef4444; }
.debt-txt { color: #c084fc; }
.tiny { font-size: 12px; }
.small { font-size: 13.5px; }
</style>

