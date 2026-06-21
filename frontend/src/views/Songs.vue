<template>
  <div class="music-library">
    <header class="lib-header">
      <div>
        <h1>Musik Bibliothek</h1>
        <p class="muted">Beats, Demos, Versionen, Alben – alles an einem Ort.</p>
      </div>
      <div class="header-actions">
        <button class="btn ghost" @click="activeTab = 'songs'" :class="{ active: activeTab === 'songs' }">Songs</button>
        <button class="btn ghost" @click="activeTab = 'albums'" :class="{ active: activeTab === 'albums' }">Alben</button>
        <button class="btn" @click="showUploadSong = true">+ Song anlegen</button>
      </div>
    </header>

    <!-- SONGS TAB -->
    <template v-if="activeTab === 'songs'">
      <section class="filter-bar">
        <input class="input search" v-model.trim="search" placeholder="Titel, Genre, Stimmung…" @input="onSearchInput" />
        <select class="input" v-model="filterStatus" @change="loadSongs(true)">
          <option value="ALL">Alle Status</option>
          <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
        </select>
        <select class="input" v-model="sort" @change="loadSongs(true)">
          <option value="-created_at">Neueste zuerst</option>
          <option value="created_at">Älteste zuerst</option>
          <option value="title">Titel A–Z</option>
          <option value="-title">Titel Z–A</option>
        </select>
      </section>

      <section class="song-grid" v-if="songs.length">
        <article
          v-for="song in songs"
          :key="`song-${song.id}`"
          class="song-card"
          :class="{ expanded: expandedSong === song.id }"
        >
          <div class="song-cover-area" @click="toggleExpand(song.id)">
            <img v-if="song.cover_url" :src="song.cover_url" :alt="song.title" class="song-cover" />
            <div v-else class="song-cover-placeholder"><span>🎵</span></div>
            <div class="song-cover-overlay">
              <span class="pill" :data-status="song.status">{{ statusLabels[song.status] || song.status }}</span>
            </div>
          </div>

          <div class="song-info">
            <div class="song-meta" @click="toggleExpand(song.id)">
              <h3>{{ song.title }}</h3>
              <p class="muted small">{{ song.description || "Keine Beschreibung" }}</p>
              <div class="meta-tags">
                <span v-if="song.genre" class="tag">{{ song.genre }}</span>
                <span v-if="song.mood" class="tag">{{ song.mood }}</span>
                <span v-if="song.bpm" class="tag">{{ song.bpm }} BPM</span>
              </div>
            </div>
            <div class="song-quick-actions">
              <label class="icon-btn cover-lbl" title="Cover hochladen">
                <input type="file" accept="image/*" @change="uploadCover(song.id, $event)" class="hidden-input" />
                🖼
              </label>
              <button class="icon-btn" @click="toggleExpand(song.id)">{{ expandedSong === song.id ? '▲' : '▼' }}</button>
            </div>
          </div>

          <div v-if="expandedSong === song.id" class="versions-panel">
            <div class="versions-list" v-if="versions[song.id]?.length">
              <article v-for="v in versions[song.id]" :key="`v-${v.id}`" class="version-row">
                <div class="version-left">
                  <span class="vtype-badge" :data-type="v.version_type">{{ versionTypeLabel(v.version_type) }}</span>
                  <div>
                    <strong>v{{ v.version_number }}</strong>
                    <span class="tags-inline">
                      <span v-if="v.is_mix_ready" class="tag small">Mix</span>
                      <span v-if="v.is_master_ready" class="tag small">Master</span>
                      <span v-if="v.is_final" class="tag small final">Final</span>
                    </span>
                    <p class="muted small">{{ v.notes || "" }}</p>
                    <small class="muted">{{ formatDate(v.created_at) }}</small>
                  </div>
                </div>
                <div class="version-right">
                  <a
                    v-if="v.file_url"
                    :href="v.file_url"
                    :download="v.file_name || `${song.title}-v${v.version_number}`"
                    class="btn ghost small"
                  >⬇ Download</a>
                  <span v-if="v.duration_seconds" class="muted small">{{ formatDuration(v.duration_seconds) }}</span>
                </div>
              </article>
            </div>
            <p v-else class="muted small">Noch keine Versionen.</p>

            <form class="version-upload-form" @submit.prevent="uploadVersion(song.id)">
              <h4>Neue Version hochladen</h4>
              <div class="upload-grid">
                <select class="input" v-model="versionDraft(song.id).version_type">
                  <option v-for="t in versionTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
                <input class="input" v-model.trim="versionDraft(song.id).notes" placeholder="Notiz (optional)" />
              </div>
              <label class="file-drop-zone" :class="{ 'has-file': versionDraft(song.id).file }">
                <input type="file" accept="audio/*,.mp3,.wav,.flac,.aac,.ogg,.m4a,.opus" @change="onAudioFile(song.id, $event)" class="hidden-input" />
                <span v-if="versionDraft(song.id).file">✓ {{ versionDraft(song.id).file.name }} ({{ formatFileSize(versionDraft(song.id).file.size) }})</span>
                <span v-else>🎵 Audio-Datei wählen (mp3, wav, flac, aac, ogg, m4a, opus)</span>
              </label>
              <div class="flags">
                <label><input type="checkbox" v-model="versionDraft(song.id).is_mix_ready" /> Mix</label>
                <label><input type="checkbox" v-model="versionDraft(song.id).is_master_ready" /> Master</label>
                <label><input type="checkbox" v-model="versionDraft(song.id).is_final" /> Final</label>
              </div>
              <div class="upload-progress-row" v-if="uploadProgress[song.id] !== undefined">
                <div class="progress-track"><div class="progress-fill" :style="{ width: uploadProgress[song.id] + '%' }"></div></div>
                <span>{{ uploadProgress[song.id] }}%</span>
              </div>
              <button class="btn" type="submit" :disabled="uploading[song.id] || !versionDraft(song.id).file">
                {{ uploading[song.id] ? "Lädt hoch…" : "Version hochladen" }}
              </button>
            </form>
          </div>
        </article>
      </section>

      <div v-if="loading" class="empty-state">Lade Songs…</div>
      <div v-else-if="!songs.length" class="empty-state">
        <span>🎵</span>
        <p>Noch keine Songs. Lege deinen ersten Song an!</p>
      </div>

      <div class="pagination" v-if="pageCount > 1">
        <button class="btn ghost small" :disabled="page === 1" @click="changePage(-1)">← Zurück</button>
        <span>{{ page }} / {{ pageCount }}</span>
        <button class="btn ghost small" :disabled="page === pageCount" @click="changePage(1)">Weiter →</button>
      </div>
    </template>

    <!-- ALBUMS TAB -->
    <template v-if="activeTab === 'albums'">
      <div class="albums-toolbar">
        <input class="input search" v-model.trim="albumSearch" placeholder="Album suchen…" @input="loadAlbums" />
        <button class="btn" @click="showCreateAlbum = true">+ Album erstellen</button>
      </div>

      <div class="album-grid" v-if="albums.length">
        <article v-for="album in albums" :key="`album-${album.id}`" class="album-card" @click="openAlbum(album)">
          <div class="album-cover-area">
            <img v-if="album.cover_url" :src="album.cover_url" :alt="album.title" class="album-cover" />
            <div v-else class="album-cover-placeholder">💿</div>
          </div>
          <div class="album-info">
            <h3>{{ album.title }}</h3>
            <p class="muted small">{{ album.song_count }} Songs</p>
          </div>
        </article>
      </div>
      <div v-else-if="!loadingAlbums" class="empty-state">
        <span>💿</span>
        <p>Noch keine Alben.</p>
      </div>
    </template>

    <!-- ALBUM DETAIL MODAL -->
    <div v-if="selectedAlbum" class="modal-overlay" @click.self="selectedAlbum = null">
      <article class="modal-card album-modal">
        <header class="modal-header">
          <div class="album-header-left">
            <label class="icon-btn cover-lbl" title="Album-Cover ändern">
              <input type="file" accept="image/*" @change="uploadAlbumCover(selectedAlbum.id, $event)" class="hidden-input" />
              <img v-if="selectedAlbum.cover_url" :src="selectedAlbum.cover_url" class="album-modal-cover" />
              <div v-else class="album-modal-cover-ph">💿</div>
            </label>
            <div><h2>{{ selectedAlbum.title }}</h2><p class="muted">{{ selectedAlbum.description }}</p></div>
          </div>
          <button class="btn ghost small" @click="selectedAlbum = null">✕</button>
        </header>

        <div class="modal-content">
          <div class="album-songs-list">
            <p class="muted small" v-if="!albumSongs.length">Keine Songs in diesem Album.</p>
            <article v-for="song in albumSongs" :key="`as-${song.id}`" class="album-song-row">
              <img v-if="song.cover_url" :src="song.cover_url" class="mini-cover" />
              <div v-else class="mini-cover-ph">🎵</div>
              <div class="flex1">
                <strong>{{ song.title }}</strong>
                <small class="muted"> · {{ song.versions?.length || 0 }} Versionen</small>
              </div>
              <button class="btn ghost small" @click="removeSongFromAlbum(selectedAlbum, song.id)">Entfernen</button>
            </article>
          </div>
          <div class="add-song-section">
            <select class="input" v-model="addSongId">
              <option value="">Song hinzufügen…</option>
              <option v-for="song in songsNotInAlbum" :key="`add-${song.id}`" :value="song.id">{{ song.title }}</option>
            </select>
            <button class="btn" :disabled="!addSongId" @click="addSongToAlbum(selectedAlbum)">Hinzufügen</button>
          </div>
        </div>
      </article>
    </div>

    <!-- CREATE SONG MODAL -->
    <div v-if="showUploadSong" class="modal-overlay" @click.self="showUploadSong = false">
      <article class="modal-card">
        <header class="modal-header">
          <h2>Song anlegen</h2>
          <button class="btn ghost small" @click="showUploadSong = false">✕</button>
        </header>
        <div class="modal-content">
          <div class="form-grid">
            <label>Titel *<input class="input" v-model.trim="songForm.title" placeholder="Songtitel" /></label>
            <label>Beschreibung<input class="input" v-model.trim="songForm.description" placeholder="Beschreibung" /></label>
            <label>Genre<input class="input" v-model.trim="songForm.genre" placeholder="z.B. Hip-Hop, R&B" /></label>
            <label>Stimmung<input class="input" v-model.trim="songForm.mood" placeholder="z.B. energetisch" /></label>
            <label>BPM<input class="input" type="number" v-model.number="songForm.bpm" min="40" max="260" placeholder="z.B. 140" /></label>
            <label>Tonart<input class="input" v-model.trim="songForm.key_signature" placeholder="z.B. Cmaj" /></label>
            <label>Status
              <select class="input" v-model="songForm.status">
                <option v-for="s in statusOptions" :key="s" :value="s">{{ statusLabels[s] }}</option>
              </select>
            </label>
            <label v-if="isTeam">Projekt (optional)
              <select class="input" v-model="songForm.project">
                <option value="">Kein Projekt</option>
                <option v-for="p in projects" :key="p.id" :value="p.id">{{ p.title }}</option>
              </select>
            </label>
          </div>
          <label class="file-drop-zone" style="margin-top: 12px;" :class="{ 'has-file': songForm.coverFile }">
            <input type="file" accept="image/*" @change="onSongCover" class="hidden-input" />
            <span v-if="songForm.coverFile">🖼 {{ songForm.coverFile.name }}</span>
            <span v-else>🖼 Cover hochladen (optional)</span>
          </label>
          <button class="btn" style="margin-top: 12px;" :disabled="creating" @click="createSong">
            {{ creating ? "Speichere…" : "Song anlegen" }}
          </button>
        </div>
      </article>
    </div>

    <!-- CREATE ALBUM MODAL -->
    <div v-if="showCreateAlbum" class="modal-overlay" @click.self="showCreateAlbum = false">
      <article class="modal-card">
        <header class="modal-header">
          <h2>Album erstellen</h2>
          <button class="btn ghost small" @click="showCreateAlbum = false">✕</button>
        </header>
        <div class="modal-content">
          <div class="form-grid">
            <label>Titel *<input class="input" v-model.trim="albumForm.title" placeholder="Albumtitel" /></label>
            <label>Beschreibung<input class="input" v-model.trim="albumForm.description" placeholder="Beschreibung" /></label>
            <label>Veröffentlichungsdatum<input class="input" type="date" v-model="albumForm.release_date" /></label>
          </div>
          <label class="file-drop-zone" style="margin-top: 12px;" :class="{ 'has-file': albumForm.coverFile }">
            <input type="file" accept="image/*" @change="onAlbumCover" class="hidden-input" />
            <span v-if="albumForm.coverFile">🖼 {{ albumForm.coverFile.name }}</span>
            <span v-else>🖼 Album-Cover hochladen (optional)</span>
          </label>
          <button class="btn" style="margin-top: 12px;" :disabled="creatingAlbum" @click="createAlbum">
            {{ creatingAlbum ? "Erstelle…" : "Album erstellen" }}
          </button>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const AUDIO_EXT = /\.(mp3|wav|flac|aac|ogg|m4a|opus|wma|aiff|aif)$/i;
