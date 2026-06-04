<template>
  <div class="anim-lab-page">
    <header class="lab-hero">
      <div>
        <p class="eyebrow">Admin Only</p>
        <h1>Tournament Animation Lab</h1>
        <p>Teste Intro-, Rank- und Battle-Animationen ohne Live-Ansicht zu stoeren.</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" @click="goAdmin">Zurueck zum Admin Hub</button>
        <button class="btn" @click="retrigger">Replay</button>
      </div>
    </header>

    <section v-if="!isTeam" class="access-denied card">
      <h2>Zugriff verweigert</h2>
      <p>Diese Seite ist nur fuer Team/Admin sichtbar.</p>
    </section>

    <template v-else>
      <section class="lab-grid">
        <article class="control-panel card">
          <h2>Controls</h2>
          <label>
            Preset
            <select v-model="preset" @change="applyPreset">
              <option value="cinematic">Cinematic</option>
              <option value="aggressive">Aggressive</option>
              <option value="minimal">Minimal</option>
            </select>
          </label>
          <label>
            Geschwindigkeit: {{ speed.toFixed(2) }}x
            <input v-model.number="speed" type="range" min="0.4" max="2.2" step="0.05" />
          </label>
          <label>
            Intensitaet: {{ intensity.toFixed(2) }}
            <input v-model.number="intensity" type="range" min="0.2" max="1.8" step="0.05" />
          </label>
          <label class="checkbox-row">
            <input v-model="loop" type="checkbox" />
            Endlos-Loop
          </label>
          <label class="checkbox-row">
            <input v-model="showParticles" type="checkbox" />
            FX Particles
          </label>
        </article>

        <article class="preview card" :key="previewKey">
          <div
            class="arena-scene"
            :class="[preset, { looping: loop, particles: showParticles }]"
            :style="sceneStyle"
          >
            <div class="intro-banner">Season Finals - Arena Clash</div>

            <div class="ranks-row">
              <div class="rank-chip bronze">Bronze</div>
              <div class="rank-chip silber">Silber</div>
              <div class="rank-chip gold">Gold</div>
              <div class="rank-chip platin">Platin</div>
              <div class="rank-chip rubin">Rubin</div>
            </div>

            <div class="battle-card">
              <div class="fighter left">Kairo</div>
              <div class="score-block">
                <span>12</span>
                <small>VS</small>
                <span>10</span>
              </div>
              <div class="fighter right">Nova</div>
            </div>
          </div>
        </article>
      </section>

      <section class="card timeline-demo" :key="`timeline-${previewKey}`">
        <h2>Timeline Motion Test</h2>
        <div class="timeline-track">
          <article class="event-card now">LIVE: Urban Arena Cup</article>
          <article class="event-card next">Heute 20:00: Producers Night</article>
          <article class="event-card later">Morgen 19:30: No Loss Sprint</article>
          <article class="event-card later">Fr 21:00: RubiN Gauntlet</article>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const { isTeam, fetchProfile } = useCurrentProfile();

const speed = ref(1);
const intensity = ref(1);
const loop = ref(true);
const showParticles = ref(true);
const preset = ref("cinematic");
const previewKey = ref(0);

const sceneStyle = computed(() => ({
  "--anim-speed": String(speed.value),
  "--anim-intensity": String(intensity.value),
}));

function retrigger() {
  previewKey.value += 1;
}

function applyPreset() {
  if (preset.value === "cinematic") {
    speed.value = 1;
    intensity.value = 1;
    loop.value = true;
    showParticles.value = true;
  } else if (preset.value === "aggressive") {
    speed.value = 1.65;
    intensity.value = 1.45;
    loop.value = true;
    showParticles.value = true;
  } else {
    speed.value = 0.75;
    intensity.value = 0.55;
    loop.value = false;
    showParticles.value = false;
  }
  retrigger();
}

function goAdmin() {
  router.push({ name: "admin-platform" });
}

