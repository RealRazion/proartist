<template>
  <div class="team-roles">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />

    <header class="card hero">
      <div>
        <p class="eyebrow">Teamverwaltung</p>
        <h1>Rollen & Zugriffe</h1>
        <p class="muted">Verwalte Team-Rollen, sperre Profile und behalte den Status im Blick.</p>
      </div>
      <div class="hero-actions">
        <input class="input search" v-model.trim="search" placeholder="Suche nach Namen oder Username" />
        <select class="input" v-model="filterRole">
          <option value="ALL">Alle Rollen</option>
          <option value="TEAM">Team</option>
          <option value="NON_TEAM">Ohne Team</option>
        </select>
        <button class="btn ghost" type="button" @click="loadProfiles" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
    </header>

    <section class="card table-card">
      <table>
        <thead>
          <tr>
            <th>Name</th>
            <th>Username</th>
            <th>Rollen</th>
            <th>Status</th>
            <th>Aktionen</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="profile in filteredProfiles" :key="profile.id">
            <td>{{ profile.name || "—" }}</td>
            <td>{{ profile.username }}</td>
            <td>
              <span
                v-for="role in profile.roles"
                :key="role.id"
                class="chip"
                :class="{ team: role.key === 'TEAM' }"
              >
                {{ roleLabels[role.key] || role.key }}
              </span>
            </td>
            <td>
              <span class="status" :class="{ locked: profile.is_locked }">
                {{ profile.is_locked ? "Gesperrt" : "Aktiv" }}
              </span>
            </td>
            <td class="actions">
              <button
                class="btn ghost tiny"
                type="button"
                @click="toggleTeamRole(profile)"
                :disabled="actionLoading === profile.id"
              >
                {{ isTeamMember(profile) ? "Team entfernen" : "Zum Team" }}
              </button>
              <button
                class="btn ghost tiny"
                type="button"
                @click="toggleLock(profile)"
                :disabled="actionLoading === profile.id"
              >
                {{ profile.is_locked ? "Entsperren" : "Sperren" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!filteredProfiles.length && !loading" class="muted empty">Keine Profile gefunden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();
const { toast, showToast, hideToast } = useToast();

const profiles = ref([]);
const loading = ref(false);
const actionLoading = ref(null);
const search = ref("");
const filterRole = ref("ALL");

const roleLabels = {
  ARTIST: "Artist",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merch",
  MKT: "Marketing",
  LOC: "Location",
  TEAM: "Team",
};

const filteredProfiles = computed(() => {
  const term = search.value.trim().toLowerCase();
  return profiles.value.filter((profile) => {
    const matchesSearch =
      !term ||
      profile.name?.toLowerCase().includes(term) ||
      profile.username?.toLowerCase().includes(term);
    const teamMember = isTeamMember(profile);
    const matchesRole =
      filterRole.value === "ALL" ||
      (filterRole.value === "TEAM" && teamMember) ||
      (filterRole.value === "NON_TEAM" && !teamMember);
    return matchesSearch && matchesRole;
  });
});

function isTeamMember(profile) {
  return (profile.roles || []).some((role) => role.key === "TEAM");
}

async function loadProfiles() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("profiles/");
    profiles.value = data;
  } catch (err) {
    console.error("Profile konnten nicht geladen werden", err);
    showToast("Profile konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function toggleTeamRole(profile) {
  actionLoading.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/team-role/`, { add: !isTeamMember(profile) });
    await loadProfiles();
    showToast("Rolle aktualisiert", "success");
  } catch (err) {
    console.error("Rolle konnte nicht geändert werden", err);
    showToast("Rolle konnte nicht geändert werden", "error");
  } finally {
    actionLoading.value = null;
  }
}

async function toggleLock(profile) {
  actionLoading.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/lock/`, { locked: !profile.is_locked });
    await loadProfiles();
    showToast(profile.is_locked ? "Profil entsperrt" : "Profil gesperrt", "success");
  } catch (err) {
    console.error("Profil konnte nicht aktualisiert werden", err);
    showToast("Profil konnte nicht aktualisiert werden", "error");
  } finally {
    actionLoading.value = null;
  }
}

onMounted(() => {
  if (isTeam.value) {
    loadProfiles();
  }
});
</script>

<style scoped>
.team-roles {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  flex-wrap: wrap;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: flex-end;
}
.hero-actions .search {
  min-width: 200px;
}
.table-card {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  text-align: left;
  padding: 12px 8px;
  border-bottom: 1px solid rgba(148, 163, 184, 0.3);
}
th {
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.chip {
  display: inline-flex;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.15);
  margin: 2px;
  font-size: 12px;
}
.chip.team {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}
.status {
  font-weight: 600;
}
.status.locked {
  color: #dc2626;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.empty {
  text-align: center;
  margin: 12px 0 0;
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
  }
  table {
    font-size: 14px;
  }
}
</style>
