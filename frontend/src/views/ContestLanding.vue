<template>
  <div class="arena-page">
    <div class="ambient-bg"></div>

    <header class="top-shell">
      <div class="topbar">
        <div class="brand-block">
          <p class="eyebrow">UNYQ COMPETITIVE MODE</p>
          <h1>Tournament Arena</h1>
          <p class="subtitle">Turniere, Battles und Ranks in einer sauberen, lesbaren Oberfläche.</p>
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
      </div>

      <nav class="main-tabs" aria-label="Turnier Navigation">
        <button
          v-for="tab in tabOptions"
          :key="tab.key"
          class="tab-pill"
          :class="{ active: activeTab === tab.key }"
          @click="selectMainTab(tab.key)"
        >
          {{ tab.label }}
        </button>
      </nav>
    </header>

    <section class="stats-strip">
      <article class="stat-card">
        <span class="stat-label">Turniere</span>
        <strong>{{ tournaments.length }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Battles</span>
        <strong>{{ battles.length }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Ranked Profiles</span>
        <strong>{{ topRankedRows.length }}</strong>
      </article>
      <article class="stat-card">
        <span class="stat-label">Dein Rank</span>
        <strong>#{{ myRankedRow?.rank || '-' }}</strong>
      </article>
    </section>

    <template v-if="activeTab === 'tournaments'">
      <section class="view-card spotlight" v-if="featuredTournament">
        <div class="spotlight-cover" :style="{ backgroundImage: `url(${tournamentCover(featuredTournament)})` }"></div>
        <div class="spotlight-content">
          <p class="eyebrow">FEATURED TOURNAMENT</p>
          <h2>{{ featuredTournament.title }}</h2>
          <p class="spotlight-copy">{{ featuredTournament.description || "Bereit fuer die naechste Runde." }}</p>
          <div class="inline-tags">
            <span class="badge">{{ statusLabel(featuredTournament.status) }}</span>
            <span v-if="featuredTournament.is_no_loss" class="badge">No Loss</span>
            <span v-if="featuredTournament.is_recurring" class="badge">Recurring</span>
          </div>
          <div class="spotlight-actions">
            <button class="btn" @click="openTournamentDetail(featuredTournament)">Turnier oeffnen</button>
            <button class="btn ghost" @click="selectTournament(nextFeaturedId)">Naechstes</button>
          </div>
        </div>
      </section>

      <section class="view-card">
        <div class="section-head compact">
          <h2>Turniere entdecken</h2>
          <p>Filter, sortieren und direkt in den Tournament-Flow springen.</p>
        </div>

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
          <p>Einladende Rangauswertung mit Podium und klaren Spielerwerten.</p>
        </div>

        <div class="rank-row" v-if="rankedOverview.tiers?.length">
          <article v-for="tier in rankedOverview.tiers" :key="tier.key" class="rank-chip">
            <img :src="rankArtwork(tier.key)" :alt="tier.label" />
            <span>{{ tier.label }}</span>
          </article>
        </div>

        <div v-if="topRankedRows.length" class="podium-grid">
          <article
            v-for="row in podiumRows"
            :key="`podium-${row.profile_id}`"
            class="podium-card"
            :class="[`place-${row.rank}`]"
          >
            <span class="podium-rank">#{{ row.rank }}</span>
            <img class="podium-rank-art" :src="rankArtwork(row.tier?.key)" :alt="row.tier?.label || 'Tier'" />
            <button class="link-btn podium-name" @click="openBattleProfileByRow(row)">{{ row.name }}</button>
            <p>{{ row.ranked_points || 0 }} RP</p>
          </article>
        </div>

        <div class="leaderboard-list" v-if="topRankedRows.length">
          <article
            v-for="row in topRankedRows"
            :key="`row-${row.profile_id}`"
            class="leaderboard-row"
            :class="{ me: row.profile_id === myProfileId }"
          >
            <div class="leader-left">
              <span class="rank-pill">#{{ row.rank }}</span>
              <img class="tiny-rank" :src="rankArtwork(row.tier?.key)" :alt="row.tier?.label || 'Tier'" />
              <div class="leader-name">
                <button class="link-btn" @click="openBattleProfileByRow(row)">{{ row.name }}</button>
                <small>{{ row.tier?.label || 'Unranked' }}</small>
              </div>
            </div>
            <div class="leader-stats">
              <span class="stat-pill"><strong>{{ row.ranked_points || 0 }}</strong><em>RP</em></span>
              <span class="stat-pill"><strong>{{ row.wins || 0 }}</strong><em>Wins</em></span>
              <span class="stat-pill"><strong>{{ winRate(row) }}</strong><em>Winrate</em></span>
              <span class="stat-pill"><strong>{{ row.battles || 0 }}</strong><em>Battles</em></span>
            </div>
          </article>
        </div>
        <div v-else class="empty">Noch keine Ranked-Daten verfuegbar.</div>
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
        <button class="btn ghost" @click="showCreateForm = !showCreateForm">{{ showCreateForm ? 'Form schliessen' : 'Neues Turnier' }}</button>
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
        <div v-else class="empty">Keine Battles verfuegbar.</div>
      </section>
    </template>

    <template v-if="activeTab === 'admin' && viewerIsTeam">
      <section class="view-card">
        <div class="section-head">
          <h2>Admin Tools</h2>
          <p>Ranked Rules und Utility-Tools fuer Team-Mitglieder.</p>
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
            <button class="btn ghost" @click="goAnimationLab">Animation Lab oeffnen</button>
          </div>
        </div>
      </section>
    </template>

    <div v-if="selectedBattleProfile" class="modal-overlay" @click.self="selectedBattleProfile = null">
      <article class="modal-card">
        <header>
          <h2>{{ selectedBattleProfile.name }}</h2>
          <button class="btn ghost small" @click="selectedBattleProfile = null">X</button>
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
            <p v-else class="muted">Keine Achievements verfuegbar.</p>
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
const podiumRows = computed(() => topRankedRows.value.filter((row) => Number(row.rank || 0) > 0).slice(0, 3));
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

function winRate(row) {
  const battlesCount = Number(row?.battles || 0);
  if (!battlesCount) return "0%";
  const wins = Number(row?.wins || 0);
  return `${Math.round((wins / battlesCount) * 100)}%`;
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
@import url("https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;700&display=swap");

.arena-page {
  --arena-bg: #f5f7fb;
  --arena-bg-elev: #ffffff;
  --arena-text: #142033;
  --arena-muted: #5a6a82;
  --arena-border: #d7deea;
  --arena-accent: #ff6a3d;
  --arena-accent-2: #ff8c3a;
  --arena-chip: #eef2fa;
  --arena-shadow: 0 12px 34px rgba(17, 26, 48, 0.08);
  min-height: 100vh;
  width: 100vw;
  margin-left: calc(50% - 50vw);
  --arena-gutter: clamp(14px, 2vw, 34px);
  padding: 0 var(--arena-gutter) 46px;
  position: relative;
  color: var(--arena-text);
  font-family: "Manrope", sans-serif;
  display: grid;
  gap: 16px;
  background: var(--arena-bg);
}

@media (prefers-color-scheme: dark) {
  .arena-page {
    --arena-bg: #090f1f;
    --arena-bg-elev: #121b2f;
    --arena-text: #ebf0ff;
    --arena-muted: #aab6cf;
    --arena-border: #2a3754;
    --arena-accent: #ff7e59;
    --arena-accent-2: #ffb347;
    --arena-chip: #1d2943;
    --arena-shadow: 0 14px 36px rgba(0, 0, 0, 0.36);
  }
}

.ambient-bg {
  position: fixed;
  inset: 0;
  z-index: -2;
  background:
    radial-gradient(circle at 8% 8%, rgba(255, 146, 75, 0.2), transparent 38%),
    radial-gradient(circle at 88% 18%, rgba(93, 203, 255, 0.22), transparent 36%),
    radial-gradient(circle at 42% 92%, rgba(255, 196, 123, 0.18), transparent 46%);
}

.view-card,
.stat-card {
  border: 1px solid var(--arena-border);
  border-radius: 16px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--arena-bg-elev) 96%, white 4%), var(--arena-bg-elev));
  box-shadow: var(--arena-shadow);
}

