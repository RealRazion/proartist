<template>
  <div
    class="card battle-duel-card"
    :class="{ 'battle-resolved': battle.status === 'CLOSED' }"
  >
    <!-- Top Meta Bar -->
    <div class="bd-top-bar">
      <div class="bd-round-tag">
        <span class="live-dot" v-if="battle.status === 'LIVE' || battle.status === 'OPEN'"></span>
        <span>RUNDE {{ battle.round_number || 1 }}</span>
      </div>
      <span class="bd-tourney-name">{{ battle.tournament_title || 'UNYQ Arena' }}</span>
      <span class="bd-status-badge" :class="battle.status.toLowerCase()">
        {{ (battle.status === 'LIVE' || battle.status === 'OPEN') ? '🔥 Voting Live' : '🏁 Beendet' }}
      </span>
    </div>

    <!-- THE FIGHTER SHOWDOWN (LEFT VS RIGHT) -->
    <div class="duel-arena-ring">
      <!-- Left Fighter Box -->
      <div
        class="fighter-card left-fighter"
        :class="{
          winner: battle.winner === 'left' || battle.winner_submission === battle.left_submission,
          voted: hasVotedSide('left'),
        }"
      >
        <div class="fighter-avatar-wrap">
          <div class="fighter-avatar" :class="{ playing: currentPlayingTrack === `battle-${battle.id}-left` }">
            {{ (battle.left_profile_name || 'A').charAt(0).toUpperCase() }}
          </div>
        </div>

        <div class="fighter-info">
          <strong class="fighter-name">{{ battle.left_profile_name || 'Artist A' }}</strong>
          <span class="fighter-track-title muted small">{{ battle.left_submission_title || 'Runde ' + (battle.round_number || 1) }}</span>
          <span class="fighter-tier-label">{{ battle.left_tier || 'Gold' }} Tier • {{ battle.left_rp || '1.600' }} RP</span>
        </div>

        <!-- Audio Player Box Left -->
        <div class="fighter-audio-deck">
          <button
            class="audio-play-trigger-btn"
            :class="{ playing: currentPlayingTrack === `battle-${battle.id}-left` }"
            @click="onToggleAudio('left')"
          >
            <span v-if="currentPlayingTrack === `battle-${battle.id}-left`">⏸ Pause</span>
            <span v-else>▶ Track anhören</span>
          </button>

          <!-- External Audio Link (Soundcloud / Drive / Direct) -->
          <a
            v-if="battle.left_media_url"
            :href="battle.left_media_url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-ext-link"
            title="In neuem Tab extern öffnen"
            @click.stop
          >
            🔗 Quelle
          </a>

          <!-- Animated Waveform Bars -->
          <div class="audio-wave-bars" :class="{ active: currentPlayingTrack === `battle-${battle.id}-left` }">
            <span v-for="i in 14" :key="i" class="wave-bar" :style="{ animationDelay: `${(i % 5) * 0.12}s` }"></span>
          </div>
        </div>

        <div class="fighter-votes-badge">
          <span class="votes-count">{{ battle.votes_left || 0 }}</span>
          <span class="votes-lbl">Votes</span>
        </div>
      </div>

      <!-- Central VS Badge & A/B Switcher -->
      <div class="duel-center-divider">
        <div class="vs-emblem">VS</div>
        <button
          class="btn-ab-switch"
          @click="onQuickSwitch"
          title="Zwischen beiden Tracks nahtlos umschalten"
        >
          ⇄ A/B Wechsel
        </button>
      </div>

      <!-- Right Fighter Box -->
      <div
        class="fighter-card right-fighter"
        :class="{
          winner: battle.winner === 'right' || battle.winner_submission === battle.right_submission,
          voted: hasVotedSide('right'),
        }"
      >
        <div class="fighter-avatar-wrap">
          <div class="fighter-avatar right-avatar" :class="{ playing: currentPlayingTrack === `battle-${battle.id}-right` }">
            {{ (battle.right_profile_name || 'B').charAt(0).toUpperCase() }}
          </div>
        </div>

        <div class="fighter-info">
          <strong class="fighter-name">{{ battle.right_profile_name || 'Artist B' }}</strong>
          <span class="fighter-track-title muted small">{{ battle.right_submission_title || 'Runde ' + (battle.round_number || 1) }}</span>
          <span class="fighter-tier-label">{{ battle.right_tier || 'Silber' }} Tier • {{ battle.right_rp || '1.200' }} RP</span>
        </div>

        <!-- Audio Player Box Right -->
        <div class="fighter-audio-deck">
          <button
            class="audio-play-trigger-btn"
            :class="{ playing: currentPlayingTrack === `battle-${battle.id}-right` }"
            @click="onToggleAudio('right')"
          >
            <span v-if="currentPlayingTrack === `battle-${battle.id}-right`">⏸ Pause</span>
            <span v-else>▶ Track anhören</span>
          </button>

          <!-- External Audio Link (Soundcloud / Drive / Direct) -->
          <a
            v-if="battle.right_media_url"
            :href="battle.right_media_url"
            target="_blank"
            rel="noopener noreferrer"
            class="btn-ext-link"
            title="In neuem Tab extern öffnen"
            @click.stop
          >
            🔗 Quelle
          </a>

          <!-- Animated Waveform Bars -->
          <div class="audio-wave-bars" :class="{ active: currentPlayingTrack === `battle-${battle.id}-right` }">
            <span v-for="i in 14" :key="i" class="wave-bar" :style="{ animationDelay: `${(i % 5) * 0.12}s` }"></span>
          </div>
        </div>

        <div class="fighter-votes-badge">
          <span class="votes-count">{{ battle.votes_right || 0 }}</span>
          <span class="votes-lbl">Votes</span>
        </div>
      </div>
    </div>

    <!-- Live Vote Meter -->
    <div class="live-vote-meter-container">
      <div class="lvm-bar-left" :style="{ width: votePctLeft + '%' }">
        <span>{{ votePctLeft }}%</span>
      </div>
      <div class="lvm-bar-right" :style="{ width: votePctRight + '%' }">
        <span>{{ votePctRight }}%</span>
      </div>
    </div>

    <!-- Voting Actions Bar -->
    <div class="battle-vote-action-bar" v-if="battle.status !== 'CLOSED'">
      <button
        class="btn-vote-fighter left-vote-btn"
        :class="{ 'has-voted': hasVotedSide('left') }"
        :disabled="hasAlreadyVoted"
        @click="$emit('vote', { battle, side: 'left', event: $event })"
      >
        <span class="vote-icon">👍</span>
        <span>{{ hasVotedSide('left') ? '✓ Dein Vote' : `Vote für ${battle.left_profile_name || 'Artist A'}` }}</span>
      </button>

      <button
        class="btn-vote-fighter right-vote-btn"
        :class="{ 'has-voted': hasVotedSide('right') }"
        :disabled="hasAlreadyVoted"
        @click="$emit('vote', { battle, side: 'right', event: $event })"
      >
        <span class="vote-icon">👍</span>
        <span>{{ hasVotedSide('right') ? '✓ Dein Vote' : `Vote für ${battle.right_profile_name || 'Artist B'}` }}</span>
      </button>
    </div>

    <div v-else class="battle-resolved-banner">
      🏆 Sieger: 
      <strong>{{ winnerDisplayName }}</strong>
      nach Voting &amp; Jury-Entscheid bestätigt!
    </div>

    <!-- Crowd Hype Reaction Floating Bar -->
    <div class="crowd-hype-toolbar">
      <span class="hype-title">Crowd Hype:</span>
      <div class="hype-buttons-group">
        <button
          v-for="emoji in ['🔥', '💥', '🤯', '👑', '👏']"
          :key="emoji"
          class="hype-react-btn"
          @click="$emit('reaction', { emoji, event: $event })"
          title="Reaktion senden"
        >
          {{ emoji }}
        </button>
      </div>
    </div>

    <!-- Admin / Jury Verdict Bar (Team Mode Only) -->
    <div class="admin-decision-bar" v-if="isTeam && battle.status !== 'CLOSED'">
      <span class="admin-verdict-label">👑 Admin / Jury Urteil:</span>
      <div class="admin-verdict-buttons">
        <button class="btn ghost btn-sm" @click="$emit('adminResolve', { battle, decision: 'left' })">
          🏆 {{ battle.left_profile_name || 'Links' }} Sieg
        </button>
        <button class="btn ghost btn-sm" @click="$emit('adminResolve', { battle, decision: 'right' })">
          🏆 {{ battle.right_profile_name || 'Rechts' }} Sieg
        </button>
        <button class="btn ghost btn-sm" @click="$emit('adminResolve', { battle, decision: 'auto' })">
          ⚡ Nach Votes schließen
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  battle: {
    type: Object,
    required: true,
  },
  currentPlayingTrack: {
    type: String,
    default: null,
  },
  userVotes: {
    type: Object,
    default: () => ({}),
  },
  isTeam: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits([
  "playAudio",
  "quickSwitch",
  "vote",
  "reaction",
  "adminResolve",
]);

