<template>
  <div class="unyq-hub-page" :class="{ 'user-relaxed-mode': viewMode === 'user' }">
    <!-- Top Hero Header -->
    <header class="hub-hero">
      <div class="hero-inner">
        <div class="hero-left">
          <!-- View Mode Toggle (Available for Admin/Team or preview) -->
          <div class="mode-switcher-bar">
            <div class="mode-pill-toggle">
              <button
                type="button"
                class="mode-btn"
                :class="{ active: viewMode === 'admin' }"
                @click="setViewMode('admin')"
                v-if="isTeam"
              >
                <span class="mode-icon">👑</span>
                <span>Admin Ansicht</span>
              </button>
              <button
                type="button"
                class="mode-btn"
                :class="{ active: viewMode === 'user' }"
                @click="setViewMode('user')"
              >
                <span class="mode-icon">✨</span>
                <span>Normal User Ansicht</span>
              </button>
            </div>
          </div>

          <!-- Title depending on mode -->
          <div v-if="viewMode === 'user'" class="user-hero-copy">
            <h1 class="hero-headline">Willkommen{{ displayName ? `, ${displayName}` : '' }}</h1>
            <p class="hero-subtext">
              Dein kreativer Freiraum für Musik, Beats, Finanzen und Community. 
              Alles Wichtige auf einen Blick – ohne Ablenkung.
            </p>
          </div>

          <div v-else class="admin-hero-copy">
            <h1 class="hero-headline">UNYQ Platform Control</h1>
            <p class="hero-subtext">
              Zentrale Steuerung aller Plattformen, ProArtist-Workflows, Reviews und Nutzer-Berechtigungen.
            </p>
          </div>
        </div>

        <div class="hero-right">
          <!-- Quick Status Card (Different for User vs Admin) -->
          <div v-if="viewMode === 'user'" class="card user-spotlight-card">
            <div class="sc-head">
              <span class="sc-icon">🎵</span>
              <div>
                <strong>UNYQ Music Tipp</strong>
                <p class="muted small">Neuer exklusiver VIP-Drop verfügbar</p>
              </div>
            </div>
            <div class="sc-track-preview">
              <span class="sc-title">Midnight Drive in Berlin</span>
              <span class="sc-artist">KAZA &amp; UNYQ</span>
            </div>
            <button class="btn btn-sm" @click="openPlatformByKey('music')">
              ▶ Jetzt reinhören
            </button>
          </div>

          <div v-else class="card admin-status-card">
            <div class="asc-head">
              <strong>Team Status Übersicht</strong>
              <span class="live-pill">Live</span>
            </div>
            <div class="asc-grid">
              <div class="asc-item" :class="{ alert: hubBadges.overdueTasks > 0 }">
                <span class="asc-val">{{ hubBadges.overdueTasks }}</span>
                <span class="asc-lbl">Überfällig</span>
              </div>
              <div class="asc-item" :class="{ warn: hubBadges.pendingReviews > 0 }">
                <span class="asc-val">{{ hubBadges.pendingReviews }}</span>
                <span class="asc-lbl">Reviews</span>
              </div>
              <div class="asc-item" :class="{ alert: hubBadges.staleGrowpro > 0 }">
                <span class="asc-val">{{ hubBadges.staleGrowpro }}</span>
                <span class="asc-lbl">GrowPro</span>
              </div>
              <div class="asc-item">
                <span class="asc-val">{{ unreadNotifications }}</span>
                <span class="asc-lbl">Alerts</span>
              </div>
            </div>
            <button class="btn ghost btn-sm asc-btn" @click="openProArtistDashboard">
              Zum ProArtist Dashboard →
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- ADMIN EXCLUSIVE: ProArtist Deep Workflows & Quick-Jump Bar -->
    <section v-if="viewMode === 'admin'" class="admin-quick-dock card">
      <div class="dock-headline">
        <span class="dock-badge">PROARTIST WORKSPACE</span>
        <h3>Schnellzugriff: Team &amp; Projektmanagement</h3>
      </div>
      <div class="dock-links">
        <button class="dock-btn" @click="router.push('/dashboard')">
          <span class="dock-icon">🏠</span>
          <span>Dashboard</span>
        </button>
        <button class="dock-btn" @click="router.push('/songs')">
          <span class="dock-icon">🎵</span>
          <span>Songs &amp; Beats</span>
        </button>
        <button class="dock-btn" @click="router.push('/app/tournaments')">
          <span class="dock-icon">🏆</span>
          <span>Turniere &amp; Arena</span>
        </button>
        <button class="dock-btn" @click="router.push('/projects')">
          <span class="dock-icon">📁</span>
          <span>Projekte</span>
        </button>
        <button class="dock-btn" @click="router.push('/tasks')">
          <span class="dock-icon">🗒️</span>
          <span>Tasks</span>
          <span v-if="hubBadges.overdueTasks" class="dock-count alert">{{ hubBadges.overdueTasks }}</span>
        </button>
        <button class="dock-btn" @click="router.push('/reviews')">
          <span class="dock-icon">✅</span>
          <span>Review</span>
          <span v-if="hubBadges.pendingReviews" class="dock-count warn">{{ hubBadges.pendingReviews }}</span>
        </button>
        <button class="dock-btn" @click="router.push('/timeline')">
          <span class="dock-icon">🗓️</span>
          <span>Timeline</span>
        </button>
        <button class="dock-btn" @click="router.push('/analytics')">
          <span class="dock-icon">📊</span>
          <span>Analytics</span>
        </button>
        <button class="dock-btn" @click="router.push('/profiles')">
          <span class="dock-icon">🎤</span>
          <span>Artists</span>
        </button>
        <button class="dock-btn" @click="router.push('/growpro')">
          <span class="dock-icon">🌱</span>
          <span>GrowPro</span>
        </button>
        <button class="dock-btn" @click="router.push('/chats')">
          <span class="dock-icon">💬</span>
          <span>Chats</span>
        </button>
        <button class="dock-btn admin-tool" @click="router.push('/platforms/admin')">
          <span class="dock-icon">👑</span>
          <span>Admin Hub</span>
        </button>
        <button class="dock-btn team-tool-btn" @click="showQuickShareModal = true">
          <span class="dock-icon">🔗</span>
          <span>Quick-Share</span>
        </button>
      </div>
    </section>

    <!-- TEAM EXCLUSIVE TOOLS SECTION -->
    <section v-if="isTeam && viewMode === 'admin'" class="team-exclusive-tools card">
      <div class="tet-header">
        <div class="tet-title-group">
          <span class="tet-badge">🔒 EXKLUSIVES TEAM-WERKZEUG</span>
          <h3>Studio Quick-Share Link Generator</h3>
          <p class="muted small">
            Erstelle passwortgeschützte oder zeitlich begrenzte Direkt-Freigabelinks für externe A&amp;Rs, Labels oder Gastmusiker – ohne Login-Zwang.
          </p>
        </div>
        <button class="btn btn-sm" @click="showQuickShareModal = true">
          🔗 Neuer Quick-Share Link
        </button>
      </div>

      <!-- Quick stats of active links -->
      <div class="tet-active-links" v-if="quickShareLinks.length">
        <div v-for="link in quickShareLinks.slice(0, 3)" :key="link.id" class="tet-link-chip">
          <span class="tl-icon">⚡</span>
          <div class="tl-info">
            <strong>{{ link.title }}</strong>
            <small class="muted tiny">Gültig bis: {{ link.expiresLabel }} · {{ link.views }} Views</small>
          </div>
          <button class="btn ghost tiny" type="button" @click="copyQuickShareLink(link)">Kopieren</button>
          <button class="btn ghost tiny danger-text" type="button" @click="deleteQuickShareLink(link.id)">✕</button>
        </div>
      </div>
    </section>

    <!-- The 8 Core UNYQ Pillars Grid -->
    <main class="hub-main-section">
      <div class="section-top-bar">
        <div class="section-title-wrap">
          <h2>{{ viewMode === 'user' ? 'Entdecke das UNYQ Universum' : 'UNYQ Haupt-Plattformen & Bereiche' }}</h2>
          <p class="muted section-subtext">
            {{ viewMode === 'user' ? 'Klicke auf einen Bereich, um direkt loszulegen.' : 'Alle 8 Kern-Plattformen. Ziehe Karten, um die Reihenfolge zu ändern.' }}
          </p>
        </div>

        <div v-if="viewMode === 'admin'" class="admin-grid-actions">
          <button
            class="btn ghost btn-sm edit-order-btn"
            :class="{ active: editMode }"
            @click="editMode = !editMode"
          >
            {{ editMode ? '✓ Fertig sortiert' : '⇄ Reihenfolge anpassen' }}
          </button>
        </div>
      </div>

      <!-- Grid of the 8 Pillars -->
      <div class="pillars-grid" :class="{ 'edit-mode-active': editMode }">
        <div
          v-for="pillar in orderedPillars"
          :key="pillar.key"
          class="card pillar-card"
          :class="[
            `theme-${pillar.color}`,
            { 'is-dragging': draggedKey === pillar.key, 'drag-over': dragOverKey === pillar.key }
          ]"
          :draggable="editMode"
          @dragstart="onDragStart($event, pillar.key)"
          @dragover="onDragOver($event, pillar.key)"
          @dragleave="dragOverKey = null"
          @drop="onDrop($event, pillar.key)"
          @dragend="onDragEnd"
          @click="!editMode && openPlatformByKey(pillar.key)"
        >
          <div v-if="editMode" class="drag-handle-badge">⋮⋮ Ziehen zum Verschieben</div>

          <div class="pillar-top">
            <div class="pillar-icon-box" :style="{ background: pillar.bgGlow }">
              <span class="pillar-emoji">{{ pillar.icon }}</span>
            </div>
            <div class="pillar-badges">
              <span class="badge-cat">{{ pillar.category }}</span>
              <span class="badge-accent" :class="`pill-${pillar.color}`">{{ pillar.badge }}</span>
            </div>
          </div>

          <div class="pillar-body">
            <h3 class="pillar-title">{{ pillar.title }}</h3>
            <p class="pillar-description">{{ pillar.description }}</p>
          </div>

          <div class="pillar-features-row">
            <span v-for="feat in pillar.features" :key="feat" class="p-feat">
              {{ feat }}
            </span>
          </div>

          <div class="pillar-footer">
            <button class="btn btn-pillar-action" @click.stop="openPlatformByKey(pillar.key)">
              <span>{{ pillar.buttonLabel }}</span>
              <span class="arrow-glyph">→</span>
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- User Inspiration / Community Highlights Banner -->
    <section v-if="viewMode === 'user'" class="user-highlights-banner card">
      <div class="highlight-column">
        <span class="hl-badge">📦 FREE SOUNDS</span>
        <h4>UNYQ Library Update</h4>
        <p class="muted small">Neue 808s, Stems &amp; Presets jetzt 100% CC0 Free zum Download bereit.</p>
        <button class="btn ghost btn-sm" @click="openPlatformByKey('library')">Library durchsuchen →</button>
      </div>

      <div class="highlight-column border-col">
        <span class="hl-badge hl-forum">💬 COMMUNITY FORUM</span>
        <h4>Austausch &amp; Feedback</h4>
        <p class="muted small">Stelle Fragen zu Mixing &amp; Beatmaking oder finde Collab-Partner im Forum.</p>
        <button class="btn ghost btn-sm" @click="openPlatformByKey('forum')">Zum Forum →</button>
      </div>

      <div class="highlight-column">
        <span class="hl-badge hl-merch">🎨 LIMITED MERCH</span>
        <h4>UNYQ Designs Drop</h4>
        <p class="muted small">Trage dich für den exklusiven Vorab-Zugang des Studio-Drop '26 ein.</p>
      </div>
    </section>

    <!-- Quick-Share Modal -->
    <div v-if="showQuickShareModal" class="modal-overlay" @click.self="showQuickShareModal = false">
      <article class="modal-card qs-modal">
        <header class="modal-header">
          <div>
            <span class="tet-badge">TEAM TOOL</span>
            <h2>🔗 Studio Quick-Share Link erstellen</h2>
            <p class="muted small">Generiere einen sicheren Vorschau-Link für externe Partner.</p>
          </div>
          <button class="btn ghost small" @click="showQuickShareModal = false" type="button">✕</button>
        </header>

        <form class="modal-content qs-content" @submit.prevent="createQuickShareLink">
          <div class="form-grid">
            <label class="full">
              Titel / Track-Name *
              <input class="input" v-model.trim="newShareForm.title" placeholder="z. B. Midnight Drive v2 Master Preview" required />
            </label>
            <label>
              Gültigkeitsdauer
              <select class="input" v-model="newShareForm.duration">
                <option value="24h">24 Stunden</option>
                <option value="7d">7 Tage</option>
                <option value="30d">30 Tage</option>
                <option value="never">Unbegrenzt</option>
              </select>
            </label>
            <label>
              Passwort-Schutz (optional)
              <input class="input" v-model.trim="newShareForm.password" placeholder="PIN z. B. 4829" />
            </label>
          </div>

          <div class="permissions-box">
            <span class="muted tiny">Freigabe-Berechtigungen:</span>
            <div class="perm-checkboxes">
              <label><input type="checkbox" v-model="newShareForm.allowStream" disabled checked /> Audio-Stream / Anhören</label>
              <label><input type="checkbox" v-model="newShareForm.allowDownload" /> Download erlauben</label>
              <label><input type="checkbox" v-model="newShareForm.allowFeedback" /> Gast-Feedback erlauben</label>
            </div>
          </div>

          <div v-if="lastCreatedLink" class="created-link-box">
            <span class="tiny muted">Generierter Freigabe-Link:</span>
            <div class="cl-row">
              <input class="input" readonly :value="lastCreatedLink" />
              <button class="btn" type="button" @click="copyText(lastCreatedLink)">Kopieren</button>
            </div>
          </div>

          <div class="modal-actions" style="display: flex; justify-content: flex-end; gap: 8px; margin-top: 16px;">
            <button class="btn ghost" type="button" @click="showQuickShareModal = false">Schließen</button>
            <button class="btn" type="submit">Link generieren</button>
          </div>
        </form>
      </article>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import api from "../api";
