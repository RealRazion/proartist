<template>
  <div class="tournament-page">
    <div class="arena-bg-layer"></div>

    <!-- TOP TOOLBAR -->
    <section class="contest-toolbar">
      <div class="toolbar-nav">
        <div class="tab-bar">
          <button
            v-for="tab in tabOptions"
            :key="tab.key"
            :class="{ active: activeTab === tab.key }"
            class="tab-btn"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </div>
      </div>
      <div class="toolbar-actions">
        <button class="btn ghost small" type="button" @click="goHome">Hub</button>
        <button v-if="isTeam" class="btn ghost small" type="button" @click="toggleArtistView">
          {{ artistPreview ? "Admin View" : "Artist View" }}
        </button>
        <button class="avatar-btn" type="button" @click="openProfile" :title="profile?.name || profile?.username || 'Profil'">
          {{ profileInitial }}
        </button>
      </div>
    </section>

    <!-- COMPACT HEADER -->
    <header class="arena-hero-compact">
      <div class="hero-title">
        <h1>UNYQ Tournament Arena</h1>
        <p v-if="artistPreview" class="preview-badge">Admin View</p>
      </div>
      <div class="hero-stats">
        <span><strong>{{ tournaments.length }}</strong> Turniere</span>
        <span><strong>{{ battles.length }}</strong> Battles</span>
        <span><strong>{{ topRankedRows.length }}</strong> ranked</span>
      </div>
    </header>

    <!-- TAB: TOURNAMENTS LIST -->
    <section v-show="activeTab === 'tournaments'" class="view-section tournaments-view">
      <div class="view-controls">
        <input
          v-model.trim="tournamentSearch"
          type="text"
          placeholder="Suche Turniere..."
          class="search-input"
        />
        <select v-model="statusFilter" class="status-filter">
          <option value="ALL">Alle Status</option>
          <option value="DRAFT">Entwurf</option>
          <option value="APPLICATION_OPEN">Bewerbung offen</option>
          <option value="SUBMISSION_OPEN">Einreichung offen</option>
          <option value="BATTLES">Battles</option>
          <option value="CLOSED">Geschlossen</option>
        </select>
        <select v-model="sortMode" class="sort-filter">
          <option value="open-first">Open First</option>
          <option value="newest">Newest</option>
          <option value="most-battles">Most Battles</option>
          <option value="most-submissions">Most Submissions</option>
        </select>
      </div>

      <div class="tournament-grid">
        <article
          v-for="tournament in visibleTournaments"
          :key="`tournament-${tournament.id}`"
          class="tournament-card"
          @click="selectTournament(tournament.id)"
          :class="{ active: selectedTournamentId === tournament.id }"
        >
          <div class="card-image" :style="{ backgroundImage: `url(${tournamentCover(tournament)})` }"></div>
          <div class="card-content">
            <h3>{{ tournament.title }}</h3>
            <p class="card-desc">{{ tournament.description }}</p>
            <div class="card-tags">
              <span class="tag">{{ statusLabel(tournament.status) }}</span>
              <span class="tag" v-if="tournament.is_no_loss">No Loss</span>
            </div>
            <button class="btn-small" @click.stop="openTournamentDetail(tournament)">Details</button>
          </div>
        </article>
      </div>

      <div v-if="!visibleTournaments.length" class="empty-state">
        <span>🎮</span>
        <p>Keine Turniere gefunden</p>
      </div>
    </section>

    <!-- TAB: LEADERBOARD -->
    <section v-show="activeTab === 'leaderboard'" class="view-section leaderboard-view">
      <div class="section-header">
        <h2>Global Leaderboard</h2>
        <p>Top ranked players</p>
      </div>

      <div class="rank-emblems-row" v-if="rankedOverview.tiers?.length">
        <article v-for="tier in rankedOverview.tiers" :key="tier.key" class="tier-badge" :title="tier.label">
          <img :src="rankArtwork(tier.key)" :alt="tier.label" />
          <span>{{ tier.label }}</span>
        </article>
      </div>

      <table class="leaderboard-table">
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Points</th>
            <th>Wins</th>
            <th>Battles</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in topRankedRows.slice(0, 50)" :key="`row-${row.profile_id}`" :class="{ 'my-row': row.profile_id === myProfileId }">
            <td class="rank-cell">
              <img class="tier-img" :src="rankArtwork(row.tier?.key)" :alt="row.tier?.label" />
              <strong>#{{ row.rank }}</strong>
            </td>
            <td class="name-cell">{{ row.name }}</td>
            <td class="points-cell"><strong>{{ row.ranked_points }}</strong> RP</td>
            <td class="win-cell">{{ row.wins }}</td>
            <td class="battle-cell">{{ row.battles }}</td>
          </tr>
        </tbody>
      </table>

      <div v-if="myRankedRow" class="my-progress-card">
        <strong>Dein Rang:</strong>
        <p>#{{ myRankedRow.rank }} {{ myRankedRow.tier?.label }} • {{ myRankedRow.ranked_points }} RP</p>
      </div>
    </section>

    <!-- TAB: MY TOURNAMENTS -->
    <section v-show="activeTab === 'my-tournaments'" class="view-section my-tournaments-view">
      <div class="section-header">
        <h2>Meine Turniere</h2>
        <p>Deine Bewerbungen und Einreichungen</p>
      </div>

      <div v-if="!viewerIsTeam" class="my-tournaments-list">
        <article v-for="app in applications" :key="`app-${app.id}`" class="tournament-mini">
          <div class="mini-header">
            <h4>{{ app.tournament_title }}</h4>
            <span class="tag">{{ app.status }}</span>
          </div>
          <p>{{ app.message || "Keine Nachricht" }}</p>
          <small>Status: {{ app.status }}</small>
        </article>

        <div v-if="!applications.length" class="empty-state">
          <span>📝</span>
          <p>Keine Bewerbungen</p>
        </div>
      </div>

      <div v-if="viewerIsTeam" class="admin-section">
        <h3>Admin: Turniere verwalten</h3>
        <button class="btn" @click="showCreateForm = !showCreateForm">
          {{ showCreateForm ? "Form ausblenden" : "Neues Turnier" }}
        </button>

        <form v-if="showCreateForm" class="create-form" @submit.prevent="createTournament">
          <input v-model.trim="createForm.title" required placeholder="Turnier Titel" />
          <textarea v-model.trim="createForm.description" rows="2" placeholder="Beschreibung"></textarea>
          <div class="form-grid">
            <select v-model="createForm.status">
              <option value="DRAFT">Entwurf</option>
              <option value="APPLICATION_OPEN">Bewerbung offen</option>
              <option value="SUBMISSION_OPEN">Einreichung offen</option>
              <option value="BATTLES">Battles</option>
              <option value="CLOSED">Geschlossen</option>
            </select>
            <input v-model="createForm.starts_at" type="datetime-local" />
            <input v-model="createForm.ends_at" type="datetime-local" />
          </div>
          <label><input v-model="createForm.has_application_phase" type="checkbox" /> Bewerbung erforderlich</label>
          <label><input v-model="createForm.is_no_loss" type="checkbox" /> No Loss Mode</label>
          <button class="btn" type="submit" :disabled="busy">Erstellen</button>
        </form>
      </div>
    </section>

    <!-- TAB: BATTLES -->
    <section v-show="activeTab === 'battles'" class="view-section battles-view">
      <div class="section-header">
        <h2>Live Battles</h2>
        <p>Aktuelle und vergangene Battles</p>
      </div>

      <div class="battles-list">
        <article v-for="battle in battles.slice(0, 20)" :key="`battle-${battle.id}`" class="battle-card">
          <div class="battle-info">
            <div class="duel-left">
              <strong>{{ battle.left_profile_name }}</strong>
              <span>Votes: {{ battle.votes_left }}</span>
            </div>
            <div class="duel-center">
              <strong>Round {{ battle.round_number }}</strong>
              <span class="vs">VS</span>
              <span class="battle-status">{{ battle.status === "CLOSED" ? "Finished" : "Live" }}</span>
            </div>
            <div class="duel-right">
              <strong>{{ battle.right_profile_name }}</strong>
              <span>Votes: {{ battle.votes_right }}</span>
            </div>
          </div>

          <div v-if="!viewerIsTeam && battle.status !== 'CLOSED'" class="battle-actions">
            <button class="btn vote-left" @click="voteBattle(battle, battle.left_submission)" :disabled="!canVoteBattle(battle)">
              Left
            </button>
            <button class="btn vote-right ghost" @click="voteBattle(battle, battle.right_submission)" :disabled="!canVoteBattle(battle)">
              Right
            </button>
          </div>

          <div v-if="viewerIsTeam && battle.status !== 'CLOSED'" class="battle-actions">
            <button class="btn ghost small" @click="closeBattle(battle)">Auto Close</button>
            <button class="btn small" @click="closeBattle(battle, battle.left_submission)">Left Win</button>
            <button class="btn small" @click="closeBattle(battle, battle.right_submission)">Right Win</button>
          </div>
        </article>

        <div v-if="!battles.length" class="empty-state">
          <span>⚔️</span>
          <p>Keine Battles</p>
        </div>
      </div>
    </section>

    <!-- TAB: ADMIN PANEL -->
    <section v-show="activeTab === 'admin' && viewerIsTeam" class="view-section admin-view">
      <div class="section-header">
        <h2>Admin Panel</h2>
        <p>Tournament Management</p>
      </div>

      <div class="admin-grid">
        <div class="admin-card">
          <h3>Ranked Config</h3>
          <div class="config-list">
            <article v-for="tier in rankConfigTiers" :key="`tier-${tier.tier_key}`" class="config-row">
              <div class="config-fields">
                <input v-model="tier.tier_key" placeholder="Tier Key" />
                <input v-model.number="tier.min_points" type="number" placeholder="Min Points" />
                <input v-model.number="tier.win_points" type="number" placeholder="Win Points" />
              </div>
            </article>
          </div>
          <button class="btn" @click="saveRankedConfig" :disabled="busy">Save Configuration</button>
        </div>

        <div class="admin-card">
          <h3>Tools</h3>
          <button class="btn ghost" @click="goAnimationLab">Animation Lab</button>
        </div>
      </div>
    </section>

    <!-- TOURNAMENT DETAIL MODAL -->
    <div v-if="selectedTournamentDetail" class="modal-overlay" @click.self="selectedTournamentDetail = null">
      <article class="modal-card">
        <header class="modal-header">
          <h2>{{ selectedTournamentDetail.title }}</h2>
          <button class="btn ghost small" @click="selectedTournamentDetail = null">✕</button>
        </header>

        <div class="modal-content">
          <img
            v-if="selectedTournamentDetail.cover_url"
            :src="selectedTournamentDetail.cover_url"
            alt="Tournament Cover"
            class="modal-image"
          />

          <p class="modal-desc">{{ selectedTournamentDetail.description }}</p>

          <div class="modal-tags">
            <span class="tag">{{ statusLabel(selectedTournamentDetail.status) }}</span>
            <span v-if="selectedTournamentDetail.is_no_loss" class="tag">No Loss</span>
            <span v-if="selectedTournamentDetail.is_recurring" class="tag">Recurring</span>
          </div>

          <!-- APPLICATION SECTION -->
          <div
            v-if="selectedTournamentDetail.has_application_phase && !viewerIsTeam && !myApplication(selectedTournamentDetail.id)"
            class="modal-section"
          >
            <h4>Apply for Tournament</h4>
            <textarea
              v-model.trim="applicationDrafts[selectedTournamentDetail.id]"
              rows="3"
              placeholder="Tell us why you want to participate..."
            ></textarea>
            <button class="btn" @click="submitApplication(selectedTournamentDetail.id)" :disabled="busy">Submit Application</button>
          </div>

          <div v-if="myApplication(selectedTournamentDetail.id)" class="modal-section">
            <p>✓ You have applied: {{ myApplication(selectedTournamentDetail.id).status }}</p>
          </div>

          <!-- SUBMISSION SECTION -->
          <div v-if="selectedTournamentDetail.status === 'SUBMISSION_OPEN' && !viewerIsTeam" class="modal-section">
            <h4>Submit Your Round</h4>
            <input
              v-model.trim="submissionDraft(selectedTournamentDetail.id).title"
              placeholder="Track / Round Title"
            />
            <input v-model.trim="submissionDraft(selectedTournamentDetail.id).media_url" placeholder="https://media-url" />
            <button class="btn" @click="submitRound(selectedTournamentDetail.id)" :disabled="busy">
              Submit Round
            </button>
          </div>

          <!-- ADMIN ACTIONS -->
          <div v-if="viewerIsTeam" class="modal-section">
            <h4>Admin Actions</h4>
            <div class="button-group">
              <button class="btn ghost" @click="setTournamentStatus(selectedTournamentDetail, 'APPLICATION_OPEN')">
                → Applications
              </button>
              <button class="btn ghost" @click="setTournamentStatus(selectedTournamentDetail, 'SUBMISSION_OPEN')">
                → Submissions
              </button>
              <button class="btn ghost" @click="setTournamentStatus(selectedTournamentDetail, 'BATTLES')">
                → Battles Live
              </button>
              <button class="btn" @click="setTournamentStatus(selectedTournamentDetail, 'CLOSED')">Close</button>
            </div>
          </div>
        </div>
      </article>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import bronzeRank from "../assets/ranks/bronze-icon.svg";
