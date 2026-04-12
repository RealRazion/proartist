<template>
  <div class="finance-tool">
    <section v-if="loading && !project" class="card loading-card">
      <h1>Finanzplaner</h1>
      <p class="muted">Lade Finanzprojekt...</p>
    </section>

    <section v-else-if="!projects.length" class="card empty-card">
      <h1>Kein Finanzprojekt vorhanden</h1>
      <p class="muted">Lege zuerst ein Finanzprojekt an. Danach bekommst du eine gemeinsame Monatsübersicht für alle Personen und Posten.</p>
      <button class="btn" type="button" @click="router.push({ name: 'platform-finance' })">Zum Einstieg</button>
    </section>

    <template v-else>
      <header class="card hero">
        <div class="hero-copy">
          <p class="eyebrow">Finanzplaner</p>
          <h1>{{ project?.title || "Finanzprojekt" }}</h1>
          <p class="muted">
            Ein Monatsbild für Guthaben, Einnahmen, Ausgänge, Sparziele und die nächsten Fälligkeiten.
          </p>
        </div>

        <div class="hero-controls">
          <label>
            Projekt
            <select class="input" :value="selectedProjectId || ''" @change="handleProjectChange">
              <option v-for="item in projects" :key="item.id" :value="item.id">{{ item.title }}</option>
            </select>
          </label>
          <div class="hero-actions">
            <button class="btn ghost" type="button" @click="router.push({ name: 'platform-finance' })">Neues Projekt</button>
            <button class="btn ghost" type="button" @click="refreshCurrent" :disabled="loading">Aktualisieren</button>
          </div>
        </div>
      </header>

      <!-- Tab Navigation -->
      <div class="finance-tabs">
        <button
          v-for="tab in tabs"
          :key="tab"
          class="tab-btn"
          :class="{ active: activeTab === tab }"
          @click="activeTab = tab"
        >
          {{ tabLabels[tab] }}
        </button>
      </div>

      <section v-if="errorMessage || successMessage" class="feedback-stack">
        <div v-if="errorMessage" class="feedback-card error">{{ errorMessage }}</div>
        <div v-if="successMessage" class="feedback-card success">{{ successMessage }}</div>
      </section>

      <!-- Übersicht Tab -->
      <section v-show="activeTab === 'overview'" class="summary-grid">
          <article class="card summary-card positive">
            <span class="label">Frei pro Monat</span>
            <strong>{{ formatCurrency(overview.monthly_left) }}</strong>
            <small class="muted">Einnahmen minus alle geplanten Ausgänge</small>
          </article>
          <article class="card summary-card">
            <span class="label">Einnahmen</span>
            <strong>{{ formatCurrency(overview.monthly_income) }}</strong>
            <small class="muted">Fixe und wiederkehrende Einnahmen</small>
          </article>
          <article class="card summary-card">
            <span class="label">Geplante Ausgänge</span>
            <strong>{{ formatCurrency(overview.monthly_outflow) }}</strong>
            <small class="muted">Fixkosten, variabel, Schulden und Sparen</small>
          </article>
          <article class="card summary-card" :class="{ warning: Number(overview.buffer_gap || 0) > 0 }">
            <span class="label">Voraussichtlicher Stand</span>
            <strong>{{ formatCurrency(overview.projected_balance) }}</strong>
            <small class="muted">
              Notgroschen-Lücke: {{ formatCurrency(overview.buffer_gap) }}
            </small>
          </article>
        </section>

        <section v-show="activeTab === 'entries'" class="finance-layout">
          <div class="main-column">
            <article class="card project-settings">
              <div class="section-head">
                <div>
                  <h2>Projektbasis</h2>
                  <p class="muted">Die paar Werte, die dein Monatsbild steuern.</p>
                </div>
                <button class="btn" type="button" @click="saveProject" :disabled="savingProject">
                  {{ savingProject ? "Speichere..." : "Basis speichern" }}
                </button>
              </div>

              <div class="grid project-grid">
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
          </article>

          <article class="card overview-card">
            <div class="section-head">
              <div>
                <h2>Monatsbild</h2>
                <p class="muted">Alles Relevante für diesen Monat in einer Übersicht.</p>
              </div>
              <span class="snapshot">{{ overview.snapshot_month || currentMonthLabel }}</span>
            </div>

            <div class="overview-grid">
              <div class="overview-stack">
                <div class="mini-stats">
                  <div>
                    <span class="label">Fixkosten</span>
                    <strong>{{ formatCurrency(overview.monthly_fixed_costs) }}</strong>
                  </div>
                  <div>
                    <span class="label">Variable Ausgaben</span>
                    <strong>{{ formatCurrency(overview.monthly_variable_costs) }}</strong>
                  </div>
                  <div>
                    <span class="label">Schulden</span>
                    <strong>{{ formatCurrency(overview.monthly_debt) }}</strong>
                  </div>
                  <div>
                    <span class="label">Sparen</span>
                    <strong>{{ formatCurrency(overview.monthly_savings) }}</strong>
                  </div>
                </div>

                <div class="progress-list">
                  <div class="progress-block">
                    <div class="progress-head">
                      <span>Sparziel</span>
                      <strong>{{ formatCurrency(overview.monthly_savings) }} / {{ formatCurrency(project?.monthly_savings_target) }}</strong>
                    </div>
                    <div class="progress-bar">
                      <span :style="{ width: `${progressPercent(overview.monthly_savings, project?.monthly_savings_target)}%` }"></span>
                    </div>
                  </div>

                  <div class="progress-block">
                    <div class="progress-head">
                      <span>Notgroschen</span>
                      <strong>{{ formatCurrency(project?.current_balance) }} / {{ formatCurrency(project?.emergency_buffer_target) }}</strong>
                    </div>
                    <div class="progress-bar alt">
                      <span :style="{ width: `${progressPercent(project?.current_balance, project?.emergency_buffer_target)}%` }"></span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="overview-stack">
                <h3>Demnächst fällig</h3>
                <ul v-if="overview.due_soon?.length" class="due-list">
                  <li v-for="item in overview.due_soon" :key="item.id">
                    <div>
                      <strong>{{ item.title }}</strong>
                      <p class="muted small">
                        {{ entryTypeLabels[item.entry_type] || item.entry_type }} · {{ item.member_name || "Nicht zugeordnet" }}
                      </p>
                    </div>
                    <div class="due-side">
                      <strong>{{ formatCurrency(item.amount) }}</strong>
                      <span class="muted small">{{ formatDate(item.due_date) }}</span>
                    </div>
                  </li>
                </ul>
                <p v-else class="muted empty-hint">Für die nächsten 14 Tage ist nichts geplant.</p>

                <h3>Personenbild</h3>
                <ul class="person-totals" v-if="overview.member_totals?.length">
                  <li v-for="row in overview.member_totals" :key="row.member_id ?? row.member_name">
                    <span>{{ row.member_name }}</span>
                    <span>{{ formatCurrency(row.net) }}</span>
                  </li>
                </ul>
              </div>
            </div>
          </article>

          <article class="card entries-card">
            <div class="section-head">
              <div>
                <h2>Posten</h2>
                <p class="muted">Alle Bausteine, aus denen sich dein Monat zusammensetzt.</p>
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
                    <button class="btn ghost sm" type="button" @click="toggleEntry(entry)">
                      {{ entry.is_active ? "Pausieren" : "Aktivieren" }}
                    </button>
                    <button class="btn ghost sm danger" type="button" @click="removeEntry(entry)">Löschen</button>
                  </div>
                </div>
              </article>
            </div>
            <p v-else class="muted empty-hint">Noch keine Posten im aktuellen Filter.</p>
          </article>
        </div>

        <aside class="side-column">
          <article class="card side-card">
            <div class="section-head compact">
              <div>
                <h2>{{ editingEntryId ? "Posten bearbeiten" : "Neuer Posten" }}</h2>
                <p class="muted">Einfach halten: Titel, Betrag, Rhythmus, Person.</p>
              </div>
              <button v-if="editingEntryId" class="btn ghost sm" type="button" @click="resetEntryForm">Neu</button>
            </div>

            <form class="stack-form" @submit.prevent="saveEntry">
              <label>
                Titel
                <input v-model.trim="entryForm.title" class="input" placeholder="z. B. Miete" required />
              </label>
              <div class="grid two">
                <label>
                  Typ
                  <select v-model="entryForm.entry_type" class="input">
                    <option v-for="(label, key) in entryTypeLabels" :key="key" :value="key">{{ label }}</option>
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
                  <input v-model.trim="entryForm.category" class="input" placeholder="z. B. Wohnen" />
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
                Datum für einmalig/jährlich/wöchentlich
                <input v-model="entryForm.due_date" class="input" type="date" />
              </label>

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

              <button class="btn" type="submit" :disabled="savingEntry">
                {{ savingEntry ? "Speichere..." : editingEntryId ? "Posten speichern" : "Posten anlegen" }}
              </button>
            </form>
          </article>

          <article class="card side-card compact-members-card">
            <div class="section-head compact">
              <div>
                <h2>Personen</h2>
                <p class="muted">Nur bei Bedarf aufklappen.</p>
              </div>
              <button class="btn ghost sm" type="button" @click="membersPanelOpen = !membersPanelOpen">
                {{ membersPanelOpen ? "Schließen" : members.length ? "Verwalten" : "Anlegen" }}
              </button>
            </div>

            <div class="member-summary">
              <strong>{{ members.length }} {{ members.length === 1 ? "Person" : "Personen" }}</strong>
              <p class="muted small">
                {{ members.length ? "Im Projekt hinterlegt." : "Noch keine Personen angelegt." }}
              </p>

              <div v-if="memberPreview.length" class="member-preview">
                <span v-for="member in memberPreview" :key="member.id" class="member-pill">
                  {{ member.name }}
                </span>
                <span v-if="members.length > memberPreview.length" class="member-pill muted">
                  +{{ members.length - memberPreview.length }}
                </span>
              </div>
            </div>

            <div v-if="membersPanelOpen" class="member-manager">
              <ul v-if="members.length" class="member-list">
                <li v-for="member in members" :key="member.id">
                  <div>
                    <strong>{{ member.name }}</strong>
                    <p class="muted small">{{ memberRoleLabels[member.role] || member.role }}</p>
                  </div>
                  <button class="btn ghost sm danger" type="button" @click="removeMember(member)">Entfernen</button>
                </li>
              </ul>
              <p v-else class="muted empty-hint">Noch keine Personen angelegt.</p>

              <form class="stack-form" @submit.prevent="createMember">
                <label>
                  Name
                  <input v-model.trim="memberForm.name" class="input" placeholder="z. B. Samir" required />
                </label>
                <label>
                  Rolle
                  <select v-model="memberForm.role" class="input">
                    <option v-for="(label, key) in memberRoleLabels" :key="key" :value="key">{{ label }}</option>
                  </select>
                </label>
                <label>
                  Notiz
                  <textarea v-model.trim="memberForm.notes" class="input textarea" rows="2" placeholder="optional"></textarea>
                </label>
                <button class="btn" type="submit" :disabled="savingMember">
                  {{ savingMember ? "Speichere..." : "Person hinzufügen" }}
                </button>
              </form>
            </div>
          </article>
        </aside>
      </section>

      <section v-show="activeTab === 'settings'" class="settings-layout">
        <article class="card project-settings">
          <div class="section-head">
            <div>
              <h2>Projektbasis</h2>
              <p class="muted">Die Werte, die dein Monatsbild steuern.</p>
            </div>
            <button class="btn" type="button" @click="saveProject" :disabled="savingProject">
              {{ savingProject ? "Speichere..." : "Basis speichern" }}
            </button>
          </div>

          <div class="grid project-grid">
            <label>
              Titel
              <input v-model.trim="projectForm.title" class="input" />
            </label>
            <label>
              Waehrung
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
        </article>

        <article class="card settings-info-card">
          <div class="section-head compact">
            <div>
              <h2>Projektstatus</h2>
              <p class="muted">Wichtige Werte auf einen Blick.</p>
            </div>
          </div>

          <div class="settings-stats">
            <div>
              <span class="label">Personen</span>
              <strong>{{ members.length }}</strong>
            </div>
            <div>
              <span class="label">Posten aktiv</span>
              <strong>{{ overview.active_entry_count || 0 }}</strong>
            </div>
            <div>
              <span class="label">Faellig bald</span>
              <strong>{{ overview.due_soon?.length || 0 }}</strong>
            </div>
            <div>
              <span class="label">Waehrung</span>
              <strong>{{ currency }}</strong>
            </div>
          </div>
        </article>
      </section>

      <!-- Debt Tracker Section -->
      <section v-show="activeTab === 'debts' && selectedProjectId" class="debt-section">
        <DebtTracker :projectId="selectedProjectId" />
      </section>
    </template>
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
const activeTab = ref("overview");
const editingEntryId = ref(null);
const membersPanelOpen = ref(false);
const errorMessage = ref("");
const successMessage = ref("");

