<template>
  <div class="music-page">

    <!-- Hero -->
    <header class="music-hero">
      <div class="hero-left">
        <p class="eyebrow">UNYQ Music Manager</p>
        <h1>Song-Bibliothek</h1>
        <p class="hero-lead">Verwalte Ideas, Demos und fertige Tracks. Tracke Mix-, Master- und Final-Status per Version.</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="goHome">← Hub</button>
        <button class="btn" type="button" @click="showCreateForm = !showCreateForm">
          {{ showCreateForm ? 'Schließen' : '+ Song anlegen' }}
        </button>
      </div>
    </header>

    <section class="stats-grid">
      <article class="stat-card">
        <strong>{{ songs.length }}</strong>
        <span>Tracks</span>
      </article>
      <article class="stat-card">
        <strong>{{ finalCount }}</strong>
        <span>Finale Songs</span>
      </article>
      <article class="stat-card">
        <strong>{{ totalVersions }}</strong>
        <span>Versionen</span>
      </article>
      <article class="stat-card">
        <strong>{{ mixReadyCount }}</strong>
        <span>Mix-ready</span>
      </article>
    </section>

    <!-- Create form -->
    <div v-if="showCreateForm" class="create-card">
      <h3>Neuen Song anlegen</h3>
      <form class="song-form" @submit.prevent="createSong">
        <label>Titel <input v-model.trim="newSong.title" required placeholder="z. B. Midnight Drive" class="sinput" /></label>
        <label>Status
          <select v-model="newSong.status" class="sinput">
            <option value="ACTIVE">Aktiv</option>
            <option value="INACTIVE">Inaktiv</option>
            <option value="ARCHIVED">Archiviert</option>
          </select>
        </label>
        <label>Genre <input v-model.trim="newSong.genre" placeholder="z. B. Drill" class="sinput" /></label>
        <label>Mood <input v-model.trim="newSong.mood" placeholder="z. B. Dark" class="sinput" /></label>
        <label>BPM <input v-model.number="newSong.bpm" type="number" min="40" max="260" class="sinput" /></label>
        <label>Key <input v-model.trim="newSong.key_signature" placeholder="z. B. Am" class="sinput" /></label>
        <label>Release-Datum <input v-model="newSong.release_date" type="date" class="sinput" /></label>
        <label>Tags (Komma-getrennt)
          <input v-model.trim="newSong.tagsInput" placeholder="club, summer, single" class="sinput" />
        </label>
        <label class="full">Beschreibung
          <textarea v-model.trim="newSong.description" class="sinput" rows="2" placeholder="Thema, Stimmung, Notizen..."></textarea>
        </label>
        <div class="form-actions full">
          <button class="btn ghost" type="button" @click="showCreateForm = false">Abbrechen</button>
          <button class="btn" type="submit" :disabled="saving">{{ saving ? 'Speichern...' : 'Song erstellen' }}</button>
        </div>
      </form>
    </div>

    <!-- Filter bar -->
    <div class="filter-bar">
      <div class="filter-chips" role="group" aria-label="Status-Filter">
        <button
          v-for="f in filters"
          :key="f.value"
          type="button"
          :class="['fchip', { active: activeFilter === f.value }]"
          @click="activeFilter = f.value"
        >{{ f.label }}</button>
      </div>
      <div class="search-wrap">
        <svg viewBox="0 0 24 24" aria-hidden="true" class="search-ico"><circle cx="11" cy="11" r="7"/><path d="M16.5 16.5l4 4"/></svg>
        <input v-model="searchQuery" class="sinput search-input" placeholder="Song suchen..." />
      </div>
      <label class="mini-filter">
        Genre
        <input v-model.trim="genreQuery" class="sinput" placeholder="Genre filtern" />
      </label>
      <label class="mini-filter check-inline">
        <input type="checkbox" v-model="onlyWithFinal" />
        Nur mit Final-Version
      </label>
    </div>

    <!-- Songs list -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Lädt Songs...</p>
    </div>

    <div v-else-if="filteredSongs.length === 0" class="empty-state">
      <span class="empty-ico">🎵</span>
      <p>{{ searchQuery ? 'Keine Songs gefunden.' : 'Noch keine Songs angelegt.' }}</p>
    </div>

    <div v-else class="songs-grid">
      <article
        v-for="song in filteredSongs"
        :key="song.id"
        class="song-card"
        :class="`song-${song.status.toLowerCase()}`"
      >
        <div class="song-top">
          <div class="song-main">
            <span :class="['song-status-badge', `badge-${song.status.toLowerCase()}`]">
              {{ statusLabel(song.status) }}
            </span>
            <h3>{{ song.title }}</h3>
            <p v-if="song.description" class="song-desc">{{ song.description }}</p>
            <div class="song-attrs">
              <span v-if="song.genre" class="meta-pill">{{ song.genre }}</span>
              <span v-if="song.mood" class="meta-pill">{{ song.mood }}</span>
              <span v-if="song.bpm" class="meta-pill">{{ song.bpm }} BPM</span>
              <span v-if="song.key_signature" class="meta-pill">Key {{ song.key_signature }}</span>
              <span v-if="song.release_date" class="meta-pill">Release {{ formatDate(song.release_date) }}</span>
              <span v-for="tag in song.tags || []" :key="`${song.id}-${tag}`" class="meta-pill">#{{ tag }}</span>
            </div>
          </div>
          <div class="song-meta">
            <span class="meta-pill">{{ song.versions?.length || 0 }} Versionen</span>
            <span class="meta-date">{{ formatDate(song.created_at) }}</span>
          </div>
        </div>

        <!-- Version list -->
        <div v-if="song.versions && song.versions.length" class="version-list">
          <div v-for="v in song.versions" :key="v.id" class="version-row">
            <span class="version-num">v{{ v.version_number }}</span>
            <div class="version-flags">
              <span :class="['vflag', { active: v.is_mix_ready }]">Mix</span>
              <span :class="['vflag', { active: v.is_master_ready }]">Master</span>
              <span :class="['vflag', { active: v.is_final }]">🏆 Final</span>
            </div>
            <span v-if="v.notes" class="version-notes">{{ v.notes }}</span>
            <span class="version-duration">{{ formatDuration(v.duration_seconds) }}</span>
            <div class="version-actions">
              <button class="btn ghost tiny" type="button" @click="playVersion(song.id, v)">
                {{ isPlaying(song.id, v.id) ? 'Stop' : 'Preview' }}
              </button>
              <button class="btn ghost tiny" type="button" @click="assignCompare(song.id, 'A', v.id)">A</button>
              <button class="btn ghost tiny" type="button" @click="assignCompare(song.id, 'B', v.id)">B</button>
            </div>
            <a v-if="v.file_url || v.file" class="file-link" :href="v.file_url || v.file" target="_blank" rel="noopener">Audio</a>
          </div>

          <div v-if="(song.versions || []).length > 1" class="ab-panel">
            <div class="ab-head">
              <strong>A/B Compare</strong>
              <button class="btn ghost tiny" type="button" @click="clearCompare(song.id)">Reset</button>
            </div>
            <div class="ab-grid">
              <div class="ab-slot">
                <span class="slot-label">A</span>
                <span class="slot-value">{{ compareVersionLabel(song, 'A') }}</span>
                <button class="btn ghost tiny" type="button" :disabled="!compareVersion(song.id, 'A')" @click="playCompare(song.id, 'A')">Play A</button>
              </div>
              <div class="ab-slot">
                <span class="slot-label">B</span>
                <span class="slot-value">{{ compareVersionLabel(song, 'B') }}</span>
                <button class="btn ghost tiny" type="button" :disabled="!compareVersion(song.id, 'B')" @click="playCompare(song.id, 'B')">Play B</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Add version form -->
        <div class="add-version">
          <button
            class="add-version-toggle"
            type="button"
            @click="toggleVersionForm(song.id)"
          >
            <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
            Version hinzufügen
          </button>
          <div v-if="openVersionForms[song.id]" class="version-form">
            <form @submit.prevent="addVersion(song.id)">
              <div class="version-form-grid">
                <label>Nr.
                  <input v-model.number="versionDraft(song.id).version_number" type="number" min="1" class="sinput" />
                </label>
                <label>Mix ready
                  <select v-model="versionDraft(song.id).is_mix_ready" class="sinput">
                    <option :value="false">Nein</option>
                    <option :value="true">Ja</option>
                  </select>
                </label>
                <label>Master ready
                  <select v-model="versionDraft(song.id).is_master_ready" class="sinput">
                    <option :value="false">Nein</option>
                    <option :value="true">Ja</option>
                  </select>
                </label>
                <label>Final
                  <select v-model="versionDraft(song.id).is_final" class="sinput">
                    <option :value="false">Nein</option>
                    <option :value="true">Ja</option>
                  </select>
                </label>
                <label class="full">Notiz
                  <input v-model.trim="versionDraft(song.id).notes" class="sinput" placeholder="z. B. BPM 140, Key Am" />
                </label>
                <label class="full">Audio-Datei (optional)
                  <input
                    type="file"
                    class="sinput"
                    accept="audio/*,.mp3,.wav,.flac,.aac,.ogg,.m4a"
                    @change="onVersionFile(song.id, $event)"
                  />
                </label>
                <label>Dauer (Sekunden)
                  <input v-model.number="versionDraft(song.id).duration_seconds" type="number" min="1" class="sinput" />
                </label>
              </div>
              <div class="form-actions">
                <button class="btn ghost" type="button" @click="openVersionForms[song.id] = false">Abbrechen</button>
                <button class="btn" type="submit" :disabled="saving">Speichern</button>
              </div>
            </form>
          </div>
        </div>
      </article>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { showToast } = useToast();

