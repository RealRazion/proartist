import { ref, computed } from "vue";
import api from "../api";

const profile = ref(null);
const loading = ref(false);
const loaded = ref(false);
const error = ref(null);

// Workspace Mode: 'CONTEST_ONLY' (Turnier-Artist) | 'UNYQ_ARTIST' (Full UNYQ Artist)
const storedMode = localStorage.getItem("unyq_artist_workspace_mode");
const workspaceMode = ref(storedMode || "UNYQ_ARTIST");

async function fetchProfile(force = false) {
  if (loading.value) return profile.value;
  if (loaded.value && !force) return profile.value;
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get("profiles/me/");
    profile.value = data;
    loaded.value = true;

    // Check if profile has an assigned workspace mode in socials or bio
    if (data.socials?.workspace_mode) {
      workspaceMode.value = data.socials.workspace_mode;
      localStorage.setItem("unyq_artist_workspace_mode", workspaceMode.value);
    } else if (data.bio) {
      const modeMatch = data.bio.match(/\[WorkspaceMode:\s*(CONTEST_ONLY|UNYQ_ARTIST)\]/i);
      if (modeMatch) {
        workspaceMode.value = modeMatch[1].toUpperCase();
        localStorage.setItem("unyq_artist_workspace_mode", workspaceMode.value);
      }
    }

    return profile.value;
  } catch (err) {
    error.value = err;
    throw err;
  } finally {
    loading.value = false;
  }
}

const isTeam = computed(() =>
  (profile.value?.roles || []).some((role) => ["TEAM", "ADMIN"].includes(role.key))
);

const isAdmin = computed(() =>
  (profile.value?.roles || []).some((role) => role.key === "ADMIN")
);

const isContestOnly = computed(() => {
  // Team members always have access to full tools, but can toggle preview
  if (isTeam.value) {
    return workspaceMode.value === "CONTEST_ONLY";
  }
  return workspaceMode.value === "CONTEST_ONLY";
});

const isUnyqArtist = computed(() => {
  if (isTeam.value) return true;
  return workspaceMode.value === "UNYQ_ARTIST";
});

async function setWorkspaceMode(mode, syncBackend = true) {
  const norm = mode === "CONTEST_ONLY" ? "CONTEST_ONLY" : "UNYQ_ARTIST";
  workspaceMode.value = norm;
  localStorage.setItem("unyq_artist_workspace_mode", norm);
  if (syncBackend && profile.value?.id) {
    try {
      const nextSocials = { ...(profile.value.socials || {}), workspace_mode: norm };
      await api.patch(`profiles/${profile.value.id}/`, { socials: nextSocials });
      profile.value.socials = nextSocials;
    } catch {
      // ignore
    }
  }
}

function canAccessModule(moduleCategory) {
  if (isTeam.value) return true;
  // If artist has explicit module permissions set by admin
  const explicit = profile.value?.socials?.module_permissions?.[moduleCategory];
  if (typeof explicit === "boolean") return explicit;

  if (workspaceMode.value === "CONTEST_ONLY") {
    // Contest-only artists only see arena, battles, chat, and profile
    return ["arena", "chat", "profile"].includes(moduleCategory);
  }
  return true;
}

function clearProfile() {
  profile.value = null;
  loaded.value = false;
  error.value = null;
}

export function useCurrentProfile() {
  return {
    profile,
    loading,
    loaded,
    error,
    isTeam,
    isAdmin,
    workspaceMode,
    isContestOnly,
    isUnyqArtist,
    setWorkspaceMode,
    canAccessModule,
    fetchProfile,
    clearProfile,
  };
}
