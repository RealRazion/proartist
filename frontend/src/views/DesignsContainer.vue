<template>
  <div class="designs-container-page">
    <!-- Hero / Drop Showcase -->
    <header class="designs-hero card">
      <div class="hero-left">
        <div class="tag-pill">
          <span class="sparkle">✨</span>
          <span>UNYQ Official Merchandise &amp; Streetwear</span>
        </div>
        <h1>UNYQ Designs</h1>
        <p class="hero-desc">
          Limitierte Drops, hochwertige Signature-Pieces und Artist-Collaborations. 
          Entworfen für das Studio, die Stage und die Straße.
        </p>

        <div class="drop-countdown-box">
          <div class="drop-title">
            <span class="pulse-red"></span>
            <strong>DROP 01 // "THE PRODUCER SUITE" COLLECTION</strong>
          </div>
          <div class="countdown-grid">
            <div class="time-slot">
              <span class="time-digit">{{ days }}</span>
              <span class="time-unit">Tage</span>
            </div>
            <div class="time-slot">
              <span class="time-digit">{{ hours }}</span>
              <span class="time-unit">Std</span>
            </div>
            <div class="time-slot">
              <span class="time-digit">{{ minutes }}</span>
              <span class="time-unit">Min</span>
            </div>
            <div class="time-slot">
              <span class="time-digit">{{ seconds }}</span>
              <span class="time-unit">Sek</span>
            </div>
          </div>
        </div>

        <div class="hero-btn-row">
          <button class="btn" type="button" @click="handleNotifyDrop">
            🔔 Für Drop benachrichtigen
          </button>
          <button class="btn ghost" type="button" @click="showLookbook = !showLookbook">
            📖 {{ showLookbook ? 'Lookbook schließen' : 'Lookbook ansehen' }}
          </button>
        </div>
      </div>

      <div class="hero-right">
        <div class="hero-showcase-card">
          <div class="merch-tag">LIMITED PREVIEW</div>
          <div class="merch-visual-art">
            <div class="hoodie-mockup">
              <div class="hoodie-front">
                <span class="unyq-embroidery">UNYQ</span>
                <span class="sub-embroidery">STUDIO EDITION // 480 GSM</span>
              </div>
            </div>
          </div>
          <div class="merch-showcase-info">
            <div class="info-title">Heavyweight Boxy Hoodie</div>
            <div class="info-price">79,00 € <span class="preorder">Vorbestellung</span></div>
          </div>
        </div>
      </div>
    </header>

    <!-- Lookbook Drawer -->
    <div v-if="showLookbook" class="lookbook-section card">
      <div class="lb-header">
        <h3>UNYQ Visual Lookbook — Season '26</h3>
        <button class="btn ghost tiny" @click="showLookbook = false">✕</button>
      </div>
      <p class="muted">Exklusive Einblicke in die Materialauswahl, Passformen und Typografie der Kollektion.</p>
      <div class="lookbook-gallery">
        <div class="lb-card">
          <div class="lb-img lb-1"></div>
          <h4>Oversized Organic Cotton</h4>
          <p class="muted small">100% GOTS-zertifizierte Bio-Baumwolle, schwere 480 GSM Grammatur.</p>
        </div>
        <div class="lb-card">
          <div class="lb-img lb-2"></div>
          <h4>Stickerei &amp; Hochpräzisions-Print</h4>
          <p class="muted small">Subtile Ton-in-Ton Bruststickung und reflektierende Backprints.</p>
        </div>
        <div class="lb-card">
          <div class="lb-img lb-3"></div>
          <h4>Studio Essentials &amp; Vinyl</h4>
          <p class="muted small">Limitierte 12" Slipmats, Producer Desk-Mats und Sound-Accessories.</p>
        </div>
      </div>
    </div>

    <!-- Container Status Banner -->
    <section class="container-status-banner card">
      <div class="status-left">
        <div class="icon-wrap">🎨</div>
        <div>
          <h3>UNYQ Designs — Container Vorbereitung</h3>
          <p class="muted">
            Dieser Bereich ist als Merch-Container vorbereitet. Der vollständige Shop mit Warenkorb, 
            Stripe-Checkout, Größenberater und automatischem Versand-Tracking wird hier scharfgestellt.
          </p>
        </div>
      </div>
      <div class="status-right">
        <span class="chip-status ready">Merch-Container Bereit</span>
      </div>
    </section>

    <!-- Product Grid Preview -->
    <section class="products-section">
      <div class="section-title-row">
        <div>
          <h2>Kommende Kollektion</h2>
          <p class="muted">Klicke auf ein Teil, um dich für den Drop eintragen zu lassen.</p>
        </div>
        <div class="filter-pills">
          <button
            v-for="cat in categories"
            :key="cat"
            class="pill-btn"
            :class="{ active: selectedCategory === cat }"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
      </div>

      <div class="products-grid">
        <div
          v-for="item in filteredProducts"
          :key="item.id"
          class="card product-card"
          @click="openProductModal(item)"
        >
          <div class="badge-status" :class="item.badgeClass">{{ item.badge }}</div>
          <div class="product-thumb">
            <span class="product-emoji">{{ item.emoji }}</span>
          </div>
          <div class="product-details">
            <div class="product-cat">{{ item.category }}</div>
            <h4 class="product-name">{{ item.name }}</h4>
            <p class="product-desc">{{ item.desc }}</p>
            <div class="product-footer">
              <span class="product-price">{{ item.price }}</span>
              <button class="btn btn-sm" @click.stop="openProductModal(item)">
                Vorschau
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Artist Merch Collaboration Box -->
    <section class="card collab-banner">
      <div class="collab-content">
        <span class="collab-badge">FOR ARTISTS</span>
        <h3>Eigenes Merch über UNYQ produzieren?</h3>
        <p class="muted">
          Du bist Artist oder Producer im UNYQ Netzwerk? Wir übernehmen Design, Produktion, Webshop 
          und weltweiten Versand für dein eigenes Merchandise ohne Vorabkosten.
        </p>
        <button class="btn" @click="handleArtistMerchRequest">
          ✉️ Merch-Anfrage einreichen
        </button>
      </div>
    </section>

    <!-- Product Detail Modal -->
    <div v-if="selectedItem" class="modal-overlay" @click.self="selectedItem = null">
      <div class="modal card">
        <div class="modal-header">
          <h3>{{ selectedItem.name }}</h3>
          <button class="btn ghost tiny" @click="selectedItem = null">✕</button>
        </div>
        <div class="modal-body">
          <div class="modal-preview-box">
            <span class="modal-emoji">{{ selectedItem.emoji }}</span>
          </div>
          <div class="modal-info">
            <div class="badge-status" :class="selectedItem.badgeClass">{{ selectedItem.badge }}</div>
            <div class="modal-price">{{ selectedItem.price }}</div>
            <p class="muted">{{ selectedItem.desc }}</p>
            <div class="sizes-box">
              <label>Verfügbare Größen:</label>
              <div class="sizes-list">
                <span class="size-pill">S</span>
                <span class="size-pill">M</span>
                <span class="size-pill active">L</span>
                <span class="size-pill">XL</span>
                <span class="size-pill">XXL</span>
              </div>
            </div>
            <div class="modal-actions">
              <button class="btn full-w" @click="handleNotifyDrop">
                🔔 Für Drop reservieren (Kostenlos)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useToast } from "../composables/useToast";

