<template>
  <div class="simulator-tab">
    <!-- Smart Tool Selector Cards -->
    <div class="tool-selector-grid">
      <button
        v-for="t in tools"
        :key="t.id"
        type="button"
        class="tool-nav-card"
        :class="{ active: activeTool === t.id }"
        @click="activeTool = t.id"
      >
        <span class="tool-ico">{{ t.icon }}</span>
        <div class="tool-copy">
          <strong>{{ t.title }}</strong>
          <span>{{ t.subtitle }}</span>
        </div>
      </button>
    </div>

    <!-- =====================================================================
         TOOL 1: ZEITRAUM- & TAGESBUDGET-SIMULATOR (DATUM A -> B + SPAREN)
         ===================================================================== -->
    <div v-if="activeTool === 'period'" class="sim-split-layout">
      <!-- Left Inputs -->
      <article class="panel sim-inputs-card">
        <div class="card-head">
          <span class="section-kicker">Zeitraum- &amp; Spar-Rechner</span>
          <h2>Wieviel kannst du von Datum A bis Datum B täglich ausgeben?</h2>
          <p class="muted small">
            Wähle deinen Zeitraum, dein verfügbares Geld und dein Sparziel — das Tool rechnet alle festen Buchungen dazwischen automatisch mit ein.
          </p>
        </div>

        <!-- Quick Presets -->
        <div class="preset-row">
          <button type="button" class="chip-btn" @click="applyPreset('month-end')">Bis Monatsende</button>
          <button type="button" class="chip-btn" @click="applyPreset('next-payday')">Bis nächstes Gehalt</button>
          <button type="button" class="chip-btn" @click="applyPreset('7d')">Nächste 7 Tage</button>
          <button type="button" class="chip-btn" @click="applyPreset('14d')">Nächste 14 Tage</button>
          <button type="button" class="chip-btn" @click="applyPreset('30d')">Nächste 30 Tage</button>
          <button type="button" class="chip-btn" @click="applyPreset('90d')">Nächste 90 Tage</button>
        </div>

        <!-- Date A & Date B -->
        <div class="form-two-col">
          <div class="field-box">
            <span class="field-lbl">Von (Datum A)</span>
            <input v-model="periodStart" type="date" class="input" />
          </div>
          <div class="field-box">
            <div class="lbl-row">
              <span class="field-lbl">Bis (Datum B)</span>
              <span class="days-badge">{{ periodResult.totalDays }} Tage</span>
            </div>
            <input v-model="periodEnd" type="date" :min="periodStart" class="input" />
          </div>
        </div>

        <!-- Starting Money -->
        <div class="sub-block">
          <div class="lbl-row">
            <span class="field-lbl">Start-Geld am {{ formatDateShortDe(periodStart) }}</span>
            <div class="mini-switch">
              <button
                type="button"
                class="mini-sw-btn"
                :class="{ active: useRealBalance }"
                @click="useRealBalance = true"
              >
                Kontostand ({{ fmt(currentBalance) }})
              </button>
              <button
                type="button"
                class="mini-sw-btn"
                :class="{ active: !useRealBalance }"
                @click="enableCustomStartMoney"
              >
                Eigener Betrag
              </button>
            </div>
          </div>

          <div class="form-two-col">
            <div v-if="!useRealBalance" class="field-box">
              <span class="muted tiny">Eigener Startbetrag (€)</span>
              <input v-model="customStartMoney" type="number" step="0.01" class="input" placeholder="z. B. 500.00" />
            </div>
            <div class="field-box" :class="{ 'full-span': useRealBalance }">
              <span class="muted tiny">+ Zusätzliches Extra-Geld im Zeitraum (optional, €)</span>
              <input v-model="extraBonusMoney" type="number" step="0.01" min="0" class="input" placeholder="0.00 (z. B. Verkauf, Bonus)" />
            </div>
          </div>
        </div>

        <!-- Savings & Buffer Block -->
        <div class="sub-block highlight-sub">
          <div class="lbl-row">
            <span class="field-lbl">💰 Geld sparen &amp; Puffer sichern</span>
          </div>

          <div class="savings-mode-pills">
            <button
              v-for="m in savingsModes"
              :key="m.id"
              type="button"
              class="chip-btn"
              :class="{ active: savingsMode === m.id }"
              @click="selectSavingsMode(m.id)"
            >
              {{ m.label }}
            </button>
          </div>

          <div class="form-two-col">
            <div class="field-box">
              <span class="muted tiny">{{ currentSavingsLabel }}</span>
              <input v-model="savingsValue" type="number" step="1" min="0" class="input" />
              <div class="quick-val-row">
                <button
                  v-for="qv in quickSavingsPresets"
                  :key="qv"
                  type="button"
                  class="tiny-preset"
                  @click="savingsValue = String(qv)"
                >
                  {{ savingsMode === 'PERCENT' ? `${qv} %` : `${qv} €` }}
                </button>
              </div>
            </div>

            <div class="field-box">
              <span class="muted tiny">Eiserne Konto-Untergrenze / Puffer (€)</span>
              <input v-model="safetyFloor" type="number" step="10" min="0" class="input" placeholder="0.00" />
              <span class="muted tiny">Wird an keinem Tag unterschritten</span>
            </div>
          </div>
        </div>

        <!-- Scheduled Bookings inside [A..B] -->
        <div class="sub-block">
          <div class="lbl-row">
            <label class="toggle-line">
              <input v-model="includeScheduled" type="checkbox" />
              <span class="field-lbl" style="margin:0">Feste Einnahmen, Abos, Fixkosten &amp; Raten einbeziehen</span>
            </label>
            <button
              v-if="includeScheduled && periodResult.occurrences.length"
              type="button"
              class="link-btn"
              @click="showOccurrences = !showOccurrences"
            >
              {{ showOccurrences ? "Ausblenden ▲" : `${periodResult.occurrences.length} Posten prüfen ▼` }}
            </button>
          </div>

          <div v-if="includeScheduled" class="sched-summary-row">
            <span class="pos-txt">+{{ fmt(periodResult.scheduledIncome) }} Einnahmen</span>
            <span class="neg-txt">−{{ fmt(periodResult.scheduledOutflow) }} Abbuchungen &amp; Raten</span>
          </div>

          <div v-if="includeScheduled && showOccurrences && periodResult.occurrences.length" class="occ-list">
            <p class="muted tiny" style="margin:0 0 6px">
              Hake einzelne Posten testweise ab, um zu sehen, wie sich dein Tagesbudget verändert:
            </p>
            <div
              v-for="occ in periodResult.occurrences"
              :key="occ.key"
              role="button"
              tabindex="0"
              class="occ-item"
              :class="{ 'is-disabled': !occ.enabled }"
              @click="toggleOccurrence(occ.key)"
              @keydown.enter.prevent="toggleOccurrence(occ.key)"
              @keydown.space.prevent="toggleOccurrence(occ.key)"
            >
              <input
                type="checkbox"
                :checked="occ.enabled"
                @click.stop
                @change="toggleOccurrence(occ.key)"
              />
              <span class="occ-date">{{ formatDateShortDe(occ.date) }}</span>
              <span class="occ-title">{{ occ.title }}</span>
              <strong :class="occ.amount > 0 ? 'pos-txt' : 'neg-txt'">
                {{ occ.amount > 0 ? "+" : "" }}{{ fmt(occ.amount) }}
              </strong>
            </div>
          </div>
        </div>
      </article>

      <!-- Right Live Output Board -->
      <aside class="sim-results-col">
        <article class="panel result-hero-card">
          <span class="section-kicker">Dein Ergebnis ({{ periodResult.totalDays }} Tage)</span>

          <div class="big-daily-box">
            <span class="big-lbl">Theoretisch täglich frei ausgebbar</span>
            <strong
              class="big-amount"
              :class="periodResult.theoreticalDailyBudget >= 0 ? 'pos-txt' : 'neg-txt'"
            >
              {{ fmt(periodResult.theoreticalDailyBudget) }}
              <small>/ Tag</small>
            </strong>
            <div class="sub-rates">
              <span>Pro Woche: <strong>{{ fmt(periodResult.theoreticalWeeklyBudget) }}</strong></span>
              <span>Gesamt frei: <strong>{{ fmt(periodResult.totalNetSpendable) }}</strong></span>
            </div>
          </div>

          <!-- Smart Mid-Period Bottleneck Warning -->
          <div v-if="periodResult.hasMidPeriodBottleneck" class="bottleneck-callout">
            <div class="bn-title">
              <span>⚡ Cashflow-Engpass vor Geldeingang erkannt!</span>
            </div>
            <p class="small" style="margin:0">
              Bevor spätere Einnahmen eintreffen, hast du bis zum
              <strong>{{ formatDateDe(periodResult.bottleneckDate) }}</strong> einen Zwischen-Engpass.
              Damit du zwischendurch nicht unter deinen Puffer ({{ fmt(periodResult.safetyFloor) }}) rutschst, gib bis dahin maximal aus:
            </p>
            <div class="bn-safe-val">
              <span>Engpass-sicheres Tagesbudget:</span>
              <strong :class="periodResult.safeDailyBudget >= 0 ? 'amber-txt' : 'neg-txt'">
                {{ fmt(periodResult.safeDailyBudget) }} / Tag
              </strong>
            </div>
          </div>

          <!-- Formula Breakdown -->
          <div class="calc-waterfall">
            <div class="wf-row">
              <span>Start-Geld + Extra</span>
              <strong>{{ fmt(periodResult.startingMoney + periodResult.extraIncome) }}</strong>
            </div>
            <div v-if="includeScheduled" class="wf-row">
              <span>+ Geplante Einnahmen im Zeitraum</span>
              <strong class="pos-txt">+{{ fmt(periodResult.scheduledIncome) }}</strong>
            </div>
            <div v-if="includeScheduled" class="wf-row">
              <span>− Fixkosten, Abos &amp; Schuldenraten</span>
              <strong class="neg-txt">−{{ fmt(periodResult.scheduledOutflow) }}</strong>
            </div>
            <div v-if="periodResult.safetyFloor > 0" class="wf-row">
              <span>− Eiserner Konto-Puffer</span>
              <strong>−{{ fmt(periodResult.safetyFloor) }}</strong>
            </div>
            <div class="wf-row save-highlight">
              <span>− Dein geplantes Erspartes</span>
              <strong class="cyan-txt">−{{ fmt(periodResult.plannedSavings) }}</strong>
            </div>
            <div class="wf-divider"></div>
            <div class="wf-row total">
              <span>= Frei zum Ausgeben ({{ periodResult.totalDays }} Tage)</span>
              <strong>{{ fmt(periodResult.totalNetSpendable) }}</strong>
            </div>
          </div>

          <div class="adopt-row">
            <button
              v-if="adoptableBudget > 0"
              type="button"
              class="btn sm"
              @click="$emit('adopt-daily-budget', adoptableBudget)"
            >
              ✓ {{ fmt(adoptableBudget) }}/Tag als Alltagsbudget übernehmen
            </button>
          </div>
        </article>

        <!-- Reverse Tester Slider -->
        <article class="panel reverse-card">
          <span class="section-kicker">Umgekehrter Spar-Tester</span>
          <h3>Was bleibt übrig, wenn ich weniger ausgebe?</h3>
          <p class="muted tiny">
            Teste eine konkrete tägliche Ausgabengrenze und sieh sofort deinen Kontostand am {{ formatDateDe(periodResult.endDateIso) }}:
          </p>

          <div class="slider-control">
            <input
              v-model="testDailySpend"
              type="range"
              min="0"
              :max="sliderMaxDaily"
              step="0.5"
              class="range-slider"
            />
            <div class="slider-input-wrap">
              <input v-model="testDailySpend" type="number" step="0.5" min="0" class="input sm-num" />
              <span class="muted small">€ / Tag</span>
            </div>
          </div>

          <div class="reverse-metrics">
            <div class="rev-box">
              <span class="muted tiny">Ausgaben gesamt ({{ periodResult.totalDays }} T.)</span>
              <strong>{{ fmt(periodResult.reverseCheck.totalSpend) }}</strong>
            </div>
            <div class="rev-box">
              <span class="muted tiny">Kontostand am {{ formatDateShortDe(periodResult.endDateIso) }}</span>
              <strong :class="periodResult.reverseCheck.projectedEndBalance >= 0 ? 'pos-txt' : 'neg-txt'">
                {{ fmt(periodResult.reverseCheck.projectedEndBalance) }}
              </strong>
            </div>
            <div class="rev-box">
              <span class="muted tiny">Tiefster Zwischenstand</span>
              <strong :class="periodResult.reverseCheck.minBalanceDuringPeriod < 0 ? 'neg-txt' : ''">
                {{ fmt(periodResult.reverseCheck.minBalanceDuringPeriod) }}
                <small class="muted">({{ formatDateShortDe(periodResult.reverseCheck.minBalanceDate) }})</small>
              </strong>
            </div>
          </div>
        </article>
      </aside>
    </div>

    <!-- =====================================================================
         TOOL 2: KAUF-CHECK ("KANN ICH MIR DAS LEISTEN?")
         ===================================================================== -->
    <div v-else-if="activeTool === 'purchase'" class="sim-split-layout">
      <article class="panel sim-inputs-card">
        <div class="card-head">
          <span class="section-kicker">90-Tage Cashflow-Prüfung</span>
          <h2>Kann ich mir diesen Kauf leisten, ohne ins Minus zu rutschen?</h2>
          <p class="muted small">
            Selbst wenn heute genug Geld auf dem Konto liegt, können Miete oder Schuldenraten in 2 Wochen ein Loch reißen. Hier prüfst du jeden Kauf vorab gegen deinen 90-Tage-Plan.
          </p>
        </div>

        <div class="form-two-col">
          <div class="field-box">
            <span class="field-lbl">Was möchtest du kaufen?</span>
            <input v-model.trim="purchaseForm.title" class="input" placeholder="z. B. Kopfhörer, Jacke, Plugin" />
          </div>
          <div class="field-box">
            <span class="field-lbl">Gesamtpreis (€)</span>
            <input v-model="purchaseForm.amount" type="number" step="0.01" min="0" class="input" placeholder="120.00" />
          </div>
        </div>

        <div class="form-two-col">
          <div class="field-box">
            <span class="field-lbl">Geplantes Kaufdatum</span>
            <input v-model="purchaseForm.date" type="date" class="input" />
          </div>
          <div class="field-box">
            <span class="field-lbl">Zahlungsart</span>
            <select v-model="purchaseForm.installments" class="input">
              <option :value="1">Sofort komplett bezahlen (1x)</option>
              <option :value="3">3 Monatsraten (0 %)</option>
              <option :value="6">6 Monatsraten (0 %)</option>
              <option :value="12">12 Monatsraten (0 %)</option>
            </select>
          </div>
        </div>

        <label class="toggle-line">
          <input v-model="purchaseIncludeLiving" type="checkbox" />
          <span class="small">Geplantes Alltags-Tagesbudget ({{ fmt(projectDailyBudget) }}/Tag) in der 90-Tage-Prüfung mit abziehen</span>
        </label>
      </article>

      <aside class="sim-results-col">
        <article
          class="panel verdict-card"
          :class="`verdict-${purchaseEval.verdict.toLowerCase()}`"
        >
          <div class="verdict-badge-row">
            <span class="verdict-pill">
              <template v-if="purchaseEval.verdict === 'SAFE'">🟢 Sicher machbar</template>
              <template v-else-if="purchaseEval.verdict === 'TIGHT'">🟡 Knapp — Puffer schmilzt</template>
              <template v-else>🔴 Gefahr — Konto rutscht ins Minus!</template>
            </span>
          </div>

          <h3>
            <template v-if="purchaseEval.totalCost <= 0">Gib links einen Preis ein</template>
            <template v-else-if="purchaseEval.verdict === 'SAFE'">
              Dein Konto bleibt in den nächsten 90 Tagen durchgehend stabil im Plus.
            </template>
            <template v-else-if="purchaseEval.verdict === 'TIGHT'">
              Kein Minus, aber am {{ formatDateDe(purchaseEval.afterMinBalanceDate) }} bleiben nur {{ fmt(purchaseEval.afterMinBalance) }} übrig.
            </template>
            <template v-else>
              Achtung: Durch diesen Kauf fällst du am {{ formatDateDe(purchaseEval.afterMinBalanceDate) }} auf {{ fmt(purchaseEval.afterMinBalance) }}!
            </template>
          </h3>

          <div class="calc-waterfall">
            <div class="wf-row">
              <span>Kaufbetrag / Rate</span>
              <strong>
                {{ purchaseEval.installments > 1 ? `${purchaseEval.installments}× ${fmt(purchaseEval.installmentAmount)}` : fmt(purchaseEval.totalCost) }}
              </strong>
            </div>
            <div class="wf-row">
              <span>Tiefster Kontostand OHNE Kauf (90 T.)</span>
              <strong>{{ fmt(purchaseEval.baselineMinBalance) }}</strong>
            </div>
            <div class="wf-row">
              <span>Tiefster Kontostand MIT Kauf (90 T.)</span>
              <strong :class="purchaseEval.afterMinBalance < 0 ? 'neg-txt' : 'pos-txt'">
                {{ fmt(purchaseEval.afterMinBalance) }}
              </strong>
            </div>
            <div class="wf-row">
              <span>Auswirkung auf 30-Tage-Tagesbudget</span>
              <strong class="neg-txt">{{ fmt(purchaseEval.dailyBudgetImpact30d) }} / Tag</strong>
            </div>
          </div>

          <div
            v-if="purchaseEval.verdict !== 'SAFE' && purchaseEval.totalCost > 0"
            class="safe-date-tip"
          >
            <template v-if="purchaseEval.earliestSafeDate">
              💡 <strong>Besserer Zeitpunkt:</strong> Wenn du bis zum
              <strong>{{ formatDateDe(purchaseEval.earliestSafeDate) }}</strong> wartest, bleibt dein Puffer sicher!
              <button
                type="button"
                class="link-btn"
                @click="purchaseForm.date = purchaseEval.earliestSafeDate"
              >
                Datum testen →
              </button>
            </template>
            <template v-else>
              💡 In den nächsten 60 Tagen ist dieser Betrag ohne zusätzliches Einkommen oder Sparen zu riskant.
            </template>
          </div>

          <div v-if="purchaseEval.totalCost > 0" class="adopt-row">
            <button
              v-if="purchaseEval.installments === 1"
              type="button"
              class="btn ghost sm"
              @click="$emit('create-planned-from-sim', { title: purchaseForm.title || 'Geplanter Kauf', amount: purchaseEval.totalCost, due_date: purchaseForm.date })"
            >
              + Als geplante Einmalzahlung vormerken
            </button>
          </div>
        </article>
      </aside>
    </div>

    <!-- =====================================================================
         TOOL 3: SPAR-PLANER & ECHTE SPARZIELE
         ===================================================================== -->
    <div v-else-if="activeTool === 'savings'" class="sim-split-layout">
      <!-- Interactive Savings Calculator -->
      <article class="panel sim-inputs-card">
        <div class="card-head">
          <span class="section-kicker">Spar-Rechner</span>
          <h2>Wie schnell wächst dein Rücklagen-Polster?</h2>
          <p class="muted small">
            Rechne aus, wie viel du täglich/monatlich für ein Ziel weglegen musst — oder wie viel du mit kleinen täglichen Beträgen aufbaust.
          </p>
        </div>

        <div class="savings-mode-pills">
          <button
            type="button"
            class="chip-btn"
            :class="{ active: savCalcDirection === 'GOAL_TO_RATE' }"
            @click="savCalcDirection = 'GOAL_TO_RATE'"
          >
            🎯 Zielbetrag → nötige Sparrate
          </button>
          <button
            type="button"
            class="chip-btn"
            :class="{ active: savCalcDirection === 'RATE_TO_WEALTH' }"
            @click="savCalcDirection = 'RATE_TO_WEALTH'"
          >
            📈 Feste Sparrate → Endvermögen
          </button>
        </div>

        <template v-if="savCalcDirection === 'GOAL_TO_RATE'">
          <div class="form-two-col">
            <div class="field-box">
              <span class="field-lbl">Wunsch-Zielbetrag (€)</span>
              <input v-model="goalCalc.target" type="number" step="10" min="0" class="input" placeholder="1000" />
            </div>
            <div class="field-box">
              <span class="field-lbl">Schon angespart (€)</span>
              <input v-model="goalCalc.current" type="number" step="10" min="0" class="input" placeholder="0" />
            </div>
          </div>
          <div class="field-box">
            <span class="field-lbl">Zieldatum</span>
            <input v-model="goalCalc.targetDate" type="date" :min="today" class="input" />
          </div>

          <div class="sav-calc-output">
            <div class="sav-kpi">
              <span class="muted tiny">Nötig pro Tag</span>
              <strong class="cyan-txt">{{ fmt(goalCalcResult.perDay) }}</strong>
            </div>
            <div class="sav-kpi">
              <span class="muted tiny">Nötig pro Woche</span>
              <strong>{{ fmt(goalCalcResult.perWeek) }}</strong>
            </div>
            <div class="sav-kpi">
              <span class="muted tiny">Nötig pro Monat</span>
              <strong>{{ fmt(goalCalcResult.perMonth) }}</strong>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="form-two-col">
            <div class="field-box">
              <span class="field-lbl">Sparbetrag (€)</span>
              <input v-model="rateCalc.amount" type="number" step="1" min="0" class="input" />
            </div>
            <div class="field-box">
              <span class="field-lbl">Rhythmus</span>
              <select v-model="rateCalc.unit" class="input">
                <option value="DAY">Pro Tag (z. B. Kleingeld / Kaffee-Verzicht)</option>
                <option value="WEEK">Pro Woche</option>
                <option value="MONTH">Pro Monat</option>
              </select>
            </div>
          </div>

          <div class="sav-calc-output four">
            <div class="sav-kpi">
              <span class="muted tiny">In 3 Monaten</span>
              <strong>{{ fmt(rateCalcResult.m3) }}</strong>
            </div>
            <div class="sav-kpi">
              <span class="muted tiny">In 6 Monaten</span>
              <strong>{{ fmt(rateCalcResult.m6) }}</strong>
            </div>
            <div class="sav-kpi">
              <span class="muted tiny">In 1 Jahr</span>
              <strong class="pos-txt">{{ fmt(rateCalcResult.m12) }}</strong>
            </div>
            <div class="sav-kpi">
              <span class="muted tiny">In 2 Jahren</span>
              <strong class="pos-txt">{{ fmt(rateCalcResult.m24) }}</strong>
            </div>
          </div>
        </template>
      </article>

      <!-- Saved Savings Goals CRUD -->
      <article class="panel goals-list-card">
        <div class="lbl-row">
          <div>
            <span class="section-kicker">Deine Sparziele</span>
            <h3 style="margin:0">Konkrete Rücklagen &amp; Notgroschen</h3>
          </div>
          <button type="button" class="btn sm" @click="openGoalModal()">+ Sparziel</button>
        </div>

        <div v-if="savingsGoals.length" class="goals-stack">
          <div v-for="goal in savingsGoals" :key="goal.id" class="goal-item" :class="{ done: goal.is_completed }">
            <div class="goal-top">
              <div>
                <strong>{{ goal.title }}</strong>
                <span v-if="goal.target_date" class="muted tiny" style="display:block">
                  Zieltermin: {{ formatDateDe(goal.target_date) }}
                  <template v-if="!goal.is_completed && goalDailyNeed(goal) > 0">
                    · noch {{ fmt(goalDailyNeed(goal)) }}/Tag nötig
                  </template>
                </span>
              </div>
              <div class="goal-actions">
                <button
                  v-if="!goal.is_completed"
                  type="button"
                  class="chip-btn pos"
                  @click="promptGoalTopUp(goal)"
                >
                  + Einzahlen
                </button>
                <button type="button" class="icon-mini" @click="openGoalModal(goal)" title="Bearbeiten">✎</button>
                <button type="button" class="icon-mini danger" @click="$emit('delete-goal', goal)" title="Löschen">✕</button>
              </div>
            </div>

            <div class="goal-prog-bar">
              <span :style="{ width: `${Math.min(100, Number(goal.progress_percent || 0))}%` }"></span>
            </div>

            <div class="goal-meta-row">
              <span><strong>{{ fmt(goal.current_amount) }}</strong> von {{ fmt(goal.target_amount) }}</span>
              <span class="muted tiny">{{ Math.round(Number(goal.progress_percent || 0)) }} % erreicht</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-hint-box">
          <p class="muted small">
            Noch kein Sparziel angelegt. Tipp: Starte mit einem kleinen <strong>Notgroschen (z. B. 300 € – 500 €)</strong>, damit unerwartete Rechnungen dich nie wieder in neue Schulden drücken!
          </p>
          <button type="button" class="btn ghost sm" @click="openNotgroschenPreset">
            🛡️ 500 € Notgroschen-Ziel anlegen
          </button>
        </div>
      </article>
    </div>

    <!-- =====================================================================
         TOOL 4: SCHULDEN-TURBO & ABO-KILLER
         ===================================================================== -->
    <div v-else-if="activeTool === 'turbo'" class="sim-split-layout">
      <!-- Abo & Fixed Cost Killer -->
      <article class="panel sim-inputs-card">
        <div class="card-head">
          <span class="section-kicker">Hebel 1: Kosten-Freischaufel-Simulator</span>
          <h2>Abo- &amp; Fixkosten-Killer</h2>
          <p class="muted small">
            Klicke Abos oder Fixkosten an, die du pausieren oder kündigen könntest. Das freiwerdende Geld fließt rechts live in deine Entschuldung!
          </p>
        </div>

        <div v-if="cancellableEntries.length" class="abo-killer-list">
          <div
            v-for="item in cancellableEntries"
            :key="item.id"
            role="button"
            tabindex="0"
            class="killer-row"
            :class="{ 'is-cut': cutEntryIds.includes(item.id) }"
            @click="toggleCutEntry(item.id)"
            @keydown.enter.prevent="toggleCutEntry(item.id)"
            @keydown.space.prevent="toggleCutEntry(item.id)"
          >
            <input
              type="checkbox"
              :checked="cutEntryIds.includes(item.id)"
              @click.stop
              @change="toggleCutEntry(item.id)"
            />
            <div class="killer-info">
              <strong>{{ item.title }}</strong>
              <span class="muted tiny">
                {{ item.entry_type === 'SUBSCRIPTION' ? 'Abo' : 'Fixkosten' }} ·
                {{ fmt(item.monthlyEq) }}/Monat ·
                <strong>{{ fmt(item.monthlyEq * 12) }}/Jahr</strong> ·
                {{ fmt(item.monthlyEq * 36) }} in 3 J.
              </span>
            </div>
            <span class="cut-badge">
              {{ cutEntryIds.includes(item.id) ? `+${fmt(item.monthlyEq)} frei!` : fmt(item.monthlyEq) }}
            </span>
          </div>
        </div>
        <p v-else class="muted small">Noch keine Abos oder Fixkosten eingetragen.</p>

        <div v-if="freedMonthlyFromCuts > 0" class="freed-banner">
          <span>Freigeschaufelt durch Auswahl:</span>
          <strong>+{{ fmt(freedMonthlyFromCuts) }} / Monat (+{{ fmt(freedMonthlyFromCuts * 12) }} / Jahr)</strong>
        </div>
      </article>

      <!-- Debt Payoff Turbo Result -->
      <aside class="sim-results-col">
        <article class="panel result-hero-card">
          <span class="section-kicker">Hebel 2: Tilgungs-Turbo</span>
          <h3 style="margin:0 0 8px">Wann bist du komplett auf 0,00 € Schulden?</h3>

          <div class="savings-mode-pills">
            <button
              type="button"
              class="chip-btn"
              :class="{ active: turboStrategy === 'SNOWBALL' }"
              @click="turboStrategy = 'SNOWBALL'"
            >
              ❄️ Schneeball (Kleinste Schuld zuerst)
            </button>
            <button
              type="button"
              class="chip-btn"
              :class="{ active: turboStrategy === 'PRESSURE' }"
              @click="turboStrategy = 'PRESSURE'"
            >
              ⚡ Raten-Druck (Höchste Rate zuerst)
            </button>
          </div>

          <div class="field-box">
            <div class="lbl-row">
              <span class="muted tiny">Zusätzliches Extra-Tilgungsbudget (€ / Monat)</span>
              <strong>+{{ fmt(totalExtraBoost) }} / Monat gesamt</strong>
            </div>
            <input v-model="extraDebtSlider" type="range" min="0" max="400" step="10" class="range-slider" />
            <span class="muted tiny">
              Davon {{ fmt(extraDebtSlider) }} Extra-Rate + {{ fmt(freedMonthlyFromCuts) }} aus gestrichenen Abos
            </span>
          </div>

          <div class="turbo-compare-grid">
            <div class="turbo-col">
              <span class="muted tiny">Aktueller Plan (ohne Rollover)</span>
              <strong>{{ baselineRoadmap.debtFreeLabel }}</strong>
              <span class="muted tiny">
                {{ baselineRoadmap.monthsUntilDebtFree !== null ? `${baselineRoadmap.monthsUntilDebtFree} Monate` : "Offen" }}
              </span>
            </div>
            <div class="turbo-col active">
              <span class="cyan-txt tiny">Mit Tilgungs-Turbo</span>
              <strong class="pos-txt">{{ turboRoadmap.debtFreeLabel }}</strong>
              <span class="muted tiny">
                {{ turboRoadmap.monthsUntilDebtFree !== null ? `${turboRoadmap.monthsUntilDebtFree} Monate` : "Offen" }}
              </span>
            </div>
          </div>

          <div v-if="monthsSavedByTurbo > 0" class="months-saved-pill">
            🎉 Du bist <strong>{{ monthsSavedByTurbo }} Monat{{ monthsSavedByTurbo === 1 ? "" : "e" }} früher</strong> komplett schuldenfrei!
          </div>

          <div v-if="turboRoadmap.payoffSchedule.length" class="payoff-mini-list">
            <span class="field-lbl">Reihenfolge deiner Schulden-Befreiung:</span>
            <div v-for="(d, idx) in turboRoadmap.payoffSchedule" :key="d.id" class="payoff-step">
              <span class="step-idx">{{ idx + 1 }}.</span>
              <div class="step-mid">
                <strong>{{ d.name }}</strong>
                <span class="muted tiny">Rest {{ fmt(d.initialRemaining) }}</span>
              </div>
              <strong class="pos-txt small">{{ d.paidOffLabel }}</strong>
            </div>
          </div>
        </article>
      </aside>
    </div>

    <!-- Goal Create/Edit Modal -->
    <div v-if="showGoalModal" class="modal-overlay" @click.self="showGoalModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>{{ goalForm.id ? "Sparziel bearbeiten" : "Neues Sparziel anlegen" }}</h3>
          <button type="button" class="modal-close" @click="showGoalModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="submitGoalForm">
          <label>
            Bezeichnung
            <input v-model.trim="goalForm.title" class="input" placeholder="z. B. Notgroschen, Urlaub, Equipment" required />
          </label>
          <div class="form-two-col">
            <label>
              Zielbetrag (€)
              <input v-model="goalForm.target_amount" type="number" step="0.01" min="1" class="input" required />
            </label>
            <label>
              Bereits angespart (€)
              <input v-model="goalForm.current_amount" type="number" step="0.01" min="0" class="input" />
            </label>
          </div>
          <label>
            Zieldatum (optional)
            <input v-model="goalForm.target_date" type="date" class="input" />
          </label>
          <label class="toggle-line">
            <input v-model="goalForm.is_completed" type="checkbox" />
            <span>Bereits abgeschlossen</span>
          </label>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showGoalModal = false">Abbrechen</button>
            <button type="submit" class="btn">Speichern</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Quick Deposit Modal -->
    <div v-if="topUpGoal" class="modal-overlay" @click.self="topUpGoal = null">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Einzahlung auf „{{ topUpGoal.title }}“</h3>
          <button type="button" class="modal-close" @click="topUpGoal = null">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="submitTopUp">
          <label>
            Betrag hinzufügen (€)
            <input v-model="topUpAmount" type="number" step="0.01" min="0.01" class="input" required />
          </label>
          <p class="muted tiny" style="margin:0">
            Aktuell: {{ fmt(topUpGoal.current_amount) }} → Neu: {{ fmt(Number(topUpGoal.current_amount || 0) + Number(topUpAmount || 0)) }}
          </p>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="topUpGoal = null">Abbrechen</button>
            <button type="submit" class="btn">Einzahlen</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, watch } from "vue";
