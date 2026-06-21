<template>
  <div class="detail-page">
    <div class="ambient"></div>

    <header class="detail-topbar">
      <div>
        <button class="btn ghost small" type="button" @click="goBack">Zur Arena</button>
        <p class="eyebrow">TOURNAMENT DETAIL</p>
        <h1>{{ tournament?.title || "Tournament" }}</h1>
      </div>
      <div class="top-actions">
        <span class="badge">{{ statusLabel(tournament?.status) }}</span>
        <button class="btn ghost small" type="button" @click="openProfile">Profil</button>
      </div>
    </header>

    <section class="hero" v-if="tournament">
      <div class="hero-cover" :style="{ backgroundImage: `url(${tournamentCover(tournament)})` }"></div>
      <div class="hero-info">
        <p>{{ tournament.description || "Dieses Turnier wartet auf starke Einreichungen." }}</p>
        <div class="hero-stats">
          <article>
            <strong>{{ participantsCount }}</strong>
            <span>Teilnehmer</span>
          </article>
          <article>
            <strong>{{ battleRows.length }}</strong>
            <span>Battles</span>
          </article>
          <article>
            <strong>{{ submissionRows.length }}</strong>
            <span>Submissions</span>
          </article>
        </div>
        <div class="hero-actions" v-if="tournament.status === 'APPLICATION_OPEN' && !viewerIsTeam">
          <textarea v-model.trim="applicationMessage" class="input" rows="2" placeholder="Kurze Bewerbung..." />
          <button class="btn" :disabled="busy" @click="submitApplication">Bewerben</button>
        </div>
      </div>
    </section>

    <nav class="subtabs">
      <button
        v-for="tab in detailTabs"
        :key="tab.key"
        class="subtab"
        :class="{ active: activeTab === tab.key }"
        @click="setTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </nav>

    <section class="panel" v-if="activeTab === 'overview'">
      <header class="section-head">
        <h2>Overview</h2>
      </header>

      <div class="two-col">
        <article class="card">
          <h3>Status Flow</h3>
          <div class="status-flow">
            <button v-for="step in statusSteps" :key="step.value" class="btn ghost small" :disabled="!viewerIsTeam || busy" @click="setTournamentStatus(step.value)">
              {{ step.label }}
            </button>
          </div>
          <p class="muted">Aktueller Status: {{ statusLabel(tournament?.status) }}</p>
        </article>

        <article class="card">
          <h3>Regeln Kompakt</h3>
          <ul class="rules">
            <li>Einreichungen nur in offenen Submission-Phasen.</li>
            <li>Votes sind nur in Battle-Phasen möglich.</li>
            <li>Admin kann Battles manuell schließen.</li>
          </ul>
        </article>
      </div>
    </section>

    <section class="panel" v-if="activeTab === 'battles'">
      <header class="section-head">
        <h2>Battles</h2>
      </header>
      <div class="battle-grid" v-if="battleRows.length">
        <article v-for="battle in battleRows" :key="`battle-${battle.id}`" class="battle-card">
          <div class="duel-head">
            <button class="link-btn" @click="openBattleProfileByName(battle.left_profile_name)">{{ battle.left_profile_name }}</button>
            <strong>{{ battle.votes_left }} : {{ battle.votes_right }}</strong>
            <button class="link-btn" @click="openBattleProfileByName(battle.right_profile_name)">{{ battle.right_profile_name }}</button>
          </div>
          <div class="duel-meta">
            <span>Runde {{ battle.round_number }}</span>
            <span class="badge">{{ battle.status }}</span>
          </div>
          <div class="duel-actions" v-if="!viewerIsTeam && tournament?.status === 'BATTLES' && battle.status !== 'CLOSED'">
            <button class="btn" :disabled="busy || !canVoteBattle(battle)" @click="voteBattle(battle, battle.left_submission)">Vote Left</button>
            <button class="btn ghost" :disabled="busy || !canVoteBattle(battle)" @click="voteBattle(battle, battle.right_submission)">Vote Right</button>
          </div>
          <div class="duel-actions" v-if="viewerIsTeam && battle.status !== 'CLOSED'">
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle)">Auto Close</button>
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.left_submission)">Left Win</button>
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.right_submission)">Right Win</button>
          </div>
        </article>
      </div>
      <div v-else class="empty">Keine Battles für dieses Turnier.</div>
    </section>

    <section class="panel" v-if="activeTab === 'participants'">
      <header class="section-head">
        <h2>Participants & Submissions</h2>
      </header>
      <div class="two-col">
        <article class="card">
          <h3>Applications</h3>
          <div class="list" v-if="applicationRows.length">
            <article class="row" v-for="app in applicationRows" :key="`app-${app.id}`">
              <div>
                <strong>{{ app.profile_name || app.profile?.name || 'Unknown' }}</strong>
                <p>{{ app.message || 'Keine Nachricht' }}</p>
              </div>
              <span class="badge">{{ app.status }}</span>
            </article>
          </div>
          <p class="muted" v-else>Keine Bewerbungen.</p>
        </article>

        <article class="card">
          <h3>Submission Upload</h3>
          <div class="upload-box" v-if="!viewerIsTeam && tournament?.status === 'SUBMISSION_OPEN'">
            <input v-model.trim="submissionTitle" class="input" placeholder="Track Titel" />
            <input v-model.trim="submissionMediaUrl" class="input" placeholder="Media URL (Audio/Video)" />
            <button class="btn" :disabled="busy" @click="submitRound">Einreichen</button>
          </div>
          <p class="muted" v-else>Upload ist nur in Submission-Phase verfügbar.</p>

          <div class="list" v-if="submissionRows.length">
            <article class="row" v-for="sub in submissionRows" :key="`sub-${sub.id}`">
              <div>
                <strong>{{ sub.title || 'Untitled' }}</strong>
                <p>{{ sub.profile_name || sub.profile?.name || 'Unknown' }}</p>
              </div>
              <a v-if="sub.media_url" class="link-btn" :href="sub.media_url" target="_blank" rel="noopener">Open</a>
            </article>
          </div>
        </article>
      </div>
    </section>

    <section class="panel" v-if="activeTab === 'rules'">
      <header class="section-head">
        <h2>Rules & Timing</h2>
      </header>
      <div class="two-col">
        <article class="card">
          <h3>Turnier-Flags</h3>
          <ul class="rules">
            <li>No Loss: {{ tournament?.is_no_loss ? 'Ja' : 'Nein' }}</li>
            <li>Recurring: {{ tournament?.is_recurring ? 'Ja' : 'Nein' }}</li>
            <li>Application Phase: {{ tournament?.has_application_phase ? 'Ja' : 'Nein' }}</li>
          </ul>
        </article>
        <article class="card">
          <h3>Zeitfenster</h3>
          <p class="muted">Start: {{ formatDate(tournament?.starts_at) }}</p>
          <p class="muted">Ende: {{ formatDate(tournament?.ends_at) }}</p>
        </article>
      </div>
    </section>

    <div v-if="selectedBattleProfile" class="modal-overlay" @click.self="selectedBattleProfile = null">
      <article class="modal-card">
        <header>
          <h2>{{ selectedBattleProfile.name }}</h2>
          <button class="btn ghost small" @click="selectedBattleProfile = null">✕</button>
        </header>
        <div class="modal-body">
          <p class="muted">Battle-Profil mit bisherigen Matches.</p>
          <div class="history" v-if="battleProfileHistory.length">
            <article v-for="battle in battleProfileHistory" :key="`hist-${battle.id}`" class="history-row">
              <strong>{{ battle.left_profile_name }} vs {{ battle.right_profile_name }}</strong>
              <span>R{{ battle.round_number }} · {{ battle.votes_left }}:{{ battle.votes_right }} · {{ battle.status }}</span>
            </article>
          </div>
          <p class="muted" v-else>Keine Battle-Historie.</p>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const router = useRouter();
