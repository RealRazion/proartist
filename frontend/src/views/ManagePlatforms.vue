<template>
  <div class="manage-platforms-page">
    <!-- Ambient Backdrop Glow -->
    <div class="ambient-glow"></div>

    <!-- Header Section -->
    <header class="card control-header">
      <div class="header-main">
        <div class="header-badge">
          <span class="badge-icon">🛡️</span>
          <span>Admin &amp; Platform Systems</span>
        </div>
        <h1 class="header-title">Platform &amp; Artist Control Center</h1>
        <p class="header-subtitle">
          Zentrales Kontrollzentrum für Plattform-Status, Versionen und Artist-Sichtbarkeit (Turnier-Artist vs. UNYQ 360° Studio).
        </p>
      </div>

      <div class="header-actions">
        <button
          class="btn ghost btn-sm"
          type="button"
          @click="syncPlatforms"
          :disabled="syncing || loading || !isTeam"
          title="Erkennt automatisch alle aktiven Routen und Plattform-Dienste"
        >
          <span v-if="syncing" class="spinner-micro"></span>
          <span v-else>🔄</span>
          <span>{{ syncing ? "Erkenne..." : "Plattformen scannen" }}</span>
        </button>
        <button
          class="btn ghost btn-sm"
          type="button"
          @click="reloadAll"
          :disabled="loading || !isTeam"
        >
          <span>⚡</span>
          <span>{{ loading ? "Lade..." : "Aktualisieren" }}</span>
        </button>
      </div>
    </header>

    <!-- Permission Warning if not Team -->
    <section v-if="!isTeam" class="card permission-gate">
      <div class="gate-icon">🔒</div>
      <h2>Kein Zugriff</h2>
      <p class="muted">Nur Mitglieder des UNYQ-Teams und Administratoren können dieses Kontrollzentrum nutzen.</p>
    </section>

    <!-- Main Content when Team -->
    <template v-else>
      <!-- Mode & Navigation Tabs -->
      <nav class="card nav-strip">
        <div class="nav-tabs">
          <button
            class="tab-pill"
            :class="{ active: activeTab === 'platforms' }"
            @click="activeTab = 'platforms'"
          >
            <span class="tab-icon">🌐</span>
            <span>Plattform-Manager</span>
            <span class="tab-badge">{{ platforms.length }}</span>
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeTab === 'artist-visibility' }"
            @click="activeTab = 'artist-visibility'"
          >
            <span class="tab-icon">👥</span>
            <span>Artist-Sichtbarkeit &amp; Rollen</span>
            <span class="tab-badge accent">{{ artistsList.length }}</span>
          </button>
          <button
            class="tab-pill"
            :class="{ active: activeTab === 'audit-log' }"
            @click="activeTab = 'audit-log'"
          >
            <span class="tab-icon">📜</span>
            <span>Audit-Log</span>
            <span class="tab-badge">{{ historyEntries.length }}</span>
          </button>
        </div>

        <div class="nav-quick-stat">
          <span class="live-dot"></span>
          <span class="stat-text">{{ activePlatformsCount }} / {{ platforms.length }} Plattformen online</span>
        </div>
      </nav>

      <!-- ================================================================= -->
      <!-- TAB 1: PLATTFORM MANAGER -->
      <!-- ================================================================= -->
      <section v-if="activeTab === 'platforms'" class="platforms-view-grid">
        <!-- Overview & Quick Stats Bar -->
        <div class="platform-stats-row">
          <div class="pstat-card">
            <span class="pstat-label">Gesamte Plattformen</span>
            <strong class="pstat-val">{{ platforms.length }}</strong>
          </div>
          <div class="pstat-card success">
            <span class="pstat-label">Aktiv (Live)</span>
            <strong class="pstat-val">{{ activePlatformsCount }}</strong>
          </div>
          <div class="pstat-card warn">
            <span class="pstat-label">Wartung / Maintenance</span>
            <strong class="pstat-val">{{ maintenancePlatformsCount }}</strong>
          </div>
          <div class="pstat-card danger">
            <span class="pstat-label">Gesperrt / Locked</span>
            <strong class="pstat-val">{{ lockedPlatformsCount }}</strong>
          </div>
        </div>

        <!-- Platforms Cards Grid -->
        <div v-if="loading && !platforms.length" class="card loading-state">
          <div class="spinner-micro large"></div>
          <p class="muted">Plattformen werden geladen...</p>
        </div>

        <div v-else class="platform-cards-grid">
          <article
            v-for="item in platforms"
            :key="item.id"
            class="card platform-card"
            :class="`status-${item.status?.toLowerCase()}`"
          >
            <!-- Platform Card Header -->
            <div class="pcard-top">
              <div class="pcard-info">
                <div class="pcard-name-row">
                  <h3 class="pcard-title">{{ item.name }}</h3>
                  <span v-if="item.is_system_defined" class="badge-system">System</span>
                </div>
                <div class="pcard-meta">
                  <span class="pcard-slug">/{{ item.slug }}</span>
                  <span class="pcard-ver">v{{ item.version || "1.0" }}</span>
                </div>
              </div>

              <!-- Current Status Pill -->
              <span class="pcard-status-pill" :class="item.status?.toLowerCase()">
                {{ item.status }}
              </span>
            </div>

            <!-- Platform Description / Info -->
            <p class="pcard-desc">
              {{ getPlatformDescription(item.slug) }}
            </p>

            <!-- Inline Settings Controls -->
            <div class="pcard-settings-box">
              <div class="setting-row">
                <label class="setting-label">Status:</label>
                <select v-model="item.status" class="input input-sm setting-select">
                  <option value="ACTIVE">ACTIVE (Verfügbar)</option>
                  <option value="MAINTENANCE">MAINTENANCE (Wartung)</option>
                  <option value="LOCKED">LOCKED (Gesperrt)</option>
                </select>
              </div>

              <div class="setting-row">
                <label class="setting-label">Version:</label>
                <input
                  v-model.trim="item.version"
                  class="input input-sm setting-input"
                  placeholder="z. B. 2.1-live"
                  maxlength="20"
                />
              </div>

              <div class="setting-row checkbox-row">
                <label class="check-container">
                  <input type="checkbox" v-model="item.allow_non_team_users" />
                  <span class="checkmark"></span>
                  <span class="check-text">Für reguläre Artists freigegeben</span>
                </label>
              </div>

              <div class="setting-row">
                <label class="setting-label">Wartungs-Hinweis:</label>
                <input
                  v-model.trim="item.status_note"
                  class="input input-sm setting-input"
                  placeholder="Optionaler Hinweis für Nutzer"
                />
              </div>
            </div>

            <!-- Card Actions -->
            <div class="pcard-footer">
              <button
                class="btn ghost btn-sm btn-open"
                type="button"
                @click="openPlatformRoute(item.slug)"
                title="Plattform in ProArtist öffnen"
              >
                ↗ Öffnen
              </button>
              <div class="pcard-save-actions">
                <button
                  class="btn btn-primary btn-sm"
                  type="button"
                  @click="savePlatform(item)"
                  :disabled="busyId === item.id"
                >
                  {{ busyId === item.id ? "Speichere..." : "✓ Speichern" }}
                </button>
                <button
                  v-if="!item.is_system_defined"
                  class="btn ghost btn-sm btn-danger"
                  type="button"
                  @click="deletePlatform(item)"
                  :disabled="busyId === item.id"
                >
                  🗑️
                </button>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 2: ARTIST & MODUL-SICHTBARKEIT TOOL -->
      <!-- ================================================================= -->
      <section v-if="activeTab === 'artist-visibility'" class="visibility-tool-layout">
        <!-- Section Banner & System Default Configuration -->
        <div class="card default-policy-card">
          <div class="dpc-header">
            <span class="dpc-icon">🎛️</span>
            <div>
              <h3>Artist-Fokus &amp; Standard-Konfiguration</h3>
              <p class="muted">
                Entscheide, wie neu registrierte oder bestehende Artists UNYQ erleben. Artists können sich rein auf Turniere konzentrieren, ohne durch Studio-Tools abgelenkt zu werden.
              </p>
            </div>
          </div>

          <div class="policy-choice-grid">
            <div
              class="policy-card"
              :class="{ selected: defaultMode === 'CONTEST_ONLY' }"
              @click="setDefaultMode('CONTEST_ONLY')"
            >
              <div class="pc-radio">
                <span class="radio-circle" :class="{ checked: defaultMode === 'CONTEST_ONLY' }"></span>
              </div>
              <div class="pc-body">
                <div class="pc-title-row">
                  <span class="pc-icon">🏆</span>
                  <strong>Nur Turniere &amp; Battles (Standard)</strong>
                  <span class="pc-tag highlight">Schlank &amp; Fokus</span>
                </div>
                <p class="pc-desc">
                  Der Artist sieht ausschließlich die Contest-Arena, aktive Battles, Votings, sein Profil und Chats. Sämtliche Studio-Sachen (Projekte, Songs, Timeline, Aufgaben, Finance) bleiben komplett verborgen!
                </p>
                <div class="pc-features">
                  <span class="feat-pill positive">✓ Contest Arena</span>
                  <span class="feat-pill positive">✓ Battles &amp; Votings</span>
                  <span class="feat-pill positive">✓ Direkte Einreichungen</span>
                  <span class="feat-pill negative">✕ Kein Studio-Überhang</span>
                </div>
              </div>
            </div>

            <div
              class="policy-card"
              :class="{ selected: defaultMode === 'UNYQ_ARTIST' }"
              @click="setDefaultMode('UNYQ_ARTIST')"
            >
              <div class="pc-radio">
                <span class="radio-circle" :class="{ checked: defaultMode === 'UNYQ_ARTIST' }"></span>
              </div>
              <div class="pc-body">
                <div class="pc-title-row">
                  <span class="pc-icon">⭐</span>
                  <strong>UNYQ 360° Artist</strong>
                  <span class="pc-tag studio">Vollständiges Studio</span>
                </div>
                <p class="pc-desc">
                  Der Artist wird vollumfänglich von UNYQ gemanagt und erhält Zugriff auf das komplette ProArtist Creator Studio: Projekte, Songs, Timeline, Aufgaben-Kanban, GrowPro und Ökosystem.
                </p>
                <div class="pc-features">
                  <span class="feat-pill positive">✓ Volle Studio-Suite</span>
                  <span class="feat-pill positive">✓ Release-Planung</span>
                  <span class="feat-pill positive">✓ GrowPro Karriere</span>
                  <span class="feat-pill positive">✓ Ökosystem &amp; Finance</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Artist Search & Filter Toolbar -->
        <div class="card roster-toolbar">
          <div class="roster-search-col">
            <span class="search-icon">🔍</span>
            <input
              v-model.trim="artistSearchQuery"
              class="input roster-search-input"
              placeholder="Artist suchen nach Name, Username, Stadt oder Genre..."
            />
          </div>

          <div class="roster-filter-pills">
            <button
              class="rf-pill"
              :class="{ active: artistFilter === 'ALL' }"
              @click="artistFilter = 'ALL'"
            >
              Alle ({{ artistsList.length }})
            </button>
            <button
              class="rf-pill contest"
              :class="{ active: artistFilter === 'CONTEST_ONLY' }"
              @click="artistFilter = 'CONTEST_ONLY'"
            >
              🏆 Nur Turniere ({{ contestOnlyCount }})
            </button>
            <button
              class="rf-pill unyq"
              :class="{ active: artistFilter === 'UNYQ_ARTIST' }"
              @click="artistFilter = 'UNYQ_ARTIST'"
            >
              ⭐ UNYQ Artists ({{ unyqArtistCount }})
            </button>
          </div>
        </div>

        <!-- Artists Table / Cards List -->
        <div class="card roster-table-card">
          <div class="table-header-row">
            <div>
              <h3>Verwaltete Artists</h3>
              <p class="muted small">Wähle für jeden Artist direkt per Knopfdruck aus, was er sehen kann.</p>
            </div>
            <span class="roster-count-tag">{{ filteredArtists.length }} Artists angezeigt</span>
          </div>

          <div v-if="artistsLoading" class="loading-state">
            <div class="spinner-micro large"></div>
            <p class="muted">Lade Artist-Profile...</p>
          </div>

          <div v-else-if="!filteredArtists.length" class="empty-state">
            <p class="muted">Keine Artists mit diesem Suchfilter gefunden.</p>
          </div>

          <div v-else class="artists-table">
            <div class="at-head">
              <span class="col-artist">Artist</span>
              <span class="col-role">Rolle</span>
              <span class="col-status">Aktueller Modus</span>
              <span class="col-action">Modus &amp; Sichtbarkeit steuern</span>
              <span class="col-details">Details</span>
            </div>

            <div
              v-for="art in filteredArtists"
              :key="art.id"
              class="at-row"
              :class="{ 'row-saving': savingArtistId === art.id }"
            >
              <!-- Col: Artist Info -->
              <div class="col-artist art-profile-cell">
                <div class="art-avatar">
                  <img v-if="art.avatar_url" :src="art.avatar_url" :alt="art.name" />
                  <span v-else>{{ (art.name || art.username || "A").substring(0, 2).toUpperCase() }}</span>
                </div>
                <div class="art-names">
                  <strong class="art-display-name">{{ art.name || art.username }}</strong>
                  <span class="art-handle">@{{ art.username }}</span>
                </div>
              </div>

              <!-- Col: System Role -->
              <div class="col-role">
                <span class="badge-role" :class="getPrimaryRole(art).toLowerCase()">
                  {{ getPrimaryRole(art) }}
                </span>
              </div>

              <!-- Col: Current Focus Badge -->
              <div class="col-status">
                <span
                  class="badge-mode-pill"
                  :class="getArtistMode(art) === 'CONTEST_ONLY' ? 'contest-mode' : 'unyq-mode'"
                >
                  {{ getArtistMode(art) === "CONTEST_ONLY" ? "🏆 Nur Turniere" : "⭐ UNYQ Artist (360°)" }}
                </span>
              </div>

              <!-- Col: Mode Switcher Quick Actions -->
              <div class="col-action mode-switcher-buttons">
                <button
                  class="btn-mode-toggle btn-contest"
                  :class="{ active: getArtistMode(art) === 'CONTEST_ONLY' }"
                  @click="updateArtistMode(art, 'CONTEST_ONLY')"
                  :disabled="savingArtistId === art.id"
                  title="Artist sieht nur Turniere & Arena"
                >
                  🏆 Nur Turniere
                </button>
                <button
                  class="btn-mode-toggle btn-unyq"
                  :class="{ active: getArtistMode(art) === 'UNYQ_ARTIST' }"
                  @click="updateArtistMode(art, 'UNYQ_ARTIST')"
                  :disabled="savingArtistId === art.id"
                  title="Artist erhält vollen ProArtist Studio Zugriff"
                >
                  ⭐ UNYQ Artist
                </button>
              </div>

              <!-- Col: Details / Granular Permissions -->
              <div class="col-details">
                <button
                  class="btn ghost btn-micro btn-modules-open"
                  @click="openModuleConfigModal(art)"
                  title="Granulare Modul-Rechte bearbeiten"
                >
                  ⚙️ Module
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ================================================================= -->
      <!-- TAB 3: AUDIT LOG -->
      <!-- ================================================================= -->
      <section v-if="activeTab === 'audit-log'" class="audit-log-section card">
        <div class="audit-head">
          <div>
            <h2>Änderungs-Historie &amp; Audit</h2>
            <p class="muted">Protokoll aller Plattform-Statuswechsel und Artist-Rechte-Änderungen.</p>
          </div>
          <button class="btn ghost btn-sm" type="button" @click="loadHistory" :disabled="historyLoading">
            {{ historyLoading ? "Lade..." : "Aktualisieren" }}
          </button>
        </div>

        <div v-if="historyLoading && !historyEntries.length" class="loading-state">
          <div class="spinner-micro large"></div>
          <p class="muted">Lade Historie...</p>
        </div>

        <p v-else-if="!historyEntries.length" class="muted empty-audit">Noch keine Aktionen protokolliert.</p>

        <div v-else class="audit-timeline">
          <div
            v-for="entry in historyEntries"
            :key="entry.id"
            class="audit-item"
            :class="`sev-${entry.severity || 'info'}`"
          >
            <div class="ai-marker"></div>
            <div class="ai-content">
              <div class="ai-header">
                <strong>{{ historyTitle(entry) }}</strong>
                <span class="ai-date">{{ formatDate(entry.created_at) }}</span>
              </div>
              <p class="ai-desc">{{ historyDescription(entry) }}</p>
              <div class="ai-meta">
                <span v-if="entry.actor" class="ai-actor">👤 {{ entry.actor.name || entry.actor.username }}</span>
                <span v-if="entry.metadata?.platform_slug" class="ai-slug">🌐 /{{ entry.metadata.platform_slug }}</span>
                <span v-if="entry.metadata?.before?.status" class="ai-trans">
                  {{ entry.metadata.before.status }} → {{ entry.metadata.status }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </template>

    <!-- ================================================================= -->
    <!-- MODAL: GRANULAR MODULE CONFIGURATION FOR ARTIST -->
    <!-- ================================================================= -->
    <div v-if="moduleModalOpen" class="modal-backdrop" @click.self="closeModuleModal">
      <div class="modal-card">
        <div class="modal-header">
          <div>
            <h3>Modul-Sichtbarkeit für {{ selectedArtist?.name || selectedArtist?.username }}</h3>
            <p class="muted small">Wähle exakt aus, welche Bereiche dieser Artist im Seitenmenü sehen darf.</p>
          </div>
          <button class="btn ghost btn-micro" @click="closeModuleModal">✕</button>
        </div>

        <div class="modal-body module-toggles-grid">
          <label class="module-toggle-item">
            <div class="mti-info">
              <strong>🏆 Contest- &amp; Battle-Arena</strong>
              <small class="muted">Turniere, Runden-Einreichungen, Battles und Community Voting</small>
            </div>
            <input type="checkbox" v-model="selectedModules.arena" />
          </label>

          <label class="module-toggle-item">
            <div class="mti-info">
              <strong>🎙️ Creator Studio (Projekte &amp; Songs)</strong>
              <small class="muted">Song-Katalog, Versions-Verwaltung, Projekt-Workspaces</small>
            </div>
            <input type="checkbox" v-model="selectedModules.studio" />
          </label>

          <label class="module-toggle-item">
            <div class="mti-info">
              <strong>📋 Aufgaben &amp; Timeline</strong>
              <small class="muted">Kanban-Board, Meilensteine, Projekt-Kalender</small>
            </div>
            <input type="checkbox" v-model="selectedModules.tasks" />
          </label>

          <label class="module-toggle-item">
            <div class="mti-info">
              <strong>📈 GrowPro &amp; Karriere</strong>
              <small class="muted">Level-System, Points, Karriere-Ziele, Analytics</small>
            </div>
            <input type="checkbox" v-model="selectedModules.growth" />
          </label>

          <label class="module-toggle-item">
            <div class="mti-info">
              <strong>🌐 UNYQ Ökosystem &amp; Plattformen</strong>
              <small class="muted">Music Player, Creator Hub, Finanzen &amp; Payouts</small>
            </div>
            <input type="checkbox" v-model="selectedModules.ecosystem" />
          </label>
        </div>

        <div class="modal-footer">
          <button class="btn ghost btn-sm" @click="closeModuleModal">Abbrechen</button>
          <button class="btn btn-primary btn-sm" @click="saveCustomModules" :disabled="savingModules">
            {{ savingModules ? "Speichere..." : "Rechte speichern" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import { invalidateManagedPlatformAccessCache } from "../services/managedPlatforms";

const router = useRouter();
const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const activeTab = ref("platforms");
const loading = ref(false);
const syncing = ref(false);
const historyLoading = ref(false);
const busyId = ref(null);

const platforms = ref([]);
const historyEntries = ref([]);

/* Artist Roster & Visibility State */
const artistsList = ref([]);
const artistsLoading = ref(false);
const artistSearchQuery = ref("");
const artistFilter = ref("ALL");
const savingArtistId = ref(null);

// Global Default Mode for new signups
const defaultMode = ref(localStorage.getItem("unyq_admin_default_artist_mode") || "CONTEST_ONLY");

/* Modal State */
const moduleModalOpen = ref(false);
const selectedArtist = ref(null);
const savingModules = ref(false);
const selectedModules = ref({
  arena: true,
  studio: false,
  tasks: false,
  growth: false,
  ecosystem: false,
});

/* Computed Counts */
const activePlatformsCount = computed(() => platforms.value.filter((p) => p.status === "ACTIVE").length);
const maintenancePlatformsCount = computed(() => platforms.value.filter((p) => p.status === "MAINTENANCE").length);
const lockedPlatformsCount = computed(() => platforms.value.filter((p) => p.status === "LOCKED").length);

const contestOnlyCount = computed(() => {
  return artistsList.value.filter((a) => getArtistMode(a) === "CONTEST_ONLY").length;
});

const unyqArtistCount = computed(() => {
  return artistsList.value.filter((a) => getArtistMode(a) === "UNYQ_ARTIST").length;
});

const filteredArtists = computed(() => {
  let list = artistsList.value;

  // Filter by mode
  if (artistFilter.value === "CONTEST_ONLY") {
    list = list.filter((a) => getArtistMode(a) === "CONTEST_ONLY");
  } else if (artistFilter.value === "UNYQ_ARTIST") {
    list = list.filter((a) => getArtistMode(a) === "UNYQ_ARTIST");
  }

  // Filter by search query
  if (artistSearchQuery.value) {
    const q = artistSearchQuery.value.toLowerCase();
    list = list.filter((a) => {
      const name = (a.name || "").toLowerCase();
      const username = (a.username || a.user?.username || "").toLowerCase();
      const city = (a.city || "").toLowerCase();
      const genre = (a.genre || "").toLowerCase();
      return name.includes(q) || username.includes(q) || city.includes(q) || genre.includes(q);
    });
  }

  return list;
});

/* Helper Functions */
function getPlatformDescription(slug) {
  const map = {
    contests: "Contest & Battle Arena: Turniere, Runden-Einreichungen, Votings und Preispools.",
    music: "UNYQ Music Player: Streaming, offizielle Releases, Playlisten und Kataloge.",
    hub: "Creator Hub: Kollaborationen, Songwriting-Sessions, Kontakte und Foren.",
    "content-studio": "Content Studio & Academy: News, Tipps, Anleitungen und Videomaterial.",
    finance: "Finanzen & Auszahlungen: Einnahmen, Beteiligungen und Preisgeld-Auszahlungen.",
    "manage-platforms": "Platform Control: Zentrale Systemverwaltung für Administratoren.",
    "admin-hub": "Admin Control Hub: Überwachung aller Dienste und Berechtigungen.",
  };
  return map[slug] || "Automatisch erkannter UNYQ System-Dienst.";
}

function openPlatformRoute(slug) {
  const map = {
    contests: "/platforms/contests",
    music: "/platforms/music",
    hub: "/platforms/hub",
    "content-studio": "/platforms/content-studio",
    finance: "/platforms/finance",
    "manage-platforms": "/platforms/manage-platforms",
    "admin-hub": "/platforms/admin",
  };
  const path = map[slug] || `/platforms/${slug}`;
  router.push(path);
}

function formatDate(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  } catch {
    return "-";
  }
}

function historyTitle(entry) {
  return entry?.title || "Plattform-Aktion";
}

function historyDescription(entry) {
  const note = entry?.metadata?.status_note;
  if (note) return note;
  if (entry?.event_type === "managed_platform_deleted") {
    return "Plattform wurde aus der Verwaltung entfernt.";
  }
  if (entry?.metadata?.before?.status) {
    return `Statuswechsel von ${entry.metadata.before.status} zu ${entry.metadata.status}.`;
  }
  return entry?.description || "Keine weiteren Details.";
}

function getPrimaryRole(profile) {
  const keys = (profile.roles || []).map((r) => r.key);
  if (keys.includes("ADMIN")) return "ADMIN";
  if (keys.includes("TEAM")) return "TEAM";
  if (keys.includes("ARTIST")) return "ARTIST";
  return "MEMBER";
}

function getArtistMode(profile) {
  // Check socials.workspace_mode first
  if (profile.socials?.workspace_mode) {
    return profile.socials.workspace_mode;
  }
  // Check bio tag fallback
  if (profile.bio) {
    const match = profile.bio.match(/\[WorkspaceMode:\s*(CONTEST_ONLY|UNYQ_ARTIST)\]/i);
    if (match) return match[1].toUpperCase();
  }
  // Default to global setting
  return defaultMode.value;
}

function setDefaultMode(mode) {
  defaultMode.value = mode;
  localStorage.setItem("unyq_admin_default_artist_mode", mode);
  showToast(`Standard-Modus für neue Artists geändert zu: ${mode === "CONTEST_ONLY" ? "Nur Turniere" : "UNYQ Artist"}`, "info");
}

/* API Calls */
async function loadPlatforms() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("manage-platforms/");
    platforms.value = Array.isArray(data) ? data : data.results || [];
  } catch {
    platforms.value = [];
    showToast("Plattformen konnten nicht geladen werden.", "error");
  } finally {
    loading.value = false;
  }
}