import {
  addDaysIso,
  calculatePeriodSimulator,
  daysInMonth,
  diffDaysInclusive,
  evaluatePurchaseSafety,
  findNextPaydayIso,
  formatDateDe,
  formatDateShortDe,
  formatMoney,
  parseIsoParts,
  round2,
  safeIsoDate,
  simulateLongTermRoadmap,
  toNum,
  todayIso,
} from "../../utils/financeEngine";

const props = defineProps({
  project: { type: Object, default: null },
  entries: { type: Array, default: () => [] },
  debts: { type: Array, default: () => [] },
  savingsGoals: { type: Array, default: () => [] },
  currency: { type: String, default: "EUR" },
});

const emit = defineEmits([
  "adopt-daily-budget",
  "create-planned-from-sim",
  "save-goal",
  "delete-goal",
]);

const today = todayIso();

const tools = [
  { id: "period", icon: "🧮", title: "Datum A → B Rechner", subtitle: "Tagesbudget & Sparen berechnen" },
  { id: "purchase", icon: "🚦", title: "Kauf-Check", subtitle: "Kann ich mir X € leisten?" },
  { id: "savings", icon: "🎯", title: "Spar-Planer & Ziele", subtitle: "Rücklagen & Notgroschen" },
  { id: "turbo", icon: "🚀", title: "Schulden-Turbo", subtitle: "Abo-Killer & schneller auf 0 €" },
];

