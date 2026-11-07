<template>
  <div class="finance-platform" :class="{ 'force-mobile-app': forceMobileApp }">
    <!-- Loading State -->
    <section v-if="loading && !project && !initialLoaded" class="card empty-hero">
      <p class="muted">Lade UNYQ Finance...</p>
    </section>

    <!-- Onboarding / First-Time Project Setup -->
    <section v-else-if="initialLoaded && !projects.length" class="card onboarding-card">
      <div class="onb-left">
        <span class="eyebrow">UNYQ Finance 2.0</span>
        <h1>Dein persönliches Finanz- &amp; Entschuldungs-Cockpit</h1>
        <p class="muted">
          Plane deinen Besitz Tag für Tag im Voraus, berechne dein echtes sicheres Tagesbudget zwischen zwei Daten und verfolge deinen exakten Weg auf 0,00 € Schulden.
        </p>
        <div class="feature-pills">
          <span>📅 Tag-für-Tag Soll-Besitz</span>
          <span>🧮 Zeitraum- &amp; Spar-Simulator</span>
          <span>📈 12–36 Monate Schuldenfrei-Plan</span>
          <span>🚦 90-Tage Kauf-Check</span>
        </div>
      </div>

      <form class="onb-form" @submit.prevent="createFirstProject">
        <h3>In 30 Sekunden starten</h3>
        <label>
          Name deines Plans
          <input v-model.trim="createForm.title" class="input" placeholder="Meine Finanzen" required />
        </label>
        <div class="two-col">
          <label>
            Aktueller Kontostand (€)
            <input v-model="createForm.current_balance" type="number" step="0.01" class="input" placeholder="z. B. 350.00" />
          </label>
          <label>
            Währung
            <select v-model="createForm.currency" class="input">
              <option value="EUR">EUR (€)</option>
              <option value="CHF">CHF</option>
              <option value="USD">USD ($)</option>
            </select>
          </label>
        </div>
        <label>
          Geplantes Alltags-Tagesbudget (€ / Tag, optional)
          <input v-model="createForm.daily_living_budget" type="number" step="0.50" min="0" class="input" placeholder="z. B. 15.00 für Essen & Alltag" />
        </label>
        <button type="submit" class="btn" :disabled="saving">
          {{ saving ? "Erstelle Plan..." : "Finanz-Cockpit starten →" }}
        </button>
      </form>
    </section>

    <!-- Main Finance Cockpit -->
    <template v-else-if="project">
      <!-- =================================================================
           NATIVE MOBILE APP HEADER & TODAY BUDGET STRIP (HANDY / APK UI)
           ================================================================= -->
      <header class="mobile-app-header card">
        <div class="mah-top">
          <div class="mah-brand">
            <button
              type="button"
              class="mah-hub-btn"
              title="UNYQ Menü & Plattformen"
              @click="showMobileHubMenu = true"
            >
              ☰
            </button>
            <div class="mah-title-wrap">
              <span class="mah-kicker">UNYQ Finance</span>
              <select
                v-if="projects.length > 1"
                :value="project.id"
                class="mah-proj-select"
                @change="onSwitchProject($event.target.value)"
              >
                <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
              </select>
              <strong v-else class="mah-proj-name">{{ project.title }}</strong>
            </div>
          </div>

          <button type="button" class="mah-balance-pill" @click="openBalanceModal">
            <span class="mah-bal-lbl">Besitz</span>
            <strong :class="currentBalance < 0 ? 'neg-txt' : 'pos-txt'">{{ fmt(currentBalance) }}</strong>
            <span class="mah-edit-ico">✎</span>
          </button>
        </div>

        <!-- Mobile Today Daily-Budget Live Bar -->
        <div class="mah-today-strip">
          <div class="mah-today-info" @click="openDailyExpenseModal(today)">
            <div class="mah-today-topline">
              <span>Heute ausgegeben: <strong>{{ fmt(todaySpentTotal) }}</strong></span>
              <span v-if="projectDailyBudget > 0" :class="todayBudgetRemaining >= 0 ? 'pos-txt' : 'neg-txt'">
                <strong>{{ todayBudgetRemaining >= 0 ? `Noch ${fmt(todayBudgetRemaining)} frei` : `${fmt(Math.abs(todayBudgetRemaining))} drüber` }}</strong>
              </span>
              <span v-else class="muted tiny">Kein Tageslimit gesetzt</span>
            </div>
            <div v-if="projectDailyBudget > 0" class="mah-budget-bar">
              <span
                :class="{ over: todayBudgetRemaining < 0 }"
                :style="{ width: `${Math.min(100, Math.round((todaySpentTotal / Math.max(1, projectDailyBudget)) * 100))}%` }"
              ></span>
            </div>
          </div>

          <button type="button" class="mah-quick-exp-btn" @click="openDailyExpenseModal(today)">
            💸 + Ausgabe
          </button>
        </div>
      </header>

      <!-- =================================================================
           DESKTOP COMMAND HEADER
           ================================================================= -->
      <header class="card finance-header desktop-only-header">
        <div class="fh-left">
          <span class="eyebrow">UNYQ Finance</span>
          <div class="project-title-row">
            <select
              v-if="projects.length > 1"
              :value="project.id"
              class="input project-switcher"
              @change="onSwitchProject($event.target.value)"
            >
              <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
            </select>
            <h1 v-else>{{ project.title }}</h1>

            <button type="button" class="btn ghost tiny" title="Projekt-Einstellungen & Dispo" @click="openBalanceModal">
              ⚙ Rahmen &amp; Dispo
            </button>
            <button type="button" class="btn ghost tiny" @click="showNewProjectModal = true">
              + Neues Projekt
            </button>
          </div>
        </div>

        <div class="fh-right">
          <button
            type="button"
            class="btn daily-exp-cta-btn"
            @click="openDailyExpenseModal(today)"
          >
            💸 + Tägliche Ausgabe
          </button>

          <button type="button" class="balance-pill-btn" @click="openBalanceModal" title="Aktuellen Kontostand anpassen">
            <span class="bp-lbl">Aktueller Besitz</span>
            <strong :class="currentBalance < 0 ? 'neg-txt' : 'pos-txt'">{{ fmt(currentBalance) }}</strong>
            <span class="bp-edit">✎</span>
          </button>

          <button
            type="button"
            class="btn ghost sm"
            :class="{ 'active-preview-btn': forceMobileApp }"
            title="Handy-App-Oberfläche testen / umschalten"
            @click="toggleForceMobileApp"
          >
            📱 {{ forceMobileApp ? "Web-Ansicht" : "Handy-UI" }}
          </button>

          <button
            type="button"
            class="btn ghost sm apk-dl-btn"
            title="UNYQ Finance Android App (.apk) herunterladen"
            @click="showApkModal = true"
          >
            🤖 Android APK
          </button>

          <button type="button" class="btn ghost sm" @click="exportCsv" title="Monatsübersicht als CSV exportieren">
            ↓ CSV
          </button>
        </div>
      </header>

      <!-- Feedback Toast Banner -->
      <div v-if="bannerMessage.text" class="toast-banner" :class="bannerMessage.type">
        <span>{{ bannerMessage.text }}</span>
        <button type="button" class="banner-close" @click="bannerMessage.text = ''">&times;</button>
      </div>

      <!-- Primary 6-Tab Navigation (Desktop) -->
      <nav class="finance-tabs desktop-only-tabs" aria-label="Finance Bereiche">
        <button
          v-for="tab in navTabs"
          :key="tab.id"
          type="button"
          class="fin-tab-btn"
          :class="{ active: activeTab === tab.id }"
          @click="setTab(tab.id)"
        >
          <span class="tab-ico">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
          <span v-if="tab.badge" class="tab-badge">{{ tab.badge }}</span>
        </button>
      </nav>

      <!-- Mobile Sub-Switcher when inside "Mehr" Tabs (Debts / Longterm / Entries) -->
      <div v-if="['debts', 'longterm', 'entries'].includes(activeTab)" class="mobile-more-subbar">
        <button
          type="button"
          class="mms-btn"
          :class="{ active: activeTab === 'debts' }"
          @click="setTab('debts')"
        >
          💳 Schulden &amp; Raten
          <span v-if="urgentDebtsCount > 0" class="tab-badge">{{ urgentDebtsCount }}</span>
        </button>
        <button
          type="button"
          class="mms-btn"
          :class="{ active: activeTab === 'longterm' }"
          @click="setTab('longterm')"
        >
          📈 36M Langzeit
        </button>
        <button
          type="button"
          class="mms-btn"
          :class="{ active: activeTab === 'entries' }"
          @click="setTab('entries')"
        >
          🧾 Fix &amp; Abos
        </button>
      </div>

      <!-- ===================================================================
           TAB 1: COCKPIT (ÜBERSICHT)
           =================================================================== -->
      <section v-if="activeTab === 'overview'" class="cockpit-view">
        <!-- Smart Urgent Alerts -->
        <div v-if="urgentDebtsCount > 0 || preview14d.firstNegativeDate" class="alerts-stack">
          <div v-if="urgentDebtsCount > 0" class="smart-alert warn">
            <div>
              <strong>⚡ {{ urgentDebtsCount }} Rate{{ urgentDebtsCount === 1 ? " ist" : "n sind" }} heute fällig oder überfällig</strong>
              <span>Prüfe kurz deine offenen Fälligkeiten, damit Restschuld und Tagesplan aktuell bleiben.</span>
            </div>
            <button type="button" class="btn sm" @click="setTab('debts')">Jetzt klären →</button>
          </div>

          <div v-if="preview14d.firstNegativeDate" class="smart-alert danger">
            <div>
              <strong>🚨 Konto-Engpass in den nächsten 14 Tagen erkannt!</strong>
              <span>
                Laut Plan fällt dein Besitz am <strong>{{ formatDateDe(preview14d.minBalanceDate) }}</strong> auf
                <strong>{{ fmt(preview14d.minBalance) }}</strong>. Prüfe den Tag-für-Tag-Plan!
              </span>
            </div>
            <button type="button" class="btn sm ghost" @click="setTab('daily')">Zum Tagesplan →</button>
          </div>
        </div>

        <!-- 4 Hero KPIs -->
        <div class="cockpit-kpi-grid">
          <article class="kpi-hero-card">
            <div class="kh-top">
              <span class="kh-lbl">Aktueller Kontostand (Besitz)</span>
              <button type="button" class="tiny-action" @click="openBalanceModal">Abgleichen</button>
            </div>
            <strong class="kh-val" :class="currentBalance < 0 ? 'neg-txt' : 'pos-txt'">
              {{ fmt(currentBalance) }}
            </strong>
            <span class="muted tiny">
              Netto-Vermögen (abzgl. Schulden):
              <strong :class="netWorthToday >= 0 ? 'pos-txt' : 'neg-txt'">{{ fmt(netWorthToday) }}</strong>
            </span>
          </article>

          <article class="kpi-hero-card">
            <div class="kh-top">
              <span class="kh-lbl">Täglich frei bis Monatsende</span>
              <button type="button" class="tiny-action" @click="setTab('simulator')">Simulator →</button>
            </div>
            <strong
              class="kh-val"
              :class="monthEndDailySim.safeDailyBudget >= 0 ? 'pos-txt' : 'neg-txt'"
            >
              {{ fmt(monthEndDailySim.hasMidPeriodBottleneck ? monthEndDailySim.safeDailyBudget : monthEndDailySim.theoreticalDailyBudget) }}
              <small>/ Tag</small>
            </strong>
            <span class="muted tiny">
              Für die nächsten {{ monthEndDailySim.totalDays }} Tage (inkl. aller offenen Abbuchungen)
            </span>
          </article>

          <article class="kpi-hero-card">
            <div class="kh-top">
              <span class="kh-lbl">Monatlich nach Fixkosten &amp; Raten</span>
              <button type="button" class="tiny-action" @click="setTab('entries')">Posten →</button>
            </div>
            <strong class="kh-val" :class="monthlyFreeAfterFixed >= 0 ? 'pos-txt' : 'neg-txt'">
              {{ monthlyFreeAfterFixed >= 0 ? "+" : "" }}{{ fmt(monthlyFreeAfterFixed) }}
            </strong>
            <span class="muted tiny">
              {{ fmt(monthlyIncomeTotal) }} Einnahmen − {{ fmt(monthlyFixedAndSubs + monthlyDebtRateTotal) }} Fix &amp; Raten
            </span>
          </article>

          <article class="kpi-hero-card">
            <div class="kh-top">
              <span class="kh-lbl">Offene Gesamtschulden</span>
              <button type="button" class="tiny-action" @click="setTab('longterm')">Langzeit →</button>
            </div>
            <strong class="kh-val" :class="totalOpenDebt > 0 ? 'neg-txt' : 'pos-txt'">
              {{ fmt(totalOpenDebt) }}
            </strong>
            <span class="muted tiny">
              <template v-if="totalOpenDebt <= 0">100 % schuldenfrei 🎉</template>
              <template v-else>Schuldenfrei-Ziel: <strong>{{ quickRoadmap.debtFreeLabel }}</strong></template>
            </span>
          </article>
        </div>

        <!-- =================================================================
             TÄGLICHE AUSGABEN & TAGESBUDGET-TRACKER (JEDEN TAG STEUERBAR)
             ================================================================= -->
        <article class="card cockpit-panel daily-tracker-card">
          <div class="dt-header">
            <div>
              <span class="section-kicker">Tägliche Ausgaben &amp; Tageslimit</span>
              <h3>Was hast du am {{ selectedTrackerDate === today ? "heutigen Tag" : formatDateDe(selectedTrackerDate) }} ausgegeben?</h3>
            </div>

            <div class="dt-date-nav">
              <button type="button" class="btn ghost tiny" @click="shiftTrackerDate(-1)" title="Ein Tag zurück">
                ←
              </button>
              <button
                v-if="selectedTrackerDate !== today"
                type="button"
                class="btn ghost tiny"
                @click="selectedTrackerDate = today"
              >
                Heute
              </button>
              <input v-model="selectedTrackerDate" type="date" class="input dt-date-input" />
              <button type="button" class="btn ghost tiny" @click="shiftTrackerDate(1)" title="Ein Tag weiter">
                →
              </button>
              <button type="button" class="btn sm daily-exp-cta-btn" @click="openDailyExpenseModal(selectedTrackerDate)">
                💸 + Ausgabe eintragen
              </button>
            </div>
          </div>

          <div class="dt-summary-grid">
            <div class="dt-stat-box">
              <span class="muted tiny">Ausgegeben am {{ formatDateShortDe(selectedTrackerDate) }}</span>
              <strong :class="trackerDaySpent > 0 ? 'amber-txt' : ''">{{ fmt(trackerDaySpent) }}</strong>
            </div>

            <div class="dt-stat-box">
              <div class="dt-lbl-inline">
                <span class="muted tiny">Geplantes Tagesbudget</span>
                <button type="button" class="tiny-link" @click="openBalanceModal">Ändern</button>
              </div>
              <strong>{{ projectDailyBudget > 0 ? `${fmt(projectDailyBudget)} / Tag` : "Nicht gesetzt" }}</strong>
            </div>

            <div class="dt-stat-box highlight">
              <span class="muted tiny">
                {{ selectedTrackerDate === today ? "Heute noch übrig" : `Am ${formatDateShortDe(selectedTrackerDate)} übrig` }}
              </span>
              <strong
                v-if="projectDailyBudget > 0"
                :class="trackerDayRemaining >= 0 ? 'pos-txt' : 'neg-txt'"
              >
                {{
                  trackerDayRemaining >= 0
                    ? `${fmt(trackerDayRemaining)} frei`
                    : `${fmt(Math.abs(trackerDayRemaining))} über Budget`
                }}
              </strong>
              <strong v-else class="muted tiny">Tagesbudget in Rahmen setzen</strong>
            </div>
          </div>

          <div v-if="projectDailyBudget > 0" class="dt-progress-track">
            <span
              :class="{ over: trackerDayRemaining < 0 }"
              :style="{ width: `${Math.min(100, Math.round((trackerDaySpent / Math.max(1, projectDailyBudget)) * 100))}%` }"
            ></span>
          </div>

          <!-- Expenses List for Selected Date -->
          <div v-if="trackerDayExpenses.length" class="dt-exp-list">
            <div v-for="exp in trackerDayExpenses" :key="exp.id" class="dt-exp-item">
              <div class="dt-exp-left">
                <span class="dt-cat-pill">{{ exp.category || "Alltag" }}</span>
                <strong>{{ exp.title }}</strong>
                <span v-if="exp.notes" class="muted tiny">· {{ exp.notes }}</span>
              </div>
              <div class="dt-exp-right">
                <strong class="neg-txt">−{{ fmt(exp.amount) }}</strong>
                <button
                  type="button"
                  class="dt-del-btn"
                  title="Ausgabe löschen"
                  @click="deleteDailyExpenseById(exp.id)"
                >
                  &times;
                </button>
              </div>
            </div>
          </div>
          <div v-else class="dt-empty-row">
            <span class="muted tiny">
              Noch keine Ausgaben für den {{ formatDateDe(selectedTrackerDate) }} eingetragen.
            </span>
            <button type="button" class="btn ghost tiny" @click="openDailyExpenseModal(selectedTrackerDate)">
              + Erste Ausgabe für diesen Tag erfassen
            </button>
          </div>
        </article>

        <!-- 2-Column Cockpit Body -->
        <div class="cockpit-columns">
          <!-- Left: 14-Day Soll-Besitz Preview -->
          <article class="card cockpit-panel">
            <div class="cp-head">
              <div>
                <span class="section-kicker">Nächste 14 Tage</span>
                <h3>Vorschau: Dein geplanter Besitz</h3>
              </div>
              <button type="button" class="btn ghost sm" @click="setTab('daily')">
                Alle 365 Tage →
              </button>
            </div>

            <div class="mini-timeline">
              <div
                v-for="day in preview14Rows"
                :key="day.date"
                class="mini-day-row"
                :class="{ 'is-neg': day.endBalance < 0, 'is-today': day.isToday }"
              >
                <div class="md-left">
                  <span class="md-wd">{{ day.weekday }}</span>
                  <strong>{{ formatDateShortDe(day.date) }}</strong>
                  <span v-if="day.isToday" class="md-tag">Heute</span>
                </div>

                <div class="md-events">
                  <template v-if="day.events.length">
                    <span
                      v-for="ev in day.events.slice(0, 2)"
                      :key="ev.id"
                      class="md-ev"
                      :class="ev.amount > 0 ? 'pos-txt' : ''"
                    >
                      {{ ev.title }} ({{ ev.amount > 0 ? "+" : "" }}{{ fmt(ev.amount) }})
                    </span>
                    <span v-if="day.events.length > 2" class="muted tiny">+{{ day.events.length - 2 }} weitere</span>
                  </template>
                  <span v-else class="muted tiny">Keine feste Buchung</span>
                </div>

                <strong class="md-bal" :class="day.endBalance < 0 ? 'neg-txt' : ''">
                  {{ fmt(day.endBalance) }}
                </strong>
              </div>
            </div>
          </article>

          <!-- Right: Monthly Cashflow Structure & Quick Actions -->
          <div class="cockpit-side-stack">
            <article class="card cockpit-panel">
              <div class="cp-head">
                <div>
                  <span class="section-kicker">Monats-Struktur</span>
                  <h3>Wohin fließt dein Einkommen?</h3>
                </div>
              </div>

              <div class="cashflow-rows">
                <div class="cf-row">
                  <span>💰 Monatliche Einnahmen</span>
                  <strong class="pos-txt">+{{ fmt(monthlyIncomeTotal) }}</strong>
                </div>
                <div class="cf-row">
                  <span>🏠 Fixkosten &amp; Verträge</span>
                  <strong>−{{ fmt(monthlyFixedOnly) }}</strong>
                </div>
                <div class="cf-row">
                  <span>🔄 Abonnements</span>
                  <strong>−{{ fmt(monthlySubsOnly) }}</strong>
                </div>
                <div class="cf-row">
                  <span>💳 Schulden- &amp; Kreditraten</span>
                  <strong class="debt-txt">−{{ fmt(monthlyDebtRateTotal) }}</strong>
                </div>
                <div v-if="projectDailyBudget > 0" class="cf-row">
                  <span>🛒 Geplantes Alltagsbudget (30 T.)</span>
                  <strong class="muted">−{{ fmt(projectDailyBudget * 30) }}</strong>
                </div>
                <div class="cf-divider"></div>
                <div class="cf-row total">
                  <span>Geplanter Monats-Überschuss</span>
                  <strong :class="monthlyNetAfterAll >= 0 ? 'pos-txt' : 'neg-txt'">
                    {{ monthlyNetAfterAll >= 0 ? "+" : "" }}{{ fmt(monthlyNetAfterAll) }}
                  </strong>
                </div>
              </div>

              <div class="quick-nav-grid">
                <button type="button" class="btn ghost sm" @click="setTab('simulator')">
                  🧮 Zeitraum-Budget berechnen
                </button>
                <button type="button" class="btn ghost sm" @click="openQuickEntryFromCockpit">
                  + Buchung anlegen
                </button>
              </div>
            </article>

            <!-- Savings Goals Snapshot -->
            <article v-if="savingsGoals.length" class="card cockpit-panel">
              <div class="cp-head">
                <div>
                  <span class="section-kicker">Rücklagen</span>
                  <h3>Aktive Sparziele</h3>
                </div>
                <button type="button" class="btn ghost tiny" @click="setTab('simulator')">Öffnen →</button>
              </div>
              <div class="mini-goals">
                <div v-for="g in savingsGoals.slice(0, 3)" :key="g.id" class="mg-row">
                  <div class="mg-top">
                    <strong>{{ g.title }}</strong>
                    <span class="muted tiny">{{ fmt(g.current_amount) }} / {{ fmt(g.target_amount) }}</span>
                  </div>
                  <div class="mg-bar">
                    <span :style="{ width: `${Math.min(100, Number(g.progress_percent || 0))}%` }"></span>
                  </div>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ===================================================================
           TAB 2: TAG-FÜR-TAG PLAN
           =================================================================== -->
      <FinanceDailyPlanTab
        v-else-if="activeTab === 'daily'"
        :project="project"
        :entries="entries"
        :debts="debts"
        :daily-expenses="dailyExpenses"
        :currency="currency"
        :saving-budget="saving"
        @open-balance-modal="openBalanceModal"
        @save-daily-budget="saveDailyLivingBudget"
        @quick-add-on-date="handleQuickAddOnDate"
        @log-daily-expense="openDailyExpenseModal"
        @delete-daily-expense="deleteDailyExpenseById"
        @jump-to-debts="setTab('debts')"
      />

      <!-- ===================================================================
           TAB 3: SIMULATOR & SMART TOOLS
           =================================================================== -->
      <FinanceSimulatorTab
        v-else-if="activeTab === 'simulator'"
        :project="project"
        :entries="entries"
        :debts="debts"
        :savings-goals="savingsGoals"
        :currency="currency"
        @adopt-daily-budget="adoptBudgetFromSimulator"
        @create-planned-from-sim="handleCreatePlannedFromSim"
        @save-goal="saveSavingsGoal"
        @delete-goal="deleteSavingsGoal"
      />

      <!-- ===================================================================
           TAB 4: LANGZEIT-ANALYSE (12–36 MONATE)
           =================================================================== -->
      <FinanceLongTermTab
        v-else-if="activeTab === 'longterm'"
        :project="project"
        :entries="entries"
        :debts="debts"
        :savings-goals="savingsGoals"
        :currency="currency"
      />

      <!-- ===================================================================
           TAB 5: SCHULDEN & RATEN
           =================================================================== -->
      <FinanceDebtsTab
        v-else-if="activeTab === 'debts'"
        :project="project"
        :debts="debts"
        :currency="currency"
        @refresh="reloadProjectData"
        @adjust-balance="adjustBalanceByDelta"
        @notify="showBanner"
      />

      <!-- ===================================================================
           TAB 6: BUCHUNGEN & ALLTAG
           =================================================================== -->
      <FinanceEntriesTab
        v-show="activeTab === 'entries'"
        ref="entriesTabRef"
        :project="project"
        :entries="entries"
        :daily-expenses="dailyExpenses"
        :currency="currency"
        @refresh="reloadProjectData"
        @adjust-balance="adjustBalanceByDelta"
        @notify="showBanner"
      />

      <!-- ===================================================================
           NATIVE MOBILE BOTTOM NAVIGATION BAR (THUMB-ZONE)
           =================================================================== -->
      <nav class="mobile-bottom-nav" aria-label="Mobile Finance Navigation">
        <button
          type="button"
          class="mbn-item"
          :class="{ active: activeTab === 'overview' }"
          @click="setTab('overview')"
        >
          <span class="mbn-ico">🏠</span>
          <span class="mbn-lbl">Heute</span>
        </button>

        <button
          type="button"
          class="mbn-item"
          :class="{ active: activeTab === 'daily' }"
          @click="setTab('daily')"
        >
          <span class="mbn-ico">📅</span>
          <span class="mbn-lbl">Tagesplan</span>
        </button>

        <button
          type="button"
          class="mbn-fab"
          title="Tägliche Ausgabe eintragen"
          @click="openDailyExpenseModal(today)"
        >
          <span class="mbn-fab-plus">＋</span>
          <span class="mbn-fab-lbl">Ausgabe</span>
        </button>

        <button
          type="button"
          class="mbn-item"
          :class="{ active: activeTab === 'simulator' }"
          @click="setTab('simulator')"
        >
          <span class="mbn-ico">🧮</span>
          <span class="mbn-lbl">Rechner</span>
        </button>

        <button
          type="button"
          class="mbn-item"
          :class="{ active: ['debts', 'longterm', 'entries'].includes(activeTab) }"
          @click="setTab(['debts', 'longterm', 'entries'].includes(activeTab) ? activeTab : 'debts')"
        >
          <span class="mbn-ico">💳</span>
          <span class="mbn-lbl">Schulden &amp; +</span>
          <span v-if="urgentDebtsCount > 0" class="mbn-dot">{{ urgentDebtsCount }}</span>
        </button>
      </nav>
    </template>

    <!-- ===== GLOBAL QUICK DAILY EXPENSE MODAL / MOBILE BOTTOM SHEET ===== -->
    <div v-if="showDailyExpenseModal" class="modal-overlay bottom-sheet-overlay" @click.self="showDailyExpenseModal = false">
      <div class="modal-box bottom-sheet-box">
        <div class="sheet-drag-handle"></div>
        <div class="modal-header">
          <div>
            <span class="section-kicker">Tägliche Ausgabe erfassen</span>
            <h3>Was und wieviel hast du ausgegeben?</h3>
          </div>
          <button type="button" class="modal-close" @click="showDailyExpenseModal = false">&times;</button>
        </div>

        <form class="modal-form exp-sheet-form" @submit.prevent="submitQuickDailyExpense">
          <!-- Date Quick Bar -->
          <div class="exp-date-bar">
            <div class="exp-date-chips">
              <button
                type="button"
                class="chip-pill"
                :class="{ active: quickExpForm.date === today }"
                @click="setQuickExpDate(today)"
              >
                Heute
              </button>
              <button
                type="button"
                class="chip-pill"
                :class="{ active: quickExpForm.date === yesterdayIso }"
                @click="setQuickExpDate(yesterdayIso)"
              >
                Gestern
              </button>
              <button
                type="button"
                class="chip-pill"
                :class="{ active: quickExpForm.date === dayBeforeYesterdayIso }"
                @click="setQuickExpDate(dayBeforeYesterdayIso)"
              >
                Vorgestern
              </button>
            </div>
            <input v-model="quickExpForm.date" type="date" class="input exp-date-picker" required />
          </div>

          <!-- Big Amount Input + Quick Amount Adders -->
          <div class="exp-amount-block">
            <label>
              Betrag (€)
              <input
                ref="quickAmountInputRef"
                v-model="quickExpForm.amount"
                type="number"
                 inputmode="decimal"
                step="0.01"
                min="0.01"
                class="input big-exp-input"
                placeholder="0.00"
                required
              />
            </label>
            <div class="quick-amt-chips">
              <button
                v-for="inc in [2, 5, 10, 20, 50]"
                :key="inc"
                type="button"
                class="amt-add-chip"
                @click="addQuickAmount(inc)"
              >
                +{{ inc }} €
              </button>
              <button
                v-if="toNum(quickExpForm.amount) > 0"
                type="button"
                class="amt-add-chip clear"
                @click="quickExpForm.amount = ''"
              >
                Reset
              </button>
            </div>
          </div>

          <!-- 1-Tap Category Presets -->
          <div class="exp-cat-section">
            <span class="tiny muted">Schnell-Kategorie antippen oder unten frei benennen:</span>
            <div class="exp-cat-grid">
              <button
                v-for="preset in expensePresets"
                :key="preset.label"
                type="button"
                class="exp-preset-chip"
                :class="{ active: quickExpForm.category === preset.category && quickExpForm.title === preset.defaultTitle }"
                @click="applyExpensePreset(preset)"
              >
                <span>{{ preset.icon }}</span>
                <span>{{ preset.label }}</span>
              </button>
            </div>
          </div>

          <div class="two-col">
            <label>
              Wofür ausgegeben? (Bezeichnung)
              <input
                v-model.trim="quickExpForm.title"
                class="input"
                placeholder="z. B. REWE Einkauf, Döner, Tanken, Kaffee"
                required
              />
            </label>
            <label>
              Kategorie / Notiz (optional)
              <input
                v-model.trim="quickExpForm.notes"
                class="input"
                placeholder="Optionaler Hinweis"
              />
            </label>
          </div>

          <!-- Live Budget & Balance Impact Preview -->
          <div class="exp-live-impact">
            <div class="eli-row">
              <span>Bisher ausgegeben am {{ formatDateShortDe(quickExpForm.date) }}:</span>
              <strong>{{ fmt(modalDateExistingSpent) }}</strong>
            </div>
            <div v-if="projectDailyBudget > 0" class="eli-row">
              <span>Vom Tagesbudget ({{ fmt(projectDailyBudget) }}) danach übrig:</span>
              <strong :class="modalDateRemainingAfter >= 0 ? 'pos-txt' : 'neg-txt'">
                {{
                  modalDateRemainingAfter >= 0
                    ? `${fmt(modalDateRemainingAfter)} übrig`
                    : `${fmt(Math.abs(modalDateRemainingAfter))} über Tagesbudget`
                }}
              </strong>
            </div>

            <label class="eli-check-row">
              <input v-model="quickExpForm.deductFromBalance" type="checkbox" />
              <span>
                Direkt vom aktuellen Kontostand abziehen
                <template v-if="quickExpForm.deductFromBalance && toNum(quickExpForm.amount) > 0">
                  (Neuer Besitz: <strong>{{ fmt(currentBalance - toNum(quickExpForm.amount)) }}</strong>)
                </template>
              </span>
            </label>
          </div>

          <!-- Existing Expenses on that Day -->
          <div v-if="modalDateExpenses.length" class="modal-day-history">
            <span class="muted tiny">Bereits eingetragen am {{ formatDateDe(quickExpForm.date) }}:</span>
            <div class="mdh-list">
              <div v-for="item in modalDateExpenses" :key="item.id" class="mdh-row">
                <span>{{ item.title }}</span>
                <div class="mdh-right">
                  <strong class="neg-txt">−{{ fmt(item.amount) }}</strong>
                  <button type="button" class="dt-del-btn" @click="deleteDailyExpenseById(item.id)">&times;</button>
                </div>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showDailyExpenseModal = false">Schließen</button>
            <button type="submit" class="btn" :disabled="saving">
              {{ saving ? "Speichere..." : `💸 Ausgabe (${fmt(toNum(quickExpForm.amount, 0))}) speichern` }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== MOBILE UNYQ HUB & QUICK MENU SHEET ===== -->
    <div v-if="showMobileHubMenu" class="modal-overlay bottom-sheet-overlay" @click.self="showMobileHubMenu = false">
      <div class="modal-box bottom-sheet-box">
        <div class="sheet-drag-handle"></div>
        <div class="modal-header">
          <div>
            <span class="section-kicker">UNYQ Ökosystem</span>
            <h3>UNYQ Finance &amp; Plattformen</h3>
          </div>
          <button type="button" class="modal-close" @click="showMobileHubMenu = false">&times;</button>
        </div>

        <div class="modal-form">
          <div class="hub-quick-grid">
            <button type="button" class="hub-nav-tile" @click="showMobileHubMenu = false; openBalanceModal()">
              <span>⚙️</span>
              <strong>Kontostand, Dispo &amp; Tageslimit</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="showMobileHubMenu = false; showNewProjectModal = true">
              <span>➕</span>
              <strong>Neues Finanzprojekt</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="showMobileHubMenu = false; exportCsv()">
              <span>📥</span>
              <strong>CSV-Finanzbericht</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="showMobileHubMenu = false; showApkModal = true">
              <span>🤖</span>
              <strong>Android App (.apk)</strong>
            </button>
          </div>

          <div class="cf-divider"></div>
          <span class="muted tiny">Zu einer anderen UNYQ-Plattform wechseln:</span>
          <div class="hub-quick-grid">
            <button type="button" class="hub-nav-tile" @click="router.push({ name: 'platforms' })">
              <span>🌐</span>
              <strong>UNYQ Hub (Alle Plattformen)</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="router.push({ name: 'dashboard' })">
              <span>🎵</span>
              <strong>ProArtist Workspace</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="router.push({ name: 'platform-music' })">
              <span>🎧</span>
              <strong>UNYQ Music</strong>
            </button>
            <button type="button" class="hub-nav-tile" @click="router.push({ name: 'tournaments' })">
              <span>🏆</span>
              <strong>UNYQ Arena &amp; Contests</strong>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- ===== ANDROID APK DOWNLOAD & INSTALL MODAL ===== -->
    <div v-if="showApkModal" class="modal-overlay bottom-sheet-overlay" @click.self="showApkModal = false">
      <div class="modal-box bottom-sheet-box">
        <div class="sheet-drag-handle"></div>
        <div class="modal-header">
          <div>
            <span class="section-kicker">UNYQ Finance für Android</span>
            <h3>🤖 Android App (.apk) installieren</h3>
          </div>
          <button type="button" class="modal-close" @click="showApkModal = false">&times;</button>
        </div>

        <div class="modal-form">
          <p class="muted small" style="margin:0">
            Die <strong>UNYQ Finance Android-App</strong> nutzt dieselbe Live-Datenbank wie das Web — dein Kontostand, deine täglichen Ausgaben, Raten und dein Tag-für-Tag-Plan sind auf Handy und PC immer 1:1 synchron.
          </p>

          <div class="apk-feature-list">
            <div>✓ Startet nach dem Login direkt in <strong>UNYQ Finance</strong></div>
            <div>✓ Eigene Handy-Navigation mit Daumen-Steuerung &amp; <strong>+ Ausgabe</strong> Schnellknopf</div>
            <div>✓ Über das <strong>☰ Menü</strong> oben links jederzeit Zugriff auf alle anderen UNYQ-Plattformen</div>
          </div>

          <a
            href="https://github.com/RealRazion/proartist/releases/download/latest-apk/UNYQ-Finance.apk"
            target="_blank"
            rel="noopener"
            class="btn apk-download-hero-btn"
          >
            📲 UNYQ-Finance.apk direkt herunterladen
          </a>

          <span class="muted tiny">
            Hinweis für Android: Beim ersten Öffnen der heruntergeladenen <code>UNYQ-Finance.apk</code> kurz „Installation aus dieser Quelle zulassen“ bestätigen.
          </span>
        </div>
      </div>
    </div>

    <!-- ===== BALANCE & PROJECT SETTINGS MODAL ===== -->
    <div v-if="showBalanceModal" class="modal-overlay" @click.self="showBalanceModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Kontostand, Rahmen &amp; Puffer abgleichen</h3>
          <button type="button" class="modal-close" @click="showBalanceModal = false">&times;</button>
        </div>

        <form class="modal-form" @submit.prevent="saveBalanceSettings">
          <label>
            Projektname
            <input v-model.trim="balanceForm.title" class="input" required />
          </label>

          <div class="two-col">
            <label>
              Aktueller Kontostand / Besitz (€)
              <input v-model="balanceForm.current_balance" type="number" step="0.01" class="input" required />
              <span class="muted tiny">Darf bei Kontoüberziehung auch negativ sein (z. B. -120)</span>
            </label>
            <label>
              Geplantes Alltags-Tagesbudget (€ / Tag)
              <input v-model="balanceForm.daily_living_budget" type="number" step="0.50" min="0" class="input" />
              <span class="muted tiny">Für Essen, Einkauf &amp; Freizeit</span>
            </label>
          </div>

          <div class="two-col">
            <label>
              Dispo-Rahmen verfügbar (€)
              <input v-model="balanceForm.dispo_limit" type="number" step="10" min="0" class="input" />
            </label>
            <label>
              Davon aktuell genutzt (€)
              <input v-model="balanceForm.dispo_used" type="number" step="10" min="0" class="input" />
            </label>
          </div>

          <div class="two-col">
            <label>
              Gewünschter Sicherheits-Puffer (€)
              <input v-model="balanceForm.emergency_buffer_target" type="number" step="10" min="0" class="input" />
            </label>
            <label>
              Feste Monats-Sparrate (€)
              <input v-model="balanceForm.monthly_savings_target" type="number" step="10" min="0" class="input" />
            </label>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showBalanceModal = false">Abbrechen</button>
            <button type="submit" class="btn" :disabled="saving">{{ saving ? "Speichere..." : "Übernehmen" }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ===== CREATE ADDITIONAL PROJECT MODAL ===== -->
    <div v-if="showNewProjectModal" class="modal-overlay" @click.self="showNewProjectModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Weiteres Finanzprojekt erstellen</h3>
          <button type="button" class="modal-close" @click="showNewProjectModal = false">&times;</button>
        </div>

        <form class="modal-form" @submit.prevent="createAdditionalProject">
          <label>
            Name (z. B. Privat, Musik/Studio, Haushalt)
            <input v-model.trim="newProjForm.title" class="input" required />
          </label>
          <div class="two-col">
            <label>
              Start-Kontostand (€)
              <input v-model="newProjForm.current_balance" type="number" step="0.01" class="input" />
            </label>
            <label>
              Währung
              <select v-model="newProjForm.currency" class="input">
                <option value="EUR">EUR (€)</option>
                <option value="CHF">CHF</option>
                <option value="USD">USD ($)</option>
              </select>
            </label>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showNewProjectModal = false">Abbrechen</button>
            <button type="submit" class="btn" :disabled="saving">Projekt anlegen</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { Capacitor } from "@capacitor/core";
import api from "../api";
import FinanceDailyPlanTab from "../components/finance/FinanceDailyPlanTab.vue";
import FinanceDebtsTab from "../components/finance/FinanceDebtsTab.vue";
import FinanceEntriesTab from "../components/finance/FinanceEntriesTab.vue";
import FinanceLongTermTab from "../components/finance/FinanceLongTermTab.vue";
import FinanceSimulatorTab from "../components/finance/FinanceSimulatorTab.vue";
import {
  addDaysIso,
  calculatePeriodSimulator,
  daysInMonth,
  formatDateDe,
  formatDateShortDe,
  formatMoney,
  parseIsoParts,
  resolveDebtNextDueDate,
  round2,
  safeIsoDate,
  simulateDailyTimeline,
  simulateLongTermRoadmap,
  toNum,
  todayIso,
} from "../utils/financeEngine";

const route = useRoute();
const router = useRouter();

const loading = ref(false);
const initialLoaded = ref(false);
const saving = ref(false);

const projects = ref([]);
const project = ref(null);
const entries = ref([]);
const debts = ref([]);
const savingsGoals = ref([]);
const dailyExpenses = ref([]);
const entriesTabRef = ref(null);

const bannerMessage = ref({ type: "success", text: "" });

const VALID_TABS = ["overview", "daily", "simulator", "longterm", "debts", "entries"];
const TAB_ALIASES = {
  savings: "simulator",
  expenses: "entries",
  planned: "entries",
  subscriptions: "entries",
  projects: "overview",
};

function resolveQueryTab(rawTab) {
  if (!rawTab) return "overview";
  const key = String(rawTab).toLowerCase();
  if (VALID_TABS.includes(key)) return key;
  return TAB_ALIASES[key] || "overview";
}

const activeTab = ref(resolveQueryTab(route.query.tab));

watch(
  () => route.query.tab,
  (qTab) => {
    activeTab.value = resolveQueryTab(qTab);
  }
);

function setTab(tabId) {
  activeTab.value = tabId;
  router.replace({
    query: { ...route.query, tab: tabId === "overview" ? undefined : tabId },
  }).catch(() => {});
}

function showBanner({ type = "success", text = "" }) {
  bannerMessage.value = { type, text };
  if (type === "success") {
    setTimeout(() => {
      if (bannerMessage.value.text === text) bannerMessage.value.text = "";
    }, 3800);
  }
}

function normaliseList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

const today = todayIso();
const yesterdayIso = addDaysIso(today, -1);
const dayBeforeYesterdayIso = addDaysIso(today, -2);
const currency = computed(() => project.value?.currency || "EUR");
const currentBalance = computed(() => toNum(project.value?.current_balance, 0));
const projectDailyBudget = computed(() => toNum(project.value?.daily_living_budget, 0));

const forceMobileApp = ref(
  Capacitor.isNativePlatform() || localStorage.getItem("unyq_finance_mobile_ui") === "1"
);
const showMobileHubMenu = ref(false);
const showApkModal = ref(false);

function toggleForceMobileApp() {
  forceMobileApp.value = !forceMobileApp.value;
  localStorage.setItem("unyq_finance_mobile_ui", forceMobileApp.value ? "1" : "0");
}

function fmt(val) {
  return formatMoney(val, currency.value);
}

// ── Daily Expenses & Day-by-Day Budget Tracking ────────────────────────────
const selectedTrackerDate = ref(today);

function shiftTrackerDate(deltaDays) {
  selectedTrackerDate.value = addDaysIso(selectedTrackerDate.value || today, deltaDays);
}

function expensesForDate(dateIso) {
  return (dailyExpenses.value || []).filter((e) => String(e.date).slice(0, 10) === dateIso);
}

const todayExpensesList = computed(() => expensesForDate(today));
const todaySpentTotal = computed(() =>
  round2(todayExpensesList.value.reduce((s, e) => s + Math.max(0, toNum(e.amount)), 0))
);
const todayBudgetRemaining = computed(() =>
  round2(projectDailyBudget.value - todaySpentTotal.value)
);

const trackerDayExpenses = computed(() => expensesForDate(selectedTrackerDate.value));
const trackerDaySpent = computed(() =>
  round2(trackerDayExpenses.value.reduce((s, e) => s + Math.max(0, toNum(e.amount)), 0))
);
const trackerDayRemaining = computed(() =>
  round2(projectDailyBudget.value - trackerDaySpent.value)
);

// Quick Daily Expense Modal State
const showDailyExpenseModal = ref(false);
const quickAmountInputRef = ref(null);
const quickExpForm = ref({
  date: today,
  amount: "",
  title: "",
  category: "Lebensmittel",
  notes: "",
  deductFromBalance: true,
});

const expensePresets = [
  { icon: "🛒", label: "Supermarkt", category: "Lebensmittel", defaultTitle: "Supermarkt / Einkauf" },
  { icon: "🍔", label: "Essen & Snack", category: "Gastronomie", defaultTitle: "Essen / Snack" },
  { icon: "☕", label: "Kaffee & Drinks", category: "Alltag", defaultTitle: "Kaffee / Getränke" },
  { icon: "⛽", label: "Tanken & ÖPNV", category: "Mobilität", defaultTitle: "Tanken / Fahrt" },
  { icon: "🛍️", label: "Drogerie / Shop", category: "Einkauf", defaultTitle: "Drogerie / Shopping" },
  { icon: "🎉", label: "Freizeit", category: "Freizeit", defaultTitle: "Freizeit / Unterwegs" },
  { icon: "📦", label: "Sonstiges", category: "Sonstiges", defaultTitle: "Tägliche Ausgabe" },
];

const modalDateExpenses = computed(() => expensesForDate(quickExpForm.value.date || today));
const modalDateExistingSpent = computed(() =>
  round2(modalDateExpenses.value.reduce((s, e) => s + Math.max(0, toNum(e.amount)), 0))
);
const modalDateRemainingAfter = computed(() =>
  round2(projectDailyBudget.value - modalDateExistingSpent.value - Math.max(0, toNum(quickExpForm.value.amount, 0)))
);

function setQuickExpDate(dateIso) {
  quickExpForm.value.date = dateIso;
  quickExpForm.value.deductFromBalance = dateIso <= today;
}

function addQuickAmount(inc) {
  const cur = Math.max(0, toNum(quickExpForm.value.amount, 0));
  quickExpForm.value.amount = String(round2(cur + inc));
}

function applyExpensePreset(preset) {
  const presetTitles = expensePresets.map((p) => p.defaultTitle);
  quickExpForm.value.category = preset.category;
  if (!quickExpForm.value.title || presetTitles.includes(quickExpForm.value.title)) {
    quickExpForm.value.title = preset.defaultTitle;
  }
}

async function openDailyExpenseModal(targetDateIso = today) {
  const cleanDate = typeof targetDateIso === "string" && targetDateIso.length >= 10 ? targetDateIso.slice(0, 10) : today;
  quickExpForm.value = {
    date: cleanDate,
    amount: "",
    title: "",
    category: "Lebensmittel",
    notes: "",
    deductFromBalance: cleanDate <= today,
  };
  showDailyExpenseModal.value = true;
  await nextTick();
  quickAmountInputRef.value?.focus?.();
}

async function submitQuickDailyExpense() {
  if (!project.value) return;
  const amt = round2(Math.max(0, toNum(quickExpForm.value.amount, 0)));
  if (amt <= 0) {
    showBanner({ type: "error", text: "Bitte einen Betrag größer als 0,00 € eingeben." });
    return;
  }
  const dateStr = quickExpForm.value.date || today;
  let finalTitle = (quickExpForm.value.title || "Tägliche Ausgabe").trim();

  // Prevent unique_together (project, date, title, amount) collision if user buys same item twice on same day
  const existingSameDay = expensesForDate(dateStr);
  let suffix = 2;
  const baseTitle = finalTitle;
  while (
    existingSameDay.some(
      (e) =>
        e.title.toLowerCase() === finalTitle.toLowerCase() &&
        Math.abs(toNum(e.amount) - amt) < 0.005
    )
  ) {
    finalTitle = `${baseTitle} #${suffix}`;
    suffix += 1;
  }

  saving.value = true;
  try {
    const { data } = await api.post("daily-expenses/", {
      project: project.value.id,
      date: dateStr,
      title: finalTitle,
      category: quickExpForm.value.category || "Alltag",
      amount: amt,
      notes: quickExpForm.value.notes || "",
    });
    dailyExpenses.value = [data, ...dailyExpenses.value];
    selectedTrackerDate.value = dateStr;

    if (quickExpForm.value.deductFromBalance) {
      await adjustBalanceByDelta(-amt);
    }

    showDailyExpenseModal.value = false;
    showBanner({
      type: "success",
      text: `Ausgabe „${finalTitle}“ (−${fmt(amt)} am ${formatDateShortDe(dateStr)}) gespeichert.`,
    });
  } catch (err) {
    showBanner({
      type: "error",
      text: err?.response?.data?.detail || "Tägliche Ausgabe konnte nicht gespeichert werden.",
    });
  } finally {
    saving.value = false;
  }
}

async function deleteDailyExpenseById(expenseId) {
  const target = dailyExpenses.value.find((e) => e.id === expenseId);
  if (!target) return;
  const amt = round2(Math.max(0, toNum(target.amount, 0)));
  const wasPastOrToday = String(target.date).slice(0, 10) <= today;
  try {
    await api.delete(`daily-expenses/${expenseId}/`);
    dailyExpenses.value = dailyExpenses.value.filter((e) => e.id !== expenseId);
    if (wasPastOrToday && amt > 0) {
      await adjustBalanceByDelta(amt);
    }
    showBanner({
      type: "success",
      text: `Ausgabe „${target.title}“ gelöscht${wasPastOrToday ? ` (+${fmt(amt)} dem Kontostand gutgeschrieben)` : ""}.`,
    });
  } catch {
    showBanner({ type: "error", text: "Ausgabe konnte nicht gelöscht werden." });
  }
}

// ── Urgent & Summary Metrics ───────────────────────────────────────────────
const urgentDebtsCount = computed(() =>
  debts.value.filter((d) => {
    if (d.status !== "ACTIVE" || d.is_fully_paid) return false;
    const nd = d.next_due_date || resolveDebtNextDueDate(d, today);
    return Boolean(nd && nd <= today);
  }).length
);

const navTabs = computed(() => [
  { id: "overview", icon: "🏠", label: "Cockpit" },
  { id: "daily", icon: "📅", label: "Tag-für-Tag Plan" },
  { id: "simulator", icon: "🧮", label: "Simulator & Tools" },
  { id: "longterm", icon: "📈", label: "Langzeit-Analyse" },
  { id: "debts", icon: "💳", label: "Schulden & Raten", badge: urgentDebtsCount.value || null },
  { id: "entries", icon: "🧾", label: "Buchungen & Alltag" },
]);

const activeEntries = computed(() => entries.value.filter((e) => e.is_active !== false));

const monthlyIncomeTotal = computed(() =>
  round2(
    activeEntries.value
      .filter((e) => e.entry_type === "INCOME" && e.frequency !== "ONCE")
      .reduce((s, e) => s + toNum(e.monthly_amount ?? e.amount), 0)
  )
);

const monthlyFixedOnly = computed(() =>
  round2(
    activeEntries.value
      .filter((e) => ["FIXED", "VARIABLE", "SAVING"].includes(e.entry_type) && e.frequency !== "ONCE")
      .reduce((s, e) => s + toNum(e.monthly_amount ?? e.amount), 0)
  )
);

const monthlySubsOnly = computed(() =>
  round2(
    activeEntries.value
      .filter((e) => e.entry_type === "SUBSCRIPTION" && e.frequency !== "ONCE")
      .reduce((s, e) => s + toNum(e.monthly_amount ?? e.amount), 0)
  )
);

const monthlyFixedAndSubs = computed(() => round2(monthlyFixedOnly.value + monthlySubsOnly.value));

const monthlyDebtRateTotal = computed(() =>
  round2(
    debts.value
      .filter((d) => d.status === "ACTIVE" && !d.is_fully_paid)
      .reduce((s, d) => s + toNum(d.scheduled_payment_amount || d.monthly_payment), 0)
  )
);

const monthlyFreeAfterFixed = computed(() =>
  round2(monthlyIncomeTotal.value - monthlyFixedAndSubs.value - monthlyDebtRateTotal.value)
);

const monthlyNetAfterAll = computed(() =>
  round2(monthlyFreeAfterFixed.value - projectDailyBudget.value * 30)
);

const totalOpenDebt = computed(() =>
  round2(
    debts.value
      .filter((d) => d.status === "ACTIVE" && !d.is_fully_paid)
      .reduce((s, d) => s + toNum(d.remaining_amount), 0)
  )
);

const totalSavedGoals = computed(() =>
  round2(savingsGoals.value.reduce((s, g) => s + toNum(g.current_amount), 0))
);

const netWorthToday = computed(() =>
  round2(currentBalance.value + totalSavedGoals.value - totalOpenDebt.value - toNum(project.value?.dispo_used, 0))
);

// End-of-month daily safe budget for Cockpit Hero KPI
const monthEndDailySim = computed(() => {
  const p = parseIsoParts(today);
  const endIso = p ? safeIsoDate(p.year, p.month, daysInMonth(p.year, p.month)) : today;
  return calculatePeriodSimulator({
    startDateIso: today,
    endDateIso: endIso,
    startingMoney: currentBalance.value,
    entries: entries.value,
    debts: debts.value,
    includeScheduled: true,
    safetyFloor: toNum(project.value?.emergency_buffer_target, 0),
  });
});

// 14-Day Preview
const preview14d = computed(() =>
  simulateDailyTimeline({
    startDateIso: today,
    days: 14,
    startingBalance: currentBalance.value,
    dispoLimit: toNum(project.value?.dispo_limit, 0),
    dispoUsed: toNum(project.value?.dispo_used, 0),
    emergencyBuffer: toNum(project.value?.emergency_buffer_target, 0),
    entries: entries.value,
    debts: debts.value,
    dailyExpenses: dailyExpenses.value,
    includeDailyBudget: projectDailyBudget.value > 0,
    dailyLivingBudget: projectDailyBudget.value,
  })
);

const preview14Rows = computed(() => {
  const all = preview14d.value.timeline;
  const picked = all.filter((d, idx) => idx === 0 || idx === all.length - 1 || d.events.length > 0 || d.endBalance < 0);
  return picked.length >= 4 ? picked.slice(0, 9) : all.slice(0, 7);
});

const quickRoadmap = computed(() =>
  simulateLongTermRoadmap({
    horizonMonths: 24,
    startingBalance: currentBalance.value,
    entries: entries.value,
    debts: debts.value,
    strategy: "CURRENT",
  })
);

// ── Data Loading ───────────────────────────────────────────────────────────
async function fetchProjectsList() {
  const { data } = await api.get("finance-projects/");
  projects.value = normaliseList(data);
}

async function loadProjectBundle(projectId) {
  loading.value = true;
  try {
    const [projRes, entriesRes, debtsRes, goalsRes, expRes] = await Promise.all([
      api.get(`finance-projects/${projectId}/`),
      api.get(`finance-entries/?project=${projectId}&active=false`),
      api.get(`debts/?project=${projectId}`),
      api.get(`finance-savings-goals/?project=${projectId}`),
      api.get(`daily-expenses/?project=${projectId}`),
    ]);
    project.value = projRes.data;
    entries.value = normaliseList(entriesRes.data);
    debts.value = normaliseList(debtsRes.data);
    savingsGoals.value = normaliseList(goalsRes.data);
    dailyExpenses.value = normaliseList(expRes.data);
  } catch {
    showBanner({ type: "error", text: "Finanzdaten konnten nicht vollständig geladen werden." });
  } finally {
    loading.value = false;
  }
}

async function reloadProjectData() {
  if (!project.value) return;
  await loadProjectBundle(project.value.id);
}

async function onSwitchProject(newId) {
  const id = Number(newId);
  if (!id) return;
  localStorage.setItem("unyq_last_finance_project_id", String(id));
  if (route.name === "finance") {
    router.replace({ name: "finance", params: { projectId: id }, query: route.query }).catch(() => {});
  }
  await loadProjectBundle(id);
}

// ── Project Creation ───────────────────────────────────────────────────────
const createForm = ref({
  title: "Meine Finanzen",
  currency: "EUR",
  current_balance: "0",
  daily_living_budget: "15",
});

async function createFirstProject() {
  saving.value = true;
  try {
    const { data } = await api.post("finance-projects/", {
      title: createForm.value.title || "Meine Finanzen",
      currency: createForm.value.currency,
      current_balance: round2(toNum(createForm.value.current_balance, 0)),
      daily_living_budget: Math.max(0, round2(toNum(createForm.value.daily_living_budget, 0))),
      initial_members: [],
    });
    await fetchProjectsList();
    localStorage.setItem("unyq_last_finance_project_id", String(data.id));
    await loadProjectBundle(data.id);
    showBanner({ type: "success", text: "Dein Finanz-Cockpit ist bereit!" });
  } catch {
    showBanner({ type: "error", text: "Projekt konnte nicht angelegt werden." });
  } finally {
    saving.value = false;
  }
}

const showNewProjectModal = ref(false);
const newProjForm = ref({ title: "", currency: "EUR", current_balance: "0" });

async function createAdditionalProject() {
  if (!newProjForm.value.title) return;
  saving.value = true;
  try {
    const { data } = await api.post("finance-projects/", {
      title: newProjForm.value.title,
      currency: newProjForm.value.currency,
      current_balance: round2(toNum(newProjForm.value.current_balance, 0)),
      initial_members: [],
    });
    showNewProjectModal.value = false;
    newProjForm.value = { title: "", currency: "EUR", current_balance: "0" };
    await fetchProjectsList();
    await onSwitchProject(data.id);
    showBanner({ type: "success", text: "Projekt erstellt." });
  } catch {
    showBanner({ type: "error", text: "Projekt konnte nicht erstellt werden." });
  } finally {
    saving.value = false;
  }
}

// ── Balance & Settings Modal ───────────────────────────────────────────────
const showBalanceModal = ref(false);
const balanceForm = ref({
  title: "",
  current_balance: "0",
  daily_living_budget: "0",
  dispo_limit: "0",
  dispo_used: "0",
  emergency_buffer_target: "0",
  monthly_savings_target: "0",
});

function openBalanceModal() {
  if (!project.value) return;
  balanceForm.value = {
    title: project.value.title || "Meine Finanzen",
    current_balance: String(project.value.current_balance ?? 0),
    daily_living_budget: String(project.value.daily_living_budget ?? 0),
    dispo_limit: String(project.value.dispo_limit ?? 0),
    dispo_used: String(project.value.dispo_used ?? 0),
    emergency_buffer_target: String(project.value.emergency_buffer_target ?? 0),
    monthly_savings_target: String(project.value.monthly_savings_target ?? 0),
  };
  showBalanceModal.value = true;
}

async function saveBalanceSettings() {
  if (!project.value) return;
  saving.value = true;
  try {
    const dispoLim = Math.max(0, round2(toNum(balanceForm.value.dispo_limit, 0)));
    const dispoUsed = Math.min(dispoLim, Math.max(0, round2(toNum(balanceForm.value.dispo_used, 0))));
    const { data } = await api.patch(`finance-projects/${project.value.id}/`, {
      title: balanceForm.value.title,
      current_balance: round2(toNum(balanceForm.value.current_balance, 0)),
      daily_living_budget: Math.max(0, round2(toNum(balanceForm.value.daily_living_budget, 0))),
      dispo_limit: dispoLim,
      dispo_used: dispoUsed,
      emergency_buffer_target: Math.max(0, round2(toNum(balanceForm.value.emergency_buffer_target, 0))),
      monthly_savings_target: Math.max(0, round2(toNum(balanceForm.value.monthly_savings_target, 0))),
    });
    project.value = { ...project.value, ...data };
    await fetchProjectsList();
    showBalanceModal.value = false;
    showBanner({ type: "success", text: "Kontostand & Rahmen aktualisiert." });
  } catch (err) {
    showBanner({ type: "error", text: err?.response?.data?.detail || "Einstellungen konnten nicht gespeichert werden." });
  } finally {
    saving.value = false;
  }
}

async function saveDailyLivingBudget(newBudget) {
  if (!project.value) return;
  saving.value = true;
  try {
    const { data } = await api.patch(`finance-projects/${project.value.id}/`, {
      daily_living_budget: round2(Math.max(0, toNum(newBudget, 0))),
    });
    project.value = { ...project.value, ...data };
    showBanner({ type: "success", text: `Alltags-Tagesbudget (${fmt(newBudget)}/Tag) gespeichert.` });
  } catch {
    showBanner({ type: "error", text: "Tagesbudget konnte nicht gespeichert werden." });
  } finally {
    saving.value = false;
  }
}

async function adoptBudgetFromSimulator(budgetVal) {
  await saveDailyLivingBudget(budgetVal);
}

async function adjustBalanceByDelta(deltaAmount) {
  if (!project.value) return;
  const nextBal = round2(toNum(project.value.current_balance, 0) + toNum(deltaAmount, 0));
  try {
    const { data } = await api.patch(`finance-projects/${project.value.id}/`, {
      current_balance: nextBal,
    });
    project.value = { ...project.value, ...data };
  } catch {
    // non-fatal
  }
}

// ── Cross-Tab Actions ──────────────────────────────────────────────────────
async function handleQuickAddOnDate(dateIso) {
  setTab("entries");
  await nextTick();
  entriesTabRef.value?.openEntryModalWithPreset({
    date: dateIso,
    frequency: "ONCE",
    entry_type: "FIXED",
  });
}

async function handleCreatePlannedFromSim({ title, amount, due_date }) {
  setTab("entries");
  await nextTick();
  entriesTabRef.value?.openEntryModalWithPreset({
    date: due_date || today,
    title,
    amount,
    frequency: "ONCE",
    entry_type: "FIXED",
  });
}

async function openQuickEntryFromCockpit() {
  setTab("entries");
  await nextTick();
  entriesTabRef.value?.openEntryModalWithPreset({
    date: today,
    frequency: "MONTHLY",
    entry_type: "FIXED",
  });
}

// ── Savings Goals CRUD ─────────────────────────────────────────────────────
async function saveSavingsGoal(goalPayload) {
  if (!project.value) return;
  try {
    const body = {
      project: project.value.id,
      title: goalPayload.title,
      target_amount: round2(toNum(goalPayload.target_amount, 0)),
      current_amount: round2(toNum(goalPayload.current_amount, 0)),
      target_date: goalPayload.target_date || null,
      is_completed: Boolean(goalPayload.is_completed),
    };
    if (goalPayload.id) {
      await api.patch(`finance-savings-goals/${goalPayload.id}/`, body);
    } else {
      await api.post("finance-savings-goals/", body);
    }
    const { data } = await api.get(`finance-savings-goals/?project=${project.value.id}`);
    savingsGoals.value = normaliseList(data);
    showBanner({ type: "success", text: "Sparziel gespeichert." });
  } catch {
    showBanner({ type: "error", text: "Sparziel konnte nicht gespeichert werden." });
  }
}

async function deleteSavingsGoal(goal) {
  if (!confirm(`Sparziel „${goal.title}“ löschen?`)) return;
  try {
    await api.delete(`finance-savings-goals/${goal.id}/`);
    savingsGoals.value = savingsGoals.value.filter((g) => g.id !== goal.id);
    showBanner({ type: "success", text: "Sparziel gelöscht." });
  } catch {
    showBanner({ type: "error", text: "Sparziel konnte nicht gelöscht werden." });
  }
}

// ── CSV Export ─────────────────────────────────────────────────────────────
async function exportCsv() {
  if (!project.value) return;
  try {
    const res = await api.get(`finance-projects/${project.value.id}/export-overview/`, {
      responseType: "blob",
    });
    const url = URL.createObjectURL(new Blob([res.data], { type: "text/csv;charset=utf-8;" }));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", `unyq_finance_${project.value.title}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  } catch {
    showBanner({ type: "error", text: "CSV-Export fehlgeschlagen." });
  }
}

// ── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(async () => {
  loading.value = true;
  try {
    await fetchProjectsList();
    if (projects.value.length) {
      const routeProjId = Number(route.params.projectId || 0);
      const savedProjId = Number(localStorage.getItem("unyq_last_finance_project_id") || 0);
      const target =
        projects.value.find((p) => p.id === routeProjId) ||
        projects.value.find((p) => p.id === savedProjId) ||
        projects.value[0];
      await loadProjectBundle(target.id);
    }
  } finally {
    initialLoaded.value = true;
    loading.value = false;
  }
});
</script>