const route = useRoute();
const { profile, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const detailTabs = [
  { key: "overview", label: "Overview" },
  { key: "battles", label: "Battles" },
  { key: "participants", label: "Participants" },
  { key: "rules", label: "Rules" },
];

const validTabs = detailTabs.map((t) => t.key);
const activeTab = ref("overview");
const busy = ref(false);
const tournament = ref(null);
const applications = ref([]);
const submissions = ref([]);
const battles = ref([]);
const myVotes = ref([]);
const rankedOverview = ref({});
const selectedBattleProfile = ref(null);
const applicationMessage = ref("");
const submissionTitle = ref("");
const submissionMediaUrl = ref("");

const tournamentId = computed(() => Number(route.params.tournamentId));
const artistPreview = computed(() => isTeam.value && String(route.query.artistView || "").toLowerCase() === "1");
const viewerIsTeam = computed(() => isTeam.value && !artistPreview.value);
const myProfileId = computed(() => profile.value?.id || null);

const statusSteps = [
  { value: "DRAFT", label: "Draft" },
  { value: "APPLICATION_OPEN", label: "Application" },
  { value: "SUBMISSION_OPEN", label: "Submission" },
  { value: "BATTLES", label: "Battles" },
  { value: "CLOSED", label: "Closed" },
];

const applicationRows = computed(() => applications.value.filter((entry) => Number(entry.tournament) === tournamentId.value));
const submissionRows = computed(() => submissions.value.filter((entry) => Number(entry.tournament) === tournamentId.value));
const battleRows = computed(() => battles.value.filter((entry) => Number(entry.tournament) === tournamentId.value));
const participantsCount = computed(() => {
  const names = new Set();
  applicationRows.value.forEach((entry) => names.add(String(entry.profile_name || entry.profile?.name || "")));
  submissionRows.value.forEach((entry) => names.add(String(entry.profile_name || entry.profile?.name || "")));
  names.delete("");
  return names.size;
});

const battleProfileHistory = computed(() => {
  if (!selectedBattleProfile.value?.name) return [];
  const target = String(selectedBattleProfile.value.name).toLowerCase();
  return battleRows.value
    .filter((battle) => {
      const left = String(battle.left_profile_name || "").toLowerCase();
      const right = String(battle.right_profile_name || "").toLowerCase();
      return left === target || right === target;
    })
    .sort((a, b) => Number(b.id || 0) - Number(a.id || 0));
});

const fallbackTournamentCovers = [
  "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1571330735066-03aaa9429d89?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
];

function asList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || payload || [];
}

