<template>
  <div class="cs-entry">
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">Content Schedule</p>
        <h1>Deine Posts. Deine Woche. Immer im Blick.</h1>
        <p class="muted lead">
          Plane YouTube-Videos, Instagram-Reels, TikToks und mehr – direkt in einer übersichtlichen Wochenansicht.
          Kein Drag &amp; Drop-Chaos, keine verschachtelten Blöcke – einfach Post planen, Status setzen, fertig.
        </p>
        <div class="hero-points">
          <span>📅 Wochennavigation</span>
          <span>🎬 YouTube · 📸 Instagram · 🎵 TikTok</span>
          <span>✅ Status-Tracking</span>
        </div>
      </div>

      <div class="launch card">
        <h2>Planer öffnen</h2>
        <p class="muted">
          Trag deinen Content für die Woche ein – mit Plattform, Titel, Status und optionaler Notiz. Alles wird lokal gespeichert.
        </p>
        <div class="launch-actions">
          <button class="btn" type="button" @click="goToPlanner">Zum Content Planer</button>
          <button class="btn ghost" type="button" @click="goBack">Zur Hub-Übersicht</button>
        </div>
      </div>
    </section>

    <section class="cards">
      <article class="card feature-card">
        <div class="feature-icon">📋</div>
        <h3>Post planen</h3>
        <p class="muted">Füge für jeden Tag Beiträge hinzu – mit Plattform, Titel und einer kurzen Notiz. Kein kompliziertes Drag &amp; Drop.</p>
      </article>
      <article class="card feature-card">
        <div class="feature-icon">🏷️</div>
        <h3>Status setzen</h3>
        <p class="muted">Drei klare Stufen: <strong>Entwurf</strong>, <strong>Bereit</strong> und <strong>Gepostet</strong>. Du siehst sofort, was noch offen ist.</p>
      </article>
      <article class="card feature-card">
        <div class="feature-icon">📅</div>
        <h3>Wochen navigieren</h3>
        <p class="muted">Spring zwischen Wochen hin und her. Der heutige Tag ist immer markiert, damit du schnell weißt, wo du stehst.</p>
      </article>
    </section>

    <section class="card steps">
      <div class="section-head">
        <h2>So planst du in 3 Schritten</h2>
        <p class="muted">Schnell starten, kein Onboarding nötig.</p>
      </div>

      <div class="step-list">
        <div class="step">
          <span class="step-num">1</span>
          <div>
            <strong>Tag auswählen</strong>
            <p class="muted">Klicke auf den „+" Button bei einem Wochentag deiner Wahl.</p>
          </div>
        </div>
        <div class="step-sep"></div>
        <div class="step">
          <span class="step-num">2</span>
          <div>
            <strong>Post ausfüllen</strong>
            <p class="muted">Wähle Plattform, gib Titel und Status an – optional noch eine kurze Notiz.</p>
          </div>
        </div>
        <div class="step-sep"></div>
        <div class="step">
          <span class="step-num">3</span>
          <div>
            <strong>Status aktualisieren</strong>
            <p class="muted">Klicke auf eine Karte, um den Status zu ändern – von Entwurf zu Gepostet, wenn's live ist.</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

function goToPlanner() {
  router.push({ name: "content-schedule" });
}

function goBack() {
  router.push({ name: "platforms" });
}
</script>

<style scoped>
.cs-entry {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
}

.hero {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 28px;
  align-items: start;
  padding: 36px;
}

.eyebrow {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brand);
  margin: 0 0 10px;
}

.hero-copy h1 {
  font-size: clamp(1.35rem, 3vw, 1.9rem);
  font-weight: 800;
  margin: 0 0 14px;
  line-height: 1.25;
}

.lead {
  font-size: 1rem;
  line-height: 1.7;
  margin: 0 0 20px;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-points span {
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
  padding: 5px 12px;
  border-radius: 20px;
  font-size: 0.82rem;
  font-weight: 600;
}

.launch {
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 24px;
}

.launch h2 {
  font-size: 1.15rem;
  font-weight: 700;
  margin: 0;
}

.launch p {
  margin: 0;
  font-size: 0.92rem;
  line-height: 1.6;
}

.launch-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* ---- Feature cards ---- */
.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.feature-icon {
  font-size: 1.8rem;
}

.feature-card h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 700;
}

.feature-card p {
  margin: 0;
  line-height: 1.6;
  font-size: 0.9rem;
}

/* ---- Steps ---- */
.steps {
  padding: 32px;
}

.section-head {
  margin-bottom: 24px;
}

.section-head h2 {
  font-size: 1.3rem;
  font-weight: 700;
  margin: 0 0 6px;
}

.section-head p {
  margin: 0;
}

.step-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 0;
}

.step-num {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(47, 99, 255, 0.12);
  color: var(--brand);
  font-size: 0.9rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step div {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.step strong {
  font-size: 0.95rem;
  font-weight: 700;
}

.step p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.5;
}

.step-sep {
  height: 1px;
  background: var(--border);
  margin-left: 48px;
}

/* ---- Global button helpers ---- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 9px 20px;
  border-radius: 10px;
  border: none;
  background: var(--brand);
  color: #fff;
  font-size: 0.9rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.15s;
}

.btn:hover { opacity: 0.88; }

.btn.ghost {
  background: var(--card);
  border: 1.5px solid var(--border);
  color: var(--text);
}

.btn.ghost:hover {
  border-color: var(--brand);
  color: var(--brand);
  opacity: 1;
}

/* ---- Responsive ---- */
@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .cards {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .cs-entry {
    padding: 14px;
    gap: 14px;
  }

  .hero {
    padding: 18px;
  }

  .steps {
    padding: 20px;
  }
}
</style>
