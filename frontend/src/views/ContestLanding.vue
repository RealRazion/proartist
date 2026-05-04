<template>
  <div class="tournament-page">
    <header class="hero card">
      <div class="hero-copy">
        <p class="eyebrow">UNYQ Turnier</p>
        <h1>Turniere, Runden und Fan-Voting</h1>
        <p>
          Team-Mitglieder erstellen Turniere mit oder ohne Bewerbungsphase. Artists bewerben sich oder reichen direkt ihre Runde ein.
          Battles laufen mit Voting, inklusive Vorbereitung auf Telefon-Verifizierung.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="goHome">Zum Hub</button>
        <button class="btn" type="button" @click="loadAll" :disabled="busy">Aktualisieren</button>
      </div>
    </header>

    <section v-if="isTeam" class="card section">
      <h2>Neues Turnier erstellen</h2>
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
          Voting per Telefon später erzwingen
          <select v-model="createForm.require_phone_vote_verification">
            <option :value="false">Nein (jetzt offen)</option>
            <option :value="true">Ja (für später vorbereitet)</option>
          </select>
        </label>
        <div class="full actions">
          <button class="btn" type="submit" :disabled="busy">Turnier anlegen</button>
        </div>
      </form>
    </section>

    <section class="section list">
      <article v-for="tournament in tournaments" :key="tournament.id" class="card tournament-card">
        <header class="tournament-head">
          <div>
            <h3>{{ tournament.title }}</h3>
            <p class="muted">{{ tournament.description || "Keine Beschreibung" }}</p>
          </div>
          <span class="badge">{{ statusLabel(tournament.status) }}</span>
        </header>

        <div class="meta-row">
          <span>Bewerbung: {{ tournament.has_application_phase ? "Ja" : "Nein" }}</span>
          <span>Apps: {{ tournament.applications_count || 0 }}</span>
          <span>Runden: {{ tournament.submissions_count || 0 }}</span>
          <span>Battles: {{ tournament.battles_count || 0 }}</span>
        </div>

        <div class="deadline-row muted">
          <span>Bewerbungsende: {{ formatDateTime(tournament.application_deadline) }}</span>
          <span>Einreichungsende: {{ formatDateTime(tournament.submission_deadline) }}</span>
        </div>

        <section v-if="!isTeam && tournament.has_application_phase" class="inline-section">
          <h4>Bewerbung</h4>
          <div v-if="myApplication(tournament.id)">
            <p>
              Status: <strong>{{ myApplication(tournament.id).status }}</strong>
            </p>
          </div>
          <form v-else @submit.prevent="submitApplication(tournament.id)">
            <textarea
              v-model.trim="applicationDrafts[tournament.id]"
              rows="2"
              placeholder="Kurze Bewerbung oder Vorstellung"
            ></textarea>
            <button class="btn" type="submit" :disabled="busy">Bewerben</button>
          </form>
        </section>

        <section v-if="!isTeam" class="inline-section">
          <h4>Runde einreichen</h4>
          <form @submit.prevent="submitRound(tournament.id)">
            <div class="submission-grid">
              <input v-model.number="submissionDraft(tournament.id).round_number" type="number" min="1" placeholder="Runde" />
              <input v-model.trim="submissionDraft(tournament.id).title" maxlength="200" placeholder="Titel der Runde" />
              <input v-model.trim="submissionDraft(tournament.id).media_url" type="url" placeholder="https://..." />
              <textarea v-model.trim="submissionDraft(tournament.id).notes" rows="2" placeholder="Notiz"></textarea>
            </div>
            <button class="btn" type="submit" :disabled="busy || !canSubmit(tournament)">Einreichen</button>
          </form>
        </section>

        <section v-if="isTeam" class="inline-section">
          <h4>Bewerbungen verwalten</h4>
          <div v-for="application in applicationsFor(tournament.id)" :key="application.id" class="app-row">
            <span>{{ application.profile?.name || application.profile?.username }} - {{ application.status }}</span>
            <div class="row-actions" v-if="application.status === 'PENDING'">
              <button class="btn small" @click="decideApplication(tournament.id, application.id, 'APPROVED')">Freigeben</button>
              <button class="btn ghost small" @click="decideApplication(tournament.id, application.id, 'REJECTED')">Ablehnen</button>
            </div>
          </div>
        </section>

        <section v-if="isTeam" class="inline-section">
          <h4>Battle anlegen</h4>
          <form @submit.prevent="createBattle(tournament.id)">
            <div class="battle-grid">
              <input v-model.number="battleDraft(tournament.id).round_number" type="number" min="1" placeholder="Runde" />
              <select v-model.number="battleDraft(tournament.id).left_submission">
                <option :value="null" disabled>Left Submission</option>
                <option v-for="entry in submissionsFor(tournament.id)" :key="`l-${entry.id}`" :value="entry.id">
                  {{ entryLabel(entry) }}
                </option>
              </select>
              <select v-model.number="battleDraft(tournament.id).right_submission">
                <option :value="null" disabled>Right Submission</option>
                <option v-for="entry in submissionsFor(tournament.id)" :key="`r-${entry.id}`" :value="entry.id">
                  {{ entryLabel(entry) }}
                </option>
              </select>
            </div>
            <button class="btn" type="submit" :disabled="busy">Battle erstellen</button>
          </form>
        </section>

        <section class="inline-section">
          <h4>Aktive Battles</h4>
          <div v-if="battlesFor(tournament.id).length === 0" class="muted">Noch keine Battles angelegt.</div>
          <div v-for="battle in battlesFor(tournament.id)" :key="battle.id" class="battle-row">
            <div>
              <strong>Runde {{ battle.round_number }}:</strong>
              {{ battle.left_profile_name }} vs {{ battle.right_profile_name }}
            </div>
            <div class="muted">{{ battle.votes_left }} : {{ battle.votes_right }}</div>
            <div v-if="!isTeam" class="vote-box">
              <input
                v-if="tournament.require_phone_vote_verification"
                v-model.trim="phoneDrafts[battle.id]"
                placeholder="Telefonnummer (später Verifizierung)"
              />
              <div class="row-actions">
                <button class="btn small" @click="voteBattle(battle, battle.left_submission)">Vote Left</button>
                <button class="btn ghost small" @click="voteBattle(battle, battle.right_submission)">Vote Right</button>
              </div>
            </div>
          </div>
        </section>
      </article>
      <article v-if="tournaments.length === 0" class="card empty">
        Noch keine Turniere vorhanden.
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
const tournaments = ref([]);
const applications = ref([]);
const submissions = ref([]);
const battles = ref([]);

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
      require_phone_vote_verification: createForm.value.require_phone_vote_verification,
    });
    createForm.value = {
      title: "",
      description: "",
      has_application_phase: true,
      application_deadline: "",
      submission_deadline: "",
      status: "DRAFT",
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

.hero {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  align-items: flex-start;
  background: linear-gradient(130deg, rgba(29, 78, 216, 0.14), rgba(16, 185, 129, 0.14));
}

.hero-copy p {
  margin: 8px 0 0;
  color: var(--muted);
  line-height: 1.6;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 12px;
  margin-bottom: 6px;
  color: var(--brand);
}

.hero-actions {
  display: flex;
  gap: 10px;
}

.section {
  display: grid;
  gap: 12px;
}

.create-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}