const activeTool = ref("period");

const currentBalance = computed(() => toNum(props.project?.current_balance, 0));
const projectDailyBudget = computed(() => toNum(props.project?.daily_living_budget, 15));

function fmt(value) {
  return formatMoney(value, props.currency);
}

// ── Tool 1: Period Simulator State ─────────────────────────────────────────
function endOfCurrentMonthIso() {
  const p = parseIsoParts(today);
  if (!p) return addDaysIso(today, 29);
  return safeIsoDate(p.year, p.month, daysInMonth(p.year, p.month));
}

const periodStart = ref(today);
const periodEnd = ref(endOfCurrentMonthIso());
const useRealBalance = ref(true);
const customStartMoney = ref("500");
const extraBonusMoney = ref("0");
const includeScheduled = ref(true);
const showOccurrences = ref(false);
const disabledOccurrenceKeys = ref(new Set());

const savingsMode = ref("AMOUNT");
const savingsValue = ref("0");
const safetyFloor = ref("0");
const testDailySpend = ref("15");

const savingsModes = [
  { id: "AMOUNT", label: "€ Festbetrag sparen" },
  { id: "PERCENT", label: "% vom Rest sparen" },
  { id: "DAILY", label: "€ / Tag weglegen" },
  { id: "TARGET_END", label: "Wunsch-Endbestand" },
];