.top-shell {
  margin-left: calc(-1 * var(--arena-gutter));
  margin-right: calc(-1 * var(--arena-gutter));
  border-bottom: 1px solid var(--arena-border);
  background:
    linear-gradient(180deg, color-mix(in srgb, var(--arena-bg-elev) 93%, white 7%), var(--arena-bg-elev)),
    linear-gradient(120deg, color-mix(in srgb, var(--arena-accent) 10%, transparent), transparent 40%);
  padding: 18px var(--arena-gutter) 10px;
  display: grid;
  gap: 10px;
}

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
}

.brand-block {
  display: grid;
  gap: 4px;
}

.brand-block h1 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: clamp(1.4rem, 2.4vw, 2.15rem);
  letter-spacing: -0.01em;
}

.subtitle {
  margin: 0;
  color: var(--arena-muted);
  font-size: 0.92rem;
}

.eyebrow {
  margin: 0;
  font-size: 0.68rem;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: color-mix(in srgb, var(--arena-accent) 66%, var(--arena-text) 34%);
  font-weight: 800;
}

.topbar-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: 1px solid color-mix(in srgb, var(--arena-border) 70%, var(--arena-text) 30%);
  background: linear-gradient(135deg, var(--arena-accent), var(--arena-accent-2));
  color: #fff;
  font-weight: 800;
  cursor: pointer;
}