async function loadHistory() {
  if (!isTeam.value) return;
  historyLoading.value = true;
  try {
    const { data } = await api.get("activity-feed/", {
      params: {
        limit: 25,
        types: "managed_platform_created,managed_platform_updated,managed_platform_deleted",
      },
    });
    historyEntries.value = Array.isArray(data) ? data : [];
  } catch {
    historyEntries.value = [];
  } finally {
    historyLoading.value = false;
  }
}

async function loadArtists() {
  if (!isTeam.value) return;
  artistsLoading.value = true;
  try {
    const { data } = await api.get("profiles/", { params: { page_size: 400 } });
    artistsList.value = Array.isArray(data) ? data : data?.results || [];
  } catch {
    artistsList.value = [];
  } finally {
    artistsLoading.value = false;
  }
}

async function savePlatform(item) {
  busyId.value = item.id;
  try {
    const payload = {
      version: item.version,
      status: item.status,
      allow_non_team_users: item.allow_non_team_users,
      status_note: item.status_note || "",
    };
    const { data } = await api.patch(`manage-platforms/${item.id}/`, payload);
    const idx = platforms.value.findIndex((row) => row.id === item.id);
    if (idx >= 0) platforms.value[idx] = data;
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    showToast(`Plattform "${item.name}" gespeichert.`, "success");
  } catch {
    showToast("Plattform konnte nicht gespeichert werden.", "error");
  } finally {
    busyId.value = null;
  }
}

