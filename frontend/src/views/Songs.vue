<template>
  <div class="songs">
    <header class="card header">
      <div>
        <h1>Songs & Versionen</h1>
        <p class="muted">Verwalte deine Songs und lade neue Versionen hoch. Projekt-Zuordnung nur für Team.</p>
      </div>
      <button class="btn ghost" type="button" @click="refresh" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section class="card filters">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="search" placeholder="Titel oder Beschreibung..." />
        </label>
        <label>
          Status
          <select class="input" v-model="filterStatus" @change="loadSongs">
            <option value="ALL">Alle</option>
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
        <label v-if="isTeam">
          Projekt
          <select class="input" v-model="filterProject" @change="loadSongs">
            <option value="ALL">Alle</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
        </label>
      </div>
    </section>

    <section class="card form">
      <h2>Song anlegen</h2>
      <div class="form-grid">
        <label>
          Titel
          <input class="input" v-model.trim="form.title" placeholder="Songtitel" />
        </label>
        <label>
          Beschreibung
          <input class="input" v-model.trim="form.description" placeholder="Notes" />
        </label>
        <label>
          Status
          <select class="input" v-model="form.status">
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
        <label v-if="isTeam">
          Projekt (optional)
          <select class="input" v-model="form.project">
            <option value="">Kein Projekt</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
        </label>
      </div>
      <button class="btn" type="button" @click="createSong" :disabled="creating">
        {{ creating ? "Speichere..." : "Song speichern" }}
      </button>
    </section>

    <section class="song-grid">
      <article v-for="song in filteredSongs" :key="song.id" class="card song">
        <div class="song-head">
          <div>
            <h3>{{ song.title }}</h3>
            <p class="muted">{{ song.description || "Keine Beschreibung" }}</p>
            <p class="muted small">Projekt: {{ song.project_title || "Keins" }}</p>
          </div>
          <span class="pill" :data-status="song.status">{{ statusLabels[song.status] || song.status }}</span>
        </div>
        <div class="versions">
          <header>
            <p class="muted">Versionen</p>
            <button class="btn ghost tiny" type="button" @click="ensureVersions(song.id, true)">
              Neu laden
            </button>
          </header>
          <ul v-if="versions[song.id]?.length">
            <li v-for="v in versions[song.id]" :key="v.id">
              <div class="row">
                <strong>v{{ v.version_number }}</strong>
                <span class="tags">
                  <span v-if="v.is_mix_ready" class="tag">Mix</span>
                  <span v-if="v.is_master_ready" class="tag">Master</span>
                  <span v-if="v.is_final" class="tag final">Final</span>
                </span>
              </div>
              <p class="muted small">{{ formatDateTime(v.created_at) }}</p>
              <p class="muted small">{{ v.notes || "Keine Notiz" }}</p>
              <a v-if="v.file" class="link" :href="v.file" target="_blank" rel="noopener">Download</a>
            </li>
          </ul>
          <p v-else class="muted small">Noch keine Versionen.</p>
          <form class="upload" @submit.prevent="uploadVersion(song.id)">
            <input class="input" v-model.trim="versionDraft(song.id).notes" placeholder="Notiz" />
            <label class="file-picker">
              <input type="file" @change="onFile(song.id, $event)" />
              {{ versionDraft(song.id).file ? versionDraft(song.id).file.name : "Datei wählen" }}
            </label>
            <div class="flags">
              <label><input type="checkbox" v-model="versionDraft(song.id).is_mix_ready" /> Mix</label>
              <label><input type="checkbox" v-model="versionDraft(song.id).is_master_ready" /> Master</label>
              <label><input type="checkbox" v-model="versionDraft(song.id).is_final" /> Final</label>
            </div>
            <button class="btn tiny" type="submit" :disabled="uploading[song.id]">
              {{ uploading[song.id] ? "Lädt..." : "Version hochladen" }}
            </button>
          </form>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();

const songs = ref([]);
const versions = ref({});
const projects = ref([]);
const loading = ref(false);
const creating = ref(false);
const uploading = ref({});

const search = ref("");
const filterStatus = ref("ALL");
const filterProject = ref("ALL");

const statusOptions = ["ACTIVE", "INACTIVE", "ARCHIVED"];
const statusLabels = {
  ACTIVE: "Aktiv",
  INACTIVE: "Inaktiv",
  ARCHIVED: "Archiviert",
};

const form = ref({
  title: "",
  description: "",
  status: "ACTIVE",
  project: "",
});

