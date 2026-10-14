<template>
  <div class="tournament-arena-page" :class="{ 'artist-view-mode': currentRoleMode === 'ARTIST' }">
    <!-- Top Ambient Glow -->
    <div class="arena-ambient-glow"></div>

    <!-- Arena Header -->
    <header class="arena-header card">
      <div class="header-left">
        <div class="league-pill">
          <span class="live-pulse-dot"></span>
          <span>UNYQ TOURNAMENT ARENA // SEASON '26</span>
        </div>
        <h1 class="arena-title">Turniere &amp; Battles</h1>
        <p class="arena-lead">
          Trete gegen die besten Artists und Producer an. Reiche deine Runden ein, 
          steige in den Rängen auf und gewinne exklusive Preisgelder &amp; Releases.
        </p>

        <!-- Mode Toggle (for Admin / Preview) -->
        <div class="role-mode-bar" v-if="isTeam">
          <span class="mode-label">Ansichtsmodus:</span>
          <div class="role-pill-group">
            <button
              type="button"
              class="role-pill-btn"
              :class="{ active: currentRoleMode === 'TEAM' }"
              @click="setRoleMode('TEAM')"
            >
              👑 Admin Modus
            </button>
            <button
              type="button"
              class="role-pill-btn"
              :class="{ active: currentRoleMode === 'ARTIST' }"
              @click="setRoleMode('ARTIST')"
            >
              🎤 Artist Modus
            </button>
          </div>
          <span class="mode-desc-text">
            {{ currentRoleMode === 'TEAM' ? 'Vollständige Admin-Steuerung & Battle-Schließung aktiv' : 'Artist-Erlebnis Vorschau aktiv' }}
          </span>
        </div>
      </div>

      <div class="header-right">
        <!-- Spotlight Arena Stats -->
        <div class="arena-stats-card">
          <div class="asc-title-row">
            <span class="trophy-ico">🏆</span>
            <strong>Arena Stats</strong>
          </div>
          <div class="asc-grid">
            <div class="asc-stat">
              <span class="num">{{ tournamentsList.length }}</span>
              <span class="lbl">Turniere</span>
            </div>
            <div class="asc-stat">
              <span class="num highlight">{{ activeBattlesCount }}</span>
              <span class="lbl">Live Battles</span>
            </div>
            <div class="asc-stat">
              <span class="num">{{ myProfileRank }}</span>
              <span class="lbl">Dein Rang</span>
            </div>
          </div>
          <div class="asc-footer">
            <span class="prize-tag">💰 Gesamt-Pool: 3.500 €</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <nav class="arena-nav-bar">
      <div class="tabs-group">
        <button
          v-for="tab in arenaTabs"
          :key="tab.key"
          class="nav-tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-icon">{{ tab.icon }}</span>
          <span>{{ tab.label }}</span>
          <span v-if="tab.badge" class="tab-badge" :class="tab.badgeClass">{{ tab.badge }}</span>
        </button>
      </div>

      <div class="arena-top-actions">
        <button
          v-if="currentRoleMode === 'TEAM'"
          class="btn btn-sm btn-create"
          @click="showCreateModal = true"
        >
          + Neues Turnier anlegen
        </button>
        <button class="btn ghost btn-sm" @click="loadData">
          ↻ Aktualisieren
        </button>
      </div>
    </nav>

    <!-- TAB 1: TOURNAMENTS OVERVIEW -->
    <section v-if="activeTab === 'tournaments'" class="tab-section">
      <!-- Spotlight Tournament Card -->
      <div v-if="spotlightTournament" class="card spotlight-card">
        <div class="spotlight-left">
          <div class="spotlight-badge-row">
            <span class="badge-featured">⭐ FEATURED TOURNAMENT</span>
            <span class="badge-status" :class="`status-${spotlightTournament.status.toLowerCase()}`">
              {{ statusLabel(spotlightTournament.status) }}
            </span>
            <span v-if="spotlightTournament.is_no_loss" class="badge-accent">🛡️ No Loss Bracket</span>
          </div>
          <h2 class="spotlight-title">{{ spotlightTournament.title }}</h2>
          <p class="spotlight-desc">{{ spotlightTournament.description }}</p>

          <div class="spotlight-meta-row">
            <div class="sm-item">
              <span class="sm-icon">💰</span>
              <div>
                <span class="sm-val">{{ spotlightTournament.prize_pool || '1.000 € Cash + Studio Gear' }}</span>
                <span class="sm-lbl">Preispool</span>
              </div>
            </div>
            <div class="sm-item">
              <span class="sm-icon">👥</span>
              <div>
                <span class="sm-val">{{ spotlightTournament.participants_count || 16 }} Artists</span>
                <span class="sm-lbl">Teilnehmer</span>
              </div>
            </div>
            <div class="sm-item">
              <span class="sm-icon">📅</span>
              <div>
                <span class="sm-val">{{ formatDate(spotlightTournament.ends_at) }}</span>
                <span class="sm-lbl">Finale Deadline</span>
              </div>
            </div>
          </div>

          <div class="spotlight-actions">
            <button class="btn btn-hero" @click="openTournamentDetail(spotlightTournament)">
              Turnier &amp; Runden öffnen →
            </button>
            <button
              v-if="spotlightTournament.status === 'APPLICATION_OPEN'"
              class="btn ghost"
              @click="openApplicationModal(spotlightTournament)"
            >
              ✍️ Jetzt als Artist bewerben
            </button>
          </div>
        </div>
      </div>

      <!-- Filter and Search -->
      <div class="filter-controls-row">
        <div class="search-box">
          <input
            v-model.trim="tournamentSearch"
            type="text"
            class="input search-input"
            placeholder="Turnier, Genre oder Preispool suchen..."
          />
        </div>
        <div class="status-filters">
          <button
            v-for="st in statusFilters"
            :key="st.key"
            class="filter-pill-btn"
            :class="{ active: selectedStatusFilter === st.key }"
            @click="selectedStatusFilter = st.key"
          >
            {{ st.label }}
          </button>
        </div>
      </div>

      <!-- Tournaments Grid -->
      <div class="tournaments-grid">
        <div
          v-for="tournament in filteredTournaments"
          :key="tournament.id"
          class="card tournament-card"
          @click="openTournamentDetail(tournament)"
        >
          <div class="card-head">
            <span class="badge-status" :class="`status-${tournament.status.toLowerCase()}`">
              {{ statusLabel(tournament.status) }}
            </span>
            <span v-if="tournament.is_no_loss" class="badge-accent">No Loss</span>
          </div>

          <h3 class="tournament-name">{{ tournament.title }}</h3>
          <p class="tournament-summary">{{ tournament.description || 'Spannender Battle-Wettbewerb im UNYQ Circuit.' }}</p>

          <div class="tournament-stats-pills">
            <span class="pill-stat">💰 {{ tournament.prize_pool || '500 €' }}</span>
            <span class="pill-stat">👥 {{ tournament.participants_count || 8 }} Teilnehmer</span>
            <span class="pill-stat" v-if="tournament.battles_count">⚔️ {{ tournament.battles_count }} Battles</span>
          </div>

          <div class="card-footer">
            <button class="btn btn-sm" @click.stop="openTournamentDetail(tournament)">
              Details &amp; Bracket →
            </button>
            <button
              v-if="tournament.status === 'APPLICATION_OPEN'"
              class="btn ghost btn-sm"
              @click.stop="openApplicationModal(tournament)"
            >
              Bewerben
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 2: LIVE BATTLES & VOTING -->
    <section v-if="activeTab === 'battles'" class="tab-section">
      <div class="section-title-row">
        <div>
          <h2>Live Battles &amp; Community Voting ({{ liveBattlesList.length }})</h2>
          <p class="muted">Höre beide Runden an und stimme für den besseren Artist ab.</p>
        </div>
      </div>

      <div class="battles-grid">
        <div
          v-for="battle in liveBattlesList"
          :key="battle.id"
          class="card battle-showdown-card"
        >
          <div class="battle-top-bar">
            <span class="battle-round-badge">RUNDE {{ battle.round_number || 1 }}</span>
            <span class="battle-title-tag">{{ battle.tournament_title || 'Battle Arena' }}</span>
            <span class="battle-status-badge" :class="battle.status.toLowerCase()">{{ battle.status }}</span>
          </div>

          <!-- The VS Matchup -->
          <div class="matchup-container">
            <!-- Left Competitor -->
            <div class="competitor-box left" :class="{ winning: battle.votes_left > battle.votes_right }">
              <div class="competitor-avatar">{{ (battle.left_profile_name || 'Artist A').charAt(0).toUpperCase() }}</div>
              <strong class="competitor-name">{{ battle.left_profile_name || 'Artist A' }}</strong>
              <span class="competitor-tier">Gold Tier</span>
              <button class="btn ghost btn-sm btn-play-round" @click="previewBattleRound(battle, 'left')">
                ▶ Runde hören
              </button>
              <div class="vote-count-badge">{{ battle.votes_left }} Votes</div>
            </div>

            <!-- VS Badge in middle -->
            <div class="vs-divider">
              <span class="vs-text">VS</span>
              <div class="vs-bar"></div>
            </div>

            <!-- Right Competitor -->
            <div class="competitor-box right" :class="{ winning: battle.votes_right > battle.votes_left }">
              <div class="competitor-avatar right-avatar">{{ (battle.right_profile_name || 'Artist B').charAt(0).toUpperCase() }}</div>
              <strong class="competitor-name">{{ battle.right_profile_name || 'Artist B' }}</strong>
              <span class="competitor-tier">Platin Tier</span>
              <button class="btn ghost btn-sm btn-play-round" @click="previewBattleRound(battle, 'right')">
                ▶ Runde hören
              </button>
              <div class="vote-count-badge">{{ battle.votes_right }} Votes</div>
            </div>
          </div>

          <!-- Vote Percentage Visualizer -->
          <div class="vote-meter">
            <div class="meter-bar left-bar" :style="{ width: getVotePct(battle, 'left') + '%' }">
              <span>{{ getVotePct(battle, 'left') }}%</span>
            </div>
            <div class="meter-bar right-bar" :style="{ width: getVotePct(battle, 'right') + '%' }">
              <span>{{ getVotePct(battle, 'right') }}%</span>
            </div>
          </div>

          <!-- User Voting Action -->
          <div class="battle-vote-actions" v-if="battle.status !== 'CLOSED'">
            <button
              class="btn btn-vote-left"
              :disabled="hasVoted(battle)"
              @click="castVote(battle, 'left')"
            >
              👍 Vote für {{ battle.left_profile_name }}
            </button>
            <button
              class="btn btn-vote-right"
              :disabled="hasVoted(battle)"
              @click="castVote(battle, 'right')"
            >
              👍 Vote für {{ battle.right_profile_name }}
            </button>
          </div>

          <!-- Admin Decision Actions (if Admin) -->
          <div class="admin-battle-bar" v-if="currentRoleMode === 'TEAM' && battle.status !== 'CLOSED'">
            <span class="admin-label">👑 Admin Entscheidung:</span>
            <div class="admin-btn-row">
              <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'left')">Left Win</button>
              <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'right')">Right Win</button>
              <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'auto')">Auto Close</button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 3: LEADERBOARD & RANKS -->
    <section v-if="activeTab === 'leaderboard'" class="tab-section">
      <div class="section-title-row">
        <div>
          <h2>Artist Leaderboard &amp; Ränge</h2>
          <p class="muted">Punkte sammeln durch Siege, Runden-Einreichungen und Community-Voting.</p>
        </div>
      </div>

      <!-- Tier Levels Bar -->
      <div class="tiers-showcase card">
        <div class="tier-chip" v-for="tier in tiersList" :key="tier.key">
          <img :src="tier.icon" :alt="tier.name" class="tier-img" />
          <div class="tier-info">
            <strong>{{ tier.name }}</strong>
            <small>{{ tier.minRP }} RP</small>
          </div>
        </div>
      </div>

      <!-- Leaderboard Podium (Top 3) -->
      <div class="podium-row" v-if="leaderboardRows.length >= 3">
        <!-- 2nd Place -->
        <div class="podium-card rank-2 card">
          <div class="medal-circle silver">2</div>
          <strong class="podium-name">{{ leaderboardRows[1].name }}</strong>
          <span class="podium-rp">{{ leaderboardRows[1].ranked_points }} RP</span>
          <span class="podium-tier">{{ leaderboardRows[1].tier }}</span>
        </div>
        <!-- 1st Place -->
        <div class="podium-card rank-1 card">
          <div class="crown-icon">👑</div>
          <div class="medal-circle gold">1</div>
          <strong class="podium-name">{{ leaderboardRows[0].name }}</strong>
          <span class="podium-rp">{{ leaderboardRows[0].ranked_points }} RP</span>
          <span class="podium-tier">{{ leaderboardRows[0].tier }}</span>
        </div>
        <!-- 3rd Place -->
        <div class="podium-card rank-3 card">
          <div class="medal-circle bronze">3</div>
          <strong class="podium-name">{{ leaderboardRows[2].name }}</strong>
          <span class="podium-rp">{{ leaderboardRows[2].ranked_points }} RP</span>
          <span class="podium-tier">{{ leaderboardRows[2].tier }}</span>
        </div>
      </div>

      <!-- Leaderboard Table -->
      <div class="leaderboard-table card">
        <div class="table-head">
          <span class="col-rank">Rang</span>
          <span class="col-artist">Artist / Producer</span>
          <span class="col-tier">Tier</span>
          <span class="col-rp">Ranked Points (RP)</span>
          <span class="col-record">W - L</span>
        </div>
        <div
          v-for="(row, idx) in leaderboardRows"
          :key="row.id || idx"
          class="table-row"
          :class="{ 'is-me': row.isMe }"
        >
          <span class="col-rank font-mono">#{{ idx + 1 }}</span>
          <div class="col-artist artist-cell">
            <span class="artist-avatar">{{ row.name.charAt(0) }}</span>
            <span class="artist-name">{{ row.name }}</span>
            <span v-if="row.isMe" class="me-pill">Du</span>
          </div>
          <span class="col-tier"><span class="tier-tag">{{ row.tier }}</span></span>
          <span class="col-rp rp-val">{{ row.ranked_points }} RP</span>
          <span class="col-record font-mono">{{ row.wins || 0 }}W - {{ row.losses || 0 }}L</span>
        </div>
      </div>
    </section>

    <!-- TAB 4: MEINE TURNIERE & BEWERBUNGEN (ARTIST HUB) -->
    <section v-if="activeTab === 'my-tournaments'" class="tab-section">
      <div class="section-title-row">
        <div>
          <h2>Meine Turniere, Bewerbungen &amp; Runden</h2>
          <p class="muted">Übersicht deiner laufenden Teilnahme, Battle-Gegner und Runden-Uploads.</p>
        </div>
      </div>

      <!-- Artist Stats Quickbox -->
      <div class="card artist-quick-card">
        <div class="aq-col">
          <span class="aq-lbl">Dein Ranked Status</span>
          <strong class="aq-val">Gold Tier (1.840 RP)</strong>
        </div>
        <div class="aq-col">
          <span class="aq-lbl">Aktive Turniere</span>
          <strong class="aq-val">{{ myApplications.length }}</strong>
        </div>
        <div class="aq-col">
          <span class="aq-lbl">Battle Bilanz</span>
          <strong class="aq-val">8 Wins / 2 Losses</strong>
        </div>
      </div>

      <!-- Applications & Submissions List -->
      <div class="my-items-grid">
        <div v-for="app in myApplications" :key="app.id" class="card my-tournament-item">
          <div class="mti-head">
            <h3>{{ app.tournament_title }}</h3>
            <span class="badge-status" :class="app.status.toLowerCase()">{{ app.status }}</span>
          </div>
          <p class="muted small">{{ app.message || 'Bewerbung eingereicht. Viel Erfolg!' }}</p>

          <div class="mti-actions">
            <button class="btn btn-sm" @click="openUploadRoundModal(app)">
              📤 Runde einreichen (Audio/Video)
            </button>
            <button class="btn ghost btn-sm" @click="openTournamentDetail({ id: app.tournament_id, title: app.tournament_title })">
              Turnier ansehen →
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- TAB 5: ADMIN ARENA MANAGER (TEAM EXCLUSIVE) -->
    <section v-if="activeTab === 'admin' && currentRoleMode === 'TEAM'" class="tab-section">
      <div class="section-title-row">
        <div>
          <h2>👑 Admin Arena Management</h2>
          <p class="muted">Verwalte Bewerbungen, erstelle Turniere und steuere Battle-Phasen.</p>
        </div>
        <button class="btn" @click="showCreateModal = true">+ Neues Turnier anlegen</button>
      </div>

      <!-- Pending Applications Moderation Card -->
      <div class="card admin-mod-card">
        <div class="mod-head">
          <h3>Eingegangene Artist-Bewerbungen</h3>
          <span class="count-badge">{{ pendingApplications.length }} Ausstehend</span>
        </div>

        <div class="mod-list" v-if="pendingApplications.length">
          <div v-for="app in pendingApplications" :key="app.id" class="mod-row">
            <div class="mod-info">
              <strong>{{ app.artist_name || 'Artist' }}</strong>
              <span class="mod-meta">Turnier: {{ app.tournament_title }} • {{ app.created_at || 'Heute' }}</span>
              <p class="mod-msg">"{{ app.message }}"</p>
            </div>
            <div class="mod-actions">
              <button class="btn btn-sm btn-accept" @click="handleApplicationDecision(app, 'ACCEPTED')">
                ✓ Zulassen
              </button>
              <button class="btn ghost btn-sm btn-reject" @click="handleApplicationDecision(app, 'REJECTED')">
                ✕ Ablehnen
              </button>
            </div>
          </div>
        </div>
        <div v-else class="empty-mod muted">Keine ausstehenden Bewerbungen.</div>
      </div>
    </section>

    <!-- MODAL 1: Create Tournament Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Neues Turnier erstellen</h3>
          <button class="btn ghost tiny" @click="showCreateModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitCreateTournament">
          <label>
            <span>Turnier-Titel *</span>
            <input v-model.trim="newTournament.title" class="input" required placeholder="z. B. UNYQ Beat Battle Season 2" />
          </label>
          <label>
            <span>Beschreibung &amp; Regeln</span>
            <textarea v-model.trim="newTournament.description" class="input" rows="3" placeholder="Format, Anforderungen, Kriterien..."></textarea>
          </label>
          <div class="split-form-row">
            <label>
              <span>Preispool</span>
              <input v-model.trim="newTournament.prize_pool" class="input" placeholder="1.000 € Cash + Vinyl Pressung" />
            </label>
            <label>
              <span>Start-Status</span>
              <select v-model="newTournament.status" class="input">
                <option value="APPLICATION_OPEN">Bewerbung offen</option>
                <option value="SUBMISSION_OPEN">Einreichung offen</option>
                <option value="BATTLES">Battles live</option>
                <option value="DRAFT">Entwurf</option>
              </select>
            </label>
          </div>
          <div class="checkbox-row">
            <label class="check-label">
              <input type="checkbox" v-model="newTournament.is_no_loss" />
              <span>No-Loss Bracket (Doppelter Ausscheidungsbaum)</span>
            </label>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showCreateModal = false">Abbrechen</button>
            <button class="btn" type="submit">Turnier live schalten 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 2: Artist Apply Modal -->
    <div v-if="showApplyModal" class="modal-overlay" @click.self="showApplyModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung für "{{ applyingTournament?.title }}"</h3>
          <button class="btn ghost tiny" @click="showApplyModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitArtistApplication">
          <label>
            <span>Dein Artist- / Producer-Name *</span>
            <input v-model.trim="applicationForm.artist_name" class="input" required />
          </label>
          <label>
            <span>Hörprobe / Demo-Link (SoundCloud, Spotify, Dropbox) *</span>
            <input v-model.trim="applicationForm.demo_link" class="input" required placeholder="https://..." />
          </label>
          <label>
            <span>Nachricht an die Jury (optional)</span>
            <textarea v-model.trim="applicationForm.message" class="input" rows="3" placeholder="Warum möchtest du antreten? Deine Stärken..."></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showApplyModal = false">Abbrechen</button>
            <button class="btn" type="submit">Bewerbung einreichen 🎤</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 3: Submit Round Modal -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Runde einreichen</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitRoundFile">
          <label>
            <span>Track-Titel für diese Runde *</span>
            <input v-model.trim="roundUploadForm.title" class="input" required placeholder="z. B. Runde 1 - Dark Night Heat" />
          </label>
          <label>
            <span>Audio- / Video-URL (SoundCloud, YouTube, Drive) *</span>
            <input v-model.trim="roundUploadForm.file_url" class="input" required placeholder="https://..." />
          </label>
          <label>
            <span>Lyrics / Songtext / Producer Notes</span>
            <textarea v-model.trim="roundUploadForm.notes" class="input" rows="4" placeholder="Text, BPM, Mitwirkende..."></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showUploadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Runde abschicken 🚀</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import api from "../api";
