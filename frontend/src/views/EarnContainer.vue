<template>
  <div class="earn-container-page">
    <!-- Top Hero Section -->
    <header class="earn-hero card">
      <div class="hero-content">
        <div class="hero-badge">
          <span class="pulse-dot"></span>
          <span>UNYQ Affiliate & Partner Program</span>
        </div>
        <h1>UNYQ Earn</h1>
        <p class="hero-lead">
          Empfehle UNYQ weiter und verdiene an jedem gewonnenen Creator, Producer und Label. 
          Transparente Provisionen, lebenslange Beteiligungen und sofortige Auszahlungen.
        </p>
        <div class="hero-stats-row">
          <div class="stat-bubble">
            <span class="stat-val">bis zu 30%</span>
            <span class="stat-lbl">Lifetime Provision</span>
          </div>
          <div class="stat-bubble">
            <span class="stat-val">30 Tage</span>
            <span class="stat-lbl">Cookie Laufzeit</span>
          </div>
          <div class="stat-bubble">
            <span class="stat-val">Monatlich</span>
            <span class="stat-lbl">SEPA & PayPal Payout</span>
          </div>
        </div>
      </div>
      <div class="hero-side">
        <div class="action-card card">
          <span class="card-icon">🚀</span>
          <h3>Dein persönlicher Partnerlink</h3>
          <p class="muted small">Teile diesen Link auf Social Media, YouTube oder direkt mit Artists.</p>
          <div class="ref-link-box">
            <input type="text" readonly :value="referralLink" class="input ref-input" />
            <button class="btn btn-copy" type="button" @click="copyReferralLink">
              {{ copied ? "✓ Kopiert!" : "Kopieren" }}
            </button>
          </div>
          <div class="social-share-row">
            <button class="social-btn" @click="shareOn('whatsapp')">💬 WhatsApp</button>
            <button class="social-btn" @click="shareOn('twitter')">🐦 X / Twitter</button>
            <button class="social-btn" @click="shareOn('telegram')">✈️ Telegram</button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Container Notice / Placeholder Section -->
    <section class="container-status-banner card">
      <div class="status-left">
        <div class="pulse-icon">⚡</div>
        <div>
          <h3>UNYQ Earn — Container Vorbereitung</h3>
          <p class="muted">
            Dieser Bereich ist als Container vorbereitet. Das vollautomatische Affiliate-Tracking, 
            Echtzeit-Conversion-Dashboards und automatische Rechnungsstellung werden hier angebunden.
          </p>
        </div>
      </div>
      <div class="status-right">
        <span class="chip-status ready">Container Aktiv</span>
      </div>
    </section>

    <!-- Dashboard Preview -->
    <div class="dash-preview-grid">
      <!-- Card 1 -->
      <div class="card metric-card">
        <div class="metric-head">
          <span class="metric-icon">💰</span>
          <span class="metric-label">Verfügbares Guthaben</span>
        </div>
        <div class="metric-value">0,00 €</div>
        <p class="metric-sub">Nächster Payout-Lauf: 1. des Monats</p>
        <button class="btn ghost btn-sm" @click="requestPayout" disabled>
          Auszahlung anfordern (ab 25 €)
        </button>
      </div>

      <!-- Card 2 -->
      <div class="card metric-card">
        <div class="metric-head">
          <span class="metric-icon">👥</span>
          <span class="metric-label">Aktive Vermittlungen</span>
        </div>
        <div class="metric-value">0</div>
        <p class="metric-sub">0 Klicks in den letzten 30 Tagen</p>
        <div class="progress-bar">
          <div class="progress-fill" style="width: 0%"></div>
        </div>
      </div>

      <!-- Card 3 -->
      <div class="card metric-card">
        <div class="metric-head">
          <span class="metric-icon">🏆</span>
          <span class="metric-label">Dein Partner-Status</span>
        </div>
        <div class="metric-value badge-tier">BRONZE</div>
        <p class="metric-sub">Noch 3 Referrals bis SILBER (20% Provision)</p>
        <div class="tier-pills">
          <span class="tp active">Bronze 10%</span>
          <span class="tp">Silber 20%</span>
          <span class="tp">Gold VIP 30%</span>
        </div>
      </div>
    </div>

    <!-- Tier Progression Table -->
    <section class="card tiers-section">
      <div class="section-header">
        <h2>Partner-Stufen &amp; Vergütung</h2>
        <p class="muted">Steige automatisch auf, je mehr Creator deiner Einladung folgen.</p>
      </div>
      <div class="tiers-grid">
        <div class="tier-box">
          <div class="tier-top">
            <span class="tier-badge bronze">Bronze</span>
            <h4>Einsteiger</h4>
            <div class="tier-rate">10%</div>
            <p class="muted small">Für jeden vermittelten UNYQ Pro Plan</p>
          </div>
          <ul class="tier-features">
            <li>✓ Basis-Partnerlink</li>
            <li>✓ Monatliche Auszahlung</li>
            <li>✓ Klick-Statistiken</li>
          </ul>
        </div>

        <div class="tier-box popular">
          <div class="tier-highlight">Am beliebtesten</div>
          <div class="tier-top">
            <span class="tier-badge silver">Silber</span>
            <h4>Fortgeschritten</h4>
            <div class="tier-rate">20%</div>
            <p class="muted small">Ab 5 aktiven Creator-Referrals</p>
          </div>
          <ul class="tier-features">
            <li>✓ 20% Lifetime-Provision</li>
            <li>✓ Eigener Promo-Code für 10% Rabatt</li>
            <li>✓ Priorisierter Support</li>
            <li>✓ Marketing-Kit mit Bannern</li>
          </ul>
        </div>

        <div class="tier-box">
          <div class="tier-top">
            <span class="tier-badge gold">Gold VIP</span>
            <h4>Elite Partner</h4>
            <div class="tier-rate">30%</div>
            <p class="muted small">Ab 20 aktiven Creator-Referrals</p>
          </div>
          <ul class="tier-features">
            <li>✓ 30% Lifetime-Provision</li>
            <li>✓ Kostenloser UNYQ Pro Zugang</li>
            <li>✓ Co-Marketing &amp; Social Shoutouts</li>
            <li>✓ Direkter Draht zum Gründerteam</li>
          </ul>
        </div>
      </div>
    </section>

    <!-- FAQ Accordion -->
    <section class="card faq-section">
      <h3>Häufige Fragen zu UNYQ Earn</h3>
      <div class="faq-list">
        <details class="faq-item">
          <summary>Wie funktioniert die Abrechnung der Provisionen?</summary>
          <p>
            Sobald ein Nutzer über deinen Link einen kostenpflichtigen Plan bucht, wird die Provision
            deinem virtuellen Konto gutgeschrieben. Nach einer 14-tägigen Sicherheitsfrist kannst du dir
            das Guthaben ab 25 € per SEPA-Überweisung oder PayPal auszahlen lassen.
          </p>
        </details>
        <details class="faq-item">
          <summary>Wann startet das Affiliate-Tracking vollständig?</summary>
          <p>
            Der Container ist live vorbereitet. Vollständige Tracking-Pixel und benutzerdefinierte Rabatt-Codes
            werden mit dem nächsten Plattform-Update scharfgeschaltet.
          </p>
        </details>
        <details class="faq-item">
          <summary>Darf ich bezahlte Anzeigen schalten?</summary>
          <p>
            Ja, Social Ads und Content Marketing sind erlaubt. Marken-Keyword-Bidding auf „UNYQ“ bei Google Ads
            ist jedoch untersagt.
          </p>
        </details>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { profile: me } = useCurrentProfile();