import {
  fetchManagedPlatformAccessState,
  mapAccessStateRows,
} from "../services/managedPlatforms";

const router = useRouter();
const { showToast } = useToast();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

const HUB_VIEW_MODE_KEY = "unyq_hub_mode_preference";
const HUB_PILLARS_ORDER_KEY = "unyq_pillars_order";

// Default view mode: team gets admin, others get user
const viewMode = ref("user");
const editMode = ref(false);
const draggedKey = ref(null);
const dragOverKey = ref(null);

const unreadNotifications = ref(0);
const hubBadges = ref({ openTasks: 0, overdueTasks: 0, pendingReviews: 0, staleGrowpro: 0 });
const accessStateBySlug = ref({});

const displayName = computed(() => {
  return (me.value?.name || me.value?.username || "").trim().split(" ")[0] || "";
});

function setViewMode(mode) {
  viewMode.value = mode;
  try {
    localStorage.setItem(HUB_VIEW_MODE_KEY, mode);
  } catch {
    // ignore
  }
}

// Quick-Share Studio Link (Exclusive Team Tool)
const showQuickShareModal = ref(false);
const quickShareLinks = ref([]);
const lastCreatedLink = ref("");
const newShareForm = ref({
  title: "",
  duration: "7d",
  password: "",
  allowStream: true,
  allowDownload: false,
  allowFeedback: true,
});

