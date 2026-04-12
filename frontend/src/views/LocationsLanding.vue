<template>
  <div class="platform-page locations-page">
    <header class="page-hero card">
      <div>
        <p class="eyebrow">UNYQ Locations</p>
        <h1>Orte, Events und Raumplanung</h1>
        <p class="lead">
          Eine eigene Plattform für Locationsuche, Terminplanung und Veranstaltungskoordination.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="goHome">Zurück zum Hub</button>
      </div>
    </header>

    <section class="highlights card">
      <article>
        <h2>Locations finden</h2>
        <p>Verwalte Orte, buchbare Räume und passende Eventflächen für dein Team.</p>
      </article>
      <article>
        <h2>Eventplanung</h2>
        <p>Plane Termine, setze Meilensteine und gebuchte Slots transparent um.</p>
      </article>
      <article>
        <h2>Team-Zugang</h2>
        <p>Gib Locationspezialisten und Produzenten gezielte Zugriffsrechte.</p>
      </article>
    </section>

    <section class="cards-grid">
      <article class="card feature-card maps">
        <h3>Standort-Map</h3>
        <p>Visualisiere verfügbare Orte und merke dir Favoriten.</p>
      </article>
      <article class="card feature-card booking">
        <h3>Buchungsübersicht</h3>
        <p>Behalt alle Reservierungen und Kostenstellen im Griff.</p>
      </article>
      <article class="card feature-card crew">
        <h3>Event-Crew</h3>
        <p>Weise Teamaufgaben für das Location-Management zu.</p>
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
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.14), rgba(74, 222, 128, 0.12));
  border: 1px solid rgba(34, 197, 94, 0.24);
}
.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
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
.feature-card.maps {
  background: rgba(34, 197, 94, 0.08);
}
.feature-card.booking {
  background: rgba(59, 130, 246, 0.08);
}
.feature-card.crew {
  background: rgba(168, 85, 247, 0.08);
}

:global(.dark) .locations-page .page-hero {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(74, 222, 128, 0.12));
}
</style>
