<template>
  <div class="finance-container-page">
    <!-- Hero Header -->
    <header class="finance-hero card">
      <div class="hero-left">
        <div class="tag-pill">
          <span class="icon">💼</span>
          <span>UNYQ Finance Suite</span>
        </div>
        <h1>UNYQ Finance</h1>
        <p class="hero-desc">
          Zentrales Finanzmanagement für Musikschaffende, Produzenten und Agenturen. 
          Einnahmen, GEMA/GVL-Tantiemen, Projektbudgets und Rechnungen an einem Ort.
        </p>

        <div class="hero-actions">
          <button class="btn" type="button" @click="openFinancePlanner">
            📊 Zu den bestehenden Projekt-Budgets
          </button>
          <button class="btn ghost" type="button" @click="showInfoModal = true">
            ℹ️ App-Schnittstelle Info
          </button>
        </div>
      </div>

      <div class="hero-right">
        <div class="finance-status-card">
          <div class="status-indicator-row">
            <span class="pulse-indicator"></span>
            <span class="status-text">Container aktiv &amp; empfangsbereit</span>
          </div>
          <p class="small muted">
            Der Docking-Slot für deine bereitgestellte Finance-Applikation ist vorkonfiguriert 
            und voll responsiv eingerichtet.
          </p>
          <div class="quick-meta-grid">
            <div class="qm-item">
              <span class="qm-val">0,00 €</span>
              <span class="qm-lbl">Gesamt-Cashflow</span>
            </div>
            <div class="qm-item">
              <span class="qm-val">0</span>
              <span class="qm-lbl">Offene Rechnungen</span>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Container Docking Station -->
    <main class="finance-app-dock card">
      <div class="dock-header">
        <div class="dock-title-box">
          <span class="dock-icon">⚡</span>
          <div>
            <h3>Finance App Docking Container</h3>
            <p class="muted small">Vorbereitete Zone für deine externe oder integrierte Finance-App</p>
          </div>
        </div>
        <div class="dock-badge">Bereit zur Code-Injektion</div>
      </div>

      <!-- App Mount Point Placeholder -->
      <div class="app-mount-placeholder">
        <div class="mount-grid-preview">
          <!-- Widget Preview 1 -->
          <div class="mount-card">
            <div class="mount-head">
              <span class="mount-ico">📈</span>
              <span class="mount-name">Monatlicher Cashflow</span>
            </div>
            <div class="mount-skeleton-bar" style="width: 80%"></div>
            <div class="mount-skeleton-bar" style="width: 50%"></div>
            <div class="mount-skeleton-chart">
              <span class="bar" style="height: 35%"></span>
              <span class="bar" style="height: 60%"></span>
              <span class="bar" style="height: 45%"></span>
              <span class="bar" style="height: 80%"></span>
              <span class="bar" style="height: 65%"></span>
              <span class="bar active" style="height: 90%"></span>
            </div>
          </div>

          <!-- Widget Preview 2 -->
          <div class="mount-card">
            <div class="mount-head">
              <span class="mount-ico">🧾</span>
              <span class="mount-name">Rechnungs- &amp; Beleg-Manager</span>
            </div>
            <div class="mount-skeleton-bar" style="width: 70%"></div>
            <div class="mount-skeleton-bar" style="width: 40%"></div>
            <div class="mount-table-rows">
              <div class="table-row-skeleton"></div>
              <div class="table-row-skeleton"></div>
              <div class="table-row-skeleton"></div>
            </div>
          </div>

          <!-- Widget Preview 3 -->
          <div class="mount-card">
            <div class="mount-head">
              <span class="mount-ico">💳</span>
              <span class="mount-name">Konten &amp; Wallet Sync</span>
            </div>
            <div class="mount-skeleton-bar" style="width: 60%"></div>
            <div class="mount-skeleton-bar" style="width: 45%"></div>
            <div class="wallet-chip">
              <span>UNYQ Treasury Wallet</span>
              <strong>Aktiviert</strong>
            </div>
          </div>
        </div>

        <div class="mount-callout">
          <div class="callout-icon">✨</div>
          <div class="callout-text">
            <strong>Bereit für deinen App-Inhalt!</strong>
            <p>
              Sobald du den Code deiner bestehenden Finance-App hier einfügst, wird dieser Container 
              automatisch durch deine interaktiven Dashboards, Bankkonten-Übersichten und Buchhaltungs-Tools ersetzt.
            </p>
          </div>
        </div>
      </div>
    </main>

    <!-- Info Modal -->
    <div v-if="showInfoModal" class="modal-overlay" @click.self="showInfoModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>UNYQ Finance Container Details</h3>
          <button class="btn ghost tiny" @click="showInfoModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p>
            Dieser Container ist so aufgebaut, dass deine Finance-App via Vue-Komponente, Iframe, 
            oder nativem Script-Import nahtlos gerendert werden kann.
          </p>
          <ul class="info-list">
            <li>✓ Vollständige Design-Token-Vererbung (Dark &amp; Light Mode)</li>
            <li>✓ Sichere Authentifizierungs-Token (JWT) übergeben</li>
            <li>✓ Responsives Layout für Mobile &amp; Desktop</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const showInfoModal = ref(false);