const loading = ref(false);
const saving = ref(false);
const songs = ref([]);
const showCreateForm = ref(false);
const activeFilter = ref("ALL");
const searchQuery = ref("");
const genreQuery = ref("");
const onlyWithFinal = ref(false);
const openVersionForms = ref({});
const versionDrafts = ref({});
const compareDrafts = ref({});
const currentAudio = ref(null);
const currentAudioKey = ref("");

const newSong = ref({
  title: "",
  description: "",
  status: "ACTIVE",
  genre: "",
  mood: "",
  bpm: null,
  key_signature: "",
  release_date: "",
  tagsInput: "",
});

const filters = [
  { label: "Alle", value: "ALL" },
  { label: "Aktiv", value: "ACTIVE" },
  { label: "Inaktiv", value: "INACTIVE" },
  { label: "Archiviert", value: "ARCHIVED" },
];

const filteredSongs = computed(() => {
  let list = songs.value;
  if (activeFilter.value !== "ALL") {
    list = list.filter((s) => s.status === activeFilter.value);
  }
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(
      (s) =>
        s.title.toLowerCase().includes(q) ||
        (s.description || "").toLowerCase().includes(q) ||
        (s.tags || []).some((tag) => String(tag).toLowerCase().includes(q))
    );
  }
  if (genreQuery.value.trim()) {
    const g = genreQuery.value.toLowerCase();
    list = list.filter((s) => (s.genre || "").toLowerCase().includes(g));
  }
  if (onlyWithFinal.value) {
    list = list.filter((s) => (s.versions || []).some((v) => v.is_final));
  }
  return list;
});

