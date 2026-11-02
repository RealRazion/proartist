<template>
  <header class="detail-header card">
    <!-- Top Bar: Navigation & Status Badges -->
    <div class="header-top-row">
      <div class="header-nav-group">
        <button class="btn ghost btn-sm btn-back" @click="$emit('goBack')">
          ← Zurück zur Arena
        </button>

        <!-- Quick Switcher Dropdown -->
        <div
          v-if="allTournaments && allTournaments.length > 1"
          class="tourney-quick-switcher"
          title="Schnell zu einem anderen Turnier wechseln"
        >
          <span class="switcher-label">Turnier:</span>
          <select
            :value="String(tournament?.id)"
            @change="$emit('switchTournament', $event.target.value)"
            class="input input-sm tourney-select"
          >
            <option
              v-for="item in allTournaments"
              :key="item.id"
              :value="String(item.id)"
            >
              {{ item.title }} ({{ getStatusLabel(item.status) }})
            </option>
          </select>
        </div>
      </div>

      <div class="top-status-pills">
        <span class="badge-status-pill" :class="`status-${(tournament?.status || 'draft').toLowerCase()}`">
          {{ getStatusLabel(tournament?.status) }}
        </span>
        <span class="badge-format-tag">
          {{ getFormatLabel(tournament?.format) }}
        </span>
        <span v-if="tournament?.is_no_loss" class="badge-no-loss">
          🛡️ No Loss
        </span>
        <span class="badge-genre-tag">{{ tournament?.genre || 'Allround' }}</span>
      </div>
    </div>

    <!-- Admin Micro-Toolbar (Team Only) -->
    <div v-if="isTeam" class="admin-compact-toolbar">
      <div class="act-phase-picker">
        <span class="act-label">👑 Admin Phase:</span>
        <select
          :value="tournament?.status"
          @change="$emit('updateStatus', $event.target.value)"
          class="input input-sm act-select"
        >
          <option v-for="st in statusSteps" :key="st.value" :value="st.value">
            {{ st.label }}
          </option>
        </select>
      </div>

      <div class="act-actions">
        <button
          class="btn btn-micro btn-accent"
          @click="$emit('generateBattles')"
          title="Paarungen aus Einreichungen generieren (inkl. Freilos/Fair Draw)"
        >
          ⚔️ Battles generieren
        </button>
        <button
          class="btn ghost btn-micro"
          @click="$emit('bulkApproveApplications')"
          title="Alle offenen Bewerber sofort freischalten"
        >
          ✓ Alle annehmen
        </button>
        <button
          class="btn ghost btn-micro btn-warn"
          @click="$emit('resetTournamentData')"
          title="Battles leeren & zurücksetzen"
        >
          ⚡ Reset
        </button>
        <button
          class="btn ghost btn-micro btn-danger-link"
          @click="$emit('deleteTournament')"
          title="Turnier löschen"
        >
          🗑️ Löschen
        </button>
      </div>
    </div>

    <!-- Main Title & Primary Action Strip -->
    <div class="header-center-strip">
      <div class="hcs-title-col">
        <div class="title-line">
          <h1 class="tournament-title">{{ cleanTitle(tournament?.title) }}</h1>
          <button
            v-if="isTeam"
            class="btn ghost btn-micro btn-edit-meta"
            @click="$emit('openEditModal')"
            title="Turnierdaten anpassen"
          >
            ✏️ Bearbeiten
          </button>
        </div>
        <p class="tournament-desc">{{ cleanDescription(tournament?.description) }}</p>
      </div>

      <!-- Action Column (Contextual CTA) -->
      <div class="hcs-action-col">
        <!-- Slot for Contextual CTA -->
        <slot name="action-button"></slot>
      </div>
    </div>

    <!-- Optional Rejection Alert Slot -->
    <slot name="rejection-banner"></slot>

    <!-- Horizontal Compact Metadata Ribbon -->
    <div class="metadata-chips-strip">
      <div class="meta-chip">
        <span class="mc-icon">💰</span>
        <span class="mc-val">{{ formattedPrizePool }}</span>
      </div>
      <div class="meta-chip">
        <span class="mc-icon">👥</span>
        <span class="mc-val">
          {{ participantsCount }} / {{ tournament?.slots || 16 }} {{ participantsCount === 1 ? 'Artist' : 'Artists' }}
        </span>
      </div>
      <div class="meta-chip">
        <span class="mc-icon">🎯</span>
        <span class="mc-val">
          {{ tournament?.total_rounds || 4 }} {{ (tournament?.total_rounds || 4) === 1 ? 'Runde' : 'Runden' }}
        </span>
      </div>
      <div class="meta-chip">
        <span class="mc-icon">⚡</span>
        <span class="mc-val">{{ (tournament?.format === 'DOUBLE_ELIMINATION') ? 'Doppel-K.O.' : 'K.O.-System' }}</span>
      </div>
      <div class="meta-chip">
        <span class="mc-icon">🎧</span>
        <span class="mc-val">{{ tournament?.genre || 'Allround' }}</span>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  tournament: {
    type: Object,
    default: () => ({}),
  },
  allTournaments: {
    type: Array,
    default: () => [],
  },
  participantsCount: {
    type: Number,
    default: 0,
  },
  isTeam: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "goBack",
  "switchTournament",
  "updateStatus",
  "generateBattles",
  "bulkApproveApplications",
  "resetTournamentData",
  "deleteTournament",
  "openEditModal",
]);

