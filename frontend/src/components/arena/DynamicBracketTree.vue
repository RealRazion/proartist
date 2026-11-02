<template>
  <div class="dynamic-bracket-wrapper">
    <!-- Bracket Toolbar -->
    <div class="bracket-controls-bar">
      <div class="bracket-meta-summary">
        <span class="tree-badge">🌳 {{ computedRounds.length }} Runden</span>
        <span class="tree-matches-count muted">Insgesamt {{ totalMatchesCount }} Matches</span>
      </div>

      <div class="bracket-filter-pills" v-if="computedRounds.length > 1">
        <button
          class="pill-btn"
          :class="{ active: selectedRoundFilter === null }"
          @click="selectedRoundFilter = null"
        >
          Alle Runden
        </button>
        <button
          v-for="r in computedRounds"
          :key="r.round"
          class="pill-btn"
          :class="{ active: selectedRoundFilter === r.round }"
          @click="selectedRoundFilter = r.round"
        >
          {{ getRoundShortTitle(r.round) }}
        </button>
      </div>

      <div class="bracket-actions">
        <button v-if="isTeam" class="btn ghost btn-sm" @click="$emit('refresh')">
          ↻ Bracket aktualisieren
        </button>
      </div>
    </div>

    <!-- Active Visual Tree -->
    <div v-if="computedRounds.length && totalMatchesCount > 0" class="bracket-tree-canvas card">
      <div class="bracket-tree-columns">
        <div
          v-for="(r, colIndex) in visibleRounds"
          :key="r.round"
          class="bracket-tree-column"
          :class="{
            'final-column': isFinalRound(r.round),
            'semi-column': isSemiRound(r.round),
          }"
        >
          <!-- Column Header -->
          <div class="column-header">
            <span class="column-round-pill">RUNDE {{ r.round }}</span>
            <h3 class="column-title">{{ getRoundTitle(r.round) }}</h3>
            <span class="column-matches-sub">{{ r.battles.length }} {{ r.battles.length === 1 ? 'Match' : 'Matches' }}</span>
          </div>

          <!-- Matches Stack -->
          <div class="column-matches-stack">
            <div
              v-for="(m, mIndex) in r.battles"
              :key="m.id"
              class="bracket-node-card"
              :class="{
                completed: isMatchClosed(m),
                live: isMatchLive(m),
                selected: selectedMatchId === m.id,
              }"
              @click="onSelectMatch(m)"
            >
              <!-- Node Top Bar -->
              <div class="node-meta-line">
                <span class="node-index">#{{ mIndex + 1 }}</span>
                <span
                  class="node-status-chip"
                  :class="{
                    closed: isMatchClosed(m),
                    live: isMatchLive(m),
                    open: !isMatchClosed(m) && !isMatchLive(m),
                  }"
                >
                  {{ isMatchClosed(m) ? 'Beendet' : (isMatchLive(m) ? '🔥 Live' : 'Bereit') }}
                </span>
              </div>

              <!-- Fighter Slot A (Top / Left) -->
              <div
                class="node-fighter-slot"
                :class="{
                  winner: isSlotWinner(m, 'left'),
                  playing: currentPlayingTrack === `battle-${m.id}-left`,
                }"
              >
                <div class="fighter-slot-lead">
                  <span class="fighter-avatar-badge">{{ getSlotInitial(m, 'left') }}</span>
                  <span class="fighter-label" :title="getSlotName(m, 'left')">
                    {{ getSlotName(m, 'left') }}
                  </span>
                </div>
                <div class="fighter-slot-trail">
                  <button
                    v-if="hasSlotAudio(m, 'left')"
                    class="btn-mini-play"
                    :class="{ active: currentPlayingTrack === `battle-${m.id}-left` }"
                    title="Audio vorhören"
                    @click.stop="onToggleMiniAudio(m, 'left')"
                  >
                    {{ currentPlayingTrack === `battle-${m.id}-left` ? '⏸' : '▶' }}
                  </button>
                  <span class="fighter-score">{{ getSlotScore(m, 'left') }}</span>
                  <span v-if="isSlotWinner(m, 'left')" class="crown-icon">👑</span>
                </div>
              </div>

              <!-- Node Divider -->
              <div class="node-divider">
                <span>VS</span>
              </div>

              <!-- Fighter Slot B (Bottom / Right) -->
              <div
                class="node-fighter-slot"
                :class="{
                  winner: isSlotWinner(m, 'right'),
                  playing: currentPlayingTrack === `battle-${m.id}-right`,
                }"
              >
                <div class="fighter-slot-lead">
                  <span class="fighter-avatar-badge right-badge">{{ getSlotInitial(m, 'right') }}</span>
                  <span class="fighter-label" :title="getSlotName(m, 'right')">
                    {{ getSlotName(m, 'right') }}
                  </span>
                </div>
                <div class="fighter-slot-trail">
                  <button
                    v-if="hasSlotAudio(m, 'right')"
                    class="btn-mini-play"
                    :class="{ active: currentPlayingTrack === `battle-${m.id}-right` }"
                    title="Audio vorhören"
                    @click.stop="onToggleMiniAudio(m, 'right')"
                  >
                    {{ currentPlayingTrack === `battle-${m.id}-right` ? '⏸' : '▶' }}
                  </button>
                  <span class="fighter-score">{{ getSlotScore(m, 'right') }}</span>
                  <span v-if="isSlotWinner(m, 'right')" class="crown-icon">👑</span>
                </div>
              </div>

              <!-- Quick Action / Footer -->
              <div class="node-footer-hint">
                <span>{{ isMatchClosed(m) ? 'Ergebnis ansehen' : 'Zum Abstimmen klicken' }}</span>
                <span>→</span>
              </div>
            </div>
          </div>

          <!-- Champion Podium next to Finale -->
          <div
            v-if="isFinalRound(r.round) && grandChampionName"
            class="champion-podium-card card"
          >
            <div class="podium-glow-orbit"></div>
            <span class="podium-trophy">🏆</span>
            <span class="podium-caption">UNYQ TOURNAMENT CHAMPION</span>
            <h4 class="podium-champion-name">{{ grandChampionName }}</h4>
            <span class="podium-badge">Circuit Sieger 🥇</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="card empty-bracket-box">
      <span class="empty-icon">🌳</span>
      <h3>Noch kein Turnierbaum vorhanden</h3>
      <p class="muted">
        Sobald Matches generiert werden, wird der vollständige interaktive Turnierbaum hier angezeigt.
      </p>
      <div v-if="isTeam" class="empty-actions">
        <button class="btn" @click="$emit('generateBattles')">
          ⚔️ Battles für Runde 1 generieren
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  rounds: {
    type: Array,
    default: () => [],
  },
  battles: {
    type: Array,
    default: () => [],
  },
  totalRounds: {
    type: Number,
    default: 0,
  },
  currentPlayingTrack: {
    type: String,
    default: null,
  },
  selectedMatchId: {
    type: [Number, String],
    default: null,
  },
  isTeam: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "selectMatch",
  "toggleAudio",
  "refresh",
  "generateBattles",
]);

