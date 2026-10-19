<template>
  <aside
    v-if="isPlayerEnabled && currentTrack"
    class="global-player-bar"
    aria-label="Globaler Studio Audio Player"
  >
    <div class="player-inner">
      <!-- Track Info -->
      <div class="player-track">
        <div class="track-thumb">
          <img v-if="currentTrack.cover_url" :src="currentTrack.cover_url" :alt="currentTrack.title" />
          <span v-else class="thumb-placeholder">🎵</span>
        </div>
        <div class="track-details">
          <strong class="track-name">{{ currentTrack.title }}</strong>
          <span class="track-artist">{{ currentTrack.artist }}</span>
        </div>
      </div>

      <!-- Controls & Progress -->
      <div class="player-center">
        <div class="player-buttons">
          <button
            type="button"
            class="play-main-btn"
            @click="togglePlay"
            :title="isPlaying ? 'Pause' : 'Abspielen'"
          >
            {{ isPlaying ? '⏸' : '▶' }}
          </button>
        </div>

        <div class="timeline-row">
          <span class="time-text">{{ formatTime(currentTime) }}</span>
          <div class="progress-bar-wrap" @click="handleSeek">
            <div class="progress-track">
              <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
            </div>
          </div>
          <span class="time-text">{{ formatTime(duration) }}</span>
        </div>
      </div>

      <!-- Volume & Dismiss -->
      <div class="player-right">
        <button
          type="button"
          class="player-icon-btn"
          @click="toggleMute"
          :title="isMuted ? 'Ton an' : 'Stummschalten'"
        >
          {{ isMuted || volume === 0 ? '🔇' : (volume < 0.5 ? '🔉' : '🔊') }}
        </button>
        <input
          type="range"
          min="0"
          max="1"
          step="0.02"
          class="vol-slider"
          :value="isMuted ? 0 : volume"
          @input="onVolumeChange"
          title="Lautstärke"
        />
        <button
          type="button"
          class="player-icon-btn close-btn"
          @click="stop"
          title="Player schließen"
        >
          ✕
        </button>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from "vue";
import { useGlobalAudio } from "../composables/useGlobalAudio";

const {
  currentTrack,
  isPlaying,
  currentTime,
  duration,
  volume,
  isMuted,
  isPlayerEnabled,
  togglePlay,
  seek,
  setVolume,
  toggleMute,
  stop,
} = useGlobalAudio();

const progressPercent = computed(() => {
  if (!duration.value || duration.value <= 0) return 0;
  return Math.min(100, Math.max(0, (currentTime.value / duration.value) * 100));
});

function formatTime(seconds) {
  if (!seconds || isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

function handleSeek(e) {
  if (!duration.value) return;
  const rect = e.currentTarget.getBoundingClientRect();
  const clickX = e.clientX - rect.left;
  const ratio = Math.max(0, Math.min(1, clickX / rect.width));
  seek(ratio * duration.value);
}

function onVolumeChange(e) {
  setVolume(parseFloat(e.target.value));
}
</script>

<style scoped>
.global-player-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 68px;
  background: rgba(14, 20, 36, 0.94);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(124, 161, 255, 0.2);
  z-index: 1000;
  display: flex;
  align-items: center;
  box-shadow: 0 -8px 30px rgba(0, 0, 0, 0.4);
  transition: transform 0.25s ease;
  color: #f1f5f9;
}

:global(:not(.dark)) .global-player-bar {
  background: rgba(255, 255, 255, 0.95);
  border-top: 1px solid rgba(15, 23, 42, 0.12);
  color: #0f172a;
  box-shadow: 0 -8px 30px rgba(15, 23, 42, 0.12);
}

.player-inner {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
}

/* Track Info */
.player-track {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 240px;
  flex-shrink: 0;
  overflow: hidden;
}

.track-thumb {
  width: 44px;
  height: 44px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.track-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumb-placeholder {
  font-size: 20px;
}

.track-details {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.track-name {
  font-size: 13.5px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 11.5px;
  color: #94a3b8;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

:global(:not(.dark)) .track-artist {
  color: #64748b;
}

/* Center Timeline & Controls */
.player-center {
  flex: 1;
  max-width: 620px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.player-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.play-main-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  border: none;
  font-size: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.play-main-btn:hover {
  transform: scale(1.06);
  box-shadow: 0 6px 16px rgba(59, 130, 246, 0.6);
}

.timeline-row {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 10px;
}

.time-text {
  font-size: 11px;
  font-variant-numeric: tabular-nums;
  color: #94a3b8;
  min-width: 32px;
}

:global(:not(.dark)) .time-text {
  color: #64748b;
}

.progress-bar-wrap {
  flex: 1;
  height: 16px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-track {
  width: 100%;
  height: 5px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.14);
  position: relative;
  overflow: hidden;
}

:global(:not(.dark)) .progress-track {
  background: rgba(15, 23, 42, 0.12);
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  border-radius: 999px;
  transition: width 0.1s linear;
}

/* Right Controls */
.player-right {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 200px;
  justify-content: flex-end;
}

.player-icon-btn {
  background: transparent;
  border: none;
  color: inherit;
  font-size: 16px;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  transition: opacity 0.2s ease;
}

.player-icon-btn:hover {
  opacity: 1;
}

.close-btn {
  font-size: 14px;
  opacity: 0.6;
}

.close-btn:hover {
  opacity: 1;
  color: #ef4444;
}

.vol-slider {
  width: 80px;
  height: 4px;
  border-radius: 999px;
  appearance: none;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.2);
  outline: none;
  cursor: pointer;
}

:global(:not(.dark)) .vol-slider {
  background: rgba(15, 23, 42, 0.18);
}

.vol-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
}

@media (max-width: 768px) {
  .player-track {
    width: 140px;
  }
  .player-right {
    width: auto;
  }
  .vol-slider {
    display: none;
  }
}
</style>