import silberRank from "../assets/ranks/silber-icon.svg";
import goldRank from "../assets/ranks/gold-icon.svg";
import platinRank from "../assets/ranks/platin-icon.svg";
import legendarRank from "../assets/ranks/legendaer-icon.svg";

const router = useRouter();
const route = useRoute();
const { profile, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const activeTab = ref("tournaments");
const busy = ref(false);
const showCreateForm = ref(false);
const tournaments = ref([]);
const applications = ref([]);
const submissions = ref([]);
const battles = ref([]);
const myVotes = ref([]);
const rankedOverview = ref({});
const rankConfigTiers = ref([]);
const tournamentSearch = ref("");
const statusFilter = ref("ALL");
const sortMode = ref("open-first");
const selectedTournamentId = ref(null);
const selectedTournamentDetail = ref(null);
const applicationDrafts = ref({});
const submissionDrafts = ref({});

const createForm = ref({
  title: "",
  description: "",
  status: "DRAFT",
  has_application_phase: true,
  is_no_loss: false,
  is_recurring: false,
  starts_at: "",
  ends_at: "",
});

const tabOptions = computed(() => {
  const tabs = [
    { key: "tournaments", label: "Turniere" },
    { key: "leaderboard", label: "Leaderboard" },
    { key: "my-tournaments", label: "Meine" },
    { key: "battles", label: "Battles" },
  ];
  if (isTeam.value) tabs.push({ key: "admin", label: "Admin" });
  return tabs;
});

const artistPreview = computed(() => isTeam.value && String(route.query.artistView || "").toLowerCase() === "1");
const viewerIsTeam = computed(() => isTeam.value && !artistPreview.value);
const profileInitial = computed(() => {
  const source = profile.value?.name || profile.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});

const myProfileId = computed(() => profile.value?.id || null);
const rankedRows = computed(() => rankedOverview.value?.rows || []);
const topRankedRows = computed(() => rankedRows.value.slice(0, 50));
const myRankedRow = computed(() => rankedRows.value.find((row) => row.profile_id === myProfileId.value) || null);

const visibleTournaments = computed(() => {
  const term = tournamentSearch.value.trim().toLowerCase();
  let rows = [...tournaments.value];
  if (statusFilter.value !== "ALL") rows = rows.filter((item) => item.status === statusFilter.value);
  if (term) rows = rows.filter((item) => `${item.title || ""} ${item.description || ""}`.toLowerCase().includes(term));

  if (sortMode.value === "most-battles") rows.sort((a, b) => (b.battles_count || 0) - (a.battles_count || 0));
  else if (sortMode.value === "most-submissions") rows.sort((a, b) => (b.submissions_count || 0) - (a.submissions_count || 0));
  else if (sortMode.value === "open-first") {
    const rank = { APPLICATION_OPEN: 0, SUBMISSION_OPEN: 1, BATTLES: 2, DRAFT: 3, CLOSED: 4 };
    rows.sort((a, b) => (rank[a.status] ?? 9) - (rank[b.status] ?? 9));
  } else rows.sort((a, b) => new Date(b.created_at || 0) - new Date(a.created_at || 0));

  return rows;
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

function rankArtwork(tierKey) {
  const key = String(tierKey || "BRONZE").toUpperCase();
  const map = { BRONZE: bronzeRank, SILBER: silberRank, GOLD: goldRank, PLATIN: platinRank, LEGENDAER: legendarRank };
  return map[key] || bronzeRank;
}

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

function tournamentCover(tournament) {
  if (!tournament) return fallbackTournamentCovers[0];
  if (tournament.cover_url) return tournament.cover_url;
  const index = Math.abs(Number(tournament.id || 0)) % fallbackTournamentCovers.length;
  return fallbackTournamentCovers[index];
}

function selectTournament(tournamentId) {
  selectedTournamentId.value = tournamentId;
}

function openTournamentDetail(tournament) {
  selectedTournamentDetail.value = tournament;
}

function submissionDraft(tournamentId) {
  if (!submissionDrafts.value[tournamentId]) {
    submissionDrafts.value[tournamentId] = { title: "", media_url: "" };
  }
  return submissionDrafts.value[tournamentId];
}

function myApplication(tournamentId) {
  return applications.value.find((entry) => entry.tournament === tournamentId && entry.profile?.id === myProfileId.value) || null;
}

function canVoteBattle(battle) {
  if (!battle) return false;
  if (battle.status === "CLOSED") return false;
  return true;
}

function goHome() {
  router.push({ name: "platforms" });
}

function openProfile() {
  router.push({ name: "me" });
}

function toggleArtistView() {
  router.push({
    name: route.name,
    query: artistPreview.value ? {} : { artistView: "1" },
  });
}

function goAnimationLab() {
  router.push({ name: "admin-tournament-animations" });
}

async function loadAll() {
  busy.value = true;
  try {
    const requests = [
      api.get("tournaments/"),
      api.get("tournament-applications/"),
      api.get("tournament-submissions/"),
      api.get("tournament-battles/"),
      api.get("tournaments/ranked-overview/"),
      api.get("tournaments/ranked-config/"),
    ];
    if (!viewerIsTeam.value) requests.push(api.get("tournament-votes/"));

    const [tournamentRes, applicationRes, submissionRes, battleRes, rankedRes, rankedConfigRes, votesRes] = await Promise.all(requests);
    tournaments.value = asList(tournamentRes.data);
    applications.value = asList(applicationRes.data);
    submissions.value = asList(submissionRes.data);
    battles.value = asList(battleRes.data);
    rankedOverview.value = rankedRes?.data || {};
    rankConfigTiers.value = asList(rankedConfigRes?.data?.tiers || []);
    myVotes.value = votesRes ? asList(votesRes.data) : [];

    if (!selectedTournamentId.value || !tournaments.value.some((entry) => entry.id === selectedTournamentId.value)) {
      selectedTournamentId.value = tournaments.value[0]?.id || null;
    }
  } catch (err) {
    console.error(err);
    showToast("Turnierdaten konnten nicht geladen werden", "error");
  } finally {
    busy.value = false;
  }
}

async function createTournament() {
  if (!isTeam.value) return;
  busy.value = true;
  try {
    await api.post("tournaments/", {
      title: createForm.value.title,
      description: createForm.value.description,
      status: createForm.value.status,
      has_application_phase: createForm.value.has_application_phase,
      is_no_loss: createForm.value.is_no_loss,
      is_recurring: createForm.value.is_recurring,
      starts_at: createForm.value.starts_at || null,
      ends_at: createForm.value.ends_at || null,
    });
    showToast("Turnier erstellt", "success");
    createForm.value = { title: "", description: "", status: "DRAFT", has_application_phase: true, is_no_loss: false, is_recurring: false, starts_at: "", ends_at: "" };
    showCreateForm.value = false;
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Turnier konnte nicht erstellt werden", "error");
  } finally {
    busy.value = false;
  }
}

async function saveRankedConfig() {
  if (!isTeam.value) return;
  busy.value = true;
  try {
    const payload = {
      tiers: rankConfigTiers.value.map((tier) => ({
        tier_key: tier.tier_key,
        min_points: Number(tier.min_points || 0),
        win_points: Number(tier.win_points || 0),
      })),
    };
    await api.patch("tournaments/ranked-config/", payload);
    showToast("Ranked-Konfiguration gespeichert", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Fehler beim Speichern", "error");
  } finally {
    busy.value = false;
  }
}

async function submitApplication(tournamentId) {
  busy.value = true;
  try {
    await api.post("tournament-applications/", {
      tournament: tournamentId,
      message: applicationDrafts.value[tournamentId] || "",
    });
    applicationDrafts.value[tournamentId] = "";
    showToast("Bewerbung gesendet", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Bewerbung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

async function submitRound(tournamentId) {
  const draft = submissionDraft(tournamentId);
  busy.value = true;
  try {
    await api.post("tournament-submissions/", {
      tournament: tournamentId,
      title: draft.title,
      media_url: draft.media_url,
    });
    submissionDrafts.value[tournamentId] = { title: "", media_url: "" };
    showToast("Runde eingereicht", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Einreichung fehlgeschlagen", "error");
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

async function setTournamentStatus(tournament, nextStatus) {
  if (!tournament || tournament.status === nextStatus) return;
  busy.value = true;
  try {
    await api.patch(`tournaments/${tournament.id}/`, { status: nextStatus });
    showToast(`Status: ${statusLabel(nextStatus)}`, "success");
    selectedTournamentDetail.value = null;
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Statusupdate fehlgeschlagen", "error");
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
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Vote fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  await loadAll();
});
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Sora:wght@400;600;700;800&display=swap");

.tournament-page {
  min-height: 100vh;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  padding: 12px clamp(14px, 2vw, 32px) 40px clamp(14px, 2vw, 32px);
  position: relative;
  z-index: 0;
  color: #f2f5ff;
  font-family: "Chakra Petch", sans-serif;
  display: grid;
  gap: 12px;
  overflow: hidden;
}

.arena-bg-layer {
  position: fixed;
  inset: 0;
  z-index: -2;
  background: radial-gradient(circle at 8% 8%, rgba(255, 82, 108, 0.34), transparent 40%),
    radial-gradient(circle at 88% 12%, rgba(90, 201, 255, 0.3), transparent 36%),
    radial-gradient(circle at 45% 84%, rgba(255, 191, 71, 0.12), transparent 45%),
    linear-gradient(145deg, #04060f 0%, #0d1530 52%, #120f24 100%);
}

/* TOOLBAR */
.contest-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 12px;
  gap: 16px;
}

.toolbar-nav {
  flex: 1;
}

.tab-bar {
  display: flex;
  gap: 4px;
  overflow-x: auto;
  padding-bottom: 4px;
}

.tab-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #b5c1e9;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
  font-weight: 600;
  font-family: "Sora", sans-serif;
}

.tab-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(255, 255, 255, 0.2);
}

.tab-btn.active {
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  border-color: transparent;
  color: #fff;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.avatar-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(125deg, #ff4d6d, #ff7b54);
  border: none;
  color: #fff;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.2s;
}

.avatar-btn:hover {
  transform: scale(1.1);
}

/* COMPACT HEADER */
.arena-hero-compact {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.08), rgba(112, 231, 255, 0.04));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
}

.hero-title h1 {
  margin: 0;
  font-size: 1.4rem;
  font-family: "Sora", sans-serif;
}

.hero-title p {
  margin: 0;
  font-size: 0.75rem;
  color: #fef3c7;
  margin-top: 4px;
}

.preview-badge {
  display: inline-block;
  padding: 4px 8px;
  background: rgba(8, 12, 26, 0.54);
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 4px;
  font-size: 0.7rem;
}

.hero-stats {
  display: flex;
  gap: 20px;
  white-space: nowrap;
}

.hero-stats span {
  font-size: 0.85rem;
  color: #b5c1e9;
}

.hero-stats strong {
  color: #fff;
  margin-right: 4px;
}

/* VIEWS */
.view-section {
  min-height: 400px;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* TOURNAMENTS VIEW */
.tournaments-view .view-controls {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.search-input,
.status-filter,
.sort-filter {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #f2f5ff;
  font-family: "Sora", sans-serif;
}

.search-input {
  flex: 1;
}

.tournament-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.tournament-card {
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.1), rgba(112, 231, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tournament-card:hover {
  border-color: rgba(255, 87, 122, 0.4);
  transform: translateY(-4px);
}

.tournament-card.active {
  border-color: #ff4d6d;
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.2), rgba(112, 231, 255, 0.08));
}

.card-image {
  width: 100%;
  height: 160px;
  background-size: cover;
  background-position: center;
  position: relative;
}

.card-image::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(4, 6, 15, 0.8));
}

.card-content {
  padding: 12px;
}

.card-content h3 {
  margin: 0 0 4px 0;
  font-size: 1rem;
  color: #fff;
}

.card-desc {
  margin: 0 0 8px 0;
  font-size: 0.8rem;
  color: #b5c1e9;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}

.tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
  font-size: 0.7rem;
  color: #7dd3fc;
}

.btn-small {
  width: 100%;
  padding: 8px;
  background: rgba(255, 87, 122, 0.2);
  border: 1px solid rgba(255, 87, 122, 0.4);
  border-radius: 6px;
  color: #ff4d6d;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}

.btn-small:hover {
  background: rgba(255, 87, 122, 0.3);
}

/* LEADERBOARD VIEW */
.leaderboard-view .section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 1.6rem;
}

.section-header p {
  margin: 4px 0 0 0;
  color: #b5c1e9;
}

.rank-emblems-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.tier-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-width: 80px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  text-align: center;
}

.tier-badge img {
  width: 48px;
  height: 48px;
}

.tier-badge span {
  font-size: 0.7rem;
  color: #b5c1e9;
}

.leaderboard-table {
  width: 100%;
  border-collapse: collapse;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  overflow: hidden;
}

.leaderboard-table thead {
  background: rgba(255, 255, 255, 0.08);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.leaderboard-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #b5c1e9;
  font-size: 0.85rem;
}

.leaderboard-table td {
  padding: 12px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  font-size: 0.9rem;
}

.leaderboard-table tr:hover {
  background: rgba(255, 255, 255, 0.06);
}

.leaderboard-table tr.my-row {
  background: rgba(255, 87, 122, 0.1);
}

.rank-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tier-img {
  width: 32px;
  height: 32px;
}

.my-progress-card {
  margin-top: 20px;
  padding: 16px;
  background: rgba(255, 87, 122, 0.1);
  border: 1px solid rgba(255, 87, 122, 0.3);
  border-radius: 8px;
}

/* BATTLES VIEW */
.battles-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.battle-card {
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.1), rgba(112, 231, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
}

.battle-info {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  margin-bottom: 12px;
  align-items: center;
}

.duel-left,
.duel-right {
  text-align: center;
}

.duel-left strong,
.duel-right strong {
  display: block;
  color: #fff;
  margin-bottom: 4px;
}

.duel-left span,
.duel-right span {
  font-size: 0.8rem;
  color: #b5c1e9;
}

.duel-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.duel-center strong {
  color: #7dd3fc;
}

.vs {
  font-size: 0.75rem;
  color: #b5c1e9;
}

.battle-status {
  padding: 2px 8px;
  background: rgba(255, 87, 122, 0.2);
  border-radius: 4px;
  font-size: 0.7rem;
  color: #ff4d6d;
  font-weight: 600;
}

.battle-actions {
  display: flex;
  gap: 8px;
}

.vote-left,
.vote-right {
  flex: 1;
  padding: 8px;
  font-size: 0.85rem;
}

.vote-left {
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  border: none;
  color: #fff;
  cursor: pointer;
  border-radius: 6px;
  font-weight: 600;
}

.vote-right {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #b5c1e9;
  cursor: pointer;
  border-radius: 6px;
}

/* MODAL */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-card {
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.1), rgba(112, 231, 255, 0.05));
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 16px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  width: 90%;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-header h2 {
  margin: 0;
  font-size: 1.4rem;
}

.modal-header .btn {
  padding: 4px 12px;
}

.modal-content {
  padding: 20px;
  display: grid;
  gap: 16px;
}

.modal-image {
  width: 100%;
  height: 240px;
  object-fit: cover;
  border-radius: 8px;
}

.modal-desc {
  color: #b5c1e9;
  margin: 0;
  line-height: 1.6;
}

.modal-tags {
  display: flex;
  gap: 8px;
}

.modal-section {
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
}

.modal-section h4 {
  margin: 0 0 12px 0;
  color: #fff;
}

.modal-section textarea,
.modal-section input {
  width: 100%;
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f2f5ff;
  margin-bottom: 8px;
  font-family: "Sora", sans-serif;
}

.button-group {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.button-group .btn {
  flex: 1;
  min-width: 120px;
}

/* BUTTONS */
.btn {
  padding: 10px 16px;
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  border: none;
  border-radius: 8px;
  color: #fff;
  font-weight: 600;
  font-family: "Sora", sans-serif;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(255, 77, 109, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.ghost {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #b5c1e9;
}

.btn.ghost:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.3);
}

.btn.small {
  padding: 6px 12px;
  font-size: 0.85rem;
}

/* EMPTY STATE */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  gap: 12px;
  color: #b5c1e9;
}

.empty-state span {
  font-size: 3rem;
}

.empty-state p {
  margin: 0;
}

/* ADMIN VIEW */
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 16px;
}

.admin-card {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px;
}

.admin-card h3 {
  margin: 0 0 12px 0;
  color: #fff;
}

.create-form {
  display: grid;
  gap: 12px;
  margin-top: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.create-form input,
.create-form textarea,
.create-form select {
  padding: 8px 12px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: #f2f5ff;
  font-family: "Sora", sans-serif;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.my-tournaments-list {
  display: grid;
  gap: 12px;
}

.tournament-mini {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 12px;
}

.mini-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.mini-header h4 {
  margin: 0;
  color: #fff;
}

.tournament-mini p {
  margin: 8px 0;
  color: #b5c1e9;
  font-size: 0.9rem;
}

.tournament-mini small {
  color: #7dd3fc;
  font-size: 0.8rem;
}

.admin-section {
  margin-top: 20px;
}

.admin-section h3 {
  margin: 0 0 12px 0;
  color: #fff;
}
</style>