const selectedRoundFilter = ref(null);

/* Normalize incoming data into sorted rounds */
const computedRounds = computed(() => {
  if (props.rounds && props.rounds.length > 0) {
    return [...props.rounds].sort((a, b) => a.round - b.round);
  }

  // Fallback: group flat battles by round_number
  if (props.battles && props.battles.length > 0) {
    const map = {};
    for (const b of props.battles) {
      const rn = b.round_number || 1;
      if (!map[rn]) map[rn] = [];
      map[rn].push(b);
    }
    const keys = Object.keys(map).map(Number).sort((a, b) => a - b);
    return keys.map((k) => ({
      round: k,
      battles: map[k],
    }));
  }

  return [];
});

const totalEffectiveRounds = computed(() => {
  if (props.totalRounds && props.totalRounds > 0) return props.totalRounds;
  return computedRounds.value.length || 1;
});

const visibleRounds = computed(() => {
  if (selectedRoundFilter.value !== null) {
    return computedRounds.value.filter((r) => r.round === selectedRoundFilter.value);
  }
  return computedRounds.value;
});

const totalMatchesCount = computed(() => {
  return computedRounds.value.reduce((acc, r) => acc + (r.battles?.length || 0), 0);
});

/* Round Title Generator */
function getRoundTitle(roundNumber) {
  const total = totalEffectiveRounds.value;
  const diffFromEnd = total - roundNumber;

  if (diffFromEnd === 0) return "Großes Finale 👑";
  if (diffFromEnd === 1) return "Halbfinale 🥈";
  if (diffFromEnd === 2) return "Viertelfinale 🥉";
  if (diffFromEnd === 3) return "Achtelfinale ⚔️";
  return `Runde ${roundNumber}`;
}