.main-tabs {
  display: flex;
  flex-wrap: nowrap;
  overflow-x: auto;
  gap: 8px;
  padding-top: 2px;
  scrollbar-width: thin;
}

.tab-pill {
  border: 1px solid var(--arena-border);
  background: var(--arena-chip);
  color: var(--arena-text);
  border-radius: 999px;
  padding: 6px 12px;
  min-height: 34px;
  cursor: pointer;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 600;
  font-size: 0.84rem;
  white-space: nowrap;
}

.tab-pill.active {
  background: linear-gradient(125deg, var(--arena-accent), var(--arena-accent-2));
  border-color: transparent;
  color: #fff;
}

.stats-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin-top: 2px;
}

.stat-card {
  padding: 12px 14px;
  display: grid;
  gap: 2px;
}

.stat-card strong {
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.25rem;
}

.stat-label {
  font-size: 0.78rem;
  color: var(--arena-muted);
}

.view-card {
  padding: 16px;
  display: grid;
  gap: 14px;
}

.section-head {
  display: grid;
  gap: 2px;
}

.section-head.compact {
  margin-bottom: 2px;
}

.section-head h2 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.24rem;
}

.section-head p {
  margin: 0;
  color: var(--arena-muted);
}

.spotlight {
  grid-template-columns: minmax(300px, 40%) minmax(0, 1fr);
  align-items: stretch;
  overflow: hidden;
  gap: 0;
  padding: 0;
}

.spotlight-cover {
  background-size: cover;
  background-position: center;
  min-height: 250px;
  position: relative;
}

.spotlight-cover::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 36%, rgba(0, 0, 0, 0.48));
}

.spotlight-content {
  padding: 18px;
  display: grid;
  gap: 10px;
}

.spotlight-content h2 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
}

.spotlight-copy {
  margin: 0;
  color: var(--arena-muted);
  line-height: 1.5;
}

.inline-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.badge {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--arena-border);
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 0.76rem;
  color: var(--arena-text);
  background: var(--arena-chip);
}