const { showToast } = useToast();

const copied = ref(false);

const referralCode = computed(() => {
  const username = me.value?.username || me.value?.name || "artist";
  return username.toLowerCase().replace(/[^a-z0-9]/g, "");
});

const referralLink = computed(() => {
  return `https://unyq.app/join?ref=${referralCode.value}`;
});

function copyReferralLink() {
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(referralLink.value);
    copied.value = true;
    showToast("Referral-Link in Zwischenablage kopiert! 📋", "success");
    setTimeout(() => {
      copied.value = false;
    }, 2500);
  } else {
    showToast(`Dein Link: ${referralLink.value}`);
  }
}

function shareOn(platform) {
  const text = encodeURIComponent("Check UNYQ ab — die beste Plattform für Artists & Producer: ");
  const url = encodeURIComponent(referralLink.value);
  if (platform === "whatsapp") {
    window.open(`https://api.whatsapp.com/send?text=${text}${url}`, "_blank");
  } else if (platform === "twitter") {
    window.open(`https://twitter.com/intent/tweet?text=${text}&url=${url}`, "_blank");
  } else if (platform === "telegram") {
    window.open(`https://t.me/share/url?url=${url}&text=${text}`, "_blank");
  }
}

function requestPayout() {
  showToast("Mindestbetrag von 25,00 € noch nicht erreicht.", "info");
}
</script>

