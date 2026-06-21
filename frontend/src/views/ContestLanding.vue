<template>
  <div class="arena-page">
    <div class="ambient-bg"></div>

    <header class="topbar">
      <div class="brand-block">
        <p class="eyebrow">UNYQ COMPETITIVE MODE</p>
        <h1>Tournament Arena</h1>
      </div>
      <div class="topbar-actions">
        <button class="btn ghost small" type="button" @click="goHome">Hub</button>
        <button v-if="isTeam" class="btn ghost small" type="button" @click="toggleArtistView">
          {{ artistPreview ? "Admin View" : "Artist View" }}
        </button>
        <button class="avatar" type="button" @click="openProfile" :title="profile?.name || profile?.username || 'Profil'">
          {{ profileInitial }}
        </button>
      </div>
    </header>

    <section class="main-tabs">
      <button
        v-for="tab in tabOptions"
        :key="tab.key"
        class="tab-pill"
        :class="{ active: activeTab === tab.key }"
        @click="selectMainTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </section>

    <section class="stats-strip">
      <article>
        <strong>{{ tournaments.length }}</strong>
        <span>Turniere</span>
      </article>
      <article>
        <strong>{{ battles.length }}</strong>
        <span>Battles</span>
      </article>
      <article>
        <strong>{{ topRankedRows.length }}</strong>
        <span>Ranked Profiles</span>
      </article>
      <article>
        <strong>#{{ myRankedRow?.rank || '-' }}</strong>
        <span>Dein Rank</span>
      </article>
    </section>

    <template v-if="activeTab === 'tournaments'">
      <section class="view-card spotlight" v-if="featuredTournament">
        <div class="spotlight-cover" :style="{ backgroundImage: `url(${tournamentCover(featuredTournament)})` }"></div>
        <div class="spotlight-content">
          <p class="eyebrow">FEATURED</p>
          <h2>{{ featuredTournament.title }}</h2>
          <p>{{ featuredTournament.description || "Bereit für die nächste Runde." }}</p>
          <div class="inline-tags">
            <span class="badge">{{ statusLabel(featuredTournament.status) }}</span>
            <span v-if="featuredTournament.is_no_loss" class="badge">No Loss</span>
            <span v-if="featuredTournament.is_recurring" class="badge">Recurring</span>
          </div>
          <div class="spotlight-actions">
            <button class="btn" @click="openTournamentDetail(featuredTournament)">Turnier öffnen</button>
            <button class="btn ghost" @click="selectTournament(nextFeaturedId)">Nächstes</button>
          </div>
        </div>
      </section>

      <section class="view-card">
        <div class="controls">
          <input v-model.trim="tournamentSearch" class="input" type="text" placeholder="Turnier suchen..." />
          <select v-model="statusFilter" class="input">
            <option value="ALL">Alle Status</option>
            <option value="DRAFT">Entwurf</option>
            <option value="APPLICATION_OPEN">Bewerbung offen</option>
            <option value="SUBMISSION_OPEN">Einreichung offen</option>
            <option value="BATTLES">Battles</option>
            <option value="CLOSED">Geschlossen</option>
          </select>
          <select v-model="sortMode" class="input">
            <option value="open-first">Open First</option>
            <option value="newest">Newest</option>
            <option value="most-battles">Most Battles</option>
            <option value="most-submissions">Most Submissions</option>
          </select>
        </div>

        <div class="tournament-grid" v-if="visibleTournaments.length">
          <article
            v-for="tournament in visibleTournaments"
            :key="`tournament-${tournament.id}`"
            class="tournament-card"
            :class="{ selected: selectedTournamentId === tournament.id }"
            @click="openTournamentDetail(tournament)"
          >
            <div class="thumb" :style="{ backgroundImage: `url(${tournamentCover(tournament)})` }"></div>
            <div class="card-body">
              <h3>{{ tournament.title }}</h3>
              <p>{{ tournament.description || 'Keine Beschreibung' }}</p>
              <div class="inline-tags">
                <span class="badge">{{ statusLabel(tournament.status) }}</span>
                <span v-if="tournament.is_no_loss" class="badge">No Loss</span>
              </div>
            </div>
          </article>
        </div>
        <div v-else class="empty">Keine Turniere gefunden.</div>
      </section>
    </template>

    <template v-if="activeTab === 'leaderboard'">
      <section class="view-card">
        <div class="section-head">
          <h2>Leaderboard</h2>
          <p>Top Spieler mit Rank-Artwork und Battle-Profilzugriff.</p>
        </div>
        <div class="rank-row" v-if="rankedOverview.tiers?.length">
          <article v-for="tier in rankedOverview.tiers" :key="tier.key" class="rank-chip">
            <img :src="rankArtwork(tier.key)" :alt="tier.label" />
            <span>{{ tier.label }}</span>
          </article>
        </div>
        <div class="table-wrap">
          <table class="table">
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
              <tr v-for="row in topRankedRows" :key="`row-${row.profile_id}`" :class="{ me: row.profile_id === myProfileId }">
                <td>
                  <div class="rank-cell">
                    <img class="tiny-rank" :src="rankArtwork(row.tier?.key)" :alt="row.tier?.label" />
                    <strong>#{{ row.rank }}</strong>
                  </div>
                </td>
                <td>
                  <button class="link-btn" @click="openBattleProfileByRow(row)">{{ row.name }}</button>
                </td>
                <td>{{ row.ranked_points }}</td>
                <td>{{ row.wins }}</td>
                <td>{{ row.battles }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <template v-if="activeTab === 'my-tournaments'">
      <section class="view-card" v-if="!viewerIsTeam">
        <div class="section-head">
          <h2>Meine Turniere</h2>
          <p>Anmeldungen und Status auf einen Blick.</p>
        </div>
        <div class="list" v-if="applications.length">
          <article v-for="app in applications" :key="`app-${app.id}`" class="list-row">
            <div>
              <strong>{{ app.tournament_title }}</strong>
              <p>{{ app.message || 'Keine Nachricht' }}</p>
            </div>
            <span class="badge">{{ app.status }}</span>
          </article>
        </div>
        <div v-else class="empty">Noch keine Bewerbungen.</div>
      </section>

      <section class="view-card" v-else>
        <div class="section-head">
          <h2>Admin Turnier-Builder</h2>
          <p>Neue Turniere anlegen und Wettbewerb live schalten.</p>
        </div>
        <button class="btn ghost" @click="showCreateForm = !showCreateForm">{{ showCreateForm ? 'Form schließen' : 'Neues Turnier' }}</button>
        <form v-if="showCreateForm" class="builder" @submit.prevent="createTournament">
          <input v-model.trim="createForm.title" class="input" required placeholder="Turnier Titel" />
          <textarea v-model.trim="createForm.description" class="input" rows="3" placeholder="Beschreibung"></textarea>
          <div class="split-2">
            <select v-model="createForm.status" class="input">
              <option value="DRAFT">Entwurf</option>
              <option value="APPLICATION_OPEN">Bewerbung offen</option>
              <option value="SUBMISSION_OPEN">Einreichung offen</option>
              <option value="BATTLES">Battles</option>
              <option value="CLOSED">Geschlossen</option>
            </select>
            <input v-model="createForm.starts_at" class="input" type="datetime-local" />
          </div>
          <div class="split-2">
            <input v-model="createForm.ends_at" class="input" type="datetime-local" />
            <label class="check"><input v-model="createForm.is_no_loss" type="checkbox" /> No Loss</label>
          </div>
          <label class="check"><input v-model="createForm.has_application_phase" type="checkbox" /> Bewerbung erforderlich</label>
          <button class="btn" type="submit" :disabled="busy">Turnier erstellen</button>
        </form>
      </section>
    </template>

    <template v-if="activeTab === 'battles'">
      <section class="view-card">
        <div class="section-head">
          <h2>Live Battles</h2>
          <p>Voting und Match-Administration in Echtzeit.</p>
        </div>
        <div class="battle-grid" v-if="battles.length">
          <article v-for="battle in battles.slice(0, 24)" :key="`battle-${battle.id}`" class="battle-tile">
            <div class="duel-head">
              <button class="link-btn" @click="openBattleProfileByName(battle.left_profile_name)">{{ battle.left_profile_name }}</button>
              <strong>{{ battle.votes_left }} : {{ battle.votes_right }}</strong>
              <button class="link-btn" @click="openBattleProfileByName(battle.right_profile_name)">{{ battle.right_profile_name }}</button>
            </div>
            <div class="duel-meta">
              <span>Runde {{ battle.round_number }}</span>
              <span class="badge">{{ battle.status }}</span>
            </div>
            <div v-if="!viewerIsTeam && battle.status !== 'CLOSED'" class="duel-actions">
              <button class="btn" :disabled="!canVoteBattle(battle) || busy" @click="voteBattle(battle, battle.left_submission)">Left</button>
              <button class="btn ghost" :disabled="!canVoteBattle(battle) || busy" @click="voteBattle(battle, battle.right_submission)">Right</button>
            </div>
            <div v-if="viewerIsTeam && battle.status !== 'CLOSED'" class="duel-actions">
              <button class="btn ghost" :disabled="busy" @click="closeBattle(battle)">Auto Close</button>
              <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.left_submission)">Left Win</button>
              <button class="btn ghost" :disabled="busy" @click="closeBattle(battle, battle.right_submission)">Right Win</button>
            </div>
          </article>
        </div>
        <div v-else class="empty">Keine Battles verfügbar.</div>
      </section>
    </template>

    <template v-if="activeTab === 'admin' && viewerIsTeam">
      <section class="view-card">
        <div class="section-head">
          <h2>Admin Tools</h2>
          <p>Ranked Rules und Utility-Tools für Team-Mitglieder.</p>
        </div>
        <div class="split-2">
          <div class="admin-box">
            <h3>Ranked Config</h3>
            <div class="mini-list">
              <article v-for="tier in rankConfigTiers" :key="`tier-${tier.tier_key}`" class="tier-edit">
                <input v-model="tier.tier_key" class="input" />
                <input v-model.number="tier.min_points" class="input" type="number" />
                <input v-model.number="tier.win_points" class="input" type="number" />
              </article>
            </div>
            <button class="btn" :disabled="busy" @click="saveRankedConfig">Config speichern</button>
          </div>
          <div class="admin-box">
            <h3>Utilities</h3>
            <button class="btn ghost" @click="goAnimationLab">Animation Lab öffnen</button>
          </div>
        </div>
      </section>
    </template>

    <div v-if="selectedBattleProfile" class="modal-overlay" @click.self="selectedBattleProfile = null">
      <article class="modal-card">
        <header>
          <h2>{{ selectedBattleProfile.name }}</h2>
          <button class="btn ghost small" @click="selectedBattleProfile = null">✕</button>
        </header>
        <div class="modal-body">
          <div class="profile-hero">
            <img class="hero-rank" :src="rankArtwork(selectedBattleProfile.tier?.key)" :alt="selectedBattleProfile.tier?.label || 'Tier'" />
            <div>
              <p><strong>#{{ selectedBattleProfile.rank || '-' }}</strong> {{ selectedBattleProfile.tier?.label || 'Unranked' }}</p>
              <p>{{ selectedBattleProfile.ranked_points || 0 }} RP · {{ selectedBattleProfile.wins || 0 }} Wins · {{ selectedBattleProfile.losses || 0 }} Losses</p>
            </div>
          </div>

          <section>
            <h4>Achievements</h4>
            <div class="chips" v-if="battleProfileAchievements.length">
              <article v-for="(item, idx) in battleProfileAchievements" :key="`ach-${idx}`" class="chip">
                <strong>{{ item.title }}</strong>
                <small>{{ item.description }}</small>
              </article>
            </div>
            <p v-else class="muted">Keine Achievements verfügbar.</p>
          </section>

          <section>
            <h4>Previous Battles</h4>
            <div class="history" v-if="battleProfileHistory.length">
              <article v-for="battle in battleProfileHistory" :key="`hist-${battle.id}`" class="history-row">
                <strong>{{ battle.left_profile_name }} vs {{ battle.right_profile_name }}</strong>
                <span>R{{ battle.round_number }} · {{ battle.votes_left }}:{{ battle.votes_right }} · {{ battle.status }}</span>
              </article>
            </div>
            <p v-else class="muted">Keine Battle-Historie.</p>
          </section>
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
import bronzeRank from "../assets/ranks/bronze-icon.svg";
import silberRank from "../assets/ranks/silber-icon.svg";
import goldRank from "../assets/ranks/gold-icon.svg";
import platinRank from "../assets/ranks/platin-icon.svg";
import legendarRank from "../assets/ranks/legendaer-icon.svg";

