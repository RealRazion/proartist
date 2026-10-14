<template>
  <div class="music-player-view">
    <!-- Top Showcase Banner / Spotlight Track -->
    <header class="spotlight-hero card">
      <div class="spotlight-visual">
        <div class="vinyl-art-wrapper" :class="{ spinning: isPlaying }">
          <div class="vinyl-disc">
            <div class="vinyl-center">
              <span class="vinyl-brand">UNYQ</span>
            </div>
          </div>
        </div>
        <div class="exclusive-badge">
          <span class="flame">🔥</span>
          <span>SPOTLIGHT DROP</span>
        </div>
      </div>

      <div class="spotlight-info">
        <div class="spotlight-tag-row">
          <span class="tag-exclusive">UNRELEASED VIP</span>
          <span class="tag-meta">{{ currentTrack.genre }} • {{ currentTrack.bpm }} BPM • {{ currentTrack.key }}</span>
        </div>
        <h1 class="track-title">{{ currentTrack.title }}</h1>
        <p class="track-artist">von <strong>{{ currentTrack.artist }}</strong></p>
        <p class="track-desc">{{ currentTrack.description }}</p>

        <!-- Waveform & Realtime Audio Visualizer -->
        <div class="waveform-container">
          <div class="eq-bars">
            <span
              v-for="i in 36"
              :key="i"
              class="eq-bar"
              :class="{ active: isPlaying }"
              :style="{ height: getBarHeight(i) + '%' }"
            ></span>
          </div>
        </div>

        <div class="hero-actions">
          <button class="btn btn-hero-play" type="button" @click="togglePlay">
            <span class="btn-icon">{{ isPlaying ? '⏸' : '▶' }}</span>
            <span>{{ isPlaying ? 'Pause' : 'Exklusiv abspielen' }}</span>
          </button>
          <button class="btn ghost" type="button" @click="toggleLikeCurrent">
            <span :class="{ 'liked-heart': currentTrack.isLiked }">
              {{ currentTrack.isLiked ? '❤️' : '🤍' }}
            </span>
            <span>{{ currentTrack.likes }} Likes</span>
          </button>
          <button class="btn ghost" type="button" @click="showUploadModal = true">
            <span>+ Eigenen Track präsentieren</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Filter & Search Controls -->
    <section class="music-nav-bar">
      <div class="filter-group">
        <button
          v-for="cat in filterCategories"
          :key="cat"
          class="cat-chip"
          :class="{ active: activeCategory === cat }"
          @click="activeCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
      <div class="search-box">
        <input
          v-model.trim="searchQuery"
          type="text"
          class="input search-input"
          placeholder="Suche exklusive Tracks, Artists, Genre..."
        />
      </div>
    </section>

    <!-- Tracklist Roster Grid -->
    <section class="tracks-roster-section">
      <div class="section-head">
        <h2>Exklusive Tracks &amp; Demos ({{ filteredTracks.length }})</h2>
        <span class="muted small">Klicke auf einen Track zum Abspielen im Player</span>
      </div>

      <div class="tracks-list card">
        <div
          v-for="(track, index) in filteredTracks"
          :key="track.id"
          class="track-row"
          :class="{ 'is-current': currentTrack.id === track.id, 'is-playing': currentTrack.id === track.id && isPlaying }"
          @click="selectAndPlayTrack(track)"
        >
          <!-- Number / Play icon -->
          <div class="track-num-col">
            <span class="num-text" v-if="currentTrack.id !== track.id || !isPlaying">{{ index + 1 }}</span>
            <span class="play-indicator" v-else>🔊</span>
          </div>

          <!-- Artwork Icon -->
          <div class="track-artwork">
            <span class="artwork-emoji">{{ track.artwork }}</span>
          </div>

          <!-- Title and Artist -->
          <div class="track-main-col">
            <div class="track-row-title-box">
              <span class="track-row-title">{{ track.title }}</span>
              <span class="badge-mini" :class="track.badgeClass">{{ track.badge }}</span>
            </div>
            <span class="track-row-artist">{{ track.artist }}</span>
          </div>

          <!-- Genre / BPM / Key -->
          <div class="track-meta-col">
            <span class="genre-pill">{{ track.genre }}</span>
            <span class="bpm-pill">{{ track.bpm }} BPM</span>
            <span class="key-pill">{{ track.key }}</span>
          </div>

          <!-- Plays & Duration -->
          <div class="track-stats-col">
            <span class="streams-count">🎧 {{ track.plays.toLocaleString('de-DE') }}</span>
            <span class="duration">{{ track.duration }}</span>
          </div>

          <!-- Actions -->
          <div class="track-actions-col" @click.stop>
            <button class="iconbtn heart-btn" @click="toggleLike(track)">
              {{ track.isLiked ? '❤️' : '🤍' }}
            </button>
            <button class="btn btn-row-play" @click="selectAndPlayTrack(track)">
              {{ currentTrack.id === track.id && isPlaying ? '⏸' : '▶' }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Artist Submission Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Exklusiven Track auf UNYQ präsentieren</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitTrack">
          <label>
            <span>Songtitel *</span>
            <input v-model.trim="newTrack.title" class="input" required placeholder="z. B. Berlin Midnight Run" />
          </label>
          <label>
            <span>Künstlername / Kollektiv *</span>
            <input v-model.trim="newTrack.artist" class="input" required placeholder="z. B. DJ Apex &amp; UNYQ" />
          </label>
          <div class="form-row-3">
            <label>
              <span>Genre</span>
              <input v-model.trim="newTrack.genre" class="input" placeholder="Trap, Drill, R&amp;B..." />
            </label>
            <label>
              <span>BPM</span>
              <input v-model.number="newTrack.bpm" class="input" type="number" min="50" max="220" placeholder="140" />
            </label>
            <label>
              <span>Key</span>
              <input v-model.trim="newTrack.key" class="input" placeholder="Am, F#m, Cmaj..." />
            </label>
          </div>
          <label>
            <span>Exklusivitäts-Status</span>
            <select v-model="newTrack.badge" class="input">
              <option value="UNRELEASED">🔥 Unreleased Track</option>
              <option value="VIP EXCLUSIVE">💎 VIP Exclusive</option>
              <option value="EARLY ACCESS">⭐ Early Access</option>
              <option value="STUDIO DEMO">🎧 Studio Demo</option>
            </select>
          </label>
          <label>
            <span>Beschreibung &amp; Notizen</span>
            <textarea v-model.trim="newTrack.description" class="input" rows="3" placeholder="Hintergrund zum Track, Mitwirkende..."></textarea>
          </label>

          <div class="upload-dropzone">
            <span class="upload-icon">🎵</span>
            <span>Audio-Datei hochladen (WAV / MP3)</span>
            <small class="muted">Maximal 100 MB • Studio Qualität bevorzugt</small>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showUploadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Track jetzt präsentieren 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Fixed Floating Bottom Music Player Bar -->
    <footer class="bottom-player-bar card">
      <div class="player-left">
        <div class="now-playing-thumb">
          <span>{{ currentTrack.artwork }}</span>
        </div>
        <div class="now-playing-info">
          <div class="np-title">{{ currentTrack.title }}</div>
          <div class="np-artist">{{ currentTrack.artist }}</div>
        </div>
        <button class="iconbtn np-heart" @click="toggleLikeCurrent">
          {{ currentTrack.isLiked ? '❤️' : '🤍' }}
        </button>
      </div>

      <div class="player-center">
        <div class="player-controls">
          <button class="iconbtn ctrl-btn" @click="playPrevTrack" title="Vorheriger Track">⏮</button>
          <button class="btn-play-round" @click="togglePlay" :title="isPlaying ? 'Pause' : 'Abspielen'">
            {{ isPlaying ? '⏸' : '▶' }}
          </button>
          <button class="iconbtn ctrl-btn" @click="playNextTrack" title="Nächster Track">⏭</button>
        </div>

        <div class="scrubber-row">
          <span class="time-stamp">{{ formatTime(currentTime) }}</span>
          <div class="scrub-track" @click="handleSeek">
            <div class="scrub-fill" :style="{ width: progressPercent + '%' }"></div>
            <div class="scrub-handle" :style="{ left: progressPercent + '%' }"></div>
          </div>
          <span class="time-stamp">{{ currentTrack.duration }}</span>
        </div>
      </div>

      <div class="player-right">
        <div class="track-pills-live">
          <span class="live-pill">{{ currentTrack.genre }}</span>
          <span class="live-pill">{{ currentTrack.bpm }} BPM</span>
        </div>
        <div class="volume-slider-box">
          <span class="vol-icon">{{ volume > 0 ? '🔊' : '🔇' }}</span>
          <input
            v-model.number="volume"
            type="range"
            min="0"
            max="1"
            step="0.05"
            class="vol-range"
            @input="updateVolume"
          />
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useToast } from "../composables/useToast";

