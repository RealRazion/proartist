import { ref, computed } from "vue";
import { PATCH_NOTES, LATEST_PATCH, parseVersionParts } from "../config/patchnotes";
import { APP_VERSION } from "../config/version";

const isModalOpen = ref(false);
const activePatchIndex = ref(0);

export function usePatchnotes() {
  const currentVersion = computed(() => APP_VERSION);
  const allPatches = computed(() => PATCH_NOTES);
  const latestPatch = computed(() => LATEST_PATCH || {
    version: APP_VERSION,
    date: new Date().toISOString().split("T")[0],
    title: `Version ${APP_VERSION}`,
    tagline: "Aktuelles Update",
    highlights: ["Laufende Verbesserungen und Stabilität"],
    changes: ["Bugfixes und Performance-Optimierungen"]
  });

  const parsedVersion = computed(() => parseVersionParts(APP_VERSION));

  function openPatchnotes(patchIndex = 0) {
    activePatchIndex.value = patchIndex;
    isModalOpen.value = true;
  }

  function closePatchnotes(markAsSeen = true) {
    if (markAsSeen && latestPatch.value?.version) {
      localStorage.setItem("unyq_last_seen_patch", latestPatch.value.version);
    }
    isModalOpen.value = false;
  }

  function checkFirstLoginNotice() {
    const token = localStorage.getItem("access");
    if (!token) return false;

    const currentVer = latestPatch.value?.version || APP_VERSION;
    const lastSeen = localStorage.getItem("unyq_last_seen_patch");

    if (lastSeen !== currentVer) {
      activePatchIndex.value = 0;
      isModalOpen.value = true;
      return true;
    }
    return false;
  }

  return {
    isModalOpen,
    activePatchIndex,
    currentVersion,
    parsedVersion,
    latestPatch,
    allPatches,
    openPatchnotes,
    closePatchnotes,
    checkFirstLoginNotice,
    parseVersionParts
  };
}
