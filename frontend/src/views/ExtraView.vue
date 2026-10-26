<template>
  <div class="extra-page">
    <!-- Header -->
    <header class="extra-hero card">
      <div class="hero-left">
        <div class="hero-badge">
          <span class="icon">🌐</span>
          <span>UNYQ Ecosystem &amp; Directory</span>
        </div>
        <h1>UNYQ Extra</h1>
        <p class="hero-desc">
          Die zentrale Schnittstelle zu allen Plattformen, Spezialtools, Community-Kanälen 
          und offiziellen Social-Media-Netzwerken von UNYQ. Finde schnell genau das, was du suchst.
        </p>

        <div class="quick-stats-row">
          <div class="stat-pill">
            <span class="stat-num">{{ platformsList.length }}</span>
            <span class="stat-text">UNYQ Plattformen</span>
          </div>
          <div class="stat-pill">
            <span class="stat-num">{{ socialChannels.length }}</span>
            <span class="stat-text">Externe Netzwerke</span>
          </div>
          <div class="stat-pill">
            <span class="stat-num">100%</span>
            <span class="stat-text">Vernetzt</span>
          </div>
        </div>
      </div>

      <div class="hero-right">
        <div class="search-hero-card">
          <label>Schnellzugriff &amp; Suche:</label>
          <input
            v-model.trim="searchQuery"
            type="text"
            class="input search-hero-input"
            placeholder="Plattform, Tool oder Social Media suchen..."
          />
          <div class="search-meta muted small">
            Tipp: Du kannst nach "Discord", "Turnier", "Spotify", "Fitness" etc. suchen.
          </div>
        </div>
      </div>
    </header>

    <!-- Filter Buttons -->
    <div class="filter-bar">
      <div class="filter-chips">
        <button
          v-for="cat in categories"
          :key="cat"
          class="cat-chip"
          :class="{ active: selectedCategory === cat }"
          @click="selectedCategory = cat"
        >
          {{ cat }}
        </button>
      </div>
    </div>

    <!-- Section 1: All Existing UNYQ Internal Platforms -->
    <section v-if="filteredPlatforms.length" class="directory-section">
      <div class="section-title-row">
        <h2>UNYQ Spezial-Plattformen &amp; Tools ({{ filteredPlatforms.length }})</h2>
        <span class="muted small">Alle internen Werkzeuge und Workflows</span>
      </div>

      <div class="platforms-grid">
        <div
          v-for="platform in filteredPlatforms"
          :key="platform.slug"
          class="card platform-card"
          @click="goToPlatform(platform.route)"
        >
          <div class="card-top">
            <div class="platform-icon-box">{{ platform.icon }}</div>
            <div class="card-badges">
              <span class="badge-status" :class="`badge-${platform.status}`">{{ platform.statusLabel }}</span>
              <span class="badge-version">v{{ platform.version }}</span>
            </div>
          </div>

          <h3 class="platform-name">{{ platform.name }}</h3>
          <p class="platform-desc">{{ platform.desc }}</p>

          <div class="platform-features">
            <span v-for="feat in platform.features" :key="feat" class="feat-tag">{{ feat }}</span>
          </div>

          <div class="card-footer">
            <button class="btn btn-sm" @click.stop="goToPlatform(platform.route)">
              {{ platform.btnLabel || 'Öffnen' }} →
            </button>
            <button class="btn ghost btn-sm" @click.stop="copyLink(platform.route)">
              Link kopieren
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Section 2: External Social Media & Ecosystem Channels -->
    <section v-if="filteredSocials.length" class="directory-section">
      <div class="section-title-row">
        <h2>Offizielle Social Media &amp; Streaming ({{ filteredSocials.length }})</h2>
        <span class="muted small">Trete unserer Community bei und folge unseren Kanälen</span>
      </div>

      <div class="socials-grid">
        <div
          v-for="social in filteredSocials"
          :key="social.name"
          class="card social-card"
          @click="openExternal(social.url)"
        >
          <div class="social-left">
            <div class="social-icon" :style="{ background: social.bgGradient }">
              {{ social.icon }}
            </div>
            <div class="social-info">
              <div class="social-header-line">
                <h4>{{ social.name }}</h4>
                <span class="handle-tag">{{ social.handle }}</span>
              </div>
              <p class="social-desc">{{ social.desc }}</p>
            </div>
          </div>

          <div class="social-right">
            <button class="btn ghost btn-sm" @click.stop="openExternal(social.url)">
              Aufrufen ↗
            </button>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { showToast } = useToast();