function loadQuickShareLinks() {
  try {
    const raw = localStorage.getItem("unyq_quick_share_links");
    if (raw) {
      quickShareLinks.value = JSON.parse(raw);
    } else {
      quickShareLinks.value = [
        {
          id: "qs-1",
          title: "Midnight Drive v2 Mix Preview",
          token: "md2_mix_78a1",
          expiresLabel: "In 6 Tagen",
          views: 4,
          url: (typeof window !== "undefined" ? window.location.origin : "https://unyq.app") + "/share/md2_mix_78a1",
        },
      ];
    }
  } catch {}
}

function saveQuickShareLinks() {
  try {
    localStorage.setItem("unyq_quick_share_links", JSON.stringify(quickShareLinks.value));
  } catch {}
}

function createQuickShareLink() {
  if (!newShareForm.value.title) return;
  const token = "st_" + Math.random().toString(36).substring(2, 10);
  const durMap = { "24h": "In 24 Stunden", "7d": "In 7 Tagen", "30d": "In 30 Tagen", "never": "Unbegrenzt" };
  const origin = typeof window !== "undefined" ? window.location.origin : "https://unyq.app";
  const fullUrl = origin + "/share/" + token;
  const item = {
    id: `qs-${Date.now()}`,
    title: newShareForm.value.title,
    token,
    expiresLabel: durMap[newShareForm.value.duration] || "In 7 Tagen",
    views: 0,
    url: fullUrl,
    hasPassword: Boolean(newShareForm.value.password),
    allowDownload: newShareForm.value.allowDownload,
    allowFeedback: newShareForm.value.allowFeedback,
  };
  quickShareLinks.value.unshift(item);
  saveQuickShareLinks();
  lastCreatedLink.value = fullUrl;
  showToast("Quick-Share Link erfolgreich generiert!", "success");
}

