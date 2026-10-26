<template>
  <div class="library-page">
    <!-- Hero Header -->
    <header class="library-hero card">
      <div class="hero-left">
        <div class="license-tag">
          <span class="cc-badge">CC0</span>
          <span>100% Free &amp; Open Source Sound Library</span>
        </div>
        <h1>UNYQ Library</h1>
        <p class="hero-desc">
          Die offene Sound- &amp; Sample-Bibliothek für Producer. 
          Kostenlose 808s, Drum-Kits, Melodic Stems, Serum Presets und MIDIs — 
          ohne Lizenzgebühren, ohne Haken. Bereit für deinen nächsten Hit.
        </p>

        <div class="hero-stats-row">
          <div class="lib-stat">
            <span class="stat-number">1.250+</span>
            <span class="stat-title">Free Samples</span>
          </div>
          <div class="lib-stat">
            <span class="stat-number">100%</span>
            <span class="stat-title">Royalty Free</span>
          </div>
          <div class="lib-stat">
            <span class="stat-number">24-Bit</span>
            <span class="stat-title">WAV Audio</span>
          </div>
        </div>

        <div class="hero-actions">
          <button class="btn" type="button" @click="downloadFeaturedPack">
            ⚡ All-in-One Producer Pack herunterladen (ZIP)
          </button>
          <button class="btn ghost" type="button" @click="showContributeModal = true">
            <span>+ Eigene Sounds beisteuern</span>
          </button>
        </div>
      </div>

      <div class="hero-right">
        <div class="license-guarantee-card">
          <div class="guarantee-icon">🛡️</div>
          <h3>Free License Garantie</h3>
          <p class="small muted">
            Alle Sounds unterliegen der Open-Source Creative Commons CC0 / UNYQ Free License. 
            Du darfst sie für kommerzielle Beats, Streaming-Releases und Placements nutzen.
          </p>
          <div class="rights-list">
            <span>✓ Kommerzielle Beats erlaubt</span>
            <span>✓ Keine Tantiemen-Abgaben</span>
            <span>✓ Kein Clearence-Aufwand</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Featured Packs Carousel/Row -->
    <section class="packs-section">
      <div class="section-head">
        <h2>Kuratierte Sound Packs</h2>
        <span class="muted small">Komplette Sample-Kits kostenlos mit 1 Klick downloaden</span>
      </div>

      <div class="packs-grid">
        <div v-for="pack in featuredPacks" :key="pack.id" class="card pack-card">
          <div class="pack-badge">{{ pack.badge }}</div>
          <div class="pack-cover">
            <span class="pack-emoji">{{ pack.emoji }}</span>
          </div>
          <div class="pack-info">
            <h4>{{ pack.name }}</h4>
            <p class="muted small">{{ pack.desc }}</p>
            <div class="pack-meta">
              <span>{{ pack.samplesCount }} Samples</span>
              <span>{{ pack.size }}</span>
            </div>
            <button class="btn btn-pack-dl" @click="downloadPack(pack)">
              ⬇️ Pack Download (Free)
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Interactive Sample Browser -->
    <section class="samples-browser-section">
      <div class="browser-header">
        <div class="browser-title-box">
          <h2>Sample &amp; Preset Browser</h2>
          <p class="muted">Höre direkt rein und lade einzelne One-Shots oder Loops herunter.</p>
        </div>
        <div class="search-input-box">
          <input
            v-model.trim="searchFilter"
            type="text"
            class="input"
            placeholder="Suche nach Kick, 808, Am, Drill, Serum..."
          />
        </div>
      </div>

      <!-- Categories Filter Tabs -->
      <div class="category-tabs">
        <button
          v-for="cat in categories"
          :key="cat"
          class="cat-tab-btn"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- Samples List Table -->
      <div class="samples-table card">
        <div
          v-for="sample in filteredSamples"
          :key="sample.id"
          class="sample-row"
          :class="{ 'is-active': activeSampleId === sample.id }"
        >
          <div class="play-cell">
            <button
              class="btn-sample-play"
              :class="{ playing: activeSampleId === sample.id && isPlaying }"
              @click="togglePlaySample(sample)"
              title="Sample vorhören"
            >
              {{ activeSampleId === sample.id && isPlaying ? '⏸' : '▶' }}
            </button>
          </div>

          <div class="sample-name-cell">
            <span class="sample-title">{{ sample.name }}</span>
            <span class="sample-cat-tag">{{ sample.category }}</span>
          </div>

          <!-- Dynamic Waveform Bar -->
          <div class="waveform-cell">
            <div class="mini-wave">
              <span
                v-for="w in 20"
                :key="w"
                class="wave-stick"
                :class="{ active: activeSampleId === sample.id && isPlaying }"
                :style="{ height: (15 + (w * 4) % 65) + '%' }"
              ></span>
            </div>
          </div>

          <div class="meta-cell">
            <span class="bpm-tag" v-if="sample.bpm">{{ sample.bpm }} BPM</span>
            <span class="key-tag" v-if="sample.key">{{ sample.key }}</span>
            <span class="format-tag">{{ sample.format }}</span>
          </div>

          <div class="dl-cell">
            <button class="btn btn-sm dl-btn" @click="downloadSample(sample)">
              ⬇️ Download
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Contribute Modal -->
    <div v-if="showContributeModal" class="modal-overlay" @click.self="showContributeModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Sounds zur Open Source Library beisteuern</h3>
          <button class="btn ghost tiny" @click="showContributeModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitContribution">
          <label>
            <span>Titel des Samples / Packs *</span>
            <input v-model.trim="newContribution.name" class="input" required placeholder="z. B. Dark Heavy 808" />
          </label>
          <label>
            <span>Dein Producer- / Künstlername *</span>
            <input v-model.trim="newContribution.producer" class="input" required placeholder="z. B. 808God_Berlin" />
          </label>
          <div class="form-row-3">
            <label>
              <span>Kategorie</span>
              <select v-model="newContribution.category" class="input">
                <option value="808 & Bass">808 &amp; Bass</option>
                <option value="Drums & Percs">Drums &amp; Percs</option>
                <option value="Melodic Loops">Melodic Loops</option>
                <option value="Vocal Chops">Vocal Chops</option>
                <option value="Presets & MIDI">Presets &amp; MIDI</option>
              </select>
            </label>
            <label>
              <span>BPM (optional)</span>
              <input v-model.number="newContribution.bpm" type="number" class="input" placeholder="140" />
            </label>
            <label>
              <span>Key (optional)</span>
              <input v-model.trim="newContribution.key" class="input" placeholder="F#m" />
            </label>
          </div>

          <div class="upload-dropzone">
            <span class="upload-icon">📦</span>
            <span>WAV, ZIP oder Preset-Datei hochladen</span>
            <small class="muted">100% eigene Kreation • CC0 Free License Bestätigung</small>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showContributeModal = false">Abbrechen</button>
            <button class="btn" type="submit">Sounds beisteuern 🚀</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from "vue";