<style scoped>
.finance-platform {
  display: grid;
  gap: 16px;
  width: 100%;
  padding-bottom: 48px;
}

.eyebrow {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--brand);
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

/* Onboarding */
.empty-hero {
  padding: 48px 24px;
  text-align: center;
}

.onboarding-card {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 28px;
  padding: 28px;
  align-items: center;
}

.onb-left {
  display: grid;
  gap: 12px;
}

.onb-left h1 {
  margin: 0;
  font-size: clamp(1.6rem, 2.8vw, 2.2rem);
  line-height: 1.2;
}

.onb-left p { margin: 0; }

.feature-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 6px;
}

.feature-pills span {
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 12.5px;
  font-weight: 600;
}

.onb-form {
  padding: 20px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 14px;
}

.onb-form h3 { margin: 0; }

/* Header */
.finance-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  padding: 16px 20px;
}

.project-title-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 2px;
}

.project-title-row h1 {
  margin: 0;
  font-size: 1.4rem;
}

.project-switcher {
  width: auto;
  min-width: 200px;
  font-weight: 700;
  padding: 7px 36px 7px 12px;
}

.fh-right {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.balance-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  cursor: pointer;
  transition: border-color 0.15s ease;
}

.balance-pill-btn:hover {
  border-color: var(--brand);
}

