<template>
  <div class="home">
    <header class="hero card">
      <div class="hero-copy">
        <p class="tag">Welcome to ProArtist</p>
        <h1>Die Schaltzentrale für Artists, Producer &amp; Teams</h1>
        <p class="lead">
          Manage Projekte, Tasks, Chats und Releases in einem klaren Workflow. Alles an einem Ort - live, sicher
          und kollaborativ.
        </p>
        <div class="hero-actions">
          <router-link class="btn" to="/login">Login</router-link>
          <router-link class="btn ghost" to="/register">Zugang anfragen</router-link>
          <span class="muted">Einladung nach Anfrage durch das Team.</span>
        </div>
      </div>
      <div class="hero-visual">
        <div class="stats card">
          <div>
            <span>Artists</span>
            <strong>150+</strong>
          </div>
          <div>
            <span>Projekte</span>
            <strong>320</strong>
          </div>
          <div>
            <span>Nachrichten</span>
            <strong>Live</strong>
          </div>
        </div>
        <div class="bubble">Chat in Echtzeit</div>
        <div class="bubble bubble--secondary">Workflows im Griff</div>
      </div>
    </header>

    <section class="features">
      <div class="feature card">
        <h3>Team Dashboard</h3>
        <p>Alle Kennzahlen und Aktionen auf einen Blick - inklusive Requests, Verträge und Payments.</p>
      </div>
      <div class="feature card">
        <h3>Profilnetzwerk</h3>
        <p>Entdecke Talente nach Rollen, Genre und Standort und starte direkt einen Chat.</p>
      </div>
      <div class="feature card">
        <h3>Projektplanung</h3>
        <p>Organisiere Projekte und Tasks, weise Verantwortliche zu und verfolge den Status.</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 32px 16px 64px;
  max-width: 1080px;
  margin: 0 auto;
}
.hero {
  display: grid;
  gap: 24px;
  align-items: center;
  padding: 32px;
  background: linear-gradient(135deg, rgba(75, 91, 255, 0.12), rgba(124, 58, 237, 0.18));
  border: 1px solid rgba(112, 130, 255, 0.2);
}
.hero-copy {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.tag {
  font-size: 14px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--brand);
  font-weight: 600;
}
.hero h1 {
  margin: 0;
  font-size: clamp(2.2rem, 4vw, 3rem);
}
.lead {
  margin: 0;
  color: var(--muted);
  max-width: 520px;
  line-height: 1.6;
}
.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}
.hero-visual {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}
.hero-visual .stats {
  display: grid;
  gap: 12px;
  padding: 24px;
  min-width: 240px;
  background: rgba(15, 21, 37, 0.75);
  color: #fff;
}
.hero-visual .stats strong {
  font-size: 1.4rem;
}
.bubble {
  position: absolute;
  top: -18px;
  right: -12px;
  background: rgba(75, 91, 255, 0.92);
  color: #fff;
  padding: 10px 16px;
  border-radius: 20px;
  font-weight: 600;
  box-shadow: 0 12px 24px rgba(75, 91, 255, 0.25);
}
.bubble--secondary {
  top: auto;
  bottom: -18px;
  right: -60px;
  background: rgba(124, 58, 237, 0.95);
}
.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 18px;
}
.feature h3 {
  margin-top: 0;
}
.feature p {
  margin-bottom: 0;
  color: var(--muted);
}

@media (max-width: 900px) {
  .hero {
    grid-template-columns: 1fr;
    text-align: center;
  }
  .hero-copy {
    align-items: center;
  }
  .lead {
    max-width: none;
  }
  .hero-visual {
    padding: 16px 0;
  }
  .bubble,
  .bubble--secondary {
    position: static;
    display: inline-flex;
    margin: 6px;
  }
}
</style>