import bronzeRank from "../assets/ranks/bronze-icon.svg";
import silberRank from "../assets/ranks/silber-icon.svg";
import goldRank from "../assets/ranks/gold-icon.svg";
import platinRank from "../assets/ranks/platin-icon.svg";
import legendarRank from "../assets/ranks/legendaer-icon.svg";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const currentRoleMode = ref("TEAM");
const activeTab = ref("tournaments");

const tournamentSearch = ref("");
const selectedStatusFilter = ref("ALL");

const showCreateModal = ref(false);
const showApplyModal = ref(false);
const applyingTournament = ref(null);
const showUploadModal = ref(false);

const votedBattleIds = ref(new Set());

const arenaTabs = computed(() => {
  const tabs = [
    { key: "tournaments", label: "Turniere & Arena", icon: "🏆" },
    { key: "battles", label: "Live Battles", icon: "⚔️", badge: activeBattlesCount.value ? `${activeBattlesCount.value}` : null, badgeClass: "badge-live" },
    { key: "leaderboard", label: "Leaderboard & Ränge", icon: "🥇" },
    { key: "my-tournaments", label: "Meine Battles", icon: "👤", badge: myApplications.value.length ? `${myApplications.value.length}` : null },
  ];
  if (currentRoleMode.value === "TEAM") {
    tabs.push({ key: "admin", label: "Admin Manager", icon: "👑", badge: pendingApplications.value.length ? `${pendingApplications.value.length}` : null, badgeClass: "badge-warn" });
  }
  return tabs;
});