.spotlight-actions {
  display: flex;
  gap: 8px;
  margin-top: 2px;
}

.controls {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 200px 200px;
  gap: 10px;
}

.input {
  border-radius: 11px;
  border: 1px solid var(--arena-border);
  background: var(--arena-bg-elev);
  color: var(--arena-text);
  padding: 9px 11px;
  font-family: "Manrope", sans-serif;
}

.input:focus {
  outline: 2px solid color-mix(in srgb, var(--arena-accent) 52%, transparent);
  outline-offset: 1px;
}

.tournament-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(245px, 1fr));
  gap: 12px;
}

.tournament-card {
  border: 1px solid var(--arena-border);
  border-radius: 14px;
  overflow: hidden;
  cursor: pointer;
  background: var(--arena-bg-elev);
  transition: transform 0.16s ease, border-color 0.16s ease, box-shadow 0.16s ease;
}

.tournament-card:hover {
  transform: translateY(-2px);
  border-color: color-mix(in srgb, var(--arena-accent) 45%, var(--arena-border) 55%);
  box-shadow: 0 12px 20px rgba(18, 30, 56, 0.12);
}

.tournament-card.selected {
  border-color: color-mix(in srgb, var(--arena-accent) 58%, var(--arena-border) 42%);
}

.thumb {
  height: 136px;
  background-size: cover;
  background-position: center;
}

.card-body {
  padding: 12px;
  display: grid;
  gap: 6px;
}

.card-body h3 {
  margin: 0;
  font-family: "Space Grotesk", sans-serif;
  font-size: 1rem;
}

.card-body p {
  margin: 0;
  font-size: 0.88rem;
  color: var(--arena-muted);
  min-height: 2.4em;
}

.rank-row {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 2px;
}

.rank-chip {
  min-width: 98px;
  border: 1px solid var(--arena-border);
  border-radius: 12px;
  padding: 9px;
  display: grid;
  place-items: center;
  gap: 6px;
  font-size: 0.75rem;
  background: var(--arena-chip);
}

.rank-chip img {
  width: 44px;
  height: 44px;
}

.podium-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.podium-card {
  border: 1px solid var(--arena-border);
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(180deg, color-mix(in srgb, var(--arena-accent) 8%, var(--arena-bg-elev) 92%), var(--arena-bg-elev));
  display: grid;
  gap: 5px;
  justify-items: center;
}

.podium-card.place-1 {
  background: linear-gradient(180deg, rgba(255, 191, 70, 0.24), var(--arena-bg-elev));
}

.podium-card.place-2 {
  background: linear-gradient(180deg, rgba(173, 188, 207, 0.27), var(--arena-bg-elev));
}

.podium-card.place-3 {
  background: linear-gradient(180deg, rgba(200, 150, 100, 0.26), var(--arena-bg-elev));
}

.podium-rank {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 40px;
  height: 26px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--arena-accent) 16%, var(--arena-bg-elev) 84%);
  border: 1px solid var(--arena-border);
  font-weight: 800;
  font-family: "Space Grotesk", sans-serif;
}

.podium-rank-art {
  width: 66px;
  height: 66px;
}

.podium-name {
  font-weight: 700;
  font-size: 0.94rem;
}

.podium-card p {
  margin: 0;
  color: var(--arena-muted);
}

.leaderboard-list {
  display: grid;
  gap: 8px;
}