function sanitizeTab(value) {
  const key = String(value || "");
  return validTabs.includes(key) ? key : "overview";
}

function setTab(tabKey) {
  const next = sanitizeTab(tabKey);
  activeTab.value = next;
  router.replace({ query: { ...route.query, tab: next } });
}

function statusLabel(status) {
  const map = {
    DRAFT: "Entwurf",
    APPLICATION_OPEN: "Bewerbung offen",
    SUBMISSION_OPEN: "Einreichung offen",
    BATTLES: "Battles",
    CLOSED: "Geschlossen",
  };
  return map[status] || status || "-";
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "-";
  return date.toLocaleString("de-DE");
}

function tournamentCover(item) {
  if (!item) return fallbackTournamentCovers[0];
  if (item.cover_url) return item.cover_url;
  const index = Math.abs(Number(item.id || 0)) % fallbackTournamentCovers.length;
  return fallbackTournamentCovers[index];
}

function goBack() {
  router.push({ name: "platform-contests", query: { tab: "tournaments", ...(artistPreview.value ? { artistView: "1" } : {}) } });
}

function openProfile() {
  router.push({ name: "me" });
}

function openBattleProfileByName(name) {
  if (!name) return;
  selectedBattleProfile.value = { name };
}

function canVoteBattle(battle) {
  if (!battle || battle.status === "CLOSED") return false;
  if (tournament.value?.status !== "BATTLES") return false;
  if (tournament.value?.allow_vote_change) return true;
  return !myVotes.value.some((vote) => Number(vote.battle) === Number(battle.id));
}