<style scoped>
.earn-container-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 8px 0 60px;
}

/* Hero Section */
.earn-hero {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top left, rgba(79, 70, 229, 0.16), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
  border: 1px solid rgba(124, 161, 255, 0.18);
  position: relative;
  overflow: hidden;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
  animation: pulse 1.8s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.8; }
}

.earn-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-lead {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 24px;
}

.hero-stats-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-bubble {
  display: flex;
  flex-direction: column;
  padding: 10px 16px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
}

.stat-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #60a5fa;
}

.stat-lbl {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.action-card {
  padding: 24px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(124, 161, 255, 0.2);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card-icon {
  font-size: 28px;
}

.action-card h3 {
  margin: 0;
  font-size: 1.1rem;
}

.ref-link-box {
  display: flex;
  gap: 8px;
  align-items: center;
}

.ref-input {
  font-family: monospace;
  font-size: 13px;
  background: rgba(0, 0, 0, 0.3);
}

.btn-copy {
  white-space: nowrap;
  padding: 10px 18px;
}

.social-share-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 4px;
}

.social-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: var(--text);
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.social-btn:hover {
  background: rgba(124, 161, 255, 0.15);
  border-color: rgba(124, 161, 255, 0.3);
}

/* Status Banner */
.container-status-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 28px;
  background: linear-gradient(90deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.08));
  border-left: 4px solid #6366f1;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.pulse-icon {
  font-size: 28px;
  background: rgba(99, 102, 241, 0.2);
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.container-status-banner h3 {
  margin: 0 0 4px;
  font-size: 1.05rem;
}

.container-status-banner p {
  margin: 0;
  font-size: 13px;
}

.chip-status.ready {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 12px;
  white-space: nowrap;
}

/* Metrics Grid */
.dash-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.metric-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.metric-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.metric-icon {
  font-size: 22px;
}

.metric-label {
  font-size: 13px;
  color: var(--muted);
  font-weight: 600;
}

.metric-value {
  font-size: 2.2rem;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.metric-sub {
  font-size: 12px;
  color: var(--muted);
  margin: 0 0 8px;
}

.progress-bar {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
}

.badge-tier {
  font-size: 1.5rem;
  color: #cd7f32;
  font-weight: 900;
}

.tier-pills {
  display: flex;
  gap: 6px;
  margin-top: 6px;
}

.tp {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.tp.active {
  background: rgba(205, 127, 50, 0.2);
  color: #e59866;
  font-weight: 700;
  border: 1px solid rgba(205, 127, 50, 0.4);
}

.btn-sm {
  min-height: 34px;
  padding: 6px 14px;
  font-size: 13px;
  margin-top: auto;
}

/* Tiers Section */
.tiers-section {
  padding: 32px;
}

.section-header {
  margin-bottom: 28px;
}

.section-header h2 {
  margin: 0 0 6px;
  font-size: 1.4rem;
}

.tiers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.tier-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  position: relative;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.tier-box:hover {
  transform: translateY(-2px);
  border-color: rgba(124, 161, 255, 0.35);
}

.tier-box.popular {
  border-color: #6366f1;
  background: linear-gradient(180deg, rgba(99, 102, 241, 0.08) 0%, rgba(255, 255, 255, 0.02) 100%);
}

.tier-highlight {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #6366f1;
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 999px;
  text-transform: uppercase;
}

.tier-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  margin-bottom: 8px;
}

.tier-badge.bronze { background: rgba(205, 127, 50, 0.2); color: #e59866; }
.tier-badge.silver { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; }
.tier-badge.gold { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }

.tier-top h4 {
  margin: 0;
  font-size: 1.1rem;
}

.tier-rate {
  font-size: 2.2rem;
  font-weight: 900;
  margin: 10px 0 4px;
  color: var(--text);
}

.tier-features {
  list-style: none;
  padding: 0;
  margin: 20px 0 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 13px;
  color: var(--muted);
  border-top: 1px solid var(--border);
  padding-top: 18px;
}

.tier-features li {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* FAQ */
.faq-section {
  padding: 28px;
}

.faq-section h3 {
  margin: 0 0 18px;
  font-size: 1.2rem;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.faq-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 12px 18px;
  background: rgba(255, 255, 255, 0.02);
}

.faq-item summary {
  font-weight: 600;
  cursor: pointer;
  outline: none;
}

.faq-item p {
  margin: 10px 0 0;
  color: var(--muted);
  font-size: 13.5px;
  line-height: 1.55;
}

@media (max-width: 900px) {
  .earn-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
