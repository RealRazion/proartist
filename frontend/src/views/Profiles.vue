<template>
  <div class="profiles">
    <header class="card header">
      <div>
        <h1>Profiles entdecken</h1>
        <p class="muted">Suche nach Artists, Produzenten oder Locations und starte direkt einen Chat.</p>
      </div>
      <input
        class="input search"
        v-model.trim="query"
        placeholder="Filter nach Name, Rolle, Genre oder Stadt…"
      />
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
      <article v-for="profile in filteredProfiles" :key="profile.id" class="card profile-card">
        <div class="profile-header">
          <div class="avatar">{{ profile.initials }}</div>
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
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const { profile: me, fetchProfile } = useCurrentProfile();

const profiles = ref([]);
const query = ref("");
const startingChat = ref(null);
const roleFilter = ref("ALL");

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
  const term = query.value.trim().toLowerCase();
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

function setRoleFilter(key) {
  if (key === "ALL") {
    roleFilter.value = "ALL";
    return;
  }
  roleFilter.value = roleFilter.value === key ? "ALL" : key;
}

onMounted(async () => {
  await fetchProfile();
  const { data } = await api.get("profiles/");
  profiles.value = data.map(decorateProfile);
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
.profile-card {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 14px;
}
.profile-card h2 {
  margin: 0;
  font-size: 1.05rem;
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
.roles {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
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