async function loadDetail() {
  busy.value = true;
  try {
    const requests = [
      api.get(`tournaments/${tournamentId.value}/`),
      api.get("tournament-applications/"),
      api.get("tournament-submissions/"),
      api.get("tournament-battles/"),
      api.get("tournaments/ranked-overview/"),
    ];
    if (!viewerIsTeam.value) requests.push(api.get("tournament-votes/"));

    const [tournamentRes, applicationsRes, submissionsRes, battlesRes, rankedRes, votesRes] = await Promise.all(requests);
    tournament.value = tournamentRes?.data || null;
    applications.value = asList(applicationsRes?.data);
    submissions.value = asList(submissionsRes?.data);
    battles.value = asList(battlesRes?.data);
    rankedOverview.value = rankedRes?.data || {};
    myVotes.value = votesRes ? asList(votesRes.data) : [];
  } catch (err) {
    console.error(err);
    showToast("Turnierdetails konnten nicht geladen werden", "error");
  } finally {
    busy.value = false;
  }
}

async function setTournamentStatus(nextStatus) {
  if (!viewerIsTeam.value || !tournament.value || tournament.value.status === nextStatus) return;
  busy.value = true;
  try {
    await api.patch(`tournaments/${tournament.value.id}/`, { status: nextStatus });
    showToast(`Status: ${statusLabel(nextStatus)}`, "success");
    await loadDetail();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Statusupdate fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function submitApplication() {
  if (!tournament.value) return;
  busy.value = true;
  try {
    await api.post("tournament-applications/", {
      tournament: tournament.value.id,
      message: applicationMessage.value || "",
    });
    applicationMessage.value = "";
    showToast("Bewerbung gesendet", "success");
    await loadDetail();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Bewerbung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function submitRound() {
  if (!tournament.value || !submissionTitle.value.trim()) {
    showToast("Titel fehlt", "warning");
    return;
  }
  busy.value = true;
  try {
    await api.post("tournament-submissions/", {
      tournament: tournament.value.id,
      title: submissionTitle.value,
      media_url: submissionMediaUrl.value,
    });
    submissionTitle.value = "";
    submissionMediaUrl.value = "";
    showToast("Runde eingereicht", "success");
    await loadDetail();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Einreichung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function voteBattle(battle, selectedSubmissionId) {
  if (!canVoteBattle(battle)) {
    showToast("Vote ist aktuell nicht möglich", "warning");
    return;
  }
  busy.value = true;
  try {
    await api.post("tournament-votes/", {
      battle: battle.id,
      selected_submission: selectedSubmissionId,
    });
    showToast("Vote gespeichert", "success");
    await loadDetail();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Vote fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function closeBattle(battle, winnerSubmissionId = null) {
  if (!viewerIsTeam.value) return;
  busy.value = true;
  try {
    const payload = winnerSubmissionId ? { winner_submission: winnerSubmissionId } : {};
    await api.post(`tournament-battles/${battle.id}/close/`, payload);
    showToast("Battle geschlossen", "success");
    await loadDetail();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Battle konnte nicht geschlossen werden", "error");
  } finally {
    busy.value = false;
  }
}

onMounted(async () => {
  activeTab.value = sanitizeTab(route.query.tab);
  await fetchProfile();
  await loadDetail();
});

watch(
  () => route.query.tab,
  (value) => {
    const next = sanitizeTab(value);
    if (activeTab.value !== next) activeTab.value = next;
  }
);

watch(
  () => route.params.tournamentId,
  async () => {
    await loadDetail();
  }
);
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Sora:wght@400;600;700;800&display=swap");

.detail-page {
  min-height: 100vh;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  padding: 18px clamp(14px, 2vw, 34px) 42px;
  position: relative;
  color: #eef3ff;
  font-family: "Chakra Petch", sans-serif;
  display: grid;
  gap: 14px;
}

.ambient {
  position: fixed;
  inset: 0;
  z-index: -2;
  background:
    radial-gradient(circle at 12% 9%, rgba(255, 73, 128, 0.3), transparent 43%),
    radial-gradient(circle at 88% 13%, rgba(93, 214, 255, 0.28), transparent 38%),
    linear-gradient(145deg, #060916 0%, #111a3d 53%, #1a1031 100%);
}

.detail-topbar,
.hero,
.subtabs,
.panel {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  backdrop-filter: blur(6px);
}

.detail-topbar {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.eyebrow {
  margin: 6px 0 0;
  font-size: 0.7rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #84dcff;
}

.detail-topbar h1 {
  margin: 2px 0 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(1.32rem, 2.1vw, 1.95rem);
}

.top-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero {
  padding: 12px;
  display: grid;
  grid-template-columns: minmax(260px, 38%) minmax(0, 1fr);
  gap: 12px;
}

.hero-cover {
  border-radius: 12px;
  min-height: 210px;
  background-size: cover;
  background-position: center;
}

.hero-info {
  display: grid;
  gap: 10px;
}

.hero-info p {
  margin: 0;
  color: #c6d3f3;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.hero-stats article {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 9px;
  background: rgba(10, 16, 35, 0.45);
  display: grid;
  gap: 2px;
}

.hero-stats strong {
  color: #fff;
}

.hero-stats span {
  color: #b8c7ed;
  font-size: 0.8rem;
}

.hero-actions {
  display: grid;
  gap: 8px;
}

.subtabs {
  padding: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.subtab {
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #ccdaff;
  border-radius: 999px;
  padding: 8px 12px;
  cursor: pointer;
  font-family: "Sora", sans-serif;
  font-weight: 600;
}

.subtab.active {
  background: linear-gradient(125deg, #ff4d6d, #ff7b54);
  border-color: transparent;
  color: #fff;
}

.panel {
  padding: 14px;
  display: grid;
  gap: 12px;
}

.section-head h2 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.two-col {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.card {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  display: grid;
  gap: 8px;
}

.card h3 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.status-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.rules {
  margin: 0;
  padding-left: 17px;
  color: #c6d3f3;
  display: grid;
  gap: 6px;
}

.battle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 12px;
}

.battle-card {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  display: grid;
  gap: 8px;
}

.duel-head {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 10px;
  align-items: center;
}

.duel-head strong {
  text-align: center;
}

.duel-head .link-btn:last-child {
  text-align: right;
}

.duel-meta {
  display: flex;
  justify-content: space-between;
  color: #b8c7ed;
  font-size: 0.84rem;
}

.duel-actions {
  display: flex;
  gap: 8px;
}

.list {
  display: grid;
  gap: 8px;
}

.row {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.row p {
  margin: 2px 0 0;
  color: #b8c7ed;
  font-size: 0.86rem;
}

.upload-box {
  display: grid;
  gap: 8px;
}

.input {
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #eef3ff;
  padding: 9px 11px;
  font-family: "Sora", sans-serif;
}

.badge {
  display: inline-flex;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  padding: 2px 9px;
  font-size: 0.72rem;
  color: #dbe7ff;
}

.link-btn {
  border: 0;
  background: transparent;
  color: #9edcff;
  font: inherit;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
  text-decoration-color: rgba(158, 220, 255, 0.4);
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.74);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  width: min(700px, 92vw);
  max-height: 82vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.14), rgba(112, 231, 255, 0.08));
}

.modal-card header {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 16px;
  display: grid;
  gap: 10px;
}

.history {
  display: grid;
  gap: 7px;
}

.history-row {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 9px;
  padding: 9px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.history-row span {
  color: #b8c7ed;
  font-size: 0.84rem;
}

.btn {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 9px;
  background: linear-gradient(125deg, #ff4d6d, #ff7b54);
  color: #fff;
  font-family: "Sora", sans-serif;
  font-weight: 700;
  padding: 8px 12px;
  cursor: pointer;
}

.btn.ghost {
  background: transparent;
  color: #d2ddff;
}

.btn.small {
  padding: 5px 9px;
  font-size: 0.82rem;
}

.muted {
  margin: 0;
  color: #b8c7ed;
}

.empty {
  padding: 20px;
  text-align: center;
  color: #b8c7ed;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

@media (max-width: 980px) {
  .hero {
    grid-template-columns: 1fr;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .two-col {
    grid-template-columns: 1fr;
  }

  .duel-head {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .duel-head .link-btn:last-child {
    text-align: center;
  }

  .history-row {
    flex-direction: column;
  }
}
</style>