const totalVersions = computed(() => songs.value.reduce((acc, song) => acc + ((song.versions || []).length), 0));
const finalCount = computed(() => songs.value.filter((song) => (song.versions || []).some((v) => v.is_final)).length);
const mixReadyCount = computed(() => songs.value.filter((song) => (song.versions || []).some((v) => v.is_mix_ready)).length);

function statusLabel(status) {
  return { ACTIVE: "Aktiv", INACTIVE: "Inaktiv", ARCHIVED: "Archiviert" }[status] || status;
}

function formatDate(val) {
  if (!val) return "";
  return new Date(val).toLocaleDateString("de-DE", { day: "2-digit", month: "short", year: "numeric" });
}

function versionDraft(songId) {
  if (!versionDrafts.value[songId]) {
    versionDrafts.value[songId] = {
      version_number: 1,
      is_mix_ready: false,
      is_master_ready: false,
      is_final: false,
      notes: "",
      file: null,
      duration_seconds: null,
    };
  }
  return versionDrafts.value[songId];
}

function normalizeTags(text) {
  return (text || "")
    .split(",")
    .map((entry) => entry.trim())
    .filter(Boolean)
    .slice(0, 12);
}

function toggleVersionForm(songId) {
  openVersionForms.value[songId] = !openVersionForms.value[songId];
}