function copyQuickShareLink(link) {
  copyText(link.url);
}

function copyText(text) {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  }
  showToast("Link in Zwischenablage kopiert!", "info");
}

function deleteQuickShareLink(id) {
  quickShareLinks.value = quickShareLinks.value.filter((l) => l.id !== id);
  saveQuickShareLinks();
  showToast("Link gelöscht", "info");
}

// The 8 Core UNYQ Pillars
const corePillars = [
  {
    key: "proartist",
    title: "UNYQ ProArtist",
    category: "Kreativ-Workspace",
    description: "Vollständige Arbeitsumgebung für Projekte, Aufgaben, Timelines, Reviews, Analytics und Team-Workflows.",
    buttonLabel: "Workspace öffnen",
    icon: "🎹",
    badge: "Workflows & Tasks",
    color: "blue",
    bgGlow: "rgba(59, 130, 246, 0.15)",
    features: ["Studio Pipeline", "Songs & Stems", "Daily Tasks", "Arena Battles"],
    route: "/dashboard",
  },
  {
    key: "contests",
    title: "UNYQ Contests",
    category: "Beat Battles & Turniere",
    description: "Kämpfe in 1v1 Audio-Duellen, steige im Rang auf (Bronze bis Legendär) und gewinne Preisgelder & Studio-Gear.",
    buttonLabel: "Arena betreten",
    icon: "🏆",
    badge: "Live Arena",
    color: "amber",
    bgGlow: "rgba(245, 158, 11, 0.15)",
    features: ["1v1 Live Battles", "Turnierbaum", "Ranked System", "Community Voting"],
    route: "/platforms/contests",
  },
  {
    key: "finance",
    title: "UNYQ Finance",
    category: "Finanz-Management",
    description: "Zentrales Finanz-Center: Einnahmen, GEMA/GVL-Tantiemen, Projektbudgets und Vorbereitung für deine Finanz-App.",
    buttonLabel: "Finance öffnen",
    icon: "💰",
    badge: "Container Bereit",
    color: "emerald",
    bgGlow: "rgba(16, 185, 129, 0.15)",
    features: ["Cashflow", "Budgets", "Wallet Sync", "App Dock"],
    route: "/platforms/finance",
  },
  {
    key: "earn",
    title: "UNYQ Earn",
    category: "Partner & Affiliate",
    description: "Empfehle UNYQ an Artists & Producer weiter und verdiene bis zu 30% Lifetime-Provision bei monatlicher Auszahlung.",
    buttonLabel: "Partnerbereich öffnen",
    icon: "💎",
    badge: "Bis 30% Provision",
    color: "amber",
    bgGlow: "rgba(245, 158, 11, 0.15)",
    features: ["Partnerlink", "Lifetime Payouts", "Tier Tiers"],
    route: "/platforms/earn",
  },
  {
    key: "designs",
    title: "UNYQ Designs",
    category: "Merchandise & Drops",
    description: "Offizielles UNYQ Merchandise, hochwertige Heavyweight Streetwear, Studio-Essentials und Artist-Kollaborationen.",
    buttonLabel: "Designs ansehen",
    icon: "🎨",
    badge: "Drop '26",
    color: "pink",
    bgGlow: "rgba(236, 72, 153, 0.15)",
    features: ["Streetwear", "Hoodies", "Vinyl Mats", "Artist Merch"],
    route: "/platforms/designs",
  },
  {
    key: "music",
    title: "UNYQ Music",
    category: "Exklusiver Music Player",
    description: "Exklusiver Music Player mit Audio-Synthesizer, VIP Drops, Unreleased Tracks und Präsentationsfläche für Artists.",
    buttonLabel: "Music Player starten",
    icon: "🎧",
    badge: "VIP Player",
    color: "purple",
    bgGlow: "rgba(168, 85, 247, 0.15)",
    features: ["Waveform Player", "VIP Drops", "Audio Engine", "Track Upload"],
    route: "/platforms/music",
  },
  {
    key: "library",
    title: "UNYQ Library",
    category: "Open Source Sound Bank",
    description: "Große offene Free License Audio-Bibliothek: 808s, Drum-Kits, Melodic Loops, Serum Presets & MIDIs für Producer.",
    buttonLabel: "Sound Bank öffnen",
    icon: "📦",
    badge: "100% Free CC0",
    color: "cyan",
    bgGlow: "rgba(6, 182, 212, 0.15)",
    features: ["808s & Drums", "Serum Presets", "STEMs", "Instant Download"],
    route: "/platforms/library",
  },
  {
    key: "forum",
    title: "UNYQ Forum",
    category: "Community & Austausch",
    description: "Das Community-Forum für Beatmaking, Mixing, Songwriting, Feature-Wünsche und Track-Feedback.",
    buttonLabel: "Forum öffnen",
    icon: "💬",
    badge: "Live Community",
    color: "indigo",
    bgGlow: "rgba(99, 102, 241, 0.15)",
    features: ["Diskussionen", "Feedback", "Collabs", "Ideen"],
    route: "/platforms/forum",
  },
  {
    key: "extra",
    title: "UNYQ Extra",
    category: "Ecosystem Directory",
    description: "Zentraler Zugang zu allen weiteren UNYQ Plattformen (Turniere, Locations, Content Schedule etc.) und offiziellen Socials.",
    buttonLabel: "Alle Plattformen",
    icon: "🌐",
    badge: "Plattformen & Socials",
    color: "sky",
    bgGlow: "rgba(14, 165, 233, 0.15)",
    features: ["Turniere", "Locations", "Schedule", "Spotify & Socials"],
    route: "/platforms/extra",
  },
];