const currentSavingsLabel = computed(() => {
  if (savingsMode.value === "PERCENT") return "Sparquote in Prozent (%)";
  if (savingsMode.value === "DAILY") return "Täglich zur Seite legen (€ / Tag)";
  if (savingsMode.value === "TARGET_END") return "Gewünschter Endkontostand am Datum B (€)";
  return "Fester Sparbetrag im Zeitraum (€)";
});

const quickSavingsPresets = computed(() => {
  if (savingsMode.value === "PERCENT") return [0, 10, 20, 30];
  if (savingsMode.value === "DAILY") return [0, 2, 5, 10];
  return [0, 50, 100, 250];
});

function selectSavingsMode(modeId) {
  savingsMode.value = modeId;
  if (modeId === "PERCENT" && toNum(savingsValue.value) > 100) {
    savingsValue.value = "20";
  }
}

function enableCustomStartMoney() {
  useRealBalance.value = false;
  customStartMoney.value = String(currentBalance.value);
}

function applyPreset(preset) {
  periodStart.value = today;
  disabledOccurrenceKeys.value = new Set();
  if (preset === "month-end") {
    periodEnd.value = endOfCurrentMonthIso();
  } else if (preset === "next-payday") {
    const nextPay = findNextPaydayIso(props.entries, today);
    // Stop 1 day before next payday to see budget UNTIL salary hits!
    const dayBefore = addDaysIso(nextPay, -1);
    periodEnd.value = dayBefore >= today ? dayBefore : nextPay;
  } else if (preset === "7d") {
    periodEnd.value = addDaysIso(today, 6);
  } else if (preset === "14d") {
    periodEnd.value = addDaysIso(today, 13);
  } else if (preset === "30d") {
    periodEnd.value = addDaysIso(today, 29);
  } else if (preset === "90d") {
    periodEnd.value = addDaysIso(today, 89);
  }
}

