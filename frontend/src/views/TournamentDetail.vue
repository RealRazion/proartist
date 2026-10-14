<template>
  <div class="tournament-detail-page">
    <!-- Ambient Cyber Glow -->
    <div class="ambient-glow"></div>

    <!-- HEADER: HERO BANNER -->
    <header class="detail-header card">
      <div class="header-top-row">
        <button class="btn ghost btn-sm btn-back-arena" @click="goBack">
          ← Zurück zur Contest-Arena
        </button>
        <div class="top-status-pills">
          <span class="badge-status-pill" :class="`status-${(tournament?.status || 'open').toLowerCase()}`">
            {{ statusLabel(tournament?.status) }}
          </span>
          <span v-if="tournament?.is_no_loss" class="badge-no-loss">
            🛡️ No Loss Bracket
          </span>
          <span class="badge-genre-tag">{{ tournament?.genre || 'Trap & 808' }}</span>
        </div>
      </div>

      <div class="hero-detail-grid">
        <div class="hero-main-info">
          <div class="kicker-league">
            <span class="live-dot"></span>
            <span>UNYQ CIRCUIT // TOURNAMENT DETAIL</span>
          </div>
          <h1 class="tournament-title">{{ tournament?.title || "UNYQ Beat Battle Season 1" }}</h1>
          <p class="tournament-description">
            {{ tournament?.description || "Der ultimative Battle-Wettbewerb. Kämpfe um Ruhm, Ranked Points und den Hauptgewinn." }}
          </p>

          <div class="stats-ribbon">
            <div class="sr-item">
              <span class="sr-icon">💰</span>
              <div>
                <strong class="sr-val">{{ tournament?.prize_pool || "2.500 € Cash + Studio Gear" }}</strong>
                <span class="sr-lbl">Preispool Gesamt</span>
              </div>
            </div>
            <div class="sr-item">
              <span class="sr-icon">👥</span>
              <div>
                <strong class="sr-val">{{ participantsCount }} Artists</strong>
                <span class="sr-lbl">Teilnehmer</span>
              </div>
            </div>
            <div class="sr-item">
              <span class="sr-icon">⚔️</span>
              <div>
                <strong class="sr-val">{{ battleRows.length }} Duelle</strong>
                <span class="sr-lbl">Aktive Battles</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Status & Action Box -->
        <div class="card hero-phase-action-box">
          <div v-if="tournament?.status === 'APPLICATION_OPEN'">
            <div class="phase-indicator">
              <span class="pulse-dot green"></span>
              <strong>Bewerbungsphase Aktiv</strong>
            </div>
            <p class="muted small">Reiche jetzt deine Hörprobe ein, um dich für den Turnierbaum zu qualifizieren.</p>
            <button class="btn full-w btn-action-hero" @click="showApplyModal = true">
              ✍️ Jetzt als Artist bewerben
            </button>
          </div>

          <div v-else-if="tournament?.status === 'SUBMISSION_OPEN'">
            <div class="phase-indicator">
              <span class="pulse-dot blue"></span>
              <strong>Einreichungsphase Läuft</strong>
            </div>
            <p class="muted small">Lade deinen Track oder dein Video für die anstehende Runde hoch.</p>
            <button class="btn full-w btn-action-hero" @click="showUploadModal = true">
              📤 Runde einreichen (Audio/Video)
            </button>
          </div>

          <div v-else-if="tournament?.status === 'BATTLES'">
            <div class="phase-indicator">
              <span class="pulse-dot red"></span>
              <strong>Battles &amp; Voting Live!</strong>
            </div>
            <p class="muted small">Die Duelle laufen. Höre beide Runden und vote für deinen Favoriten.</p>
            <button class="btn full-w btn-action-hero" @click="activeTab = 'battles'">
              ⚔️ Zu den Live Battles
            </button>
          </div>

          <div v-else>
            <div class="phase-indicator">
              <strong>Turnier Abgeschlossen</strong>
            </div>
            <p class="muted small">Ergebnisse und Gewinner stehen fest.</p>
          </div>

          <!-- Admin Quick Status Changer -->
          <div v-if="isTeam" class="admin-phase-stepper">
            <span class="admin-phase-lbl">👑 Admin Phase wechseln:</span>
            <div class="stepper-buttons">
              <button
                v-for="st in statusSteps"
                :key="st.value"
                class="btn ghost btn-micro"
                :class="{ active: tournament?.status === st.value }"
                @click="updateTournamentStatus(st.value)"
              >
                {{ st.label }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- DETAIL NAVIGATION TABS -->
    <nav class="detail-navigation-bar card">
      <div class="tabs-scroll">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span>{{ tab.label }}</span>
          <span v-if="tab.count !== undefined" class="tab-count-pill">{{ tab.count }}</span>
        </button>
      </div>
    </nav>

    <!-- ================================================================= -->
    <!-- TAB 1: BATTLES & VOTING SHOWDOWN -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'battles'" class="detail-tab-section">
      <div class="section-heading-bar">
        <h2>⚔️ Aktive Duelle &amp; Voting ({{ battleRows.length }})</h2>
        <p class="muted">Höre beide Runden an und stimme für den besseren Artist ab.</p>
      </div>

      <div class="battles-deck-grid" v-if="battleRows.length">
        <div v-for="b in battleRows" :key="b.id" class="card duel-card">
          <div class="dc-top">
            <span class="dc-round">RUNDE {{ b.round_number || 1 }}</span>
            <span class="dc-status">{{ b.status === 'OPEN' ? '🔥 Voting Live' : 'Beendet' }}</span>
          </div>

          <div class="dc-showdown">
            <!-- Left Side -->
            <div class="dc-side left" :class="{ winner: b.winner === 'left' }">
              <div class="dc-avatar">{{ (b.left_profile_name || 'A').charAt(0) }}</div>
              <strong class="dc-name">{{ b.left_profile_name }}</strong>
              <button class="btn ghost btn-sm btn-play" @click="playAudio(b.left_profile_name)">
                ▶ Runde hören
              </button>
              <div class="dc-votes">{{ b.votes_left }} Votes</div>
            </div>

            <div class="dc-vs">VS</div>

            <!-- Right Side -->
            <div class="dc-side right" :class="{ winner: b.winner === 'right' }">
              <div class="dc-avatar right-av">{{ (b.right_profile_name || 'B').charAt(0) }}</div>
              <strong class="dc-name">{{ b.right_profile_name }}</strong>
              <button class="btn ghost btn-sm btn-play" @click="playAudio(b.right_profile_name)">
                ▶ Runde hören
              </button>
              <div class="dc-votes">{{ b.votes_right }} Votes</div>
            </div>
          </div>

          <!-- Vote Bar -->
          <div class="dc-meter">
            <div class="dc-bar-left" :style="{ width: getVotePct(b, 'left') + '%' }">
              {{ getVotePct(b, 'left') }}%
            </div>
            <div class="dc-bar-right" :style="{ width: getVotePct(b, 'right') + '%' }">
              {{ getVotePct(b, 'right') }}%
            </div>
          </div>

          <!-- Vote Actions -->
          <div class="dc-actions" v-if="b.status !== 'CLOSED'">
            <button class="btn btn-sm btn-vote-l" @click="vote(b, 'left')">
              Vote {{ b.left_profile_name }}
            </button>
            <button class="btn btn-sm btn-vote-r" @click="vote(b, 'right')">
              Vote {{ b.right_profile_name }}
            </button>
          </div>

          <!-- Admin Resolution -->
          <div class="dc-admin-row" v-if="isTeam && b.status !== 'CLOSED'">
            <span class="admin-lbl">👑 Admin Urteil:</span>
            <button class="btn ghost btn-micro" @click="resolveBattle(b, 'left')">Left Win</button>
            <button class="btn ghost btn-micro" @click="resolveBattle(b, 'right')">Right Win</button>
            <button class="btn ghost btn-micro" @click="resolveBattle(b, 'auto')">Auto Close</button>
          </div>
        </div>
      </div>
      <div v-else class="card empty-state-box muted">Keine aktiven Battles für dieses Turnier.</div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 2: INTERAKTIVER TURNIERBAUM (BRACKET TREE) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'bracket'" class="detail-tab-section">
      <div class="section-heading-bar">
        <h2>🌳 Interaktiver Turnierbaum (Bracket)</h2>
        <p class="muted">Klicke auf ein Match, um die Runden anzuhören und Details zu sehen.</p>
      </div>

      <div class="card bracket-visual-board">
        <div class="bracket-rounds-container">
          <!-- Column 1: Viertelfinale (Quarterfinals) -->
          <div class="bracket-column">
            <h3 class="b-col-title">Viertelfinale</h3>
            <div class="bracket-matches-list">
              <div
                v-for="m in bracketData.quarterFinals"
                :key="m.id"
                class="bracket-match-node"
                :class="{ completed: m.winner }"
                @click="inspectMatch(m)"
              >
                <div class="b-slot" :class="{ winner: m.winner === m.artistA }">
                  <span class="b-name">{{ m.artistA }}</span>
                  <span class="b-score">{{ m.scoreA }}</span>
                </div>
                <div class="b-slot" :class="{ winner: m.winner === m.artistB }">
                  <span class="b-name">{{ m.artistB }}</span>
                  <span class="b-score">{{ m.scoreB }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Halbfinale (Semifinals) -->
          <div class="bracket-column">
            <h3 class="b-col-title">Halbfinale</h3>
            <div class="bracket-matches-list semi-list">
              <div
                v-for="m in bracketData.semiFinals"
                :key="m.id"
                class="bracket-match-node"
                :class="{ completed: m.winner }"
                @click="inspectMatch(m)"
              >
                <div class="b-slot" :class="{ winner: m.winner === m.artistA }">
                  <span class="b-name">{{ m.artistA }}</span>
                  <span class="b-score">{{ m.scoreA }}</span>
                </div>
                <div class="b-slot" :class="{ winner: m.winner === m.artistB }">
                  <span class="b-name">{{ m.artistB }}</span>
                  <span class="b-score">{{ m.scoreB }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 3: Grand Final -->
          <div class="bracket-column">
            <h3 class="b-col-title final-title">👑 Grand Final</h3>
            <div class="bracket-matches-list final-list">
              <div
                class="bracket-match-node grand-final-node"
                @click="inspectMatch(bracketData.grandFinal)"
              >
                <div class="b-slot" :class="{ winner: bracketData.grandFinal.winner === bracketData.grandFinal.artistA }">
                  <span class="b-name">{{ bracketData.grandFinal.artistA }}</span>
                  <span class="b-score">{{ bracketData.grandFinal.scoreA }}</span>
                </div>
                <div class="b-slot" :class="{ winner: bracketData.grandFinal.winner === bracketData.grandFinal.artistB }">
                  <span class="b-name">{{ bracketData.grandFinal.artistB }}</span>
                  <span class="b-score">{{ bracketData.grandFinal.scoreB }}</span>
                </div>
              </div>

              <!-- Champion Trophy Box -->
              <div class="champion-crown-podium card">
                <span class="trophy-symbol">🏆</span>
                <strong>{{ bracketData.grandFinal.winner || 'Finale läuft' }}</strong>
                <small class="champ-sub">UNYQ Season Champion</small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 3: TEILNEHMER & SUBMISSIONS -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'participants'" class="detail-tab-section">
      <div class="two-column-layout">
        <!-- Submissions -->
        <div class="card panel-box">
          <div class="pb-header">
            <h3>Eingereichte Runden ({{ submissionRows.length }})</h3>
            <button class="btn btn-sm" @click="showUploadModal = true">+ Runde einreichen</button>
          </div>

          <div class="submissions-list" v-if="submissionRows.length">
            <div v-for="sub in submissionRows" :key="sub.id" class="sub-item-card">
              <div class="sub-info">
                <span class="sub-icon">🎵</span>
                <div>
                  <strong>{{ sub.title }}</strong>
                  <span class="sub-artist">von {{ sub.profile_name }}</span>
                </div>
              </div>
              <button class="btn ghost btn-sm" @click="playAudio(sub.profile_name)">
                ▶ Anhören
              </button>
            </div>
          </div>
          <div v-else class="empty-muted-box muted">Noch keine Runden eingereicht.</div>
        </div>

        <!-- Applications -->
        <div class="card panel-box">
          <div class="pb-header">
            <h3>Bewerbungen ({{ applicationRows.length }})</h3>
            <button class="btn ghost btn-sm" @click="showApplyModal = true">+ Bewerben</button>
          </div>

          <div class="applications-list" v-if="applicationRows.length">
            <div v-for="app in applicationRows" :key="app.id" class="app-item-card">
              <div class="app-info">
                <strong>{{ app.profile_name }}</strong>
                <p class="muted small">{{ app.message }}</p>
              </div>
              <span class="badge-status-pill" :class="app.status.toLowerCase()">{{ app.status }}</span>
            </div>
          </div>
          <div v-else class="empty-muted-box muted">Noch keine Bewerbungen.</div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 4: REGELN & PREISPOOL -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'rules'" class="detail-tab-section">
      <div class="rules-grid-layout">
        <div class="card rules-card">
          <h3>Offizielle Turnier-Regeln &amp; Kriterien</h3>
          <ul class="rules-bullet-list">
            <li>
              <strong>Originalität &amp; Copyright:</strong>
              Alle eingereichten Runden müssen selbst komponiert, produziert oder eingesungen sein.
            </li>
            <li>
              <strong>Fristen &amp; Uploads:</strong>
              Runden müssen bis zur jeweiligen Runden-Deadline vollständig hochgeladen werden.
            </li>
            <li>
              <strong>48-Stunden Community Voting:</strong>
              Die Community stimmt in jedem Battle live ab. Verifizierte User erhalten Stimmgewicht.
            </li>
            <li>
              <strong>Anti-Cheat &amp; Fair Play:</strong>
              Manipulierte Votes oder Botting führen zur sofortigen Disqualifikation.
            </li>
          </ul>
        </div>

        <div class="card prize-pool-card">
          <h3>Preispool Aufteilung</h3>
          <div class="prize-tiers-list">
            <div class="pt-item gold">
              <span class="pt-rank">1. Platz (Champion)</span>
              <strong class="pt-val">1.500 € Cash + Vinyl Pressung + Studio Monitor Set</strong>
            </div>
            <div class="pt-item silver">
              <span class="pt-rank">2. Platz (Runner-Up)</span>
              <strong class="pt-val">600 € Cash + UNYQ Sample Pack Bundle</strong>
            </div>
            <div class="pt-item bronze">
              <span class="pt-rank">3. Platz</span>
              <strong class="pt-val">400 € Cash + VIP Producer Pass</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- MODAL 1: APPLY -->
    <div v-if="showApplyModal" class="modal-overlay" @click.self="showApplyModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung für "{{ tournament?.title }}"</h3>
          <button class="btn ghost tiny" @click="showApplyModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitApply">
          <label>
            <span>Artist-Name *</span>
            <input v-model.trim="applyArtistName" class="input" required />
          </label>
          <label>
            <span>Demo- / Track-Link *</span>
            <input v-model.trim="applyDemoLink" class="input" required placeholder="https://soundcloud.com/..." />
          </label>
          <label>
            <span>Nachricht an die Jury</span>
            <textarea v-model.trim="applyMessage" class="input" rows="3" placeholder="Deine Motivation..."></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showApplyModal = false">Abbrechen</button>
            <button class="btn" type="submit">Bewerbung abschicken 🎤</button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL 2: UPLOAD ROUND -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Runde einreichen</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitRound">
          <label>
            <span>Track-Titel für diese Runde *</span>
            <input v-model.trim="uploadRoundTitle" class="input" required placeholder="z. B. Runde 1 - Focus &amp; Flow" />
          </label>
          <label>
            <span>Audio- oder Video-Link (SoundCloud, Drive, YouTube) *</span>
            <input v-model.trim="uploadMediaUrl" class="input" required placeholder="https://..." />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showUploadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Runde einreichen 🚀</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import api from "../api";

const route = useRoute();
const router = useRouter();
const { profile: me, isTeam } = useCurrentProfile();
const { showToast } = useToast();

const tournament = ref(null);
const activeTab = ref("battles");

const battleRows = ref([
  {
    id: 1,
    round_number: 1,
    status: "OPEN",
    left_profile_name: "Neo_Producer",
    votes_left: 64,
    right_profile_name: "808_Phantom",
    votes_right: 48,
  },
  {
    id: 2,
    round_number: 1,
    status: "OPEN",
    left_profile_name: "KAZA",
    votes_left: 92,
    right_profile_name: "Aura_Vox",
    votes_right: 88,
  },
]);

const submissionRows = ref([
  { id: 1, title: "Dark Drill Pressure", profile_name: "Neo_Producer" },
  { id: 2, title: "Subzero Late Night", profile_name: "808_Phantom" },
  { id: 3, title: "Golden Glow", profile_name: "KAZA" },
  { id: 4, title: "Soulful Rain", profile_name: "Aura_Vox" },
]);

const applicationRows = ref([
  { id: 1, profile_name: "Neo_Producer", status: "ACCEPTED", message: "Bereit für Runde 1." },
  { id: 2, profile_name: "808_Phantom", status: "ACCEPTED", message: "808s sind gestimmt." },
  { id: 3, profile_name: "KAZA", status: "ACCEPTED", message: "Flow sitzt." },
  { id: 4, profile_name: "Aura_Vox", status: "ACCEPTED", message: "Vocals aufgenommen." },
]);

/* Bracket Tree Structure */
const bracketData = ref({
  quarterFinals: [
    { id: 1, artistA: "Neo_Producer", scoreA: "84", artistB: "808_Phantom", scoreB: "68", winner: "Neo_Producer" },
    { id: 2, artistA: "Mika_LoFi", scoreA: "42", artistB: "Cyber_Pulse", scoreB: "76", winner: "Cyber_Pulse" },
    { id: 3, artistA: "KAZA", scoreA: "112", artistB: "Aura_Vox", scoreB: "98", winner: "KAZA" },
    { id: 4, artistA: "DrillKing_030", scoreA: "56", artistB: "Sarah_Soul", scoreB: "89", winner: "Sarah_Soul" },
  ],
  semiFinals: [
    { id: 5, artistA: "Neo_Producer", scoreA: "95", artistB: "Cyber_Pulse", scoreB: "78", winner: "Neo_Producer" },
    { id: 6, artistA: "KAZA", scoreA: "108", artistB: "Sarah_Soul", scoreB: "92", winner: "KAZA" },
  ],
  grandFinal: {
    id: 7,
    artistA: "Neo_Producer",
    scoreA: "128",
    artistB: "KAZA",
    scoreB: "135",
    winner: "KAZA",
  },
});

const participantsCount = computed(() => applicationRows.value.length);

const tabs = computed(() => [
  { key: "battles", label: "⚔️ Battles & Voting", count: battleRows.value.length },
  { key: "bracket", label: "🌳 Turnierbaum" },
  { key: "participants", label: "👥 Teilnehmer & Runden", count: submissionRows.value.length },
  { key: "rules", label: "📜 Regeln & Preispool" },
]);

const statusSteps = [
  { value: "APPLICATION_OPEN", label: "Bewerbung offen" },
  { value: "SUBMISSION_OPEN", label: "Einreichung offen" },
  { value: "BATTLES", label: "Battles live" },
  { value: "CLOSED", label: "Beendet" },
];

const showApplyModal = ref(false);
const applyArtistName = ref("");
const applyDemoLink = ref("");
const applyMessage = ref("");

const showUploadModal = ref(false);
const uploadRoundTitle = ref("");
const uploadMediaUrl = ref("");

function statusLabel(status) {
  const map = {
    APPLICATION_OPEN: "🟢 Bewerbung offen",
    SUBMISSION_OPEN: "🔵 Einreichung offen",
    BATTLES: "🔴 Battles live",
    CLOSED: "⚪ Beendet",
  };
  return map[status] || status || "Live";
}

function goBack() {
  router.push({ name: "platform-contests" });
}

function getVotePct(battle, side) {
  const total = (battle.votes_left || 0) + (battle.votes_right || 0);
  if (!total) return 50;
  const count = side === "left" ? battle.votes_left : battle.votes_right;
  return Math.round((count / total) * 100);
}

function vote(battle, side) {
  if (side === "left") {
    battle.votes_left++;
  } else {
    battle.votes_right++;
  }
  showToast(`Vote gezählt für ${side === 'left' ? battle.left_profile_name : battle.right_profile_name}! +10 RP ⚡`, "success");
}

function playAudio(artist) {
  showToast(`▶ Spiele Runde von ${artist} (Studio Stream)`, "info");
}

function resolveBattle(battle, resolution) {
  battle.status = "CLOSED";
  if (resolution === "left") battle.winner = "left";
  else if (resolution === "right") battle.winner = "right";
  else battle.winner = battle.votes_left >= battle.votes_right ? "left" : "right";
  showToast(`Battle geschlossen! 🏆`, "success");
}

function updateTournamentStatus(newStatus) {
  if (tournament.value) {
    tournament.value.status = newStatus;
  }
  showToast(`Status auf "${statusLabel(newStatus)}" gesetzt! ⚡`, "success");
}

function submitApply() {
  applicationRows.value.push({
    id: Date.now(),
    profile_name: applyArtistName.value,
    status: "PENDING",
    message: applyMessage.value,
  });
  showApplyModal.value = false;
  showToast("Bewerbung erfolgreich eingereicht! 🎤", "success");
}

function submitRound() {
  submissionRows.value.push({
    id: Date.now(),
    title: uploadRoundTitle.value,
    profile_name: me.value?.name || "Du",
  });
  showUploadModal.value = false;
  showToast("Runde erfolgreich eingereicht! 🚀", "success");
}

function inspectMatch(match) {
  showToast(`Match: ${match.artistA} vs ${match.artistB} ausgewählt`, "info");
}

async function loadTournament() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournaments/${id}/`);
    tournament.value = data;
  } catch {
    tournament.value = {
      id,
      title: "UNYQ Beat Battle Season 1 // 808 Showcase",
      description: "Der ultimative Beatmaking-Wettbewerb im UNYQ Circuit. Produziere den härtesten Trap/Drill Track.",
      status: "BATTLES",
      genre: "Trap & 808",
      prize_pool: "2.500 € Cash + Studio Gear",
      is_no_loss: true,
    };
  }
}

onMounted(() => {
  applyArtistName.value = me.value?.name || me.value?.username || "";
  loadTournament();
});
</script>

<style scoped>
.tournament-detail-page {
  display: flex;
  flex-direction: column;
  gap: 26px;
  max-width: 1320px;
  margin: 0 auto;
  padding: 8px 16px 90px;
  position: relative;
}

.ambient-glow {
  position: absolute;
  top: 0;
  left: 15%;
  width: 70%;
  height: 340px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, rgba(59, 130, 246, 0.1) 45%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Header */
.detail-header {
  padding: 34px 32px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.18), transparent 50%),
    linear-gradient(135deg, rgba(28, 22, 45, 0.95), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 26px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  position: relative;
  z-index: 1;
}

.header-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-back-arena {
  font-weight: 700;
}

.top-status-pills {
  display: flex;
  gap: 8px;
}

.badge-status-pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.badge-status-pill.status-battles {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-no-loss {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}

.badge-genre-tag {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 999px;
}

.hero-detail-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 32px;
  align-items: center;
}

.kicker-league {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #fbbf24;
  margin-bottom: 8px;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
}

.tournament-title {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 900;
  color: #fff;
  margin: 0 0 10px;
  line-height: 1.15;
}

.tournament-description {
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.stats-ribbon {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.sr-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.04);
  padding: 10px 14px;
  border-radius: 12px;
}

.sr-icon {
  font-size: 20px;
}

.sr-val {
  display: block;
  font-size: 13.5px;
  font-weight: 800;
  color: #fff;
}

.sr-lbl {
  font-size: 11px;
  color: var(--muted);
}

.hero-phase-action-box {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 20px;
  padding: 24px;
}

.phase-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #fff;
  margin-bottom: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pulse-dot.green { background: #34d399; }
.pulse-dot.blue { background: #60a5fa; }
.pulse-dot.red { background: #f87171; }

.btn-action-hero {
  padding: 12px;
  font-weight: 800;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}

.admin-phase-stepper {
  margin-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

.admin-phase-lbl {
  font-size: 11.5px;
  color: #fbbf24;
  font-weight: 700;
}

.stepper-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 6px;
}

/* Nav */
.detail-navigation-bar {
  padding: 8px 12px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.tabs-scroll {
  display: flex;
  gap: 8px;
}

.nav-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-tab-btn.active {
  background: #fff;
  color: #0f172a;
}

.tab-count-pill {
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 999px;
  font-size: 10px;
}

/* TAB 1: BATTLES */
.battles-deck-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 20px;
}

.duel-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.dc-top {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 700;
}

.dc-round {
  color: #fbbf24;
}

.dc-status {
  color: #f87171;
}

.dc-showdown {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 16px;
}

.dc-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.dc-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
}

.dc-avatar.right-av {
  background: #a855f7;
}

.dc-name {
  font-size: 14px;
  color: #fff;
}

.dc-votes {
  font-size: 12px;
  color: var(--muted);
}

.dc-vs {
  font-size: 16px;
  font-weight: 900;
  color: #fbbf24;
}

.dc-meter {
  display: flex;
  height: 14px;
  border-radius: 999px;
  overflow: hidden;
  font-size: 9.5px;
  font-weight: 800;
  color: #fff;
}

.dc-bar-left {
  background: #3b82f6;
  display: flex;
  align-items: center;
  padding-left: 8px;
}

.dc-bar-right {
  background: #a855f7;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
}

.dc-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-vote-l {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.btn-vote-r {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.4);
}

.dc-admin-row {
  display: flex;
  gap: 6px;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 10px;
}

/* TAB 2: BRACKET */
.bracket-visual-board {
  padding: 32px 24px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow-x: auto;
}

.bracket-rounds-container {
  display: grid;
  grid-template-columns: repeat(3, minmax(240px, 1fr));
  gap: 36px;
}

.b-col-title {
  font-size: 14px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
  margin: 0 0 20px;
  text-align: center;
}

.b-col-title.final-title {
  color: #fbbf24;
}

.bracket-matches-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.semi-list {
  margin-top: 36px;
  gap: 72px;
}

.final-list {
  margin-top: 90px;
  gap: 24px;
}

.bracket-match-node {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bracket-match-node:hover {
  border-color: #38bdf8;
  transform: translateY(-2px);
}

.b-slot {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.b-slot:last-child {
  border-bottom: none;
}

.b-slot.winner {
  background: rgba(52, 211, 153, 0.12);
  color: #fff;
  font-weight: 700;
}

.b-slot.winner .b-score {
  color: #34d399;
  font-weight: 900;
}

.champion-crown-podium {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(15, 23, 42, 0.8));
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 16px;
  padding: 18px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.trophy-symbol {
  font-size: 32px;
}

.champ-sub {
  font-size: 11px;
  color: #fbbf24;
}

/* TAB 3: PARTICIPANTS */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.panel-box {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pb-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.pb-header h3 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.submissions-list,
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sub-item-card,
.app-item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px 14px;
}

.sub-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sub-icon {
  font-size: 20px;
}

.sub-artist {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
}

/* TAB 4: RULES */
.rules-grid-layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
}

.rules-card,
.prize-pool-card {
  padding: 28px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.rules-bullet-list {
  padding-left: 18px;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin: 16px 0 0;
  font-size: 14px;
  line-height: 1.5;
}

.prize-tiers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.pt-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 4px solid var(--muted);
}

.pt-item.gold {
  border-left-color: #fbbf24;
  background: rgba(245, 158, 11, 0.08);
}

.pt-item.silver {
  border-left-color: #cbd5e1;
}

.pt-item.bronze {
  border-left-color: #d97706;
}

.pt-rank {
  display: block;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 2px;
}

.pt-val {
  font-size: 13.5px;
  color: #fff;
}

/* MODALS */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 500px;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 22px;
  padding: 26px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
  color: #fff;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .hero-detail-grid {
    grid-template-columns: 1fr;
  }
  .two-column-layout,
  .rules-grid-layout {
    grid-template-columns: 1fr;
  }
}
</style>
