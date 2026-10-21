<template>
  <div class="home">
    <header class="hero card">
      <div class="hero-copy">
        <p class="tag">Welcome to UNYQ</p>
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
        <span class="feat-icon">🎹</span>
        <h3>UNYQ ProArtist</h3>
        <p>Kuratierte Arbeitsoberfläche für Projekte, Tasks, Timeline, Reviews und Team-Workflows.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">🎧</span>
        <h3>UNYQ Music</h3>
        <p>Exklusiver Music Player für unreleased VIP-Drops, Studio Cuts und Artist-Präsentationen.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">📦</span>
        <h3>UNYQ Library</h3>
        <p>100% Free &amp; Open Source Sound-Bank mit 808s, Drum-Kits, Stems und Serum-Presets für Producer.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">💰</span>
        <h3>UNYQ Finance</h3>
        <p>Zentraler Cashflow, Tantiemen, Projektbudgets und Rechnungsverwaltung.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">💎</span>
        <h3>UNYQ Earn</h3>
        <p>Verdiene an Empfehlungen mit bis zu 30% Lifetime-Provision im Partnerprogramm.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">🎨</span>
        <h3>UNYQ Designs</h3>
        <p>Official Merch Drops, Heavyweight Studio-Streetwear und limitierte Vinyl-Essentials.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">💬</span>
        <h3>UNYQ Forum</h3>
        <p>Community-Austausch zu Beatmaking, Mixing, Feedback und Collab-Suche.</p>
      </div>
      <div class="feature card">
        <span class="feat-icon">🌐</span>
        <h3>UNYQ Extra</h3>
        <p>Zentrales Verzeichnis aller Spezial-Tools, Turniere, Locations und offizieller Social Media.</p>
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
  overflow: hidden;
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
  line-height: 1.15;
  overflow-wrap: break-word;
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
  width: min(100%, 280px);
  background: var(--card);
  color: var(--text);
  border: 1px solid var(--border);
  box-shadow: var(--shadow-strong);
  border-radius: 18px;
}
:global(.dark) .hero-visual .stats {
  background: rgba(15, 21, 37, 0.85);
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 18px;
}
.feat-icon {
  font-size: 28px;
  display: inline-block;
  margin-bottom: 8px;
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
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }
  .bubble,
  .bubble--secondary {
    position: static;
    display: inline-flex;
    margin: 6px;
    max-width: 100%;
    text-align: center;
    white-space: normal;
  }
}

@media (max-width: 520px) {
  .home {
    gap: 24px;
    padding: 20px 12px 48px;
  }
  .hero {
    padding: 24px 18px;
    gap: 20px;
  }
  .hero h1 {
    font-size: clamp(2rem, 8vw, 2.7rem);
  }
  .hero-actions {
    width: 100%;
    justify-content: center;
  }
  .hero-visual {
    width: 100%;
  }
  .hero-visual .stats {
    min-width: 0;
  }
}
</style>