/* Vote Calculations */
const votePctLeft = computed(() => {
  const l = props.battle.votes_left || 0;
  const r = props.battle.votes_right || 0;
  const total = l + r;
  if (!total) return 50;
  return Math.round((l / total) * 100);
});

const votePctRight = computed(() => {
  return 100 - votePctLeft.value;
});

const hasAlreadyVoted = computed(() => {
  return Boolean(props.userVotes[props.battle.id]);
});

function hasVotedSide(side) {
  return props.userVotes[props.battle.id] === side;
}

const winnerDisplayName = computed(() => {
  if (props.battle.winner_submission === props.battle.left_submission) {
    return props.battle.left_profile_name || "Artist A";
  }
  if (props.battle.winner_submission === props.battle.right_submission) {
    return props.battle.right_profile_name || "Artist B";
  }
  if (props.battle.votes_left >= props.battle.votes_right) {
    return props.battle.left_profile_name || "Artist A";
  }
  return props.battle.right_profile_name || "Artist B";
});

/* Audio Event Triggers */
function onToggleAudio(side) {
  const trackKey = `battle-${props.battle.id}-${side}`;
  const artistName = side === "left" ? props.battle.left_profile_name : props.battle.right_profile_name;
  const mediaUrl = side === "left" ? props.battle.left_media_url : props.battle.right_media_url;

  emit("playAudio", {
    trackKey,
    artistName: artistName || "Artist",
    mediaUrl,
    side,
    battle: props.battle,
  });
}