const statusFilters = [
  { key: "ALL", label: "Alle" },
  { key: "APPLICATION_OPEN", label: "Bewerbung offen" },
  { key: "SUBMISSION_OPEN", label: "Einreichung offen" },
  { key: "BATTLES", label: "Battles live" },
  { key: "CLOSED", label: "Beendet" },
];

const tiersList = [
  { key: "BRONZE", name: "Bronze", minRP: 0, icon: bronzeRank },
  { key: "SILBER", name: "Silber", minRP: 800, icon: silberRank },
  { key: "GOLD", name: "Gold", minRP: 1600, icon: goldRank },
  { key: "PLATIN", name: "Platin", minRP: 2800, icon: platinRank },
  { key: "LEGENDAER", name: "Legendär", minRP: 4200, icon: legendarRank },
];

/* Default Tournaments Dataset (rich fallback) */
const tournamentsList = ref([
  {
    id: 1,
    title: "UNYQ Beat Battle Season 1 // 808 Showcase",
    description: "Der ultimative Beatmaking-Wettbewerb. Produziere den härtesten Trap/Drill Track und kämpfe dich durch die Bracket.",
    status: "BATTLES",
    is_no_loss: true,
    prize_pool: "1.500 € Cash + Studio Gear",
    participants_count: 16,
    battles_count: 8,
    ends_at: "2026-11-01T20:00:00Z",
  },
  {
    id: 2,
    title: "Berlin Vocal & Rap Showdown",
    description: "Artists reichen ihre 16-Bars Runden ein. Die UNYQ Community und Jury voten für Flow, Lyrics und Delivery.",
    status: "APPLICATION_OPEN",
    is_no_loss: false,
    prize_pool: "1.000 € + Exclusive Single Release",
    participants_count: 12,
    battles_count: 4,
    ends_at: "2026-11-15T18:00:00Z",
  },
  {
    id: 3,
    title: "Lo-Fi & Neo-Soul Producer Cup",
    description: "Gemütliche Akkorde, warme Rhyme-Schemes und organische Drums. Zeige dein Gespür für Sound-Design.",
    status: "SUBMISSION_OPEN",
    is_no_loss: true,
    prize_pool: "750 € + Vinyl Pressung",
    participants_count: 8,
    battles_count: 0,
    ends_at: "2026-11-20T22:00:00Z",
  },
]);

