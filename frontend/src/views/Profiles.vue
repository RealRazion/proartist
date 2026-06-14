<template>
  <div :class="['profiles', { compact: compactCards }]">
    <header class="card header">
      <div>
        <h1>{{ adminMode ? "Alle Nutzer" : "Artists entdecken" }}</h1>
        <p class="muted">{{ adminMode ? "Admin-Ansicht: alle Nutzerprofile inklusive Team." : "Suche gezielt nach Artists und Team-Mitgliedern und starte direkt einen Chat." }}</p>
      </div>
      <div class="search-area">
        <input
          class="input search"
          v-model.trim="queryInput"
          placeholder="Filter nach Name, Rolle (z. B. Videograf), Genre oder Stadt..."
        />
        <span class="result-info">
          <span v-if="filtering">Filtert...</span>
          <span v-else>{{ filteredCount }} Treffer</span>
        </span>
        <button
          type="button"
          class="view-toggle"
          :aria-pressed="compactCards"
          @click="toggleCompact"
        >
          {{ compactCards ? "Größere Karten" : "Kompakte Karten" }}
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
          <div class="avatar-wrap">
            <img v-if="profile.avatar_url" :src="asAbsoluteMediaUrl(profile.avatar_url)" :alt="profile.name || profile.username" class="avatar" />
            <img v-else :src="anonymousAvatar" alt="Anonym" class="avatar" />
          </div>
          <div>
            <h2>
              {{ profile.name || profile.username }}
              <span v-if="isTeamMember(profile)" class="team-badge">Team</span>
            </h2>
            <p class="muted">{{ profile.city || "Ort unbekannt" }}</p>
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
        <footer class="footer" :class="{ 'has-actions': profile.id !== me?.id || canManageTeam(profile) }">
          <a v-if="isTeam && profile.email" class="link email" :href="`mailto:${profile.email}`">{{ profile.email }}</a>
          <div v-if="profile.id !== me?.id || canManageTeam(profile)" class="quick-actions">
            <button
              v-if="profile.id !== me?.id"
              class="btn tiny"
              type="button"
              @click="chatWith(profile.id)"
              :disabled="startingChat === profile.id"
            >
              {{ startingChat === profile.id ? "Starte Chat..." : "Chat starten" }}
            </button>
            <button
              v-if="canManageTeam(profile) && !isTeamMember(profile)"
              class="btn ghost tiny"
              type="button"
              @click="toggleTeam(profile, true)"
              :disabled="teamLoading === profile.id"
            >
              Zum Team
            </button>
            <button
              v-if="canManageTeam(profile) && isTeamMember(profile)"
              class="btn ghost tiny"
              type="button"
              @click="toggleTeam(profile, false)"
              :disabled="teamLoading === profile.id"
            >
              Entfernen
            </button>
            <button
              v-if="canManageTeam(profile)"
              class="btn ghost tiny"
              type="button"
              @click="toggleLock(profile)"
              :disabled="lockLoading === profile.id"
            >
              {{ profile.is_locked ? "Entsperren" : "Sperren" }}
            </button>
            <button
              v-if="canManageTeam(profile)"
              class="btn ghost tiny"
              type="button"
              @click="openManage(profile)"
            >
              Rollen
            </button>
          </div>
        </footer>
      </article>
      <p v-if="!filteredProfiles.length" class="empty muted">
        Keine Artists gefunden. Passe deine Suche an.
      </p>
    </section>

    <div v-if="manage.open" class="modal-backdrop" @click.self="closeManage">
      <div class="modal card">
        <header class="modal-head">
          <div>
            <p class="eyebrow">Rechteverwaltung</p>
            <h3>{{ manage.profile?.name || manage.profile?.username || "-" }}</h3>
            <p class="muted">{{ manage.profile?.email || "Keine E-Mail sichtbar" }}</p>
          </div>
          <button class="btn ghost tiny" type="button" @click="closeManage">Schließen</button>
        </header>

        <section v-if="manage.loading" class="modal-body">
          <p class="muted">Lade Profil...</p>
        </section>
        <section v-else class="modal-body">
          <div class="role-grid">
            <label v-for="role in nonTeamRoles" :key="role.id">
              <input type="checkbox" :value="role.id" v-model="manage.roleIds" />
              {{ role.key }}
            </label>
          </div>
          <label class="toggle-line">
            <input type="checkbox" v-model="manage.teamMember" />
            Team-Rechte
          </label>
          <p v-if="manage.error" class="error-msg">{{ manage.error }}</p>
        </section>

        <footer class="modal-actions">
          <button class="btn ghost" type="button" @click="closeManage">Abbrechen</button>
          <button class="btn" type="button" @click="saveManage" :disabled="manage.saving || manage.loading">
            {{ manage.saving ? "Speichere..." : "Speichern" }}
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from "vue";
import { useRouter, useRoute } from "vue-router";
import api, { toAbsoluteMediaUrl } from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const router = useRouter();
const route = useRoute();
const { profile: me, fetchProfile, isAdmin } = useCurrentProfile();
const { showToast } = useToast();

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
const lockLoading = ref(null);
const roles = ref([]);
const manage = ref({
  open: false,
  loading: false,
  profile: null,
  roleIds: [],
  teamMember: false,
  saving: false,
  error: "",
});