const AUDIO_MIME = /^audio\//;

const versionTypes = [
  { value: "BEAT", label: "Beat" },
  { value: "DEMO", label: "Demo" },
  { value: "DRAFT", label: "Draft" },
  { value: "ACOUSTIC", label: "Acoustic" },
  { value: "INSTRUMENTAL", label: "Instrumental" },
  { value: "MIX", label: "Mix" },
  { value: "MASTER", label: "Master" },
  { value: "FINAL", label: "Final" },
];

const statusOptions = ["ACTIVE", "INACTIVE", "ARCHIVED"];
const statusLabels = { ACTIVE: "Aktiv", INACTIVE: "Inaktiv", ARCHIVED: "Archiviert" };

const activeTab = ref("songs");
const songs = ref([]);
const allSongs = ref([]);
const albums = ref([]);
const versions = ref({});
const projects = ref([]);
const expandedSong = ref(null);
const selectedAlbum = ref(null);
const albumSongs = ref([]);
const addSongId = ref("");

const loading = ref(false);
const loadingAlbums = ref(false);
const creating = ref(false);
const creatingAlbum = ref(false);
const uploading = ref({});
const uploadProgress = ref({});

const search = ref("");
const filterStatus = ref("ALL");
const sort = ref("-created_at");
const page = ref(1);
const PAGE_SIZE = 12;
const total = ref(0);
const albumSearch = ref("");