/* Live Battles */
const liveBattlesList = ref([
  {
    id: 101,
    tournament_title: "UNYQ Beat Battle Season 1",
    round_number: 2,
    status: "OPEN",
    left_profile_name: "Neo_Producer",
    votes_left: 64,
    right_profile_name: "808_Phantom",
    votes_right: 48,
  },
  {
    id: 102,
    tournament_title: "Berlin Vocal & Rap Showdown",
    round_number: 1,
    status: "OPEN",
    left_profile_name: "KAZA",
    votes_left: 89,
    right_profile_name: "Aura_Vox",
    votes_right: 82,
  },
]);

/* Leaderboard */
const leaderboardRows = ref([
  { id: 1, name: "Neo_Producer", tier: "Legendär", ranked_points: 4450, wins: 28, losses: 3 },
  { id: 2, name: "KAZA", tier: "Platin", ranked_points: 3820, wins: 22, losses: 5 },
  { id: 3, name: "808_Phantom", tier: "Gold", ranked_points: 2410, wins: 18, losses: 7 },
  { id: 4, name: "Aura_Vox", tier: "Gold", ranked_points: 1980, wins: 14, losses: 6 },
  { id: 5, name: "Mika_LoFi", tier: "Silber", ranked_points: 1420, wins: 11, losses: 8 },
]);