const drafts = ref({});

const filteredSongs = computed(() =>
  songs.value.filter((song) => {
    const term = search.value.trim().toLowerCase();
    const matchesText =
      !term ||
      song.title.toLowerCase().includes(term) ||
      (song.description || "").toLowerCase().includes(term);
    const matchesStatus = filterStatus.value === "ALL" || song.status === filterStatus.value;
    const matchesProject =
      filterProject.value === "ALL" || String(song.project) === String(filterProject.value);
    return matchesText && matchesStatus && matchesProject;
  })
);

function versionDraft(songId) {
  if (!drafts.value[songId]) {
    drafts.value[songId] = { notes: "", file: null, is_mix_ready: false, is_master_ready: false, is_final: false };
  }
  return drafts.value[songId];
}

function formatDateTime(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

async function loadProjects() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("projects/");
    projects.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    projects.value = [];
  }
}

async function loadSongs() {
  loading.value = true;
  try {
    const params = {};
    if (filterStatus.value !== "ALL") params.status = filterStatus.value;
    if (filterProject.value !== "ALL") params.project = filterProject.value;
    const { data } = await api.get("songs/", { params });
    songs.value = data || [];
    // Lazy load versions for visible songs
    songs.value.forEach((song) => ensureVersions(song.id));
  } catch (err) {
    console.error("Songs konnten nicht geladen werden", err);
    songs.value = [];
  } finally {
    loading.value = false;
  }
}

async function ensureVersions(songId, force = false) {
  if (!force && versions.value[songId]) return;
  try {
    const { data } = await api.get("song-versions/", { params: { song: songId } });
    versions.value = { ...versions.value, [songId]: data || [] };
  } catch (err) {
    console.error("Versionen konnten nicht geladen werden", err);
  }
}

async function createSong() {
  if (!form.value.title) return;
  creating.value = true;
  try {
    await api.post("songs/", form.value);
    form.value = { title: "", description: "", status: "ACTIVE", project: "" };
    await loadSongs();
  } catch (err) {
    console.error("Song konnte nicht erstellt werden", err);
  } finally {
    creating.value = false;
  }
}

function onFile(songId, event) {
  versionDraft(songId).file = event.target.files?.[0] || null;
}

async function uploadVersion(songId) {
  const draft = versionDraft(songId);
  if (!draft.file) return;
  uploading.value = { ...uploading.value, [songId]: true };
  try {
    const formData = new FormData();
    formData.append("song", songId);
    formData.append("file", draft.file);
    formData.append("notes", draft.notes);
    formData.append("is_mix_ready", draft.is_mix_ready ? 1 : 0);
    formData.append("is_master_ready", draft.is_master_ready ? 1 : 0);
    formData.append("is_final", draft.is_final ? 1 : 0);
    await api.post("song-versions/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    draft.file = null;
    draft.notes = "";
    draft.is_mix_ready = false;
    draft.is_master_ready = false;
    draft.is_final = false;
    await ensureVersions(songId, true);
  } catch (err) {
    console.error("Version konnte nicht hochgeladen werden", err);
  } finally {
    uploading.value = { ...uploading.value, [songId]: false };
  }
}

async function refresh() {
  await loadSongs();
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProjects(), loadSongs()]);
});
</script>

<style scoped>
.songs {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}
.filters .filter-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.song-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 12px;
}
.song {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.song-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}
.pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(75, 91, 255, 0.18);
}
.pill[data-status="INACTIVE"] {
  background: rgba(148, 163, 184, 0.18);
  color: #475569;
}
.pill[data-status="ARCHIVED"] {
  background: rgba(0, 0, 0, 0.08);
  color: #475569;
}
.versions ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.versions li {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 10px;
  padding: 8px 10px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
}
.tags {
  display: flex;
  gap: 6px;
}
.tag {
  background: rgba(59, 130, 246, 0.18);
  color: #1d4ed8;
  border-radius: 8px;
  padding: 2px 8px;
  font-size: 11px;
  font-weight: 600;
}
.tag.final {
  background: rgba(16, 185, 129, 0.18);
  color: #0f766e;
}
.upload {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  align-items: center;
}
.file-picker {
  border: 1px dashed var(--border);
  border-radius: 10px;
  padding: 6px 10px;
  font-size: 13px;
  cursor: pointer;
}
.file-picker input {
  display: none;
}
.flags {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 13px;
}
.small {
  font-size: 13px;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}
@media (min-width: 1200px) {
  .song-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