const showUploadSong = ref(false);
const showCreateAlbum = ref(false);
const drafts = ref({});

const songForm = ref({ title: "", description: "", genre: "", mood: "", bpm: null, key_signature: "", status: "ACTIVE", project: "", coverFile: null });
const albumForm = ref({ title: "", description: "", release_date: "", coverFile: null });

const pageCount = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)));

const songsNotInAlbum = computed(() => {
  if (!selectedAlbum.value) return allSongs.value;
  const inAlbum = new Set((selectedAlbum.value.songs || []).map(Number));
  return allSongs.value.filter((s) => !inAlbum.has(Number(s.id)));
});

function versionDraft(songId) {
  if (!drafts.value[songId]) {
    drafts.value[songId] = { notes: "", file: null, version_type: "DEMO", is_mix_ready: false, is_master_ready: false, is_final: false };
  }
  return drafts.value[songId];
}

function versionTypeLabel(type) {
  return versionTypes.find((t) => t.value === type)?.label || type || "Demo";
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "short", timeStyle: "short" }).format(new Date(value));
}

function formatDuration(seconds) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, "0")}`;
}

function formatFileSize(bytes) {
  if (!bytes) return "";
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function asList(data) {
  return Array.isArray(data) ? data : data?.results || [];
}

function toggleExpand(songId) {
  expandedSong.value = expandedSong.value === songId ? null : songId;
  if (expandedSong.value === songId) ensureVersions(songId);
}

function validateAudioFile(file) {
  if (!file) return "Keine Datei ausgewählt.";
  const mimeOk = AUDIO_MIME.test(file.type);
  const extOk = AUDIO_EXT.test(file.name);
  if (!mimeOk && !extOk) return `"${file.name}" ist keine gültige Audio-Datei. Erlaubt: mp3, wav, flac, aac, ogg, m4a, opus.`;
  if (file.size > 300 * 1024 * 1024) return `Datei ist zu groß (max. 300 MB). Aktuell: ${formatFileSize(file.size)}.`;
  return null;
}

function onAudioFile(songId, event) {
  const file = event.target.files?.[0] || null;
  event.target.value = "";
  if (!file) { versionDraft(songId).file = null; return; }
  const err = validateAudioFile(file);
  if (err) { showToast(err, "error"); versionDraft(songId).file = null; return; }
  versionDraft(songId).file = file;
}

function onSongCover(event) { songForm.value.coverFile = event.target.files?.[0] || null; event.target.value = ""; }
function onAlbumCover(event) { albumForm.value.coverFile = event.target.files?.[0] || null; event.target.value = ""; }

let searchTimer = null;
function onSearchInput() {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(() => loadSongs(true), 350);
}

async function loadProjects() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("projects/", { params: { page_size: 100 } });
    projects.value = asList(data);
  } catch { projects.value = []; }
}

async function loadSongs(resetPage = false) {
  if (resetPage) page.value = 1;
  loading.value = true;
  try {
    const params = { page: page.value, page_size: PAGE_SIZE, ordering: sort.value };
    if (filterStatus.value !== "ALL") params.status = filterStatus.value;
    if (search.value) params.search = search.value;
    const { data } = await api.get("songs/", { params });
    const items = asList(data);
    songs.value = items;
    total.value = data?.count || items.length;
  } catch (err) {
    console.error(err);
    songs.value = [];
    total.value = 0;
  } finally {
    loading.value = false;
  }
}

async function loadAllSongs() {
  try {
    const { data } = await api.get("songs/", { params: { page_size: 200, ordering: "title" } });
    allSongs.value = asList(data);
  } catch { allSongs.value = []; }
}

async function ensureVersions(songId, force = false) {
  if (!force && versions.value[songId]) return;
  try {
    const { data } = await api.get("song-versions/", { params: { song: songId, ordering: "-version_number", page_size: 50 } });
    versions.value = { ...versions.value, [songId]: asList(data) };
  } catch { console.error("Versions konnte nicht geladen werden"); }
}

async function loadAlbums() {
  loadingAlbums.value = true;
  try {
    const params = { page_size: 50, ordering: "-created_at" };
    if (albumSearch.value) params.search = albumSearch.value;
    const { data } = await api.get("albums/", { params });
    albums.value = asList(data);
  } catch { albums.value = []; } finally { loadingAlbums.value = false; }
}

async function createSong() {
  if (!songForm.value.title.trim()) { showToast("Titel ist erforderlich", "error"); return; }
  creating.value = true;
  try {
    const fd = new FormData();
    fd.append("title", songForm.value.title);
    if (songForm.value.description) fd.append("description", songForm.value.description);
    if (songForm.value.genre) fd.append("genre", songForm.value.genre);
    if (songForm.value.mood) fd.append("mood", songForm.value.mood);
    if (songForm.value.bpm) fd.append("bpm", songForm.value.bpm);
    if (songForm.value.key_signature) fd.append("key_signature", songForm.value.key_signature);
    fd.append("status", songForm.value.status);
    if (songForm.value.project) fd.append("project", songForm.value.project);
    if (songForm.value.coverFile) fd.append("cover", songForm.value.coverFile);
    await api.post("songs/", fd, { headers: { "Content-Type": "multipart/form-data" } });
    songForm.value = { title: "", description: "", genre: "", mood: "", bpm: null, key_signature: "", status: "ACTIVE", project: "", coverFile: null };
    showUploadSong.value = false;
    showToast("Song angelegt", "success");
    await Promise.all([loadSongs(true), loadAllSongs()]);
  } catch (err) {
    showToast(err?.response?.data?.detail || "Fehler beim Speichern", "error");
  } finally { creating.value = false; }
}

async function uploadVersion(songId) {
  const draft = versionDraft(songId);
  if (!draft.file) { showToast("Bitte zuerst eine Audio-Datei wählen", "error"); return; }
  uploading.value = { ...uploading.value, [songId]: true };
  uploadProgress.value = { ...uploadProgress.value, [songId]: 0 };
  try {
    const fd = new FormData();
    fd.append("song", songId);
    fd.append("file", draft.file);
    fd.append("notes", draft.notes || "");
    fd.append("version_type", draft.version_type || "DEMO");
    fd.append("is_mix_ready", draft.is_mix_ready ? "1" : "0");
    fd.append("is_master_ready", draft.is_master_ready ? "1" : "0");
    fd.append("is_final", draft.is_final ? "1" : "0");
    await api.post("song-versions/", fd, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress: (e) => {
        if (e.total) uploadProgress.value = { ...uploadProgress.value, [songId]: Math.round((e.loaded / e.total) * 100) };
      },
    });
    drafts.value[songId] = { notes: "", file: null, version_type: "DEMO", is_mix_ready: false, is_master_ready: false, is_final: false };
    showToast("Version hochgeladen!", "success");
    await ensureVersions(songId, true);
  } catch (err) {
    const detail = err?.response?.data?.file?.[0] || err?.response?.data?.detail || "Upload fehlgeschlagen";
    showToast(detail, "error");
  } finally {
    uploading.value = { ...uploading.value, [songId]: false };
    const next = { ...uploadProgress.value };
    delete next[songId];
    uploadProgress.value = next;
  }
}

async function uploadCover(songId, event) {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) return;
  try {
    const fd = new FormData();
    fd.append("cover", file);
    const { data } = await api.patch(`songs/${songId}/`, fd, { headers: { "Content-Type": "multipart/form-data" } });
    songs.value = songs.value.map((s) => s.id === songId ? { ...s, cover_url: data.cover_url } : s);
    showToast("Cover aktualisiert", "success");
  } catch { showToast("Cover-Upload fehlgeschlagen", "error"); }
}

async function uploadAlbumCover(albumId, event) {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file) return;
  try {
    const fd = new FormData();
    fd.append("cover", file);
    const { data } = await api.patch(`albums/${albumId}/`, fd, { headers: { "Content-Type": "multipart/form-data" } });
    selectedAlbum.value = { ...selectedAlbum.value, cover_url: data.cover_url };
    albums.value = albums.value.map((a) => a.id === albumId ? { ...a, cover_url: data.cover_url } : a);
    showToast("Album-Cover aktualisiert", "success");
  } catch { showToast("Cover-Upload fehlgeschlagen", "error"); }
}

async function createAlbum() {
  if (!albumForm.value.title.trim()) { showToast("Albumtitel erforderlich", "error"); return; }
  creatingAlbum.value = true;
  try {
    const fd = new FormData();
    fd.append("title", albumForm.value.title);
    if (albumForm.value.description) fd.append("description", albumForm.value.description);
    if (albumForm.value.release_date) fd.append("release_date", albumForm.value.release_date);
    if (albumForm.value.coverFile) fd.append("cover", albumForm.value.coverFile);
    await api.post("albums/", fd, { headers: { "Content-Type": "multipart/form-data" } });
    albumForm.value = { title: "", description: "", release_date: "", coverFile: null };
    showCreateAlbum.value = false;
    showToast("Album erstellt", "success");
    await loadAlbums();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Album-Erstellung fehlgeschlagen", "error");
  } finally { creatingAlbum.value = false; }
}

async function openAlbum(album) {
  selectedAlbum.value = album;
  addSongId.value = "";
  const songIds = (album.songs || []).map(Number);
  if (songIds.length) {
    albumSongs.value = allSongs.value.filter((s) => songIds.includes(Number(s.id)));
    if (!albumSongs.value.length) {
      await loadAllSongs();
      albumSongs.value = allSongs.value.filter((s) => songIds.includes(Number(s.id)));
    }
  } else {
    albumSongs.value = [];
  }
}

async function addSongToAlbum(album) {
  if (!addSongId.value) return;
  const current = (album.songs || []).map(Number);
  const updated = [...new Set([...current, Number(addSongId.value)])];
  try {
    const { data } = await api.patch(`albums/${album.id}/`, { songs: updated });
    selectedAlbum.value = { ...album, songs: data.songs };
    albums.value = albums.value.map((a) => a.id === album.id ? { ...a, song_count: updated.length } : a);
    addSongId.value = "";
    await openAlbum(selectedAlbum.value);
    showToast("Song hinzugefügt", "success");
  } catch { showToast("Fehler beim Hinzufügen", "error"); }
}

async function removeSongFromAlbum(album, songId) {
  const current = (album.songs || []).map(Number);
  const updated = current.filter((id) => id !== Number(songId));
  try {
    const { data } = await api.patch(`albums/${album.id}/`, { songs: updated });
    selectedAlbum.value = { ...album, songs: data.songs };
    albumSongs.value = albumSongs.value.filter((s) => Number(s.id) !== Number(songId));
    albums.value = albums.value.map((a) => a.id === album.id ? { ...a, song_count: updated.length } : a);
    showToast("Song entfernt", "success");
  } catch { showToast("Fehler beim Entfernen", "error"); }
}

function changePage(delta) {
  const next = page.value + delta;
  if (next < 1 || next > pageCount.value) return;
  page.value = next;
  loadSongs();
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProjects(), loadSongs(), loadAllSongs(), loadAlbums()]);
});
</script>

<style scoped>
.music-library {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.lib-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.lib-header h1 { margin: 0; }

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-bar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}
.filter-bar .search { flex: 1; min-width: 200px; }

.song-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 16px;
}

.song-card {
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255,255,255,0.03);
  transition: box-shadow 0.2s;
}
.song-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.25); }
.song-card.expanded { border-color: rgba(99,179,237,0.35); }

.song-cover-area {
  position: relative;
  aspect-ratio: 1;
  cursor: pointer;
  overflow: hidden;
}
.song-cover { width: 100%; height: 100%; object-fit: cover; display: block; }
.song-cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
  background: linear-gradient(135deg, rgba(99,179,237,0.1), rgba(255,77,109,0.08));
}
.song-cover-overlay { position: absolute; bottom: 8px; left: 8px; }

.song-info {
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}
.song-meta { flex: 1; cursor: pointer; }
.song-meta h3 { margin: 0 0 3px; font-size: 0.95rem; }
.meta-tags { display: flex; flex-wrap: wrap; gap: 4px; margin-top: 5px; }
.song-quick-actions { display: flex; gap: 6px; align-items: center; }

.versions-panel {
  border-top: 1px solid rgba(255,255,255,0.08);
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.versions-list { display: flex; flex-direction: column; gap: 8px; }

.version-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  padding: 10px;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 8px;
  background: rgba(255,255,255,0.02);
}
.version-left { display: flex; gap: 10px; align-items: flex-start; min-width: 0; }
.version-right { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; white-space: nowrap; }

.vtype-badge {
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  border: 1px solid rgba(99,179,237,0.3);
  background: rgba(99,179,237,0.12);
  color: #63b3ed;
  white-space: nowrap;
  flex-shrink: 0;
}
.vtype-badge[data-type="BEAT"] { background: rgba(246,173,85,0.12); border-color: rgba(246,173,85,0.3); color: #f6ad55; }
.vtype-badge[data-type="DEMO"] { background: rgba(154,205,50,0.12); border-color: rgba(154,205,50,0.3); color: #9acd32; }
.vtype-badge[data-type="DRAFT"] { background: rgba(160,174,192,0.12); border-color: rgba(160,174,192,0.3); color: #a0aec0; }
.vtype-badge[data-type="FINAL"] { background: rgba(72,187,120,0.15); border-color: rgba(72,187,120,0.4); color: #48bb78; }
.vtype-badge[data-type="MASTER"] { background: rgba(255,77,109,0.12); border-color: rgba(255,77,109,0.3); color: #ff4d6d; }
.vtype-badge[data-type="INSTRUMENTAL"] { background: rgba(159,122,234,0.12); border-color: rgba(159,122,234,0.3); color: #9f7aea; }

.tags-inline { display: inline-flex; gap: 4px; margin-left: 6px; }

.version-upload-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid rgba(255,255,255,0.07);
}
.version-upload-form h4 { margin: 0; font-size: 0.9rem; }

.upload-grid {
  display: grid;
  grid-template-columns: 160px 1fr;
  gap: 8px;
}

.file-drop-zone {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 50px;
  border: 1.5px dashed rgba(255,255,255,0.18);
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
  cursor: pointer;
  font-size: 0.83rem;
  color: rgba(255,255,255,0.5);
  transition: border-color 0.2s, color 0.2s;
}
.file-drop-zone:hover { border-color: rgba(99,179,237,0.5); color: #63b3ed; }
.file-drop-zone.has-file { border-color: rgba(72,187,120,0.5); color: #48bb78; }

.flags { display: flex; gap: 16px; font-size: 0.85rem; }

.upload-progress-row { display: flex; align-items: center; gap: 10px; }
.progress-track { flex: 1; height: 6px; background: rgba(255,255,255,0.1); border-radius: 3px; overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, #63b3ed, #48bb78); border-radius: 3px; transition: width 0.3s; }

/* ALBUMS */
.albums-toolbar { display: flex; gap: 12px; align-items: center; }
.albums-toolbar .search { flex: 1; max-width: 400px; }

.album-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 14px;
}

.album-card {
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 10px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  background: rgba(255,255,255,0.03);
}
.album-card:hover { border-color: rgba(99,179,237,0.35); transform: translateY(-3px); }
.album-cover-area { aspect-ratio: 1; overflow: hidden; }
.album-cover { width: 100%; height: 100%; object-fit: cover; }
.album-cover-placeholder {
  width: 100%; height: 100%;
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem;
  background: linear-gradient(135deg, rgba(99,179,237,0.08), rgba(255,77,109,0.06));
}
.album-info { padding: 8px 10px; }
.album-info h3 { margin: 0 0 2px; font-size: 0.88rem; }

/* MODALS */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.72);
  display: flex; align-items: center; justify-content: center;
  z-index: 1000;
}
.modal-card {
  background: #0f172a;
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 14px;
  max-width: 640px;
  max-height: 86vh;
  overflow-y: auto;
  width: 94%;
}
.album-modal { max-width: 680px; }

.modal-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 18px 20px;
  border-bottom: 1px solid rgba(255,255,255,0.09);
}
.album-header-left { display: flex; gap: 14px; align-items: center; }
.album-modal-cover { width: 72px; height: 72px; border-radius: 8px; object-fit: cover; cursor: pointer; }
.album-modal-cover-ph {
  width: 72px; height: 72px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.07); font-size: 2rem; cursor: pointer;
}
.modal-content { padding: 18px; display: flex; flex-direction: column; gap: 14px; }

.album-songs-list { display: flex; flex-direction: column; gap: 8px; }
.album-song-row {
  display: flex; align-items: center; gap: 10px;
  padding: 8px 10px;
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 8px;
}
.mini-cover { width: 36px; height: 36px; border-radius: 4px; object-fit: cover; }
.mini-cover-ph {
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  background: rgba(255,255,255,0.06); border-radius: 4px; font-size: 1rem;
}
.flex1 { flex: 1; }
.add-song-section { display: flex; gap: 8px; align-items: center; }
.add-song-section select { flex: 1; }

/* SHARED */
.hidden-input { display: none !important; }

.icon-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 6px;
  color: inherit;
  cursor: pointer;
  padding: 5px 9px;
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.cover-lbl { padding: 5px 9px; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.form-grid label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; }

.empty-state { text-align: center; padding: 60px 20px; color: rgba(255,255,255,0.38); }
.empty-state span { font-size: 3rem; display: block; margin-bottom: 10px; }

.pagination { display: flex; justify-content: center; align-items: center; gap: 16px; }

.tag, .tag.small {
  display: inline-flex;
  padding: 2px 7px;
  background: rgba(255,255,255,0.09);
  border-radius: 4px;
  font-size: 0.68rem;
}
.tag.final { background: rgba(72,187,120,0.18); color: #48bb78; }

.pill { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.68rem; background: rgba(255,255,255,0.1); }
.pill[data-status="ACTIVE"] { background: rgba(59,130,246,0.18); color: #93c5fd; }
.pill[data-status="ARCHIVED"] { background: rgba(148,163,184,0.14); color: #94a3b8; }
.pill[data-status="INACTIVE"] { background: rgba(234,179,8,0.14); color: #fbbf24; }

.muted { color: rgba(255,255,255,0.48); }
.small { font-size: 0.8rem; }

.input {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.14);
  border-radius: 8px;
  color: inherit;
  padding: 8px 12px;
  font-size: 0.9rem;
  width: 100%;
  box-sizing: border-box;
}
.input:focus { outline: none; border-color: rgba(99,179,237,0.45); }

.btn {
  border: 1px solid rgba(255,255,255,0.16);
  border-radius: 8px;
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  color: #fff;
  font-weight: 600;
  padding: 8px 14px;
  cursor: pointer;
  white-space: nowrap;
  transition: opacity 0.15s, transform 0.15s;
}
.btn:hover:not(:disabled) { transform: translateY(-1px); opacity: 0.9; }
.btn:disabled { opacity: 0.42; cursor: not-allowed; }
.btn.ghost {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.18);
  color: rgba(255,255,255,0.68);
}
.btn.ghost.active {
  background: rgba(99,179,237,0.13);
  border-color: rgba(99,179,237,0.38);
  color: #63b3ed;
}
.btn.small, .btn.ghost.small { padding: 5px 10px; font-size: 0.8rem; }
</style>
