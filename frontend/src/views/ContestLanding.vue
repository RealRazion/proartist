<template>
  <div class="tournament-page">

    <!-- Hero -->
    <header class="contest-hero">
      <div class="hero-inner">
        <div class="hero-copy">
          <p class="eyebrow">UNYQ Turnier</p>
          <h1>Turniere • Battles • Voting</h1>
          <p class="hero-lead">
            Team erstellt Turniere, Artists bewerben sich und reichen Runden ein.
            Battles laufen mit echtem Fan-Voting.
          </p>
        </div>
        <div class="hero-stats">
          <div class="hstat">
            <span class="hstat-num">{{ tournaments.length }}</span>
            <span class="hstat-label">Turniere</span>
          </div>
          <div class="hstat">
            <span class="hstat-num">{{ battles.length }}</span>
            <span class="hstat-label">Battles</span>
          </div>
          <div class="hstat">
            <span class="hstat-num">{{ submissions.length }}</span>
            <span class="hstat-label">Einreichungen</span>
          </div>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="goHome">Zum Hub</button>
        <button class="btn" type="button" @click="loadAll" :disabled="busy">
          <svg class="spin-icon" :class="{ spinning: busy }" viewBox="0 0 24 24" aria-hidden="true"><path d="M21 12a9 9 0 1 1-9-9"/></svg>
          Aktualisieren
        </button>
      </div>
    </header>

    <!-- Turnier erstellen (Team only) -->
    <section v-if="isTeam" class="card collapsible-section">
      <button class="collapsible-head" type="button" @click="showCreateForm = !showCreateForm">
        <span class="collapsible-title">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
          Neues Turnier erstellen
        </span>
        <svg class="chevron" :class="{ open: showCreateForm }" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9l6 6 6-6"/></svg>
      </button>
      <div v-if="showCreateForm" class="collapsible-body">
        <form class="create-grid" @submit.prevent="createTournament">
          <label>
            Titel
            <input v-model.trim="createForm.title" required maxlength="200" placeholder="z. B. UNYQ Summer Battle" />
          </label>
          <label>
            Status
            <select v-model="createForm.status">
              <option value="DRAFT">Entwurf</option>
              <option value="APPLICATION_OPEN">Bewerbung offen</option>
              <option value="SUBMISSION_OPEN">Einreichung offen</option>
              <option value="BATTLES">Battles laufen</option>
              <option value="CLOSED">Geschlossen</option>
            </select>
          </label>
          <label class="full">
            Beschreibung
            <textarea v-model.trim="createForm.description" rows="3" placeholder="Kurzbeschreibung für Teilnehmer und Fans"></textarea>
          </label>
          <label>
            Bewerbungsphase
            <select v-model="createForm.has_application_phase">
              <option :value="true">Mit Bewerbung</option>
              <option :value="false">Ohne Bewerbung</option>
            </select>
          </label>
          <label>
            Bewerbungsdeadline
            <input v-model="createForm.application_deadline" type="datetime-local" />
          </label>
          <label>
            Einreichungsdeadline
            <input v-model="createForm.submission_deadline" type="datetime-local" />
          </label>
          <label>
            Telefon-Voting erzwingen
            <select v-model="createForm.require_phone_vote_verification">
              <option :value="false">Nein</option>
              <option :value="true">Ja (für später)</option>
            </select>
          </label>
          <label>
            Voting-Modus
            <select v-model="createForm.voting_mode">
              <option value="COMMUNITY">Community</option>
              <option value="HYBRID">Hybrid (Community + Jury)</option>
              <option value="JURY_ONLY">Nur Jury</option>
            </select>
          </label>
          <label>
            Vote-Änderung erlauben
            <select v-model="createForm.allow_vote_change">
              <option :value="true">Ja</option>
              <option :value="false">Nein</option>
            </select>
          </label>
          <label>
            Mindest-Accountalter (Stunden)
            <input v-model.number="createForm.min_account_age_hours" type="number" min="0" max="720" />
          </label>
          <label>
            Max Votes pro IP / Stunde
            <input v-model.number="createForm.max_votes_per_ip_per_hour" type="number" min="1" max="1000" />
          </label>
          <div class="full actions">
            <button class="btn" type="submit" :disabled="busy">Turnier anlegen</button>
          </div>
        </form>
      </div>
    </section>

    <!-- Turniere Liste -->
    <section class="list">
      <article v-if="tournaments.length === 0" class="card empty-state">
        <span class="empty-icon">🏆</span>
        <p>Noch keine Turniere vorhanden.</p>
      </article>

      <article v-for="tournament in tournaments" :key="tournament.id" class="tournament-card">
        <!-- Card Header -->
        <div class="tcard-header">
          <div class="tcard-title-row">
            <span :class="['status-badge', `status-${tournament.status}`]">{{ statusLabel(tournament.status) }}</span>
            <h3>{{ tournament.title }}</h3>
          </div>
          <p v-if="tournament.description" class="tcard-desc">{{ tournament.description }}</p>
          <div class="tcard-meta">
            <span class="meta-chip">{{ tournament.has_application_phase ? 'Mit Bewerbung' : 'Ohne Bewerbung' }}</span>
            <span class="meta-chip">{{ votingModeLabel(tournament.voting_mode) }}</span>
            <span class="meta-chip">{{ tournament.allow_vote_change ? 'Vote änderbar' : 'Vote fix' }}</span>
            <span class="meta-chip">Min Alter: {{ tournament.min_account_age_hours || 0 }}h</span>
            <span class="meta-chip">IP-Limit: {{ tournament.max_votes_per_ip_per_hour || 0 }}/h</span>
            <span class="meta-chip">{{ tournament.applications_count || 0 }} Apps</span>
            <span class="meta-chip">{{ tournament.submissions_count || 0 }} Runden</span>
            <span class="meta-chip highlight">{{ tournament.battles_count || 0 }} Battles</span>
          </div>
          <div class="deadline-row">
            <span v-if="tournament.application_deadline">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
              Bewerbungsende: {{ formatDateTime(tournament.application_deadline) }}
            </span>
            <span v-if="tournament.submission_deadline">
              <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/></svg>
              Einreichungsende: {{ formatDateTime(tournament.submission_deadline) }}
            </span>
          </div>
        </div>

        <!-- Artist: Bewerbung -->
        <div v-if="!isTeam && tournament.has_application_phase" class="tcard-section">
          <button class="section-toggle" type="button" @click="toggleSection(tournament.id, 'apply')">
            Bewerbung
            <span v-if="myApplication(tournament.id)" :class="['app-status', myApplication(tournament.id).status.toLowerCase()]">{{ myApplication(tournament.id).status }}</span>
            <svg class="chevron" :class="{ open: openSections[tournament.id]?.apply }" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div v-if="openSections[tournament.id]?.apply" class="section-body">
            <div v-if="myApplication(tournament.id)" class="applied-notice">
              Beworben – Status: <strong>{{ myApplication(tournament.id).status }}</strong>
            </div>
            <form v-else @submit.prevent="submitApplication(tournament.id)" class="inline-form">
              <textarea v-model.trim="applicationDrafts[tournament.id]" rows="2" placeholder="Kurze Bewerbung oder Vorstellung"></textarea>
              <button class="btn" type="submit" :disabled="busy">Bewerben</button>
            </form>
          </div>
        </div>

        <!-- Artist: Runde einreichen -->
        <div v-if="!isTeam" class="tcard-section">
          <button class="section-toggle" type="button" @click="toggleSection(tournament.id, 'submit')">
            Runde einreichen
            <svg class="chevron" :class="{ open: openSections[tournament.id]?.submit }" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div v-if="openSections[tournament.id]?.submit" class="section-body">
            <form @submit.prevent="submitRound(tournament.id)" class="submission-form">
              <div class="submission-grid">
                <label>Runde <input v-model.number="submissionDraft(tournament.id).round_number" type="number" min="1" /></label>
                <label>Titel <input v-model.trim="submissionDraft(tournament.id).title" maxlength="200" placeholder="Titel der Runde" /></label>
                <label class="full">Link <input v-model.trim="submissionDraft(tournament.id).media_url" type="url" placeholder="https://..." /></label>
                <label class="full">Notiz <textarea v-model.trim="submissionDraft(tournament.id).notes" rows="2" placeholder="Anmerkungen"></textarea></label>
              </div>
              <button class="btn" type="submit" :disabled="busy || !canSubmit(tournament)">
                {{ !canSubmit(tournament) ? 'Bewerbung nicht freigegeben' : 'Einreichen' }}
              </button>
            </form>
          </div>
        </div>

        <!-- Team: Bewerbungen verwalten -->
        <div v-if="isTeam" class="tcard-section">
          <button class="section-toggle" type="button" @click="toggleSection(tournament.id, 'applications')">
            Bewerbungen
            <span class="section-count">{{ applicationsFor(tournament.id).length }}</span>
            <svg class="chevron" :class="{ open: openSections[tournament.id]?.applications }" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div v-if="openSections[tournament.id]?.applications" class="section-body">
            <div v-if="applicationsFor(tournament.id).length === 0" class="empty-inline">Keine Bewerbungen</div>
            <div v-for="application in applicationsFor(tournament.id)" :key="application.id" class="app-row">
              <div class="app-info">
                <strong>{{ application.profile?.name || application.profile?.username }}</strong>
                <span :class="['app-status', application.status.toLowerCase()]">{{ application.status }}</span>
              </div>
              <div class="row-actions" v-if="application.status === 'PENDING'">
                <button class="btn small" @click="decideApplication(tournament.id, application.id, 'APPROVED')">Freigeben</button>
                <button class="btn ghost small" @click="decideApplication(tournament.id, application.id, 'REJECTED')">Ablehnen</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Team: Battle anlegen -->
        <div v-if="isTeam" class="tcard-section">
          <button class="section-toggle" type="button" @click="toggleSection(tournament.id, 'battle')">
            Battle anlegen
            <svg class="chevron" :class="{ open: openSections[tournament.id]?.battle }" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div v-if="openSections[tournament.id]?.battle" class="section-body">
            <form @submit.prevent="createBattle(tournament.id)" class="battle-form">
              <div class="battle-grid">
                <label>Runde <input v-model.number="battleDraft(tournament.id).round_number" type="number" min="1" /></label>
                <label>Links
                  <select v-model.number="battleDraft(tournament.id).left_submission">
                    <option :value="null" disabled>Submission wählen</option>
                    <option v-for="entry in submissionsFor(tournament.id)" :key="`l-${entry.id}`" :value="entry.id">{{ entryLabel(entry) }}</option>
                  </select>
                </label>
                <label>Rechts
                  <select v-model.number="battleDraft(tournament.id).right_submission">
                    <option :value="null" disabled>Submission wählen</option>
                    <option v-for="entry in submissionsFor(tournament.id)" :key="`r-${entry.id}`" :value="entry.id">{{ entryLabel(entry) }}</option>
                  </select>
                </label>
              </div>
              <button class="btn" type="submit" :disabled="busy">Battle erstellen</button>
            </form>
          </div>
        </div>

        <!-- Team: Verdächtige Votes -->
        <div v-if="isTeam" class="tcard-section">
          <button class="section-toggle" type="button" @click="toggleSection(tournament.id, 'flags')">
            Verdächtige Votes
            <span class="section-count">{{ flaggedVotesFor(tournament.id).length }}</span>
            <svg class="chevron" :class="{ open: openSections[tournament.id]?.flags }" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6"/></svg>
          </button>
          <div v-if="openSections[tournament.id]?.flags" class="section-body">
            <div v-if="flaggedVotesFor(tournament.id).length === 0" class="empty-inline">Keine offenen Auffälligkeiten.</div>
            <div v-for="vote in flaggedVotesFor(tournament.id)" :key="vote.id" class="flag-row">
              <div class="flag-info">
                <strong>{{ vote.voter_name || vote.voter?.name || vote.voter?.username }}</strong>
                <span class="muted">Battle #{{ vote.battle }} · Runde {{ vote.battle_round }}</span>
                <span class="muted">Grund: {{ vote.flag_reason || 'Auffälligkeitsmuster' }}</span>
                <span :class="['app-status', vote.moderation_status?.toLowerCase()]">{{ moderationLabel(vote.moderation_status) }}</span>
              </div>
              <div class="row-actions">
                <button class="btn small" @click="moderateVote(vote.id, 'APPROVED')">Freigeben</button>
                <button class="btn ghost small" @click="moderateVote(vote.id, 'REJECTED')">Ablehnen</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Battles -->
        <div class="tcard-section always-open">
          <div class="section-toggle static">
            Aktive Battles
            <span class="section-count">{{ battlesFor(tournament.id).length }}</span>
          </div>
          <div class="section-body">
            <div v-if="battlesFor(tournament.id).length === 0" class="empty-inline">Noch keine Battles angelegt.</div>
            <div v-for="battle in battlesFor(tournament.id)" :key="battle.id" class="battle-row">
              <div class="battle-matchup">
                <span class="fighter">{{ battle.left_profile_name }}</span>
                <div class="vs-block">
                  <span class="score">{{ battle.votes_left }}</span>
                  <span class="vs">vs</span>
                  <span class="score">{{ battle.votes_right }}</span>
                </div>
                <span class="fighter right">{{ battle.right_profile_name }}</span>
              </div>
              <div class="battle-round-label">Runde {{ battle.round_number }}</div>
              <div v-if="!isTeam" class="vote-actions">
                <input
                  v-if="tournament.require_phone_vote_verification"
                  v-model.trim="phoneDrafts[battle.id]"
                  placeholder="Telefonnummer (Verifizierung später)"
                  class="phone-input"
                />
                <div class="row-actions vote-row">
                  <button class="btn vote-btn" @click="voteBattle(battle, battle.left_submission)">{{ battle.left_profile_name }} wählen</button>
                  <button class="btn ghost vote-btn" @click="voteBattle(battle, battle.right_submission)">{{ battle.right_profile_name }} wählen</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { profile, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const busy = ref(false);
const showCreateForm = ref(false);
const tournaments = ref([]);
const applications = ref([]);
const submissions = ref([]);
const battles = ref([]);
const flaggedVotes = ref([]);
const openSections = ref({});

function toggleSection(id, key) {
  if (!openSections.value[id]) openSections.value[id] = {};
  openSections.value[id][key] = !openSections.value[id][key];
}

const applicationDrafts = ref({});
const submissionDrafts = ref({});
const battleDrafts = ref({});
const phoneDrafts = ref({});

const createForm = ref({
  title: "",
  description: "",
  has_application_phase: true,
  application_deadline: "",
  submission_deadline: "",
  status: "DRAFT",
  voting_mode: "COMMUNITY",
  allow_vote_change: true,
  min_account_age_hours: 0,
  max_votes_per_ip_per_hour: 20,
  require_phone_vote_verification: false,
});

const myProfileId = computed(() => profile.value?.id || null);

function asList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
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

function votingModeLabel(mode) {
  const map = {
    COMMUNITY: "Community",
    HYBRID: "Hybrid",
    JURY_ONLY: "Nur Jury",
  };
  return map[mode] || "Community";
}

function myApplication(tournamentId) {
  return applications.value.find((entry) => entry.tournament === tournamentId && entry.profile?.id === myProfileId.value) || null;
}

function canSubmit(tournament) {
  if (!tournament.has_application_phase) return true;
  const app = myApplication(tournament.id);
  return app?.status === "APPROVED";
}

function applicationsFor(tournamentId) {
  return applications.value.filter((entry) => entry.tournament === tournamentId);
}

function submissionsFor(tournamentId) {
  return submissions.value.filter((entry) => entry.tournament === tournamentId);
}

function battlesFor(tournamentId) {
  return battles.value.filter((entry) => entry.tournament === tournamentId);
}

function flaggedVotesFor(tournamentId) {
  return flaggedVotes.value.filter((entry) => entry.tournament === tournamentId);
}

function moderationLabel(status) {
  if (status === "PENDING_REVIEW") return "In Prüfung";
  if (status === "REJECTED") return "Abgelehnt";
  return "Freigegeben";
}

function submissionDraft(tournamentId) {
  if (!submissionDrafts.value[tournamentId]) {
    submissionDrafts.value[tournamentId] = { round_number: 1, title: "", media_url: "", notes: "" };
  }
  return submissionDrafts.value[tournamentId];
}

function battleDraft(tournamentId) {
  if (!battleDrafts.value[tournamentId]) {
    battleDrafts.value[tournamentId] = { round_number: 1, left_submission: null, right_submission: null };
  }
  return battleDrafts.value[tournamentId];
}

function entryLabel(entry) {
  const name = entry.profile?.name || entry.profile?.username || "Teilnehmer";
  return `R${entry.round_number} - ${name}`;
}

function goHome() {
  router.push({ name: "platforms" });
}

async function loadAll() {
  busy.value = true;
  try {
    const [tournamentRes, applicationRes, submissionRes, battleRes] = await Promise.all([
      api.get("tournaments/"),
      api.get("tournament-applications/"),
      api.get("tournament-submissions/"),
      api.get("tournament-battles/"),
    ]);
    tournaments.value = asList(tournamentRes.data);
    applications.value = asList(applicationRes.data);
    submissions.value = asList(submissionRes.data);
    battles.value = asList(battleRes.data);
    if (isTeam.value) {
      const { data } = await api.get("tournament-votes/flags/");
      flaggedVotes.value = asList(data);
    } else {
      flaggedVotes.value = [];
    }
  } catch (err) {
    console.error(err);
    showToast("Turnierdaten konnten nicht geladen werden", "error");
  } finally {
    busy.value = false;
  }
}

async function moderateVote(voteId, decision) {
  busy.value = true;
  try {
    await api.post(`tournament-votes/${voteId}/moderate/`, { decision });
    showToast("Vote-Moderation gespeichert", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
    showToast(err?.response?.data?.detail || "Moderation fehlgeschlagen", "error");
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
      status: createForm.value.status,
      voting_mode: createForm.value.voting_mode,
      allow_vote_change: createForm.value.allow_vote_change,
      min_account_age_hours: createForm.value.min_account_age_hours,
      max_votes_per_ip_per_hour: createForm.value.max_votes_per_ip_per_hour,
      require_phone_vote_verification: createForm.value.require_phone_vote_verification,
    });
    createForm.value = {
      title: "",
      description: "",
      has_application_phase: true,
      application_deadline: "",
      submission_deadline: "",
      status: "DRAFT",
      voting_mode: "COMMUNITY",
      allow_vote_change: true,
      min_account_age_hours: 0,
      max_votes_per_ip_per_hour: 20,
      require_phone_vote_verification: false,
    };
    showToast("Turnier erstellt", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
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
  } finally {
    busy.value = false;
  }
}

async function decideApplication(tournamentId, applicationId, decision) {
  busy.value = true;
  try {
    await api.post(`tournaments/${tournamentId}/applications/${applicationId}/decision/`, { decision });
    showToast("Bewerbung aktualisiert", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
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
  } finally {
    busy.value = false;
  }
}

async function createBattle(tournamentId) {
  const draft = battleDraft(tournamentId);
  busy.value = true;
  try {
    await api.post("tournament-battles/", {
      tournament: tournamentId,
      round_number: draft.round_number,
      left_submission: draft.left_submission,
      right_submission: draft.right_submission,
      status: "LIVE",
    });
    battleDrafts.value[tournamentId] = { round_number: 1, left_submission: null, right_submission: null };
    showToast("Battle erstellt", "success");
    await loadAll();
  } catch (err) {
    console.error(err);
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
.tournament-page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* Hero */
.contest-hero {
  background: linear-gradient(135deg, rgba(29, 78, 216, 0.18) 0%, rgba(16, 185, 129, 0.12) 100%);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 28px 24px 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.hero-inner {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}

.hero-copy p.hero-lead {
  margin: 8px 0 0;
  color: var(--muted);
  line-height: 1.6;
  max-width: 540px;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 11px;
  margin-bottom: 6px;
  color: var(--brand);
  font-weight: 700;
}

.hero-copy h1 {
  margin: 0;
  font-size: clamp(1.5rem, 2.8vw, 2.1rem);
  font-weight: 800;
  line-height: 1.15;
}

.hero-stats {
  display: flex;
  gap: 24px;
  flex-shrink: 0;
}

.hstat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}

.hstat-num {
  font-size: 2rem;
  font-weight: 800;
  color: var(--brand);
  line-height: 1;
}

.hstat-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--muted);
}

.hero-actions {
  display: flex;
  gap: 10px;
}

.spin-icon {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  flex-shrink: 0;
}

.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Create form */
.collapsible-section {
  border-radius: 16px;
  padding: 0;
  overflow: hidden;
}

.collapsible-head {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text);
  font-weight: 600;
  font-size: 1rem;
  text-align: left;
  gap: 12px;
}

.collapsible-head:hover {
  background: color-mix(in srgb, var(--brand) 6%, transparent 94%);
}

.collapsible-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.collapsible-title svg {
  width: 18px;
  height: 18px;
  fill: none;
  stroke: var(--brand);
  stroke-width: 2;
  stroke-linecap: round;
}

.collapsible-body {
  padding: 0 20px 20px;
}

.chevron {
  width: 16px;
  height: 16px;
  fill: none;
  stroke: var(--muted);
  stroke-width: 2;
  stroke-linecap: round;
  transition: transform 0.2s ease;
  flex-shrink: 0;
}

.chevron.open {
  transform: rotate(180deg);
}

.create-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.create-grid .full {
  grid-column: 1 / -1;
}

.create-grid label,
.submission-form label,
.battle-form label {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--muted);
}

