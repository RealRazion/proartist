<template>
  <div class="tournament-page">
    <div class="arena-bg-layer"></div>

    <section class="contest-toolbar">
      <div class="toolbar-nav">
        <p>Contest Navigation</p>
        <select class="rail-select" v-model="selectedNavTarget" @change="jumpToSection(selectedNavTarget)">
          <option v-for="entry in navTargets" :key="`nav-${entry.key}`" :value="entry.key">{{ entry.label }}</option>
        </select>
        <div class="toolbar-pills">
          <button v-for="entry in navTargets" :key="entry.key" class="nav-pill" type="button" @click="jumpToSection(entry.key)">
            {{ entry.label }}
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

    <header class="arena-hero">
      <div class="hero-left">
        <p class="eyebrow">UNYQ Arena Mode</p>
        <h1>Battle Royale fuer Musik-Creator</h1>
        <p>
          Keine Office-Plattform. Keine 200 Fenster. Eine Arena mit Fokus auf Matches,
          Ranks und Live-Feeling.
        </p>
        <p v-if="artistPreview" class="preview-badge">Artist View aktiv – Admin Controls sind ausgeblendet.</p>
      </div>
      <div class="hero-right">
        <div class="hero-stat"><strong>{{ tournaments.length }}</strong><span>Turniere</span></div>
        <div class="hero-stat"><strong>{{ battles.length }}</strong><span>Battles</span></div>
        <div class="hero-stat"><strong>{{ topRankedRows.length }}</strong><span>Im Ranking</span></div>
      </div>

      <div class="hero-progress" id="rank-progress">
        <div class="hero-progress-head">
          <strong>{{ rankProgress.currentTier }}</strong>
          <span v-if="rankProgress.nextTier">Noch {{ rankProgress.remaining }} RP bis {{ rankProgress.nextTier }}</span>
          <span v-else>Max Rank erreicht</span>
        </div>
        <div class="hero-progress-track">
          <span class="hero-progress-fill" :style="{ width: `${rankProgress.percent}%` }"></span>
        </div>
        <small>{{ rankProgress.points }} RP</small>
      </div>
    </header>

    <section class="arena-slideshow" id="turniere" v-if="visibleTournaments.length">
      <button class="slide-arrow left" type="button" @click="prevTournament" aria-label="Vorheriges Turnier">&#10094;</button>

      <article class="tournament-slide" :style="{ '--slide-image': `url(${tournamentCover(featuredTournament)})` }">
        <div class="slide-content">
          <p class="eyebrow">Aktuelles Turnier</p>
          <h2>{{ featuredTournament.title }}</h2>
          <p>{{ featuredTournament.description || "Bereit fuer die naechste Runde." }}</p>
          <div class="stage-tags">
            <span class="tag">{{ statusLabel(featuredTournament.status) }}</span>
            <span class="tag" v-if="featuredTournament.is_no_loss">No Loss</span>
            <span class="tag" v-if="featuredTournament.is_recurring">Recurring</span>
          </div>
        </div>
      </article>

      <button class="slide-arrow right" type="button" @click="nextTournament" aria-label="Nächstes Turnier">&#10095;</button>
    </section>

    <section class="rank-emblems" v-if="rankedOverview.tiers?.length">
      <article
        v-for="tier in rankedOverview.tiers"
        :key="tier.key"
        class="emblem-card"
        :class="`tier-${(tier.key || 'BRONZE').toLowerCase()}`"
      >
        <img :src="rankArtwork(tier.key)" :alt="`${tier.label} emblem`" />
        <div>
          <strong>{{ tier.label }}</strong>
        </div>
      </article>
    </section>

    <section class="arena-main" id="aktuelle-battles" v-if="featuredTournament">
      <article class="arena-stage">
        <div class="stage-head">
          <h2>{{ featuredTournament.title }}</h2>
          <div class="stage-tags">
            <span class="tag">{{ statusLabel(featuredTournament.status) }}</span>
            <span class="tag" v-if="featuredTournament.is_no_loss">No Loss</span>
            <span class="tag" v-if="featuredTournament.is_recurring">
              Recurring {{ recurrenceLabel(featuredTournament.recurrence_type) }}
            </span>
          </div>
        </div>

        <p class="stage-desc">{{ featuredTournament.description || 'Bereit fuer die naechste Runde.' }}</p>

        <div class="battle-feed">
          <div v-if="battlesFor(featuredTournament.id).length === 0" class="empty-inline">Noch keine Live-Battles.</div>
          <article class="battle-duel" v-for="battle in battlesFor(featuredTournament.id)" :key="`duel-${battle.id}`">
            <div class="duel-player left">{{ battle.left_profile_name }}</div>
            <div class="duel-center">
              <strong>{{ battle.votes_left }} : {{ battle.votes_right }}</strong>
              <span>Runde {{ battle.round_number }}</span>
            </div>
            <div class="duel-player right">{{ battle.right_profile_name }}</div>
            <div class="duel-actions" v-if="!viewerIsTeam">
              <button class="btn vote-btn" @click="voteBattle(featuredTournament, battle, battle.left_submission)" :disabled="!canVoteBattle(featuredTournament, battle)">Left</button>
              <button class="btn ghost vote-btn" @click="voteBattle(featuredTournament, battle, battle.right_submission)" :disabled="!canVoteBattle(featuredTournament, battle)">Right</button>
            </div>
            <div class="duel-actions" v-if="viewerIsTeam && battle.status !== 'CLOSED'">
              <button class="btn small" @click="closeBattle(featuredTournament, battle)">Auto Close</button>
              <button class="btn ghost small" @click="closeBattle(featuredTournament, battle, battle.left_submission)">Left Win</button>
              <button class="btn ghost small" @click="closeBattle(featuredTournament, battle, battle.right_submission)">Right Win</button>
            </div>
          </article>
        </div>

        <div class="quick-actions" v-if="!viewerIsTeam && featuredTournament.has_application_phase && !myApplication(featuredTournament.id)">
          <textarea v-model.trim="applicationDrafts[featuredTournament.id]" rows="2" placeholder="Kurze Bewerbung"></textarea>
          <button class="btn" @click="submitApplication(featuredTournament.id)" :disabled="busy">Jetzt bewerben</button>
        </div>

        <div class="quick-actions" v-if="!viewerIsTeam">
          <input v-model.trim="submissionDraft(featuredTournament.id).title" placeholder="Track / Runde Titel" />
          <input v-model.trim="submissionDraft(featuredTournament.id).media_url" placeholder="https://media-link" />
          <button class="btn" @click="submitRound(featuredTournament.id)" :disabled="busy || !canSubmit(featuredTournament)">Runde einreichen</button>
        </div>

        <div class="quick-actions" v-if="viewerIsTeam">
          <button class="btn ghost" @click="setTournamentStatus(featuredTournament, 'APPLICATION_OPEN')">Applications</button>
          <button class="btn ghost" @click="setTournamentStatus(featuredTournament, 'SUBMISSION_OPEN')">Submissions</button>
          <button class="btn ghost" @click="setTournamentStatus(featuredTournament, 'BATTLES')">Battle Live</button>
          <button class="btn" @click="setTournamentStatus(featuredTournament, 'CLOSED')">Close Tournament</button>
        </div>
      </article>

      <aside class="arena-side" id="rank">
        <section class="side-block ladder">
          <h3>Top Ladder</h3>
          <article class="ladder-row" v-for="row in topRankedRows.slice(0, 6)" :key="`ladder-${row.profile_id}`">
            <img class="ladder-rank-art" :src="rankArtwork(row.tier?.key)" :alt="row.tier?.label" />
            <div>
              <strong>#{{ row.rank }} {{ row.name }}</strong>
              <span>{{ row.ranked_points }} RP</span>
            </div>
          </article>
        </section>

        <section class="side-block timeline" id="historie">
          <h3>Timeline</h3>
          <article class="timeline-row live" v-for="event in timelineCurrent.slice(0, 3)" :key="`live-${event.id}`">
            <strong>{{ event.title }}</strong>
            <span>{{ formatDateTime(event.date) }}</span>
          </article>
          <article class="timeline-row upcoming" v-for="event in timelineUpcoming.slice(0, 4)" :key="`up-${event.id}`">
            <strong>{{ event.title }}</strong>
            <span>{{ formatDateTime(event.date) }}</span>
          </article>
        </section>

        <section class="side-block profile" id="meine-turniere" v-if="!viewerIsTeam">
          <h3>Mein Fortschritt</h3>
          <p v-if="myRankedRow">{{ myRankedRow.tier?.label }} • #{{ myRankedRow.rank }} • {{ myRankedRow.ranked_points }} RP</p>
          <p v-else>Noch kein Ladder-Eintrag.</p>
        </section>

        <section class="side-block admin" v-if="viewerIsTeam">
          <h3>Admin Tools</h3>
          <button class="btn" @click="goAnimationLab">Animation Lab</button>
          <button class="btn ghost" @click="showCreateForm = !showCreateForm">{{ showCreateForm ? 'Hide' : 'Show' }} Create</button>
          <button class="btn ghost" @click="saveRankedConfig" :disabled="busy">Save Ranked Rules</button>
        </section>
      </aside>
    </section>

    <section class="admin-overlay" v-if="viewerIsTeam && showCreateForm">
      <article class="overlay-card">
        <header>
          <h3>Turnier Builder</h3>
          <button class="btn ghost small" @click="showCreateForm = false">Close</button>
        </header>
        <form class="overlay-form" @submit.prevent="createTournament">
          <input v-model.trim="createForm.title" required maxlength="200" placeholder="Turnier Titel" />
          <textarea v-model.trim="createForm.description" rows="2" placeholder="Beschreibung"></textarea>
          <div class="overlay-grid">
            <select v-model="createForm.status">
              <option value="DRAFT">Entwurf</option>
              <option value="APPLICATION_OPEN">Bewerbung offen</option>
              <option value="SUBMISSION_OPEN">Einreichung offen</option>
              <option value="BATTLES">Battles</option>
              <option value="CLOSED">Geschlossen</option>
            </select>
            <select v-model="createForm.voting_mode">
              <option value="COMMUNITY">Community</option>
              <option value="HYBRID">Hybrid</option>
              <option value="JURY_ONLY">Jury</option>
            </select>
            <input v-model="createForm.starts_at" type="datetime-local" />
            <input v-model="createForm.ends_at" type="datetime-local" />
            <input v-model="createForm.next_starts_at" type="datetime-local" :disabled="!createForm.is_recurring" />
            <select v-model="createForm.recurrence_type" :disabled="!createForm.is_recurring">
              <option value="NONE">Keine</option>
              <option value="WEEKLY">Woechentlich</option>
              <option value="MONTHLY">Monatlich</option>
              <option value="QUARTERLY">Quartalsweise</option>
            </select>
          </div>
          <div class="overlay-switches">
            <label><input v-model="createForm.has_application_phase" type="checkbox" /> Bewerbung</label>
            <label><input v-model="createForm.is_no_loss" type="checkbox" /> No Loss</label>
            <label><input v-model="createForm.is_recurring" type="checkbox" /> Recurring</label>
            <label><input v-model="createForm.allow_vote_change" type="checkbox" /> Vote Change</label>
          </div>
          <button class="btn" type="submit" :disabled="busy">Publish Tournament</button>
        </form>
      </article>
    </section>

    <section class="empty-state" v-if="!featuredTournament">
      <span class="empty-icon">🎮</span>
      <p>Keine Turniere aktiv. Als Team kannst du direkt eins erstellen.</p>
    </section>
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