.bp-lbl {
  font-size: 12px;
  color: var(--muted);
  font-weight: 600;
}

.bp-edit {
  color: var(--brand);
  font-size: 13px;
}

/* Toast Banner */
.toast-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 13.5px;
  font-weight: 600;
  border: 1px solid var(--border);
  background: var(--surface);
}

.toast-banner.success {
  border-color: rgba(34, 197, 94, 0.4);
  color: #22c55e;
}

.toast-banner.error {
  border-color: rgba(239, 68, 68, 0.45);
  color: #ef4444;
}

.banner-close {
  border: none;
  background: transparent;
  color: inherit;
  font-size: 18px;
  cursor: pointer;
}

/* Navigation Tabs */
.finance-tabs {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  padding: 5px;
  border-radius: 15px;
  background: var(--card);
  border: 1px solid var(--border);
}

.fin-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 9px 15px;
  border-radius: 11px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 13.5px;
  font-weight: 600;
  white-space: nowrap;
  cursor: pointer;
  transition: all 0.15s ease;
}

.fin-tab-btn:hover {
  color: var(--text);
  background: var(--surface);
}

.fin-tab-btn.active {
  background: linear-gradient(135deg, var(--brand), var(--brand-2, #35d0ff));
  color: #ffffff;
  box-shadow: 0 4px 12px rgba(47, 99, 255, 0.25);
}

.tab-badge {
  padding: 1px 7px;
  border-radius: 999px;
  background: #ef4444;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}

/* Cockpit */
.cockpit-view {
  display: grid;
  gap: 16px;
}

.alerts-stack {
  display: grid;
  gap: 10px;
}

.smart-alert {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding: 13px 18px;
  border-radius: 14px;
  border: 1px solid var(--border);
  background: var(--card);
  font-size: 13.5px;
}

.smart-alert > div {
  display: grid;
  gap: 2px;
}

.smart-alert.warn {
  border-color: rgba(245, 158, 11, 0.45);
  background: color-mix(in srgb, #f59e0b 8%, var(--card));
}

.smart-alert.danger {
  border-color: rgba(239, 68, 68, 0.48);
  background: color-mix(in srgb, #ef4444 8%, var(--card));
}

.cockpit-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(225px, 1fr));
  gap: 12px;
}

.kpi-hero-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 16px 18px;
  display: grid;
  gap: 6px;
}

.kh-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.kh-lbl {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--muted);
}

.tiny-action {
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--brand);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
}

