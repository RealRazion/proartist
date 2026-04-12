<template>
  <div class="finance-entry">
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">Finance</p>
        <h1>Ein Finanzprojekt statt zehn Einzelseiten.</h1>
        <p class="muted lead">
          Lege euer Haushalts- oder Finanzprojekt an, trage Personen ein und arbeite danach in einer klaren Monatsübersicht
          mit Einnahmen, Fixkosten, Schulden, Sparen und den nächsten Fälligkeiten.
        </p>
        <div class="hero-points">
          <span>Ein Konto für mehrere Personen</span>
          <span>Monatsbild statt zerstreuter Tabs</span>
          <span>Schnell genug für den Alltag</span>
        </div>
      </div>

      <form class="create-panel" @submit.prevent="createProject">
        <div class="panel-head">
          <h2>Finanzprojekt anlegen</h2>
          <button class="btn ghost" type="button" @click="goBack">Zur Plattformübersicht</button>
        </div>

        <label>
          Titel
          <input v-model.trim="form.title" class="input" placeholder="z. B. Haushalt Samir & Aylin" required />
        </label>

        <label>
          Kurze Notiz
          <textarea
            v-model.trim="form.description"
            class="input textarea"
            rows="3"
            placeholder="Wofür nutzt ihr das Projekt?"
          ></textarea>
        </label>

        <div class="grid two">
          <label>
            Währung
            <select v-model="form.currency" class="input">
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="CHF">CHF</option>
            </select>
          </label>
          <label>
            Startguthaben
            <input v-model="form.current_balance" class="input" type="number" step="0.01" min="0" placeholder="0.00" />
          </label>
        </div>

        <div class="grid two">
          <label>
            Sparziel pro Monat
            <input
              v-model="form.monthly_savings_target"
              class="input"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
          </label>
          <label>
            Notgroschen-Ziel
            <input
              v-model="form.emergency_buffer_target"
              class="input"
              type="number"
              step="0.01"
              min="0"
              placeholder="0.00"
            />
          </label>
        </div>

        <label>
          Personen im Projekt
          <textarea
            v-model.trim="form.members"
            class="input textarea"
            rows="3"
            placeholder="z. B. Samir, Aylin"
          ></textarea>
          <small class="muted hint">Kommagetrennt oder Zeile für Zeile. So könnt ihr direkt 2 Personen unter einem Account führen.</small>
        </label>

        <button class="btn" type="submit" :disabled="saving">
          {{ saving ? "Lege an..." : "Projekt erstellen" }}
        </button>
      </form>
    </section>

    <section v-if="errorMessage || successMessage" class="feedback-stack">
      <div v-if="errorMessage" class="feedback-card error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="feedback-card success">{{ successMessage }}</div>
    </section>

    <section v-if="projects.length" class="card projects-card">
      <div class="section-head">
        <div>
          <h2>Bestehende Finanzprojekte</h2>
          <p class="muted">Öffne direkt das passende Monatsbild.</p>
        </div>
        <button class="btn ghost" type="button" @click="loadProjects" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>

      <div class="project-grid">
        <article v-for="project in projects" :key="project.id" class="project-card">
          <div class="project-top">
            <div>
              <h3>{{ project.title }}</h3>
              <p class="muted small">{{ project.members?.map((member) => member.name).join(", ") || "Ohne Personen" }}</p>
            </div>
            <button class="btn ghost sm" type="button" @click="openProject(project.id)">Öffnen</button>
          </div>

          <div class="stats-grid">
            <div>
              <span class="label">Frei pro Monat</span>
              <strong>{{ formatCurrency(project.overview?.monthly_left, project.currency) }}</strong>
            </div>
            <div>
              <span class="label">Einnahmen</span>
              <strong>{{ formatCurrency(project.overview?.monthly_income, project.currency) }}</strong>
            </div>
            <div>
              <span class="label">Ausgänge</span>
              <strong>{{ formatCurrency(project.overview?.monthly_outflow, project.currency) }}</strong>
            </div>
            <div>
              <span class="label">Faellig bald</span>
              <strong>{{ project.overview?.due_soon?.length || 0 }}</strong>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();