const busy = ref(false);
const showCreateForm = ref(false);
const tournaments = ref([]);
const applications = ref([]);
const submissions = ref([]);
const battles = ref([]);
const myVotes = ref([]);
const rankedOverview = ref({});
const timelineCurrent = ref([]);
const timelineUpcoming = ref([]);
const rankConfigSeason = ref({});
const rankConfigTiers = ref([]);
const tournamentSearch = ref("");
const statusFilter = ref("ALL");
const sortMode = ref("open-first");
const selectedTournamentId = ref(null);
const selectedNavTarget = ref("turniere");

const navTargets = [
  { key: "turniere", label: "Turniere" },
  { key: "meine-turniere", label: "Meine Turniere" },
  { key: "historie", label: "Historie" },
  { key: "aktuelle-battles", label: "Aktuelle Battles" },
  { key: "rank", label: "Rank" },
];

const fallbackTournamentCovers = [
  "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1571330735066-03aaa9429d89?auto=format&fit=crop&w=1200&q=80",
  "https://images.unsplash.com/photo-1516450360452-9312f5e86fc7?auto=format&fit=crop&w=1200&q=80",
];

const applicationDrafts = ref({});
const submissionDrafts = ref({});
const phoneDrafts = ref({});

const createForm = ref({
  title: "",
  description: "",
  has_application_phase: true,
  application_deadline: "",
  submission_deadline: "",
  starts_at: "",
  ends_at: "",
  status: "DRAFT",
  voting_mode: "COMMUNITY",
  allow_vote_change: true,
  min_account_age_hours: 0,
  max_votes_per_ip_per_hour: 20,
  require_phone_vote_verification: false,
  is_no_loss: false,
  is_recurring: false,
  recurrence_type: "NONE",
  recurrence_interval: 1,
  next_starts_at: "",
});