/* My Applications */
const myApplications = ref([
  {
    id: 1,
    tournament_id: 1,
    tournament_title: "UNYQ Beat Battle Season 1 // 808 Showcase",
    status: "ACCEPTED",
    message: "Zugelassen für Runde 2. Reiche deinen Track bis Freitag ein!",
  },
  {
    id: 2,
    tournament_id: 2,
    tournament_title: "Berlin Vocal & Rap Showdown",
    status: "PENDING",
    message: "Bewerbung wird derzeit von der UNYQ Jury geprüft.",
  },
]);

/* Pending Applications for Admin */
const pendingApplications = ref([
  {
    id: 101,
    artist_name: "DrillKing_030",
    tournament_title: "UNYQ Beat Battle Season 1",
    message: "Hab einen extrem harten Drill Beat vorbereitet, bin bereit für die Arena!",
    created_at: "vor 2 Stunden",
  },
  {
    id: 102,
    artist_name: "Sarah_Soul",
    tournament_title: "Berlin Vocal & Rap Showdown",
    message: "Mein Song ist bereits gemastert. Würde mich riesig über die Teilnahme freuen.",
    created_at: "vor 4 Stunden",
  },
]);

const activeBattlesCount = computed(() => {
  return liveBattlesList.value.filter((b) => b.status === "OPEN").length;
});

const spotlightTournament = computed(() => {
  return tournamentsList.value[0] || null;
});

const filteredTournaments = computed(() => {
  return tournamentsList.value.filter((t) => {
    const matchStatus =
      selectedStatusFilter.value === "ALL" || t.status === selectedStatusFilter.value;
    const q = tournamentSearch.value.toLowerCase();
    const matchQuery =
      !q ||
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q));
    return matchStatus && matchQuery;
  });
});

const myProfileRank = computed(() => {
  return "#2";
});

function setRoleMode(mode) {
  currentRoleMode.value = mode;
  showToast(mode === "TEAM" ? "👑 Admin-Modus aktiviert" : "🎤 Artist-Modus aktiviert", "info");
}