function loadSavedOrder() {
  try {
    const raw = localStorage.getItem(HUB_PILLARS_ORDER_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

const savedOrder = ref(loadSavedOrder());

const orderedPillars = computed(() => {
  if (!savedOrder.value.length) return corePillars;
  const list = [...corePillars];
  const ordered = [];
  savedOrder.value.forEach((key) => {
    const found = list.find((p) => p.key === key);
    if (found) ordered.push(found);
  });
  list.forEach((p) => {
    if (!ordered.some((o) => o.key === p.key)) ordered.push(p);
  });
  return ordered;
});

function openPlatformByKey(key) {
  const pillar = corePillars.find((p) => p.key === key);
  if (!pillar) return;

  // check access state
  const state = accessStateBySlug.value[key];
  if (state && state.is_accessible === false) {
    showToast(state.status_note || "Diese Plattform ist aktuell gewartet.", "warning");
    return;
  }

  router.push(pillar.route);
}

function openProArtistDashboard() {
  router.push("/dashboard");
}

/* Drag & Drop */
function onDragStart(event, key) {
  if (!editMode.value) return;
  draggedKey.value = key;
  event.dataTransfer.effectAllowed = "move";
}

function onDragOver(event, key) {
  event.preventDefault();
  dragOverKey.value = key;
  event.dataTransfer.dropEffect = "move";
}

function onDrop(event, targetKey) {
  event.preventDefault();
  if (!draggedKey.value || draggedKey.value === targetKey) {
    dragOverKey.value = null;
    return;
  }
  const list = [...orderedPillars.value];
  const fromIdx = list.findIndex((p) => p.key === draggedKey.value);
  const toIdx = list.findIndex((p) => p.key === targetKey);
  if (fromIdx === -1 || toIdx === -1) return;
  const [moved] = list.splice(fromIdx, 1);
  list.splice(toIdx, 0, moved);
  savedOrder.value = list.map((p) => p.key);
  try {
    localStorage.setItem(HUB_PILLARS_ORDER_KEY, JSON.stringify(savedOrder.value));
  } catch {
    // ignore
  }
  draggedKey.value = null;
  dragOverKey.value = null;
  showToast("Reihenfolge gespeichert! ✨", "success");
}

function onDragEnd() {
  draggedKey.value = null;
  dragOverKey.value = null;
}

/* Data Loading */
async function loadAccessState() {
  try {
    const rows = await fetchManagedPlatformAccessState();
    accessStateBySlug.value = mapAccessStateRows(rows);
  } catch {
    accessStateBySlug.value = {};
  }
}

async function loadNotificationCount() {
  try {
    const { data } = await api.get("notifications/unread-count/");
    unreadNotifications.value = Number(data?.unread || 0);
  } catch {
    unreadNotifications.value = 0;
  }
}

async function loadHubBadges() {
  if (!isTeam.value) return;
  try {
    const [tasksRes, reviewRes, growproRes] = await Promise.all([
      api.get("tasks/", { params: { status: "OPEN,IN_PROGRESS", include_archived: 0, page_size: 1 } }).catch(() => null),
      api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", include_done: 1, include_archived: 0, page_size: 1 } }).catch(() => null),
      api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 200 } }).catch(() => null),
    ]);
    const taskCount = tasksRes?.data?.count ?? (Array.isArray(tasksRes?.data) ? tasksRes.data.length : 0);
    const overdueCount = await api.get("analytics/summary/").then((r) => r.data?.overdue_tasks || 0).catch(() => 0);
    const reviewCount = reviewRes?.data?.count ?? (Array.isArray(reviewRes?.data) ? reviewRes.data.length : 0);
    const growproItems = Array.isArray(growproRes?.data) ? growproRes.data : growproRes?.data?.results || [];
    const now = Date.now();
    const staleCount = growproItems.filter((g) => {
      if (["DONE", "ARCHIVED"].includes(g?.status)) return false;
      const last = g.last_logged_at ? new Date(g.last_logged_at).getTime() : null;
      return !last || (now - last) / (1000 * 60 * 60) > 72;
    }).length;

    hubBadges.value = {
      openTasks: Math.min(99, taskCount),
      overdueTasks: Math.min(99, overdueCount),
      pendingReviews: Math.min(99, reviewCount),
      staleGrowpro: Math.min(99, staleCount),
    };
  } catch {
    // ignore
  }
}