const myProfileId = computed(() => profile.value?.id || null);
const artistPreview = computed(() => isTeam.value && String(route.query.artistView || "").toLowerCase() === "1");
const viewerIsTeam = computed(() => isTeam.value && !artistPreview.value);
const profileInitial = computed(() => {
  const source = profile.value?.name || profile.value?.username || "";
  return source ? source.trim().charAt(0).toUpperCase() : "U";
});
const rankedRows = computed(() => rankedOverview.value?.rows || []);
const topRankedRows = computed(() => rankedRows.value.slice(0, 12));
const rankDistribution = computed(() => rankedOverview.value?.rank_distribution || {});
const myRankedRow = computed(() => rankedRows.value.find((row) => row.profile_id === myProfileId.value) || null);

const rankProgress = computed(() => {
  const points = Number(myRankedRow.value?.ranked_points || 0);
  const tiers = asList(rankedOverview.value?.tiers || [])
    .slice()
    .sort((a, b) => Number(a.min_points || 0) - Number(b.min_points || 0));

  if (!tiers.length) {
    return {
      points,
      percent: 0,
      currentTier: "Unranked",
      nextTier: null,
      remaining: 0,
    };
  }

  let current = tiers[0];
  let next = null;

  for (let idx = 0; idx < tiers.length; idx += 1) {
    const tier = tiers[idx];
    if (points >= Number(tier.min_points || 0)) {
      current = tier;
      next = tiers[idx + 1] || null;
    }
  }

  if (!next) {
    return {
      points,
      percent: 100,
      currentTier: current.label || current.tier_key || "Rank",
      nextTier: null,
      remaining: 0,
    };
  }

  const start = Number(current.min_points || 0);
  const end = Number(next.min_points || start + 1);
  const span = Math.max(end - start, 1);
  const percent = Math.max(0, Math.min(100, Math.round(((points - start) / span) * 100)));

  return {
    points,
    percent,
    currentTier: current.label || current.tier_key || "Rank",
    nextTier: next.label || next.tier_key || "Next",
    remaining: Math.max(end - points, 0),
  };
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
  if (selectedTournamentId.value) {
    const selected = visibleTournaments.value.find((entry) => entry.id === selectedTournamentId.value);
    if (selected) return selected;
  }
  return visibleTournaments.value[0] || null;
});