const selectedCategory = ref("Alle");
const searchQuery = ref("");

const categories = ["Alle", "Interne Plattformen", "Streaming & Musik", "Social Media", "Community & Dev"];

const platformsList = [
  {
    slug: "contests",
    name: "UNYQ Turniere & Contests",
    icon: "🏆",
    category: "Interne Plattformen",
    status: "live",
    statusLabel: "Live",
    version: "1.0",
    desc: "Musik-Battles, Turnierbäume, Runden-Einreichungen und Community-Voting.",
    features: ["Battles", "Voting", "Prize Pools"],
    route: "/platforms/contests",
    btnLabel: "Turniere ansehen",
  },
  {
    slug: "locations",
    name: "UNYQ Locations & Venues",
    icon: "📍",
    category: "Interne Plattformen",
    status: "beta",
    statusLabel: "Beta",
    version: "0.8",
    desc: "Finde und buche Studios, Konzert-Locations, Eventhallen und Booking-Orte.",
    features: ["Studios", "Venues", "Buchungen"],
    route: "/platforms/locations",
    btnLabel: "Locations durchsuchen",
  },
  {
    slug: "content-schedule",
    name: "ACH Content Schedule",
    icon: "📅",
    category: "Interne Plattformen",
    status: "live",
    statusLabel: "Live",
    version: "1.2",
    desc: "Wöchentlicher Drag & Drop Planer für Social Media Posts, Content-Serien und Drops.",
    features: ["Wochenplan", "Drag & Drop", "Content-Serien"],
    route: "/platforms/content-schedule",
    btnLabel: "Planer öffnen",
  },
  {
    slug: "content-studio",
    name: "UNYQ Content Studio",
    icon: "📝",
    category: "Interne Plattformen",
    status: "beta",
    statusLabel: "Beta",
    version: "0.9",
    desc: "Erstelle Tipps, Ankündigungen, Newsartikel und Tutorials für die Community.",
    features: ["Tipps", "News", "Tutorials"],
    route: "/platforms/content-studio",
    btnLabel: "Studio starten",
  },
  {
    slug: "plugin-guides",
    name: "UNYQ Plugin Guides",
    icon: "🔌",
    category: "Interne Plattformen",
    status: "live",
    statusLabel: "Live",
    version: "1.1",
    desc: "Umfangreiche Setup-Guides, Mixing-Tutorials und DAW-Workflows.",
    features: ["DAW-Setups", "Guides", "Best Practices"],
    route: "/platforms/plugin-guides",
    btnLabel: "Guides lesen",
  },
  {
    slug: "fitness",
    name: "UNYQ Fitness & Nutrition",
    icon: "🏋️",
    category: "Interne Plattformen",
    status: "beta",
    statusLabel: "Beta",
    version: "0.7",
    desc: "Kalorien-Tracker, Tagesverbrauch-Rechner und einfache Essensideen für Musiker.",
    features: ["Kcal", "Makros", "Essensideen"],
    route: "/platforms/fitness",
    btnLabel: "Tracker öffnen",
  },
  {
    slug: "todo",
    name: "UNYQ Todo & Kalender",
    icon: "✅",
    category: "Interne Plattformen",
    status: "live",
    statusLabel: "Live",
    version: "1.0",
    desc: "Fokussierte Aufgabenverwaltung mit optionalem Zieldatum und Kalender-Export.",
    features: ["Todos", "Datum", "Kalender-Sync"],
    route: "/platforms/todo",
    btnLabel: "Todos öffnen",
  },
  {
    slug: "api-center",
    name: "UNYQ API Platform",
    icon: "🔑",
    category: "Community & Dev",
    status: "live",
    statusLabel: "Live",
    version: "1.0",
    desc: "Integrationen, API-Keys, Webhooks und Entwickler-Schnittstellen für externe Apps.",
    features: ["API Keys", "Webhooks", "Automation"],
    route: "/platforms/api-center",
    btnLabel: "APIs verwalten",
  },
  {
    slug: "admin",
    name: "UNYQ Admin Control Hub",
    icon: "👑",
    category: "Interne Plattformen",
    status: "live",
    statusLabel: "Team",
    version: "2.1",
    desc: "Zentrales Verwaltungszentrum für Plattform-Status, Rollen und Artist-Vorschau.",
    features: ["Nutzer-Rollen", "Plattform-Steuerung", "Artist View"],
    route: "/platforms/admin",
    btnLabel: "Admin Hub",
  },
  {
    slug: "testing",
    name: "UNYQ Testing Lab",
    icon: "🧪",
    category: "Community & Dev",
    status: "beta",
    statusLabel: "Debug",
    version: "0.5",
    desc: "Interne Tests für E-Mail-Templates, System-Events und Backend-Diagnose.",
    features: ["E-Mail Tests", "Events", "Debug"],
    route: "/app/testing",
    btnLabel: "Test Lab",
  },
];