.create-grid .full {
  grid-column: 1 / -1;
}

.create-grid input,
.create-grid select,
.create-grid textarea,
.submission-grid input,
.submission-grid textarea,
.battle-grid input,
.battle-grid select,
.vote-box input,
textarea {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--card);
  color: var(--text);
}

.list {
  display: grid;
  gap: 12px;
}

.tournament-card {
  display: grid;
  gap: 12px;
}

.tournament-head {
  display: flex;
  justify-content: space-between;
  gap: 14px;
}

.meta-row,
.deadline-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 14px;
  font-size: 0.9rem;
}

.badge {
  align-self: flex-start;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(14, 165, 233, 0.1);
  font-size: 0.8rem;
}

.inline-section {
  border-top: 1px solid var(--border);
  padding-top: 10px;
  display: grid;
  gap: 8px;
}

.submission-grid,
.battle-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 8px;
}

.app-row,
.battle-row {
  padding: 10px;
  border-radius: 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  display: grid;
  gap: 8px;
}

.row-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.small {
  padding: 7px 10px;
  font-size: 0.84rem;
}

.muted {
  color: var(--muted);
}

.empty {
  text-align: center;
  color: var(--muted);
}

@media (max-width: 840px) {
  .hero {
    flex-direction: column;
  }
}
</style>