function onQuickSwitch() {
  emit("quickSwitch", props.battle);
}
</script>

<style scoped>
.battle-duel-card {
  padding: 24px;
  background: 
    radial-gradient(circle at top, rgba(245, 158, 11, 0.08), transparent 60%),
    linear-gradient(135deg, rgba(22, 18, 36, 0.95), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(245, 158, 11, 0.2);
  border-radius: 20px;
  position: relative;
  overflow: hidden;
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.battle-duel-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.35);
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.4);
}

.battle-resolved {
  opacity: 0.88;
  border-color: rgba(255, 255, 255, 0.1);
}

.bd-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  font-size: 12px;
}

.bd-round-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.15);
  padding: 3px 9px;
  border-radius: 6px;
}

.live-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  animation: pulseDot 1.4s infinite;
}

@keyframes pulseDot {
  0% { transform: scale(0.9); opacity: 0.7; }
  50% { transform: scale(1.3); opacity: 1; }
  100% { transform: scale(0.9); opacity: 0.7; }
}

.bd-tourney-name {
  color: var(--text-muted, #94a3b8);
  font-weight: 600;
  font-size: 12px;
}

.bd-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
}

.bd-status-badge.live,
.bd-status-badge.open {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.bd-status-badge.closed {
  background: rgba(255, 255, 255, 0.08);
  color: #94a3b8;
}

/* Ring Showdown */
.duel-arena-ring {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 16px;
  align-items: center;
  margin-bottom: 20px;
}

.fighter-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: 18px 14px;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.2s ease;
}

.fighter-card.winner {
  border-color: #fbbf24;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.12), rgba(0, 0, 0, 0.4));
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.fighter-card.voted {
  border-color: #38bdf8;
}

.fighter-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #000;
  font-weight: 800;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 10px;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.3);
  transition: transform 0.2s ease;
}

.fighter-avatar.right-avatar {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}

.fighter-avatar.playing {
  animation: pulseAvatar 1s infinite alternate;
}

@keyframes pulseAvatar {
  0% { transform: scale(1); }
  100% { transform: scale(1.08); box-shadow: 0 0 20px rgba(245, 158, 11, 0.6); }
}