function getRoundShortTitle(roundNumber) {
  const total = totalEffectiveRounds.value;
  const diffFromEnd = total - roundNumber;

  if (diffFromEnd === 0) return "👑 Finale";
  if (diffFromEnd === 1) return "Halbfinale";
  if (diffFromEnd === 2) return "Viertelfinale";
  if (diffFromEnd === 3) return "Achtelfinale";
  return `Runde ${roundNumber}`;
}

function isFinalRound(roundNumber) {
  return roundNumber === totalEffectiveRounds.value;
}

function isSemiRound(roundNumber) {
  return roundNumber === totalEffectiveRounds.value - 1;
}

/* Match & Fighter Helpers */
function isMatchClosed(m) {
  return m.status === "CLOSED" || Boolean(m.winner || m.winner_name || m.winner_submission);
}

function isMatchLive(m) {
  return m.status === "LIVE" || m.status === "OPEN";
}

function getSlotName(m, side) {
  if (side === "left") {
    return m.left_name || m.left_profile_name || m.artistA || "Artist A";
  }
  return m.right_name || m.right_profile_name || m.artistB || "Artist B";
}

function getSlotInitial(m, side) {
  const name = getSlotName(m, side);
  return name.charAt(0).toUpperCase() || (side === "left" ? "A" : "B");
}

function getSlotScore(m, side) {
  if (side === "left") {
    if (m.votes_left !== undefined) return m.votes_left;
    if (m.scoreA !== undefined) return m.scoreA;
    return 0;
  }
  if (m.votes_right !== undefined) return m.votes_right;
  if (m.scoreB !== undefined) return m.scoreB;
  return 0;
}

function isSlotWinner(m, side) {
  if (!isMatchClosed(m)) return false;

  const leftSub = m.left_submission || m.left_submission_id;
  const rightSub = m.right_submission || m.right_submission_id;
  const leftName = getSlotName(m, "left");
  const rightName = getSlotName(m, "right");

  if (side === "left") {
    if (m.winner === "left" || m.winner === leftName) return true;
    if (m.winner_submission && m.winner_submission === leftSub) return true;
    if (m.winner_name && m.winner_name === leftName) return true;
    return false;
  } else {
    if (m.winner === "right" || m.winner === rightName) return true;
    if (m.winner_submission && m.winner_submission === rightSub) return true;
    if (m.winner_name && m.winner_name === rightName) return true;
    return false;
  }
}

function hasSlotAudio(m, side) {
  if (side === "left") return Boolean(m.left_media_url);
  return Boolean(m.right_media_url);
}

/* Grand Champion */
const grandChampionName = computed(() => {
  const finalRound = computedRounds.value.find((r) => isFinalRound(r.round));
  if (!finalRound || !finalRound.battles?.length) return null;
  const finalMatch = finalRound.battles[0];
  if (!finalMatch || !isMatchClosed(finalMatch)) return null;

  if (isSlotWinner(finalMatch, "left")) return getSlotName(finalMatch, "left");
  if (isSlotWinner(finalMatch, "right")) return getSlotName(finalMatch, "right");
  return finalMatch.winner_name || null;
});

/* Event Emitters */
function onSelectMatch(m) {
  emit("selectMatch", m);
}

function onToggleMiniAudio(m, side) {
  const trackKey = `battle-${m.id}-${side}`;
  const artistName = getSlotName(m, side);
  const mediaUrl = side === "left" ? m.left_media_url : m.right_media_url;
  emit("toggleAudio", { trackKey, artistName, mediaUrl, side, match: m });
}
</script>

<style scoped>
.dynamic-bracket-wrapper {
  display: flex;
  flex-direction: column;
  gap: 18px;
  width: 100%;
}

/* Toolbar */
.bracket-controls-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
  padding: 12px 18px;
  background: rgba(20, 24, 39, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  backdrop-filter: blur(12px);
}

.bracket-meta-summary {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tree-badge {
  font-size: 13px;
  font-weight: 700;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 4px 10px;
  border-radius: 8px;
}

.tree-matches-count {
  font-size: 12px;
}

.bracket-filter-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.pill-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-muted, #94a3b8);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 20px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.pill-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
}

.pill-btn.active {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #000;
  font-weight: 700;
  border-color: #f59e0b;
}