.kh-val {
  font-size: 1.5rem;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.kh-val small {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--muted);
}

.cockpit-columns {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 16px;
  align-items: start;
}

.cockpit-side-stack {
  display: grid;
  gap: 16px;
}

.cockpit-panel {
  padding: 20px;
  display: grid;
  gap: 14px;
}

.cp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.cp-head h3 {
  margin: 0;
  font-size: 1.05rem;
}

/* Mini Timeline */
.mini-timeline {
  display: grid;
  gap: 7px;
}

.mini-day-row {
  display: grid;
  grid-template-columns: 120px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 11px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 13px;
}

.mini-day-row.is-today {
  border-color: var(--brand);
}

.mini-day-row.is-neg {
  border-color: rgba(239, 68, 68, 0.45);
}

.md-left {
  display: flex;
  align-items: center;
  gap: 6px;
}

.md-wd {
  color: var(--muted);
  font-size: 12px;
  width: 22px;
}

.md-tag {
  padding: 1px 6px;
  border-radius: 999px;
  background: var(--brand);
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

.md-events {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  overflow: hidden;
}

.md-ev {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--card);
  border: 1px solid var(--border);
}

.md-bal {
  font-variant-numeric: tabular-nums;
}

/* Cashflow Breakdown */
.cashflow-rows {
  display: grid;
  gap: 8px;
  font-size: 13.5px;
}