const { showToast } = useToast();

const showLookbook = ref(false);
const selectedCategory = ref("Alle");
const selectedItem = ref(null);

const categories = ["Alle", "Hoodies", "T-Shirts", "Headwear", "Accessoires"];

const products = [
  {
    id: 1,
    name: "UNYQ Signature 480GSM Hoodie",
    category: "Hoodies",
    desc: "Heavyweight French Terry Baumwolle in Deep Black mit dezenter Stickung.",
    price: "79,00 €",
    badge: "DROP 01",
    badgeClass: "badge-hot",
    emoji: "🧥",
  },
  {
    id: 2,
    name: "Producer Oversized Tee // Vintage Acid Wash",
    category: "T-Shirts",
    desc: "280 GSM schweres Baumwollshirt im lässigen Boxy Cut.",
    price: "42,00 €",
    badge: "LIMITED",
    badgeClass: "badge-blue",
    emoji: "👕",
  },
  {
    id: 3,
    name: "UNYQ Studio Dad Cap (Black Embroidered)",
    category: "Headwear",
    desc: "Unstrukturierte 6-Panel Kappe mit Metallverschluss und 3D-Stick.",
    price: "34,00 €",
    badge: "DROP 01",
    badgeClass: "badge-hot",
    emoji: "🧢",
  },
  {
    id: 4,
    name: "Vinyl Turntable Slipmat Duo (Cork & Felt)",
    category: "Accessoires",
    desc: "2x antistatische Slipmats für DJing und audiophiles Listening.",
    price: "24,00 €",
    badge: "ACCESSOIRE",
    badgeClass: "badge-green",
    emoji: "💿",
  },
  {
    id: 5,
    name: "Studio Desk Pad XXL (Waterproof Felt)",
    category: "Accessoires",
    desc: "900x400mm Studio Unterlage für Tastatur, Maus und Audio-Interface.",
    price: "38,00 €",
    badge: "STUDIO",
    badgeClass: "badge-blue",
    emoji: "🎛️",
  },
  {
    id: 6,
    name: "Heavy Canvas Tote Bag (UNYQ Sound System)",
    category: "Accessoires",
    desc: "Verstärkte Baumwoll-Tasche, perfekt für 12\" Vinyls und Headphones.",
    price: "22,00 €",
    badge: "DROP 01",
    badgeClass: "badge-hot",
    emoji: "🛍️",
  },
];