const { showToast } = useToast();

const isPlaying = ref(false);
const currentTime = ref(0);
const durationSec = ref(184); // 3:04
const volume = ref(0.75);
const activeCategory = ref("Alle");
const searchQuery = ref("");
const showUploadModal = ref(false);

const filterCategories = ["Alle", "Unreleased", "VIP Exclusive", "Drill & Trap", "R&B / Soul", "Lo-Fi"];

const tracks = ref([
  {
    id: 1,
    title: "Midnight Drive in Berlin",
    artist: "KAZA & UNYQ Collective",
    genre: "Melodic Trap",
    bpm: 138,
    key: "F#m",
    duration: "3:04",
    durationSec: 184,
    plays: 14250,
    likes: 842,
    isLiked: true,
    badge: "UNRELEASED",
    badgeClass: "badge-hot",
    artwork: "🌃",
    description: "Exklusiver Pre-Release Track für UNYQ Member. Tiefe 808s, sphärische Ambient-Gitarren und markante Vocals.",
  },
  {
    id: 2,
    title: "Cyber Drip (808 Edition)",
    artist: "Beatmaker Neo",
    genre: "Drill & Trap",
    bpm: 142,
    key: "Gm",
    duration: "2:48",
    durationSec: 168,
    plays: 8910,
    likes: 512,
    isLiked: false,
    badge: "VIP EXCLUSIVE",
    badgeClass: "badge-vip",
    artwork: "⚡",
    description: "High-Energy Cyberdrill Beat mit verzerrten Glides und aggressivem Hi-Hat Roll.",
  },
  {
    id: 3,
    title: "Golden Hour Sunset",
    artist: "Aura Vox",
    genre: "R&B / Soul",
    bpm: 94,
    key: "Db",
    duration: "3:22",
    durationSec: 202,
    plays: 19800,
    likes: 1240,
    isLiked: true,
    badge: "EARLY ACCESS",
    badgeClass: "badge-star",
    artwork: "🌅",
    description: "Warme Vintage-Rhodes Akkorde mit samtigen R&B Vocal Harmonies.",
  },
  {
    id: 4,
    title: "Subzero Pressure",
    artist: "808 Phantom",
    genre: "Drill & Trap",
    bpm: 130,
    key: "Dm",
    duration: "2:36",
    durationSec: 156,
    plays: 6420,
    likes: 389,
    isLiked: false,
    badge: "UNRELEASED",
    badgeClass: "badge-hot",
    artwork: "❄️",
    description: "Kalter, minimalistischer Trap-Banger für Late Night Sessions.",
  },
  {
    id: 5,
    title: "Tokyo Rain (Coffee & Stems)",
    artist: "Mika Lo-Fi",
    genre: "Lo-Fi",
    bpm: 82,
    key: "Cmaj7",
    duration: "2:55",
    durationSec: 175,
    plays: 23100,
    likes: 1980,
    isLiked: false,
    badge: "STUDIO DEMO",
    badgeClass: "badge-demo",
    artwork: "🌧️",
    description: "Knisterndes Vinyl, entspannte Jazz-Chords und gemütliche Drums.",
  },
  {
    id: 6,
    title: "Neon Horizon (Synthwave Dub)",
    artist: "Solaris 99",
    genre: "Lo-Fi",
    bpm: 110,
    key: "Em",
    duration: "3:15",
    durationSec: 195,
    plays: 7430,
    likes: 495,
    isLiked: false,
    badge: "VIP EXCLUSIVE",
    badgeClass: "badge-vip",
    artwork: "🌆",
    description: "Retro-analoge Synthesizer gepaart mit modernem Bass-Design.",
  },
]);

