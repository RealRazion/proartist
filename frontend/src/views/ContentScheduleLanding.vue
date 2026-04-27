<template>
  <div class="cs-entry">
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">Content Schedule</p>
        <h1>Plane deinen Content von Montag bis Sonntag – strukturiert & visuell.</h1>
        <p class="muted lead">
          Erstelle Content-Serien mit Header, Parts und Verlinkungen. Ziehe Blöcke per Drag &amp; Drop in
          die Woche und behalte jederzeit den Überblick über Deadlines und Format-Rhythmen.
        </p>
        <div class="hero-points">
          <span>Wochenplanung</span>
          <span>Drag &amp; Drop</span>
          <span>Header · Part · Link</span>
        </div>
      </div>

      <div class="launch card">
        <h2>Planer öffnen</h2>
        <p class="muted">
          Lege Content-Serien an, ordne Parts zu und verknüpfe deine Beiträge – alles in einer übersichtlichen Wochenansicht.
        </p>
        <div class="launch-actions">
          <button class="btn" type="button" @click="goToPlanner">Zum Content Planer</button>
          <button class="btn ghost" type="button" @click="goBack">Zur Hub-Übersicht</button>
        </div>
      </div>
    </section>

    <section class="grid cards">
      <article class="card feature-card">
        <div class="feature-icon">📌</div>
        <h3>Header – Dein Projekt</h3>
        <p class="muted">Ein Header steht für eine Content-Reihe wie „Fix yourself" oder „Top 5". Er spannt sich über beliebige Wochentage.</p>
      </article>
      <article class="card feature-card">
        <div class="feature-icon">📄</div>
        <h3>Part – Der Inhalt</h3>
        <p class="muted">Parts sind einzelne Inhalte innerhalb einer Reihe, z.&nbsp;B. „Zwischenstand" oder „Review". Du benennst sie selbst.</p>
      </article>
      <article class="card feature-card">
        <div class="feature-icon">🔗</div>
        <h3>Link – Die Verlinkung</h3>
        <p class="muted">Links sind Referenzen oder URLs, die du einem Part anfügst – z.&nbsp;B. das fertige Video oder ein Script.</p>
      </article>
    </section>

    <section class="card sample">
      <div class="section-head">
        <div>
          <h2>So funktioniert der Planer</h2>
          <p class="muted">Drei Schritte, um deine Woche zu strukturieren.</p>
        </div>
      </div>

      <div class="sample-grid">
        <div class="sample-step">
          <strong>1. Header ziehen</strong>
          <p class="muted">Ziehe einen Header-Block aus der Palette in den gewünschten Wochentag, um eine neue Content-Reihe anzulegen.</p>
        </div>
        <div class="sample-step">
          <strong>2. Parts zuweisen</strong>
          <p class="muted">Ziehe Parts in den Header-Block des passenden Tages und benenne sie frei, z.&nbsp;B. „Zielankündigung" oder „Review".</p>
        </div>
        <div class="sample-step">
          <strong>3. Links hinzufügen</strong>
          <p class="muted">Füge zu jedem Part beliebig viele Links hinzu – der Block wächst automatisch, um alle Links anzuzeigen.</p>
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
  grid-template-columns: 1fr 340px;
  gap: 32px;
  align-items: start;
  padding: 40px;
}

.eyebrow {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brand);
  margin: 0 0 12px;
}

.hero-copy h1 {
  font-size: clamp(1.4rem, 3vw, 2rem);
  font-weight: 800;
  margin: 0 0 16px;
  line-height: 1.25;
}

.lead {
  font-size: 1.05rem;
  line-height: 1.7;
  margin: 0 0 24px;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-points span {
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
}

.launch {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 28px;
}

.launch h2 {
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0;
}

.launch p {
  margin: 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.launch-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.feature-card {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-icon {
  font-size: 2rem;
}

.feature-card h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 700;
}

.feature-card p {
  margin: 0;
  line-height: 1.6;
  font-size: 0.95rem;
}

.sample {
  padding: 36px;
}

.section-head {
  margin-bottom: 28px;
}

.section-head h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0 0 8px;
}

.section-head p {
  margin: 0;
}

.sample-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
}

.sample-step {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 20px;
  background: var(--bg-soft);
  border-radius: 12px;
}

.sample-step strong {
  font-size: 1rem;
  font-weight: 700;
}

.sample-step p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.6;
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }

  .cards {
    grid-template-columns: 1fr;
  }

  .sample-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .cs-entry {
    padding: 16px;
  }

  .hero {
    padding: 20px;
  }

  .sample {
    padding: 20px;
  }
}
</style>
