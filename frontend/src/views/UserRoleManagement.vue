<template>
  <div class="user-role-management">
    <header class="card hero">
      <div>
        <p class="eyebrow">Admin Control Hub</p>
        <h1>Nutzer- und Rollenverwaltung</h1>
        <p class="muted">
          Eigenständige Plattform für Nutzer, Rollenhierarchie und Rechte je Rolle.
        </p>
        <div class="hierarchy">Hierarchie: <strong>Admin > Team > Artist > Member</strong></div>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="reloadAll" :disabled="loading">Neu laden</button>
      </div>
    </header>

    <section v-if="!isAdmin" class="card blocked">
      <h2>Kein Zugriff</h2>
      <p class="muted">Diese Plattform ist nur für Admin-Accounts freigeschaltet.</p>
    </section>

    <template v-else>
      <section class="card matrix">
        <div class="matrix-head">
          <div>
            <h2>Rollenrechte nach Plattform</h2>
            <p class="muted">Lege fest, auf welche Plattformen Team, Artist und Member zugreifen dürfen.</p>
          </div>
          <span class="muted small" v-if="savingPolicy">Speichere Rechte...</span>
        </div>
        <div class="matrix-table-wrap">
          <table class="matrix-table">
            <thead>
              <tr>
                <th>Rolle</th>
                <th v-for="platform in matrixPlatforms" :key="platform.slug">{{ platform.name }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="roleKey in matrixRoleKeys" :key="roleKey">
                <td>{{ roleLabel(roleKey) }}</td>
                <td v-for="platform in matrixPlatforms" :key="`${roleKey}-${platform.slug}`">
                  <input
                    type="checkbox"
                    :checked="isAllowed(roleKey, platform.slug)"
                    @change="updateRoleAccess(roleKey, platform.slug, $event.target.checked)"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section class="card users">
        <div class="users-head">
          <div>
            <h2>Nutzer</h2>
            <p class="muted">Große Karten mit Avatar, Rang und Rollen.</p>
          </div>
          <input class="input search" v-model.trim="query" placeholder="Suche nach Name, Rolle, Stadt..." />
        </div>

        <div class="grid">
          <article v-for="profile in filteredProfiles" :key="profile.id" class="profile-card">
            <div class="avatar-wrap">
              <img v-if="profile.avatar_url" :src="asAbsoluteMediaUrl(profile.avatar_url)" :alt="profile.name || profile.username" class="avatar-img" />
              <img v-else :src="anonymousAvatar" alt="Anonym" class="avatar-img" />
            </div>
            <div class="meta">
              <h3>{{ profile.name || profile.username }}</h3>
              <p class="muted">{{ profile.city || "Ort unbekannt" }}</p>
              <p class="rank">{{ roleLabel(primaryRole(profile)) }}</p>
            </div>
            <div class="roles">
              <span v-for="role in profile.roles" :key="role.id" class="pill">{{ roleLabel(role.key) }}</span>
            </div>
            <div class="actions">
              <button class="btn tiny" type="button" @click="openManage(profile)">Bearbeiten</button>
              <button class="btn ghost tiny" type="button" @click="toggleLock(profile)" :disabled="lockLoading === profile.id">
                {{ profile.is_locked ? "Entsperren" : "Sperren" }}
              </button>
            </div>
          </article>
        </div>
      </section>
    </template>

    <div v-if="manage.open" class="modal-backdrop" @click.self="closeManage">
      <div class="modal card">
        <header class="modal-head">
          <h3>{{ manage.profile?.name || manage.profile?.username }}</h3>
          <button class="btn ghost tiny" type="button" @click="closeManage">Schließen</button>
        </header>

        <section class="modal-body">
          <label>
            <span>Hierarchie-Rolle</span>
            <select class="input" v-model="manage.primaryRoleKey">
              <option v-for="key in hierarchyRoleKeys" :key="key" :value="key">{{ roleLabel(key) }}</option>
            </select>
          </label>

          <div class="extras">
            <p class="muted small">Zusatzrollen</p>
            <label v-for="role in extraRoles" :key="role.id" class="extra-row">
              <input type="checkbox" :value="role.id" v-model="manage.extraRoleIds" />
              <span>{{ roleLabel(role.key) }}</span>
            </label>
          </div>

          <p v-if="manage.error" class="error-msg">{{ manage.error }}</p>
        </section>

        <footer class="modal-actions">
          <button class="btn ghost" type="button" @click="closeManage">Abbrechen</button>
          <button class="btn" type="button" @click="saveManage" :disabled="manage.saving">
            {{ manage.saving ? "Speichere..." : "Speichern" }}
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api, { toAbsoluteMediaUrl } from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { profile: me, fetchProfile, isAdmin } = useCurrentProfile();
const { showToast } = useToast();

const loading = ref(false);
const profiles = ref([]);
const roles = ref([]);
const policies = ref([]);
const platforms = ref([]);
const query = ref("");
const savingPolicy = ref(false);
const lockLoading = ref(null);

const hierarchyRoleKeys = ["ADMIN", "TEAM", "ARTIST", "MEMBER"];

const manage = ref({
  open: false,
  saving: false,
  error: "",
  profile: null,
  primaryRoleKey: "MEMBER",
  extraRoleIds: [],
});

const anonymousAvatar =
  "data:image/svg+xml;utf8," +
  encodeURIComponent(
    `<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 120 120'>
      <rect width='120' height='120' fill='#e8ecf3'/>
      <circle cx='60' cy='44' r='22' fill='#b8c2d1'/>
      <rect x='24' y='74' width='72' height='34' rx='17' fill='#c9d2df'/>
    </svg>`
  );

const roleNameMap = {
  ADMIN: "Admin",
  TEAM: "Team",
  ARTIST: "Artist",
  MEMBER: "Member",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merch",
  MKT: "Marketing",
  LOC: "Location",
};

const matrixRoleKeys = ["TEAM", "ARTIST", "MEMBER"];

const matrixPlatforms = computed(() =>
  (platforms.value || [])
    .map((p) => ({ slug: p.slug, name: p.name }))
    .sort((a, b) => a.name.localeCompare(b.name))
);

const filteredProfiles = computed(() => {
  const term = query.value.toLowerCase();
  return profiles.value.filter((profile) => {
    if (!term) return true;
    const text = [
      profile.name,
      profile.username,
      profile.city,
      ...(profile.roles || []).map((role) => role.key),
    ]
      .filter(Boolean)
      .join(" ")
      .toLowerCase();
    return text.includes(term);
  });
});

const extraRoles = computed(() =>
  roles.value.filter((role) => !hierarchyRoleKeys.includes(role.key))
);

function roleLabel(key) {
  return roleNameMap[key] || key;
}

function primaryRole(profile) {
  const keys = (profile.roles || []).map((r) => r.key);
  if (keys.includes("ADMIN")) return "ADMIN";
  if (keys.includes("TEAM")) return "TEAM";
  if (keys.includes("ARTIST")) return "ARTIST";
  return "MEMBER";
}

function policyFor(roleKey) {
  return policies.value.find((row) => row.role_key === roleKey) || null;
}

function isAllowed(roleKey, slug) {
  const policy = policyFor(roleKey);
  if (!policy) return true;
  const rules = policy.access_rules || {};
  if (!(slug in rules)) return true;
  return Boolean(rules[slug]);
}

async function reloadAll() {
  loading.value = true;
  try {
    await fetchProfile(true);
    if (!isAdmin.value) return;
    const [profilesRes, rolesRes, policiesRes, platformsRes] = await Promise.all([
      api.get("profiles/", { params: { page_size: 400 } }),
      api.get("roles/"),
      api.get("role-access-policies/"),
      api.get("manage-platforms/access-state/"),
    ]);
    profiles.value = Array.isArray(profilesRes.data) ? profilesRes.data : profilesRes.data?.results || [];
    roles.value = Array.isArray(rolesRes.data) ? rolesRes.data : rolesRes.data?.results || [];
    policies.value = Array.isArray(policiesRes.data) ? policiesRes.data : policiesRes.data?.results || [];
    platforms.value = Array.isArray(platformsRes.data) ? platformsRes.data : [];
  } catch (err) {
    console.error("UserRoleManagement load failed", err);
    showToast("Daten konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function updateRoleAccess(roleKey, slug, checked) {
  if (!isAdmin.value) return;
  savingPolicy.value = true;
  try {
    let policy = policyFor(roleKey);
    if (!policy) {
      const created = await api.post("role-access-policies/", { role_key: roleKey, access_rules: { [slug]: checked } });
      policies.value.push(created.data);
    } else {
      const nextRules = { ...(policy.access_rules || {}), [slug]: checked };
      const updated = await api.put(`role-access-policies/${policy.id}/`, {
        role_key: policy.role_key,
        access_rules: nextRules,
      });
      policies.value = policies.value.map((row) => (row.id === policy.id ? updated.data : row));
    }
    showToast("Rollenrechte gespeichert", "success");
  } catch (err) {
    console.error("policy update failed", err);
    showToast("Rollenrechte konnten nicht gespeichert werden", "error");
  } finally {
    savingPolicy.value = false;
  }
}

function openManage(profile) {
  const keys = (profile.roles || []).map((r) => r.key);
  const primary = keys.includes("ADMIN")
    ? "ADMIN"
    : keys.includes("TEAM")
      ? "TEAM"
      : keys.includes("ARTIST")
        ? "ARTIST"
        : "MEMBER";
  const primaryRole = roles.value.find((r) => r.key === primary);
  const extra = (profile.roles || [])
    .filter((r) => !hierarchyRoleKeys.includes(r.key))
    .map((r) => r.id);

  manage.value = {
    open: true,
    saving: false,
    error: "",
    profile,
    primaryRoleKey: primaryRole?.key || "MEMBER",
    extraRoleIds: extra,
  };
}

function closeManage() {
  manage.value.open = false;
}

async function saveManage() {
  if (!manage.value.profile) return;
  manage.value.saving = true;
  manage.value.error = "";
  try {
    const selectedHierarchy = roles.value.find((r) => r.key === manage.value.primaryRoleKey);
    if (!selectedHierarchy) {
      manage.value.error = "Hierarchie-Rolle nicht gefunden.";
      return;
    }
    const roleIds = [selectedHierarchy.id, ...manage.value.extraRoleIds];
    await api.put(`profiles/${manage.value.profile.id}/`, { role_ids: roleIds });
    await reloadAll();
    closeManage();
    showToast("Nutzerrolle aktualisiert", "success");
  } catch (err) {
    console.error("save manage failed", err);
    manage.value.error = "Rollen konnten nicht gespeichert werden.";
  } finally {
    manage.value.saving = false;
  }
}

async function toggleLock(profile) {
  lockLoading.value = profile.id;
  try {
    await api.post(`profiles/${profile.id}/lock/`, { locked: !profile.is_locked });
    await reloadAll();
    showToast(profile.is_locked ? "Profil entsperrt" : "Profil gesperrt", "success");
  } catch (err) {
    console.error("toggle lock failed", err);
    showToast("Sperren fehlgeschlagen", "error");
  } finally {
    lockLoading.value = null;
  }
}

function asAbsoluteMediaUrl(value) {
  return toAbsoluteMediaUrl(value);
}

onMounted(async () => {
  await reloadAll();
});
</script>

<style scoped>
.user-role-management {
  display: grid;
  gap: 18px;
}
.hero {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}
.hierarchy {
  margin-top: 10px;
  font-size: 14px;
}
.blocked {
  text-align: center;
  padding: 28px;
}
.matrix-table-wrap {
  overflow: auto;
}
.matrix-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 700px;
}
.matrix-table th,
.matrix-table td {
  border-bottom: 1px solid var(--border);
  padding: 10px;
  text-align: center;
}
.matrix-table th:first-child,
.matrix-table td:first-child {
  text-align: left;
  font-weight: 600;
  white-space: nowrap;
}
.users-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.search {
  max-width: 360px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}
.profile-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  display: grid;
  gap: 10px;
  background: var(--surface);
}
.avatar-wrap {
  width: 100%;
  aspect-ratio: 1 / 1;
  border-radius: 12px;
  overflow: hidden;
  background: #e8ecf3;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.meta h3 {
  margin: 0;
}
.rank {
  font-weight: 600;
  margin: 4px 0 0;
}
.roles {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(75, 91, 255, 0.14);
  color: var(--brand);
}
.actions {
  display: flex;
  gap: 8px;
}
.btn.tiny {
  padding: 6px 10px;
  font-size: 12px;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 70;
  padding: 16px;
}
.modal {
  width: min(540px, 100%);
  display: grid;
  gap: 12px;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.modal-body {
  display: grid;
  gap: 12px;
}
.extras {
  display: grid;
  gap: 8px;
}
.extra-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
.error-msg {
  color: #dc2626;
  margin: 0;
}
@media (max-width: 760px) {
  .hero,
  .users-head {
    flex-direction: column;
    align-items: stretch;
  }
  .search {
    max-width: none;
  }
}
</style>