.cf-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.cf-divider {
  height: 1px;
  background: var(--border);
  margin: 2px 0;
}

.cf-row.total {
  font-size: 14.5px;
  font-weight: 700;
}

.quick-nav-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

/* Mini Goals */
.mini-goals {
  display: grid;
  gap: 10px;
}

.mg-row {
  display: grid;
  gap: 5px;
}

.mg-top {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.mg-bar {
  height: 6px;
  border-radius: 999px;
  background: var(--surface);
  overflow: hidden;
}

.mg-bar span {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, var(--brand), #22c55e);
}

/* Modals */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay, rgba(2, 6, 23, 0.78));
  display: grid;
  place-items: center;
  z-index: 100;
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
.amber-txt { color: #f59e0b; }
.debt-txt { color: #c084fc; }
.tiny { font-size: 12px; }
.small { font-size: 13.5px; }

/* CTA Button for Daily Expense */
.daily-exp-cta-btn {
  background: linear-gradient(135deg, #10b981, #059669);
  border-color: rgba(16, 185, 129, 0.5);
  color: #ffffff;
  font-weight: 700;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.25);
}

.daily-exp-cta-btn:hover {
  filter: brightness(1.06);
}

.active-preview-btn {
  border-color: var(--brand);
  color: var(--brand);
}

/* Daily Tracker Card inside Cockpit */
.daily-tracker-card {
  border-color: color-mix(in srgb, #10b981 32%, var(--border));
}

.dt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.dt-header h3 {
  margin: 0;
  font-size: 1.08rem;
}

.dt-date-nav {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
}

.dt-date-input {
  width: auto;
  padding: 6px 10px;
  font-size: 12.5px;
}

.dt-summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.dt-stat-box {
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 4px;
}

.dt-stat-box.highlight {
  border-color: color-mix(in srgb, var(--brand) 35%, var(--border));
}

.dt-stat-box strong {
  font-size: 1.15rem;
  font-variant-numeric: tabular-nums;
}

.dt-lbl-inline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
}

.tiny-link {
  border: none;
  background: transparent;
  color: var(--brand);
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.dt-progress-track {
  height: 8px;
  border-radius: 999px;
  background: var(--surface);
  border: 1px solid var(--border);
  overflow: hidden;
}

.dt-progress-track span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #10b981, #34d399);
  transition: width 0.2s ease;
}

.dt-progress-track span.over {
  background: linear-gradient(90deg, #f59e0b, #ef4444);
}

.dt-exp-list {
  display: grid;
  gap: 6px;
}

.dt-exp-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  padding: 9px 12px;
  border-radius: 11px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 13px;
}

.dt-exp-left {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.dt-cat-pill {
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--card);
  border: 1px solid var(--border);
  font-size: 11px;
  font-weight: 600;
  color: var(--muted);
}

.dt-exp-right {
  display: flex;
  align-items: center;
  gap: 10px;
  font-variant-numeric: tabular-nums;
}

.dt-del-btn {
  width: 24px;
  height: 24px;
  border-radius: 6px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--muted);
  font-size: 15px;
  line-height: 1;
  cursor: pointer;
}

.dt-del-btn:hover {
  border-color: #ef4444;
  color: #ef4444;
}

.dt-empty-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 11px;
  background: var(--surface);
  border: 1px dashed var(--border);
}

