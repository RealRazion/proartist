<template>
  <div :class="['profiles', { compact: compactCards }]">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
    <header class="card header">
      <div>
        <h1>Profiles entdecken</h1>
        <p class="muted">Suche nach Artists, Produzenten oder Locations und starte direkt einen Chat.</p>
      </div>
      <div class="search-area">
        <input
          class="input search"
          v-model.trim="queryInput"
          placeholder="Filter nach Name, Rolle, Genre oder Stadt..."
        />
        <span class="result-info">
          <span v-if="filtering">? Filtert...</span>
          <span v-else>{{ filteredCount }} Treffer</span>
        </span>
        <button
          type="button"
          class="view-toggle"
          :aria-pressed="compactCards"
          @click="toggleCompact"
        >
          {{ compactCards ? "Groessere Karten" : "Kompakte Karten" }}
        </button>
      </div>
    </header>

    <div class="filters card">
      <button
        v-for="role in roleFilterOptions"
        :key="role.key"
        type="button"
        class="filter-chip"
        :class="{ active: roleFilter === role.key }"
        @click="setRoleFilter(role.key)"
      >
        {{ role.label }}
      </button>
    </div>

    <section class="grid">
      <article
        v-for="profile in filteredProfiles"
        :key="profile.id"
        :class="['card profile-card', { compact: compactCards }]"
      >
        <div class="profile-header">
          <div class="avatar">{{ profile.initials }}</div>
          <div>
            <h2>
              {{ profile.name || profile.username }}
              <span v-if="isTeamMember(profile)" class="team-badge">Team</span>
            </h2>
            <p class="muted">{{ profile.city || "Ort unbekannt" }}</p>
          </div>
          <div v-if="canManageTeam(profile)" class="team-actions">
            <button
              class="btn tiny"
              type="button"
              v-if="!isTeamMember(profile)"
              @click="toggleTeam(profile, true)"
              :disabled="teamLoading === profile.id"
            >
              Zum Team
            </button>
            <button
              class="btn ghost tiny"
              type="button"
              v-else
              @click="toggleTeam(profile, false)"
              :disabled="teamLoading === profile.id"
            >
              Entfernen
            </button>
          </div>
        </div>
        <div class="roles" v-if="profile.roles?.length">
          <span v-for="role in profile.roles" :key="role.id" class="role-pill">
            {{ roleLabels[role.key] || role.key }}
          </span>
        </div>
        <p class="muted">{{ profile.genre || "Kein Genre angegeben" }}</p>
        <div v-if="socialLinks(profile).length" class="socials">
          <a
            v-for="link in socialLinks(profile)"
            :key="link.label"
            class="social-link"
            :href="link.url"
            target="_blank"
            rel="noopener"
            :title="link.label"
          >
            {{ link.icon }}
          </a>
        </div>
        <footer class="footer">
          <a v-if="profile.email" class="link" :href="`mailto:${profile.email}`">{{ profile.email }}</a>
          <button
            v-if="profile.id !== me?.id"
            class="btn"
            type="button"
            @click="chatWith(profile.id)"
            :disabled="startingChat === profile.id"
          >
            {{ startingChat === profile.id ? "Starte Chat…" : "Chat starten" }}
          </button>
        </footer>
      </article>
      <p v-if="!filteredProfiles.length" class="empty muted">
        Keine Profile gefunden. Passe deine Suche an.
      </p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";

const router = useRouter();
const route = useRoute();
const { profile: me, fetchProfile } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();

const COMPACT_KEY = "profiles:compactMode";
const profiles = ref([]);
const queryInput = ref("");
const debouncedQuery = ref("");
const startingChat = ref(null);
const roleFilter = ref("ALL");
const filtering = ref(false);
const compactCards = ref(false);
let debounceTimer = null;
const teamLoading = ref(null);

const isTeam = computed(() => (me.value?.roles || []).some((r) => r.key === "TEAM"));

if (typeof window !== "undefined") {
  const saved = window.localStorage.getItem(COMPACT_KEY);
  compactCards.value = saved === "1";
}

const roleLabels = {
  ARTIST: "Artist",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merchandiser",
  MKT: "Marketing",
  LOC: "Location",
  TEAM: "Team",
};

const roleFilterOptions = computed(() => {
  const keys = new Set();
  profiles.value.forEach((profile) => {
    (profile.roles || []).forEach((role) => keys.add(role.key));
  });
  const rest = Array.from(keys)
    .map((key) => ({ key, label: roleLabels[key] || key }))
    .sort((a, b) => a.label.localeCompare(b.label));
  return [{ key: "ALL", label: "Alle Rollen" }, ...rest];
});