const router = useRouter();
const route = useRoute();
const { profile, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const validTabs = ["tournaments", "leaderboard", "my-tournaments", "battles", "admin"];
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
const selectedBattleProfile = ref(null);
const myAchievements = ref([]);
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

const battleProfileHistory = computed(() => {
  if (!selectedBattleProfile.value?.name) return [];
  const target = String(selectedBattleProfile.value.name).toLowerCase();
  return battles.value
    .filter((battle) => {
      const left = String(battle.left_profile_name || "").toLowerCase();
      const right = String(battle.right_profile_name || "").toLowerCase();
      return left === target || right === target;
    })
    .sort((a, b) => Number(b.id || 0) - Number(a.id || 0))
    .slice(0, 10);
});

const battleProfileAchievements = computed(() => {
  const row = selectedBattleProfile.value;
  if (!row) return [];
  const items = [];
  if (Number(row.wins || 0) >= 1) items.push({ title: "Erster Sieg", description: "Mindestens einen Battle gewonnen." });
  if (Number(row.wins || 0) >= 10) items.push({ title: "Win Streak", description: "10 oder mehr Siege erreicht." });
  if (Number(row.ranked_points || 0) >= 150) items.push({ title: "Ranked Grinder", description: "150+ Ranked Points erspielt." });
  if (Number(row.battles || 0) >= 20) items.push({ title: "Veteran", description: "20+ Battles gespielt." });

  const isOwnProfile = row.profile_id && row.profile_id === myProfileId.value;
  if (isOwnProfile) {
    const ownAchievements = asList(myAchievements.value);
    ownAchievements.forEach((entry) => {
      const title = entry?.achievement?.title || entry?.title;
      const description = entry?.achievement?.description || entry?.description;
      if (title) items.push({ title, description: description || "Freigeschaltet" });
    });
  }
  return items;
});

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

const featuredTournament = computed(() => {
  if (!visibleTournaments.value.length) return null;
  if (!selectedTournamentId.value) return visibleTournaments.value[0];
  return visibleTournaments.value.find((t) => t.id === selectedTournamentId.value) || visibleTournaments.value[0];
});

const nextFeaturedId = computed(() => {
  if (!featuredTournament.value || !visibleTournaments.value.length) return null;
  const idx = visibleTournaments.value.findIndex((t) => t.id === featuredTournament.value.id);
  const nextIdx = (idx + 1) % visibleTournaments.value.length;
  return visibleTournaments.value[nextIdx]?.id || featuredTournament.value.id;
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

function sanitizeMainTab(value) {
  const key = String(value || "");
  return validTabs.includes(key) ? key : "tournaments";
}

function selectMainTab(tabKey) {
  const next = sanitizeMainTab(tabKey);
  activeTab.value = next;
  router.replace({ query: { ...route.query, tab: next } });
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

function tournamentOfBattle(battle) {
  return tournaments.value.find((t) => Number(t.id) === Number(battle.tournament));
}

function selectTournament(tournamentId) {
  selectedTournamentId.value = tournamentId;
}

function openTournamentDetail(tournament) {
  if (!tournament?.id) return;
  selectTournament(tournament.id);
  router.push({ name: "platform-contest-detail", params: { tournamentId: tournament.id } });
}

function openBattleProfileByRow(row) {
  selectedBattleProfile.value = row || null;
}

function openBattleProfileByName(name) {
  if (!name) return;
  const row = rankedRows.value.find((entry) => String(entry.name || "").toLowerCase() === String(name).toLowerCase());
  const fallbackBattleCount = battles.value.filter((battle) => {
    const left = String(battle.left_profile_name || "").toLowerCase();
    const right = String(battle.right_profile_name || "").toLowerCase();
    return left === String(name).toLowerCase() || right === String(name).toLowerCase();
  }).length;
  selectedBattleProfile.value = row || {
    name,
    tier: null,
    rank: null,
    ranked_points: 0,
    wins: 0,
    losses: 0,
    battles: fallbackBattleCount,
  };
}

function submissionDraft(tournamentId) {
  if (!submissionDrafts.value[tournamentId]) {
    submissionDrafts.value[tournamentId] = { title: "", media_url: "" };
  }
  return submissionDrafts.value[tournamentId];
}

function canVoteBattle(battle) {
  if (!battle) return false;
  if (battle.status === "CLOSED") return false;
  const tournament = tournamentOfBattle(battle);
  if (!tournament || tournament.status !== "BATTLES") return false;
  if (tournament.allow_vote_change) return true;
  return !myVotes.value.some((vote) => Number(vote.battle) === Number(battle.id));
}

function goHome() {
  router.push({ name: "platforms" });
}

function openProfile() {
  router.push({ name: "me" });
}

function toggleArtistView() {
  router.push({ name: route.name, query: artistPreview.value ? {} : { artistView: "1", tab: activeTab.value } });
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
      api.get("my-achievements/").catch(() => null),
    ];
    if (!viewerIsTeam.value) requests.push(api.get("tournament-votes/"));

    const [tournamentRes, applicationRes, submissionRes, battleRes, rankedRes, rankedConfigRes, myAchievementsRes, votesRes] = await Promise.all(requests);
    tournaments.value = asList(tournamentRes.data);
    applications.value = asList(applicationRes.data);
    submissions.value = asList(submissionRes.data);
    battles.value = asList(battleRes.data);
    rankedOverview.value = rankedRes?.data || {};
    rankConfigTiers.value = asList(rankedConfigRes?.data?.tiers || []);
    myAchievements.value = asList(myAchievementsRes?.data || []);
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

async function createOrRefreshAndToast(request, success, error) {
  try {
    await request();
    showToast(success, "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || error, "error");
  }
}

async function closeBattle(battle, winnerSubmissionId = null) {
  busy.value = true;
  await createOrRefreshAndToast(
    () => api.post(`tournament-battles/${battle.id}/close/`, winnerSubmissionId ? { winner_submission: winnerSubmissionId } : {}),
    "Battle geschlossen",
    "Battle konnte nicht geschlossen werden"
  );
  busy.value = false;
}

async function voteBattle(battle, selectedSubmissionId) {
  if (!canVoteBattle(battle)) {
    showToast("Vote ist aktuell nicht möglich", "warning");
    return;
  }
  busy.value = true;
  await createOrRefreshAndToast(
    () => api.post("tournament-votes/", { battle: battle.id, selected_submission: selectedSubmissionId }),
    "Vote gespeichert",
    "Vote fehlgeschlagen"
  );
  busy.value = false;
}

onMounted(async () => {
  activeTab.value = sanitizeMainTab(route.query.tab);
  await fetchProfile();
  await loadAll();
});

watch(
  () => route.query.tab,
  (value) => {
    const nextTab = sanitizeMainTab(value);
    if (activeTab.value !== nextTab) activeTab.value = nextTab;
  }
);
</script>

<style scoped>
@import url("https://fonts.googleapis.com/css2?family=Chakra+Petch:wght@400;500;600;700&family=Sora:wght@400;600;700;800&display=swap");

.arena-page {
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

.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: -2;
  background:
    radial-gradient(circle at 9% 10%, rgba(255, 71, 126, 0.28), transparent 43%),
    radial-gradient(circle at 85% 14%, rgba(88, 213, 255, 0.24), transparent 38%),
    radial-gradient(circle at 50% 90%, rgba(255, 190, 92, 0.16), transparent 42%),
    linear-gradient(145deg, #050711 0%, #0d1534 50%, #160f2a 100%);
}

.topbar,
.main-tabs,
.stats-strip,
.view-card {
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  background: linear-gradient(160deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  backdrop-filter: blur(6px);
}

.topbar {
  padding: 14px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.brand-block h1 {
  margin: 2px 0 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(1.35rem, 2.1vw, 2rem);
}

.eyebrow {
  margin: 0;
  font-size: 0.7rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #78d5ff;
}

.topbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: linear-gradient(125deg, #ff4d6d, #ff7b54);
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.main-tabs {
  padding: 8px;
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tab-pill {
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.05);
  color: #ccdaff;
  border-radius: 999px;
  padding: 8px 12px;
  cursor: pointer;
  font-family: "Sora", sans-serif;
  font-weight: 600;
}

.tab-pill.active {
  background: linear-gradient(125deg, #ff4d6d, #ff7b54);
  border-color: transparent;
  color: #fff;
}

.stats-strip {
  padding: 12px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.stats-strip article {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  background: rgba(10, 16, 35, 0.45);
  padding: 10px;
  display: grid;
  gap: 2px;
}

.stats-strip strong {
  font-size: 1.1rem;
  color: #fff;
}

.stats-strip span {
  font-size: 0.78rem;
  color: #b8c7ed;
}

.view-card {
  padding: 14px;
  display: grid;
  gap: 12px;
}

.spotlight {
  grid-template-columns: minmax(260px, 38%) minmax(0, 1fr);
  align-items: stretch;
  overflow: hidden;
}

.spotlight-cover {
  border-radius: 12px;
  background-size: cover;
  background-position: center;
  min-height: 220px;
  position: relative;
}

.spotlight-cover::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(5, 7, 17, 0.75));
}

.spotlight-content h2 {
  margin: 2px 0;
  font-family: "Sora", sans-serif;
}

.inline-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.badge {
  display: inline-flex;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  padding: 2px 9px;
  font-size: 0.72rem;
  color: #dbe7ff;
}

.spotlight-actions {
  display: flex;
  gap: 8px;
  margin-top: 6px;
}

.controls {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 190px 190px;
  gap: 10px;
}

.input {
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.06);
  color: #eef3ff;
  padding: 9px 11px;
  font-family: "Sora", sans-serif;
}

.tournament-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 12px;
}

.tournament-card {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.03);
}

.tournament-card.selected {
  border-color: #ff6f8b;
}

.thumb {
  height: 130px;
  background-size: cover;
  background-position: center;
}

.card-body {
  padding: 10px;
  display: grid;
  gap: 6px;
}

.card-body h3 {
  margin: 0;
  font-family: "Sora", sans-serif;
  font-size: 0.96rem;
}

.card-body p {
  margin: 0;
  font-size: 0.84rem;
  color: #bbcaef;
  min-height: 2.3em;
}

.section-head h2 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.section-head p {
  margin: 2px 0 0;
  color: #b8c7ed;
  font-size: 0.9rem;
}

.rank-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.rank-chip {
  min-width: 85px;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 10px;
  padding: 7px;
  display: grid;
  place-items: center;
  gap: 4px;
  font-size: 0.74rem;
}

.rank-chip img {
  width: 40px;
  height: 40px;
}

.table-wrap {
  overflow: auto;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  text-align: left;
}

.table th {
  font-size: 0.82rem;
  color: #b8c7ed;
}

.table tr.me {
  background: rgba(255, 110, 145, 0.16);
}

.rank-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tiny-rank {
  width: 26px;
  height: 26px;
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

.list {
  display: grid;
  gap: 8px;
}

.list-row {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.list-row p {
  margin: 2px 0 0;
  color: #b8c7ed;
  font-size: 0.85rem;
}

.builder {
  display: grid;
  gap: 9px;
}

.split-2 {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.check {
  display: inline-flex;
  gap: 8px;
  align-items: center;
}

.battle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 12px;
}

.battle-tile {
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 12px;
  padding: 10px;
  display: grid;
  gap: 8px;
  background: rgba(255, 255, 255, 0.03);
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
  font-size: 0.82rem;
  color: #b8c7ed;
}

.duel-actions {
  display: flex;
  gap: 8px;
}

.admin-box {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 12px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  display: grid;
  gap: 8px;
}

.admin-box h3 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.mini-list {
  display: grid;
  gap: 8px;
}

.tier-edit {
  display: grid;
  grid-template-columns: 1fr 120px 120px;
  gap: 8px;
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
  width: min(760px, 92vw);
  max-height: 84vh;
  overflow-y: auto;
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.14), rgba(112, 231, 255, 0.08));
}

.modal-card header {
  padding: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.14);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.modal-body {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.profile-hero {
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
}

.hero-rank {
  width: 56px;
  height: 56px;
}

.chips {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 8px;
}

.chip {
  border: 1px solid rgba(255, 255, 255, 0.14);
  border-radius: 10px;
  padding: 10px;
  background: rgba(255, 255, 255, 0.03);
  display: grid;
  gap: 3px;
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

.empty {
  padding: 20px;
  text-align: center;
  color: #b8c7ed;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  border-radius: 12px;
}

@media (max-width: 980px) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .spotlight {
    grid-template-columns: 1fr;
  }

  .controls {
    grid-template-columns: 1fr;
  }

  .split-2 {
    grid-template-columns: 1fr;
  }

  .tier-edit {
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
