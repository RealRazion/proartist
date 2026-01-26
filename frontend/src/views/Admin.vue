<template>
  <div class="admin wide">
    <header class="card header">
      <div>
        <h1>Admin Dashboard</h1>
        <p class="muted">?berblick ?ber Nutzer, Projekte und kritische Werte.</p>
      </div>
      <button class="btn ghost" type="button" @click="refresh" :disabled="loading">
        {{ loading ? "Aktualisiere..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Kein Zugriff</h2>
      <p class="muted">Nur Team-Mitglieder mit Admin-Rechten können dieses Modul verwenden.</p>
    </section>

    <section v-else class="metrics card">
      <div class="tile">
        <p class="label">Nutzer gesamt</p>
        <strong>{{ metrics.total_users }}</strong>
      </div>
      <div class="tile">
        <p class="label">Gesperrt</p>
        <strong>{{ metrics.locked_users }}</strong>
      </div>
      <div class="tile">
        <p class="label">Team-Mitglieder</p>
        <strong>{{ metrics.team_members }}</strong>
      </div>
      <div class="tile">
        <p class="label">Neue Nutzer (7T)</p>
        <strong>{{ metrics.new_users_last_7_days }}</strong>
      </div>
      <div class="tile">
        <p class="label">Aktive Projekte</p>
        <strong>{{ metrics.active_projects }}</strong>
      </div>
      <div class="tile alert">
        <p class="label">Überfällige Tasks</p>
        <strong>{{ metrics.overdue_tasks }}</strong>
      </div>
    </section>

    <section v-if="isTeam" class="card users">
      <h2>Userverwaltung</h2>
      <div class="table-head">
        <input class="input" v-model.trim="userSearch" placeholder="Nutzer suchen..." />
      </div>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>E-Mail</th>
              <th>Rollen</th>
              <th>Status</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="profile in filteredProfiles" :key="profile.id">
              <td>{{ profile.name || profile.username }}</td>
              <td>{{ profile.email }}</td>
              <td>{{ profile.roles.map((r) => r.key).join(", ") || "-" }}</td>
              <td>
                <span class="badge" :class="{ danger: profile.is_locked }">
                  {{ profile.is_locked ? "Gesperrt" : "Aktiv" }}
                </span>
                <span v-if="profile.is_team_member" class="badge team">Team</span>
              </td>
              <td class="actions">
                <button class="btn ghost tiny" type="button" @click="openManage(profile)">
                  Verwalten
                </button>
                <button class="btn ghost tiny" type="button" @click="toggleLock(profile)" :disabled="savingId === profile.id">
                  {{ profile.is_locked ? "Entsperren" : "Sperren" }}
                </button>
                <button class="btn ghost tiny" type="button" @click="toggleTeam(profile)" :disabled="savingId === profile.id">
                  {{ profile.is_team_member ? "Team entfernen" : "Team zuweisen" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <div v-if="manage.open" class="modal-backdrop">
      <div class="modal card">
        <header>
          <div>
            <p class="eyebrow">User verwalten</p>
            <h3>{{ manage.profile?.name || manage.profile?.username || "-" }}</h3>
            <p class="muted">{{ manage.profile?.email }}</p>
          </div>
          <button class="btn ghost tiny" type="button" @click="closeManage">Schließen</button>
        </header>
        <section v-if="manage.loading" class="modal-body">
          <p class="muted">Lade Daten...</p>
        </section>
        <section v-else class="modal-body">
          <div class="info-block">
            <p><strong>Stadt:</strong> {{ manage.profile?.city || "-" }}</p>
            <p><strong>Genre:</strong> {{ manage.profile?.genre || "-" }}</p>
            <p><strong>Erstellt:</strong> {{ formatDateDisplay(manage.profile?.created_at) }}</p>
          </div>
          <div class="roles-block">
            <h4>Rollen</h4>
            <div class="role-grid">
              <label v-for="role in nonTeamRoles" :key="role.id">
                <input type="checkbox" :value="role.id" v-model="manage.roleIds" />
                {{ role.key }}
              </label>
            </div>
            <label class="toggle">
              <input type="checkbox" v-model="manage.teamMember" />
              Team-Rechte
            </label>
          </div>
          <p v-if="manage.error" class="error">{{ manage.error }}</p>
        </section>
        <footer class="modal-footer">
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
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();
const loading = ref(false);
const metrics = ref({
  total_users: 0,
  locked_users: 0,
  team_members: 0,
  new_users_last_7_days: 0,
  active_projects: 0,
  overdue_tasks: 0,
});
const profiles = ref([]);
const userSearch = ref("");
const savingId = ref(null);
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

const filteredProfiles = computed(() => {
  const term = userSearch.value.trim().toLowerCase();
  if (!term) return profiles.value;
  return profiles.value.filter((profile) =>
    `${profile.name} ${profile.username} ${profile.email}`.toLowerCase().includes(term)
  );
});

const nonTeamRoles = computed(() =>
  roles.value.filter((role) => role.key !== "TEAM")
);

const teamRoleId = computed(() => roles.value.find((role) => role.key === "TEAM")?.id || null);

async function loadMetrics() {
  const { data } = await api.get("admin/overview/");
  metrics.value = data;
}

async function loadProfiles() {
  const { data } = await api.get("profiles/");
  profiles.value = data;
}

function formatDateDisplay(value) {
  if (!value) return "-";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" }).format(new Date(value));
}

async function loadRoles() {
  const { data } = await api.get("roles/");
  roles.value = data;
}

async function refresh() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    await Promise.all([loadMetrics(), loadProfiles(), loadRoles()]);
  } catch (err) {
    console.error("Admin Daten konnten nicht geladen werden", err);
  } finally {
    loading.value = false;
  }
}

async function toggleLock(profile) {
  savingId.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/lock/`, { locked: !profile.is_locked });
    profile.is_locked = !profile.is_locked;
  } catch (err) {
    console.error("Lock/Unlock fehlgeschlagen", err);
  } finally {
    savingId.value = null;
  }
}

async function toggleTeam(profile) {
  savingId.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/team-role/`, { add: !profile.is_team_member });
    profile.is_team_member = !profile.is_team_member;
  } catch (err) {
    console.error("Teamzuweisung fehlgeschlagen", err);
  } finally {
    savingId.value = null;
  }
}