import { useToast } from "../composables/useToast";

const { showToast } = useToast();

const selectedCategory = ref("Alle");
const searchFilter = ref("");
const activeSampleId = ref(null);
const isPlaying = ref(false);
const showContributeModal = ref(false);

const categories = ["Alle", "808 & Bass", "Drums & Percs", "Melodic Loops", "Vocal Chops", "Presets & MIDI"];

const featuredPacks = [
  {
    id: 1,
    name: "UNYQ 808 Titanics Vol. 1",
    desc: "32 perfekt gestimmte, sub-schwere 808s für Trap, Drill & Rage.",
    samplesCount: 32,
    size: "48 MB",
    badge: "TOP BEATMAKER",
    emoji: "💣",
  },
  {
    id: 2,
    name: "Midnight Melodic STEMs",
    desc: "18 düstere & emotionale Sample Loops inkl. separaten Stems & MIDI.",
    samplesCount: 72,
    size: "180 MB",
    badge: "STEMS INCLUDED",
    emoji: "🎹",
  },
  {
    id: 3,
    name: "Punch Drill Essentials '26",
    desc: "Hart zuschlagende Snares, Kicks, Glides und Rolls für Producer.",
    samplesCount: 64,
    size: "82 MB",
    badge: "DRILL READY",
    emoji: "🥁",
  },
  {
    id: 4,
    name: "Serum & Vital Secret Presets",
    desc: "40 analog-modellierte Synthesizer Presets für Pads, Plucks & Leads.",
    samplesCount: 40,
    size: "24 MB",
    badge: "PRESETS",
    emoji: "🎛️",
  },
];