const filteredProfiles = computed(() => {
  const term = debouncedQuery.value.trim().toLowerCase();
  return profiles.value.filter((profile) => {
    const haystack = [
      profile.name,
      profile.username,
      profile.city,
      profile.genre,
      ...(profile.roles || []).map((role) => roleLabels[role.key] || role.key),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    const matchesText = !term || haystack.includes(term);
    const matchesRole =
      roleFilter.value === "ALL" ||
      (profile.roles || []).some((role) => role.key === roleFilter.value);
    return matchesText && matchesRole;
  });
});
const filteredCount = computed(() => filteredProfiles.value.length);

function toggleCompact() {
  compactCards.value = !compactCards.value;
}

function decorateProfile(profile) {
  const name = profile.name || profile.username || "";
  const initials = name
    .split(" ")
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  return { ...profile, initials: initials || "PR" };
}

async function chatWith(profileId) {
  startingChat.value = profileId;
  try {
    const { data } = await api.post("threads/ensure/", { profile_id: profileId });
    if (typeof window !== "undefined") {
      sessionStorage.setItem("chat:pendingThread", String(data.id));
    }
    await router.push({ path: "/app/chats", query: { thread: data.id } });
  } catch (err) {
    console.error("Chat konnte nicht gestartet werden", err);
    if (typeof window !== "undefined") {
      window.alert("Chat konnte nicht gestartet werden. Bitte versuche es erneut.");
    }
  } finally {
    startingChat.value = null;
  }
}

function isTeamMember(profile) {
  return (profile.roles || []).some((role) => role.key === "TEAM");
}

const canManageTeam = (profile) => isTeam.value && profile.id !== me.value?.id;

async function toggleTeam(profile, add) {
  if (!canManageTeam(profile)) return;
  teamLoading.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/team-role/`, { add });
    await loadProfiles();
    showToast(add ? "Zum Team hinzugefügt" : "Aus Team entfernt", "success");
  } catch (err) {
    console.error("Team-Update fehlgeschlagen", err);
    showToast("Aktion fehlgeschlagen", "error");
  } finally {
    teamLoading.value = null;
  }
}

function socialLinks(profile) {
  const socials = profile.socials || {};
  const links = [];
  if (socials.instagram) links.push({ icon: "??", label: "Instagram", url: socials.instagram });
  if (socials.youtube) links.push({ icon: "??", label: "YouTube", url: socials.youtube });
  if (socials.soundcloud) links.push({ icon: "??", label: "SoundCloud", url: socials.soundcloud });
  if (socials.tiktok) links.push({ icon: "??", label: "TikTok", url: socials.tiktok });
  if (socials.spotify) links.push({ icon: "??", label: "Spotify", url: socials.spotify });
  return links;
}

function setRoleFilter(key) {
  if (key === "ALL") {
    roleFilter.value = "ALL";
    return;
  }
  roleFilter.value = roleFilter.value === key ? "ALL" : key;
}

async function loadProfiles() {
  const { data } = await api.get("profiles/");
  profiles.value = data.map(decorateProfile);
}

onMounted(async () => {
  await fetchProfile();
  await loadProfiles();
  const initialSearch = route.query.q;
  if (initialSearch) {
    const value = String(initialSearch);
    queryInput.value = value;
    debouncedQuery.value = value;
  }
});

watch(
  () => queryInput.value,
  (value) => {
    filtering.value = true;
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      debouncedQuery.value = value;
      filtering.value = false;
    }, 250);
  }
);

watch(
  () => compactCards.value,
  (value) => {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(COMPACT_KEY, value ? "1" : "0");
    }
  }
);

watch(
  () => route.query.q,
  (value) => {
    const normalized = value ? String(value) : "";
    if (normalized !== queryInput.value) {
      queryInput.value = normalized;
      debouncedQuery.value = normalized;
    }
  }
);

onBeforeUnmount(() => {
  if (debounceTimer) clearTimeout(debounceTimer);
});
</script>

<style scoped>
.profiles {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}
.header {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.search {
  max-width: 400px;
}
.search-area {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}
.result-info {
  font-size: 12px;
  color: var(--muted);
}
.view-toggle {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s ease, border 0.2s ease;
}
.view-toggle[aria-pressed="true"] {
  background: rgba(112, 130, 255, 0.18);
  color: #fff;
  border-color: transparent;
}
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px 12px;
  overflow-x: auto;
}
.filter-chip {
  border: 1px solid var(--border);
  background: transparent;
  color: var(--text);
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
  transition: background 0.2s ease, border 0.2s ease;
}
.filter-chip:hover {
  border-color: var(--brand);
}
.filter-chip.active {
  background: rgba(112, 130, 255, 0.18);
  border-color: transparent;
  color: #fff;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
  gap: 10px;
}
.profiles.compact .grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px;
}
.profiles.compact .grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
}
.profile-card.compact {
  gap: 8px;
  padding: 10px;
  font-size: 13px;
}
.profiles.compact .profile-card .muted {
  font-size: 12px;
}
.profiles.compact .profile-card .roles {
  display: none;
}
.profiles.compact .profile-card .socials {
  display: none;
}
.profile-card h2 {
  margin: 0;
  font-size: 1.05rem;
}
.profile-card.compact h2 {
  font-size: 1rem;
}
.profile-card p {
  margin: 0;
}
.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.avatar {
  width: 40px;
  height: 40px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 18px;
}
.profile-card.compact .avatar {
  width: 36px;
  height: 36px;
  border-radius: 12px;
  font-size: 16px;
}
.profiles.compact .footer {
  flex-direction: column;
  align-items: flex-start;
  gap: 6px;
}
.roles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.profile-card.compact .roles {
  gap: 6px;
}
.socials {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.social-link {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(75, 91, 255, 0.16);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  text-decoration: none;
}
.team-badge {
  margin-left: 8px;
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(124, 58, 237, 0.16);
  color: var(--brand-2);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}
.role-pill {
  padding: 4px 10px;
  background: rgba(75, 91, 255, 0.12);
  color: var(--brand);
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.profile-card.compact .role-pill {
  font-size: 11px;
  padding: 3px 8px;
}
.footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.link {
  color: var(--brand);
  text-decoration: none;
  font-size: 14px;
}
.link:hover {
  text-decoration: underline;
}
.btn {
  white-space: nowrap;
}
.empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 24px 0;
}
</style>