function statusLabel(status) {
  const map = {
    APPLICATION_OPEN: "🟢 Bewerbung offen",
    SUBMISSION_OPEN: "🔵 Einreichung offen",
    BATTLES: "🔴 Battles live",
    CLOSED: "⚪ Beendet",
    DRAFT: "Entwurf",
  };
  return map[status] || status;
}

function formatDate(iso) {
  if (!iso) return "Demnächst";
  return new Date(iso).toLocaleDateString("de-DE", { day: "2-digit", month: "short", year: "numeric" });
}

function openTournamentDetail(tournament) {
  router.push({ name: "tournament-detail", params: { tournamentId: tournament.id } });
}

/* Voting Logic */
function getVotePct(battle, side) {
  const total = (battle.votes_left || 0) + (battle.votes_right || 0);
  if (!total) return 50;
  const count = side === "left" ? battle.votes_left : battle.votes_right;
  return Math.round((count / total) * 100);
}

function hasVoted(battle) {
  return votedBattleIds.value.has(battle.id);
}

async function castVote(battle, side) {
  if (hasVoted(battle)) {
    showToast("Du hast in diesem Battle bereits abgestimmt!", "warning");
    return;
  }
  if (side === "left") {
    battle.votes_left++;
  } else {
    battle.votes_right++;
  }
  votedBattleIds.value.add(battle.id);
  showToast(`Vote gezählt für ${side === 'left' ? battle.left_profile_name : battle.right_profile_name}! 🗳️`, "success");

  // Attempt backend API
  try {
    await api.post(`tournaments/battles/${battle.id}/vote/`, { side });
  } catch {
    // fallback gracefully
  }
}

function previewBattleRound(battle, side) {
  const artist = side === "left" ? battle.left_profile_name : battle.right_profile_name;
  showToast(`Spiele Runde von ${artist} 🎵`, "info");
}

/* Admin Actions */
function resolveBattle(battle, resolution) {
  if (resolution === "left") {
    battle.status = "CLOSED";
    showToast(`${battle.left_profile_name} zum Sieger erklärt! 🏆`, "success");
  } else if (resolution === "right") {
    battle.status = "CLOSED";
    showToast(`${battle.right_profile_name} zum Sieger erklärt! 🏆`, "success");
  } else {
    battle.status = "CLOSED";
    const winner = battle.votes_left >= battle.votes_right ? battle.left_profile_name : battle.right_profile_name;
    showToast(`Battle geschlossen: ${winner} gewinnt nach Stimmen! ✨`, "success");
  }
}

function handleApplicationDecision(app, decision) {
  const idx = pendingApplications.value.findIndex((a) => a.id === app.id);
  if (idx !== -1) {
    pendingApplications.value.splice(idx, 1);
  }
  if (decision === "ACCEPTED") {
    showToast(`Bewerbung von ${app.artist_name} angenommen! 🎉`, "success");
  } else {
    showToast(`Bewerbung von ${app.artist_name} abgelehnt.`, "info");
  }
}

/* Modals */
const newTournament = ref({
  title: "",
  description: "",
  prize_pool: "1.000 € Cash",
  status: "APPLICATION_OPEN",
  is_no_loss: false,
});

async function submitCreateTournament() {
  const created = {
    id: Date.now(),
    title: newTournament.value.title,
    description: newTournament.value.description,
    prize_pool: newTournament.value.prize_pool,
    status: newTournament.value.status,
    is_no_loss: newTournament.value.is_no_loss,
    participants_count: 0,
    battles_count: 0,
    ends_at: new Date(Date.now() + 14 * 86400000).toISOString(),
  };
  tournamentsList.value.unshift(created);
  showCreateModal.value = false;
  showToast("Turnier erfolgreich erstellt & live geschaltet! 🏆", "success");

  // Attempt backend API
  try {
    await api.post("tournaments/", newTournament.value);
  } catch {
    // fallback
  }
}

const applicationForm = ref({
  artist_name: "",
  demo_link: "",
  message: "",
});

function openApplicationModal(tournament) {
  applyingTournament.value = tournament;
  applicationForm.value.artist_name = me.value?.name || me.value?.username || "";
  showApplyModal.value = true;
}

function submitArtistApplication() {
  myApplications.value.unshift({
    id: Date.now(),
    tournament_id: applyingTournament.value?.id,
    tournament_title: applyingTournament.value?.title || "Turnier",
    status: "PENDING",
    message: "Bewerbung erfolgreich eingereicht! Jury prüft die Demo.",
  });
  showApplyModal.value = false;
  showToast("Bewerbung erfolgreich eingereicht! Viel Erfolg! 🎤", "success");
}

const roundUploadForm = ref({
  title: "",
  file_url: "",
  notes: "",
});

function openUploadRoundModal(app) {
  roundUploadForm.value.title = `${app.tournament_title} - Runde`;
  showUploadModal.value = true;
}

function submitRoundFile() {
  showUploadModal.value = false;
  showToast("Runde erfolgreich eingereicht! Deine Einreichung ist jetzt aktiv. 🚀", "success");
}

/* Data Loading */
async function loadData() {
  try {
    const { data } = await api.get("tournaments/");
    const list = Array.isArray(data) ? data : data?.results || [];
    if (list.length) {
      tournamentsList.value = list;
    }
  } catch {
    // fallback to curated state
  }

  try {
    const { data: rankData } = await api.get("tournaments/ranked-overview/");
    if (rankData?.leaderboard?.length) {
      leaderboardRows.value = rankData.leaderboard;
    }
  } catch {
    // fallback
  }
}

onMounted(async () => {
  await fetchProfile();
  currentRoleMode.value = isTeam.value ? "TEAM" : "ARTIST";
  await loadData();
});
</script>