function audioUrl(version) {
  return version?.file_url || version?.file || "";
}

function formatDuration(seconds) {
  if (!seconds || Number.isNaN(Number(seconds))) return "--:--";
  const total = Number(seconds);
  const min = Math.floor(total / 60);
  const sec = total % 60;
  return `${String(min).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

function ensureCompare(songId) {
  if (!compareDrafts.value[songId]) {
    compareDrafts.value[songId] = { A: null, B: null };
  }
  return compareDrafts.value[songId];
}

function assignCompare(songId, slot, versionId) {
  const draft = ensureCompare(songId);
  draft[slot] = versionId;
}

function clearCompare(songId) {
  compareDrafts.value[songId] = { A: null, B: null };
}

function compareVersion(songId, slot) {
  const draft = ensureCompare(songId);
  const versionId = draft[slot];
  const song = songs.value.find((entry) => entry.id === songId);
  return (song?.versions || []).find((entry) => entry.id === versionId) || null;
}

function compareVersionLabel(song, slot) {
  const selected = compareVersion(song.id, slot);
  return selected ? `v${selected.version_number}` : "nicht gewählt";
}

function isPlaying(songId, versionId) {
  return currentAudioKey.value === `${songId}:${versionId}`;
}

function stopAudio() {
  if (currentAudio.value) {
    currentAudio.value.pause();
    currentAudio.value.currentTime = 0;
    currentAudio.value = null;
  }
  currentAudioKey.value = "";
}

async function playVersion(songId, version) {
  const source = audioUrl(version);
  if (!source) {
    showToast("Für diese Version liegt keine Audio-Datei vor", "info");
    return;
  }
  const key = `${songId}:${version.id}`;
  if (currentAudioKey.value === key) {
    stopAudio();
    return;
  }
  stopAudio();
  try {
    const audio = new Audio(source);
    currentAudio.value = audio;
    currentAudioKey.value = key;
    audio.onended = () => {
      if (currentAudioKey.value === key) stopAudio();
    };
    await audio.play();
  } catch (err) {
    console.error(err);
    stopAudio();
    showToast("Audio konnte nicht abgespielt werden", "error");
  }
}

function playCompare(songId, slot) {
  const version = compareVersion(songId, slot);
  if (!version) {
    showToast(`Slot ${slot} ist leer`, "info");
    return;
  }
  playVersion(songId, version);
}

function goHome() {
  router.push({ name: "platforms" });
}

async function loadSongs() {
  loading.value = true;
  try {
    const { data } = await api.get("songs/");
    songs.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error(err);
    showToast("Songs konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function createSong() {
  if (!newSong.value.title.trim()) return;
  saving.value = true;
  try {
    const payload = {
      title: newSong.value.title,
      description: newSong.value.description,
      status: newSong.value.status,
      genre: newSong.value.genre,
      mood: newSong.value.mood,
      bpm: newSong.value.bpm || null,
      key_signature: newSong.value.key_signature,
      release_date: newSong.value.release_date || null,
      tags: normalizeTags(newSong.value.tagsInput),
    };
    const { data } = await api.post("songs/", payload);
    songs.value.unshift({ ...data, versions: [] });
    newSong.value = {
      title: "",
      description: "",
      status: "ACTIVE",
      genre: "",
      mood: "",
      bpm: null,
      key_signature: "",
      release_date: "",
      tagsInput: "",
    };
    showCreateForm.value = false;
    showToast("Song angelegt", "success");
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Song konnte nicht erstellt werden", "error");
  } finally {
    saving.value = false;
  }
}

function onVersionFile(songId, event) {
  const file = event.target.files?.[0] || null;
  if (!file) {
    versionDraft(songId).file = null;
    return;
  }
  if (/\.(js|mjs|cjs|ts|sh|bat|cmd)$/i.test(file.name)) {
    showToast("Nur Audio-Dateien sind erlaubt", "error");
    event.target.value = "";
    versionDraft(songId).file = null;
    return;
  }
  versionDraft(songId).file = file;
}

async function addVersion(songId) {
  const draft = versionDraft(songId);
  saving.value = true;
  try {
    let data;
    if (draft.file) {
      const payload = new FormData();
      payload.append("song", songId);
      payload.append("notes", draft.notes || "");
      payload.append("is_mix_ready", draft.is_mix_ready ? "true" : "false");
      payload.append("is_master_ready", draft.is_master_ready ? "true" : "false");
      payload.append("is_final", draft.is_final ? "true" : "false");
      if (draft.duration_seconds) payload.append("duration_seconds", String(draft.duration_seconds));
      payload.append("file", draft.file, draft.file.name);
      const response = await api.post("song-versions/", payload, { headers: { "Content-Type": "multipart/form-data" } });
      data = response.data;
    } else {
      const response = await api.post("song-versions/", {
        song: songId,
        notes: draft.notes,
        is_mix_ready: draft.is_mix_ready,
        is_master_ready: draft.is_master_ready,
        is_final: draft.is_final,
        duration_seconds: draft.duration_seconds || null,
      });
      data = response.data;
    }
    const song = songs.value.find((s) => s.id === songId);
    if (song) {
      if (!song.versions) song.versions = [];
      if (data.is_final) {
        song.versions = song.versions.map((entry) => ({ ...entry, is_final: false }));
      }
      song.versions.unshift(data);
    }
    versionDrafts.value[songId] = {
      version_number: (draft.version_number || 1) + 1,
      is_mix_ready: false,
      is_master_ready: false,
      is_final: false,
      notes: "",
      file: null,
      duration_seconds: null,
    };
    openVersionForms.value[songId] = false;
    showToast("Version gespeichert", "success");
  } catch (err) {
    console.error(err);
    const payload = err?.response?.data;
    const detail = payload?.detail || payload?.file?.[0] || payload?.non_field_errors?.[0] || "Version konnte nicht gespeichert werden";
    showToast(detail, "error");
  } finally {
    saving.value = false;
  }
}

onMounted(loadSongs);
</script>

<style scoped>
.music-page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

/* Hero */
.music-hero {
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.16) 0%, rgba(14, 165, 233, 0.10) 100%);
  border: 1px solid rgba(14, 165, 233, 0.24);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 11px;
  color: #0ea5e9;
  font-weight: 700;
  margin: 0 0 6px;
}

.music-hero h1 {
  font-size: clamp(1.5rem, 2.8vw, 2.1rem);
  font-weight: 800;
  margin: 0 0 6px;
}

.hero-lead {
  color: var(--muted);
  font-size: 0.95rem;
  margin: 0;
  line-height: 1.5;
  max-width: 520px;
}

.hero-actions {
  display: flex;
  gap: 10px;
  flex-shrink: 0;
}

.stats-grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
}

.stat-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--card);
  padding: 14px;
  display: grid;
  gap: 4px;
}

.stat-card strong {
  font-size: 1.35rem;
  color: var(--brand);
}

.stat-card span {
  color: var(--muted);
  font-size: 0.82rem;
}

/* Create form */
.create-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: var(--shadow-soft);
}

.create-card h3 {
  margin: 0 0 16px;
  font-size: 1rem;
  font-weight: 700;
}

.song-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.song-form label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--muted);
}

.song-form .full {
  grid-column: 1 / -1;
}

/* Filter */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.filter-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.fchip {
  padding: 7px 14px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.18s ease;
}

.fchip.active {
  background: var(--brand);
  border-color: var(--brand);
  color: white;
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 160px;
  max-width: 300px;
}

.mini-filter {
  display: grid;
  gap: 4px;
  font-size: 0.75rem;
  color: var(--muted);
}

.check-inline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.search-ico {
  position: absolute;
  left: 11px;
  top: 50%;
  transform: translateY(-50%);
  width: 15px;
  height: 15px;
  fill: none;
  stroke: var(--muted);
  stroke-width: 2;
  stroke-linecap: round;
  pointer-events: none;
}

.search-input {
  padding-left: 34px !important;
}

/* Songs grid */
.songs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 16px;
}

.song-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  display: flex;
  flex-direction: column;
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}

.song-card:hover {
  box-shadow: var(--shadow-strong);
  border-color: color-mix(in srgb, var(--brand) 40%, var(--border) 60%);
}

.song-top {
  padding: 18px 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.song-main h3 {
  margin: 4px 0 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.song-attrs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.song-desc {
  color: var(--muted);
  font-size: 0.88rem;
  margin: 4px 0 0;
  line-height: 1.4;
}

.song-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: 6px;
}

.meta-pill {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--muted);
}

.meta-date {
  font-size: 0.78rem;
  color: var(--muted);
}

.song-status-badge {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.badge-active { background: color-mix(in srgb, #10b981 16%, transparent); color: #059669; }
.badge-inactive { background: color-mix(in srgb, #f59e0b 16%, transparent); color: #d97706; }
.badge-archived { background: color-mix(in srgb, #94a3b8 16%, transparent); color: #64748b; }

/* Versions */
.version-list {
  border-top: 1px solid var(--border);
  padding: 10px 18px;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.version-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.version-actions {
  display: inline-flex;
  gap: 6px;
}

.version-duration {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 600;
}

.version-num {
  font-size: 0.78rem;
  font-weight: 800;
  color: var(--brand);
  min-width: 24px;
}

.version-flags {
  display: flex;
  gap: 6px;
}

.vflag {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--muted);
  transition: all 0.15s ease;
}

.vflag.active {
  background: color-mix(in srgb, #10b981 16%, var(--surface) 84%);
  border-color: color-mix(in srgb, #10b981 40%, var(--border) 60%);
  color: #059669;
}

.version-notes {
  font-size: 0.78rem;
  color: var(--muted);
  font-style: italic;
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-link {
  font-size: 0.76rem;
  color: var(--brand);
  text-decoration: none;
  font-weight: 600;
}

.ab-panel {
  margin-top: 8px;
  border-top: 1px dashed var(--border);
  padding-top: 10px;
  display: grid;
  gap: 8px;
}

.ab-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ab-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.ab-slot {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px;
  display: grid;
  gap: 6px;
  background: color-mix(in srgb, var(--card) 84%, transparent);
}

.slot-label {
  font-size: 0.72rem;
  font-weight: 800;
  color: var(--brand);
}

.slot-value {
  font-size: 0.8rem;
  color: var(--muted);
}

/* Add version */
.add-version {
  border-top: 1px solid var(--border);
}

.add-version-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 11px 18px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--brand);
  font-size: 0.85rem;
  font-weight: 600;
  text-align: left;
}

.add-version-toggle:hover {
  background: color-mix(in srgb, var(--brand) 6%, transparent 94%);
}

.add-version-toggle svg {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
}

.version-form {
  padding: 0 18px 16px;
}

.version-form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.version-form-grid label,
.version-form-grid .full {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
}

.version-form-grid .full {
  grid-column: 1 / -1;
}

/* Shared inputs */
.sinput {
  width: 100%;
  padding: 9px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
  font-size: 0.9rem;
  font-family: inherit;
}

.sinput:focus {
  outline: none;
  border-color: var(--brand);
  box-shadow: 0 0 0 3px var(--ring);
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.form-actions.full {
  grid-column: 1 / -1;
}

/* States */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
  padding: 60px 24px;
  color: var(--muted);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border);
  border-top-color: var(--brand);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 60px 24px;
  color: var(--muted);
  text-align: center;
}

.empty-ico { font-size: 3rem; }

@media (max-width: 640px) {
  .songs-grid { grid-template-columns: 1fr; }
  .music-hero { flex-direction: column; align-items: flex-start; }
  .filter-bar { flex-direction: column; align-items: flex-start; }
  .search-wrap { max-width: 100%; width: 100%; }
  .ab-grid { grid-template-columns: 1fr; }
}
</style>