function openFinancePlanner() {
  router.push({ name: "finance" });
}
</script>

<style scoped>
.finance-container-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1240px;
  margin: 0 auto;
  padding: 8px 0 60px;
}

/* Hero */
.finance-hero {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top left, rgba(16, 185, 129, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(52, 211, 153, 0.2);
  position: relative;
  overflow: hidden;
}

.tag-pill {
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

.finance-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #6ee7b7 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 24px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Status Card */
.finance-status-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(52, 211, 153, 0.2);
  border-radius: 18px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.status-indicator-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.pulse-indicator {
  width: 10px;
  height: 10px;
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

.status-text {
  font-size: 13px;
  font-weight: 700;
  color: #34d399;
}

.quick-meta-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 14px;
}

.qm-item {
  display: flex;
  flex-direction: column;
}

.qm-val {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
}

.qm-lbl {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

/* Docking Station */
.finance-app-dock {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 24px;
  border: 2px dashed rgba(52, 211, 153, 0.35);
  background: rgba(15, 23, 42, 0.45);
}

.dock-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 18px;
}

.dock-title-box {
  display: flex;
  align-items: center;
  gap: 14px;
}

.dock-icon {
  font-size: 26px;
  background: rgba(16, 185, 129, 0.15);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.dock-title-box h3 {
  margin: 0 0 2px;
  font-size: 1.15rem;
}

.dock-badge {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
  padding: 5px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

/* App Mount Placeholder */
.app-mount-placeholder {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mount-grid-preview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.mount-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mount-head {
  display: flex;
  align-items: center;
  gap: 8px;
}

.mount-ico {
  font-size: 18px;
}

.mount-name {
  font-weight: 600;
  font-size: 13px;
}

.mount-skeleton-bar {
  height: 8px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 4px;
}

.mount-skeleton-chart {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  height: 70px;
  padding-top: 10px;
}

.mount-skeleton-chart .bar {
  flex: 1;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
}

.mount-skeleton-chart .bar.active {
  background: #10b981;
}

.mount-table-rows {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}

.table-row-skeleton {
  height: 18px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 4px;
}

.wallet-chip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: rgba(16, 185, 129, 0.08);
  border-radius: 8px;
  border: 1px solid rgba(16, 185, 129, 0.2);
  font-size: 12px;
  margin-top: 8px;
}

.wallet-chip strong {
  color: #34d399;
}

/* Callout */
.mount-callout {
  display: flex;
  align-items: center;
  gap: 18px;
  padding: 18px 24px;
  background: linear-gradient(90deg, rgba(16, 185, 129, 0.12), rgba(59, 130, 246, 0.08));
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.callout-icon {
  font-size: 32px;
}

.callout-text strong {
  font-size: 1.05rem;
  display: block;
  margin-bottom: 4px;
}

.callout-text p {
  margin: 0;
  color: var(--muted);
  font-size: 13.5px;
  line-height: 1.5;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 500px;
  width: 100%;
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.info-list {
  padding-left: 20px;
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13.5px;
}

@media (max-width: 900px) {
  .finance-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