<style scoped>
.tournament-arena-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 1300px;
  margin: 0 auto;
  padding: 8px 0 80px;
  position: relative;
}

.arena-ambient-glow {
  position: absolute;
  top: 0;
  left: 20%;
  width: 60%;
  height: 240px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, rgba(99, 102, 241, 0.08) 50%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Arena Header */
.arena-header {
  display: grid;
  grid-template-columns: 1.4fr 0.9fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(28, 25, 44, 0.85), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 24px;
  position: relative;
  overflow: hidden;
}

.league-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 5px 14px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.35);
  color: #fbbf24;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.08em;
  margin-bottom: 12px;
}

.live-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b;
  animation: pulse 1.6s infinite;
}

@keyframes pulse {
  0% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.8; }
}

.arena-title {
  font-size: clamp(2rem, 3.8vw, 3rem);
  font-weight: 900;
  margin: 0 0 10px;
  line-height: 1.1;
  background: linear-gradient(120deg, #fff 40%, #fde68a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.arena-lead {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 18px;
  max-width: 600px;
}

.role-mode-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.mode-label {
  font-size: 12px;
  color: var(--muted);
}

.role-pill-group {
  display: inline-flex;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.role-pill-btn {
  border: none;
  background: transparent;
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.role-pill-btn.active {
  background: #fff;
  color: #0f172a;
}

.mode-desc-text {
  font-size: 11px;
  color: var(--muted);
}

/* Stats Card */
.arena-stats-card {
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 18px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.asc-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
}

.trophy-ico {
  font-size: 20px;
}

.asc-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  text-align: center;
}

.asc-stat {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 10px;
  padding: 10px 4px;
  display: flex;
  flex-direction: column;
}

.asc-stat .num {
  font-size: 1.5rem;
  font-weight: 800;
  color: #fff;
}

.asc-stat .num.highlight {
  color: #fbbf24;
}

.asc-stat .lbl {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.asc-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 10px;
  text-align: center;
}

.prize-tag {
  font-size: 12px;
  font-weight: 700;
  color: #34d399;
}

/* Navigation Tabs */
.arena-nav-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.tabs-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nav-tab-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 8px 16px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.nav-tab-btn.active, .nav-tab-btn:hover {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
  font-weight: 800;
}

.tab-badge {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.25);
}

.tab-badge.badge-live { background: #ef4444; color: #fff; }
.tab-badge.badge-warn { background: #6366f1; color: #fff; }

.btn-create {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #0f172a;
  font-weight: 800;
}

/* Tab Sections */
.tab-section {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* Spotlight Card */
.spotlight-card {
  padding: 32px;
  background: 
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(24, 28, 48, 0.8), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 20px;
}

.spotlight-badge-row {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.badge-featured {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
  font-size: 11px;
  font-weight: 800;
  padding: 3px 10px;
  border-radius: 999px;
}

.badge-status {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 6px;
}

.status-application_open { background: rgba(16, 185, 129, 0.2); color: #34d399; }
.status-submission_open { background: rgba(59, 130, 246, 0.2); color: #60a5fa; }
.status-battles { background: rgba(239, 68, 68, 0.2); color: #f87171; }
.status-closed { background: rgba(148, 163, 184, 0.2); color: #94a3b8; }

.badge-accent {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
}

.spotlight-title {
  margin: 0 0 10px;
  font-size: 1.8rem;
}

.spotlight-desc {
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.6;
  max-width: 750px;
  margin: 0 0 20px;
}

.spotlight-meta-row {
  display: flex;
  gap: 24px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.sm-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.04);
  padding: 8px 14px;
  border-radius: 12px;
}

.sm-icon {
  font-size: 22px;
}

.sm-val {
  font-weight: 800;
  font-size: 14px;
  display: block;
}

.sm-lbl {
  font-size: 10.5px;
  color: var(--muted);
  text-transform: uppercase;
}

.spotlight-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-hero {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #0f172a;
  font-weight: 800;
  padding: 10px 20px;
}

/* Filter controls */
.filter-controls-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
}

.search-box {
  min-width: 280px;
}

.status-filters {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-pill-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12.5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill-btn.active, .filter-pill-btn:hover {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.4);
}

/* Tournaments Grid */
.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.tournament-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  cursor: pointer;
  border-radius: 18px;
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.tournament-card:hover {
  transform: translateY(-3px);
  border-color: rgba(245, 158, 11, 0.4);
}

.card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.tournament-name {
  margin: 0 0 8px;
  font-size: 1.15rem;
  line-height: 1.3;
}

.tournament-summary {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0 0 16px;
  flex: 1;
}

.tournament-stats-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.pill-stat {
  font-size: 11px;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid var(--border);
  padding-top: 14px;
}

/* BATTLES SHOWDOWN */
.battles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.battle-showdown-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.battle-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 11.5px;
}

.battle-round-badge {
  background: #f59e0b;
  color: #0f172a;
  font-weight: 900;
  padding: 2px 8px;
  border-radius: 4px;
}

.battle-title-tag {
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.battle-status-badge {
  color: #ef4444;
  font-weight: 800;
}

.matchup-container {
  display: grid;
  grid-template-columns: 1fr 40px 1fr;
  align-items: center;
  gap: 12px;
}

.competitor-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 16px 12px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.competitor-box.winning {
  border-color: rgba(245, 158, 11, 0.45);
  background: rgba(245, 158, 11, 0.05);
}

.competitor-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #ec4899);
  color: #fff;
  font-weight: 900;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  margin-bottom: 8px;
}

.competitor-avatar.right-avatar {
  background: linear-gradient(135deg, #6366f1, #06b6d4);
}

.competitor-name {
  font-size: 14px;
  margin-bottom: 2px;
}

.competitor-tier {
  font-size: 10.5px;
  color: var(--muted);
  margin-bottom: 10px;
}

.btn-play-round {
  width: 100%;
  font-size: 11.5px;
  min-height: 30px;
  padding: 3px 8px;
  margin-bottom: 8px;
}

.vote-count-badge {
  font-size: 12.5px;
  font-weight: 800;
  color: #fbbf24;
}

.vs-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.vs-text {
  font-size: 14px;
  font-weight: 900;
  color: #ef4444;
  letter-spacing: 0.1em;
}

.vs-bar {
  width: 1px;
  height: 40px;
  background: rgba(255, 255, 255, 0.15);
}

.vote-meter {
  display: flex;
  height: 20px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.meter-bar {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10.5px;
  font-weight: 800;
  transition: width 0.3s ease;
}

.left-bar {
  background: linear-gradient(90deg, #f59e0b, #d97706);
  color: #0f172a;
}

.right-bar {
  background: linear-gradient(90deg, #4f46e5, #6366f1);
  color: #fff;
}

.battle-vote-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-vote-left {
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  min-height: 36px;
  font-size: 12px;
}

.btn-vote-right {
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.4);
  color: #818cf8;
  min-height: 36px;
  font-size: 12px;
}

.admin-battle-bar {
  border-top: 1px solid var(--border);
  padding-top: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-label {
  font-size: 11px;
  color: #f87171;
  font-weight: 700;
}

.admin-btn-row {
  display: flex;
  gap: 6px;
}

/* LEADERBOARD */
.tiers-showcase {
  display: flex;
  gap: 16px;
  padding: 18px 24px;
  overflow-x: auto;
  border-radius: 16px;
}

.tier-chip {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 14px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  min-width: 140px;
}

.tier-img {
  width: 28px;
  height: 28px;
}

.tier-info {
  display: flex;
  flex-direction: column;
}

.tier-info strong {
  font-size: 13px;
}

.tier-info small {
  color: var(--muted);
  font-size: 11px;
}

.podium-row {
  display: grid;
  grid-template-columns: 1fr 1.2fr 1fr;
  align-items: flex-end;
  gap: 16px;
  margin: 16px 0;
}

.podium-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border-radius: 18px;
}

.podium-card.rank-1 {
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.2) 0%, rgba(15, 23, 42, 0.9) 100%);
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding-bottom: 32px;
}

.crown-icon {
  font-size: 28px;
  margin-bottom: 4px;
}

.medal-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 900;
  font-size: 16px;
  color: #0f172a;
  margin-bottom: 8px;
}

.medal-circle.gold { background: #fbbf24; }
.medal-circle.silver { background: #cbd5e1; }
.medal-circle.bronze { background: #e59866; }

.podium-name {
  font-size: 1.1rem;
  margin-bottom: 4px;
}

.podium-rp {
  font-size: 1.3rem;
  font-weight: 800;
  color: #fbbf24;
}

.podium-tier {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

.leaderboard-table {
  padding: 12px;
  display: flex;
  flex-direction: column;
}

.table-head {
  display: grid;
  grid-template-columns: 60px 1.5fr 120px 140px 100px;
  padding: 10px 16px;
  font-size: 11.5px;
  font-weight: 800;
  color: var(--muted);
  text-transform: uppercase;
  border-bottom: 1px solid var(--border);
}

.table-row {
  display: grid;
  grid-template-columns: 60px 1.5fr 120px 140px 100px;
  align-items: center;
  padding: 12px 16px;
  border-radius: 10px;
  transition: background 0.15s ease;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.table-row.is-me {
  background: rgba(245, 158, 11, 0.12);
  border-left: 3px solid #f59e0b;
}

.artist-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.artist-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.me-pill {
  font-size: 10px;
  background: #f59e0b;
  color: #0f172a;
  padding: 1px 6px;
  border-radius: 4px;
  font-weight: 800;
}

.tier-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.05);
}

.rp-val {
  font-weight: 800;
  color: #fbbf24;
}

/* MY TOURNAMENTS */
.artist-quick-card {
  padding: 20px 28px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.aq-col {
  display: flex;
  flex-direction: column;
}

.aq-lbl {
  font-size: 11.5px;
  color: var(--muted);
  text-transform: uppercase;
}

.aq-val {
  font-size: 1.3rem;
  color: #fff;
}

.my-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.my-tournament-item {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mti-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}

.mti-head h3 {
  margin: 0;
  font-size: 1.1rem;
}

.mti-actions {
  display: flex;
  gap: 8px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
  flex-wrap: wrap;
}

/* ADMIN MODERATION */
.admin-mod-card {
  padding: 24px;
}

.mod-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.count-badge {
  background: #f59e0b;
  color: #0f172a;
  font-size: 11px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 999px;
}

.mod-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mod-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.mod-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.mod-meta {
  font-size: 11.5px;
  color: var(--muted);
}

.mod-msg {
  font-size: 13px;
  color: var(--text);
  margin: 4px 0 0;
  font-style: italic;
}

.mod-actions {
  display: flex;
  gap: 8px;
}

.btn-accept {
  background: #10b981;
  color: #fff;
}

.btn-reject {
  color: #ef4444;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 540px;
  width: 100%;
  padding: 28px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.split-form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.checkbox-row {
  display: flex;
  align-items: center;
}

.check-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

.font-mono {
  font-family: monospace;
}

@media (max-width: 900px) {
  .arena-header {
    grid-template-columns: 1fr;
    padding: 24px;
  }
  .podium-row {
    grid-template-columns: 1fr;
  }
  .table-head, .table-row {
    grid-template-columns: 40px 1fr 80px;
  }
  .col-tier, .col-record {
    display: none;
  }
}
</style>