const samples = ref([
  { id: 1, name: "UNYQ_SubHeavy_808_C", category: "808 & Bass", bpm: null, key: "C", format: "WAV 24-bit" },
  { id: 2, name: "Deep_Slide_808_Fm", category: "808 & Bass", bpm: null, key: "Fm", format: "WAV 24-bit" },
  { id: 3, name: "Drill_Distortion_808_Am", category: "808 & Bass", bpm: 142, key: "Am", format: "WAV 24-bit" },
  { id: 4, name: "Hard_Smack_Snare_01", category: "Drums & Percs", bpm: null, key: null, format: "WAV 24-bit" },
  { id: 5, name: "Punchy_Kick_Puncher_99", category: "Drums & Percs", bpm: null, key: null, format: "WAV 24-bit" },
  { id: 6, name: "HiHat_Roll_Pattern_140", category: "Drums & Percs", bpm: 140, key: null, format: "WAV 24-bit" },
  { id: 7, name: "Midnight_Piano_Loop_Em", category: "Melodic Loops", bpm: 130, key: "Em", format: "WAV 24-bit" },
  { id: 8, name: "Dark_Guitar_Trap_Am", category: "Melodic Loops", bpm: 138, key: "Am", format: "WAV 24-bit" },
  { id: 9, name: "Soulful_Vocal_Chop_Gm", category: "Vocal Chops", bpm: 124, key: "Gm", format: "WAV 24-bit" },
  { id: 10, name: "Serum_Pad_Celestial_Preset", category: "Presets & MIDI", bpm: null, key: null, format: "fxp / preset" },
  { id: 11, name: "Vital_Lead_NeonCyber_Preset", category: "Presets & MIDI", bpm: null, key: null, format: "vitalbank" },
  { id: 12, name: "RNB_Chord_Progression_MIDI", category: "Presets & MIDI", bpm: 90, key: "Db", format: "MIDI File" },
]);

const newContribution = ref({
  name: "",
  producer: "",
  category: "808 & Bass",
  bpm: 140,
  key: "Am",
});

const filteredSamples = computed(() => {
  return samples.value.filter((s) => {
    const matchCat = selectedCategory.value === "Alle" || s.category === selectedCategory.value;
    const q = searchFilter.value.toLowerCase();
    const matchQuery =
      !q ||
      s.name.toLowerCase().includes(q) ||
      s.category.toLowerCase().includes(q) ||
      (s.key && s.key.toLowerCase().includes(q)) ||
      (s.bpm && String(s.bpm).includes(q));
    return matchCat && matchQuery;
  });
});

// Audio synth for preview
let audioCtx = null;
let osc = null;
let gain = null;
let previewTimeout = null;

function initAudio() {
  if (typeof window === "undefined") return;
  if (!audioCtx) {
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    if (AudioContext) audioCtx = new AudioContext();
  }
}

function playSampleSynth(sample) {
  initAudio();
  if (!audioCtx) return;
  if (audioCtx.state === "suspended") audioCtx.resume();

  stopSampleSynth();

  gain = audioCtx.createGain();
  osc = audioCtx.createOscillator();

  if (sample.category.includes("808")) {
    osc.type = "sine";
    osc.frequency.setValueAtTime(65, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(32, audioCtx.currentTime + 0.8);
    gain.gain.setValueAtTime(0.3, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.2);
  } else if (sample.category.includes("Drums")) {
    osc.type = "triangle";
    osc.frequency.setValueAtTime(220, audioCtx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(50, audioCtx.currentTime + 0.3);
    gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.4);
  } else {
    osc.type = "sine";
    osc.frequency.setValueAtTime(440, audioCtx.currentTime);
    gain.gain.setValueAtTime(0.15, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 1.5);
  }

  osc.connect(gain);
  gain.connect(audioCtx.destination);
  osc.start();

  previewTimeout = setTimeout(() => {
    stopSampleSynth();
    isPlaying.value = false;
  }, 1600);
}

function stopSampleSynth() {
  if (previewTimeout) {
    clearTimeout(previewTimeout);
    previewTimeout = null;
  }
  try {
    if (osc) {
      osc.stop();
      osc.disconnect();
      osc = null;
    }
  } catch {
    // ignore
  }
}

function togglePlaySample(sample) {
  if (activeSampleId.value === sample.id && isPlaying.value) {
    stopSampleSynth();
    isPlaying.value = false;
    return;
  }
  activeSampleId.value = sample.id;
  isPlaying.value = true;
  playSampleSynth(sample);
  showToast(`Sample Vorschau: "${sample.name}" 🎵`, "info");
}

function downloadSample(sample) {
  showToast(`Download gestartet: ${sample.name} (100% Free CC0) ⬇️`, "success");
}

function downloadPack(pack) {
  showToast(`Pack-Download gestartet: ${pack.name} (${pack.size}) 🚀`, "success");
}

function downloadFeaturedPack() {
  showToast("UNYQ Mega Producer Bundle heruntergeladen! 🎶", "success");
}

function submitContribution() {
  const newId = Date.now();
  samples.value.unshift({
    id: newId,
    name: newContribution.value.name,
    category: newContribution.value.category,
    bpm: newContribution.value.bpm,
    key: newContribution.value.key,
    format: "WAV 24-bit",
  });
  showContributeModal.value = false;
  showToast("Vielen Dank! Deine Sounds sind jetzt in der UNYQ Library verfügbar. ❤️", "success");
}

onBeforeUnmount(() => {
  stopSampleSynth();
});
</script>

<style scoped>
.library-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 8px 0 60px;
}

