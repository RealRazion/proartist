<template>
  <div class="tournament-detail-page">
    <div class="detail-bg"></div>

    <section class="detail-toolbar">
      <button class="btn ghost" type="button" @click="goBack">Zurueck</button>
      <button class="btn ghost" type="button" @click="goPlatforms">Hub</button>
    </section>

    <section v-if="tournament" class="detail-hero">
      <img v-if="tournament.cover_url" :src="tournament.cover_url" :alt="tournament.title" class="hero-cover" />
      <div class="hero-copy">
        <p class="eyebrow">Turnier Detail</p>
        <h1>{{ tournament.title }}</h1>
        <p>{{ tournament.description || "Bereit fuer die naechste Runde." }}</p>
        <div class="tag-row">
          <span class="tag">{{ statusLabel(tournament.status) }}</span>
          <span v-if="tournament.is_no_loss" class="tag">No Loss</span>
          <span v-if="tournament.is_recurring" class="tag">Recurring</span>
        </div>
      </div>
    </section>

    <section v-if="tournament" class="detail-tabs">
      <button class="detail-tab" :class="{ active: activeDetailTab === 'overview' }" @click="selectDetailTab('overview')">Overview</button>
      <button class="detail-tab" :class="{ active: activeDetailTab === 'battles' }" @click="selectDetailTab('battles')">Battles</button>
      <button class="detail-tab" :class="{ active: activeDetailTab === 'participants' }" @click="selectDetailTab('participants')">Teilnehmer</button>
      <button class="detail-tab" :class="{ active: activeDetailTab === 'rules' }" @click="selectDetailTab('rules')">Rules</button>
    </section>

    <section v-if="activeDetailTab === 'overview' && tournament && !viewerIsTeam && tournament.has_application_phase" class="panel">
      <h3>Bewerbung</h3>
      <p v-if="myApplication">Status: {{ myApplication.status }}</p>
      <div v-else class="form-row">
        <textarea v-model.trim="applicationDraft" rows="3" placeholder="Kurz bewerben"></textarea>
        <button class="btn" :disabled="busy" @click="submitApplication">Jetzt bewerben</button>
      </div>
    </section>

    <section v-if="activeDetailTab === 'overview' && tournament && !viewerIsTeam" class="panel">
      <h3>Runde einreichen</h3>
      <div class="form-row">
        <input v-model.trim="submissionDraft.title" placeholder="Track / Runde Titel" />
        <input v-model.trim="submissionDraft.media_url" placeholder="https://media-link" />
        <button class="btn" :disabled="busy || !canSubmit" @click="submitRound">Runde einreichen</button>
      </div>
    </section>

    <section v-if="activeDetailTab === 'overview' && tournament && viewerIsTeam" class="panel">
      <h3>Admin Aktionen</h3>
      <div class="actions">
        <button class="btn ghost" :disabled="busy" @click="setStatus('APPLICATION_OPEN')">Applications</button>
        <button class="btn ghost" :disabled="busy" @click="setStatus('SUBMISSION_OPEN')">Submissions</button>
        <button class="btn ghost" :disabled="busy" @click="setStatus('BATTLES')">Battles</button>
        <button class="btn" :disabled="busy" @click="setStatus('CLOSED')">Close</button>
      </div>
    </section>

    <section v-if="activeDetailTab === 'battles'" class="panel">
      <h3>Battles</h3>
      <div v-if="tournamentBattles.length" class="battle-list">
        <article v-for="battle in tournamentBattles" :key="`battle-${battle.id}`" class="battle-card">
          <div class="battle-head">
            <strong>{{ battle.left_profile_name }}</strong>
            <span>{{ battle.votes_left }} : {{ battle.votes_right }}</span>
            <strong>{{ battle.right_profile_name }}</strong>
          </div>
          <small>Runde {{ battle.round_number }} • {{ battle.status }}</small>
          <div v-if="!viewerIsTeam && battle.status !== 'CLOSED'" class="actions">
            <button class="btn" :disabled="busy || !canVoteBattle(battle)" @click="voteBattle(battle, battle.left_submission)">Left</button>
            <button class="btn ghost" :disabled="busy || !canVoteBattle(battle)" @click="voteBattle(battle, battle.right_submission)">Right</button>
          </div>
          <div v-if="viewerIsTeam && battle.status !== 'CLOSED'" class="actions">
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle)">Auto Close</button>
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.left_submission)">Left Win</button>
            <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.right_submission)">Right Win</button>
          </div>
        </article>
      </div>
      <p v-else>Noch keine Battles fuer dieses Turnier.</p>
    </section>

    <section v-if="activeDetailTab === 'participants'" class="panel">
      <h3>Teilnehmer</h3>
      <table v-if="participantRows.length" class="participants-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Submissions</th>
            <th>Wins</th>
            <th>Ranked RP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in participantRows" :key="`participant-${row.name}`">
            <td>{{ row.name }}</td>
            <td>{{ row.submissions }}</td>
            <td>{{ row.wins }}</td>
            <td>{{ row.ranked_points }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else>Noch keine Teilnehmerdaten vorhanden.</p>
    </section>

    <section v-if="activeDetailTab === 'rules' && tournament" class="panel">
      <h3>Regeln & Setup</h3>
      <div class="rules-grid">
        <div><strong>Application Phase:</strong> {{ boolLabel(tournament.has_application_phase) }}</div>
        <div><strong>No Loss:</strong> {{ boolLabel(tournament.is_no_loss) }}</div>
        <div><strong>Recurring:</strong> {{ boolLabel(tournament.is_recurring) }}</div>
        <div><strong>Voting Mode:</strong> {{ tournament.voting_mode || '-' }}</div>
        <div><strong>Vote Change:</strong> {{ boolLabel(tournament.allow_vote_change) }}</div>
        <div><strong>Min. Account Age (h):</strong> {{ tournament.min_account_age_hours ?? '-' }}</div>
        <div><strong>Max Votes/IP/h:</strong> {{ tournament.max_votes_per_ip_per_hour ?? '-' }}</div>
        <div><strong>Start:</strong> {{ tournament.starts_at || '-' }}</div>
        <div><strong>Ende:</strong> {{ tournament.ends_at || '-' }}</div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const route = useRoute();
const router = useRouter();
const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const busy = ref(false);
const activeDetailTab = ref("overview");
const tournament = ref(null);
const battles = ref([]);
const submissions = ref([]);
const rankedOverview = ref({});
const applications = ref([]);
const myVotes = ref([]);
const applicationDraft = ref("");
const submissionDraft = ref({ title: "", media_url: "" });
const validTabs = ["overview", "battles", "participants", "rules"];

const viewerIsTeam = computed(() => isTeam.value);
const tournamentId = computed(() => Number(route.params.tournamentId));
const tournamentBattles = computed(() => battles.value.filter((b) => Number(b.tournament) === tournamentId.value));
const myApplication = computed(() => applications.value.find((entry) => Number(entry.tournament) === tournamentId.value) || null);
const participantRows = computed(() => {
  const rows = {};
  const rankedRows = Array.isArray(rankedOverview.value?.rows) ? rankedOverview.value.rows : [];
  const tournamentSubmissions = submissions.value.filter((entry) => Number(entry.tournament) === tournamentId.value);

  tournamentSubmissions.forEach((entry) => {
    const name =
      entry.profile_name ||
      entry.profile?.name ||
      entry.profile?.username ||
      entry.artist_name ||
      "Unknown";
    if (!rows[name]) {
      const rankedRow = rankedRows.find((rankedEntry) => String(rankedEntry.name || "").toLowerCase() === String(name).toLowerCase());
      rows[name] = {
        name,
        submissions: 0,
        wins: Number(rankedRow?.wins || 0),
        ranked_points: Number(rankedRow?.ranked_points || 0),
      };
    }
    rows[name].submissions += 1;
  });

  return Object.values(rows).sort((a, b) => b.ranked_points - a.ranked_points || b.wins - a.wins || b.submissions - a.submissions);
});
const canSubmit = computed(() => {
  if (!tournament.value?.has_application_phase) return true;
  return myApplication.value?.status === "APPROVED";
});

function statusLabel(status) {
  const map = {
    DRAFT: "Entwurf",
    APPLICATION_OPEN: "Bewerbung offen",
    SUBMISSION_OPEN: "Einreichung offen",
    BATTLES: "Battles",
    CLOSED: "Geschlossen",
  };
  return map[status] || status;
}

function boolLabel(value) {
  return value ? "Ja" : "Nein";
}

function sanitizeTab(tabValue) {
  const tab = String(tabValue || "").toLowerCase();
  return validTabs.includes(tab) ? tab : "overview";
}

function selectDetailTab(tabKey) {
  const nextTab = sanitizeTab(tabKey);
  if (activeDetailTab.value === nextTab) return;
  activeDetailTab.value = nextTab;
  router.replace({ query: { ...route.query, tab: nextTab } });
}

function canVoteBattle(battle) {
  if (!battle || battle.status === "CLOSED") return false;
  if (!tournament.value) return false;
  if (tournament.value.allow_vote_change) return true;
  return !myVotes.value.some((vote) => Number(vote.battle) === Number(battle.id));
}

function goBack() {
  router.push({ name: "platform-contests" });
}

function goPlatforms() {
  router.push({ name: "platforms" });
}

async function loadAll() {
  busy.value = true;
  try {
    const [tournamentRes, battlesRes, submissionsRes, rankedOverviewRes, applicationsRes, votesRes] = await Promise.all([
      api.get(`tournaments/${tournamentId.value}/`),
      api.get("tournament-battles/"),
      api.get("tournament-submissions/"),
      api.get("tournaments/ranked-overview/"),
      api.get("tournament-applications/"),
      api.get("tournament-votes/").catch(() => null),
    ]);
    tournament.value = tournamentRes?.data || null;
    battles.value = Array.isArray(battlesRes?.data) ? battlesRes.data : battlesRes?.data?.results || [];
    submissions.value = Array.isArray(submissionsRes?.data) ? submissionsRes.data : submissionsRes?.data?.results || [];
    rankedOverview.value = rankedOverviewRes?.data || {};
    applications.value = Array.isArray(applicationsRes?.data) ? applicationsRes.data : applicationsRes?.data?.results || [];
    myVotes.value = votesRes ? (Array.isArray(votesRes?.data) ? votesRes.data : votesRes?.data?.results || []) : [];
  } catch (err) {
    console.error(err);
    showToast("Turnier konnte nicht geladen werden", "error");
    router.push({ name: "platform-contests" });
  } finally {
    busy.value = false;
  }
}

async function submitApplication() {
  busy.value = true;
  try {
    await api.post("tournament-applications/", {
      tournament: tournamentId.value,
      message: applicationDraft.value,
    });
    applicationDraft.value = "";
    showToast("Bewerbung gesendet", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Bewerbung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function submitRound() {
  busy.value = true;
  try {
    await api.post("tournament-submissions/", {
      tournament: tournamentId.value,
      title: submissionDraft.value.title,
      media_url: submissionDraft.value.media_url,
    });
    submissionDraft.value = { title: "", media_url: "" };
    showToast("Runde eingereicht", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Einreichung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function voteBattle(battle, selectedSubmissionId) {
  busy.value = true;
  try {
    await api.post("tournament-votes/", {
      battle: battle.id,
      selected_submission: selectedSubmissionId,
    });
    showToast("Vote gespeichert", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Vote fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function closeBattle(battle, winnerSubmissionId = null) {
  busy.value = true;
  try {
    const payload = winnerSubmissionId ? { winner_submission: winnerSubmissionId } : {};
    await api.post(`tournament-battles/${battle.id}/close/`, payload);
    showToast("Battle geschlossen", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Battle konnte nicht geschlossen werden", "error");
  } finally {
    busy.value = false;
  }
}

async function setStatus(nextStatus) {
  if (!tournament.value || tournament.value.status === nextStatus) return;
  busy.value = true;
  try {
    await api.patch(`tournaments/${tournamentId.value}/`, { status: nextStatus });
    showToast(`Status: ${statusLabel(nextStatus)}`, "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Statusupdate fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

onMounted(async () => {
  activeDetailTab.value = sanitizeTab(route.query.tab);
  await fetchProfile();
  await loadAll();
});

watch(
  () => route.query.tab,
  (value) => {
    const nextTab = sanitizeTab(value);
    if (activeDetailTab.value !== nextTab) activeDetailTab.value = nextTab;
  }
);
</script>

<style scoped>
.tournament-detail-page {
  min-height: 100vh;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  padding: 20px clamp(14px, 2vw, 32px) 40px;
  position: relative;
  color: #f2f5ff;
  display: grid;
  gap: 14px;
}

.detail-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background:
    radial-gradient(circle at 8% 8%, rgba(255, 82, 108, 0.28), transparent 40%),
    radial-gradient(circle at 90% 16%, rgba(90, 201, 255, 0.22), transparent 35%),
    linear-gradient(145deg, #04060f 0%, #0d1530 50%, #120f24 100%);
}

.detail-toolbar {
  display: flex;
  gap: 8px;
}

.detail-tabs {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-tab {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
  color: #d7e3ff;
  padding: 7px 12px;
  cursor: pointer;
  font-weight: 600;
}

.detail-tab.active {
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  border-color: transparent;
  color: #fff;
}

.detail-hero,
.panel {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: rgba(6, 10, 24, 0.75);
  padding: 14px;
}

.detail-hero {
  display: grid;
  grid-template-columns: minmax(200px, 340px) 1fr;
  gap: 14px;
}

.hero-cover {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 10px;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.14em;
  font-size: 0.72rem;
  color: #7dd3fc;
}

.hero-copy h1 {
  margin: 6px 0;
}

.tag-row {
  display: flex;
  gap: 8px;
}

.tag {
  display: inline-flex;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.form-row {
  display: grid;
  gap: 8px;
}

textarea,
input {
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.06);
  color: #f2f5ff;
  padding: 10px 12px;
}

.battle-list {
  display: grid;
  gap: 10px;
}

.battle-card {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.04);
  display: grid;
  gap: 8px;
}

.battle-head {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 8px;
  align-items: center;
}

.battle-head strong:last-child {
  text-align: right;
}

.participants-table {
  width: 100%;
  border-collapse: collapse;
}

.participants-table th,
.participants-table td {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.participants-table th {
  color: #b9c9f2;
  font-size: 0.85rem;
}

.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 10px;
}

.rules-grid div {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.04);
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  color: #fff;
  font-weight: 700;
  padding: 8px 12px;
  cursor: pointer;
}

.btn.ghost {
  background: transparent;
  color: #d7e3ff;
}

@media (max-width: 900px) {
  .detail-hero {
    grid-template-columns: 1fr;
  }
}
</style>
