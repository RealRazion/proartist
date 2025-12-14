<template>
  <div class="songs">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
    <header class="card header">
      <div>
        <h1>Songs & Versionen</h1>
        <p class="muted">
          Verwalte Songs, lade neue Versionen hoch. Projekte zuweisen d&uuml;rfen nur Team-Mitglieder.
        </p>
      </div>
      <button class="btn ghost" type="button" @click="refresh" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section class="card filters">
      <div class="filter-row">
        <label>
          Suche
          <input class="input" v-model.trim="search" placeholder="Titel oder Beschreibung..." @keyup.enter="applyFilters" />
        </label>
        <label>
          Status
          <select class="input" v-model="filterStatus" @change="applyFilters">
            <option value="ALL">Alle</option>
            <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
          </select>
        </label>
        <label v-if="isTeam">
          Projekt
          <select class="input" v-model="filterProject" @change="applyFilters">
            <option value="ALL">Alle</option>
            <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
          </select>
        </label>
        <label>
          Sortierung
          <select class="input" v-model="sort" @change="applyFilters">
            <option value="-created_at">Neueste zuerst</option>
            <option value="created_at">&Auml;lteste zuerst</option>
            <option value="title">Titel A-Z</option>
            <option value="-title">Titel Z-A</option>
            <option value="status">Status</option>
          </select>
        </label>
      </div>
      <div class="filter-row secondary">
        <label class="check"><input type="checkbox" v-model="filterMix" @change="applyFilters" /> Mix vorhanden</label>
        <label class="check"><input type="checkbox" v-model="filterMaster" @change="applyFilters" /> Master vorhanden</label>
        <label class="check"><input type="checkbox" v-model="filterFinal" @change="applyFilters" /> Finale Version</label>
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
      <div class="form-actions">
        <button class="btn" type="button" @click="createSong" :disabled="creating || loading">
          {{ creating ? "Speichere..." : "Song speichern" }}
        </button>
        <p v-if="formMessage" :class="['feedback', formMessageType]">{{ formMessage }}</p>
      </div>
    </section>

    <section class="song-grid">
      <article v-for="song in filteredSongs" :key="song.id" class="card song" :data-status="song.status">
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
                <div>
                  <strong>v{{ v.version_number }}</strong>
                  <span class="tags">
                    <span v-if="v.is_mix_ready" class="tag">Mix</span>
                    <span v-if="v.is_master_ready" class="tag">Master</span>
                    <span v-if="v.is_final" class="tag final">Final</span>
                  </span>
                </div>
                <small class="muted">{{ formatDateTime(v.created_at) }}</small>
              </div>
              <p class="muted small">{{ v.notes || "Keine Notiz" }}</p>
              <a v-if="v.file" class="link" :href="v.file" target="_blank" rel="noopener">Download</a>
            </li>
          </ul>
          <p v-else class="muted small">Noch keine Versionen.</p>
          <form class="upload" @submit.prevent="uploadVersion(song.id)">
            <input class="input" v-model.trim="versionDraft(song.id).notes" placeholder="Notiz" />
            <label class="file-picker">
              <input type="file" @change="onFile(song.id, $event)" />
              {{ versionDraft(song.id).file ? versionDraft(song.id).file.name : "Datei w&auml;hlen" }}
            </label>
            <div class="flags">
              <label><input type="checkbox" v-model="versionDraft(song.id).is_mix_ready" /> Mix</label>
              <label><input type="checkbox" v-model="versionDraft(song.id).is_master_ready" /> Master</label>
              <label><input type="checkbox" v-model="versionDraft(song.id).is_final" /> Final</label>
            </div>
            <button class="btn tiny" type="submit" :disabled="uploading[song.id]">
              {{ uploading[song.id] ? "L&auml;dt..." : "Version hochladen" }}
            </button>
          </form>
        </div>
      </article>
    </section>

    <div class="pagination" v-if="pageCount > 1">
      <button class="btn ghost tiny" type="button" :disabled="page === 1 || loading" @click="changePage(-1)">Zur&uuml;ck</button>
      <span>Seite {{ page }} / {{ pageCount }}</span>
      <button class="btn ghost tiny" type="button" :disabled="page === pageCount || loading" @click="changePage(1)">Weiter</button>
    </div>

    <section v-if="isTeam" class="card activity">
      <div class="activity-head">
        <h2>Aktivit&auml;t</h2>
        <button class="btn ghost tiny" type="button" @click="loadActivity" :disabled="loadingActivity">
          {{ loadingActivity ? "Lade..." : "Neu laden" }}
        </button>
      </div>
      <ul v-if="activities.length">
        <li v-for="item in activities" :key="item.id">
          <div class="row">
            <strong>{{ item.title }}</strong>
            <span class="pill subtle">{{ formatDateTime(item.created_at) }}</span>
          </div>
          <p class="muted small">{{ item.description || item.event_type }}</p>
        </li>
      </ul>
      <p v-else class="muted small">Keine Aktivit&auml;ten vorhanden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";

const { isTeam, fetchProfile } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();

const songs = ref([]);
const versions = ref({});
const projects = ref([]);
const activities = ref([]);

const loading = ref(false);
const creating = ref(false);
const uploading = ref({});
const loadingActivity = ref(false);

const search = ref("");
const filterStatus = ref("ALL");
const filterProject = ref("ALL");
const filterMix = ref(false);
const filterMaster = ref(false);
const filterFinal = ref(false);
const sort = ref("-created_at");

const page = ref(1);
const pageSize = ref(9);
const total = ref(0);

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
const formMessage = ref("");
const formMessageType = ref("info");

const drafts = ref({});