onMounted(async () => {
  await fetchProfile();
  try {
    const stored = localStorage.getItem(HUB_VIEW_MODE_KEY);
    if (stored === "admin" || stored === "user") {
      viewMode.value = isTeam.value ? stored : "user";
    } else {
      viewMode.value = isTeam.value ? "admin" : "user";
    }
  } catch {
    viewMode.value = isTeam.value ? "admin" : "user";
  }
  loadQuickShareLinks();
  await Promise.all([loadAccessState(), loadNotificationCount(), loadHubBadges()]);
});
</script>

<style scoped>
.unyq-hub-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 1320px;
  margin: 0 auto;
  padding: 16px 20px 80px;
}

/* User Relaxed Mode adjustments */
.user-relaxed-mode {
  gap: 36px;
}

/* Hero Section */
.hub-hero {
  border-radius: 24px;
  background: 
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.22), transparent 50%),
    radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.12), transparent 40%),
    linear-gradient(135deg, rgba(24, 28, 48, 0.85), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(124, 161, 255, 0.22);
  padding: clamp(28px, 4vw, 44px);
  position: relative;
  overflow: hidden;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.25);
}

.hero-inner {
  display: grid;
  grid-template-columns: 1.35fr 0.9fr;
  gap: 32px;
  align-items: center;
}