async function openManage(profile) {
  manage.value.open = true;
  manage.value.loading = true;
  manage.value.error = "";
  try {
    const { data } = await api.get(`profiles/${profile.id}/`);
    manage.value.profile = data;
    manage.value.roleIds = (data.roles || [])
      .filter((role) => role.key !== "TEAM")
      .map((role) => role.id);
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
  manage.value.profile = null;
  manage.value.roleIds = [];
  manage.value.teamMember = false;
  manage.value.error = "";
}

async function saveManage() {
  if (!manage.value.profile) return;
  manage.value.saving = true;
  manage.value.error = "";
  const payloadRoleIds = [...manage.value.roleIds];
  if (manage.value.teamMember && teamRoleId.value) {
    payloadRoleIds.push(teamRoleId.value);
  }
  try {
    const { data } = await api.put(`profiles/${manage.value.profile.id}/`, {
      role_ids: payloadRoleIds,
    });
    manage.value.profile = data;
    const idx = profiles.value.findIndex((p) => p.id === data.id);
    if (idx >= 0) {
      profiles.value[idx] = data;
    }
    closeManage();
  } catch (err) {
    console.error("Rollen konnten nicht gespeichert werden", err);
    manage.value.error = "Rollen konnten nicht gespeichert werden.";
  } finally {
    manage.value.saving = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  await refresh();
});
</script>

<style scoped>
.admin {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}
.info {
  max-width: 600px;
}
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}
.tile {
  border: 1px solid rgba(15, 23, 42, 0.08);
  border-radius: 12px;
  padding: 16px;
}
.tile .label {
  margin: 0 0 4px;
  font-size: 13px;
  color: var(--muted);
}
.tile strong {
  font-size: 1.6rem;
}
.tile.alert {
  background: rgba(248, 113, 113, 0.1);
  border-color: rgba(248, 113, 113, 0.4);
}
.users .table-head {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}
.table-wrap {
  overflow-x: auto;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th,
td {
  text-align: left;
  padding: 10px;
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
  font-size: 14px;
}
th {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
}
.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.btn.tiny {
  padding: 4px 12px;
  font-size: 12px;
}
.badge {
  padding: 2px 8px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.15);
  color: #15803d;
  font-size: 12px;
  font-weight: 600;
}
.badge.danger {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.badge.team {
  background: rgba(59, 130, 246, 0.18);
  color: #1d4ed8;
  margin-left: 4px;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 20px;
}
.modal {
  max-width: 560px;
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.modal .eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-size: 12px;
  color: var(--muted);
  margin: 0 0 4px;
}
.modal-body {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.info-block {
  display: grid;
  gap: 6px;
  font-size: 14px;
}
.roles-block {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.role-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 8px;
  font-size: 14px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
.error {
  color: #dc2626;
  margin: 0;
}
@media (max-width: 900px) {
  .metrics {
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  }
  th,
  td {
    font-size: 13px;
  }
}
</style>

