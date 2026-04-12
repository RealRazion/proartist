<template>
  <div class="platform-page contest-page">
    <header class="page-hero card">
      <div>
        <p class="eyebrow">UNYQ Contests</p>
        <h1>Wettbewerb, Sichtbarkeit und neue Chancen</h1>
        <p class="lead">
          Hier findest du aktuelle Wettbewerbe, Challenges und alle Anmeldungen rund um Auftritte und Teamaktionen.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="goHome">Zurück zum Hub</button>
      </div>
    </header>

    <section class="highlights card">
      <article>
        <h2>Live Challenges</h2>
        <p>Behalte Bewerbungsfristen, Jury-Entscheidungen und Teambeteiligungen im Blick.</p>
      </article>
      <article>
        <h2>Deine aktuellen Einreichungen</h2>
        <p>Sieh auf einen Blick, welche Projekte noch offen, bestätigt oder blockiert sind.</p>
      </article>
      <article>
        <h2>Team-Performance</h2>
        <p>Vergleiche aktuelle Rankings und entdecke Chancen für dein Team.</p>
      </article>
    </section>

    <section class="cards-grid">
      <article class="card feature-card contest">
        <h3>Live-Übersicht</h3>
        <p>Aktuelle Contest-Stände, Bewerbungsstatus und wichtige Fristen.</p>
      </article>
      <article class="card feature-card pitch">
        <h3>Pitch-Material</h3>
        <p>Speichere Teamvideos, Bilder und Beschreibungen für jede Bewerbung.</p>
      </article>
      <article class="card feature-card collaboration">
        <h3>Team-Kollaboration</h3>
        <p>Verteile Aufgaben an Teammitglieder und arbeite direkt am Wettbewerbspitch.</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
const router = useRouter();
function goHome() {
  router.push({ name: "platforms" });
}
</script>

<style scoped>
.platform-page {
  display: grid;
  gap: 20px;
}
.page-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 28px;
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.14), rgba(251, 191, 36, 0.12));
  border: 1px solid rgba(251, 191, 36, 0.24);
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 12px;
  margin-bottom: 8px;
  color: var(--brand);
}
.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}
.hero-actions {
  display: grid;
  align-items: center;
}
.highlights {
  display: grid;
  gap: 14px;
  padding: 20px;
}
.highlights article {
  padding: 18px;
  border-radius: 16px;
  background: var(--card);
  border: 1px solid var(--border);
}
.cards-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.feature-card {
  padding: 24px;
  border-radius: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.feature-card.contest {
  background: rgba(244, 114, 182, 0.08);
}
.feature-card.pitch {
  background: rgba(59, 130, 246, 0.08);
}
.feature-card.collaboration {
  background: rgba(16, 185, 129, 0.08);
}

:global(.dark) .contest-page .page-hero {
  background: linear-gradient(135deg, rgba(249, 115, 22, 0.18), rgba(251, 191, 36, 0.12));
}
</style>