const currentTrack = ref(tracks.value[0]);

const newTrack = ref({
  title: "",
  artist: "",
  genre: "Melodic Trap",
  bpm: 135,
  key: "Am",
  badge: "UNRELEASED",
  description: "",
});

const filteredTracks = computed(() => {
  return tracks.value.filter((t) => {
    const matchCat =
      activeCategory.value === "Alle" ||
      (activeCategory.value === "Unreleased" && t.badge === "UNRELEASED") ||
      (activeCategory.value === "VIP Exclusive" && t.badge === "VIP EXCLUSIVE") ||
      (activeCategory.value === "Drill & Trap" && t.genre.includes("Trap")) ||
      (activeCategory.value === "R&B / Soul" && t.genre.includes("R&B")) ||
      (activeCategory.value === "Lo-Fi" && t.genre.includes("Lo-Fi"));

    const query = searchQuery.value.toLowerCase();
    const matchQuery =
      !query ||
      t.title.toLowerCase().includes(query) ||
      t.artist.toLowerCase().includes(query) ||
      t.genre.toLowerCase().includes(query);

    return matchCat && matchQuery;
  });
});

const progressPercent = computed(() => {
  if (!currentTrack.value.durationSec) return 0;
  return Math.min(100, (currentTime.value / currentTrack.value.durationSec) * 100);
});

