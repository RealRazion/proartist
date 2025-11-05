<template>
  <div class="projects">
    <header class="card header">
      <div>
        <h1>Projekte</h1>
        <p class="muted">Plane Releases, Kampagnen oder Events im Team.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadProjects" :disabled="loading">
        {{ loading ? "Lade…" : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">
        Projekte können nur von Team-Mitgliedern verwaltet werden. Falls du Zugriff brauchst, kontaktiere dein Team.
      </p>
    </section>

    <section v-else class="grid">
      <form class="card form" @submit.prevent="createProject">
        <h2>Neues Projekt</h2>
        <label>
          Titel
          <input class="input" v-model.trim="newProject.title" placeholder="z. B. Album Release" required />
        </label>
        <label>
          Beschreibung
          <textarea class="input textarea" v-model.trim="newProject.description" placeholder="Kurzbeschreibung"></textarea>
        </label>
        <label>
          Status
          <select class="input" v-model="newProject.status">
            <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
          </select>
        </label>
        <label>
          Team / Künstler
          <select class="input" v-model="newProject.participant_ids" multiple size="6">
            <option v-for="profile in profiles" :key="profile.id" :value="profile.id">
              {{ profile.name }}
            </option>
          </select>
          <small class="hint muted">Mehrfachauswahl mit Strg/⌘ möglich.</small>
        </label>
        <button class="btn" type="submit" :disabled="creating">
          {{ creating ? "Speichere…" : "Projekt anlegen" }}
        </button>
      </form>

      <div class="card filters-panel">
        <h2>Filter</h2>
        <div class="filters">
          <label>
            Suche
            <input class="input" v-model.trim="search" placeholder="Titel durchsuchen" />
          </label>
          <label>
            Status
            <select class="input" v-model="filterStatus">
              <option value="ALL">Alle</option>
              <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
            </select>
          </label>
          <label>
            Teilnehmer
            <select class="input" v-model="filterMember">
              <option value="ALL">Alle</option>
              <option v-for="profile in profiles" :key="profile.id" :value="profile.id">{{ profile.name }}</option>
            </select>
          </label>
        </div>
      </div>

      <div class="card list">
        <h2>Aktuelle Projekte</h2>
        <div v-if="!filteredProjects.length" class="muted empty">Keine Projekte passend zum Filter.</div>
        <ul>
          <li v-for="project in filteredProjects" :key="project.id">
            <div class="meta">
              <h3>{{ project.title }}</h3>
              <span class="status" :data-status="project.status">{{ statusLabels[project.status] || project.status }}</span>
            </div>
            <p class="muted">{{ project.description || "Keine Beschreibung" }}</p>
            <div class="participants" v-if="project.participants?.length">
              <span class="chip" v-for="member in project.participants" :key="member.id">{{ member.name }}</span>
            </div>
            <footer>
              <small class="muted">Erstellt am {{ formatDate(project.created_at) }}</small>
              <select class="input status-select" v-model="project.status" @change="updateStatus(project)">
                <option v-for="opt in statusOptions" :key="opt" :value="opt">{{ statusLabels[opt] }}</option>
              </select>
            </footer>
          </li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

const projects = ref([]);
const profiles = ref([]);
const loading = ref(false);
const creating = ref(false);

const newProject = ref({
  title: "",
  description: "",
  status: "PLANNED",
  participant_ids: [],
});
const search = ref("");
const filterStatus = ref("ALL");
const filterMember = ref("ALL");

const statusOptions = ["PLANNED", "IN_PROGRESS", "REVIEW", "DONE", "ON_HOLD"];
const statusLabels = {
  PLANNED: "Geplant",
  IN_PROGRESS: "In Arbeit",
  REVIEW: "Review",
  DONE: "Abgeschlossen",
  ON_HOLD: "Pausiert",
};

const filteredProjects = computed(() => {
  const term = search.value.trim().toLowerCase();
  return projects.value.filter((project) => {
    const matchesSearch =
      !term ||
      project.title.toLowerCase().includes(term) ||
      (project.description || "").toLowerCase().includes(term);
    const matchesStatus = filterStatus.value === "ALL" || project.status === filterStatus.value;
    const matchesMember =
      filterMember.value === "ALL" ||
      (project.participants || []).some((p) => String(p.id) === String(filterMember.value));
    return matchesSearch && matchesStatus && matchesMember;
  });
});

async function loadProjects() {
  if (loading.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("projects/");
    projects.value = data;
  } catch (err) {
    console.error("Projekte konnten nicht geladen werden", err);
  } finally {
    loading.value = false;
  }
}

async function loadProfiles() {
  try {
    const { data } = await api.get("profiles/");
    profiles.value = data.map((profile) => ({
      id: profile.id,
      name: profile.name || profile.username,
    }));
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    profiles.value = [];
  }
}

async function createProject() {
  if (!newProject.value.title) return;
  creating.value = true;
  try {
    await api.post("projects/", newProject.value);
    newProject.value = { title: "", description: "", status: "PLANNED", participant_ids: [] };
    await loadProjects();
  } catch (err) {
    console.error("Projekt konnte nicht erstellt werden", err);
  } finally {
    creating.value = false;
  }
}

async function updateStatus(project) {
  try {
    await api.patch(`projects/${project.id}/`, { status: project.status });
  } catch (err) {
    console.error("Status-Update fehlgeschlagen", err);
    await loadProjects();
  }
}

function formatDate(dateValue) {
  if (!dateValue) return "Unbekannt";
  return new Date(dateValue).toLocaleDateString();
}

onMounted(async () => {
  await fetchProfile();
  if (isTeam.value) {
    await loadProfiles();
    await loadProjects();
  }
});
</script>

<style scoped>
.projects {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.info {
  max-width: 600px;
}
.grid {
  display: grid;
  grid-template-columns: minmax(260px, 320px) 1fr;
  gap: 18px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.filters-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.filters {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}
.hint {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
}
.textarea {
  min-height: 90px;
  resize: vertical;
}
.list ul {
  list-style: none;
  margin: 16px 0 0;
  padding: 0;
  display: grid;
  gap: 14px;
}
.list li {
  border: 1px solid rgba(75, 91, 255, 0.08);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  background: rgba(75, 91, 255, 0.12);
  color: var(--brand);
}
[data-status="PLANNED"] {
  background: rgba(75, 91, 255, 0.12);
  color: var(--brand);
}
[data-status="DONE"] {
  background: rgba(52, 211, 153, 0.18);
  color: #059669;
}
[data-status="IN_PROGRESS"] {
  background: rgba(249, 115, 22, 0.18);
  color: #ea580c;
}
[data-status="ON_HOLD"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.participants {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.chip {
  background: rgba(112, 130, 255, 0.18);
  color: var(--brand);
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}
.status-select {
  max-width: 160px;
}
.empty {
  text-align: center;
  padding: 20px 0;
}

@media (max-width: 960px) {
  .grid {
    grid-template-columns: 1fr;
  }
  footer {
    flex-direction: column;
    align-items: flex-start;
  }
  .status-select {
    width: 100%;
  }
  .filters {
    grid-template-columns: 1fr;
  }
}
</style>