function toggleOccurrence(key) {
  const next = new Set(disabledOccurrenceKeys.value);
  if (next.has(key)) next.delete(key);
  else next.add(key);
  disabledOccurrenceKeys.value = next;
}

const periodResult = computed(() =>
  calculatePeriodSimulator({
    startDateIso: periodStart.value || today,
    endDateIso: periodEnd.value || today,
    startingMoney: useRealBalance.value ? currentBalance.value : toNum(customStartMoney.value, 0),
    extraIncome: toNum(extraBonusMoney.value, 0),
    entries: props.entries,
    debts: props.debts,
    includeScheduled: includeScheduled.value,
    disabledOccurrenceKeys: disabledOccurrenceKeys.value,
    savingsMode: savingsMode.value,
    savingsValue: toNum(savingsValue.value, 0),
    safetyFloor: toNum(safetyFloor.value, 0),
    testDailySpend: toNum(testDailySpend.value, 0),
  })
);

const sliderMaxDaily = computed(() => {
  const base = Math.max(30, periodResult.value.theoreticalDailyBudget * 1.5);
  return Math.min(500, Math.ceil(base / 5) * 5);
});

const adoptableBudget = computed(() => {
  const candidate = periodResult.value.hasMidPeriodBottleneck
    ? periodResult.value.safeDailyBudget
    : periodResult.value.theoreticalDailyBudget;
  return round2(Math.max(0, candidate));
});