const socialChannels = [
  {
    name: "Spotify",
    category: "Streaming & Musik",
    handle: "@unyq_records",
    desc: "Offizielle Playlists, kuratierte Member-Releases und Artist Spotlight Compilations.",
    icon: "🎧",
    bgGradient: "linear-gradient(135deg, #1db954, #128c3e)",
    url: "https://spotify.com",
  },
  {
    name: "Apple Music",
    category: "Streaming & Musik",
    handle: "UNYQ Curated",
    desc: "Spatial Audio Releases, Exclusive DJ Mixes und redaktionelle Playlists.",
    icon: "🍎",
    bgGradient: "linear-gradient(135deg, #fa243c, #b31427)",
    url: "https://music.apple.com",
  },
  {
    name: "SoundCloud",
    category: "Streaming & Musik",
    handle: "soundcloud.com/unyq",
    desc: "Demos, unveröffentlichte Bootlegs, Live-Sets und Community Mixes.",
    icon: "☁️",
    bgGradient: "linear-gradient(135deg, #ff5500, #cc4400)",
    url: "https://soundcloud.com",
  },
  {
    name: "YouTube",
    category: "Social Media",
    handle: "@UNYQ_Music",
    desc: "Offizielle Musikvideos, Studio Sessions, Sample Breakdowns und Interviews.",
    icon: "▶️",
    bgGradient: "linear-gradient(135deg, #ff0000, #cc0000)",
    url: "https://youtube.com",
  },
  {
    name: "Instagram",
    category: "Social Media",
    handle: "@unyq.official",
    desc: "Tägliche Einblicke in Releases, Studio-Stories, Drop-Countdowns und Artist-News.",
    icon: "📸",
    bgGradient: "linear-gradient(135deg, #e1306c, #833ab4)",
    url: "https://instagram.com",
  },
  {
    name: "TikTok",
    category: "Social Media",
    handle: "@unyq_sounds",
    desc: "Virale Sound-Snippets, Producer-Tips, Beatmaking in 60 Sekunden und Highlights.",
    icon: "🎵",
    bgGradient: "linear-gradient(135deg, #00f2fe, #4facfe)",
    url: "https://tiktok.com",
  },
  {
    name: "Discord",
    category: "Community & Dev",
    handle: "discord.gg/unyq",
    desc: "Der größte Creator-Hub: Live-Feedback, Sample-Sharing, Battle-Talk und Collabs.",
    icon: "💬",
    bgGradient: "linear-gradient(135deg, #5865f2, #4752c4)",
    url: "https://discord.com",
  },
  {
    name: "Twitch",
    category: "Social Media",
    handle: "twitch.tv/unyqlive",
    desc: "Wöchentliche Live Beat-Cookups, Producer-Battles und Track-Listening Streams.",
    icon: "🎦",
    bgGradient: "linear-gradient(135deg, #9146ff, #6441a5)",
    url: "https://twitch.tv",
  },
  {
    name: "Telegram",
    category: "Community & Dev",
    handle: "t.me/unyq_vip",
    desc: "VIP-Broadcast für sofortige Benachrichtigungen zu Sample Drops und Events.",
    icon: "✈️",
    bgGradient: "linear-gradient(135deg, #0088cc, #006699)",
    url: "https://telegram.org",
  },
  {
    name: "GitHub",
    category: "Community & Dev",
    handle: "github.com/unyq-labs",
    desc: "Open-Source Bibliotheken, Web-Audio Algorithmen und Integrations-SDKs.",
    icon: "🐙",
    bgGradient: "linear-gradient(135deg, #24292e, #1b1f23)",
    url: "https://github.com",
  },
];