.create-grid input,
.create-grid select,
.create-grid textarea,
.submission-form input,
.submission-form select,
.submission-form textarea,
.battle-form input,
.battle-form select,
.phone-input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
  font-size: 0.95rem;
}

/* Tournaments list */
.list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.tournament-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
}

.tcard-header {
  padding: 20px 20px 16px;
  border-bottom: 1px solid var(--border);
}

.tcard-title-row {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 6px;
}

.tcard-title-row h3 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
}

.tcard-desc {
  color: var(--muted);
  font-size: 0.92rem;
  margin: 0 0 12px;
}

.tcard-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.meta-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 3px 10px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--muted);
}

.meta-chip.highlight {
  background: color-mix(in srgb, var(--brand) 12%, var(--surface) 88%);
  color: var(--brand);
  border-color: color-mix(in srgb, var(--brand) 30%, var(--border) 70%);
}

.status-badge {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  flex-shrink: 0;
}

.status-badge.status-DRAFT { background: color-mix(in srgb, #94a3b8 18%, transparent); color: #64748b; }
.status-badge.status-APPLICATION_OPEN { background: color-mix(in srgb, #f59e0b 18%, transparent); color: #d97706; }
.status-badge.status-SUBMISSION_OPEN { background: color-mix(in srgb, #3b82f6 18%, transparent); color: #2563eb; }
.status-badge.status-BATTLES { background: color-mix(in srgb, #a855f7 18%, transparent); color: #9333ea; }
.status-badge.status-CLOSED { background: color-mix(in srgb, #10b981 18%, transparent); color: #059669; }

.deadline-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 20px;
  font-size: 0.82rem;
  color: var(--muted);
}

.deadline-row span {
  display: flex;
  align-items: center;
  gap: 5px;
}

.deadline-row svg {
  width: 13px;
  height: 13px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linecap: round;
  flex-shrink: 0;
}

/* Collapsible sections inside tournament card */
.tcard-section {
  border-top: 1px solid var(--border);
}

.section-toggle {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 13px 20px;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text);
  font-weight: 600;
  font-size: 0.9rem;
  text-align: left;
}

.section-toggle:hover {
  background: color-mix(in srgb, var(--brand) 5%, transparent 95%);
}

.section-toggle .chevron {
  margin-left: auto;
}

.section-toggle.static {
  cursor: default;
  pointer-events: none;
}

.section-count {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 999px;
  padding: 1px 8px;
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--muted);
}

.section-body {
  padding: 4px 20px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.app-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  flex-wrap: wrap;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.app-status {
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.app-status.pending { background: color-mix(in srgb, #f59e0b 18%, transparent); color: #d97706; }
.app-status.approved { background: color-mix(in srgb, #10b981 18%, transparent); color: #059669; }
.app-status.rejected { background: color-mix(in srgb, #ef4444 18%, transparent); color: #dc2626; }

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.small {
  padding: 7px 12px;
  font-size: 0.84rem;
  min-height: 34px;
}

/* Battle display */
.battle-row {
  padding: 14px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.battle-matchup {
  display: flex;
  align-items: center;
  gap: 12px;
}

.fighter {
  flex: 1;
  font-weight: 700;
  text-align: right;
  font-size: 0.95rem;
}

.fighter.right {
  text-align: left;
}

.vs-block {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.score {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--brand);
  min-width: 28px;
  text-align: center;
}

.vs {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.1em;
}

.battle-round-label {
  font-size: 0.78rem;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
}

.vote-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.vote-row {
  display: flex;
  gap: 8px;
}

.vote-btn {
  flex: 1;
  font-size: 0.85rem;
  padding: 9px 12px;
  min-height: 38px;
}

.phone-input {
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
  padding: 8px 12px;
}

/* Submission / Battle forms */
.submission-grid,
.battle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin-bottom: 12px;
}

.submission-grid .full,
.battle-grid .full {
  grid-column: 1 / -1;
}

.inline-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.inline-form textarea {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--input-bg);
  color: var(--text);
}

.applied-notice {
  padding: 10px 14px;
  border-radius: 10px;
  background: color-mix(in srgb, #10b981 12%, var(--surface) 88%);
  border: 1px solid color-mix(in srgb, #10b981 30%, var(--border) 70%);
  color: var(--text);
  font-size: 0.9rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 48px 24px;
  text-align: center;
  color: var(--muted);
}

.empty-icon {
  font-size: 3rem;
}

.empty-inline {
  color: var(--muted);
  font-size: 0.88rem;
  padding: 4px 0;
}

.flag-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-top: 8px;
  background: color-mix(in srgb, var(--card) 80%, transparent);
}

.flag-info {
  display: grid;
  gap: 4px;
}

@media (max-width: 600px) {
  .hero-inner {
    flex-direction: column;
  }

  .hero-stats {
    width: 100%;
    justify-content: space-around;
  }

  .battle-matchup {
    flex-direction: column;
    text-align: center;
  }

  .fighter { text-align: center; }
  .fighter.right { text-align: center; }
}
</style>