.fighter-name {
  font-size: 15px;
  color: #fff;
  margin-bottom: 2px;
}

.fighter-track-title {
  display: block;
  font-size: 11px;
  color: #cbd5e1;
  margin-bottom: 4px;
}

.fighter-tier-label {
  font-size: 11px;
  color: var(--text-muted, #94a3b8);
  margin-bottom: 12px;
}

/* Audio Deck */
.fighter-audio-deck {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.audio-play-trigger-btn {
  width: 100%;
  padding: 8px 12px;
  border-radius: 9px;
  font-size: 12px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
}

.audio-play-trigger-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  border-color: rgba(255, 255, 255, 0.3);
}

.audio-play-trigger-btn.playing {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  border-color: transparent;
  box-shadow: 0 4px 15px rgba(245, 158, 11, 0.35);
}

.btn-ext-link {
  font-size: 11px;
  color: #38bdf8;
  text-decoration: none;
  font-weight: 600;
}

.btn-ext-link:hover {
  text-decoration: underline;
}

.audio-wave-bars {
  display: flex;
  align-items: flex-end;
  gap: 2px;
  height: 16px;
  opacity: 0.3;
  transition: opacity 0.2s ease;
}

.audio-wave-bars.active {
  opacity: 1;
}

.wave-bar {
  width: 2px;
  height: 4px;
  background: #fbbf24;
  border-radius: 2px;
}

.audio-wave-bars.active .wave-bar {
  animation: danceWave 0.6s ease-in-out infinite alternate;
}

@keyframes danceWave {
  0% { height: 3px; }
  100% { height: 16px; }
}

.fighter-votes-badge {
  display: flex;
  flex-direction: column;
  margin-top: 10px;
}

.votes-count {
  font-size: 18px;
  font-weight: 800;
  color: #fff;
}

.votes-lbl {
  font-size: 10px;
  color: var(--text-muted, #94a3b8);
  text-transform: uppercase;
}

/* Duel Center Divider */
.duel-center-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.vs-emblem {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: radial-gradient(circle, #dc2626, #991b1b);
  border: 2px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  font-weight: 900;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 15px rgba(220, 38, 38, 0.5);
}

.btn-ab-switch {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.btn-ab-switch:hover {
  background: #38bdf8;
  color: #000;
  border-color: #38bdf8;
}

/* Meter */
.live-vote-meter-container {
  display: flex;
  height: 10px;
  border-radius: 6px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.4);
  margin-bottom: 16px;
}

.lvm-bar-left {
  background: linear-gradient(90deg, #f59e0b, #d97706);
  font-size: 8px;
  font-weight: 800;
  color: #000;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.3s ease;
}

.lvm-bar-right {
  background: linear-gradient(90deg, #1d4ed8, #3b82f6);
  font-size: 8px;
  font-weight: 800;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: width 0.3s ease;
}

/* Vote Buttons */
.battle-vote-action-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}

.btn-vote-fighter {
  padding: 10px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.12);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  transition: all 0.2s ease;
}

.left-vote-btn {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.3);
}

.left-vote-btn:hover:not(:disabled) {
  background: #f59e0b;
  color: #000;
  transform: translateY(-1px);
}

.right-vote-btn {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.3);
}

.right-vote-btn:hover:not(:disabled) {
  background: #3b82f6;
  color: #fff;
  transform: translateY(-1px);
}

.btn-vote-fighter.has-voted {
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);
  font-weight: 800;
}

.btn-vote-fighter:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.battle-resolved-banner {
  padding: 12px;
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fbbf24;
  text-align: center;
  font-size: 13px;
  margin-bottom: 16px;
}

/* Crowd Hype */
.crowd-hype-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.25);
  margin-bottom: 12px;
}

.hype-title {
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted, #94a3b8);
  text-transform: uppercase;
}

.hype-buttons-group {
  display: flex;
  gap: 6px;
}

.hype-react-btn {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.15s ease;
  padding: 2px 4px;
}

.hype-react-btn:hover {
  transform: scale(1.3);
}

/* Admin Decision */
.admin-decision-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  flex-wrap: wrap;
  gap: 8px;
}

.admin-verdict-label {
  font-size: 11px;
  font-weight: 700;
  color: #fbbf24;
}

.admin-verdict-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
</style>