// Real-Time Audio Synthesizer (Web Audio API)
let audioCtx = null;
let osc1 = null;
let osc2 = null;
let gainNode = null;
let filterNode = null;
let playTimer = null;

function initAudio() {
  if (typeof window === "undefined") return;
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) {
      audioCtx = new AudioContext();
    }
  }
}

function startAudioSynth() {
  initAudio();
  if (!audioCtx) return;
  if (audioCtx.state === "suspended") {
    audioCtx.resume();
  }

  stopAudioSynth();

  gainNode = audioCtx.createGain();
  gainNode.gain.setValueAtTime(0.08 * volume.value, audioCtx.currentTime);

  filterNode = audioCtx.createBiquadFilter();
  filterNode.type = "lowpass";
  filterNode.frequency.setValueAtTime(800, audioCtx.currentTime);

  // Smooth warm chords synth
  const baseFreq = currentTrack.value.bpm ? currentTrack.value.bpm * 1.5 : 220;
  osc1 = audioCtx.createOscillator();
  osc1.type = "sine";
  osc1.frequency.setValueAtTime(baseFreq, audioCtx.currentTime);

  osc2 = audioCtx.createOscillator();
  osc2.type = "triangle";
  osc2.frequency.setValueAtTime(baseFreq * 1.5, audioCtx.currentTime);

  osc1.connect(filterNode);
  osc2.connect(filterNode);
  filterNode.connect(gainNode);
  gainNode.connect(audioCtx.destination);

  osc1.start();
  osc2.start();
}

function stopAudioSynth() {
  try {
    if (osc1) {
      osc1.stop();
      osc1.disconnect();
      osc1 = null;
    }
    if (osc2) {
      osc2.stop();
      osc2.disconnect();
      osc2 = null;
    }
  } catch {
    // ignore
  }
}

function togglePlay() {
  isPlaying.value = !isPlaying.value;
  if (isPlaying.value) {
    startAudioSynth();
    showToast(`Spiele exklusiv: "${currentTrack.value.title}" 🎶`, "info");
    startTimer();
  } else {
    stopAudioSynth();
    stopTimer();
  }
}

function selectAndPlayTrack(track) {
  if (currentTrack.value.id === track.id) {
    togglePlay();
    return;
  }
  currentTrack.value = track;
  currentTime.value = 0;
  durationSec.value = track.durationSec;
  isPlaying.value = true;
  startAudioSynth();
  startTimer();
  showToast(`Lädt exklusiven Track: "${track.title}" 🔥`, "success");
}

function playNextTrack() {
  const currentIndex = tracks.value.findIndex((t) => t.id === currentTrack.value.id);
  const nextTrack = tracks.value[(currentIndex + 1) % tracks.value.length];
  selectAndPlayTrack(nextTrack);
}

function playPrevTrack() {
  const currentIndex = tracks.value.findIndex((t) => t.id === currentTrack.value.id);
  const prevIndex = (currentIndex - 1 + tracks.value.length) % tracks.value.length;
  selectAndPlayTrack(tracks.value[prevIndex]);
}

function startTimer() {
  stopTimer();
  playTimer = setInterval(() => {
    if (currentTime.value < currentTrack.value.durationSec) {
      currentTime.value++;
    } else {
      playNextTrack();
    }
  }, 1000);
}

function stopTimer() {
  if (playTimer) {
    clearInterval(playTimer);
    playTimer = null;
  }
}

function handleSeek(event) {
  const rect = event.currentTarget.getBoundingClientRect();
  const clickX = event.clientX - rect.left;
  const ratio = Math.max(0, Math.min(1, clickX / rect.width));
  currentTime.value = Math.floor(ratio * currentTrack.value.durationSec);
}