.leaderboard-row {
  border: 1px solid var(--arena-border);
  border-radius: 12px;
  padding: 10px;
  background: var(--arena-bg-elev);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.leaderboard-row.me {
  border-color: color-mix(in srgb, var(--arena-accent) 52%, var(--arena-border) 48%);
  background: color-mix(in srgb, var(--arena-accent) 8%, var(--arena-bg-elev) 92%);
}

.leader-left {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.rank-pill {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 42px;
  height: 30px;
  border-radius: 999px;
  background: var(--arena-chip);
  border: 1px solid var(--arena-border);
  font-weight: 800;
}

.tiny-rank {
  width: 34px;
  height: 34px;
}

.leader-name {
  display: grid;
  min-width: 0;
}

.leader-name small {
  color: var(--arena-muted);
}

.leader-stats {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.stat-pill {
  border: 1px solid var(--arena-border);
  border-radius: 999px;
  padding: 4px 10px;
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  background: var(--arena-chip);
}

.stat-pill strong {
  font-family: "Space Grotesk", sans-serif;
}

.stat-pill em {
  font-style: normal;
  font-size: 0.73rem;
  color: var(--arena-muted);
}

.link-btn {
  border: 0;
  background: transparent;
  color: color-mix(in srgb, var(--arena-accent) 72%, var(--arena-text) 28%);
  font: inherit;
  padding: 0;
  cursor: pointer;
  text-decoration: none;
  font-weight: 700;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.list {
  display: grid;
  gap: 8px;
}

.list-row {
  border: 1px solid var(--arena-border);
  border-radius: 12px;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
  background: var(--arena-bg-elev);
}

.list-row p {
  margin: 3px 0 0;
  color: var(--arena-muted);
  font-size: 0.88rem;
}

.builder,
.mini-list,
.history,
.modal-body {
  display: grid;
  gap: 10px;
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

.battle-tile,
.admin-box,
.chip,
.history-row,
.profile-hero {
  border: 1px solid var(--arena-border);
  border-radius: 12px;
  background: var(--arena-bg-elev);
}

.battle-tile {
  padding: 10px;
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
  font-size: 0.83rem;
  color: var(--arena-muted);
}

.duel-actions {
  display: flex;
  gap: 8px;
}

.admin-box {
  padding: 12px;
}

.admin-box h3 {
  margin: 0 0 8px;
  font-family: "Space Grotesk", sans-serif;
}

.tier-edit {
  display: grid;
  grid-template-columns: 1fr 120px 120px;
  gap: 8px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(5, 8, 16, 0.6);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-card {
  width: min(760px, 92vw);
  max-height: 84vh;
  overflow-y: auto;
  border: 1px solid var(--arena-border);
  border-radius: 18px;
  background: var(--arena-bg-elev);
  box-shadow: var(--arena-shadow);
}

.modal-card header {
  padding: 16px;
  border-bottom: 1px solid var(--arena-border);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.profile-hero {
  grid-template-columns: auto 1fr;
  gap: 12px;
  padding: 10px;
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

.chip,
.history-row {
  padding: 10px;
}

.chip {
  display: grid;
  gap: 3px;
}

.history-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}

.history-row span,
.muted {
  color: var(--arena-muted);
  font-size: 0.86rem;
}

.btn {
  border: 1px solid transparent;
  border-radius: 10px;
  background: linear-gradient(125deg, var(--arena-accent), var(--arena-accent-2));
  color: #fff;
  font-family: "Space Grotesk", sans-serif;
  font-weight: 700;
  padding: 8px 12px;
  cursor: pointer;
}

.btn.ghost {
  background: transparent;
  border-color: var(--arena-border);
  color: var(--arena-text);
}

.btn.small {
  padding: 6px 10px;
  font-size: 0.82rem;
}

.empty {
  padding: 20px;
  text-align: center;
  color: var(--arena-muted);
  border: 1px dashed var(--arena-border);
  border-radius: 12px;
  background: color-mix(in srgb, var(--arena-chip) 55%, transparent);
}

@media (max-width: 1100px) {
  .stats-strip {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .spotlight {
    grid-template-columns: 1fr;
  }

  .podium-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 920px) {
  .top-shell {
    padding-top: 14px;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }

  .controls,
  .split-2,
  .tier-edit {
    grid-template-columns: 1fr;
  }

  .leaderboard-row {
    flex-direction: column;
    align-items: flex-start;
  }

  .leader-stats {
    justify-content: flex-start;
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
