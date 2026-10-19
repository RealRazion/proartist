import { ref } from "vue";

const STORAGE_KEY_ENABLED = "unyq_global_player_enabled";

let audioElement = null;

const currentTrack = ref(null);
const isPlaying = ref(false);
const currentTime = ref(0);
const duration = ref(0);
const volume = ref(0.85);
const isMuted = ref(false);
const isPlayerEnabled = ref(true);

// Initialize setting from localStorage
try {
  const stored = localStorage.getItem(STORAGE_KEY_ENABLED);
  if (stored !== null) {
    isPlayerEnabled.value = stored === "1";
  }
} catch {
  // ignore
}

function getAudio() {
  if (typeof window === "undefined") return null;
  if (!audioElement) {
    audioElement = new Audio();
    audioElement.volume = volume.value;

    audioElement.addEventListener("timeupdate", () => {
      currentTime.value = audioElement.currentTime || 0;
    });

    audioElement.addEventListener("loadedmetadata", () => {
      duration.value = audioElement.duration || 0;
    });

    audioElement.addEventListener("ended", () => {
      isPlaying.value = false;
      currentTime.value = 0;
    });

    audioElement.addEventListener("play", () => {
      isPlaying.value = true;
    });

    audioElement.addEventListener("pause", () => {
      isPlaying.value = false;
    });

    audioElement.addEventListener("error", () => {
      isPlaying.value = false;
    });
  }
  return audioElement;
}

export function useGlobalAudio() {
  function playTrack(track) {
    if (!track?.audio_url && !track?.url && !track?.src) {
      return;
    }
    const audio = getAudio();
    if (!audio) return;

    const source = track.audio_url || track.url || track.src;

    // If same track is playing, toggle play/pause
    if (currentTrack.value && (currentTrack.value.id === track.id || currentTrack.value.url === source)) {
      if (isPlaying.value) {
        audio.pause();
      } else {
        audio.play().catch(() => {});
      }
      return;
    }

    currentTrack.value = {
      id: track.id || Math.random(),
      title: track.title || "Studio Track",
      artist: track.artist || track.artist_name || track.profile_name || "UNYQ Creator",
      cover_url: track.cover_url || track.cover || "",
      url: source,
    };

    audio.src = source;
    audio.currentTime = 0;
    audio.play().catch(() => {});
  }

  function togglePlay() {
    const audio = getAudio();
    if (!audio || !currentTrack.value) return;
    if (isPlaying.value) {
      audio.pause();
    } else {
      audio.play().catch(() => {});
    }
  }

  function seek(timeInSeconds) {
    const audio = getAudio();
    if (!audio) return;
    audio.currentTime = Math.max(0, Math.min(timeInSeconds, duration.value || 0));
    currentTime.value = audio.currentTime;
  }

  function setVolume(val) {
    const audio = getAudio();
    const clamped = Math.max(0, Math.min(val, 1));
    volume.value = clamped;
    if (audio) {
      audio.volume = clamped;
    }
    if (clamped > 0) isMuted.value = false;
  }

  function toggleMute() {
    const audio = getAudio();
    if (!audio) return;
    isMuted.value = !isMuted.value;
    audio.muted = isMuted.value;
  }

  function stop() {
    const audio = getAudio();
    if (audio) {
      audio.pause();
      audio.currentTime = 0;
    }
    isPlaying.value = false;
    currentTrack.value = null;
  }

  function switchAudioSource(source, trackMeta = {}) {
    const audio = getAudio();
    if (!audio) return;
    const wasPlaying = isPlaying.value;
    const preservedTime = audio.currentTime || 0;

    currentTrack.value = {
      ...(currentTrack.value || {}),
      ...trackMeta,
      url: source,
    };

    audio.src = source;
    // Wait for metadata or set immediately
    const onLoaded = () => {
      audio.currentTime = Math.min(preservedTime, audio.duration || preservedTime);
      if (wasPlaying) {
        audio.play().catch(() => {});
      }
      audio.removeEventListener("loadedmetadata", onLoaded);
    };
    audio.addEventListener("loadedmetadata", onLoaded);
    audio.currentTime = preservedTime;
    if (wasPlaying) {
      audio.play().catch(() => {});
    }
  }

  function setPlayerEnabled(enabled) {
    isPlayerEnabled.value = !!enabled;
    try {
      localStorage.setItem(STORAGE_KEY_ENABLED, enabled ? "1" : "0");
    } catch {
      // ignore
    }
    if (!enabled && isPlaying.value) {
      stop();
    }
  }

  return {
    currentTrack,
    isPlaying,
    currentTime,
    duration,
    volume,
    isMuted,
    isPlayerEnabled,
    playTrack,
    togglePlay,
    seek,
    setVolume,
    toggleMute,
    stop,
    switchAudioSource,
    setPlayerEnabled,
  };
}