const filteredProducts = computed(() => {
  if (selectedCategory.value === "Alle") return products;
  return products.filter((p) => p.category === selectedCategory.value);
});

// Countdown logic
const days = ref(4);
const hours = ref(18);
const minutes = ref(42);
const seconds = ref(15);
let timer = null;

onMounted(() => {
  timer = setInterval(() => {
    if (seconds.value > 0) {
      seconds.value--;
    } else {
      seconds.value = 59;
      if (minutes.value > 0) {
        minutes.value--;
      } else {
        minutes.value = 59;
        if (hours.value > 0) {
          hours.value--;
        } else {
          hours.value = 23;
          if (days.value > 0) days.value--;
        }
      }
    }
  }, 1000);
});

onBeforeUnmount(() => {
  if (timer) clearInterval(timer);
});

function handleNotifyDrop() {
  showToast("Erfolgreich für den Drop vorgemerkt! Du erhältst VIP-Zugang. 🚀", "success");
  selectedItem.value = null;
}

function handleArtistMerchRequest() {
  showToast("Merch-Kooperation geöffnet! Unser Merch-Team meldet sich bei dir. 🎨", "info");
}

function openProductModal(item) {
  selectedItem.value = item;
}
</script>

<style scoped>
.designs-container-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1240px;
  margin: 0 auto;
  padding: 8px 0 60px;
}

/* Hero */
.designs-hero {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top right, rgba(236, 72, 153, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(244, 114, 182, 0.2);
  position: relative;
  overflow: hidden;
}

.tag-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(236, 72, 153, 0.12);
  border: 1px solid rgba(236, 72, 153, 0.3);
  color: #f472b6;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.designs-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #f472b6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.drop-countdown-box {
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 14px;
  padding: 16px 20px;
  margin-bottom: 24px;
}

.drop-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #f472b6;
  letter-spacing: 0.05em;
  margin-bottom: 12px;
}

.pulse-red {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.2); }
  100% { opacity: 0.6; transform: scale(0.9); }
}

.countdown-grid {
  display: flex;
  gap: 12px;
}

.time-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 52px;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.time-digit {
  font-size: 1.4rem;
  font-weight: 800;
  color: #fff;
  font-family: monospace;
}

.time-unit {
  font-size: 10px;
  color: var(--muted);
  text-transform: uppercase;
}