const loading = ref(false);
const saving = ref(false);
const projects = ref([]);
const errorMessage = ref("");
const successMessage = ref("");
const form = ref({
  title: "",
  description: "",
  currency: "EUR",
  current_balance: "",
  monthly_savings_target: "",
  emergency_buffer_target: "",
  members: "Ich",
});

function toAmount(value) {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function parseMembers(value) {
  return [...new Set((value || "").split(/[\n,;]+/).map((item) => item.trim()).filter(Boolean))];
}

function formatCurrency(value, currency = "EUR") {
  const amount = Number(value || 0);
  return new Intl.NumberFormat("de-DE", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(amount);
}

function setError(message) {
  errorMessage.value = message;
  successMessage.value = "";
}

function setSuccess(message) {
  successMessage.value = message;
  errorMessage.value = "";
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
      .map(([field, value]) => `${field}: ${Array.isArray(value) ? value.join(", ") : value}`)
      .join(" | ");
    if (message) {
      return message;
    }
  }
  return fallbackMessage;
}

async function loadProjects() {
  loading.value = true;
  try {
    const { data } = await api.get("finance-projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (error) {
    projects.value = [];
    setError(getApiErrorMessage(error, "Finanzprojekte konnten nicht geladen werden."));
  } finally {
    loading.value = false;
  }
}

async function createProject() {
  saving.value = true;
  try {
    const payload = {
      title: form.value.title,
      description: form.value.description,
      currency: form.value.currency,
      current_balance: toAmount(form.value.current_balance),
      monthly_savings_target: toAmount(form.value.monthly_savings_target),
      emergency_buffer_target: toAmount(form.value.emergency_buffer_target),
      initial_members: parseMembers(form.value.members),
    };
    const { data } = await api.post("finance-projects/", payload);
    await loadProjects();
    setSuccess("Finanzprojekt erstellt.");
    router.push({ name: "finance", params: { projectId: data.id } });
  } catch (error) {
    setError(getApiErrorMessage(error, "Finanzprojekt konnte nicht erstellt werden."));
  } finally {
    saving.value = false;
  }
}

function openProject(projectId) {
  router.push({ name: "finance", params: { projectId } });
}

function goBack() {
  router.push({ name: "platforms" });
}

onMounted(loadProjects);
</script>

<style scoped>
.finance-entry {
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
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(320px, 0.95fr);
  gap: 18px;
  padding: 22px;
  background:
    radial-gradient(circle at top right, rgba(47, 99, 255, 0.16), transparent 42%),
    linear-gradient(145deg, var(--card), var(--bg-soft));
}

.hero-copy {
  display: grid;
  gap: 14px;
  align-content: start;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--brand);
  font-weight: 700;
}

.lead {
  max-width: 62ch;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-points span {
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(47, 99, 255, 0.08);
  border: 1px solid rgba(47, 99, 255, 0.12);
  font-size: 14px;
  font-weight: 600;
}

.create-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background: var(--card);
  border: 1px solid var(--border);
}

.panel-head,
.section-head,
.project-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.grid {
  display: grid;
  gap: 12px;
}

.grid.two {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.textarea {
  min-height: 96px;
  resize: vertical;
}

.hint,
.small {
  font-size: 13px;
}

.projects-card {
  display: grid;
  gap: 16px;
}

.project-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.project-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 18px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.stats-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.label {
  display: block;
  margin-bottom: 4px;
  color: var(--muted);
  font-size: 13px;
}

.sm {
  padding: 8px 12px;
  font-size: 14px;
}

:global(.dark) .finance-entry .feedback-card.error {
  color: #fecaca;
  background: rgba(127, 29, 29, 0.4);
  border-color: rgba(248, 113, 113, 0.28);
}

:global(.dark) .finance-entry .feedback-card.success {
  color: #bbf7d0;
  background: rgba(20, 83, 45, 0.42);
  border-color: rgba(74, 222, 128, 0.24);
}

@media (max-width: 920px) {
  .hero {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .grid.two,
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .panel-head,
  .section-head,
  .project-top {
    flex-direction: column;
  }
}

:global(.dark) .finance-entry .hero {
  background:
    radial-gradient(circle at top right, rgba(47, 99, 255, 0.2), transparent 42%),
    linear-gradient(145deg, rgba(13, 25, 53, 0.96), rgba(10, 20, 45, 0.94));
}
</style>
