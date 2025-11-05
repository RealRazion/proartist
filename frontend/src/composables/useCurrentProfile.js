import { ref, computed } from "vue";
import api from "../api";

const profile = ref(null);
const loading = ref(false);
const loaded = ref(false);
const error = ref(null);

async function fetchProfile(force = false) {
  if (loading.value) return profile.value;
  if (loaded.value && !force) return profile.value;
  loading.value = true;
  error.value = null;
  try {
    const { data } = await api.get("profiles/me/");
    profile.value = data;
    loaded.value = true;
    return profile.value;
  } catch (err) {
    error.value = err;
    throw err;
  } finally {
    loading.value = false;
  }
}

const isTeam = computed(() =>
  (profile.value?.roles || []).some((role) => role.key === "TEAM")
);

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
    fetchProfile,
    clearProfile,
  };
}