.hero-btn-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* Showcase Visual */
.hero-showcase-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.merch-tag {
  position: absolute;
  top: 14px;
  left: 14px;
  background: rgba(236, 72, 153, 0.2);
  border: 1px solid rgba(236, 72, 153, 0.4);
  color: #f472b6;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}

.merch-visual-art {
  width: 100%;
  height: 220px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hoodie-mockup {
  width: 160px;
  height: 180px;
  background: linear-gradient(145deg, #18181b, #09090b);
  border-radius: 24px 24px 16px 16px;
  border: 2px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.hoodie-front {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.unyq-embroidery {
  font-size: 1.4rem;
  font-weight: 900;
  letter-spacing: 0.15em;
  color: #fff;
  text-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.sub-embroidery {
  font-size: 8px;
  color: rgba(255, 255, 255, 0.5);
  letter-spacing: 0.1em;
}

.merch-showcase-info {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 12px;
}

.info-title {
  font-weight: 700;
  font-size: 14px;
}

.info-price {
  font-weight: 800;
  color: #f472b6;
}

.preorder {
  font-size: 10px;
  color: var(--muted);
  font-weight: normal;
  display: block;
  text-align: right;
}

/* Lookbook */
.lookbook-section {
  padding: 24px;
}

.lb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.lookbook-gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.lb-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
}

.lb-img {
  height: 120px;
  border-radius: 10px;
  margin-bottom: 12px;
}

.lb-1 { background: linear-gradient(135deg, #374151, #111827); }
.lb-2 { background: linear-gradient(135deg, #4f46e5, #1e1b4b); }
.lb-3 { background: linear-gradient(135deg, #059669, #064e3b); }

/* Status Banner */
.container-status-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 20px 28px;
  background: linear-gradient(90deg, rgba(236, 72, 153, 0.1), rgba(168, 85, 247, 0.08));
  border-left: 4px solid #ec4899;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.icon-wrap {
  font-size: 28px;
  background: rgba(236, 72, 153, 0.2);
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
  background: rgba(236, 72, 153, 0.15);
  color: #f472b6;
  border: 1px solid rgba(236, 72, 153, 0.3);
  padding: 6px 14px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 12px;
  white-space: nowrap;
}

/* Products Section */
.products-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title-row h2 {
  margin: 0 0 4px;
  font-size: 1.4rem;
}

.filter-pills {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn.active, .pill-btn:hover {
  background: var(--brand);
  color: #fff;
  border-color: var(--brand);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.product-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  position: relative;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.product-card:hover {
  transform: translateY(-3px);
  border-color: rgba(244, 114, 182, 0.4);
}

.badge-status {
  position: absolute;
  top: 14px;
  left: 14px;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  text-transform: uppercase;
}

.badge-hot { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
.badge-blue { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid rgba(59, 130, 246, 0.3); }
.badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); }

.product-thumb {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 12px;
  margin-bottom: 14px;
}

.product-emoji {
  font-size: 54px;
  filter: drop-shadow(0 6px 12px rgba(0, 0, 0, 0.3));
}

.product-cat {
  font-size: 11px;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.product-name {
  margin: 0 0 6px;
  font-size: 1.05rem;
  line-height: 1.3;
}

.product-desc {
  font-size: 12.5px;
  color: var(--muted);
  margin: 0 0 16px;
  line-height: 1.45;
  flex: 1;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.product-price {
  font-weight: 800;
  font-size: 1.15rem;
}

.btn-sm {
  min-height: 32px;
  padding: 4px 12px;
  font-size: 12px;
}

/* Collab Banner */
.collab-banner {
  padding: 32px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.85));
  border: 1px dashed rgba(244, 114, 182, 0.3);
}

.collab-badge {
  display: inline-block;
  padding: 4px 10px;
  background: rgba(244, 114, 182, 0.15);
  color: #f472b6;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 700;
  margin-bottom: 8px;
}

.collab-banner h3 {
  margin: 0 0 8px;
  font-size: 1.3rem;
}

.collab-banner p {
  max-width: 600px;
  margin: 0 0 20px;
  line-height: 1.6;
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
  margin-bottom: 20px;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-preview-box {
  height: 140px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-emoji {
  font-size: 64px;
}

.modal-price {
  font-size: 1.6rem;
  font-weight: 900;
  margin: 8px 0;
  color: #f472b6;
}

.sizes-box label {
  font-size: 12px;
  font-weight: 600;
  color: var(--muted);
  display: block;
  margin-bottom: 8px;
}

.sizes-list {
  display: flex;
  gap: 8px;
}

.size-pill {
  width: 38px;
  height: 38px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
}

.size-pill.active {
  background: #f472b6;
  color: #fff;
  border-color: #f472b6;
}

.full-w {
  width: 100%;
}

@media (max-width: 900px) {
  .designs-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