async function deletePlatform(item) {
  const ok = window.confirm(`Plattform "${item.name}" wirklich aus der Verwaltung löschen?`);
  if (!ok) return;
  busyId.value = item.id;
  try {
    await api.delete(`manage-platforms/${item.id}/`);
    platforms.value = platforms.value.filter((row) => row.id !== item.id);
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    showToast("Plattform gelöscht.", "success");
  } catch {
    showToast("Plattform konnte nicht gelöscht werden.", "error");
  } finally {
    busyId.value = null;
  }
}

async function syncPlatforms() {
  syncing.value = true;
  try {
    const { data } = await api.post("manage-platforms/sync/");
    platforms.value = Array.isArray(data?.results) ? data.results : data?.results || [];
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    const created = Number(data?.stats?.created || 0);
    const updated = Number(data?.stats?.updated || 0);
    showToast(`Plattform-Katalog aktualisiert (${created} neu, ${updated} aktualisiert).`, "success");
  } catch {
    showToast("Synchronisation fehlgeschlagen.", "error");
  } finally {
    syncing.value = false;
  }
}

async function updateArtistMode(artist, newMode) {
  savingArtistId.value = artist.id;
  try {
    const nextSocials = {
      ...(artist.socials || {}),
      workspace_mode: newMode,
    };

    // Also update module_permissions default based on mode
    if (newMode === "CONTEST_ONLY") {
      nextSocials.module_permissions = {
        arena: true,
        studio: false,
        tasks: false,
        growth: false,
        ecosystem: false,
      };
    } else {
      nextSocials.module_permissions = {
        arena: true,
        studio: true,
        tasks: true,
        growth: true,
        ecosystem: true,
      };
    }

    const { data } = await api.patch(`profiles/${artist.id}/`, { socials: nextSocials });

    // Update in local array
    const idx = artistsList.value.findIndex((a) => a.id === artist.id);
    if (idx >= 0) artistsList.value[idx] = data;

    showToast(
      `${artist.name || artist.username} ist jetzt im Modus: ${newMode === "CONTEST_ONLY" ? "🏆 Nur Turniere" : "⭐ UNYQ Artist"}`,
      "success"
    );
  } catch {
    showToast("Modus konnte nicht aktualisiert werden.", "error");
  } finally {
    savingArtistId.value = null;
  }
}