const statusSteps = [
  { value: "DRAFT", label: "Entwurf (DRAFT)" },
  { value: "APPLICATION_OPEN", label: "Bewerbungsphase (OFFEN)" },
  { value: "SUBMISSION_OPEN", label: "Einreichungsphase (TRACKS)" },
  { value: "BATTLES", label: "Voting & Battles (LIVE)" },
  { value: "CLOSED", label: "Beendet (ARCHIV)" },
];

function getStatusLabel(s) {
  const map = {
    DRAFT: "Entwurf",
    APPLICATION_OPEN: "Bewerbungsphase",
    SUBMISSION_OPEN: "Einreichung offen",
    BATTLES: "Voting aktiv 🔥",
    CLOSED: "Beendet 🏁",
  };
  return map[s] || s || "Entwurf";
}

function getFormatLabel(f) {
  const map = {
    SINGLE_ELIMINATION: "Single Elimination",
    DOUBLE_ELIMINATION: "Double Elimination",
    GROUP_STAGE_KNOCKOUT: "Gruppenphase + K.O.",
  };
  return map[f] || f || "K.O.-System";
}

function cleanTitle(t) {
  if (!t) return "UNYQ Arena Contest";
  return t.replace(/\s*\[(Slots|Preispool|TotalRounds|Genre|Format|GroupsCount|GroupSize):[^\]]+\]/gi, "").trim();
}

function cleanDescription(desc) {
  if (!desc) return "Offizielles UNYQ Battle Turnier. Tritt im 1v1 an, sammle RP und kämpfe um den Sieg.";
  const cleaned = desc.replace(/\s*\[(Slots|Preispool|TotalRounds|Genre|Format|GroupsCount|GroupSize):[^\]]+\]/gi, "").trim();
  return cleaned || "Offizielles UNYQ Battle Turnier.";
}

const formattedPrizePool = computed(() => {
  const p = props.tournament?.prize_pool;
  if (!p || p.toLowerCase().includes("kein") || p.toLowerCase().includes("festgelegt")) {
    return "Community Cup & RP";
  }
  return p;
});
</script>

<style scoped>
.detail-header {
  padding: 30px 28px;
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
  margin-bottom: 16px;
  flex-wrap: wrap;
  gap: 12px;
}

.header-nav-group {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tourney-quick-switcher {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.05);
  padding: 3px 8px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.switcher-label {
  font-size: 11px;
  font-weight: 700;
  color: #fbbf24;
}

.tourney-select {
  background: transparent;
  border: none;
  color: #fff;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  padding: 2px 4px;
}

.top-status-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.badge-status-pill {
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-status-pill.status-battles {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.4);
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.badge-status-pill.status-submission_open {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.badge-status-pill.status-application_open {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.badge-status-pill.status-closed {
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}

.badge-status-pill.status-draft {
  background: rgba(255, 255, 255, 0.05);
  color: #64748b;
}

.badge-format-tag,
.badge-genre-tag,
.badge-no-loss {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #e2e8f0;
}

.badge-no-loss {
  border-color: rgba(56, 189, 248, 0.4);
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
}

/* Admin Toolbar */
.admin-compact-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 8px 14px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 12px;
  margin-bottom: 18px;
  flex-wrap: wrap;
}

.act-phase-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.act-label {
  font-size: 12px;
  font-weight: 800;
  color: #fbbf24;
}

.act-select {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  border-radius: 8px;
  padding: 4px 8px;
  font-size: 12px;
}

.act-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-micro {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 6px;
}

.btn-danger-link {
  color: #f87171 !important;
}

.btn-warn {
  color: #fbbf24 !important;
}

/* Center Strip */
.header-center-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.hcs-title-col {
  flex: 1;
  min-width: 280px;
}

.title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.tournament-title {
  font-size: 28px;
  font-weight: 900;
  margin: 0;
  color: #fff;
  letter-spacing: -0.5px;
}

.tournament-desc {
  font-size: 14px;
  color: var(--text-muted, #94a3b8);
  line-height: 1.5;
  margin: 0;
  max-width: 800px;
}

.hcs-action-col {
  display: flex;
  align-items: center;
  gap: 10px;
}

/* Metadata Chips Strip */
.metadata-chips-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.meta-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 5px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #e2e8f0;
}

.mc-icon {
  font-size: 14px;
}
</style>