/* Hero */
.library-hero {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top left, rgba(14, 165, 233, 0.18), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(56, 189, 248, 0.2);
  position: relative;
  overflow: hidden;
}

.license-tag {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(14, 165, 233, 0.12);
  border: 1px solid rgba(14, 165, 233, 0.3);
  color: #38bdf8;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.cc-badge {
  background: #38bdf8;
  color: #0f172a;
  font-size: 11px;
  font-weight: 900;
  padding: 2px 6px;
  border-radius: 4px;
}

.library-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #7dd3fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.hero-stats-row {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
}

.lib-stat {
  display: flex;
  flex-direction: column;
}

.stat-number {
  font-size: 1.4rem;
  font-weight: 800;
  color: #38bdf8;
}

.stat-title {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Guarantee Card */
.license-guarantee-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.guarantee-icon {
  font-size: 32px;
}

.license-guarantee-card h3 {
  margin: 0;
  font-size: 1.15rem;
}

.rights-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  color: #38bdf8;
  font-weight: 600;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

/* Packs Section */
.packs-section {
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

.packs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 20px;
}

.pack-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.pack-card:hover {
  transform: translateY(-3px);
  border-color: rgba(56, 189, 248, 0.4);
}

.pack-badge {
  position: absolute;
  top: 14px;
  left: 14px;
  background: rgba(14, 165, 233, 0.2);
  color: #38bdf8;
  border: 1px solid rgba(14, 165, 233, 0.3);
  font-size: 10px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 6px;
}

.pack-cover {
  height: 120px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 14px;
}

.pack-emoji {
  font-size: 54px;
}

.pack-info h4 {
  margin: 0 0 6px;
  font-size: 1.05rem;
}

.pack-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--muted);
  margin: 12px 0 16px;
  border-top: 1px solid var(--border);
  padding-top: 8px;
}

.btn-pack-dl {
  width: 100%;
  min-height: 36px;
  font-size: 13px;
  background: linear-gradient(135deg, #0284c7, #0369a1);
}

/* Samples Browser */
.samples-browser-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.browser-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.browser-title-box h2 {
  margin: 0 0 2px;
  font-size: 1.3rem;
}

.browser-title-box p {
  margin: 0;
  font-size: 13px;
}

.category-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.cat-tab-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-tab-btn.active, .cat-tab-btn:hover {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
  font-weight: 700;
}

/* Samples Table */
.samples-table {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.sample-row {
  display: grid;
  grid-template-columns: 44px 1.5fr 1fr 180px 120px;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  border-radius: 10px;
  transition: background 0.15s ease;
}

.sample-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.sample-row.is-active {
  background: rgba(56, 189, 248, 0.12);
  border-left: 3px solid #38bdf8;
}

.btn-sample-play {
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text);
  font-size: 12px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.btn-sample-play.playing {
  background: #38bdf8;
  color: #0f172a;
}

.sample-name-cell {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.sample-title {
  font-weight: 700;
  font-size: 13.5px;
  font-family: monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.sample-cat-tag {
  font-size: 11px;
  color: var(--muted);
}

.waveform-cell {
  height: 24px;
  display: flex;
  align-items: center;
}

.mini-wave {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 100%;
  width: 100%;
}

.wave-stick {
  flex: 1;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 2px;
}

.wave-stick.active {
  background: #38bdf8;
}

.meta-cell {
  display: flex;
  gap: 8px;
  align-items: center;
}

.bpm-tag, .key-tag, .format-tag {
  font-size: 11px;
  padding: 3px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
}

.dl-cell {
  display: flex;
  justify-content: flex-end;
}

.dl-btn {
  min-height: 30px;
  padding: 4px 12px;
  font-size: 12px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 520px;
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
  border: 2px dashed rgba(56, 189, 248, 0.35);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  background: rgba(56, 189, 248, 0.05);
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
  .library-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  .sample-row {
    grid-template-columns: 36px 1fr 80px;
  }
  .waveform-cell, .meta-cell {
    display: none;
  }
}
</style>