const filteredSongs = computed(() => {
  return songs.value.filter((song) => {
    const term = search.value.trim().toLowerCase();
    const matchesText =
      !term ||
      song.title.toLowerCase().includes(term) ||
      (song.description || "").toLowerCase().includes(term);
    const matchesStatus = filterStatus.value === "ALL" || song.status === filterStatus.value;
    const matchesProject =
      filterProject.value === "ALL" || String(song.project) === String(filterProject.value);
    const flags = versions.value[song.id] || [];
    const hasMix = flags.some((v) => v.is_mix_ready);
    const hasMaster = flags.some((v) => v.is_master_ready);
    const hasFinal = flags.some((v) => v.is_final);
    const matchesMix = !filterMix.value || hasMix;
    const matchesMaster = !filterMaster.value || hasMaster;
    const matchesFinal = !filterFinal.value || hasFinal;
    return matchesText && matchesStatus && matchesProject && matchesMix && matchesMaster && matchesFinal;
  });
});

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)));

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
    const { data } = await api.get("projects/", { params: { page_size: 100 } });
    const list = Array.isArray(data) ? data : data.results || [];
    projects.value = list;
  } catch (err) {
    projects.value = [];
  }
}

async function loadSongs(resetPage = false) {
  if (resetPage) page.value = 1;
  loading.value = true;
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value,
      ordering: sort.value,
    };
    if (filterStatus.value !== "ALL") params.status = filterStatus.value;
    if (filterProject.value !== "ALL") params.project = filterProject.value;
    if (search.value.trim()) params.search = search.value.trim();
    const { data } = await api.get("songs/", { params });
    const payload = data || {};
    const items = Array.isArray(payload) ? payload : payload.results || [];
    songs.value = items;
    total.value = payload.count || items.length;
    items.forEach((song) => ensureVersions(song.id));
  } catch (err) {
    console.error("Songs konnten nicht geladen werden", err);
    songs.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

async function ensureVersions(songId, force = false) {
  if (!force && versions.value[songId]) return;
  try {
    const { data } = await api.get("song-versions/", { params: { song: songId, ordering: "-created_at", page_size: 50 } });
    const payload = data || {};
    const items = Array.isArray(payload) ? payload : payload.results || [];
    versions.value = { ...versions.value, [songId]: items };
  } catch (err) {
    console.error("Versionen konnten nicht geladen werden", err);
  }
}

async function loadActivity() {
  if (!isTeam.value) {
    activities.value = [];
    return;
  }
  loadingActivity.value = true;
  try {
    const { data } = await api.get("activity/", {
      params: { limit: 40, types: "song_created,song_updated,song_version_created" },
    });
    activities.value = data || [];
  } catch (err) {
    activities.value = [];
  } finally {
    loadingActivity.value = false;
  }
}

async function createSong() {
  if (!form.value.title) {
    showFormMessage("Titel ist erforderlich", "error");
    return;
  }
  creating.value = true;
  showFormMessage("");
  try {
    await api.post("songs/", form.value);
    form.value = { title: "", description: "", status: "ACTIVE", project: "" };
    await loadSongs(true);
    showFormMessage("Song angelegt", "success");
    showToast("Song angelegt", "success");
  } catch (err) {
    console.error("Song konnte nicht erstellt werden", err);
    showFormMessage("Fehler beim Speichern", "error");
    showToast("Fehler beim Speichern", "error");
  } finally {
    creating.value = false;
  }
}

function onFile(songId, event) {
  versionDraft(songId).file = event.target.files?.[0] || null;
}

async function uploadVersion(songId) {
  const draft = versionDraft(songId);
  if (!draft.file) {
    showFormMessage("Bitte eine Datei ausw&auml;hlen", "error");
    return;
  }
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
    showFormMessage("Version hochgeladen", "success");
    showToast("Version hochgeladen", "success");
  } catch (err) {
    console.error("Version konnte nicht hochgeladen werden", err);
    showFormMessage("Fehler beim Upload", "error");
    showToast("Fehler beim Upload", "error");
  } finally {
    uploading.value = { ...uploading.value, [songId]: false };
  }
}

function showFormMessage(text, type = "info") {
  formMessage.value = text;
  formMessageType.value = type;
  if (text) {
    setTimeout(() => (formMessage.value = ""), 2500);
  }
}

async function refresh() {
  await Promise.all([loadProjects(), loadSongs(), loadActivity()]);
}

function changePage(delta) {
  const next = page.value + delta;
  if (next < 1 || next > pageCount.value) return;
  page.value = next;
  loadSongs();
}

function applyFilters() {
  loadSongs(true);
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProjects(), loadSongs(), loadActivity()]);
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
  align-items: flex-end;
}
.filters .secondary {
  margin-top: 6px;
}
.filters .check {
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
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
.form-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.feedback {
  margin: 0;
  font-size: 14px;
}
.feedback.error {
  color: #dc2626;
}
.feedback.success {
  color: #16a34a;
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
  border-top: 4px solid transparent;
}
.song[data-status="ARCHIVED"] {
  border-top-color: rgba(148, 163, 184, 0.6);
}
.song[data-status="INACTIVE"] {
  border-top-color: rgba(234, 179, 8, 0.5);
}
.song[data-status="ACTIVE"] {
  border-top-color: rgba(59, 130, 246, 0.5);
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
.pill.subtle {
  background: rgba(15, 23, 42, 0.06);
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
  align-items: center;
}
.tags {
  display: inline-flex;
  gap: 6px;
  margin-left: 6px;
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
.pagination {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}
.activity ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.activity-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
@media (min-width: 1200px) {
  .song-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 720px) {
  .upload {
    grid-template-columns: 1fr;
  }
}
</style>