/* Tree Canvas */
.bracket-tree-canvas {
  padding: 24px 20px;
  background: radial-gradient(circle at center, rgba(30, 27, 50, 0.6) 0%, rgba(13, 15, 26, 0.95) 100%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 22px;
  overflow-x: auto;
}

.bracket-tree-columns {
  display: flex;
  align-items: flex-start;
  gap: 32px;
  min-width: min-content;
  padding-bottom: 12px;
}

.bracket-tree-column {
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 270px;
  min-width: 270px;
  position: relative;
}

.column-header {
  text-align: center;
  padding-bottom: 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.column-round-pill {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.8px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-muted, #94a3b8);
}

.column-title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.final-column .column-title {
  color: #fbbf24;
}

.column-matches-sub {
  font-size: 11px;
  color: var(--text-muted, #94a3b8);
}

/* Match Stack */
.column-matches-stack {
  display: flex;
  flex-direction: column;
  justify-content: space-around;
  gap: 20px;
  flex: 1;
}

.bracket-node-card {
  background: rgba(18, 21, 35, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.22s ease;
  position: relative;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
}

.bracket-node-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 8px 24px rgba(245, 158, 11, 0.15);
}

.bracket-node-card.live {
  border-color: rgba(239, 68, 68, 0.4);
}

.bracket-node-card.selected {
  border-color: #f59e0b;
  box-shadow: 0 0 16px rgba(245, 158, 11, 0.35);
}

/* Node Meta */
.node-meta-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 10px;
}

.node-index {
  font-weight: 700;
  color: var(--text-muted, #94a3b8);
}

.node-status-chip {
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 700;
}

.node-status-chip.live {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
}

.node-status-chip.closed {
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}

.node-status-chip.open {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
}

/* Fighter Slot */
.node-fighter-slot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 6px 8px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  border: 1px solid transparent;
  transition: all 0.15s ease;
}

.node-fighter-slot.winner {
  background: linear-gradient(90deg, rgba(245, 158, 11, 0.15), rgba(245, 158, 11, 0.05));
  border-color: rgba(245, 158, 11, 0.4);
}

.node-fighter-slot.playing {
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(56, 189, 248, 0.3);
}

.fighter-slot-lead {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  flex: 1;
}

.fighter-avatar-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #000;
  font-size: 11px;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.fighter-avatar-badge.right-badge {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
}

.fighter-label {
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #fff;
}

.fighter-slot-trail {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.btn-mini-play {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  border-radius: 4px;
  font-size: 10px;
  padding: 2px 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-mini-play:hover {
  background: #f59e0b;
  color: #000;
}

.btn-mini-play.active {
  background: #38bdf8;
  color: #000;
}

.fighter-score {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-muted, #94a3b8);
  min-width: 18px;
  text-align: right;
}

.node-fighter-slot.winner .fighter-score {
  color: #fbbf24;
}

.crown-icon {
  font-size: 12px;
}

.node-divider {
  text-align: center;
  font-size: 9px;
  font-weight: 800;
  color: var(--text-muted, #64748b);
  letter-spacing: 1px;
  margin: 3px 0;
}

.node-footer-hint {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 10px;
  color: var(--text-muted, #64748b);
  margin-top: 6px;
  padding-top: 4px;
  border-top: 1px dashed rgba(255, 255, 255, 0.06);
}

.bracket-node-card:hover .node-footer-hint {
  color: #fbbf24;
}

/* Champion Podium */
.champion-podium-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 20px 14px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.18), rgba(28, 22, 45, 0.95));
  border: 1px solid rgba(245, 158, 11, 0.45);
  border-radius: 18px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(245, 158, 11, 0.25);
  margin-top: 10px;
}

.podium-glow-orbit {
  position: absolute;
  top: -40px;
  width: 140px;
  height: 140px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.4) 0%, transparent 70%);
  pointer-events: none;
}

.podium-trophy {
  font-size: 38px;
  margin-bottom: 6px;
  animation: floatTrophy 2.4s ease-in-out infinite alternate;
}

@keyframes floatTrophy {
  0% { transform: translateY(0) rotate(-2deg); }
  100% { transform: translateY(-6px) rotate(2deg); }
}

.podium-caption {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 1px;
  color: var(--text-muted, #94a3b8);
  margin-bottom: 4px;
}

.podium-champion-name {
  font-size: 18px;
  font-weight: 900;
  color: #fbbf24;
  margin: 0 0 8px;
  text-shadow: 0 2px 10px rgba(245, 158, 11, 0.5);
}

.podium-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  background: #f59e0b;
  color: #000;
  border-radius: 6px;
}

/* Empty State */
.empty-bracket-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 48px 24px;
  border-radius: 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty-actions {
  margin-top: 16px;
}
</style>
