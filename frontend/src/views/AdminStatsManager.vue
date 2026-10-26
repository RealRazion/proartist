<template>
  <div class="admin-stats-manager">
    <!-- Header -->
    <header class="page-header card">
      <div class="header-left">
        <div class="header-badge">ADMIN CONTROL</div>
        <h1>📊 Nutzer-Daten &amp; Stats-Zentrale</h1>
        <p class="subtitle">
          Einsicht aller realen Nutzer-Statistiken, RP-Ränge, Battle-Bilanzen und zentrale Reset-Steuerung für Entwicklung und Saison-Starts.
        </p>
      </div>
      <div class="header-actions">
        <button class="btn ghost btn-sm" @click="fetchData" :disabled="loading">
          <span :class="{ spinning: loading }">🔄</span> Aktualisieren
        </button>
        <router-link to="/platforms/admin" class="btn btn-sm">
          ← Zurück zum Admin Hub
        </router-link>
      </div>
    </header>

    <!-- Global Key Metrics -->
    <div class="metrics-grid">
      <div class="metric-card card">
        <div class="metric-icon">👥</div>
        <div class="metric-body">
          <span class="metric-val">{{ globalStats.total_users || 0 }}</span>
          <span class="metric-lbl">Gesamt-Accounts</span>
        </div>
      </div>
      <div class="metric-card card">
        <div class="metric-icon">⚔️</div>
        <div class="metric-body">
          <span class="metric-val">{{ globalStats.total_battles || 0 }}</span>
          <span class="metric-lbl">Battles im System</span>
        </div>
      </div>
      <div class="metric-card card">
        <div class="metric-icon">🗳️</div>
        <div class="metric-body">
          <span class="metric-val">{{ globalStats.total_votes || 0 }}</span>
          <span class="metric-lbl">Abgegebene Votes</span>
        </div>
      </div>
      <div class="metric-card card">
        <div class="metric-icon">🎵</div>
        <div class="metric-body">
          <span class="metric-val">{{ globalStats.total_submissions || 0 }}</span>
          <span class="metric-lbl">Eingereichte Runden</span>
        </div>
      </div>
      <div class="metric-card card highlight-card">
        <div class="metric-icon">🏆</div>
        <div class="metric-body">
          <span class="metric-val">{{ activeRankedUsersCount }}</span>
          <span class="metric-lbl">Aktive Ranked Spieler</span>
        </div>
      </div>
    </div>

    <!-- Dev / Season Reset Action Center -->
    <section class="reset-zone card">
      <div class="reset-zone-header">
        <div class="rz-left">
          <span class="rz-icon">⚡</span>
          <div>
            <h3>Entwicklungs- &amp; Saison-Reset Hub</h3>
            <p class="muted small">
              Setze unkompliziert Test-Daten, Test-Battles oder Ränge zurück, um mit sauberen Werten zu testen.
            </p>
          </div>
        </div>
      </div>

      <div class="reset-actions-row">
        <div class="reset-action-box full-clean">
          <div class="rab-info">
            <strong>🧹 Entwicklungs-Reset (Full Clean Slate)</strong>
            <span>Löscht alle Test-Battles, Runden, Votes und Bewerbungen und setzt alle Ränge auf 0 RP (Bronze) zurück.</span>
          </div>
          <button class="btn danger btn-sm" @click="confirmAction('FULL_CLEAN_SLATE')">
            Vollständigen Reset ausführen
          </button>
        </div>

        <div class="reset-action-box">
          <div class="rab-info">
            <strong>⭐ Alle Ränge auf 0 RP resetten</strong>
            <span>Setzt die Rangpunkte (RP) und Tiers aller Accounts auf Bronze (0 RP), ohne Battles zu löschen.</span>
          </div>
          <button class="btn warning btn-sm" @click="confirmAction('RESET_ALL_RP')">
            Alle Ränge auf 0 setzen
          </button>
        </div>
      </div>
    </section>

    <!-- Users Table Section -->
    <section class="users-section card">
      <div class="section-toolbar">
        <div class="search-wrap">
          <input
            v-model.trim="searchQuery"
            class="input search-input"
            placeholder="Nutzer, E-Mail oder Name filtern…"
          />
          <button v-if="searchQuery" class="clear-btn" @click="searchQuery = ''">✕</button>
        </div>

        <div class="filter-wrap">
          <select v-model="roleFilter" class="input filter-select">
            <option value="ALL">Alle Rollen</option>
            <option value="ADMIN">Admin</option>
            <option value="TEAM">Team</option>
            <option value="ARTIST">Artist</option>
            <option value="MEMBER">Member</option>
          </select>
        </div>

        <div class="count-pill">
          {{ filteredUsers.length }} von {{ users.length }} Nutzern
        </div>
      </div>

      <div v-if="loading" class="state-box">
        <div class="spinner"></div>
        <p>Lade Nutzerstatistiken…</p>
      </div>

      <div v-else-if="!filteredUsers.length" class="state-box empty">
        <p>Keine Nutzer gefunden, die den Kriterien entsprechen.</p>
      </div>

      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Nutzer / Profil</th>
              <th>Rollen</th>
              <th>Ranked Status</th>
              <th>Battle Bilanz</th>
              <th>Turniere</th>
              <th>Preisgelder</th>
              <th class="th-actions">Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="u in filteredUsers" :key="u.id" :class="{ 'row-reset': u.is_reset }">
              <td>
                <div class="user-cell">
                  <div class="avatar-circle">
                    {{ (u.name || u.username || '?').charAt(0).toUpperCase() }}
                  </div>
                  <div class="user-cell-meta">
                    <strong class="user-display-name">{{ u.name || u.username }}</strong>
                    <span class="user-sub-line">@{{ u.username }} · {{ u.email || 'Keine Mail' }}</span>
                  </div>
                </div>
              </td>

              <td>
                <div class="roles-tags">
                  <span
                    v-for="role in u.roles"
                    :key="role"
                    class="role-badge"
                    :class="role.toLowerCase()"
                  >
                    {{ role }}
                  </span>
                </div>
              </td>

              <td>
                <div class="tier-cell">
                  <span
                    class="tier-pill"
                    :style="{ borderColor: u.tier_accent, color: u.tier_accent }"
                  >
                    {{ u.tier_label || u.tier }}
                  </span>
                  <strong class="rp-text">{{ u.ranked_points }} RP</strong>
                  <span v-if="u.is_reset" class="reset-tag" title="Rang wurde manuell zurückgesetzt">Reset</span>
                </div>
              </td>

              <td>
                <div class="battle-stats-cell">
                  <strong class="wl-text">{{ u.wins_count }}W / {{ u.losses_count }}L</strong>
                  <span class="rate-muted">{{ u.battles_count }} Battles ({{ u.win_rate }}%)</span>
                </div>
              </td>

              <td>
                <div class="tourn-meta-cell">
                  <span>📥 {{ u.applications_count }} Bewerbungen</span>
                  <span>🎵 {{ u.submissions_count }} Runden</span>
                  <span>🗳️ {{ u.votes_count }} Votes</span>
                </div>
              </td>

              <td>
                <div class="earnings-cell">
                  <strong class="prize-tag" :class="{ nonzero: u.prize_money > 0 }">
                    {{ u.prize_money_formatted }}
                  </strong>
                </div>
              </td>

              <td class="td-actions">
                <div class="row-action-btns">
                  <button
                    class="action-btn"
                    title="Rangpunkte auf 0 setzen"
                    @click="resetUserRp(u)"
                  >
                    0 RP
                  </button>
                  <button
                    class="action-btn"
                    title="Punkte manuell setzen"
                    @click="openSetPointsModal(u)"
                  >
                    ✏️ RP
                  </button>
                  <button
                    class="action-btn btn-trash"
                    title="Alle Turnier- & Battle-Daten dieses Nutzers löschen"
                    @click="confirmUserClean(u)"
                  >
                    🗑️ Bereinigen
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Modal: Bestätigung für destruktive Aktionen -->
    <div v-if="showConfirmModal" class="modal-backdrop" @click.self="showConfirmModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>⚠️ Aktion bestätigen</h3>
          <button class="close-btn" @click="showConfirmModal = false">✕</button>
        </div>
        <p class="modal-text">{{ confirmModalText }}</p>
        <div class="modal-actions">
          <button class="btn ghost" @click="showConfirmModal = false" :disabled="actionLoading">
            Abbrechen
          </button>
          <button class="btn danger" @click="executeConfirmedAction" :disabled="actionLoading">
            {{ actionLoading ? "Wird ausgeführt…" : "Ja, Ausführen" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Modal: RP manuell anpassen -->
    <div v-if="showPointsModal" class="modal-backdrop" @click.self="showPointsModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Rangpunkte (RP) anpassen</h3>
          <button class="close-btn" @click="showPointsModal = false">✕</button>
        </div>
        <p class="modal-text">
          Punkte für <strong>{{ selectedUser?.name || selectedUser?.username }}</strong> festlegen:
        </p>
        <div class="modal-body">
          <label class="form-label">
            Neue RP-Anzahl:
            <input
              type="number"
              min="0"
              step="10"
              class="input"
              v-model.number="customPoints"
            />
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn ghost" @click="showPointsModal = false" :disabled="actionLoading">
            Abbrechen
          </button>
          <button class="btn btn-primary" @click="saveCustomPoints" :disabled="actionLoading">
            {{ actionLoading ? "Speichern…" : "RP Speichern" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useToast } from "../composables/useToast";
import api from "../api";

const { showToast } = useToast();

const loading = ref(false);
const actionLoading = ref(false);
const users = ref([]);
const globalStats = ref({
  total_users: 0,
  total_votes: 0,
  total_submissions: 0,
  total_applications: 0,
  total_battles: 0,
});

const searchQuery = ref("");
const roleFilter = ref("ALL");

// Modals
const showConfirmModal = ref(false);
const confirmModalAction = ref("");
const confirmModalText = ref("");
const targetProfileId = ref(null);

const showPointsModal = ref(false);
const selectedUser = ref(null);
const customPoints = ref(0);

const activeRankedUsersCount = computed(() => {
  return users.value.filter((u) => u.ranked_points > 0).length;
});

const filteredUsers = computed(() => {
  let list = users.value;
  if (roleFilter.value !== "ALL") {
    list = list.filter((u) => (u.roles || []).includes(roleFilter.value));
  }
  if (searchQuery.value) {
    const q = searchQuery.value.toLowerCase();
    list = list.filter(
      (u) =>
        (u.name || "").toLowerCase().includes(q) ||
        (u.username || "").toLowerCase().includes(q) ||
        (u.email || "").toLowerCase().includes(q)
    );
  }
  return list;
});

async function fetchData() {
  loading.value = true;
  try {
    const { data } = await api.get("admin/user-stats/");
    users.value = data.users || [];
    globalStats.value = {
      total_users: data.total_users || 0,
      total_votes: data.total_votes || 0,
      total_submissions: data.total_submissions || 0,
      total_applications: data.total_applications || 0,
      total_battles: data.total_battles || 0,
    };
  } catch (err) {
    console.error(err);
    showToast("Fehler beim Laden der Admin-Nutzerdaten.", "error");
  } finally {
    loading.value = false;
  }
}

function confirmAction(actionType) {
  confirmModalAction.value = actionType;
  targetProfileId.value = null;

  if (actionType === "FULL_CLEAN_SLATE") {
    confirmModalText.value =
      "Möchtest du wirklich einen VOLLSTÄNDIGEN Entwicklungs-Reset durchführen? Alle Battles, Runden, Votes und Bewerbungen werden gelöscht und alle Spieler auf 0 RP (Bronze) zurückgesetzt.";
  } else if (actionType === "RESET_ALL_RP") {
    confirmModalText.value =
      "Möchtest du die Rangpunkte (RP) aller Nutzer auf 0 setzen? Die Battle-Historie bleibt erhalten.";
  }
  showConfirmModal.value = true;
}

function resetUserRp(user) {
  confirmModalAction.value = "RESET_USER_RP";
  targetProfileId.value = user.id;
  confirmModalText.value = `Möchtest du die RP von ${user.name || user.username} auf 0 (Bronze) zurücksetzen?`;
  showConfirmModal.value = true;
}

function confirmUserClean(user) {
  confirmModalAction.value = "CLEAR_USER_TOURNAMENT_DATA";
  targetProfileId.value = user.id;
  confirmModalText.value = `Möchtest du alle Turnier-Bewerbungen, Einreichungen, Battles und Votes für ${user.name || user.username} löschen und den Rang auf 0 RP setzen?`;
  showConfirmModal.value = true;
}

async function executeConfirmedAction() {
  actionLoading.value = true;
  try {
    const payload = {
      action: confirmModalAction.value,
      profile_id: targetProfileId.value,
    };
    const { data } = await api.post("admin/reset-stats/", payload);
    showToast(data?.message || "Aktion erfolgreich ausgeführt.", "success");
    showConfirmModal.value = false;
    await fetchData();
  } catch (err) {
    console.error(err);
    const detail = err?.response?.data?.detail;
    showToast(typeof detail === "string" && detail ? detail : "Aktion fehlgeschlagen.", "error");
  } finally {
    actionLoading.value = false;
  }
}

function openSetPointsModal(user) {
  selectedUser.value = user;
  customPoints.value = user.ranked_points || 0;
  showPointsModal.value = true;
}

async function saveCustomPoints() {
  if (!selectedUser.value) return;
  actionLoading.value = true;
  try {
    const { data } = await api.post("admin/reset-stats/", {
      action: "SET_USER_RP",
      profile_id: selectedUser.value.id,
      points: customPoints.value,
    });
    showToast(data?.message || "Punkte aktualisiert.", "success");
    showPointsModal.value = false;
    await fetchData();
  } catch (err) {
    console.error(err);
    showToast("Punkte konnten nicht gespeichert werden.", "error");
  } finally {
    actionLoading.value = false;
  }
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.admin-stats-manager {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 24px 20px 80px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(30, 32, 48, 0.95), rgba(18, 19, 30, 0.95));
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2px;
  color: #a78bfa;
  background: rgba(139, 92, 246, 0.15);
  border: 1px solid rgba(139, 92, 246, 0.3);
  padding: 3px 10px;
  border-radius: 999px;
  margin-bottom: 8px;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 6px;
  color: #fff;
}

.subtitle {
  color: #94a3b8;
  font-size: 14px;
  margin: 0;
  max-width: 760px;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.spinning {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: #141624;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
}

.metric-card.highlight-card {
  background: linear-gradient(135deg, rgba(139, 92, 246, 0.15), rgba(99, 102, 241, 0.08));
  border-color: rgba(139, 92, 246, 0.3);
}

.metric-icon {
  font-size: 32px;
}

.metric-body {
  display: flex;
  flex-direction: column;
}

.metric-val {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  line-height: 1.2;
}

.metric-lbl {
  font-size: 12px;
  color: #94a3b8;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* Reset Zone */
.reset-zone {
  padding: 22px 26px;
  background: #131522;
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.reset-zone-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rz-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.rz-icon {
  font-size: 28px;
  padding: 10px;
  background: rgba(239, 68, 68, 0.15);
  border-radius: 10px;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.rz-left h3 {
  margin: 0 0 4px;
  font-size: 17px;
  font-weight: 700;
  color: #fff;
}

.reset-actions-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
  gap: 14px;
}

.reset-action-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #181b2c;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  gap: 16px;
}

.reset-action-box.full-clean {
  border-color: rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.05);
}

.rab-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rab-info strong {
  font-size: 14px;
  color: #fff;
}

.rab-info span {
  font-size: 12px;
  color: #94a3b8;
  line-height: 1.4;
}

/* Users Section */
.users-section {
  padding: 24px;
  background: #131522;
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.search-wrap {
  position: relative;
  flex: 1;
  min-width: 260px;
}

.search-input {
  width: 100%;
  padding: 10px 14px;
  border-radius: 10px;
  background: #0d0e17;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
}

.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}

.filter-select {
  padding: 10px 14px;
  border-radius: 10px;
  background: #0d0e17;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 14px;
}

.count-pill {
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  background: #181b2c;
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

/* Table */
.table-container {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table th {
  background: #181a2b;
  padding: 14px 16px;
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #94a3b8;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.data-table td {
  padding: 14px 16px;
  font-size: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: middle;
}

.data-table tr:hover {
  background: rgba(255, 255, 255, 0.02);
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar-circle {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #fff;
  font-size: 14px;
}

.user-cell-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.user-display-name {
  color: #fff;
  font-weight: 700;
}

.user-sub-line {
  font-size: 12px;
  color: #64748b;
}

.roles-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.role-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

.role-badge.admin {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.role-badge.team {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
}

.role-badge.artist {
  background: rgba(168, 85, 247, 0.2);
  color: #d8b4fe;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.tier-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tier-pill {
  font-size: 11px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
  border: 1px solid;
  text-transform: uppercase;
}

.rp-text {
  color: #fff;
  font-size: 13px;
}

.reset-tag {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(234, 179, 8, 0.2);
  color: #fde047;
  font-weight: 700;
}

.battle-stats-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.wl-text {
  color: #fff;
  font-size: 13px;
}

.rate-muted {
  font-size: 12px;
  color: #64748b;
}

.tourn-meta-cell {
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 12px;
  color: #94a3b8;
}

.earnings-cell {
  display: flex;
  align-items: center;
}

.prize-tag {
  font-size: 13px;
  font-weight: 700;
  color: #64748b;
  padding: 3px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.04);
}

.prize-tag.nonzero {
  color: #34d399;
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.td-actions {
  text-align: right;
}

.row-action-btns {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.action-btn {
  padding: 6px 10px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 6px;
  background: #1e2133;
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  background: #2a2e45;
  color: #fff;
}

.action-btn.btn-trash {
  background: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.25);
  color: #f87171;
}

.action-btn.btn-trash:hover {
  background: rgba(239, 68, 68, 0.25);
}

/* State Box */
.state-box {
  padding: 60px 20px;
  text-align: center;
  color: #94a3b8;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid rgba(255, 255, 255, 0.1);
  border-top-color: #8b5cf6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 460px;
  background: #181b2c;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
}

.modal-text {
  margin: 0;
  font-size: 14px;
  color: #cbd5e1;
  line-height: 1.5;
}

.form-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 13px;
  font-weight: 600;
  color: #cbd5e1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

.btn.danger {
  background: #ef4444;
  color: #fff;
}

.btn.danger:hover {
  background: #dc2626;
}

.btn.warning {
  background: #f59e0b;
  color: #111;
}

.btn.warning:hover {
  background: #d97706;
}
</style>