watch(
  () => periodResult.value.theoreticalDailyBudget,
  (val) => {
    if (val > 0 && toNum(testDailySpend.value) === 15) {
      testDailySpend.value = String(Math.max(0, round2(val * 0.8)));
    }
  },
  { once: true }
);

// ── Tool 2: Purchase Safety Check ──────────────────────────────────────────
const purchaseForm = ref({
  title: "",
  amount: "80",
  date: today,
  installments: 1,
});
const purchaseIncludeLiving = ref(true);

const purchaseEval = computed(() =>
  evaluatePurchaseSafety({
    title: purchaseForm.value.title || "Geplanter Kauf",
    amount: toNum(purchaseForm.value.amount, 0),
    purchaseDateIso: purchaseForm.value.date || today,
    installments: Number(purchaseForm.value.installments || 1),
    startingBalance: currentBalance.value,
    dispoLimit: toNum(props.project?.dispo_limit, 0),
    dispoUsed: toNum(props.project?.dispo_used, 0),
    emergencyBuffer: toNum(props.project?.emergency_buffer_target, 0),
    dailyLivingBudget: projectDailyBudget.value,
    includeDailyBudget: purchaseIncludeLiving.value,
    entries: props.entries,
    debts: props.debts,
  })
);

// ── Tool 3: Savings Planner & Goals ────────────────────────────────────────
const savCalcDirection = ref("GOAL_TO_RATE");
const goalCalc = ref({
  target: "1000",
  current: "0",
  targetDate: addDaysIso(today, 180),
});
const rateCalc = ref({
  amount: "5",
  unit: "DAY",
});

const goalCalcResult = computed(() => {
  const gap = Math.max(0, toNum(goalCalc.value.target) - toNum(goalCalc.value.current));
  const days = Math.max(1, diffDaysInclusive(today, goalCalc.value.targetDate || today));
  const perDay = round2(gap / days);
  return {
    gap,
    days,
    perDay,
    perWeek: round2(perDay * 7),
    perMonth: round2(perDay * 30.4375),
  };
});

const rateCalcResult = computed(() => {
  const amt = Math.max(0, toNum(rateCalc.value.amount));
  let monthly = amt;
  if (rateCalc.value.unit === "DAY") monthly = amt * 30.4375;
  else if (rateCalc.value.unit === "WEEK") monthly = (amt * 52) / 12;
  return {
    m3: round2(monthly * 3),
    m6: round2(monthly * 6),
    m12: round2(monthly * 12),
    m24: round2(monthly * 24),
  };
});