function openModuleConfigModal(artist) {
  selectedArtist.value = artist;
  const currentPerms = artist.socials?.module_permissions || {};
  const isContest = getArtistMode(artist) === "CONTEST_ONLY";

  selectedModules.value = {
    arena: currentPerms.arena !== undefined ? currentPerms.arena : true,
    studio: currentPerms.studio !== undefined ? currentPerms.studio : !isContest,
    tasks: currentPerms.tasks !== undefined ? currentPerms.tasks : !isContest,
    growth: currentPerms.growth !== undefined ? currentPerms.growth : !isContest,
    ecosystem: currentPerms.ecosystem !== undefined ? currentPerms.ecosystem : !isContest,
  };
  moduleModalOpen.value = true;
}

function closeModuleModal() {
  moduleModalOpen.value = false;
  selectedArtist.value = null;
}

async function saveCustomModules() {
  if (!selectedArtist.value) return;
  savingModules.value = true;
  try {
    const nextSocials = {
      ...(selectedArtist.value.socials || {}),
      module_permissions: { ...selectedModules.value },
    };

    const { data } = await api.patch(`profiles/${selectedArtist.value.id}/`, { socials: nextSocials });

    const idx = artistsList.value.findIndex((a) => a.id === selectedArtist.value.id);
    if (idx >= 0) artistsList.value[idx] = data;

    showToast(`Modulrechte für ${selectedArtist.value.name || selectedArtist.value.username} aktualisiert.`, "success");
    closeModuleModal();
  } catch {
    showToast("Modulrechte konnten nicht gespeichert werden.", "error");
  } finally {
    savingModules.value = false;
  }
}

