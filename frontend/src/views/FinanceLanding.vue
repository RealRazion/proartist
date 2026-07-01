<template>
  <div class="finance-landing">
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">Finance</p>
        <h1>Finanzplaner</h1>
        <p class="muted lead">
          Behalte den Überblick über deine Einnahmen, Schulden und Abos –
          alles an einem Ort, klar und einfach.
        </p>
        <div class="hero-points">
          <span>Einnahmen im Blick</span>
          <span>Schulden im Griff</span>
          <span>Abos auf einen Blick</span>
        </div>
      </div>

      <div class="action-panel">
        <div class="panel-head">
          <h2>Projekte</h2>
          <button class="btn ghost sm" type="button" @click="goBack">← Zurück</button>
        </div>
        <p class="muted">Öffne ein bestehendes Projekt oder starte ein neues.</p>
        <button class="btn" type="button" @click="showCreateModal = true">Neues Projekt erstellen</button>
      </div>
    </section>

    <!-- Feedback -->
    <section v-if="errorMessage || successMessage" class="feedback-bar">
      <div v-if="errorMessage" class="feedback-pill error">{{ errorMessage }}</div>
      <div v-if="successMessage" class="feedback-pill success">{{ successMessage }}</div>
    </section>

    <!-- Project list -->
    <section v-if="projects.length" class="card projects-section">
      <div class="section-head">
        <h2>Deine Projekte</h2>
        <button class="btn ghost sm" type="button" @click="loadProjects" :disabled="loading">
          {{ loading ? "Lädt..." : "Aktualisieren" }}
        </button>
      </div>

      <div class="project-grid">
        <article v-for="project in projects" :key="project.id" class="project-card">
          <h3>{{ project.title }}</h3>
          <p v-if="project.description" class="muted small">{{ project.description }}</p>
          <button class="btn sm" type="button" @click="openProject(project.id)">Öffnen</button>
        </article>
      </div>
    </section>

    <!-- Create modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal-box">
        <div class="modal-header">
          <h3>Neues Projekt erstellen</h3>
          <button class="modal-close" type="button" @click="showCreateModal = false">&times;</button>
        </div>
        <form class="modal-form" @submit.prevent="createProject">
          <label>
            Titel
            <input v-model.trim="form.title" class="input" placeholder="z. B. Mein Haushalt" required />
          </label>
          <label>
            Währung
            <select v-model="form.currency" class="input">
              <option value="EUR">EUR</option>
              <option value="USD">USD</option>
              <option value="CHF">CHF</option>
            </select>
          </label>
          <label>
            Notiz (optional)
            <textarea v-model.trim="form.description" class="input textarea" rows="2" placeholder=""></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showCreateModal = false">Abbrechen</button>
            <button class="btn" type="submit" :disabled="saving">
              {{ saving ? "Erstelle..." : "Projekt erstellen" }}
            </button>
          </div>
        </form>
      </div>
    </div>
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
const showCreateModal = ref(false);
const errorMessage = ref("");
const successMessage = ref("");
const form = ref({ title: "", currency: "EUR", description: "" });

function goBack() {
  router.push({ name: "platforms" });
}

function openProject(id) {
  router.push({ name: "finance", params: { projectId: id } });
}

function apiError(err, fallback) {
  const d = err?.response?.data;
  if (typeof d === "string" && d.trim()) return d;
  if (d?.detail) return d.detail;
  if (d && typeof d === "object") {
    const msg = Object.entries(d).map(([k, v]) => `${k}: ${Array.isArray(v) ? v.join(", ") : v}`).join(" | ");
    if (msg) return msg;
  }
  return fallback;
}

async function loadProjects() {
  loading.value = true;
  try {
    const { data } = await api.get("finance-projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    errorMessage.value = apiError(err, "Projekte konnten nicht geladen werden.");
  } finally {
    loading.value = false;
  }
}

async function createProject() {
  saving.value = true;
  try {
    const { data } = await api.post("finance-projects/", {
      title: form.value.title,
      currency: form.value.currency,
      description: form.value.description,
      initial_members: [],
    });
    showCreateModal.value = false;
    form.value = { title: "", currency: "EUR", description: "" };
    await loadProjects();
    router.push({ name: "finance", params: { projectId: data.id } });
  } catch (err) {
    errorMessage.value = apiError(err, "Projekt konnte nicht erstellt werden.");
  } finally {
    saving.value = false;
  }
}

onMounted(loadProjects);
</script>

<style scoped>
.finance-landing {
  display: grid;
  gap: 18px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
  gap: 18px;
  padding: 22px;
  background:
    radial-gradient(circle at top right, rgba(47, 99, 255, 0.15), transparent 42%),
    linear-gradient(145deg, var(--card), var(--bg-soft));
}

.hero-copy {
  display: grid;
  gap: 14px;
  align-content: start;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--brand, #2f63ff);
  font-weight: 700;
}

.lead { max-width: 60ch; }

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-points span {
  padding: 8px 12px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--brand, #2f63ff) 10%, var(--surface));
  border: 1px solid color-mix(in srgb, var(--brand, #2f63ff) 18%, var(--border));
  font-size: 14px;
  font-weight: 600;
}

.action-panel {
  display: grid;
  gap: 14px;
  padding: 18px;
  border-radius: 16px;
  border: 1px solid var(--border);
  background: var(--card);
  align-content: start;
}

.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.section-head h2 { margin: 0; }

.projects-section {
  display: grid;
  gap: 16px;
  padding: 20px;
}

.project-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
}

.project-card {
  display: grid;
  gap: 10px;
  padding: 16px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.project-card h3 { margin: 0; }

.feedback-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.feedback-pill {
  padding: 10px 16px;
  border-radius: 12px;
  font-weight: 500;
  font-size: 14px;
  border: 1px solid var(--border);
  background: var(--surface);
}

.feedback-pill.error {
  background: color-mix(in srgb, #ef4444 12%, var(--surface));
  border-color: color-mix(in srgb, #ef4444 24%, var(--border));
  color: color-mix(in srgb, #ef4444 70%, var(--text));
}

.feedback-pill.success {
  background: color-mix(in srgb, #22c55e 12%, var(--surface));
  border-color: color-mix(in srgb, #22c55e 24%, var(--border));
  color: color-mix(in srgb, #22c55e 70%, var(--text));
}

.modal-overlay {
  position: fixed;
  inset: 0;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.5);
  z-index: 50;
  padding: 16px;
}

.modal-box {
  width: min(440px, 100%);
  max-height: 90vh;
  overflow: auto;
  border-radius: 20px;
  border: 1px solid var(--border);
  background: var(--card);
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
  font-size: 22px;
  cursor: pointer;
  color: var(--muted);
  line-height: 1;
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

.textarea { min-height: 70px; resize: vertical; }
.small { font-size: 13px; }
.sm { padding: 8px 14px; font-size: 14px; }

@media (max-width: 900px) {
  .hero { grid-template-columns: 1fr; }
}
</style>
