<template>
  <div class="finance-tool">
    <section v-if="loading && !project" class="status-card loading-card">
      <h1>Finanzplaner</h1>
      <p class="muted">Lade Finanzprojekt...</p>
    </section>

    <section v-else-if="!projects.length" class="status-card empty-card">
      <h1>Kein Finanzprojekt vorhanden</h1>
      <p class="muted">Lege zuerst ein Finanzprojekt an. Danach kannst du hier deine Monatsplanung klar strukturieren.</p>
      <button class="btn" type="button" @click="router.push({ name: 'platform-finance' })">Zum Einstieg</button>
    </section>

    <template v-else>
      <header class="topbar-card">
        <div class="topbar-main">
          <div class="topbar-meta">
            <p class="eyebrow">Finanzplaner</p>
            <h1>{{ project?.title || "Finanzprojekt" }}</h1>
          </div>

          <div class="topbar-actions">
            <div class="topbar-buttons">
              <button class="btn ghost" type="button" @click="refreshCurrent" :disabled="loading">Aktualisieren</button>
              <button class="btn ghost" type="button" @click="showProjectSettingsModal = true">Projektbasis</button>
              <button class="btn ghost" type="button" @click="openForecastModal" :disabled="loading">Prognose</button>
              <button class="btn ghost" type="button" @click="openCompareModal" :disabled="loading">Vergleich</button>
              <button class="btn" type="button" @click="exportOverview">Exportieren</button>
            </div>
          </div>
        </div>
      </header>

      <section v-if="errorMessage || successMessage" class="feedback-bar">
        <div v-if="errorMessage" class="feedback-pill error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="feedback-pill success">{{ successMessage }}</div>
      </section>

      <div class="tab-nav">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="tab-pill"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          {{ tabLabels[tab] }}
        </button>
      </div>

      <section class="summary-band">
        <article class="metric-card balance-card">
          <div class="metric-top">
            <div>
              <span class="metric-label">Frei im Monat</span>
              <strong>{{ formatCurrency(overview.monthly_left) }}</strong>
            </div>
            <span class="metric-pill">{{ overview.snapshot_month }}</span>
          </div>
          <p class="metric-note">Einnahmen minus Ausgaben, Sparen und Schuldentilgung. Hier siehst du direkt, ob der Monat aufgeht.</p>
          <div class="metric-progress">
            <span class="metric-pill small">{{ overview.people_count }} Personen</span>
            <span class="metric-pill small">{{ overview.active_entry_count || 0 }} aktive Posten</span>
          </div>
          <div class="metric-breakdown">
            <p class="metric-breakdown-row current-balance-row">
              <span>Aktueller Kontostand:</span>
              <strong>{{ formatCurrency(currentBalance) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>Saldo ohne Dispo:</span>
              <strong>{{ formatCurrency(projectedBalanceWithoutDispo) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>Saldo mit Dispo:</span>
              <strong>{{ formatCurrency(projectedBalanceWithDispo) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>Dispo genutzt:</span>
              <strong>{{ formatCurrency(dispoUsed) }}</strong>
            </p>
          </div>
        </article>

        <article class="metric-card">
          <span class="metric-label">Monatliche Einnahmen</span>
          <strong>{{ formatCurrency(overview.monthly_income) }}</strong>
          <p class="metric-note">Fixe und wiederkehrende Werte, die den Monat tragen.</p>
        </article>

        <article class="metric-card">
          <span class="metric-label">Monatliche Ausgaben</span>
          <strong>{{ formatCurrency(overview.monthly_outflow) }}</strong>
          <p class="metric-note">Gesamter Mittelabfluss inklusive Sparen, Schulden und laufender Kosten.</p>
          <div class="metric-breakdown">
            <p class="metric-breakdown-row">
              <span>davon Abos:</span>
              <strong>{{ formatCurrency(monthlySubscriptions) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>davon Kredite:</span>
              <strong>{{ formatCurrency(monthlyCreditOutflow) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>davon regelmäßig geplant:</span>
              <strong>{{ formatCurrency(monthlyPlannedOutflow) }}</strong>
            </p>
            <p class="metric-breakdown-row">
              <span>davon variabel/einmalig:</span>
              <strong>{{ formatCurrency(monthlyUnplannedOutflow) }}</strong>
            </p>
          </div>
        </article>

        <article class="metric-card due-metric-card">
          <span class="metric-label">Fälligkeiten</span>
          <ul class="due-metric-list">
            <li v-if="!dueSoonPreview.length" class="muted small">Keine baldigen Fälligkeiten vorhanden.</li>
            <li v-for="item in dueSoonPreview" :key="item.id" class="due-metric-item">
              <span>{{ item.title }}</span>
              <strong :class="dueAmountClass(item)">{{ dueAmountText(item) }}</strong>
            </li>
          </ul>
        </article>
      </section>

      <section class="tab-panel">
        <div class="workspace-shell">
          <main class="workspace-main">
            <section v-show="activeTab === 'planner'" class="planner-page">
              <div class="planner-grid">
                <article class="panel chart-panel">
                  <div class="panel-head planner-head">
                    <div>
                      <h2>Monatliche Struktur</h2>
                      <p class="muted">Übersicht über Einnahmen, Ausgaben und Nettoergebnis.</p>
                    </div>
                    <div class="planner-head-controls">
                      <label class="planner-month-control">
                        Monat
                        <input v-model="plannerMonth" type="month" class="input" />
                      </label>
                      <span class="badge">{{ overview.snapshot_month }}</span>
                    </div>
                  </div>

                  <div class="performance-cards">
                    <div class="performance-item income">
                      <span>Einnahmen</span>
                      <strong>{{ formatCurrency(overview.monthly_income) }}</strong>
                    </div>
                    <div class="performance-item outcome">
                      <span>Ausgaben</span>
                      <strong>{{ formatCurrency(overview.monthly_outflow) }}</strong>
                    </div>
                    <div class="performance-item balance">
                      <span>Saldo</span>
                      <strong>{{ formatCurrency(overview.monthly_left) }}</strong>
                    </div>
                  </div>

                  <div v-if="chartScaleMax > 0" class="chart-container">
                    <div class="chart-bar income" :style="{ '--bar-height': `${incomeBarHeight}%` }">
                      <span>Einnahmen</span>
                      <strong>{{ formatCurrency(overview.monthly_income) }}</strong>
                    </div>
                    <div class="chart-bar expense" :style="{ '--bar-height': `${expenseBarHeight}%` }">
                      <span>Ausgaben</span>
                      <strong>{{ formatCurrency(overview.monthly_outflow) }}</strong>
                    </div>
                  </div>
                  <div v-else class="chart-empty-state">
                    <p class="muted">{{ plannerEmptyMessage }}</p>
                  </div>
                </article>

                <article class="panel summary-split-panel">
                  <div class="panel-head panel-head-space">
                    <div>
                      <h2>Einnahmen und Ausgaben</h2>
                      <p class="muted">Beide Bereiche kompakt im selben Fenster.</p>
                    </div>
                    <button class="btn" type="button" @click="openCreateEntryModal">Posten hinzufügen</button>
                  </div>

                  <div class="summary-split-grid">
                    <section class="summary-column">
                      <h3>Einnahmen</h3>
                      <ul v-if="plannerIncomeEntries.length" class="summary-sublist">
                        <li v-for="entry in plannerIncomeEntries" :key="entry.id" class="summary-subitem">
                          <span>{{ entry.title }}</span>
                          <strong>{{ formatCurrency(entry.monthly_amount || entry.amount) }}</strong>
                        </li>
                      </ul>
                      <p v-else class="muted small">Keine Einnahmen hinterlegt.</p>
                    </section>

                    <section class="summary-column">
                      <h3>Ausgaben</h3>
                      <ul v-if="plannerExpenseEntries.length" class="summary-sublist">
                        <li v-for="entry in plannerExpenseEntries" :key="entry.id" class="summary-subitem">
                          <span>{{ entry.title }}</span>
                          <strong>{{ formatCurrency(entry.monthly_amount || entry.amount) }}</strong>
                        </li>
                      </ul>
                      <p v-else class="muted small">Keine Ausgaben hinterlegt.</p>
                    </section>
                  </div>
                </article>
              </div>

              <article class="panel entries-panel">
                <div class="panel-head panel-head-space">
                  <div>
                    <h2>Posten</h2>
                    <p class="muted">Wähle einen Filter, um die Auflistung direkt einzuordnen.</p>
                  </div>
                  <div class="filter-row">
                    <button
                      v-for="option in entryFilters"
                      :key="option.value"
                      type="button"
                      class="chip"
                      :class="{ active: activeEntryFilter === option.value }"
                      @click="activeEntryFilter = option.value"
                    >
                      {{ option.label }}
                    </button>
                  </div>
                </div>

                <div v-if="filteredEntries.length" class="entry-list">
                  <article v-for="entry in filteredEntries" :key="entry.id" class="entry-row" :class="{ inactive: !entry.is_active }">
                    <div class="entry-main">
                      <div class="entry-title-line">
                        <strong>{{ entry.title }}</strong>
                        <span class="type-badge" :data-type="entry.entry_type">{{ entryTypeLabels[entry.entry_type] }}</span>
                      </div>
                      <p class="muted small">
                        {{ entry.category || "Ohne Kategorie" }} · {{ frequencyLabels[entry.frequency] }} ·
                        {{ entry.member_name || (entry.is_shared ? "Gemeinsam" : "Nicht zugeordnet") }}
                      </p>
                      <p v-if="entry.notes" class="muted small">{{ entry.notes }}</p>
                    </div>
                    <div class="entry-side">
                      <strong>{{ formatCurrency(entry.amount) }}</strong>
                      <span class="muted small">Monatlich: {{ formatCurrency(entry.monthly_amount) }}</span>
                      <span class="muted small">{{ dueLabel(entry) }}</span>
                      <div class="entry-actions">
                        <button class="btn ghost sm" type="button" @click="editEntry(entry)">Bearbeiten</button>
                        <button class="btn ghost sm" type="button" @click="toggleEntry(entry)">{{ entry.is_active ? "Pausieren" : "Aktivieren" }}</button>
                        <button class="btn ghost sm danger" type="button" @click="removeEntry(entry)">Löschen</button>
                      </div>
                    </div>
                  </article>
                </div>
                <p v-else class="muted empty-hint">Kein Posten im aktuellen Filter.</p>
              </article>

              <article class="panel list-panel top-categories-panel">
                <div class="panel-head">
                  <h2>Top-Kategorien</h2>
                </div>
                <ul class="compact-list">
                  <li v-if="!overview.top_categories?.length" class="empty-text">Keine Kategoriendaten verfügbar.</li>
                  <li v-for="item in overview.top_categories" :key="item.category">
                    <span>{{ item.category }}</span>
                    <strong>{{ formatCurrency(item.amount) }}</strong>
                  </li>
                </ul>
              </article>
            </section>

            <section v-show="activeTab === 'daily'" class="daily-page">
              <div class="daily-header">
                <div>
                  <h2>Tägliche Ausgaben</h2>
                  <p class="muted">Verfolge alltägliche Ausgaben wie Einkäufe, Kaffee und Transport.</p>
                </div>
                <div class="daily-controls">
                  <label>
                    Monat
                    <input v-model="dailyMonth" type="month" class="input" @change="loadDailyExpenses" />
                  </label>
                  <button class="btn" type="button" @click="openCreateDailyExpenseModal">Neue Ausgabe</button>
                </div>
              </div>

              <div class="daily-summary">
                <div class="summary-item">
                  <span class="label">Gesamt</span>
                  <strong>{{ formatCurrency(dailyExpensesTotal) }}</strong>
                </div>
                <div class="summary-item">
                  <span class="label">Einträge</span>
                  <strong>{{ dailyExpenses.length }}</strong>
                </div>
                <div class="summary-item">
                  <span class="label">Ø pro Tag</span>
                  <strong>{{ formatCurrency(dailyExpensesAverage) }}</strong>
                </div>
              </div>

              <div v-if="dailyExpenses.length" class="daily-list">
                <article v-for="expense in dailyExpenses" :key="expense.id" class="daily-item">
                  <div class="daily-main">
                    <div class="daily-title-line">
                      <strong>{{ expense.title }}</strong>
                      <span class="category-badge" v-if="expense.category">{{ expense.category }}</span>
                    </div>
                    <p class="muted small">{{ formatDate(expense.date) }} · {{ expense.member_name || "Nicht zugeordnet" }}</p>
                    <p v-if="expense.notes" class="muted small">{{ expense.notes }}</p>
                  </div>
                  <div class="daily-side">
                    <strong>{{ formatCurrency(expense.amount) }}</strong>
                    <div class="daily-actions">
                      <button class="btn ghost sm" type="button" @click="editDailyExpense(expense)">Bearbeiten</button>
                      <button class="btn ghost sm danger" type="button" @click="removeDailyExpense(expense)">Löschen</button>
                    </div>
                  </div>
                </article>
              </div>

              <div v-else class="empty-state">
                <p class="muted">Noch keine täglichen Ausgaben für {{ dailyMonthLabel }}.</p>
                <button class="btn" type="button" @click="openCreateDailyExpenseModal">Erste Ausgabe hinzufügen</button>
              </div>
            </section>

            <section v-show="activeTab === 'debts'" class="debt-page">
              <article class="panel debt-summary-panel">
                <div class="panel-head">
                  <div>
                    <h2>Schuldenübersicht</h2>
                    <p class="muted">Gesamtbestand und monatliche Belastung.</p>
                  </div>
                </div>
                <div class="status-grid">
                  <div>
                    <span class="info-label">Total</span>
                    <strong>{{ formatCurrency(overview.total_debt) }}</strong>
                  </div>
                  <div>
                    <span class="info-label">Kredite offen</span>
                    <strong>{{ formatCurrency(overview.total_credit || 0) }}</strong>
                  </div>
                  <div>
                    <span class="info-label">Monatlich</span>
                    <strong>{{ formatCurrency(overview.monthly_debt) }}</strong>
                  </div>
                  <div>
                    <span class="info-label">Fällig bald</span>
                    <strong>{{ overview.due_soon?.filter(item => item.entry_type === 'DEBT').length || 0 }}</strong>
                  </div>
                </div>
              </article>

              <DebtTracker :projectId="selectedProjectId" />
            </section>

            <section v-show="activeTab === 'tips'" class="tips-page">
              <article class="panel tips-panel">
                <div class="panel-head panel-head-space">
                  <div>
                    <h2>Tipps und Einnahmequellen</h2>
                    <p class="muted">Cashback, Rabattaktionen und Empfehlungsprogramme direkt im Planer.</p>
                  </div>
                  <button class="btn ghost" type="button" @click="router.push({ name: 'platform-content-studio' })">
                    Zum Content Studio
                  </button>
                </div>

                <div v-if="loadingFinanceTips" class="skeleton-list">
                  <div class="skeleton-card" v-for="n in 3" :key="`tip-sk-${n}`"></div>
                </div>
                <ul v-else-if="financeTips.length" class="tip-list">
                  <li v-for="tip in financeTips" :key="tip.id" class="tip-card">
                    <div class="tip-head">
                      <h3>{{ tip.title }}</h3>
                      <span class="badge badge-soft">{{ tipTypeLabel(tip.tip_type) }}</span>
                    </div>
                    <p class="muted small">{{ formatDate(tip.created_at) }} von {{ tip.author?.name || tip.author?.username || "Team" }}</p>
                    <p class="tip-body">{{ tip.body }}</p>
                  </li>
                </ul>
                <div v-else class="empty-state">
                  <p class="muted">Noch keine Tipps und Einnahmequellen vorhanden.</p>
                  <button class="btn" type="button" @click="router.push({ name: 'platform-content-studio' })">
                    Inhalte ansehen
                  </button>
                </div>
              </article>
            </section>
          </main>
        </div>
      </section>
    </template>

    <!-- Project Settings Modal -->
      <div v-if="showProjectSettingsModal" class="modal-overlay" @click="showProjectSettingsModal = false">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Projektbasis</h3>
            <button class="modal-close" @click="showProjectSettingsModal = false">&times;</button>
          </div>
          <div class="modal-body">
            <form class="stack-form" @submit.prevent="saveProjectFromModal">
              <div class="settings-grid">
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
                  Aktuelles Guthaben
                  <input v-model="projectForm.current_balance" class="input" type="number" step="0.01" />
                </label>
                <label>
                  Dispo verfügbar
                  <input v-model="projectForm.dispo_limit" class="input" type="number" step="0.01" min="0" />
                </label>
                <label>
                  Dispo genutzt
                  <input v-model="projectForm.dispo_used" class="input" type="number" step="0.01" min="0" />
                </label>
                <label>
                  Sparziel pro Monat
                  <input v-model="projectForm.monthly_savings_target" class="input" type="number" step="0.01" />
                </label>
                <label>
                  Notgroschen-Ziel
                  <input v-model="projectForm.emergency_buffer_target" class="input" type="number" step="0.01" />
                </label>
                <label class="full">
                  Notiz
                  <textarea v-model.trim="projectForm.description" class="input textarea" rows="3"></textarea>
                </label>
              </div>
              <div class="modal-actions">
                <button class="btn ghost" type="button" @click="showProjectSettingsModal = false">Abbrechen</button>
                <button class="btn" type="submit" :disabled="savingProject">
                  {{ savingProject ? "Speichere..." : "Basis speichern" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

    <!-- Forecast Modal -->
      <div v-if="showForecastModal" class="modal-overlay" @click="closeForecastModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Monatsprognose</h3>
            <button class="modal-close" @click="closeForecastModal">&times;</button>
          </div>
          <div class="modal-body">
            <label>
              Monat auswählen
              <input v-model="forecastMonth" type="month" class="input" />
            </label>
            <button class="btn" @click="calculateForecast" :disabled="calculatingForecast">
              {{ calculatingForecast ? "Berechne..." : "Prognose berechnen" }}
            </button>
            <div v-if="forecast" class="forecast-result">
              <h4>Prognose für {{ forecast.month }}</h4>
              <p v-if="forecast.project_start_month" class="muted small">
                Kumulierung ab {{ forecast.project_start_month }} (Projekterstellung)
              </p>
              <div class="forecast-grid">
                <div>
                  <span>Einnahmen</span>
                  <strong>{{ formatCurrency(forecast.income) }}</strong>
                </div>
                <div>
                  <span>Ausgaben</span>
                  <strong>{{ formatCurrency(forecast.expenses) }}</strong>
                </div>
                <div>
                  <span>Schuldenzahlungen</span>
                  <strong>{{ formatCurrency(forecast.debt_payments) }}</strong>
                </div>
                <div>
                  <span>Gesamt Ausgaben</span>
                  <strong>{{ formatCurrency(forecast.total_expenses) }}</strong>
                </div>
                <div>
                  <span>Verbleibende Schulden</span>
                  <strong>{{ formatCurrency(forecast.remaining_debt) }}</strong>
                </div>
                <div>
                  <span>Netto diesen Monat</span>
                  <strong>{{ formatCurrency(forecast.net_income) }}</strong>
                </div>
                <div v-if="forecast.savings_percentage > 0">
                  <span>Sparen ({{ forecast.savings_percentage }}%)</span>
                  <strong>{{ formatCurrency(forecast.savings_amount) }}</strong>
                </div>
                <div v-if="forecast.carryover !== 0" class="forecast-carryover">
                  <span>Übertrag Vormonate</span>
                  <strong :class="forecast.carryover >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(forecast.carryover) }}
                  </strong>
                </div>
                <div class="forecast-cumulative">
                  <span>Kumulierter Saldo</span>
                  <strong :class="forecast.cumulative_balance >= 0 ? 'positive' : 'negative'">
                    {{ formatCurrency(forecast.cumulative_balance) }}
                  </strong>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Compare Modal -->
      <div v-if="showCompareModal" class="modal-overlay" @click="closeCompareModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>Monate vergleichen</h3>
            <button class="modal-close" @click="closeCompareModal">&times;</button>
          </div>
          <div class="modal-body">
            <div class="grid two">
              <label>
                Monat 1
                <input v-model="compareMonth1" type="month" class="input" />
              </label>
              <label>
                Monat 2
                <input v-model="compareMonth2" type="month" class="input" />
              </label>
            </div>
            <button class="btn" @click="calculateComparison" :disabled="calculatingComparison">
              {{ calculatingComparison ? "Berechne..." : "Vergleich berechnen" }}
            </button>
            <div v-if="comparison" class="comparison-result">
              <h4>Vergleich</h4>
              <div class="table-responsive">
              <table class="comparison-table table-stack">
                <thead>
                  <tr>
                    <th>Kategorie</th>
                    <th>{{ comparison.month1 }}</th>
                    <th>{{ comparison.month2 }}</th>
                    <th>Differenz</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td data-label="Kategorie">Einnahmen</td>
                    <td :data-label="comparison.month1">{{ formatCurrency(comparison.forecast1.income) }}</td>
                    <td :data-label="comparison.month2">{{ formatCurrency(comparison.forecast2.income) }}</td>
                    <td data-label="Differenz">{{ formatCurrency(comparison.forecast2.income - comparison.forecast1.income) }}</td>
                  </tr>
                  <tr>
                    <td data-label="Kategorie">Ausgaben</td>
                    <td :data-label="comparison.month1">{{ formatCurrency(comparison.forecast1.expenses) }}</td>
                    <td :data-label="comparison.month2">{{ formatCurrency(comparison.forecast2.expenses) }}</td>
                    <td data-label="Differenz">{{ formatCurrency(comparison.forecast2.expenses - comparison.forecast1.expenses) }}</td>
                  </tr>
                  <tr>
                    <td data-label="Kategorie">Netto-Einkommen</td>
                    <td :data-label="comparison.month1">{{ formatCurrency(comparison.forecast1.net_income) }}</td>
                    <td :data-label="comparison.month2">{{ formatCurrency(comparison.forecast2.net_income) }}</td>
                    <td data-label="Differenz">{{ formatCurrency(comparison.forecast2.net_income - comparison.forecast1.net_income) }}</td>
                  </tr>
                </tbody>
              </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Entry Modal -->
      <div v-if="showEntryModal" class="modal-overlay" @click="closeEntryModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ editingEntryId ? "Posten bearbeiten" : "Neuer Posten" }}</h3>
            <button class="modal-close" @click="closeEntryModal">&times;</button>
          </div>
          <div class="modal-body">
            <form class="stack-form" @submit.prevent="saveEntry">
              <label>
                Titel
                <input v-model.trim="entryForm.title" class="input" placeholder="z. B. Miete" required />
              </label>
              <div class="grid two">
                <label>
                  Typ
                  <select v-model="entryForm.entry_type" class="input">
                    <option v-for="(label, key) in entryTypeFormOptions" :key="key" :value="key">{{ label }}</option>
                  </select>
                </label>
                <label>
                  Betrag
                  <input v-model="entryForm.amount" class="input" type="number" step="0.01" min="0" required />
                </label>
              </div>

              <div class="grid two">
                <label>
                  Rhythmus
                  <select v-model="entryForm.frequency" class="input">
                    <option v-for="(label, key) in frequencyLabels" :key="key" :value="key">{{ label }}</option>
                  </select>
                </label>
                <label>
                  Kategorie
                  <input
                    v-model.trim="entryForm.category"
                    class="input"
                    placeholder="z. B. Wohnen"
                    list="finance-category-suggestions"
                  />
                </label>
              </div>

              <div class="grid two">
                <label>
                  Zugeordnet an
                  <select v-model="entryForm.member" class="input">
                    <option :value="null">Nicht zugeordnet</option>
                    <option v-for="member in members" :key="member.id" :value="member.id">{{ member.name }}</option>
                  </select>
                </label>
                <label>
                  Monatlicher Fälligkeitstag
                  <input
                    v-model="entryForm.due_day"
                    class="input"
                    type="number"
                    min="1"
                    max="31"
                    :disabled="entryForm.frequency !== 'MONTHLY'"
                    placeholder="optional"
                  />
                </label>
              </div>

              <label>
                {{ entryDateFieldLabel }}
                <input v-model="entryForm.due_date" class="input" type="date" :disabled="entryDateFieldDisabled" />
              </label>

              <p class="muted small form-hint">
                Monatliche Posten dürfen auch ohne Fälligkeitstag gespeichert werden. Schulden pflegst du unten separat.
              </p>

              <label>
                Notiz
                <textarea v-model.trim="entryForm.notes" class="input textarea" rows="3" placeholder="optional"></textarea>
              </label>

              <div class="toggle-row">
                <label class="toggle">
                  <input v-model="entryForm.is_shared" type="checkbox" />
                  Gemeinsam rechnen
                </label>
                <label class="toggle">
                  <input v-model="entryForm.is_active" type="checkbox" />
                  Aktiv
                </label>
              </div>

              <div class="modal-actions">
                <button class="btn ghost" type="button" @click="closeEntryModal">Abbrechen</button>
                <button class="btn" type="submit" :disabled="savingEntry">
                  {{ savingEntry ? "Speichere..." : editingEntryId ? "Posten speichern" : "Posten anlegen" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <!-- Daily Expense Modal -->
      <div v-if="showDailyExpenseModal" class="modal-overlay" @click="closeDailyExpenseModal">
        <div class="modal-content" @click.stop>
          <div class="modal-header">
            <h3>{{ editingDailyExpenseId ? "Ausgabe bearbeiten" : "Neue tägliche Ausgabe" }}</h3>
            <button class="modal-close" @click="closeDailyExpenseModal">&times;</button>
          </div>
          <div class="modal-body">
            <form class="stack-form" @submit.prevent="saveDailyExpense">
              <div class="grid two">
                <label>
                  Datum
                  <input v-model="dailyExpenseForm.date" class="input" type="date" required />
                </label>
                <label>
                  Betrag
                  <input v-model="dailyExpenseForm.amount" class="input" type="number" step="0.01" min="0" required />
                </label>
              </div>

              <label>
                Titel
                <input v-model.trim="dailyExpenseForm.title" class="input" placeholder="z. B. Aldi Einkauf" required />
              </label>

              <div class="grid two">
                <label>
                  Kategorie
                  <input
                    v-model.trim="dailyExpenseForm.category"
                    class="input"
                    placeholder="z. B. Lebensmittel"
                    list="finance-category-suggestions"
                  />
                </label>
                <label>
                  Zugeordnet an
                  <select v-model="dailyExpenseForm.member" class="input">
                    <option :value="null">Nicht zugeordnet</option>
                    <option v-for="member in members" :key="member.id" :value="member.id">{{ member.name }}</option>
                  </select>
                </label>
              </div>

              <label>
                Notiz
                <textarea v-model.trim="dailyExpenseForm.notes" class="input textarea" rows="2" placeholder="optional"></textarea>
              </label>

              <div class="modal-actions">
                <button class="btn ghost" type="button" @click="closeDailyExpenseModal">Abbrechen</button>
                <button class="btn" type="submit" :disabled="savingDailyExpense">
                  {{ savingDailyExpense ? "Speichere..." : editingDailyExpenseId ? "Ausgabe speichern" : "Ausgabe hinzufügen" }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      <datalist id="finance-category-suggestions">
        <option v-for="category in categorySuggestions" :key="category" :value="category"></option>
      </datalist>
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
const savingMember = ref(false);
const savingEntry = ref(false);
const projects = ref([]);
const project = ref(null);
const selectedProjectId = ref(null);
const activeEntryFilter = ref("ALL");
const activeTab = ref("planner");
const editingEntryId = ref(null);
const membersPanelOpen = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const showForecastModal = ref(false);
const forecastMonth = ref(new Date().toISOString().slice(0, 7));
const forecast = ref(null);
const calculatingForecast = ref(false);
const showCompareModal = ref(false);
const compareMonth1 = ref(new Date().toISOString().slice(0, 7));
const compareMonth2 = ref(new Date().toISOString().slice(0, 7));
const comparison = ref(null);
const calculatingComparison = ref(false);
const showProjectSettingsModal = ref(false);
const showEntryModal = ref(false);
const showDailyExpenseModal = ref(false);
const dailyMonth = ref(new Date().toISOString().slice(0, 7));
const plannerMonth = ref(new Date().toISOString().slice(0, 7));
const dailyExpenses = ref([]);
const financeTips = ref([]);
const loadingFinanceTips = ref(false);
const editingDailyExpenseId = ref(null);
const savingDailyExpense = ref(false);
const localStoredCategories = ref(loadStoredCategories());

const tabs = ["planner", "daily", "debts", "tips"];
const tabLabels = {
  planner: "Planer",
  daily: "Tägliche Ausgaben",
  debts: "Schulden",
  tips: "Tipps und Einnahmequellen",
};
const tipTypeLabels = {
  CASHBACK: "Cashback",
  DISCOUNT: "Rabattaktion",
  REFERRAL: "Empfehlungsprämie",
  OTHER: "Sonstiges",
};

const memberRoleLabels = {
  PRIMARY: "Hauptperson",
  PARTNER: "Partner",
  CHILD: "Kind",
  OTHER: "Weitere Person",
};

const entryTypeLabels = {
  INCOME: "Einnahme",
  FIXED: "Fixkosten",
  VARIABLE: "Variabel",
  DEBT: "Schulden",
  SAVING: "Sparen",
};

const frequencyLabels = {
  MONTHLY: "Monatlich",
  WEEKLY: "Wöchentlich",
  YEARLY: "Jährlich",
  ONCE: "Einmalig",
};

const entryTypeFormOptions = computed(() => {
  const options = {
    INCOME: entryTypeLabels.INCOME,
    FIXED: entryTypeLabels.FIXED,
    VARIABLE: entryTypeLabels.VARIABLE,
    SAVING: entryTypeLabels.SAVING,
  };
  if (entryForm.value.entry_type === "DEBT") {
    options.DEBT = "Schulden (Altbestand)";
  }
  return options;
});

const entryFilters = [
  { value: "ALL", label: "Alle" },
  { value: "INCOME", label: "Einnahmen" },
  { value: "FIXED", label: "Fixkosten" },
  { value: "VARIABLE", label: "Variabel" },
  { value: "DEBT", label: "Schulden" },
  { value: "SAVING", label: "Sparen" },
];

const projectForm = ref(buildProjectForm());
const memberForm = ref(buildMemberForm());
const entryForm = ref(buildEntryForm());
const dailyExpenseForm = ref(buildDailyExpenseForm());

function buildProjectForm(data = {}) {
  return {
    title: data.title || "",
    description: data.description || "",
    currency: data.currency || "EUR",
    current_balance: data.current_balance ?? 0,
    dispo_limit: data.dispo_limit ?? 0,
    dispo_used: data.dispo_used ?? 0,
    monthly_savings_target: data.monthly_savings_target ?? 0,
    emergency_buffer_target: data.emergency_buffer_target ?? 0,
  };
}

function buildMemberForm() {
  return {
    name: "",
    role: "PRIMARY",
    notes: "",
  };
}

function buildEntryForm(data = {}) {
  return {
    title: data.title || "",
    category: data.category || "",
    entry_type: data.entry_type || "FIXED",
    amount: data.amount ?? "",
    frequency: data.frequency || "MONTHLY",
    due_day: data.due_day ?? "",
    due_date: data.due_date || "",
    member: data.member ?? null,
    is_shared: Boolean(data.is_shared),
    is_active: data.is_active ?? true,
    notes: data.notes || "",
  };
}

function buildDailyExpenseForm(data = {}) {
  return {
    date: data.date || new Date().toISOString().split('T')[0],
    title: data.title || "",
    category: data.category || "",
    amount: data.amount ?? "",
    member: data.member ?? null,
    notes: data.notes || "",
  };
}

const overview = computed(() => project.value?.overview || {});
const members = computed(() => project.value?.members || []);
const entries = computed(() => project.value?.entries || []);
const currency = computed(() => project.value?.currency || "EUR");
const currentBalance = computed(() => Number(project.value?.current_balance ?? overview.value?.current_balance ?? 0));
const currentMonthLabel = computed(() => new Date().toISOString().slice(0, 7));
const plannerMonthLabel = computed(() => {
  if (!isValidMonth(plannerMonth.value)) return currentMonthLabel.value;
  return plannerMonth.value;
});
const memberPreview = computed(() => members.value.slice(0, 4));
const dueSoonPreview = computed(() => {
  const source = Array.isArray(overview.value?.due_soon) ? overview.value.due_soon : [];
  return source.slice(0, 5);
});
const monthlyCreditOutflow = computed(() => Number(overview.value.monthly_credit || 0));
const projectedBalanceWithoutDispo = computed(() => Number(overview.value.projected_balance || 0));
const projectedBalanceWithDispo = computed(() => {
  const fromOverview = overview.value.projected_balance_with_dispo;
  if (fromOverview !== undefined && fromOverview !== null) {
    return Number(fromOverview || 0);
  }
  const dispoLimit = Math.max(0, Number(overview.value.dispo_limit || 0));
  const dispoUsedValue = Math.max(0, Number(overview.value.dispo_used || 0));
  const dispoRemaining = Math.max(0, dispoLimit - dispoUsedValue);
  return projectedBalanceWithoutDispo.value + dispoRemaining;
});
const dispoUsed = computed(() => {
  const manualUsed = overview.value.dispo_used;
  if (manualUsed !== undefined && manualUsed !== null) {
    return Math.max(0, Number(manualUsed || 0));
  }
  const dispoLimit = Math.max(0, Number(overview.value.dispo_limit || 0));
  if (dispoLimit <= 0) {
    return 0;
  }
  const deficitWithoutDispo = Math.max(0, -projectedBalanceWithoutDispo.value);
  return Math.min(dispoLimit, deficitWithoutDispo);
});

function isValidMonth(value) {
  return typeof value === "string" && /^\d{4}-\d{2}$/.test(value);
}

const dailyMonthLabel = computed(() => {
  if (!isValidMonth(dailyMonth.value)) return currentMonthLabel.value;
  return dailyMonth.value;
});
const dailyExpensesTotal = computed(() => {
  return dailyExpenses.value.reduce((sum, expense) => sum + parseFloat(expense.amount || 0), 0);
});
const dailyExpensesAverage = computed(() => {
  if (!dailyExpenses.value.length) return 0;
  const monthValue = dailyMonthLabel.value;
  const daysInMonth = new Date(monthValue.slice(0, 4), monthValue.slice(5, 7), 0).getDate();
  return dailyExpensesTotal.value / daysInMonth;
});

const filteredEntries = computed(() => {
  if (activeEntryFilter.value === "ALL") {
    return entries.value;
  }
  return entries.value.filter((entry) => entry.entry_type === activeEntryFilter.value);
});

const entryDateFieldDisabled = computed(() =>
  entryForm.value.frequency === "MONTHLY" && entryForm.value.entry_type !== "INCOME"
);

const entryDateFieldLabel = computed(() => {
  if (entryForm.value.entry_type === "INCOME" && entryForm.value.frequency === "MONTHLY") {
    return "Startdatum für regelmäßige Einnahmen";
  }
  return "Datum für einmalig/jährlich/wöchentlich";
});

const plannerIncomeEntries = computed(() =>
  entries.value.filter((entry) => entry.entry_type === "INCOME" && entry.is_active !== false)
);

const plannerExpenseEntries = computed(() =>
  entries.value.filter((entry) => entry.entry_type !== "INCOME" && entry.is_active !== false)
);

function normalizeCategory(value) {
  return String(value || "").trim();
}

function categoryKey(value) {
  return normalizeCategory(value).toLocaleLowerCase("de-DE");
}

function dedupeCategories(values) {
  const seen = new Set();
  const result = [];
  for (const value of values) {
    const normalized = normalizeCategory(value);
    if (!normalized) continue;
    const key = categoryKey(normalized);
    if (seen.has(key)) continue;
    seen.add(key);
    result.push(normalized);
  }
  return result;
}

function loadStoredCategories() {
  if (typeof window === "undefined") return [];
  try {
    const raw = window.localStorage.getItem("finance.categorySuggestions");
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) return [];
    return dedupeCategories(parsed);
  } catch {
    return [];
  }
}

function persistStoredCategories() {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("finance.categorySuggestions", JSON.stringify(localStoredCategories.value));
}

const knownCategoriesFromData = computed(() => {
  const fromEntries = entries.value
    .filter((entry) => entry.entry_type !== "INCOME")
    .map((entry) => entry.category);
  const fromDailyExpenses = dailyExpenses.value.map((expense) => expense.category);
  return dedupeCategories([...fromEntries, ...fromDailyExpenses]);
});

const categorySuggestions = computed(() =>
  dedupeCategories([...knownCategoriesFromData.value, ...localStoredCategories.value]).sort((a, b) =>
    a.localeCompare(b, "de-DE")
  )
);

function maybeStoreCategory(categoryValue) {
  const category = normalizeCategory(categoryValue);
  if (!category) return;
  const exists = categorySuggestions.value.some((item) => categoryKey(item) === categoryKey(category));
  if (exists) return;
  const shouldStore = window.confirm(`Möchtest du "${category}" als Kategorie für spätere Transaktionen speichern?`);
  if (!shouldStore) return;
  localStoredCategories.value = dedupeCategories([...localStoredCategories.value, category]);
  persistStoredCategories();
}

function normalizeText(value) {
  return String(value || "").toLowerCase();
}

function isActiveExpense(entry) {
  if (!entry || entry.entry_type === "INCOME") return false;
  return entry.is_active !== false;
}

function isSubscriptionEntry(entry) {
  const haystack = [entry?.category, entry?.title, entry?.notes].map(normalizeText).join(" ");
  const keywords = ["abo", "abonnement", "subscription", "mitgliedschaft", "mitgliedsbeitrag", "streaming"];
  return keywords.some((keyword) => haystack.includes(keyword));
}

const monthlyPlannedOutflow = computed(() =>
  {
    const monthlyEntryOutflow = entries.value
      .filter((entry) => isActiveExpense(entry) && entry.frequency === "MONTHLY")
      .reduce((sum, entry) => sum + Number(entry.monthly_amount || entry.amount || 0), 0);
    const monthlyDebtFromEntries = entries.value
      .filter((entry) => isActiveExpense(entry) && entry.entry_type === "DEBT")
      .reduce((sum, entry) => sum + Number(entry.monthly_amount || entry.amount || 0), 0);
    const monthlyDebtTotal = Number(overview.value.monthly_debt || 0);
    const debtDelta = Math.max(0, monthlyDebtTotal - monthlyDebtFromEntries);
    return monthlyEntryOutflow + debtDelta;
  }
);

const monthlySubscriptions = computed(() =>
  entries.value
    .filter((entry) => isActiveExpense(entry) && isSubscriptionEntry(entry))
    .reduce((sum, entry) => sum + Number(entry.monthly_amount || entry.amount || 0), 0)
);

const monthlyUnplannedOutflow = computed(() => {
  const totalOutflow = Number(overview.value.monthly_outflow || 0);
  return Math.max(0, totalOutflow - monthlyPlannedOutflow.value);
});

function percentOfMax(value, maxValue) {
  if (!maxValue) return 0;
  const safeValue = Number(value || 0);
  return Math.max(0, Math.min(100, (safeValue / maxValue) * 100));
}

const chartScaleMax = computed(() => {
  const income = Number(overview.value.monthly_income || 0);
  const outflow = Number(overview.value.monthly_outflow || 0);
  return Math.max(income, outflow, 0);
});

const incomeBarHeight = computed(() => percentOfMax(overview.value.monthly_income, chartScaleMax.value));
const expenseBarHeight = computed(() => percentOfMax(overview.value.monthly_outflow, chartScaleMax.value));
const plannerHasMonthData = computed(() => {
  if (typeof overview.value?.has_month_data === "boolean") {
    return overview.value.has_month_data;
  }
  const monthEntryCount = Number(overview.value?.month_entry_count || 0);
  const monthDebtCount = Number(overview.value?.month_debt_count || 0);
  const monthDailyExpenseCount = Number(overview.value?.month_daily_expense_count || 0);
  if (monthEntryCount || monthDebtCount || monthDailyExpenseCount) {
    return true;
  }
  return Number(overview.value?.monthly_income || 0) > 0 || Number(overview.value?.monthly_outflow || 0) > 0;
});
const plannerMonthIsPast = computed(() => plannerMonthLabel.value < currentMonthLabel.value);
const plannerEmptyMessage = computed(() => {
  if (plannerMonthIsPast.value && !plannerHasMonthData.value) {
    return `Für ${plannerMonthLabel.value} liegen keine Datensätze vor.`;
  }
  return `Noch keine Einnahmen oder Ausgaben für ${plannerMonthLabel.value} hinterlegt.`;
});

function toAmount(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function formatCurrency(value) {
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency: currency.value,
    maximumFractionDigits: 2,
  }).format(Number(value || 0));
}

function formatDate(value) {
  if (!value) return "Kein Datum";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" }).format(new Date(value));
}

function progressPercent(current, target) {
  const targetValue = Number(target || 0);
  if (targetValue <= 0) return 0;
  return Math.max(0, Math.min(100, (Number(current || 0) / targetValue) * 100));
}

function dueLabel(entry) {
  if (entry.next_due_date) {
    return `Nächste Fälligkeit: ${formatDate(entry.next_due_date)}`;
  }
  if (entry.frequency === "MONTHLY" && entry.due_day) {
    return `Monatlich am ${entry.due_day}.`;
  }
  if (entry.due_date) {
    return formatDate(entry.due_date);
  }
  return "Ohne Fälligkeit";
}

function dueAmountDirection(item) {
  return item?.entry_type === "INCOME" ? "plus" : "minus";
}

function dueAmountText(item) {
  const direction = dueAmountDirection(item);
  const amount = formatCurrency(Math.abs(Number(item?.monthly_amount || 0)));
  return direction === "plus" ? `+ ${amount}` : `- ${amount}`;
}

function dueAmountClass(item) {
  return dueAmountDirection(item) === "plus" ? "due-plus" : "due-minus";
}

function setError(message) {
  errorMessage.value = message;
  successMessage.value = "";
}

function setSuccess(message) {
  successMessage.value = message;
  errorMessage.value = "";
}

function clearFeedback() {
  errorMessage.value = "";
  successMessage.value = "";
}

function getApiErrorMessage(error, fallbackMessage) {
  const responseData = error?.response?.data;
  if (typeof responseData === "string" && responseData.trim()) {
    return responseData;
  }
  if (responseData?.detail) {
    return responseData.detail;
  }
  if (responseData && typeof responseData === "object") {
    const message = Object.entries(responseData)
      .map(([field, value]) => {
        const parts = Array.isArray(value) ? value : [value];
        return `${field}: ${parts.join(", ")}`;
      })
      .join(" | ");
    if (message) {
      return message;
    }
  }
  return fallbackMessage;
}

function tipTypeLabel(value) {
  return tipTypeLabels[value] || tipTypeLabels.OTHER;
}

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
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
      params: { month: plannerMonthLabel.value },
    });
    project.value = data;
    selectedProjectId.value = data.id;
    const snapshotMonth = data?.overview?.snapshot_month;
    if (isValidMonth(snapshotMonth) && snapshotMonth !== plannerMonth.value) {
      plannerMonth.value = snapshotMonth;
    }
    projectForm.value = buildProjectForm(data);
    membersPanelOpen.value = false;
    showForecastModal.value = false;
    showCompareModal.value = false;
    showProjectSettingsModal.value = false;
    closeEntryModal();
    closeDailyExpenseModal();
    forecast.value = null;
    comparison.value = null;
    clearFeedback();
    if (activeTab.value === "daily") {
      await loadDailyExpenses();
    }
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
    const nextProjectId = projects.value.some((item) => item.id === routeProjectId)
      ? routeProjectId
      : selectedProjectId.value || projects.value[0].id;

    if (!routeProjectId || routeProjectId !== nextProjectId) {
      await router.replace({ name: "finance", params: { projectId: nextProjectId } });
    }
    await loadProjectDetail(nextProjectId);
  } catch {
    // Errors are already surfaced via setError.
  }
}

async function refreshCurrent() {
  await syncProjectSelection();
  if (activeTab.value === "tips") {
    await loadFinanceTips();
  }
}

async function saveProject() {
  if (!selectedProjectId.value) return;
  savingProject.value = true;
  try {
    await api.patch(`finance-projects/${selectedProjectId.value}/`, {
      ...projectForm.value,
      current_balance: toAmount(projectForm.value.current_balance),
      dispo_limit: toAmount(projectForm.value.dispo_limit),
      dispo_used: toAmount(projectForm.value.dispo_used),
      monthly_savings_target: toAmount(projectForm.value.monthly_savings_target),
      emergency_buffer_target: toAmount(projectForm.value.emergency_buffer_target),
    });
    await refreshCurrent();
    setSuccess("Projektbasis gespeichert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Projektbasis konnte nicht gespeichert werden."));
  } finally {
    savingProject.value = false;
  }
}

async function saveProjectFromModal() {
  await saveProject();
  if (!errorMessage.value) {
    showProjectSettingsModal.value = false;
  }
}

async function createMember() {
  if (!selectedProjectId.value) return;
  savingMember.value = true;
  try {
    await api.post("finance-members/", {
      project: selectedProjectId.value,
      name: memberForm.value.name,
      role: memberForm.value.role,
      notes: memberForm.value.notes,
      sort_order: members.value.length,
    });
    memberForm.value = buildMemberForm();
    membersPanelOpen.value = false;
    await refreshCurrent();
    setSuccess("Person hinzugefuegt.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Person konnte nicht hinzugefuegt werden."));
  } finally {
    savingMember.value = false;
  }
}

async function removeMember(member) {
  if (!window.confirm(`Person "${member.name}" wirklich entfernen? Zugeordnete Posten bleiben bestehen, aber ohne Person.`)) {
    return;
  }
  try {
    await api.delete(`finance-members/${member.id}/`);
    await refreshCurrent();
    setSuccess(`Person "${member.name}" entfernt.`);
  } catch (error) {
    setError(getApiErrorMessage(error, "Person konnte nicht entfernt werden."));
  }
}

function openForecastModal() {
  showForecastModal.value = true;
  forecast.value = null;
  forecastMonth.value = plannerMonthLabel.value;
}

function closeForecastModal() {
  showForecastModal.value = false;
}

function openCompareModal() {
  showCompareModal.value = true;
  comparison.value = null;
  compareMonth1.value = plannerMonthLabel.value;
  compareMonth2.value = plannerMonthLabel.value;
}

function closeCompareModal() {
  showCompareModal.value = false;
}

function openCreateEntryModal() {
  resetEntryForm();
  showEntryModal.value = true;
}

function closeEntryModal() {
  showEntryModal.value = false;
  resetEntryForm();
}

function editEntry(entry) {
  editingEntryId.value = entry.id;
  entryForm.value = buildEntryForm(entry);
  showEntryModal.value = true;
}

function resetEntryForm() {
  editingEntryId.value = null;
  entryForm.value = buildEntryForm();
}

async function saveEntry() {
  if (!selectedProjectId.value) return;
  savingEntry.value = true;
  try {
    const wasEditing = Boolean(editingEntryId.value);
    if (entryForm.value.entry_type !== "INCOME") {
      maybeStoreCategory(entryForm.value.category);
    }
    const payload = {
      project: selectedProjectId.value,
      member: entryForm.value.member || null,
      title: entryForm.value.title,
      category: entryForm.value.category,
      entry_type: entryForm.value.entry_type,
      amount: toAmount(entryForm.value.amount),
      frequency: entryForm.value.frequency,
      due_day: entryForm.value.frequency === "MONTHLY" && entryForm.value.due_day ? Number(entryForm.value.due_day) : null,
      due_date: entryForm.value.due_date || null,
      is_shared: entryForm.value.is_shared,
      is_active: entryForm.value.is_active,
      notes: entryForm.value.notes,
    };
    if (editingEntryId.value) {
      await api.patch(`finance-entries/${editingEntryId.value}/`, payload);
    } else {
      await api.post("finance-entries/", payload);
    }
    closeEntryModal();
    await refreshCurrent();
    setSuccess(wasEditing ? "Posten gespeichert." : "Posten angelegt.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Posten konnte nicht gespeichert werden."));
  } finally {
    savingEntry.value = false;
  }
}

async function toggleEntry(entry) {
  try {
    await api.patch(`finance-entries/${entry.id}/`, { is_active: !entry.is_active });
    await refreshCurrent();
    setSuccess(entry.is_active ? "Posten pausiert." : "Posten aktiviert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Postenstatus konnte nicht geändert werden."));
  }
}

async function removeEntry(entry) {
  if (!window.confirm(`Posten "${entry.title}" wirklich löschen?`)) {
    return;
  }
  try {
    await api.delete(`finance-entries/${entry.id}/`);
    if (editingEntryId.value === entry.id) {
      resetEntryForm();
    }
    await refreshCurrent();
    setSuccess(`Posten "${entry.title}" gelöscht.`);
  } catch (error) {
    setError(getApiErrorMessage(error, "Posten konnte nicht gelöscht werden."));
  }
}

// Daily Expense functions
async function loadDailyExpenses() {
  if (!selectedProjectId.value || !isValidMonth(dailyMonth.value)) return;
  try {
    const { data } = await api.get(`daily-expenses/?project=${selectedProjectId.value}&month=${dailyMonth.value}`);
    dailyExpenses.value = Array.isArray(data) ? data : data?.results || [];
  } catch (error) {
    dailyExpenses.value = [];
    setError(getApiErrorMessage(error, "Tägliche Ausgaben konnten nicht geladen werden."));
  }
}

function editDailyExpense(expense) {
  editingDailyExpenseId.value = expense.id;
  dailyExpenseForm.value = buildDailyExpenseForm(expense);
  showDailyExpenseModal.value = true;
}

function resetDailyExpenseForm() {
  editingDailyExpenseId.value = null;
  dailyExpenseForm.value = buildDailyExpenseForm();
}

function openCreateDailyExpenseModal() {
  resetDailyExpenseForm();
  showDailyExpenseModal.value = true;
}

function closeDailyExpenseModal() {
  showDailyExpenseModal.value = false;
  resetDailyExpenseForm();
}

async function saveDailyExpense() {
  if (!selectedProjectId.value) return;
  savingDailyExpense.value = true;
  try {
    const wasEditing = Boolean(editingDailyExpenseId.value);
    maybeStoreCategory(dailyExpenseForm.value.category);
    const payload = {
      project: selectedProjectId.value,
      member: dailyExpenseForm.value.member || null,
      date: dailyExpenseForm.value.date,
      title: dailyExpenseForm.value.title,
      category: dailyExpenseForm.value.category,
      amount: toAmount(dailyExpenseForm.value.amount),
      notes: dailyExpenseForm.value.notes,
    };
    if (editingDailyExpenseId.value) {
      await api.patch(`daily-expenses/${editingDailyExpenseId.value}/`, payload);
    } else {
      await api.post("daily-expenses/", payload);
    }
    closeDailyExpenseModal();
    await loadDailyExpenses();
    await refreshCurrent(); // Update overview
    setSuccess(wasEditing ? "Ausgabe gespeichert." : "Ausgabe hinzugefügt.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Ausgabe konnte nicht gespeichert werden."));
  } finally {
    savingDailyExpense.value = false;
  }
}

async function removeDailyExpense(expense) {
  if (!window.confirm(`Ausgabe "${expense.title}" wirklich löschen?`)) {
    return;
  }
  try {
    await api.delete(`daily-expenses/${expense.id}/`);
    if (editingDailyExpenseId.value === expense.id) {
      resetDailyExpenseForm();
    }
    await loadDailyExpenses();
    await refreshCurrent(); // Update overview
    setSuccess(`Ausgabe "${expense.title}" gelöscht.`);
  } catch (error) {
    setError(getApiErrorMessage(error, "Ausgabe konnte nicht gelöscht werden."));
  }
}

async function loadFinanceTips() {
  loadingFinanceTips.value = true;
  try {
    const { data } = await api.get("finance-tips/");
    financeTips.value = normalizeList(data);
  } catch (error) {
    financeTips.value = [];
    console.error("Tipps konnten nicht geladen werden", error);
  } finally {
    loadingFinanceTips.value = false;
  }
}

watch(
  () => route.params.projectId,
  async (projectId, previousProjectId) => {
    const nextId = Number(projectId || 0);
    if (!nextId || nextId === Number(previousProjectId || 0)) {
      return;
    }
    if (projects.value.length && !projects.value.some((item) => item.id === nextId)) {
      await syncProjectSelection();
      return;
    }
    try {
      await loadProjectDetail(nextId);
    } catch {
      if (projects.value.length) {
        await syncProjectSelection();
      }
    }
  }
);

watch(
  () => plannerMonth.value,
  async (nextMonth, previousMonth) => {
    if (nextMonth === previousMonth || !selectedProjectId.value) {
      return;
    }
    if (!isValidMonth(nextMonth)) {
      return;
    }
    try {
      await loadProjectDetail(selectedProjectId.value);
    } catch {
      // Error state is already handled in loadProjectDetail.
    }
  }
);

watch(
  () => [entryForm.value.frequency, entryForm.value.entry_type],
  ([frequency, entryType]) => {
    if (frequency !== "MONTHLY") {
      entryForm.value.due_day = "";
    }
    if (frequency === "MONTHLY" && entryType !== "INCOME") {
      entryForm.value.due_date = "";
    }
  }
);

watch(
  () => activeTab.value,
  async (newTab) => {
    if (newTab === 'daily' && selectedProjectId.value) {
      await loadDailyExpenses();
      return;
    }
    if (newTab === "tips") {
      await loadFinanceTips();
    }
  }
);

async function calculateForecast() {
  if (!selectedProjectId.value || !forecastMonth.value) return;
  calculatingForecast.value = true;
  try {
    const response = await api.get(`finance-projects/${selectedProjectId.value}/monthly-forecast/?month=${forecastMonth.value}`);
    forecast.value = response.data;
  } catch (error) {
    setError(getApiErrorMessage(error, "Prognose konnte nicht berechnet werden."));
  } finally {
    calculatingForecast.value = false;
  }
}

async function calculateComparison() {
  if (!selectedProjectId.value || !compareMonth1.value || !compareMonth2.value) return;
  calculatingComparison.value = true;
  try {
    const [response1, response2] = await Promise.all([
      api.get(`finance-projects/${selectedProjectId.value}/monthly-forecast/?month=${compareMonth1.value}`),
      api.get(`finance-projects/${selectedProjectId.value}/monthly-forecast/?month=${compareMonth2.value}`)
    ]);
    comparison.value = {
      month1: compareMonth1.value,
      month2: compareMonth2.value,
      forecast1: response1.data,
      forecast2: response2.data
    };
  } catch (error) {
    setError(getApiErrorMessage(error, "Vergleich konnte nicht berechnet werden."));
  } finally {
    calculatingComparison.value = false;
  }
}

watch(
  () => activeTab.value,
  async (newTab) => {
    if (newTab === 'planner' && selectedProjectId.value) {
      forecastMonth.value = plannerMonthLabel.value;
      await calculateForecast();
    }
  }
);

async function exportOverview() {
  if (!selectedProjectId.value) return;
  try {
    const response = await api.get(`finance-projects/${selectedProjectId.value}/export-overview/`, {
      responseType: 'blob',
      params: { month: plannerMonthLabel.value },
    });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `finance_overview_${plannerMonthLabel.value}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    setSuccess("Übersicht exportiert.");
  } catch (error) {
    setError(getApiErrorMessage(error, "Export fehlgeschlagen."));
  }
}

onMounted(async () => {
  await Promise.all([syncProjectSelection(), loadFinanceTips()]);
});
</script>

<style scoped>
.finance-tool {
  display: grid;
  gap: 18px;
}

.feedback-stack {
  display: grid;
  gap: 10px;
}

.feedback-card {
  padding: 14px 16px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--surface);
  font-weight: 500;
}

.feedback-card.error {
  border-color: rgba(239, 68, 68, 0.26);
  background: rgba(239, 68, 68, 0.08);
  color: #b91c1c;
}

.feedback-card.success {
  border-color: rgba(16, 185, 129, 0.26);
  background: rgba(16, 185, 129, 0.1);
  color: #047857;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: end;
}

.hero-copy {
  display: grid;
  gap: 8px;
}

/* Tab Navigation */
.finance-tabs {
  display: flex;
  gap: 8px;
  padding: 0;
  border-bottom: 2px solid var(--border);
  overflow-x: auto;
  margin: 0 0 18px 0;
}

.tab-btn {
  padding: 12px 16px;
  border: none;
  background: none;
  color: var(--muted);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  position: relative;
  white-space: nowrap;
  transition: color 0.2s;
}

.tab-btn:hover {
  color: var(--text);
}

.tab-btn.active {
  color: var(--brand);
}

.tab-btn.active::after {
  content: '';
  position: absolute;
  bottom: -2px;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--brand);
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 12px;
  color: var(--brand);
  font-weight: 700;
}

.hero-controls {
  display: grid;
  gap: 10px;
  min-width: min(340px, 100%);
}

.hero-actions,
.section-head,
.filter-row,
.toggle-row,
.entry-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.section-head {
  justify-content: space-between;
  align-items: flex-start;
}

.section-head.compact {
  margin-bottom: 10px;
}

.summary-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.summary-card {
  display: grid;
  gap: 6px;
}

.summary-card.positive {
  background: linear-gradient(160deg, rgba(16, 185, 129, 0.12), rgba(255, 255, 255, 0.9));
}

.summary-card.warning {
  background: linear-gradient(160deg, rgba(245, 158, 11, 0.12), rgba(255, 255, 255, 0.92));
}

.alert-card.warning {
  background: linear-gradient(160deg, rgba(245, 158, 11, 0.15), rgba(255, 255, 255, 0.95));
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.label {
  color: var(--muted);
  font-size: 13px;
}

.finance-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(320px, 0.9fr);
  gap: 18px;
}

.settings-layout {
  display: grid;
  gap: 18px;
}

.main-column,
.side-column {
  display: grid;
  gap: 18px;
  align-content: start;
}

.grid {
  display: grid;
  gap: 12px;
}

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.project-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.settings-stats {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.full {
  grid-column: 1 / -1;
}

.textarea {
  min-height: 92px;
  resize: vertical;
}

.overview-grid {
  display: grid;
  gap: 18px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.overview-stack {
  display: grid;
  gap: 16px;
}

.mini-stats {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.progress-list {
  display: grid;
  gap: 12px;
}

.progress-block {
  display: grid;
  gap: 8px;
}

.progress-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 14px;
}

.progress-bar {
  position: relative;
  height: 10px;
  border-radius: 999px;
  background: rgba(47, 99, 255, 0.1);
  overflow: hidden;
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
}

.progress-bar.alt {
  background: rgba(16, 185, 129, 0.12);
}

.progress-bar.alt span {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.snapshot {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(47, 99, 255, 0.08);
  color: var(--brand);
  font-weight: 600;
}

.due-list,
.member-list,
.person-totals {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.due-list li,
.member-list li,
.person-totals li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.due-side {
  text-align: right;
  display: grid;
  gap: 4px;
}

.entry-list {
  display: grid;
  gap: 12px;
}

.entry-row {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) auto;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.entry-row.inactive {
  opacity: 0.62;
}

.entry-main {
  display: grid;
  gap: 6px;
}

.entry-title-line {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.type-badge {
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(47, 99, 255, 0.08);
}

.type-badge[data-type="INCOME"] {
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.type-badge[data-type="FIXED"] {
  background: rgba(59, 130, 246, 0.12);
  color: #1d4ed8;
}

.type-badge[data-type="VARIABLE"] {
  background: rgba(245, 158, 11, 0.16);
  color: #b45309;
}

.type-badge[data-type="DEBT"] {
  background: rgba(239, 68, 68, 0.12);
  color: #b91c1c;
}

.type-badge[data-type="SAVING"] {
  background: rgba(139, 92, 246, 0.12);
  color: #6d28d9;
}

.entry-side {
  display: grid;
  gap: 6px;
  justify-items: end;
  text-align: right;
}

.side-card {
  display: grid;
  gap: 12px;
}

.compact-members-card {
  gap: 10px;
}

.member-summary {
  display: grid;
  gap: 8px;
  padding: 12px 14px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.member-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.member-pill {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(47, 99, 255, 0.08);
  border: 1px solid rgba(47, 99, 255, 0.12);
  font-size: 12px;
  font-weight: 600;
}

.member-manager {
  display: grid;
  gap: 12px;
}

.stack-form {
  display: grid;
  gap: 12px;
}

.toggle {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.chip {
  padding: 8px 12px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
}

.chip.active {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(47, 99, 255, 0.08);
}

.small {
  font-size: 13px;
}

.form-hint {
  margin: -2px 0 0;
}

.sm {
  padding: 8px 12px;
  font-size: 14px;
}

.danger {
  color: #b91c1c;
}

.empty-hint {
  margin: 0;
}

:global(.dark) .finance-tool .summary-card {
  background: linear-gradient(160deg, rgba(47, 99, 255, 0.08), rgba(255, 255, 255, 0.02));
}

:global(.dark) .finance-tool .summary-card.positive {
  background: linear-gradient(160deg, rgba(16, 185, 129, 0.1), rgba(255, 255, 255, 0.02));
}

:global(.dark) .finance-tool .summary-card.warning {
  background: linear-gradient(160deg, rgba(245, 158, 11, 0.1), rgba(255, 255, 255, 0.02));
}

:global(.dark) .finance-tool .feedback-card.error {
  color: #fecaca;
  background: rgba(127, 29, 29, 0.4);
  border-color: rgba(248, 113, 113, 0.28);
}

:global(.dark) .finance-tool .feedback-card.success {
  color: #bbf7d0;
  background: rgba(20, 83, 45, 0.42);
  border-color: rgba(74, 222, 128, 0.24);
}

:global(.dark) .finance-tool .surface {
  background-color: rgba(255, 255, 255, 0.02);
}

:global(.dark) .finance-tool .progress-bar {
  background: rgba(47, 99, 255, 0.15);
}

:global(.dark) .finance-tool .progress-bar.alt {
  background: rgba(16, 185, 129, 0.15);
}

/* Debt Section */
.debt-section {
  margin-top: 28px;
}

@media (max-width: 1120px) {
  .summary-grid,
  .overview-grid,
  .project-grid,
  .mini-stats,
  .settings-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .finance-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .hero,
  .entry-row,
  .member-list li,
  .due-list li,
  .person-totals li {
    grid-template-columns: 1fr;
    display: grid;
  }

  .hero {
    align-items: stretch;
  }

  .summary-grid,
  .overview-grid,
  .project-grid,
  .mini-stats,
  .settings-stats,
  .grid.two {
    grid-template-columns: 1fr;
  }

  .entry-side {
    justify-items: start;
    text-align: left;
  }
}

/* Forecast Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 16px;
}

.modal-content {
  background: var(--surface);
  border-radius: 16px;
  max-width: 500px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid var(--border);
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--muted);
}

.modal-body {
  padding: 20px;
  display: grid;
  gap: 16px;
}

.forecast-result {
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.forecast-result h4 {
  margin: 0 0 12px 0;
}

.forecast-grid {
  display: grid;
  gap: 8px;
}

.forecast-grid > div {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.forecast-carryover {
  border-color: rgba(59, 130, 246, 0.35) !important;
  background: rgba(59, 130, 246, 0.07) !important;
}

.forecast-cumulative {
  border-color: rgba(34, 197, 94, 0.4) !important;
  background: rgba(34, 197, 94, 0.08) !important;
  font-weight: 600;
}

.forecast-grid .positive { color: var(--status-ok, #22c55e); }
.forecast-grid .negative { color: var(--status-overdue, #f87171); }

/* Category Breakdown */
.category-breakdown {
  margin-top: 8px;
}

.category-breakdown ul {
  list-style: none;
  padding: 0;
  margin: 4px 0 0 0;
  font-size: 12px;
}

.category-breakdown li {
  margin: 2px 0;
  color: var(--muted);
}

/* Chart */
.chart-container {
  display: flex;
  align-items: end;
  gap: 20px;
  height: 200px;
  padding: 20px;
  background: var(--surface);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.chart-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: end;
  align-items: center;
  padding: 10px;
  border-radius: 8px;
  color: white;
  font-weight: 500;
  text-align: center;
  min-height: 40px;
}

.chart-bar.income {
  background: linear-gradient(135deg, #10b981, #34d399);
}

.chart-bar.expense {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.chart-bar span {
  font-size: 12px;
  margin-bottom: 4px;
}

.chart-bar strong {
  font-size: 14px;
}

/* Comparison Table */
.comparison-result {
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.comparison-result h4 {
  margin: 0 0 12px 0;
}

.comparison-table {
  width: 100%;
  border-collapse: collapse;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border);
}

.comparison-table th,
.comparison-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid var(--border);
}

.comparison-table th {
  background: var(--surface);
  font-weight: 600;
  font-size: 14px;
}

.comparison-table td {
  background: var(--surface);
}

.comparison-table tr:last-child th,
.comparison-table tr:last-child td {
  border-bottom: none;
}

/* Daily Expenses */
.daily-section {
  margin-top: 28px;
}

.daily-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  gap: 16px;
  margin-bottom: 20px;
}

.daily-controls {
  display: flex;
  gap: 12px;
  align-items: end;
}

.daily-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.summary-item {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  text-align: center;
}

.daily-list {
  display: grid;
  gap: 12px;
}

.daily-item {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) auto;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.daily-main {
  display: grid;
  gap: 6px;
}

.daily-title-line {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.category-badge {
  padding: 4px 8px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(139, 92, 246, 0.12);
  color: #6d28d9;
}

.daily-side {
  display: grid;
  gap: 6px;
  justify-items: end;
  text-align: right;
}

.daily-actions {
  display: flex;
  gap: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
}

.tips-panel {
  align-content: start;
}

.tip-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.tip-card {
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px 16px;
  background: var(--surface);
  display: grid;
  gap: 8px;
}

.tip-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.tip-head h3 {
  margin: 0;
}

.tip-body {
  margin: 0;
  white-space: pre-line;
}

@media (max-width: 760px) {
  .daily-header {
    flex-direction: column;
    align-items: stretch;
  }

  .daily-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .daily-item {
    grid-template-columns: 1fr;
  }

  .daily-side {
    justify-items: start;
    text-align: left;
  }

  .tip-head {
    flex-direction: column;
  }
}

/* New Finance Dashboard Design */
.topbar-card {
  display: grid;
  gap: 18px;
  padding: 28px;
  border-radius: 24px;
  background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
  color: white;
}

.topbar-main {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) minmax(260px, 1fr);
  gap: 24px;
  align-items: start;
}

.topbar-meta {
  display: grid;
  gap: 12px;
}

.topbar-meta h1 {
  margin: 0;
  font-size: clamp(2rem, 2.5vw, 2.8rem);
}

.topbar-meta .muted {
  color: rgba(255, 255, 255, 0.78);
  max-width: 720px;
}

.topbar-actions {
  display: grid;
  gap: 16px;
  justify-items: end;
}

.topbar-buttons {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 12px;
}

.topbar-insights {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 14px;
}

.topbar-insight {
  display: grid;
  gap: 10px;
  padding: 14px;
  border-radius: 16px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: rgba(15, 23, 42, 0.24);
}

.topbar-insight-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.topbar-insight-head h2 {
  margin: 0;
  font-size: 16px;
}

.topbar-due-list strong {
  color: #f8fafc;
}

.topbar-due-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 8px;
}

.topbar-due-list li {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  background: rgba(15, 23, 42, 0.38);
}

.feedback-bar {
  display: grid;
  gap: 12px;
  margin-top: 18px;
}

.feedback-pill {
  padding: 16px 18px;
  border-radius: 18px;
  font-weight: 600;
}

.feedback-pill.error {
  background: rgba(248, 113, 113, 0.16);
  color: #7f1d1d;
}

.feedback-pill.success {
  background: rgba(20, 184, 166, 0.16);
  color: #0f766e;
}

.summary-band {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 18px;
  margin-top: 20px;
}

.metric-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 24px;
  display: grid;
  gap: 14px;
  min-height: 150px;
}

.balance-card {
  background: linear-gradient(135deg, #0f766e, #10b981);
  color: #f8fafc;
  border: none;
  box-shadow: 0 28px 74px rgba(15, 118, 110, 0.18);
}

.balance-card .metric-label {
  color: rgba(236, 253, 245, 0.9);
}

.balance-card .metric-note {
  color: rgba(236, 253, 245, 0.92);
}

.balance-card .metric-breakdown-row {
  color: rgba(236, 253, 245, 0.9);
}

.balance-card .metric-breakdown-row strong {
  color: #ffffff;
}

.balance-card .metric-pill {
  background: rgba(255, 255, 255, 0.2);
  color: #f8fafc;
  border: 1px solid rgba(255, 255, 255, 0.32);
}

.metric-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.metric-label {
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 12px;
  color: var(--muted);
}

.metric-note {
  font-size: 14px;
  line-height: 1.6;
  color: var(--muted);
}

.metric-breakdown {
  display: grid;
  gap: 6px;
}

.metric-breakdown-row {
  margin: 0;
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 10px;
  font-size: 13px;
  color: var(--muted);
}

.metric-breakdown-row strong {
  color: var(--text);
  font-size: 14px;
}

.metric-progress {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.metric-pill {
  padding: 7px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 12px;
  line-height: 1;
}

.metric-pill.small {
  opacity: 0.84;
}

.due-metric-card {
  align-content: start;
}

.due-metric-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.due-metric-item {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 14px;
}

.due-plus {
  color: #047857;
}

.due-minus {
  color: #b91c1c;
}

.tab-panel {
  margin-top: 28px;
}

.tab-nav {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 8px;
}

.tab-pill {
  border: none;
  background: none;
  padding: 12px 20px;
  border-radius: 999px;
  color: var(--muted);
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s ease;
}

.tab-pill.active {
  background: var(--brand);
  color: white;
  box-shadow: 0 12px 32px rgba(59, 130, 246, 0.12);
}

.workspace-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 22px;
  margin-top: 22px;
}

.workspace-main {
  display: grid;
  align-content: start;
  gap: 22px;
}

.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 24px;
  padding: 22px;
  display: grid;
  gap: 18px;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.panel-head h2 {
  margin: 0;
}

.badge {
  padding: 8px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(59, 130, 246, 0.14);
  color: var(--brand);
}

.badge.badge-soft {
  background: rgba(59, 130, 246, 0.08);
  color: var(--text);
  border: 1px solid rgba(59, 130, 246, 0.2);
  font-weight: 600;
}

.settings-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.setting-note {
  margin: 6px 0 0;
}

.info-row,
.status-grid {
  display: grid;
  gap: 14px;
}

.info-row {
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
}

.status-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}

.info-row > div,
.status-grid > div {
  background: linear-gradient(160deg, rgba(59, 130, 246, 0.08), rgba(59, 130, 246, 0.03));
  border: 1px solid rgba(59, 130, 246, 0.16);
  padding: 16px;
  border-radius: 18px;
}

.compact-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.compact-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.empty-text {
  color: var(--muted);
}

.performance-cards {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.performance-item {
  border-radius: 20px;
  padding: 20px;
  display: grid;
  gap: 12px;
  min-height: 104px;
  color: white;
}

.performance-item span {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  opacity: 0.92;
}

.performance-item strong {
  font-size: 1.5rem;
}

.performance-item.income {
  background: linear-gradient(135deg, #059669, #10b981);
}

.performance-item.outcome {
  background: linear-gradient(135deg, #c2410c, #f97316);
}

.performance-item.balance {
  background: linear-gradient(135deg, #1d4ed8, #3b82f6);
}

.entries-panel .panel-head {
  flex-direction: column;
  align-items: stretch;
}

.panel-head-space {
  gap: 16px;
}

.filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.planner-head {
  align-items: flex-end;
}

.planner-head-controls {
  display: flex;
  align-items: flex-end;
  justify-content: flex-end;
  gap: 12px;
  flex-wrap: wrap;
}

.planner-month-control {
  display: grid;
  gap: 6px;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--muted);
}

.planner-month-control .input {
  min-width: 170px;
}

.planner-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 20px;
}

.summary-split-panel {
  align-content: start;
}

.summary-split-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.summary-column {
  display: grid;
  gap: 10px;
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 14px;
  background: var(--surface);
}

.summary-column h3 {
  margin: 0;
  font-size: 1rem;
}

.summary-sublist {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}

.summary-subitem {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  font-size: 14px;
}

.settings-panel,
.status-panel {
  align-content: start;
}

.settings-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(340px, 1fr));
  gap: 20px;
  margin-top: 22px;
  align-items: start;
}

.settings-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.settings-grid label.full {
  grid-column: span 2;
}

.member-panel {
  margin-top: 22px;
}

.top-categories-panel {
  margin-top: 22px;
}

.member-summary {
  display: grid;
  gap: 12px;
  padding: 0;
  border: none;
  background: transparent;
}

.daily-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 18px;
  margin-bottom: 22px;
}

.daily-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: flex-end;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 20px;
  height: 210px;
  padding: 20px;
  background: var(--surface);
  border-radius: 20px;
  border: 1px solid var(--border);
  overflow: hidden;
}

.chart-empty-state {
  min-height: 210px;
  border-radius: 20px;
  border: 1px dashed var(--border);
  background: rgba(59, 130, 246, 0.04);
  display: grid;
  place-items: center;
  text-align: center;
  padding: 20px;
}

.chart-empty-state p {
  margin: 0;
  max-width: 48ch;
}

.chart-bar {
  flex: 1;
  display: grid;
  gap: 8px;
  justify-items: center;
  align-items: end;
  padding: 16px;
  border-radius: 18px;
  color: white;
  text-align: center;
  box-sizing: border-box;
  height: clamp(68px, var(--bar-height), 100%);
  overflow: hidden;
}

.chart-bar.income {
  background: linear-gradient(135deg, #22c55e, #4ade80);
}

.chart-bar.expense {
  background: linear-gradient(135deg, #f59e0b, #fbbf24);
}

.chart-bar span {
  font-size: 12px;
}

.chart-bar strong {
  font-size: 1rem;
}

.debt-summary-panel {
  grid-column: 1 / -1;
}

@media (max-width: 1200px) {
  .planner-grid,
  .settings-row {
    grid-template-columns: 1fr;
  }

  .topbar-main,
  .topbar-insights {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .summary-split-grid {
    grid-template-columns: 1fr;
  }

  .summary-band {
    grid-template-columns: 1fr;
  }

  .topbar-actions {
    justify-items: start;
  }

  .topbar-buttons {
    justify-content: flex-start;
  }

  .daily-header,
  .daily-controls {
    flex-direction: column;
    align-items: stretch;
  }

  .panel-head {
    flex-direction: column;
    align-items: stretch;
  }

  .planner-head-controls {
    width: 100%;
    justify-content: flex-start;
  }

  .planner-month-control .input {
    width: 100%;
    min-width: 0;
  }

  .settings-meta {
    justify-content: flex-start;
  }
}
</style>