async function reloadAll() {
  await Promise.all([loadPlatforms(), loadHistory(), loadArtists()]);
}

onMounted(async () => {
  await fetchProfile();
  await reloadAll();
});
</script>

<style scoped>
.manage-platforms-page {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 22px;
  max-width: 1360px;
  margin: 0 auto;
  padding: 8px 16px 80px;
}

/* Ambient Backdrop Glow */
.ambient-glow {
  position: absolute;
  top: -60px;
  right: 15%;
  width: 500px;
  height: 250px;
  background: radial-gradient(circle, rgba(255, 170, 0, 0.08) 0%, rgba(0, 229, 255, 0.04) 50%, transparent 80%);
  pointer-events: none;
  z-index: 0;
}

/* Header */
.control-header {
  position: relative;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(20, 26, 40, 0.95), rgba(12, 16, 26, 0.98));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.35);
  backdrop-filter: blur(12px);
  z-index: 1;
}

.header-main {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.header-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--brand, #ffaa00);
}

.header-title {
  font-size: 1.85rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: #fff;
  margin: 0;
}

.header-subtitle {
  color: #94a3b8;
  font-size: 0.92rem;
  max-width: 650px;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* Nav Strip */
.nav-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  border-radius: 14px;
  background: rgba(15, 21, 33, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.nav-tabs {
  display: flex;
  gap: 8px;
}

.tab-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 18px;
  border-radius: 10px;
  font-size: 0.88rem;
  font-weight: 600;
  background: transparent;
  color: #94a3b8;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-pill:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.04);
}

.tab-pill.active {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.16), rgba(255, 170, 0, 0.06));
  color: #ffaa00;
  border-color: rgba(255, 170, 0, 0.35);
}