function goalDailyNeed(goal) {
  if (!goal.target_date) return 0;
  const gap = Math.max(0, toNum(goal.target_amount) - toNum(goal.current_amount));
  if (gap <= 0) return 0;
  const days = diffDaysInclusive(today, goal.target_date);
  return round2(gap / Math.max(1, days));
}

const showGoalModal = ref(false);
const goalForm = ref({
  id: null,
  title: "",
  target_amount: "",
  current_amount: "0",
  target_date: "",
  is_completed: false,
});

function openGoalModal(goal = null) {
  if (goal) {
    goalForm.value = {
      id: goal.id,
      title: goal.title,
      target_amount: String(goal.target_amount),
      current_amount: String(goal.current_amount || 0),
      target_date: goal.target_date || "",
      is_completed: Boolean(goal.is_completed),
    };
  } else {
    goalForm.value = {
      id: null,
      title: "",
      target_amount: "",
      current_amount: "0",
      target_date: addDaysIso(today, 180),
      is_completed: false,
    };
  }
  showGoalModal.value = true;
}

function openNotgroschenPreset() {
  goalForm.value = {
    id: null,
    title: "Notgroschen (Sicherheits-Puffer)",
    target_amount: "500",
    current_amount: "0",
    target_date: addDaysIso(today, 150),
    is_completed: false,
  };
  showGoalModal.value = true;
}

function submitGoalForm() {
  emit("save-goal", {
    id: goalForm.value.id,
    title: goalForm.value.title,
    target_amount: toNum(goalForm.value.target_amount, 0),
    current_amount: toNum(goalForm.value.current_amount, 0),
    target_date: goalForm.value.target_date || null,
    is_completed: goalForm.value.is_completed,
  });
  showGoalModal.value = false;
}

const topUpGoal = ref(null);
const topUpAmount = ref("25");

function promptGoalTopUp(goal) {
  topUpGoal.value = goal;
  topUpAmount.value = "25";
}

function submitTopUp() {
  if (!topUpGoal.value) return;
  const newCurrent = round2(toNum(topUpGoal.value.current_amount, 0) + Math.max(0, toNum(topUpAmount.value, 0)));
  const target = toNum(topUpGoal.value.target_amount, 0);
  emit("save-goal", {
    id: topUpGoal.value.id,
    title: topUpGoal.value.title,
    target_amount: target,
    current_amount: newCurrent,
    target_date: topUpGoal.value.target_date || null,
    is_completed: newCurrent >= target,
  });
  topUpGoal.value = null;
}

// ── Tool 4: Debt Turbo & Abo Killer ────────────────────────────────────────
const cutEntryIds = ref([]);
const extraDebtSlider = ref("0");
const turboStrategy = ref("SNOWBALL");

const cancellableEntries = computed(() =>
  (props.entries || [])
    .filter((e) => e.is_active !== false && ["SUBSCRIPTION", "FIXED", "VARIABLE"].includes(e.entry_type) && e.frequency !== "ONCE")
    .map((e) => {
      let monthlyEq = toNum(e.amount);
      if (e.frequency === "WEEKLY") monthlyEq = (monthlyEq * 52) / 12;
      else if (e.frequency === "YEARLY") monthlyEq = monthlyEq / 12;
      return { ...e, monthlyEq: round2(monthlyEq) };
    })
    .sort((a, b) => (a.entry_type === "SUBSCRIPTION" ? -1 : 1) || b.monthlyEq - a.monthlyEq)
);

function toggleCutEntry(id) {
  if (cutEntryIds.value.includes(id)) {
    cutEntryIds.value = cutEntryIds.value.filter((x) => x !== id);
  } else {
    cutEntryIds.value = [...cutEntryIds.value, id];
  }
}

const freedMonthlyFromCuts = computed(() =>
  round2(
    cancellableEntries.value
      .filter((e) => cutEntryIds.value.includes(e.id))
      .reduce((s, e) => s + e.monthlyEq, 0)
  )
);

const totalExtraBoost = computed(() =>
  round2(toNum(extraDebtSlider.value, 0) + freedMonthlyFromCuts.value)
);

const baselineRoadmap = computed(() =>
  simulateLongTermRoadmap({
    horizonMonths: 36,
    startingBalance: currentBalance.value,
    entries: props.entries,
    debts: props.debts,
    strategy: "CURRENT",
    extraMonthlyDebtBudget: 0,
  })
);

const turboRoadmap = computed(() =>
  simulateLongTermRoadmap({
    horizonMonths: 36,
    startingBalance: currentBalance.value,
    entries: props.entries,
    debts: props.debts,
    strategy: turboStrategy.value,
    extraMonthlyDebtBudget: totalExtraBoost.value,
    disabledEntryIds: new Set(cutEntryIds.value),
  })
);

const monthsSavedByTurbo = computed(() => {
  const baseM = baselineRoadmap.value.monthsUntilDebtFree;
  const turboM = turboRoadmap.value.monthsUntilDebtFree;
  if (baseM === null || turboM === null) return 0;
  return Math.max(0, baseM - turboM);
});
</script>

<style scoped>
.simulator-tab {
  display: grid;
  gap: 18px;
}

.tool-selector-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(215px, 1fr));
  gap: 10px;
}

.tool-nav-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
  text-align: left;
  cursor: pointer;
  transition: all 0.16s ease;
}

.tool-nav-card:hover {
  border-color: var(--brand);
}

.tool-nav-card.active {
  border-color: var(--brand);
  background: color-mix(in srgb, var(--brand) 12%, var(--card));
  box-shadow: 0 6px 20px rgba(47, 99, 255, 0.14);
}

.tool-ico {
  font-size: 24px;
  width: 42px;
  height: 42px;
  border-radius: 12px;
  background: var(--surface);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.tool-copy {
  display: grid;
  gap: 2px;
}

.tool-copy strong {
  font-size: 13.5px;
}

.tool-copy span {
  font-size: 12px;
  color: var(--muted);
}

.sim-split-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 16px;
  align-items: start;
}

.panel {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 20px;
}

.sim-inputs-card,
.goals-list-card {
  display: grid;
  gap: 16px;
}

.sim-results-col {
  display: grid;
  gap: 16px;
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

.card-head h2 {
  margin: 0 0 6px;
  font-size: 1.2rem;
}

.card-head p {
  margin: 0;
}

.preset-row,
.savings-mode-pills,
.quick-val-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip-btn {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s ease;
}

.chip-btn:hover {
  border-color: var(--brand);
  color: var(--text);
}

.chip-btn.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #ffffff;
}

.chip-btn.pos {
  border-color: rgba(34, 197, 94, 0.35);
  color: #22c55e;
}

.tiny-preset {
  padding: 3px 9px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  font-size: 11.5px;
  cursor: pointer;
}

.tiny-preset:hover {
  border-color: var(--brand);
  color: var(--text);
}