function asList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || payload || [];
}

function normalizeDateTime(value) {
  if (!value) return null;
  return new Date(value).toISOString();
}

function formatDateTime(value) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "-";
  return parsed.toLocaleString("de-DE", { dateStyle: "short", timeStyle: "short" });
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

function recurrenceLabel(mode) {
  const map = { NONE: "Keine", WEEKLY: "Woche", MONTHLY: "Monat", QUARTERLY: "Quartal" };
  return map[mode] || "Keine";
}

function rankArtwork(tierKey) {
  const key = String(tierKey || "BRONZE").toUpperCase();
  const map = { BRONZE: bronzeRank, SILBER: silberRank, GOLD: goldRank, PLATIN: platinRank, LEGENDAER: legendarRank };
  return map[key] || bronzeRank;
}

function myApplication(tournamentId) {
  return applications.value.find((entry) => entry.tournament === tournamentId && entry.profile?.id === myProfileId.value) || null;
}

function canSubmit(tournament) {
  if (!tournament.has_application_phase) return true;
  const app = myApplication(tournament.id);
  return app?.status === "APPROVED";
}

function submissionDraft(tournamentId) {
  if (!submissionDrafts.value[tournamentId]) {
    submissionDrafts.value[tournamentId] = { round_number: 1, title: "", media_url: "", notes: "" };
  }
  return submissionDrafts.value[tournamentId];
}