.tab-badge {
  font-size: 0.72rem;
  padding: 2px 7px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
}

.tab-badge.accent {
  background: rgba(0, 229, 255, 0.15);
  color: #00e5ff;
}

.nav-quick-stat {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: #94a3b8;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 10px #10b981;
}

/* Stats Row */
.platform-stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.pstat-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 16px 20px;
  background: rgba(18, 24, 38, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
}

.pstat-label {
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.pstat-val {
  font-size: 1.6rem;
  font-weight: 800;
  color: #fff;
}

.pstat-card.success .pstat-val { color: #10b981; }
.pstat-card.warn .pstat-val { color: #f59e0b; }
.pstat-card.danger .pstat-val { color: #ef4444; }

/* Platform Cards Grid */
.platform-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 18px;
}

.platform-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  gap: 16px;
  padding: 22px;
  background: rgba(18, 24, 38, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.platform-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 170, 0, 0.3);
}

.pcard-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.pcard-name-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pcard-title {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: #fff;
}

.badge-system {
  font-size: 0.65rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(0, 229, 255, 0.12);
  color: #00e5ff;
  border: 1px solid rgba(0, 229, 255, 0.25);
  font-weight: 700;
}

.pcard-meta {
  display: flex;
  gap: 8px;
  font-size: 0.78rem;
  color: #64748b;
  margin-top: 2px;
}

.pcard-status-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.pcard-status-pill.active {
  background: rgba(16, 185, 129, 0.15);
  color: #10b981;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.pcard-status-pill.maintenance {
  background: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.pcard-status-pill.locked {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.pcard-desc {
  margin: 0;
  font-size: 0.85rem;
  color: #94a3b8;
  line-height: 1.45;
}

.pcard-settings-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border-radius: 10px;
  background: rgba(10, 14, 23, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.setting-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.setting-row.checkbox-row {
  margin-top: 2px;
}

.setting-label {
  font-size: 0.74rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.setting-select,
.setting-input {
  background: rgba(15, 21, 33, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  border-radius: 8px;
  font-size: 0.82rem;
  padding: 6px 10px;
}

/* Checkbox Style */
.check-container {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
  color: #cbd5e1;
  cursor: pointer;
}

.pcard-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 14px;
}

.pcard-save-actions {
  display: flex;
  gap: 6px;
}

/* ================================================================= */
/* ARTIST VISIBILITY TAB */
/* ================================================================= */
.visibility-tool-layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.default-policy-card {
  padding: 24px;
  border-radius: 16px;
  background: rgba(18, 24, 38, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.dpc-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 20px;
}

.dpc-icon {
  font-size: 1.8rem;
}

.dpc-header h3 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  color: #fff;
}

.policy-choice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 16px;
}

.policy-card {
  display: flex;
  gap: 14px;
  padding: 20px;
  border-radius: 14px;
  background: rgba(12, 16, 26, 0.6);
  border: 1.5px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.policy-card:hover {
  background: rgba(15, 21, 33, 0.8);
  border-color: rgba(255, 255, 255, 0.2);
}

.policy-card.selected {
  background: linear-gradient(135deg, rgba(255, 170, 0, 0.1), rgba(255, 170, 0, 0.02));
  border-color: #ffaa00;
  box-shadow: 0 8px 24px rgba(255, 170, 0, 0.12);
}

.radio-circle {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: 2px solid #64748b;
  display: block;
  margin-top: 3px;
  transition: all 0.2s ease;
}

.radio-circle.checked {
  border-color: #ffaa00;
  background: radial-gradient(circle, #ffaa00 45%, transparent 55%);
}

.pc-body {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

.pc-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pc-tag {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  margin-left: auto;
}

.pc-tag.highlight {
  background: rgba(255, 170, 0, 0.15);
  color: #ffaa00;
}

.pc-tag.studio {
  background: rgba(0, 229, 255, 0.15);
  color: #00e5ff;
}

.pc-desc {
  margin: 0;
  font-size: 0.84rem;
  color: #94a3b8;
  line-height: 1.45;
}

.pc-features {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.feat-pill {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 6px;
}

.feat-pill.positive {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.feat-pill.negative {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

/* Roster Toolbar */
.roster-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 20px;
  border-radius: 14px;
  background: rgba(18, 24, 38, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.roster-search-col {
  position: relative;
  flex: 1;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 0.9rem;
  color: #64748b;
}

.roster-search-input {
  width: 100%;
  padding-left: 36px;
  background: rgba(12, 16, 26, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  color: #fff;
  font-size: 0.88rem;
}

.roster-filter-pills {
  display: flex;
  gap: 6px;
}

.rf-pill {
  padding: 7px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  color: #94a3b8;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.rf-pill:hover {
  color: #fff;
}

.rf-pill.active {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.rf-pill.contest.active {
  background: rgba(255, 170, 0, 0.15);
  color: #ffaa00;
  border-color: rgba(255, 170, 0, 0.35);
}

.rf-pill.unyq.active {
  background: rgba(0, 229, 255, 0.15);
  color: #00e5ff;
  border-color: rgba(0, 229, 255, 0.35);
}

/* Roster Table */
.roster-table-card {
  padding: 22px;
  border-radius: 16px;
  background: rgba(18, 24, 38, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.table-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.table-header-row h3 {
  margin: 0;
  font-size: 1.15rem;
  color: #fff;
}

.roster-count-tag {
  font-size: 0.78rem;
  color: #64748b;
  font-weight: 600;
}

.artists-table {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.at-head {
  display: grid;
  grid-template-columns: 2.5fr 1fr 1.6fr 2.4fr 0.8fr;
  padding: 10px 16px;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
  font-weight: 700;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.at-row {
  display: grid;
  grid-template-columns: 2.5fr 1fr 1.6fr 2.4fr 0.8fr;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  background: rgba(12, 16, 26, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.2s ease, border-color 0.2s ease;
}

.at-row:hover {
  background: rgba(15, 21, 33, 0.7);
  border-color: rgba(255, 255, 255, 0.1);
}

.at-row.row-saving {
  opacity: 0.5;
  pointer-events: none;
}

.art-profile-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.art-avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2d3748, #1a202c);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #ffaa00;
  font-size: 0.85rem;
  border: 1.5px solid rgba(255, 170, 0, 0.2);
  overflow: hidden;
  flex-shrink: 0;
}

.art-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.art-names {
  display: flex;
  flex-direction: column;
}

.art-display-name {
  color: #fff;
  font-size: 0.92rem;
}

.art-handle {
  font-size: 0.76rem;
  color: #64748b;
}

.badge-role {
  font-size: 0.7rem;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 4px;
}

.badge-role.admin { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
.badge-role.team { background: rgba(0, 229, 255, 0.15); color: #00e5ff; }
.badge-role.artist { background: rgba(255, 170, 0, 0.15); color: #ffaa00; }
.badge-role.member { background: rgba(148, 163, 184, 0.15); color: #94a3b8; }

.badge-mode-pill {
  font-size: 0.74rem;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  display: inline-block;
}

.badge-mode-pill.contest-mode {
  background: rgba(255, 170, 0, 0.12);
  color: #ffaa00;
  border: 1px solid rgba(255, 170, 0, 0.25);
}

.badge-mode-pill.unyq-mode {
  background: rgba(0, 229, 255, 0.12);
  color: #00e5ff;
  border: 1px solid rgba(0, 229, 255, 0.25);
}

.mode-switcher-buttons {
  display: flex;
  gap: 6px;
}

.btn-mode-toggle {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.76rem;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.04);
  color: #94a3b8;
  border: 1px solid rgba(255, 255, 255, 0.08);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-mode-toggle:hover {
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.btn-mode-toggle.btn-contest.active {
  background: rgba(255, 170, 0, 0.2);
  color: #ffaa00;
  border-color: #ffaa00;
}

.btn-mode-toggle.btn-unyq.active {
  background: rgba(0, 229, 255, 0.2);
  color: #00e5ff;
  border-color: #00e5ff;
}

/* Audit Log */
.audit-log-section {
  padding: 24px;
  border-radius: 16px;
  background: rgba(18, 24, 38, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.audit-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}

.audit-head h2 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  color: #fff;
}

.audit-timeline {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.audit-item {
  position: relative;
  display: flex;
  gap: 16px;
  padding: 14px 18px;
  border-radius: 10px;
  background: rgba(12, 16, 26, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.04);
}

.ai-marker {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ffaa00;
  margin-top: 6px;
  flex-shrink: 0;
}

.ai-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.ai-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ai-date {
  font-size: 0.74rem;
  color: #64748b;
}

.ai-desc {
  margin: 0;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.ai-meta {
  display: flex;
  gap: 10px;
  font-size: 0.76rem;
  color: #64748b;
  margin-top: 4px;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
  padding: 16px;
}

.modal-card {
  width: 100%;
  max-width: 520px;
  background: #121826;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 18px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.modal-header h3 {
  margin: 0 0 4px;
  font-size: 1.15rem;
  color: #fff;
}

.module-toggles-grid {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.module-toggle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  background: rgba(10, 14, 23, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.05);
  cursor: pointer;
}

.mti-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mti-info strong {
  font-size: 0.88rem;
  color: #fff;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 6px;
}

/* Spinner */
.spinner-micro {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-top-color: #ffaa00;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  display: inline-block;
}

.spinner-micro.large {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  gap: 12px;
  color: #94a3b8;
}

@media (max-width: 900px) {
  .control-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .at-head {
    display: none;
  }
  .at-row {
    grid-template-columns: 1fr;
    gap: 10px;
  }
}
</style>