/* Quick Daily Expense Modal & Bottom Sheet */
.sheet-drag-handle {
  display: none;
  width: 42px;
  height: 5px;
  border-radius: 999px;
  background: var(--border);
  margin: 10px auto 2px;
}

.exp-date-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.exp-date-chips {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.chip-pill {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.chip-pill.active {
  background: var(--brand);
  border-color: var(--brand);
  color: #fff;
}

.exp-date-picker {
  width: auto;
  padding: 6px 10px;
  font-size: 12.5px;
}

.exp-amount-block {
  display: grid;
  gap: 8px;
}

.big-exp-input {
  font-size: 1.55rem;
  font-weight: 800;
  padding: 10px 14px;
  font-variant-numeric: tabular-nums;
}

.quick-amt-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.amt-add-chip {
  padding: 5px 11px;
  border-radius: 9px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.amt-add-chip:hover {
  border-color: var(--brand);
}

.amt-add-chip.clear {
  color: var(--muted);
}

.exp-cat-section {
  display: grid;
  gap: 6px;
}

.exp-cat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(128px, 1fr));
  gap: 6px;
}

.exp-preset-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
}

.exp-preset-chip.active {
  border-color: #10b981;
  background: rgba(16, 185, 129, 0.14);
}

.exp-live-impact {
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  display: grid;
  gap: 8px;
  font-size: 12.5px;
}

