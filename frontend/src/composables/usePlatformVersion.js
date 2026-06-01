import { computed, ref, watch } from "vue";
import {
  fetchManagedPlatformAccessState,
  mapAccessStateRows,
  routeNameToPlatformSlug,
} from "../services/managedPlatforms";

export function usePlatformVersion(routeRef) {
  const stateBySlug = ref({});
  const loading = ref(false);

  async function refresh({ force = false } = {}) {
    loading.value = true;
    try {
      const rows = await fetchManagedPlatformAccessState({ force });
      stateBySlug.value = mapAccessStateRows(rows);
    } catch {
      stateBySlug.value = {};
    } finally {
      loading.value = false;
    }
  }

  watch(
    () => routeRef?.value?.name,
    async (routeName) => {
      const slug = routeName ? routeNameToPlatformSlug(routeName) : null;
      if (!slug) return;
      if (!stateBySlug.value[slug]) {
        await refresh();
      }
    },
    { immediate: true }
  );

  const platformSlug = computed(() => routeNameToPlatformSlug(routeRef?.value?.name));
  const platformState = computed(() => {
    const slug = platformSlug.value;
    return slug ? stateBySlug.value[slug] || null : null;
  });

  const platformVersion = computed(() => platformState.value?.version || "0.1");

  return {
    loading,
    refresh,
    platformSlug,
    platformState,
    platformVersion,
  };
}