const tabs = ["overview", "entries", "debts", "settings"];
const tabLabels = {
  overview: "📊 Übersicht",
  entries: "📝 Posten verwalten",
  debts: "💳 Schulden",
  settings: "⚙️ Einstellungen",
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

function buildProjectForm(data = {}) {
  return {
    title: data.title || "",
    description: data.description || "",
    currency: data.currency || "EUR",
    current_balance: data.current_balance ?? 0,
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

const overview = computed(() => project.value?.overview || {});
const members = computed(() => project.value?.members || []);
const entries = computed(() => project.value?.entries || []);
const currency = computed(() => project.value?.currency || "EUR");
const currentMonthLabel = computed(() => new Date().toISOString().slice(0, 7));
const memberPreview = computed(() => members.value.slice(0, 4));

const filteredEntries = computed(() => {
  if (activeEntryFilter.value === "ALL") {
    return entries.value;
  }
  return entries.value.filter((entry) => entry.entry_type === activeEntryFilter.value);
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
    const { data } = await api.get(`finance-projects/${projectId}/`);
    project.value = data;
    selectedProjectId.value = data.id;
    projectForm.value = buildProjectForm(data);
    membersPanelOpen.value = false;
    clearFeedback();
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
}

async function saveProject() {
  if (!selectedProjectId.value) return;
  savingProject.value = true;
  try {
    await api.patch(`finance-projects/${selectedProjectId.value}/`, {
      ...projectForm.value,
      current_balance: toAmount(projectForm.value.current_balance),
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

function editEntry(entry) {
  editingEntryId.value = entry.id;
  entryForm.value = buildEntryForm(entry);
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
    resetEntryForm();
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
    setError(getApiErrorMessage(error, "Postenstatus konnte nicht geaendert werden."));
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
    setSuccess(`Posten "${entry.title}" geloescht.`);
  } catch (error) {
    setError(getApiErrorMessage(error, "Posten konnte nicht geloescht werden."));
  }
}

async function handleProjectChange(event) {
  const nextId = Number(event.target.value);
  if (!nextId) return;
  await router.push({ name: "finance", params: { projectId: nextId } });
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
  () => entryForm.value.frequency,
  (frequency) => {
    if (frequency !== "MONTHLY") {
      entryForm.value.due_day = "";
    }
    if (frequency === "MONTHLY") {
      entryForm.value.due_date = "";
    }
  }
);

onMounted(syncProjectSelection);
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

/* Dark Mode and Accessibility Fixes */
.input,
.textarea,
select {
  background-color: var(--input-bg);
  color: var(--text);
  border-color: var(--border);
}

.input:focus,
.textarea:focus,
select:focus {
  background-color: var(--input-bg-focus);
  color: var(--text);
  border-color: var(--brand);
  box-shadow: 0 0 0 2px rgba(47, 99, 255, 0.1);
}

/* Dark mode explicit color support */
:global(.dark) .finance-tool .input,
:global(.dark) .finance-tool .textarea,
:global(.dark) .finance-tool select {
  background-color: rgba(255, 255, 255, 0.05);
  color: #fff;
}

:global(.dark) .finance-tool .input::placeholder,
:global(.dark) .finance-tool .textarea::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

:global(.dark) .finance-tool .input:focus,
:global(.dark) .finance-tool .textarea:focus,
:global(.dark) .finance-tool select:focus {
  background-color: rgba(255, 255, 255, 0.08);
}

:global(.dark) .finance-tool .card {
  background-color: rgba(255, 255, 255, 0.04);
  border-color: rgba(255, 255, 255, 0.1);
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
</style>
