<template>
  <div class="platform-landing">
    <header class="hero card">
      <div class="hero-copy">
        <p class="tag">UNYQ Startseite</p>
        <h1>Wähle deine UNYQ-Plattform</h1>
        <p class="lead">
          Diese Seite ist dein privater Einstieg in die UNYQ-Welten. Hier findest du später die unterschiedlichen Plattformen als klar strukturierte Auswahl.
        </p>
      </div>
    </header>

    <section class="platform-grid">
      <article class="platform-card platform-card--contests card">
        <div>
          <span class="card-label">UNYQ Contests</span>
          <h2>Wettbewerbe &amp; Challenges</h2>
          <p>Ein eigener Bereich für Wettbewerbe, Bewerbungen und kreative Aktionen.</p>
        </div>
        <button class="btn" type="button" @click="openPlatform('contests')">
          Zur Contests-Ansicht
        </button>
      </article>

      <article class="platform-card platform-card--music card">
        <div>
          <span class="card-label">UNYQ Music Manager</span>
          <h2>Musikprojekte &amp; Releases</h2>
          <p>Verwalte Songs, Projekte und Releases in einer klaren Musikübersicht.</p>
        </div>
        <button class="btn" type="button" @click="openPlatform('music')">
          Zum Music Manager
        </button>
      </article>

      <article class="platform-card platform-card--locations card">
        <div>
          <span class="card-label">UNYQ Locations</span>
          <h2>Locations &amp; Events</h2>
          <p>Verwalte Orte, Termine und Veranstaltungsoptionen für dein Team.</p>
        </div>
        <button class="btn" type="button" @click="openPlatform('locations')">
          Zu Locations
        </button>
      </article>
    </section>

    <footer class="platform-note card">
      <p>
        Diese Seite nutzt die Team-Farbwelt von UNYQ, bleibt aber bewusst minimal.
        Später kann sie als Hub zu eigenen Plattformen wie Contests, Music Manager und Locations dienen.
      </p>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { showToast } = useToast();

function openPlatform(platform) {
  const mapping = {
    contests: "/app/projects?platform=contests",
    music: "/app/projects?platform=music-manager",
    locations: "/app/activity",
  };
  const path = mapping[platform];
  if (path) {
    router.push(path);
    return;
  }
  showToast("Diese Plattform wird bald verfügbar sein", "info");
}
</script>

<style scoped>
.platform-landing {
  max-width: 1080px;
  margin: 0 auto;
  padding: 36px 20px 60px;
}

.hero {
  padding: 32px;
  background: linear-gradient(135deg, rgba(47, 99, 255, 0.16), rgba(6, 182, 212, 0.12));
  border: 1px solid rgba(47, 99, 255, 0.18);
}

.tag {
  display: inline-flex;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(6, 182, 212, 0.12);
  color: var(--brand);
  font-weight: 700;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.hero h1 {
  margin: 18px 0 12px;
  font-size: clamp(2rem, 2.8vw, 3rem);
}

.lead {
  margin: 0;
  max-width: 690px;
  color: var(--muted);
  line-height: 1.72;
}

.platform-grid {
  display: grid;
  gap: 20px;
  margin-top: 28px;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.platform-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 260px;
  gap: 22px;
  padding: 28px;
  border: 1px solid rgba(47, 99, 255, 0.16);
  background: rgba(255, 255, 255, 0.88);
}

.platform-card--contests {
  background: rgba(47, 99, 255, 0.06);
}

.platform-card--music {
  background: rgba(6, 182, 212, 0.06);
}

.platform-card--locations {
  background: rgba(76, 196, 116, 0.08);
}

.card-label {
  display: inline-flex;
  margin-bottom: 14px;
  color: var(--brand);
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.platform-card h2 {
  margin: 0;
  font-size: 1.45rem;
}

.platform-card p {
  margin: 0;
  color: var(--muted);
  line-height: 1.6;
}

.platform-card .btn {
  width: 100%;
  justify-content: center;
}

.platform-note {
  margin-top: 24px;
  padding: 22px;
  border: 1px solid rgba(47, 99, 255, 0.12);
  background: rgba(247, 250, 255, 0.9);
}

.platform-note p {
  margin: 0;
  color: var(--muted);
}

@media (max-width: 720px) {
  .platform-landing {
    padding: 24px 16px 40px;
  }

  .hero {
    padding: 24px;
  }

  .platform-card {
    padding: 22px;
  }
}
</style>