function updateVolume() {
  if (gainNode && audioCtx) {
    gainNode.gain.setValueAtTime(0.08 * volume.value, audioCtx.currentTime);
  }
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function getBarHeight(i) {
  if (!isPlaying.value) return 15;
  const t = Date.now() / 150;
  return 20 + Math.abs(Math.sin(t + i * 0.4)) * 75;
}

function toggleLike(track) {
  track.isLiked = !track.isLiked;
  track.likes += track.isLiked ? 1 : -1;
  showToast(track.isLiked ? "Zu Favoriten hinzugefügt! ❤️" : "Aus Favoriten entfernt.");
}

function toggleLikeCurrent() {
  toggleLike(currentTrack.value);
}

function submitTrack() {
  const id = Date.now();
  const created = {
    id,
    title: newTrack.value.title,
    artist: newTrack.value.artist,
    genre: newTrack.value.genre || "Melodic Trap",
    bpm: newTrack.value.bpm || 135,
    key: newTrack.value.key || "Am",
    duration: "2:50",
    durationSec: 170,
    plays: 1,
    likes: 1,
    isLiked: true,
    badge: newTrack.value.badge || "UNRELEASED",
    badgeClass: "badge-hot",
    artwork: "🚀",
    description: newTrack.value.description || "Frisch eingereichter Exklusiv-Track auf UNYQ Music.",
  };
  tracks.value.unshift(created);
  showUploadModal.value = false;
  showToast("Track erfolgreich eingereicht und im Player platziert! 🎵", "success");
  selectAndPlayTrack(created);
}

onMounted(() => {
  // initial setup
});

onBeforeUnmount(() => {
  stopAudioSynth();
  stopTimer();
});
</script>

<style scoped>
.music-player-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1240px;
  margin: 0 auto;
  padding: 8px 0 120px; /* Space for bottom player */
}