.eli-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.eli-check-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-top: 6px;
  border-top: 1px solid var(--border);
  cursor: pointer;
  font-size: 12.5px;
}

.modal-day-history {
  display: grid;
  gap: 6px;
  max-height: 130px;
  overflow-y: auto;
}

.mdh-list {
  display: grid;
  gap: 4px;
}

.mdh-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  border-radius: 8px;
  background: var(--surface);
  font-size: 12px;
}

.mdh-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Hub Quick Grid & APK Modal */
.hub-quick-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.hub-nav-tile {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  text-align: left;
  font-size: 12.5px;
  cursor: pointer;
}

.hub-nav-tile:hover {
  border-color: var(--brand);
}

.apk-feature-list {
  display: grid;
  gap: 6px;
  padding: 12px 14px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-size: 13px;
}

.apk-download-hero-btn {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 13px 18px;
  font-size: 14.5px;
  font-weight: 800;
  text-decoration: none;
  text-align: center;
}

/* =====================================================================
   NATIVE MOBILE APP UI (DEFAULT HIDDEN ON DESKTOP UNLESS FORCE-MOBILE)
   ===================================================================== */
.mobile-app-header,
.mobile-bottom-nav,
.mobile-more-subbar {
  display: none;
}

.mah-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.mah-brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.mah-hub-btn {
  width: 38px;
  height: 38px;
  border-radius: 11px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 17px;
  font-weight: 700;
  cursor: pointer;
}