/* Mode Switcher */
.mode-switcher-bar {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.mode-pill-toggle {
  display: inline-flex;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.mode-btn {
  border: none;
  background: transparent;
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12.5px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.mode-btn.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.mode-hint {
  font-size: 11.5px;
  color: var(--muted);
  font-style: italic;
}

/* Hero Headings */

.hero-headline {
  font-size: clamp(2.2rem, 4vw, 3.2rem);
  font-weight: 900;
  margin: 0 0 10px;
  line-height: 1.1;
  background: linear-gradient(120deg, #ffffff 40%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtext {
  font-size: clamp(14px, 1.6vw, 16px);
  color: var(--muted);
  line-height: 1.6;
  max-width: 620px;
  margin: 0;
}

/* User Spotlight Card */
.user-spotlight-card {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(168, 85, 247, 0.25);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.sc-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sc-icon {
  font-size: 26px;
  background: rgba(168, 85, 247, 0.18);
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
}

.sc-track-preview {
  display: flex;
  flex-direction: column;
  padding: 10px 14px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  border-left: 3px solid #a855f7;
}

.sc-title {
  font-weight: 700;
  font-size: 14px;
}

.sc-artist {
  font-size: 12px;
  color: var(--muted);
}

/* Admin Status Card */
.admin-status-card {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.25);
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.asc-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13.5px;
}

.live-pill {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}

.asc-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  text-align: center;
}

.asc-item {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 8px 4px;
  display: flex;
  flex-direction: column;
}

.asc-item.alert .asc-val { color: #f87171; }
.asc-item.warn .asc-val { color: #fbbf24; }

.asc-val {
  font-size: 1.4rem;
  font-weight: 800;
  color: #60a5fa;
}

.asc-lbl {
  font-size: 10.5px;
  color: var(--muted);
  text-transform: uppercase;
}

.asc-btn {
  width: 100%;
}

/* Admin Quick Dock */
.admin-quick-dock {
  padding: 20px 24px;
  background: rgba(15, 23, 42, 0.65);
  border: 1px solid rgba(99, 102, 241, 0.25);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.dock-headline {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dock-badge {
  background: rgba(99, 102, 241, 0.2);
  color: #818cf8;
  font-size: 10.5px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
  letter-spacing: 0.06em;
}

.dock-headline h3 {
  margin: 0;
  font-size: 1.05rem;
}

.dock-links {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.dock-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  position: relative;
  transition: all 0.2s ease;
}

.dock-btn:hover {
  background: rgba(124, 161, 255, 0.18);
  border-color: rgba(124, 161, 255, 0.4);
}

.dock-btn.admin-tool {
  background: rgba(239, 68, 68, 0.12);
  border-color: rgba(239, 68, 68, 0.3);
  color: #fca5a5;
}

.dock-count {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 5px;
  border-radius: 999px;
}

.dock-count.alert { background: #ef4444; color: #fff; }
.dock-count.warn { background: #f59e0b; color: #fff; }

/* Main Section */
.hub-main-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
}

.section-title-wrap {
  display: flex;
  align-items: baseline;
  gap: 16px;
  flex-wrap: wrap;
}

.section-title-wrap h2 {
  margin: 0;
  font-size: clamp(1.35rem, 2.2vw, 1.75rem);
  font-weight: 800;
}

.section-title-wrap .section-subtext {
  margin: 0;
  font-size: 14px;
}

/* Pillars Grid */
.pillars-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr));
  gap: 22px;
}

.pillar-card {
  padding: 26px;
  display: flex;
  flex-direction: column;
  position: relative;
  cursor: pointer;
  transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
  border-radius: 20px;
  background: rgba(20, 26, 46, 0.75);
}

.pillar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 18px 36px rgba(0, 0, 0, 0.35);
}

/* Theme accent hover borders */
.pillar-card.theme-blue:hover { border-color: rgba(59, 130, 246, 0.6); }
.pillar-card.theme-emerald:hover { border-color: rgba(16, 185, 129, 0.6); }
.pillar-card.theme-amber:hover { border-color: rgba(245, 158, 11, 0.6); }
.pillar-card.theme-pink:hover { border-color: rgba(236, 72, 153, 0.6); }
.pillar-card.theme-purple:hover { border-color: rgba(168, 85, 247, 0.6); }
.pillar-card.theme-cyan:hover { border-color: rgba(6, 182, 212, 0.6); }
.pillar-card.theme-indigo:hover { border-color: rgba(99, 102, 241, 0.6); }
.pillar-card.theme-sky:hover { border-color: rgba(14, 165, 233, 0.6); }

.drag-handle-badge {
  position: absolute;
  top: 10px;
  right: 14px;
  font-size: 11px;
  color: var(--muted);
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 8px;
  border-radius: 4px;
}

.pillar-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}

.pillar-icon-box {
  width: 52px;
  height: 52px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.pillar-emoji {
  font-size: 26px;
}

.pillar-badges {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.badge-cat {
  font-size: 11px;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
}

.badge-accent {
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
}

.pill-blue { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.pill-emerald { background: rgba(16, 185, 129, 0.15); color: #34d399; }
.pill-amber { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.pill-pink { background: rgba(236, 72, 153, 0.15); color: #f472b6; }
.pill-purple { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.pill-cyan { background: rgba(6, 182, 212, 0.15); color: #22d3ee; }
.pill-indigo { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.pill-sky { background: rgba(14, 165, 233, 0.15); color: #38bdf8; }

.pillar-title {
  margin: 0 0 8px;
  font-size: 1.25rem;
  font-weight: 800;
}

.pillar-description {
  margin: 0 0 16px;
  font-size: 13.5px;
  color: var(--muted);
  line-height: 1.55;
  flex: 1;
}

.pillar-features-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.p-feat {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
}

.pillar-footer {
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.btn-pillar-action {
  width: 100%;
  justify-content: space-between;
  min-height: 40px;
  font-size: 13.5px;
}

.arrow-glyph {
  font-size: 16px;
  transition: transform 0.2s ease;
}

.pillar-card:hover .arrow-glyph {
  transform: translateX(4px);
}

/* User Highlights Banner */
.user-highlights-banner {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 24px;
  padding: 28px;
  background: 
    radial-gradient(circle at bottom right, rgba(99, 102, 241, 0.12), transparent 50%),
    rgba(15, 23, 42, 0.65);
}

.highlight-column {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.border-col {
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  padding: 0 24px;
}

.hl-badge {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 800;
  color: #38bdf8;
  letter-spacing: 0.06em;
}

.hl-forum { color: #818cf8; }
.hl-merch { color: #f472b6; }

.highlight-column h4 {
  margin: 0;
  font-size: 1.1rem;
}

.highlight-column p {
  margin: 0 0 12px;
  line-height: 1.5;
  flex: 1;
}

@media (max-width: 960px) {
  .hero-inner {
    grid-template-columns: 1fr;
  }
  .user-highlights-banner {
    grid-template-columns: 1fr;
  }
  .border-col {
    border-left: none;
    border-right: none;
    padding: 16px 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }
}

/* Team Exclusive Quick-Share Tool Styling */
.team-exclusive-tools {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(168, 85, 247, 0.04) 100%);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 18px;
  padding: 20px 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}
.tet-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}
.tet-badge {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #818cf8;
  display: block;
  margin-bottom: 4px;
}
.tet-title-group h3 {
  margin: 0 0 4px 0;
  font-size: 1.15rem;
}
.tet-active-links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}
.tet-link-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 8px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
}
.tl-info {
  display: flex;
  flex-direction: column;
}
.tl-info strong {
  font-size: 12px;
}
.danger-text {
  color: #f87171 !important;
}

/* Quick Share Modal */
.qs-modal {
  max-width: 520px;
  width: 100%;
}
.qs-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding-top: 10px;
}
.permissions-box {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.perm-checkboxes {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
}
.perm-checkboxes label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.created-link-box {
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 10px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.cl-row {
  display: flex;
  gap: 8px;
}
</style>