onMounted(async () => {
  await fetchProfile();
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;600;700&family=Sora:wght@400;700;800&display=swap");

.anim-lab-page {
  min-height: 100%;
  display: grid;
  gap: 14px;
  color: #edf2ff;
  font-family: "Chakra Petch", sans-serif;
}

.lab-hero {
  border: 1px solid #304278;
  border-radius: 20px;
  background: linear-gradient(140deg, #10182f 0%, #1d1f41 50%, #321437 100%);
  padding: 18px;
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.eyebrow {
  margin: 0;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #7dd3fc;
  font-size: 0.72rem;
}

.lab-hero h1 {
  margin: 6px 0;
  font-family: "Sora", sans-serif;
}

.lab-hero p {
  margin: 0;
  color: #a8b8e8;
}

.hero-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.lab-grid {
  display: grid;
  grid-template-columns: 300px 1fr;
  gap: 12px;
}

.card {
  background: #11192f;
  border: 1px solid #2f3d68;
  border-radius: 16px;
  padding: 14px;
}

.control-panel {
  display: grid;
  gap: 10px;
  align-content: start;
}

.control-panel h2,
.timeline-demo h2 {
  margin: 0 0 6px;
  font-family: "Sora", sans-serif;
}

.control-panel label {
  display: grid;
  gap: 6px;
  font-size: 0.86rem;
  color: #aac0eb;
}

.control-panel select,
.control-panel input[type="range"] {
  width: 100%;
}

.checkbox-row {
  display: flex !important;
  align-items: center;
  gap: 8px;
}

.preview {
  padding: 0;
  overflow: hidden;
}

.arena-scene {
  min-height: 280px;
  padding: 14px;
  background:
    radial-gradient(circle at 22% 8%, rgba(251, 113, 133, calc(0.26 * var(--anim-intensity))) 0%, transparent 42%),
    radial-gradient(circle at 84% 14%, rgba(56, 189, 248, calc(0.24 * var(--anim-intensity))) 0%, transparent 40%),
    linear-gradient(145deg, #090d1f 0%, #101733 100%);
  display: grid;
  gap: 14px;
  align-content: center;
  position: relative;
}

.arena-scene.particles::after {
  content: "";
  position: absolute;
  inset: 0;
  background-image: radial-gradient(rgba(255, 255, 255, 0.15) 1px, transparent 1px);
  background-size: 18px 18px;
  animation: particleDrift calc(12s / var(--anim-speed)) linear infinite;
  pointer-events: none;
}

.intro-banner {
  justify-self: center;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  font-family: "Sora", sans-serif;
  animation: introPulse calc(2.4s / var(--anim-speed)) ease-in-out infinite;
}

.ranks-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 8px;
}

.rank-chip {
  text-align: center;
  font-size: 0.78rem;
  font-weight: 700;
  border-radius: 12px;
  padding: 8px 4px;
  animation: rankFloat calc(2s / var(--anim-speed)) ease-in-out infinite;
}

.rank-chip.bronze { background: rgba(212, 138, 74, 0.2); border: 1px solid #d48a4a; }
.rank-chip.silber { background: rgba(168, 177, 192, 0.2); border: 1px solid #a8b1c0; }
.rank-chip.gold { background: rgba(240, 191, 73, 0.2); border: 1px solid #f0bf49; }
.rank-chip.platin { background: rgba(81, 198, 201, 0.2); border: 1px solid #51c6c9; }
.rank-chip.rubin { background: rgba(230, 79, 125, 0.2); border: 1px solid #e64f7d; }

.battle-card {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 10px;
  align-items: center;
  border: 1px solid #415493;
  background: rgba(14, 24, 51, 0.75);
  border-radius: 14px;
  padding: 10px;
  animation: cardRise calc(1.8s / var(--anim-speed)) ease-out;
}

.fighter {
  font-family: "Sora", sans-serif;
  font-weight: 700;
}

.fighter.left { text-align: right; }

.score-block {
  display: grid;
  text-align: center;
  font-family: "Sora", sans-serif;
  color: #ffd369;
}

.score-block span { font-size: 1.3rem; font-weight: 800; }
.score-block small { font-size: 0.65rem; color: #9fb0e5; }

.timeline-track {
  display: grid;
  gap: 8px;
}

.event-card {
  border-radius: 10px;
  border: 1px solid #33487d;
  padding: 9px 10px;
  background: rgba(255, 255, 255, 0.03);
  transform: translateX(0);
  animation: slideIn calc(0.8s / var(--anim-speed)) ease both;
}

.event-card.now { border-color: #ff6b6b; }
.event-card.next { border-color: #60a5fa; animation-delay: 0.08s; }
.event-card.later { border-color: #a78bfa; animation-delay: 0.16s; }

.access-denied h2 {
  margin: 0 0 6px;
}

.access-denied p {
  margin: 0;
  color: #a8b8e8;
}

@keyframes introPulse {
  0%, 100% { transform: scale(1); box-shadow: 0 0 0 rgba(255, 255, 255, 0.2); }
  50% { transform: scale(calc(1 + 0.05 * var(--anim-intensity))); box-shadow: 0 0 24px rgba(255, 255, 255, 0.22); }
}

@keyframes rankFloat {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(calc(-8px * var(--anim-intensity))); }
}

@keyframes cardRise {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes slideIn {
  from { opacity: 0; transform: translateX(-14px); }
  to { opacity: 1; transform: translateX(0); }
}

@keyframes particleDrift {
  from { background-position: 0 0; }
  to { background-position: 0 260px; }
}

.btn {
  min-height: 34px;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid transparent;
  background: linear-gradient(125deg, #f43f5e, #fb7185);
  color: white;
  font-weight: 700;
  cursor: pointer;
}

.btn.ghost {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.25);
}

.arena-scene.minimal .intro-banner,
.arena-scene.minimal .rank-chip {
  animation-iteration-count: 1;
}

@media (max-width: 920px) {
  .lab-grid {
    grid-template-columns: 1fr;
  }

  .ranks-row {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