.mah-title-wrap {
  display: grid;
  gap: 1px;
}

.mah-kicker {
  font-size: 10px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand);
}

.mah-proj-name {
  font-size: 15px;
  font-weight: 800;
}

.mah-proj-select {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 15px;
  font-weight: 800;
  padding: 0;
}

.mah-balance-pill {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 12px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 13.5px;
  cursor: pointer;
}

.mah-bal-lbl {
  font-size: 11px;
  color: var(--muted);
}

.mah-edit-ico {
  font-size: 12px;
  color: var(--brand);
}

.mah-today-strip {
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.mah-today-info {
  display: grid;
  gap: 6px;
  cursor: pointer;
}

.mah-today-topline {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 6px;
  font-size: 12px;
}

.mah-budget-bar {
  height: 6px;
  border-radius: 999px;
  background: var(--card);
  overflow: hidden;
}

.mah-budget-bar span {
  display: block;
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #10b981, #34d399);
}

.mah-budget-bar span.over {
  background: linear-gradient(90deg, #f59e0b, #ef4444);
}

.mah-quick-exp-btn {
  padding: 9px 13px;
  border-radius: 11px;
  border: none;
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  font-size: 12.5px;
  font-weight: 800;
  white-space: nowrap;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.28);
}

.mms-btn {
  flex: 1;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  gap: 5px;
  padding: 8px 10px;
  border-radius: 10px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
}

.mms-btn.active {
  background: var(--brand);
  color: #fff;
}

/* Mobile Bottom Nav Bar */
.mbn-item {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  border: none;
  background: transparent;
  color: var(--muted);
  padding: 6px 4px;
  font-size: 10.5px;
  font-weight: 700;
  cursor: pointer;
}

.mbn-item.active {
  color: var(--brand);
}

.mbn-ico {
  font-size: 18px;
  line-height: 1.1;
}

.mbn-dot {
  position: absolute;
  top: 2px;
  right: 12px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  border-radius: 999px;
  background: #ef4444;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.mbn-fab {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  margin-top: -20px;
  width: 62px;
  height: 54px;
  border-radius: 18px;
  border: 2px solid var(--card);
  background: linear-gradient(135deg, #10b981, #059669);
  color: #ffffff;
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.38);
  cursor: pointer;
}

.mbn-fab-plus {
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
}

.mbn-fab-lbl {
  font-size: 9.5px;
  font-weight: 800;
}

/* Activate Mobile App Mode when forced OR on screens <= 820px */
.finance-platform.force-mobile-app {
  max-width: 480px;
  margin: 0 auto;
  padding-bottom: 104px;
}

.finance-platform.force-mobile-app .mobile-app-header {
  display: grid;
  gap: 10px;
  padding: 12px 14px;
}

.finance-platform.force-mobile-app .desktop-only-header,
.finance-platform.force-mobile-app .desktop-only-tabs {
  display: none;
}

.finance-platform.force-mobile-app .mobile-more-subbar {
  display: flex;
  gap: 4px;
  padding: 4px;
  border-radius: 13px;
  background: var(--card);
  border: 1px solid var(--border);
}

.finance-platform.force-mobile-app .mobile-bottom-nav {
  position: fixed;
  left: 50%;
  transform: translateX(-50%);
  bottom: 0;
  width: min(480px, 100vw);
  display: grid;
  grid-template-columns: 1fr 1fr auto 1fr 1fr;
  align-items: center;
  gap: 4px;
  padding: 6px 10px calc(8px + env(safe-area-inset-bottom, 0px));
  background: color-mix(in srgb, var(--card) 94%, transparent);
  backdrop-filter: blur(14px);
  border-top: 1px solid var(--border);
  border-radius: 20px 20px 0 0;
  z-index: 85;
  box-shadow: 0 -8px 28px rgba(0, 0, 0, 0.32);
}

.finance-platform.force-mobile-app .cockpit-kpi-grid {
  grid-template-columns: 1fr 1fr;
}

.finance-platform.force-mobile-app .cockpit-columns,
.finance-platform.force-mobile-app .dt-summary-grid {
  grid-template-columns: 1fr;
}

@media (max-width: 960px) {
  .onboarding-card,
  .cockpit-columns {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 820px) {
  .finance-platform {
    padding-bottom: 100px;
    gap: 12px;
  }

  .mobile-app-header {
    display: grid;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 16px;
  }

  .desktop-only-header,
  .desktop-only-tabs {
    display: none;
  }

  .mobile-more-subbar {
    display: flex;
    gap: 4px;
    padding: 4px;
    border-radius: 13px;
    background: var(--card);
    border: 1px solid var(--border);
  }

  .mobile-bottom-nav {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    display: grid;
    grid-template-columns: 1fr 1fr auto 1fr 1fr;
    align-items: center;
    gap: 4px;
    padding: 6px 10px calc(8px + env(safe-area-inset-bottom, 0px));
    background: color-mix(in srgb, var(--card) 95%, transparent);
    backdrop-filter: blur(14px);
    border-top: 1px solid var(--border);
    z-index: 85;
    box-shadow: 0 -8px 28px rgba(0, 0, 0, 0.35);
  }

  .cockpit-kpi-grid {
    grid-template-columns: 1fr 1fr;
    gap: 8px;
  }

  .kpi-hero-card {
    padding: 12px 14px;
  }

  .kh-val {
    font-size: 1.2rem;
  }

  .dt-summary-grid {
    grid-template-columns: 1fr;
  }

  .bottom-sheet-overlay {
    align-items: end;
    padding: 0;
  }

  .bottom-sheet-box {
    width: 100%;
    max-height: 92vh;
    border-radius: 24px 24px 0 0;
    border-bottom: none;
  }

  .sheet-drag-handle {
    display: block;
  }
}

@media (max-width: 640px) {
  .two-col,
  .quick-nav-grid,
  .hub-quick-grid {
    grid-template-columns: 1fr;
  }
  .mini-day-row {
    grid-template-columns: 1fr auto;
  }
  .md-events {
    grid-column: 1 / -1;
  }
}
</style>