const isTeam = computed(() => (me.value?.roles || []).some((r) => ["TEAM", "ADMIN"].includes(r.key)));
const adminMode = computed(() => isAdmin.value && String(route.query.admin || "") === "1");

const anonymousAvatar =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>
      <rect width='120' height='120' fill='#e8ecf3'/>
      <circle cx='60' cy='44' r='22' fill='#b8c2d1'/>
      <rect x='24' y='74' width='72' height='34' rx='17' fill='#c9d2df'/>
    </svg>`
  );

if (typeof window !== "undefined") {
  const saved = window.localStorage.getItem(COMPACT_KEY);
  compactCards.value = saved === "1";
}

const roleLabels = {
  ADMIN: "Admin",
  ARTIST: "Artist",
  MEMBER: "Member",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merchandiser",
  MKT: "Marketing",
  LOC: "Location",
  TEAM: "Team",
};

const roleFilterLabels = {
  ADMIN: "Admins",
  ARTIST: "Artists",
  MEMBER: "Members",
  PROD: "Producer",
  VIDEO: "Videografen",
  MERCH: "Merch",
  MKT: "Marketing",
  LOC: "Locations",
  TEAM: "Team",
};

const roleFilterOrder = ["ADMIN", "TEAM", "ARTIST", "MEMBER", "PROD", "VIDEO", "MERCH", "MKT", "LOC"];

const roleFilterOptions = computed(() => {
  const keys = new Set();
  profiles.value.forEach((profile) => {
    (profile.roles || []).forEach((role) => keys.add(role.key));
  });
  const preferred = roleFilterOrder
    .filter((key) => keys.has(key))
    .map((key) => ({ key, label: roleFilterLabels[key] || roleLabels[key] || key }));
  const custom = Array.from(keys)
    .filter((key) => !roleFilterOrder.includes(key))
    .map((key) => ({ key, label: roleFilterLabels[key] || roleLabels[key] || key }))
    .sort((a, b) => a.label.localeCompare(b.label));
  const rest = [...preferred, ...custom];
  return [{ key: "ALL", label: "Alle Rollen" }, ...rest];
});
const nonTeamRoles = computed(() => roles.value.filter((role) => role.key !== "TEAM"));
const teamRoleId = computed(() => roles.value.find((role) => role.key === "TEAM")?.id || null);

const visibleProfiles = computed(() => {
  if (adminMode.value) return profiles.value;
  return profiles.value.filter((profile) => {
    const keys = (profile.roles || []).map((role) => role.key);
    return keys.includes("TEAM") || keys.includes("ARTIST");
  });
});

const filteredProfiles = computed(() => {
  const term = debouncedQuery.value.trim().toLowerCase();
  return visibleProfiles.value.filter((profile) => {
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

const canManageTeam = (profile) => isAdmin.value && profile.id !== me.value?.id;

const asAbsoluteMediaUrl = (value) => toAbsoluteMediaUrl(value);

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

async function toggleLock(profile) {
  if (!canManageTeam(profile)) return;
  lockLoading.value = profile.id;
  try {
    const { data } = await api.post(`profiles/${profile.id}/lock/`, { locked: !profile.is_locked });
    profile.is_locked = Boolean(data?.locked);
    showToast(profile.is_locked ? "Profil gesperrt" : "Profil entsperrt", "success");
  } catch (err) {
    console.error("Sperren fehlgeschlagen", err);
    showToast("Sperren/Entsperren fehlgeschlagen", "error");
  } finally {
    lockLoading.value = null;
  }
}

function socialLinks(profile) {
  const socials = profile.socials || {};
  const links = [];
  if (socials.instagram) links.push({ icon: "IG", label: "Instagram", url: socials.instagram });
  if (socials.youtube) links.push({ icon: "YT", label: "YouTube", url: socials.youtube });
  if (socials.soundcloud) links.push({ icon: "SC", label: "SoundCloud", url: socials.soundcloud });
  if (socials.tiktok) links.push({ icon: "TT", label: "TikTok", url: socials.tiktok });
  if (socials.spotify) links.push({ icon: "SP", label: "Spotify", url: socials.spotify });
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
  try {
    const { data } = await api.get("profiles/", { params: { page_size: 300 } });
    const rows = Array.isArray(data) ? data : data?.results || [];
    profiles.value = rows.map(decorateProfile);
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    profiles.value = [];
    showToast("Profile konnten nicht geladen werden", "error");
  }
}

async function loadRoles() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("roles/");
    roles.value = Array.isArray(data) ? data : data?.results || [];
  } catch (err) {
    console.error("Rollen konnten nicht geladen werden", err);
    roles.value = [];
  }
}

async function openManage(profile) {
  if (!canManageTeam(profile)) return;
  manage.value.open = true;
  manage.value.loading = true;
  manage.value.error = "";
  try {
    const { data } = await api.get(`profiles/${profile.id}/`);
    manage.value.profile = data;
    manage.value.roleIds = (data.roles || []).filter((role) => role.key !== "TEAM").map((role) => role.id);
    manage.value.teamMember = (data.roles || []).some((role) => role.key === "TEAM");
  } catch (err) {
    console.error("Profil konnte nicht geladen werden", err);
    manage.value.error = "Profil konnte nicht geladen werden.";
  } finally {
    manage.value.loading = false;
  }
}

function closeManage() {
  manage.value.open = false;
  manage.value.loading = false;
  manage.value.profile = null;
  manage.value.roleIds = [];
  manage.value.teamMember = false;
  manage.value.error = "";
}

async function saveManage() {
  if (!manage.value.profile) return;
  manage.value.saving = true;
  manage.value.error = "";
  const nextRoleIds = [...manage.value.roleIds];
  if (manage.value.teamMember && teamRoleId.value) {
    nextRoleIds.push(teamRoleId.value);
  }
  try {
    await api.put(`profiles/${manage.value.profile.id}/`, { role_ids: nextRoleIds });
    showToast("Rollen aktualisiert", "success");
    await loadProfiles();
    closeManage();
  } catch (err) {
    console.error("Rollenupdate fehlgeschlagen", err);
    manage.value.error = "Rollen konnten nicht gespeichert werden.";
  } finally {
    manage.value.saving = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadProfiles(), loadRoles()]);
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
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
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
  background: linear-gradient(135deg, var(--brand), var(--brand-2));
  border-color: transparent;
  color: #fff;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 18px;
  align-items: stretch;
}
.profiles.compact .grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 1280px) {
  .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .profiles.compact .grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
@media (max-width: 980px) {
  .profiles.compact .grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .quick-actions {
    position: static;
    opacity: 1;
    transform: none;
    pointer-events: auto;
  }
  .footer.has-actions {
    padding-right: 0;
  }
  .footer .email {
    max-width: 100%;
  }
}
@media (max-width: 760px) {
  .grid {
    grid-template-columns: 1fr;
  }
  .profiles.compact .grid {
    grid-template-columns: 1fr;
  }
}
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 16px;
  position: relative;
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
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.profile-header > div:nth-child(2) {
  flex: 1;
}
.team-actions {
  margin-left: auto;
}
.avatar-wrap {
  width: 96px;
  aspect-ratio: 1 / 1;
  border-radius: 14px;
  overflow: hidden;
  background: #e8ecf3;
}
.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.profile-card.compact .avatar-wrap {
  width: 72px;
  border-radius: 12px;
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
  flex-wrap: wrap;
  position: relative;
}
.footer.has-actions {
  padding-right: 150px;
}
.footer .email {
  max-width: calc(100% - 150px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.quick-actions {
  position: absolute;
  right: 12px;
  bottom: 12px;
  display: inline-flex;
  gap: 8px;
  opacity: 0;
  transform: translateY(6px);
  pointer-events: none;
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.profile-card:hover .quick-actions,
.profile-card:focus-within .quick-actions {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
.btn.tiny {
  padding: 6px 12px;
  font-size: 12px;
}
@media (hover: none) {
  .quick-actions {
    position: static;
    opacity: 1;
    transform: none;
    pointer-events: auto;
  }
  .footer.has-actions {
    padding-right: 0;
  }
  .footer .email {
    max-width: 100%;
  }
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
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 60;
  padding: 16px;
}
.modal {
  width: min(560px, 100%);
  max-height: 88vh;
  overflow: auto;
  display: grid;
  gap: 12px;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: flex-start;
}
.modal-head h3 {
  margin: 4px 0;
}
.modal-body {
  display: grid;
  gap: 10px;
}
.role-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
}
.role-grid label {
  display: flex;
  align-items: center;
  gap: 8px;
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 8px 10px;
  background: var(--surface);
  font-size: 13px;
}
.toggle-line {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}
.empty {
  grid-column: 1 / -1;
  text-align: center;
  padding: 24px 0;
}
</style>