.form-two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.field-box {
  display: grid;
  gap: 6px;
}

.field-box.full-span {
  grid-column: 1 / -1;
}

.field-lbl {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text);
}

.lbl-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.days-badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 11.5px;
  font-weight: 700;
  color: var(--brand);
}

.sub-block {
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 12px;
}

.highlight-sub {
  border-color: color-mix(in srgb, var(--brand) 30%, var(--border));
}

.mini-switch {
  display: inline-flex;
  gap: 4px;
  padding: 3px;
  border-radius: 10px;
  background: var(--card);
  border: 1px solid var(--border);
}

.mini-sw-btn {
  padding: 4px 10px;
  border-radius: 7px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 11.5px;
  font-weight: 600;
  cursor: pointer;
}

.mini-sw-btn.active {
  background: var(--brand);
  color: #fff;
}

.toggle-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 13px;
}

.link-btn {
  border: none;
  background: transparent;
  color: var(--brand);
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
}

.sched-summary-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
  font-weight: 600;
}

.occ-list {
  display: grid;
  gap: 5px;
  max-height: 220px;
  overflow-y: auto;
  padding-top: 6px;
  border-top: 1px solid var(--border);
}

.occ-item {
  display: grid;
  grid-template-columns: auto 56px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 6px 8px;
  border-radius: 8px;
  background: var(--card);
  font-size: 12.5px;
  cursor: pointer;
}

.occ-item.is-disabled {
  opacity: 0.52;
}

.occ-item.is-disabled .occ-title {
  text-decoration: line-through;
}

.occ-date {
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* Result Hero */
.result-hero-card,
.reverse-card,
.verdict-card {
  display: grid;
  gap: 14px;
}

.big-daily-box {
  padding: 18px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 6px;
}

.big-lbl {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
}

.big-amount {
  font-size: clamp(1.85rem, 3.2vw, 2.5rem);
  font-weight: 900;
  line-height: 1.1;
  font-variant-numeric: tabular-nums;
}

.big-amount small {
  font-size: 1rem;
  font-weight: 600;
  color: var(--muted);
}

.sub-rates {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 13px;
  color: var(--muted);
  padding-top: 6px;
  border-top: 1px solid var(--border);
}

.bottleneck-callout {
  padding: 14px;
  border-radius: 14px;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.4);
  display: grid;
  gap: 8px;
}

.bn-title {
  font-weight: 700;
  font-size: 13px;
  color: #fbbf24;
}

.bn-safe-val {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 6px;
  border-top: 1px solid rgba(245, 158, 11, 0.25);
  font-size: 13.5px;
}

.calc-waterfall {
  display: grid;
  gap: 7px;
  font-size: 13px;
}

.wf-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.wf-divider {
  height: 1px;
  background: var(--border);
  margin: 3px 0;
}

.wf-row.total {
  font-size: 14px;
  font-weight: 700;
}

.adopt-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

/* Reverse Card */
.reverse-card h3 {
  margin: 0;
  font-size: 1.05rem;
}

.slider-control {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 12px;
}

.range-slider {
  width: 100%;
  accent-color: var(--brand);
  cursor: pointer;
}

.slider-input-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}

.sm-num {
  width: 90px;
  padding: 7px 10px;
}

.reverse-metrics {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.rev-box {
  padding: 10px;
  border-radius: 11px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 3px;
}

/* Purchase Verdict */
.verdict-card.verdict-safe {
  border-color: rgba(34, 197, 94, 0.45);
}
.verdict-card.verdict-tight {
  border-color: rgba(245, 158, 11, 0.45);
}
.verdict-card.verdict-danger {
  border-color: rgba(239, 68, 68, 0.5);
}

.verdict-pill {
  display: inline-block;
  padding: 5px 12px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 12.5px;
  font-weight: 700;
}

.verdict-card h3 {
  margin: 0;
  font-size: 1.08rem;
  line-height: 1.4;
}

.safe-date-tip {
  padding: 12px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 13px;
}

/* Savings Calc & Goals */
.sav-calc-output {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.sav-calc-output.four {
  grid-template-columns: repeat(2, 1fr);
}

.sav-kpi {
  padding: 14px;
  border-radius: 13px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 4px;
}

.sav-kpi strong {
  font-size: 1.2rem;
}

.goals-stack {
  display: grid;
  gap: 10px;
}

.goal-item {
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 10px;
}

.goal-item.done {
  opacity: 0.72;
}

.goal-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.goal-actions {
  display: flex;
  align-items: center;
  gap: 6px;
}

.icon-mini {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  cursor: pointer;
}

.icon-mini.danger:hover {
  color: #ef4444;
  border-color: #ef4444;
}

.goal-prog-bar {
  height: 8px;
  border-radius: 999px;
  background: var(--card);
  overflow: hidden;
}

.goal-prog-bar span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--brand), #22c55e);
  border-radius: 999px;
}

.goal-meta-row {
  display: flex;
  justify-content: space-between;
  font-size: 12.5px;
}

.empty-hint-box {
  padding: 18px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px dashed var(--border);
  display: grid;
  gap: 10px;
  justify-items: start;
}

/* Turbo & Abo Killer */
.abo-killer-list {
  display: grid;
  gap: 8px;
  max-height: 380px;
  overflow-y: auto;
}

.killer-row {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer;
}

.killer-row.is-cut {
  border-color: rgba(34, 197, 94, 0.45);
  background: rgba(34, 197, 94, 0.08);
}

.killer-info {
  display: grid;
  gap: 2px;
}

.cut-badge {
  font-size: 12.5px;
  font-weight: 700;
}

.freed-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.35);
  color: #22c55e;
  font-size: 13px;
}

.turbo-compare-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.turbo-col {
  padding: 12px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 4px;
}

.turbo-col.active {
  border-color: rgba(34, 197, 94, 0.45);
}

.months-saved-pill {
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(34, 197, 94, 0.12);
  border: 1px solid rgba(34, 197, 94, 0.35);
  font-size: 13px;
}

.payoff-mini-list {
  display: grid;
  gap: 6px;
}

.payoff-step {
  display: grid;
  grid-template-columns: 24px 1fr auto;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: 10px;
  background: var(--surface);
  font-size: 13px;
}

.step-mid {
  display: grid;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay, rgba(2, 6, 23, 0.78));
  display: grid;
  place-items: center;
  z-index: 90;
  padding: 16px;
}

.modal-box {
  width: min(460px, 100%);
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  overflow: hidden;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.pos-txt { color: #22c55e; }
.neg-txt { color: #ef4444; }
.amber-txt { color: #f59e0b; }
.cyan-txt { color: #38bdf8; }
.tiny { font-size: 12px; }
.small { font-size: 13.5px; }

@media (max-width: 980px) {
  .sim-split-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .form-two-col,
  .reverse-metrics,
  .sav-calc-output,
  .turbo-compare-grid {
    grid-template-columns: 1fr;
  }
}
</style>