function battlesFor(tournamentId) {
  return battles.value.filter((entry) => entry.tournament === tournamentId);
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

function tournamentCover(tournament) {
  if (!tournament) return fallbackTournamentCovers[0];
  if (tournament.cover_url) return tournament.cover_url;
  const index = Math.abs(Number(tournament.id || 0)) % fallbackTournamentCovers.length;
  return fallbackTournamentCovers[index];
}

function nextTournament() {
  if (!visibleTournaments.value.length) return;
  const index = visibleTournaments.value.findIndex((entry) => entry.id === featuredTournament.value?.id);
  const nextIndex = index >= 0 ? (index + 1) % visibleTournaments.value.length : 0;
  selectTournament(visibleTournaments.value[nextIndex].id);
}

function prevTournament() {
  if (!visibleTournaments.value.length) return;
  const index = visibleTournaments.value.findIndex((entry) => entry.id === featuredTournament.value?.id);
  const prevIndex = index >= 0
    ? (index - 1 + visibleTournaments.value.length) % visibleTournaments.value.length
    : 0;
  selectTournament(visibleTournaments.value[prevIndex].id);
}

function jumpToSection(sectionKey) {
  const target = document.getElementById(sectionKey);
  if (!target) {
    showToast("Bereich ist aktuell nicht verfuegbar", "warning");
    return;
  }
  target.scrollIntoView({ behavior: "smooth", block: "start" });
}

function goAnimationLab() {
  router.push({ name: "admin-tournament-animations" });
}

function selectTournament(tournamentId) {
  selectedTournamentId.value = tournamentId;
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
      api.get("tournaments/timeline/"),
      api.get("tournaments/ranked-config/"),
    ];
    if (!viewerIsTeam.value) requests.push(api.get("tournament-votes/"));

    const [tournamentRes, applicationRes, submissionRes, battleRes, rankedRes, timelineRes, rankedConfigRes, votesRes] = await Promise.all(requests);
    tournaments.value = asList(tournamentRes.data);
    applications.value = asList(applicationRes.data);
    submissions.value = asList(submissionRes.data);
    battles.value = asList(battleRes.data);
    rankedOverview.value = rankedRes?.data || {};
    timelineCurrent.value = asList(timelineRes?.data?.current || []);
    timelineUpcoming.value = asList(timelineRes?.data?.upcoming || []);
    rankConfigSeason.value = rankedConfigRes?.data?.season || {};
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

async function closeBattle(tournament, battle, winnerSubmissionId = null) {
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

async function createTournament() {
  if (!isTeam.value) return;
  busy.value = true;
  try {
    await api.post("tournaments/", {
      title: createForm.value.title,
      description: createForm.value.description,
      has_application_phase: createForm.value.has_application_phase,
      application_deadline: normalizeDateTime(createForm.value.application_deadline),
      submission_deadline: normalizeDateTime(createForm.value.submission_deadline),
      starts_at: normalizeDateTime(createForm.value.starts_at),
      ends_at: normalizeDateTime(createForm.value.ends_at),
      status: createForm.value.status,
      voting_mode: createForm.value.voting_mode,
      allow_vote_change: createForm.value.allow_vote_change,
      min_account_age_hours: createForm.value.min_account_age_hours,
      max_votes_per_ip_per_hour: createForm.value.max_votes_per_ip_per_hour,
      require_phone_vote_verification: createForm.value.require_phone_vote_verification,
      is_no_loss: createForm.value.is_no_loss,
      is_recurring: createForm.value.is_recurring,
      recurrence_type: createForm.value.is_recurring ? createForm.value.recurrence_type : "NONE",
      recurrence_interval: createForm.value.is_recurring ? createForm.value.recurrence_interval : 1,
      next_starts_at: createForm.value.is_recurring ? normalizeDateTime(createForm.value.next_starts_at) : null,
    });
    showToast("Turnier erstellt", "success");
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
      season: { duration_months: rankConfigSeason.value.duration_months || 3 },
      tiers: rankConfigTiers.value.map((tier) => ({
        tier_key: tier.tier_key,
        min_points: Number(tier.min_points || 0),
        max_points: tier.max_points === null || tier.max_points === "" ? null : Number(tier.max_points),
        win_points: Number(tier.win_points || 0),
        vote_points: Number(tier.vote_points || 0),
        submission_points: Number(tier.submission_points || 0),
        battle_points: Number(tier.battle_points || 0),
        loss_penalty: Number(tier.loss_penalty || 0),
        max_losses_without_penalty: Number(tier.max_losses_without_penalty || 0),
      })),
    };
    await api.patch("tournaments/ranked-config/", payload);
    showToast("Ranked-Konfiguration gespeichert", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Ranked-Konfiguration fehlgeschlagen", "error");
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

async function setTournamentStatus(tournament, nextStatus) {
  if (!tournament || tournament.status === nextStatus) return;
  busy.value = true;
  try {
    await api.patch(`tournaments/${tournament.id}/`, { status: nextStatus });
    showToast(`Status: ${statusLabel(nextStatus)}`, "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Statusupdate fehlgeschlagen", "error");
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
      round_number: draft.round_number,
      title: draft.title,
      media_url: draft.media_url,
      notes: draft.notes,
    });
    submissionDrafts.value[tournamentId] = { round_number: 1, title: "", media_url: "", notes: "" };
    showToast("Runde eingereicht", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Einreichung fehlgeschlagen", "error");
  } finally {
    busy.value = false;
  }
}

function canVoteBattle(tournament, battle) {
  if (!tournament || !battle) return false;
  if (battle.status === "CLOSED") return false;
  if (tournament.status !== "BATTLES") return false;
  if (tournament.allow_vote_change) return true;
  return !myVotes.value.some((vote) => vote.battle === battle.id);
}

async function voteBattle(tournament, battle, selectedSubmissionId) {
  if (!canVoteBattle(tournament, battle)) {
    showToast("Vote ist fuer diese Battle aktuell nicht moeglich", "warning");
    return;
  }
  busy.value = true;
  try {
    await api.post("tournament-votes/", {
      battle: battle.id,
      selected_submission: selectedSubmissionId,
      phone_number: phoneDrafts.value[battle.id] || "",
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
  padding: 20px clamp(14px, 2vw, 32px) 40px clamp(14px, 2vw, 32px);
  position: relative;
  z-index: 0;
  color: #f2f5ff;
  font-family: "Chakra Petch", sans-serif;
  display: grid;
  gap: 14px;
  overflow: hidden;
}

.arena-bg-layer {
  position: fixed;
  inset: 0;
  z-index: -2;
  background:
    radial-gradient(circle at 8% 8%, rgba(255, 82, 108, 0.34), transparent 40%),
    radial-gradient(circle at 88% 12%, rgba(90, 201, 255, 0.3), transparent 36%),
    radial-gradient(circle at 45% 84%, rgba(255, 191, 71, 0.12), transparent 45%),
    linear-gradient(145deg, #04060f 0%, #0d1530 52%, #120f24 100%);
}

.btn {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 12px;
  background: linear-gradient(125deg, #ff4d6d 0%, #ff7b54 100%);
  color: #fff;
  font-family: "Sora", sans-serif;
  font-weight: 700;
  padding: 10px 14px;
  cursor: pointer;
}

.btn.ghost {
  background: rgba(255, 255, 255, 0.06);
}

.btn.small {
  padding: 7px 11px;
  font-size: 0.82rem;
}

.contest-toolbar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  padding: 14px 16px;
  border: 1px solid rgba(125, 211, 252, 0.18);
  border-radius: 18px;
  background: rgba(7, 12, 28, 0.72);
  backdrop-filter: blur(12px);
}

.toolbar-nav {
  display: grid;
  gap: 10px;
}

.toolbar-nav p {
  margin: 0;
  font-size: 0.78rem;
  color: #9eb2e7;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.toolbar-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.nav-pill {
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  color: #edf2ff;
  padding: 8px 12px;
  font: inherit;
  cursor: pointer;
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.avatar-btn {
  width: 42px;
  height: 42px;
  border-radius: 999px;
  border: 1px solid rgba(125, 211, 252, 0.35);
  background: linear-gradient(135deg, rgba(110, 231, 255, 0.22), rgba(255, 95, 130, 0.28));
  color: #fff;
  font-family: "Sora", sans-serif;
  font-weight: 700;
  cursor: pointer;
}

.arena-left-rail {
  position: fixed;
  left: 18px;
  top: 24px;
  width: 200px;
  z-index: 8;
  border: 1px solid #2f426f;
  border-radius: 14px;
  background: rgba(8, 12, 26, 0.86);
  backdrop-filter: blur(8px);
  padding: 12px;
  display: grid;
  gap: 8px;
}

.arena-left-rail p {
  margin: 0;
  font-size: 0.78rem;
  color: #9eb2e7;
  text-transform: uppercase;
  letter-spacing: 0.12em;
}

.rail-select {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  padding: 10px 14px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.04)),
    rgba(10, 16, 35, 0.88);
  color: #edf2ff;
  min-width: min(320px, 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.arena-hero {
  border: 1px solid #334b84;
  border-radius: 22px;
  padding: 18px;
  background: linear-gradient(145deg, rgba(255, 87, 122, 0.18), rgba(112, 231, 255, 0.12) 45%, rgba(255, 189, 72, 0.08));
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.9fr);
  gap: 16px;
}

.hero-left h1 {
  margin: 6px 0;
  font-family: "Sora", sans-serif;
  font-size: clamp(1.4rem, 2.5vw, 2.2rem);
}

.hero-left p {
  margin: 0;
  color: #b5c1e9;
}

.preview-badge {
  margin-top: 14px !important;
  display: inline-flex;
  align-items: center;
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(8, 12, 26, 0.54);
  border: 1px solid rgba(255, 255, 255, 0.14);
  color: #fef3c7 !important;
}

.eyebrow {
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #7dd3fc;
  font-size: 0.72rem;
}

.hero-right {
  display: grid;
  grid-template-columns: repeat(3, minmax(90px, 1fr));
  gap: 8px;
  align-content: start;
}

.hero-stat {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 12px;
  padding: 8px;
  background: rgba(6, 10, 26, 0.45);
  display: grid;
}

.hero-stat strong {
  font-family: "Sora", sans-serif;
  font-size: 1rem;
}

.hero-stat span {
  font-size: 0.74rem;
  color: #a9b7de;
}

.hero-progress {
  grid-column: 2;
  display: grid;
  gap: 6px;
  align-self: start;
  border: 1px solid rgba(255, 255, 255, 0.16);
  border-radius: 18px;
  background: rgba(6, 10, 26, 0.48);
  padding: 14px;
}

.hero-progress-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.hero-progress-head strong {
  font-family: "Sora", sans-serif;
}

.hero-progress-head span,
.hero-progress small {
  color: #adc0ec;
  font-size: 0.82rem;
}

.hero-progress-track {
  width: 100%;
  height: 10px;
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.28);
  background: rgba(6, 10, 26, 0.65);
}

.hero-progress-fill {
  display: block;
  height: 100%;
  width: 0;
  background: linear-gradient(90deg, #ff5f82, #ffd166 55%, #6ee7ff);
  transition: width 0.3s ease;
}

.arena-slideshow {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
}

.slide-arrow {
  width: 56px;
  height: 84px;
  border: 1px solid #3a4f8c;
  border-radius: 14px;
  background: rgba(8, 12, 26, 0.8);
  color: #f8fbff;
  font-size: 2rem;
  cursor: pointer;
}

.tournament-slide {
  position: relative;
  min-height: 380px;
  max-width: 380px;
  width: 100%;
  margin: 0 auto;
  border-radius: 24px;
  border: 1px solid #3c548f;
  overflow: hidden;
  box-shadow: 0 20px 50px rgba(3, 5, 14, 0.45);
}

.tournament-slide::before {
  content: "";
  position: absolute;
  inset: -18px;
  background-image: var(--slide-image);
  background-size: cover;
  background-position: center;
  filter: blur(12px) saturate(0.75) brightness(0.75);
  transform: scale(1.06);
  transition: filter 0.25s ease, transform 0.25s ease;
}

.tournament-slide:hover::before {
  filter: blur(0px) saturate(1) brightness(0.92);
  transform: scale(1.12);
}

.tournament-slide::after {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(8, 12, 26, 0.1), rgba(8, 12, 26, 0.82));
}

.slide-content {
  position: absolute;
  inset: auto 0 0;
  z-index: 2;
  padding: 16px;
  display: grid;
  gap: 8px;
}

.slide-content h2 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.slide-content p {
  margin: 0;
  color: #d8e3ff;
}

.rank-emblems {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}

.emblem-card {
  border: 1px solid #344985;
  border-radius: 14px;
  background: rgba(8, 14, 34, 0.7);
  padding: 8px;
  display: flex;
  gap: 8px;
  align-items: center;
}

.emblem-card img {
  width: 48px;
  height: 48px;
  object-fit: contain;
}

.emblem-card strong {
  display: block;
  font-family: "Sora", sans-serif;
}

.emblem-card span {
  color: #9fb0dd;
  font-size: 0.8rem;
}

.arena-main {
  display: grid;
  grid-template-columns: 1.35fr 0.8fr;
  gap: 12px;
}

.arena-stage,
.side-block {
  border: 1px solid #2f426f;
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(17, 24, 48, 0.94), rgba(9, 13, 29, 0.95));
}

.arena-stage {
  padding: 14px;
  display: grid;
  gap: 12px;
}

.stage-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
  flex-wrap: wrap;
}

.stage-head h2 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.stage-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.tag {
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 999px;
  padding: 3px 9px;
  font-size: 0.74rem;
  color: #b6c6f1;
}

.stage-desc {
  margin: 0;
  color: #b2c0e8;
}

.battle-feed {
  display: grid;
  gap: 8px;
}

.battle-duel {
  border: 1px solid #33497f;
  border-radius: 14px;
  padding: 10px;
  background: rgba(6, 10, 26, 0.55);
  display: grid;
  grid-template-columns: 1fr auto 1fr auto;
  gap: 8px;
  align-items: center;
}

.duel-player {
  font-family: "Sora", sans-serif;
  font-weight: 700;
}

.duel-player.left {
  text-align: right;
}

.duel-center {
  display: grid;
  text-align: center;
  min-width: 90px;
}

.duel-center strong {
  color: #ffd479;
  font-size: 1.08rem;
}

.duel-center span {
  font-size: 0.72rem;
  color: #98a8d5;
}

.duel-actions {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.quick-actions {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  gap: 8px;
}

.quick-actions textarea,
.quick-actions input {
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: #eef2ff;
  padding: 9px 10px;
}

.arena-side {
  display: grid;
  gap: 10px;
}

.side-block {
  padding: 12px;
}

.side-block h3 {
  margin: 0 0 8px;
  font-family: "Sora", sans-serif;
}

.ladder-row,
.timeline-row {
  border: 1px solid #31457a;
  border-radius: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.ladder-row {
  display: grid;
  grid-template-columns: 38px 1fr;
  gap: 8px;
  align-items: center;
  margin-bottom: 6px;
}

.ladder-row img {
  width: 34px;
  height: 34px;
  object-fit: contain;
}

.ladder-row strong,
.timeline-row strong {
  display: block;
  font-size: 0.88rem;
}

.ladder-row span,
.timeline-row span,
.side-block p {
  color: #a5b5e0;
  font-size: 0.78rem;
  margin: 0;
}

.timeline-row.live {
  border-color: rgba(255, 96, 96, 0.45);
}

.timeline-row.upcoming {
  border-color: rgba(110, 184, 255, 0.44);
}

.admin-overlay {
  position: fixed;
  inset: 0;
  background: rgba(4, 6, 12, 0.72);
  display: grid;
  place-items: center;
  padding: 20px;
  z-index: 40;
}

.overlay-card {
  width: min(860px, 100%);
  border: 1px solid #3a4f8a;
  border-radius: 16px;
  background: linear-gradient(180deg, #141d3a, #0d1328);
  padding: 12px;
  display: grid;
  gap: 10px;
}

.overlay-card header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.overlay-card h3 {
  margin: 0;
  font-family: "Sora", sans-serif;
}

.overlay-form {
  display: grid;
  gap: 8px;
}

.overlay-form input,
.overlay-form textarea,
.overlay-form select {
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  color: #eef2ff;
  padding: 9px 10px;
}

.overlay-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}

.overlay-switches {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  color: #adc0ed;
  font-size: 0.85rem;
}

.empty-state {
  border: 1px dashed #3e578f;
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  color: #acbae6;
  background: rgba(255, 255, 255, 0.04);
}

.empty-icon {
  display: block;
  font-size: 2.4rem;
  margin-bottom: 8px;
}

.empty-inline {
  color: #a6b4df;
  font-size: 0.86rem;
}

@media (max-width: 980px) {
  .contest-toolbar {
    flex-direction: column;
  }

  .toolbar-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .rail-select {
    min-width: 0;
  }

  .arena-hero,
  .arena-main {
    grid-template-columns: 1fr;
  }

  .hero-progress {
    grid-column: 1;
  }

  .hero-right {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }

  .battle-duel {
    grid-template-columns: 1fr;
    text-align: center;
  }

  .duel-player.left,
  .duel-player.right {
    text-align: center;
  }

  .duel-actions {
    justify-content: center;
  }

  .quick-actions {
    grid-template-columns: 1fr;
  }

  .overlay-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .toolbar-pills {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .arena-slideshow {
    grid-template-columns: 1fr;
  }

  .slide-arrow {
    width: 100%;
    height: 48px;
  }

  .hero-right {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .emblem-card {
    min-height: 62px;
  }
}
</style>
