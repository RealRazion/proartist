<template>
  <div class="tournament-detail-page">
    <div class="ambient-glow"></div>

    <!-- Header & Navigation -->
    <header class="detail-header card">
      <div class="header-top">
        <button class="btn ghost btn-sm" @click="goBack">
          ← Zurück zur Turnier-Arena
        </button>
        <div class="top-status-pills">
          <span class="badge-status" :class="`status-${(tournament?.status || 'open').toLowerCase()}`">
            {{ statusLabel(tournament?.status) }}
          </span>
          <span v-if="tournament?.is_no_loss" class="badge-accent">🛡️ No Loss Bracket</span>
        </div>
      </div>

      <div class="hero-detail-body">
        <div class="hero-main">
          <span class="kicker">UNYQ TOURNAMENT // MATCH CIRCUIT</span>
          <h1>{{ tournament?.title || "Turnier Details" }}</h1>
          <p class="tournament-desc">{{ tournament?.description || "Kämpfe um Ruhm, Ranked Points und den Hauptgewinn." }}</p>

          <div class="stats-row">
            <div class="detail-stat">
              <span class="ds-icon">💰</span>
              <div>
                <strong>{{ tournament?.prize_pool || "1.000 € Cash" }}</strong>
                <small>Preispool</small>
              </div>
            </div>
            <div class="detail-stat">
              <span class="ds-icon">👥</span>
              <div>
                <strong>{{ participantsCount }} Artists</strong>
                <small>Teilnehmer</small>
              </div>
            </div>
            <div class="detail-stat">
              <span class="ds-icon">⚔️</span>
              <div>
                <strong>{{ battleRows.length }} Battles</strong>
                <small>Matches</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Action Box based on Status & Role -->
        <div class="hero-action-box card">
          <div v-if="tournament?.status === 'APPLICATION_OPEN'">
            <div class="phase-head">
              <span class="pulse-dot"></span>
              <strong>Bewerbungsphase Aktiv</strong>
            </div>
            <p class="muted small">Reiche deine Bewerbung mit Hörprobe ein, um dich für den Turnierbaum zu qualifizieren.</p>
            <button class="btn full-w" @click="showApplyModal = true">
              ✍️ Jetzt bewerben
            </button>
          </div>

          <div v-else-if="tournament?.status === 'SUBMISSION_OPEN'">
            <div class="phase-head">
              <span class="pulse-dot blue"></span>
              <strong>Einreichungsphase Läuft</strong>
            </div>
            <p class="muted small">Reiche deinen Track oder dein Video für die anstehende Runde ein.</p>
            <button class="btn full-w" @click="showUploadModal = true">
              📤 Runde einreichen (Audio/Video)
            </button>
          </div>

          <div v-else-if="tournament?.status === 'BATTLES'">
            <div class="phase-head">
              <span class="pulse-dot red"></span>
              <strong>Battles &amp; Voting Live!</strong>
            </div>
            <p class="muted small">Die Matches laufen. Höre die Runden an und stimme ab.</p>
            <button class="btn full-w btn-battles" @click="activeTab = 'battles'">
              ⚔️ Zu den Live Battles
            </button>
          </div>

          <div v-else>
            <div class="phase-head">
              <strong>Turnier Beendet</strong>
            </div>
            <p class="muted small">Dieses Turnier ist abgeschlossen. Ergebnisse und Sieger stehen fest.</p>
          </div>

          <!-- Admin Quick Status Changer -->
          <div v-if="isTeam" class="admin-phase-changer">
            <span class="admin-phase-lbl">👑 Admin Status ändern:</span>
            <div class="status-buttons">
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

    <!-- Sub-tabs Navigation -->
    <nav class="detail-tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span>{{ tab.label }}</span>
        <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
      </button>
    </nav>

    <!-- TAB 1: BATTLES & VOTING -->
    <section v-if="activeTab === 'battles'" class="detail-section">
      <div class="section-title-box">
        <h2>Live Battles &amp; Duelle ({{ battleRows.length }})</h2>
        <p class="muted">Höre beide Runden an und stimme für deinen Favoriten ab.</p>
      </div>

      <div class="battles-grid" v-if="battleRows.length">
        <div v-for="battle in battleRows" :key="battle.id" class="card battle-duel-card">
          <div class="bd-head">
            <span class="bd-round">RUNDE {{ battle.round_number || 1 }}</span>
            <span class="bd-status">{{ battle.status }}</span>
          </div>

          <div class="duel-showdown">
            <div class="duel-side left">
              <div class="avatar">{{ (battle.left_profile_name || 'A').charAt(0) }}</div>
              <strong>{{ battle.left_profile_name || 'Artist A' }}</strong>
              <button class="btn ghost btn-sm" @click="playRoundAudio(battle, 'left')">▶ Runde hören</button>
              <div class="votes-num">{{ battle.votes_left }} Votes</div>
            </div>

            <div class="vs-center">VS</div>

            <div class="duel-side right">
              <div class="avatar right-av">{{ (battle.right_profile_name || 'B').charAt(0) }}</div>
              <strong>{{ battle.right_profile_name || 'Artist B' }}</strong>
              <button class="btn ghost btn-sm" @click="playRoundAudio(battle, 'right')">▶ Runde hören</button>
              <div class="votes-num">{{ battle.votes_right }} Votes</div>
            </div>
          </div>

          <!-- Meter -->
          <div class="meter-bar-container">
            <div class="bar left" :style="{ width: getVotePct(battle, 'left') + '%' }">
              {{ getVotePct(battle, 'left') }}%
            </div>
            <div class="bar right" :style="{ width: getVotePct(battle, 'right') + '%' }">
              {{ getVotePct(battle, 'right') }}%
            </div>
          </div>

          <!-- Actions -->
          <div class="duel-vote-row" v-if="battle.status !== 'CLOSED'">
            <button class="btn btn-sm btn-left" @click="vote(battle, 'left')">
              Vote {{ battle.left_profile_name }}
            </button>
            <button class="btn btn-sm btn-right" @click="vote(battle, 'right')">
              Vote {{ battle.right_profile_name }}
            </button>
          </div>

          <!-- Admin resolution -->
          <div class="admin-resolve-row" v-if="isTeam && battle.status !== 'CLOSED'">
            <span class="admin-lbl">👑 Admin:</span>
            <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'left')">Left Win</button>
            <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'right')">Right Win</button>
            <button class="btn ghost btn-sm" @click="resolveBattle(battle, 'auto')">Auto Close</button>
          </div>
        </div>
      </div>
      <div v-else class="empty-card card muted">Keine Battles für dieses Turnier aktiv.</div>
    </section>

    <!-- TAB 2: TEILNEHMER & SUBMISSIONS -->
    <section v-if="activeTab === 'participants'" class="detail-section">
      <div class="two-column-grid">
        <!-- Submissions -->
        <div class="card panel-card">
          <div class="panel-head">
            <h3>Eingereichte Runden ({{ submissionRows.length }})</h3>
          </div>
          <div class="submissions-list" v-if="submissionRows.length">
            <div v-for="sub in submissionRows" :key="sub.id" class="sub-item">
              <div class="sub-left">
                <span class="sub-icon">🎵</span>
                <div>
                  <strong>{{ sub.title }}</strong>
                  <span class="sub-artist">von {{ sub.profile_name || 'Artist' }}</span>
                </div>
              </div>
              <button class="btn ghost btn-sm" @click="playRoundAudio(sub, 'round')">
                ▶ Anhören
              </button>
            </div>
          </div>
          <div v-else class="empty muted">Noch keine Runden eingereicht.</div>
        </div>

        <!-- Applications -->
        <div class="card panel-card">
          <div class="panel-head">
            <h3>Bewerbungen ({{ applicationRows.length }})</h3>
          </div>
          <div class="applications-list" v-if="applicationRows.length">
            <div v-for="app in applicationRows" :key="app.id" class="app-item">
              <div class="app-info">
                <strong>{{ app.profile_name || app.artist_name || 'Artist' }}</strong>
                <p class="muted small">{{ app.message || 'Bewerbung eingereicht.' }}</p>
              </div>
              <span class="badge-status" :class="app.status.toLowerCase()">{{ app.status }}</span>
            </div>
          </div>
          <div v-else class="empty muted">Noch keine Bewerbungen.</div>
        </div>
      </div>
    </section>

    <!-- TAB 3: REGELN & DETAILS -->
    <section v-if="activeTab === 'rules'" class="detail-section">
      <div class="card rules-card">
        <h3>Offizielle Turnier-Regeln &amp; Kriterien</h3>
        <ul class="rules-list">
          <li><strong>Originalität:</strong> Alle eingereichten Runden müssen selbst verfasst und produziert sein.</li>
          <li><strong>Fristen:</strong> Runden müssen innerhalb des Einreichungs-Fensters vollständig hochgeladen werden.</li>
          <li><strong>Voting:</strong> Die Community stimmt in der Battle-Phase 48 Stunden lang live ab.</li>
          <li><strong>Fair Play:</strong> Manipulierte Votes führen zur sofortigen Disqualifikation.</li>
        </ul>
      </div>
    </section>

    <!-- Modal Apply -->
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
            <button class="btn" type="submit">Bewerbung abschicken 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal Upload Round -->
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
    votes_left: 45,
    right_profile_name: "808_Phantom",
    votes_right: 38,
  },
  {
    id: 2,
    round_number: 1,
    status: "OPEN",
    left_profile_name: "KAZA",
    votes_left: 72,
    right_profile_name: "Aura_Vox",
    votes_right: 68,
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

const participantsCount = computed(() => {
  return applicationRows.value.length;
});

const tabs = computed(() => [
  { key: "battles", label: "⚔️ Battles & Voting", count: battleRows.value.length },
  { key: "participants", label: "👥 Teilnehmer & Runden", count: submissionRows.value.length },
  { key: "rules", label: "📜 Regeln & Kriterien" },
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
  showToast(`Vote gezählt! 🗳️`, "success");
}

function playRoundAudio(battle, side) {
  showToast(`Spiele Runde ab 🎵`, "info");
}

function resolveBattle(battle, side) {
  battle.status = "CLOSED";
  showToast(`Battle geschlossen! 🏆`, "success");
}

function updateTournamentStatus(newStatus) {
  if (tournament.value) {
    tournament.value.status = newStatus;
  }
  showToast(`Status auf "${statusLabel(newStatus)}" aktualisiert! ⚡`, "success");
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

async function loadTournament() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournaments/${id}/`);
    tournament.value = data;
  } catch {
    tournament.value = {
      id,
      title: "UNYQ Beat Battle Season 1 // 808 Showcase",
      description: "Der ultimative Beatmaking-Wettbewerb im UNYQ Circuit.",
      status: "BATTLES",
      prize_pool: "1.500 € Cash + Studio Gear",
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
  gap: 24px;
  max-width: 1240px;
  margin: 0 auto;
  padding: 8px 0 80px;
  position: relative;
}

.ambient-glow {
  position: absolute;
  top: 0;
  left: 20%;
  width: 60%;
  height: 240px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

/* Header */
.detail-header {
  padding: 32px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(28, 25, 44, 0.85), rgba(15, 23, 42, 0.95));
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 24px;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.top-status-pills {
  display: flex;
  gap: 8px;
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

.hero-detail-body {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 32px;
  align-items: center;
}

.kicker {
  font-size: 11px;
  letter-spacing: 0.1em;
  color: #fbbf24;
  font-weight: 800;
}

.hero-main h1 {
  font-size: clamp(1.8rem, 3.2vw, 2.6rem);
  font-weight: 900;
  margin: 6px 0 10px;
  line-height: 1.15;
}

.tournament-desc {
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.stats-row {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.detail-stat {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.04);
  padding: 8px 14px;
  border-radius: 12px;
}

.ds-icon {
  font-size: 22px;
}

.detail-stat strong {
  display: block;
  font-size: 14px;
}

.detail-stat small {
  color: var(--muted);
  font-size: 10.5px;
  text-transform: uppercase;
}

/* Action box */
.hero-action-box {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 16px;
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.phase-head {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13.5px;
  margin-bottom: 4px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  box-shadow: 0 0 8px #10b981;
}

.pulse-dot.blue { background: #3b82f6; box-shadow: 0 0 8px #3b82f6; }
.pulse-dot.red { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

.full-w {
  width: 100%;
}

.btn-battles {
  background: linear-gradient(135deg, #ef4444, #f59e0b);
  color: #fff;
  font-weight: 800;
}

.admin-phase-changer {
  border-top: 1px solid var(--border);
  padding-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.admin-phase-lbl {
  font-size: 11px;
  color: #f87171;
  font-weight: 700;
}

.status-buttons {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.btn-micro {
  padding: 3px 8px;
  font-size: 10.5px;
}

.btn-micro.active {
  background: #f59e0b;
  color: #0f172a;
}

/* Tabs */
.detail-tabs {
  display: flex;
  gap: 8px;
}

.tab-btn {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 8px 18px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
}

.tab-btn.active, .tab-btn:hover {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
  font-weight: 800;
}

.tab-count {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.25);
}

/* Detail sections */
.detail-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.battles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.battle-duel-card {
  padding: 22px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  border-radius: 18px;
}

.bd-head {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
}

.bd-round {
  background: #f59e0b;
  color: #0f172a;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 4px;
}

.duel-showdown {
  display: grid;
  grid-template-columns: 1fr 30px 1fr;
  align-items: center;
  gap: 10px;
}

.duel-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 12px 8px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 12px;
}

.duel-side .avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #f59e0b;
  color: #0f172a;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 6px;
}

.duel-side .right-av {
  background: #6366f1;
  color: #fff;
}

.duel-side strong {
  font-size: 13.5px;
  margin-bottom: 8px;
}

.votes-num {
  font-size: 12px;
  font-weight: 800;
  color: #fbbf24;
  margin-top: 6px;
}

.vs-center {
  font-weight: 900;
  color: #ef4444;
  text-align: center;
}

.meter-bar-container {
  display: flex;
  height: 18px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.3);
}

.bar {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 10.5px;
  font-weight: 800;
}

.bar.left { background: #f59e0b; color: #0f172a; }
.bar.right { background: #6366f1; color: #fff; }

.duel-vote-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.btn-left { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
.btn-right { background: rgba(99, 102, 241, 0.2); color: #818cf8; }

.admin-resolve-row {
  border-top: 1px solid var(--border);
  padding-top: 8px;
  display: flex;
  gap: 6px;
  align-items: center;
}

.admin-lbl {
  font-size: 10.5px;
  color: #f87171;
  font-weight: 700;
}

/* Two column */
.two-column-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.panel-card {
  padding: 24px;
}

.submissions-list, .applications-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 14px;
}

.sub-item, .app-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  border: 1px solid var(--border);
}

.sub-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.sub-artist {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
}

/* Rules */
.rules-card {
  padding: 28px;
}

.rules-list {
  padding-left: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  font-size: 14px;
  color: var(--muted);
}

.rules-list strong {
  color: var(--text);
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
  max-width: 500px;
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

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .hero-detail-body {
    grid-template-columns: 1fr;
  }
  .two-column-grid {
    grid-template-columns: 1fr;
  }
}
</style>