const filteredPlatforms = computed(() => {
  return platformsList.filter((p) => {
    const matchCat =
      selectedCategory.value === "Alle" ||
      selectedCategory.value === p.category ||
      (selectedCategory.value === "Interne Plattformen" && p.category === "Interne Plattformen");
    const q = searchQuery.value.toLowerCase();
    const matchQuery =
      !q ||
      p.name.toLowerCase().includes(q) ||
      p.desc.toLowerCase().includes(q) ||
      p.features.some((f) => f.toLowerCase().includes(q));
    return matchCat && matchQuery;
  });
});

const filteredSocials = computed(() => {
  return socialChannels.filter((s) => {
    const matchCat =
      selectedCategory.value === "Alle" ||
      selectedCategory.value === s.category ||
      (selectedCategory.value === "Streaming & Musik" && s.category === "Streaming & Musik") ||
      (selectedCategory.value === "Social Media" && s.category === "Social Media") ||
      (selectedCategory.value === "Community & Dev" && s.category === "Community & Dev");
    const q = searchQuery.value.toLowerCase();
    const matchQuery =
      !q ||
      s.name.toLowerCase().includes(q) ||
      s.handle.toLowerCase().includes(q) ||
      s.desc.toLowerCase().includes(q);
    return matchCat && matchQuery;
  });
});

function goToPlatform(route) {
  router.push(route);
}

function copyLink(route) {
  const full = `${window.location.origin}${route}`;
  if (navigator?.clipboard?.writeText) {
    navigator.clipboard.writeText(full);
    showToast("Link in Zwischenablage kopiert! 📋", "success");
  } else {
    showToast(`Link: ${full}`);
  }
}

function openExternal(url) {
  window.open(url, "_blank");
}
</script>

<style scoped>
.extra-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 8px 0 60px;
}

/* Hero */
.extra-hero {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.18), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(96, 165, 250, 0.2);
  position: relative;
  overflow: hidden;
}

.hero-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.3);
  color: #60a5fa;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.extra-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #93c5fd 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.quick-stats-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.stat-pill {
  display: flex;
  flex-direction: column;
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.stat-num {
  font-size: 1.3rem;
  font-weight: 800;
  color: #60a5fa;
}

.stat-text {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.search-hero-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(96, 165, 250, 0.2);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.search-hero-card label {
  font-size: 13px;
  font-weight: 700;
}

.search-hero-input {
  background: rgba(0, 0, 0, 0.3);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  gap: 8px;
}

.filter-chips {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.cat-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 7px 16px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-chip.active, .cat-chip:hover {
  background: #3b82f6;
  color: #fff;
  border-color: #3b82f6;
  font-weight: 700;
}

/* Directory Section */
.directory-section {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
}

.section-title-row h2 {
  margin: 0;
  font-size: 1.3rem;
}

/* Grid */
.platforms-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.platform-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.platform-card:hover {
  transform: translateY(-3px);
  border-color: rgba(96, 165, 250, 0.4);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.platform-icon-box {
  width: 44px;
  height: 44px;
  background: rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.card-badges {
  display: flex;
  align-items: center;
  gap: 6px;
}

.badge-status {
  font-size: 10px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  text-transform: uppercase;
}

.badge-live { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.badge-beta { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }

.badge-version {
  font-size: 10px;
  color: var(--muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 6px;
  border-radius: 4px;
}

.platform-name {
  margin: 0;
  font-size: 1.1rem;
}

.platform-desc {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  flex: 1;
}

.platform-features {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.feat-tag {
  font-size: 11px;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 6px;
  color: var(--muted);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  padding-top: 14px;
  margin-top: 4px;
}

.btn-sm {
  min-height: 32px;
  padding: 4px 12px;
  font-size: 12px;
}

/* Social Grid */
.socials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 16px;
}

.social-card {
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  cursor: pointer;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.social-card:hover {
  transform: translateY(-2px);
  border-color: rgba(148, 163, 184, 0.35);
}

.social-left {
  display: flex;
  align-items: center;
  gap: 14px;
  min-width: 0;
}

.social-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.3);
}

.social-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.social-header-line {
  display: flex;
  align-items: center;
  gap: 8px;
}

.social-header-line h4 {
  margin: 0;
  font-size: 14.5px;
}

.handle-tag {
  font-size: 11px;
  color: var(--muted);
  font-family: monospace;
}

.social-desc {
  margin: 2px 0 0;
  font-size: 12px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (max-width: 900px) {
  .extra-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
