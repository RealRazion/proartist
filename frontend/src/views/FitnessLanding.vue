<template>
  <div class="fitness-entry">
    <section class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">Fitness</p>
        <h1>Kalorien tracken, Verbrauch verstehen, Essen einfacher planen.</h1>
        <p class="muted lead">
          Der Fitness-Bereich kombiniert Tagesverbrauch, Kalorien-Tracking, einen einfachen Plus/Minus-Rechner
          und schnelle Essensideen auf einer klaren Oberfläche.
        </p>
        <div class="hero-points">
          <span>Kcal Tracker</span>
          <span>TDEE & Grundumsatz</span>
          <span>Frühstück bis Snack</span>
        </div>
      </div>

      <div class="launch card">
        <h2>Direkt starten</h2>
        <p class="muted">
          Du kannst sofort mit deinem Tagesprofil, Mahlzeiten und Essensideen arbeiten. Die Werte werden lokal im Browser gespeichert.
        </p>
        <div class="launch-actions">
          <button class="btn" type="button" @click="goToTracker">Zum Fitness Tracker</button>
          <button class="btn ghost" type="button" @click="goBack">Zur Hub-Übersicht</button>
        </div>
      </div>
    </section>

    <section class="grid cards">
      <article class="card feature-card burn">
        <h3>Verbrauch</h3>
        <p class="muted">Gewicht, Größe, Alter, Aktivität und Ziel zusammenführen statt grob zu raten.</p>
      </article>
      <article class="card feature-card track">
        <h3>Tages-Tracking</h3>
        <p class="muted">Frühstück, Lunch, Dinner und Snacks eintragen und direkt gegen das Tagesziel sehen.</p>
      </article>
      <article class="card feature-card ideas">
        <h3>Essensideen</h3>
        <p class="muted">Für jede Tageszeit grobe Ideen mit kcal-Werten, die du später selbst feinjustieren kannst.</p>
      </article>
    </section>

    <section class="card sample">
      <div class="section-head">
        <div>
          <h2>So ist der Bereich gedacht</h2>
          <p class="muted">Nicht medizinisch kompliziert, sondern schnell hilfreich im Alltag.</p>
        </div>
      </div>

      <div class="sample-grid">
        <div class="sample-step">
          <strong>1. Profil setzen</strong>
          <p class="muted">Kg, cm, Alter, Geschlecht und Aktivität eintragen.</p>
        </div>
        <div class="sample-step">
          <strong>2. Tagesziel prüfen</strong>
          <p class="muted">Grundumsatz, Gesamtverbrauch und dein Ziel-Defizit oder Überschuss sehen.</p>
        </div>
        <div class="sample-step">
          <strong>3. Essen planen</strong>
          <p class="muted">Ideen auswählen oder eigene Mahlzeiten hinzufügen und den Tag sauber gegenrechnen.</p>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";

const router = useRouter();

function goToTracker() {
  router.push({ name: "fitness" });
}

function goBack() {
  router.push({ name: "platforms" });
}
</script>

<style scoped>
.fitness-entry {
  display: grid;
  gap: 18px;
}

.hero {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
  gap: 18px;
  padding: 22px;
  background:
    radial-gradient(circle at top right, rgba(34, 197, 94, 0.16), transparent 38%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(241, 255, 246, 0.92));
}

.hero-copy {
  display: grid;
  gap: 14px;
  align-content: start;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #15803d;
  font-weight: 700;
}

.lead {
  max-width: 64ch;
}

.hero-points {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.hero-points span {
  padding: 9px 12px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.08);
  border: 1px solid rgba(34, 197, 94, 0.16);
  font-size: 14px;
  font-weight: 600;
}

.launch {
  display: grid;
  gap: 12px;
  align-content: start;
  background: rgba(255, 255, 255, 0.82);
}

.launch-actions,
.cards,
.sample-grid {
  display: grid;
  gap: 14px;
}

.cards {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.feature-card {
  min-height: 160px;
}

.feature-card.burn {
  background: linear-gradient(180deg, rgba(16, 185, 129, 0.1), transparent);
}

.feature-card.track {
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.1), transparent);
}

.feature-card.ideas {
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.1), transparent);
}

.sample-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.sample-step {
  padding: 16px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
}

@media (max-width: 900px) {
  .hero,
  .cards,
  .sample-grid {
    grid-template-columns: 1fr;
  }
}
</style>