/* Spotlight Hero */
.spotlight-hero {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 36px;
  align-items: center;
  padding: 36px;
  background: 
    radial-gradient(circle at top right, rgba(147, 51, 234, 0.2), transparent 60%),
    linear-gradient(135deg, rgba(24, 24, 37, 0.9), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(168, 85, 247, 0.25);
  border-radius: 24px;
  position: relative;
  overflow: hidden;
}

.spotlight-visual {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.vinyl-art-wrapper {
  width: 220px;
  height: 220px;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vinyl-art-wrapper.spinning .vinyl-disc {
  animation: rotateDisc 10s linear infinite;
}

@keyframes rotateDisc {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.vinyl-disc {
  width: 100%;
  height: 100%;
  background: 
    radial-gradient(circle, #09090b 40%, #18181b 45%, #09090b 50%, #18181b 55%, #09090b 60%, #18181b 70%),
    #09090b;
  border-radius: 50%;
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.6), inset 0 0 0 2px rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
}

.vinyl-center {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #7c3aed, #ec4899);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 4px solid #09090b;
}

.vinyl-brand {
  font-size: 13px;
  font-weight: 900;
  color: #fff;
  letter-spacing: 0.1em;
}

.exclusive-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  color: #f87171;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  margin-top: 14px;
}

.spotlight-info {
  display: flex;
  flex-direction: column;
}

.spotlight-tag-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.tag-exclusive {
  background: #a855f7;
  color: #fff;
  font-size: 11px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 6px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tag-meta {
  font-size: 12px;
  color: var(--muted);
}

.track-title {
  font-size: clamp(1.8rem, 3.2vw, 2.6rem);
  font-weight: 800;
  margin: 4px 0 6px;
  line-height: 1.15;
}

.track-artist {
  margin: 0 0 12px;
  font-size: 1.05rem;
  color: var(--muted);
}

.track-artist strong {
  color: #c084fc;
}

.track-desc {
  font-size: 14px;
  color: var(--muted);
  line-height: 1.5;
  max-width: 650px;
  margin: 0 0 20px;
}

/* Waveform Visualizer */
.waveform-container {
  height: 48px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 6px 16px;
  display: flex;
  align-items: flex-end;
  margin-bottom: 24px;
}

.eq-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  width: 100%;
  height: 100%;
}

.eq-bar {
  width: 3px;
  background: rgba(168, 85, 247, 0.35);
  border-radius: 2px;
  transition: height 0.1s ease;
}

.eq-bar.active {
  background: linear-gradient(180deg, #c084fc 0%, #7c3aed 100%);
  box-shadow: 0 0 6px rgba(168, 85, 247, 0.4);
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-hero-play {
  background: linear-gradient(135deg, #9333ea, #4f46e5);
  padding: 12px 24px;
  font-size: 15px;
}

.btn-hero-play .btn-icon {
  font-size: 16px;
}

/* Nav Bar */
.music-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.filter-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.cat-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-chip.active, .cat-chip:hover {
  background: rgba(168, 85, 247, 0.18);
  color: #c084fc;
  border-color: rgba(168, 85, 247, 0.4);
}

.search-box {
  min-width: 280px;
}

/* Tracks Roster */
.tracks-roster-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.section-head h2 {
  margin: 0;
  font-size: 1.3rem;
}

.tracks-list {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.track-row {
  display: grid;
  grid-template-columns: 36px 44px 1.5fr 1fr 120px 100px;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.track-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.track-row.is-current {
  background: rgba(168, 85, 247, 0.12);
  border-left: 3px solid #a855f7;
}

.track-num-col {
  color: var(--muted);
  font-size: 13px;
  font-weight: 600;
  text-align: center;
}

.play-indicator {
  font-size: 14px;
  animation: pulse 1s infinite;
}

.track-artwork {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.track-main-col {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.track-row-title-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.track-row-title {
  font-weight: 700;
  font-size: 14.5px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.badge-mini {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge-hot { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.badge-vip { background: rgba(168, 85, 247, 0.2); color: #c084fc; }
.badge-star { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.badge-demo { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

.track-row-artist {
  font-size: 12.5px;
  color: var(--muted);
}

.track-meta-col {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.genre-pill, .bpm-pill, .key-pill {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
}

.track-stats-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
  font-size: 12px;
  color: var(--muted);
}

.track-actions-col {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
}

.heart-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 6px;
}

.btn-row-play {
  min-height: 32px;
  width: 32px;
  padding: 0;
  border-radius: 50%;
  font-size: 12px;
}

/* Floating Bottom Player */
.bottom-player-bar {
  position: fixed;
  bottom: 14px;
  left: 50%;
  transform: translateX(-50%);
  width: min(1200px, calc(100% - 32px));
  padding: 12px 24px;
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(168, 85, 247, 0.3);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  border-radius: 20px;
  display: grid;
  grid-template-columns: 280px 1fr 240px;
  align-items: center;
  gap: 24px;
  z-index: 50;
}

.player-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.now-playing-thumb {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  flex-shrink: 0;
}

.now-playing-info {
  min-width: 0;
}

.np-title {
  font-weight: 700;
  font-size: 14px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.np-artist {
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.player-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.player-controls {
  display: flex;
  align-items: center;
  gap: 16px;
}

.ctrl-btn {
  background: transparent;
  border: none;
  color: var(--text);
  font-size: 18px;
  cursor: pointer;
}

.btn-play-round {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #a855f7, #6366f1);
  color: #fff;
  font-size: 16px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 14px rgba(168, 85, 247, 0.4);
}

.scrubber-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
}

.time-stamp {
  font-size: 11px;
  color: var(--muted);
  font-family: monospace;
  width: 32px;
}

.scrub-track {
  flex: 1;
  height: 6px;
  background: rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  position: relative;
  cursor: pointer;
}

.scrub-fill {
  height: 100%;
  background: linear-gradient(90deg, #a855f7, #ec4899);
  border-radius: 999px;
}

.scrub-handle {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #fff;
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  box-shadow: 0 0 8px rgba(0, 0, 0, 0.5);
}

.player-right {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
}

.track-pills-live {
  display: flex;
  gap: 6px;
}

.live-pill {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--muted);
}

.volume-slider-box {
  display: flex;
  align-items: center;
  gap: 8px;
}

.vol-range {
  width: 70px;
  accent-color: #a855f7;
  cursor: pointer;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 540px;
  width: 100%;
  padding: 28px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}

.upload-dropzone {
  border: 2px dashed rgba(168, 85, 247, 0.35);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: rgba(168, 85, 247, 0.05);
  cursor: pointer;
}

.upload-icon {
  font-size: 28px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .spotlight-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  .track-row {
    grid-template-columns: 28px 36px 1fr 80px;
  }
  .track-meta-col, .track-stats-col {
    display: none;
  }
  .bottom-player-bar {
    grid-template-columns: 1fr 60px;
  }
  .player-right {
    display: none;
  }
}
</style>
