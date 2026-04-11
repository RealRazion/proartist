<template>
  <div class="platform-page music-page">
    <header class="page-hero card">
      <div>
        <p class="eyebrow">UNYQ Music Manager</p>
        <h1>Musikprojekte neu denken</h1>
        <p class="lead">
          Ein eigener Musikbereich für Songs, Releases, Team-Workflows und Produktionstracking.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="goHome">Zurück zum Hub</button>
      </div>
    </header>

    <section class="highlights card">
      <article>
        <h2>Projekt-Flow</h2>
        <p>Verwalte Songs, Versionen und Release-Deadlines in einer visuellen Übersicht.</p>
      </article>
      <article>
        <h2>Team-Kooperation</h2>
        <p>Weise Musikern, Produzenten und Locations eigene Rollen zu und koordiniere Kompositionen.</p>
      </article>
      <article>
        <h2>Release-Plan</h2>
        <p>Behalte Mix-, Master- und Veröffentlichungstermine im Blick.</p>
      </article>
    </section>

    <section class="cards-grid">
      <article class="card feature-card composer">
        <h3>Song-Bibliothek</h3>
        <p>Organisiere Ideas, Demos und fertige Tracks als eigenständige Assets.</p>
      </article>
      <article class="card feature-card release">
        <h3>Release Planner</h3>
        <p>Setze Veröffentlichungsstrategien und verknüpfe Tasks mit jedem Release.</p>
      </article>
      <article class="card feature-card sync">
        <h3>Team Sync</h3>
        <p>Synchronisiere kreative Schritte zwischen Produzenten, Künstlern und Support.</p>
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
  background: linear-gradient(135deg, rgba(6, 182, 212, 0.14), rgba(14, 165, 233, 0.12));
  border: 1px solid rgba(14, 165, 233, 0.24);
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
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(15, 23, 42, 0.08);
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
.feature-card.composer {
  background: rgba(59, 130, 246, 0.08);
}
.feature-card.release {
  background: rgba(168, 85, 247, 0.08);
}
.feature-card.sync {
  background: rgba(34, 197, 94, 0.08);
}
</style>