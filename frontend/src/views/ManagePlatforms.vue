<template>
  <div class="manage-platforms">
    <header class="card head">
      <div>
        <p class="eyebrow">Admin</p>
        <h1>Platform Control</h1>
        <p class="muted">Automatisch erkannte Plattformen zentral im Admin-Bereich steuern.</p>
      </div>
      <div class="head-actions">
        <button class="btn ghost" type="button" @click="syncPlatforms" :disabled="syncing || loading || !isTeam">
          {{ syncing ? "Erkenne..." : "Plattformen erkennen" }}
        </button>
        <button class="btn ghost" type="button" @click="loadPlatforms" :disabled="loading || !isTeam">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card">
      <h2>Kein Zugriff</h2>
      <p class="muted">Nur Team-Mitglieder können Manage Plattforms verwenden.</p>
    </section>

    <section v-else class="grid">
      <article class="card sync-card">
        <h2>Automatische Erkennung</h2>
        <p class="muted">
          Plattformen werden aus dem Systemkatalog synchronisiert und mit Version, Status und Zugriffen verwaltet.
          Der frühere manuelle Bereich zum Erstellen einzelner Plattformen ist deshalb entfernt.
        </p>
        <div class="sync-meta">
          <span class="sync-pill">Systembasiert</span>
          <span class="sync-pill">Versioniert</span>
          <span class="sync-pill">Admin-only</span>
        </div>
      </article>

      <article class="card list-card">
        <h2>Bestehende Plattformen</h2>
        <p v-if="loading" class="muted">Lade Plattformen...</p>
        <p v-else-if="!platforms.length" class="muted">Noch keine Plattformen vorhanden.</p>
        <div v-else class="list">
          <div v-for="item in platforms" :key="item.id" class="row">
            <div class="row-title">
              <strong>{{ item.name }}</strong>
              <span class="muted">/{{ item.slug }}</span>
              <span class="muted">v{{ item.version || '0.1' }}</span>
              <span v-if="item.is_system_defined" class="system-badge">System</span>
              <span class="muted tiny">Zuletzt: {{ formatDate(item.updated_at) }}</span>
            </div>
            <div class="row-fields">
              <label>
                <span>Status</span>
                <select v-model="item.status" class="input">
                  <option value="ACTIVE">ACTIVE</option>
                  <option value="MAINTENANCE">MAINTENANCE</option>
                  <option value="LOCKED">LOCKED</option>
                </select>
              </label>
              <label class="checkline">
                <input type="checkbox" v-model="item.allow_non_team_users" />
                <span>Normale Nutzer erlaubt</span>
              </label>
              <label>
                <span>Status-Hinweis</span>
                <input v-model.trim="item.status_note" class="input" placeholder="Optional" />
              </label>
            </div>
            <div class="row-actions">
              <button class="btn ghost tiny" type="button" @click="savePlatform(item)" :disabled="busyId === item.id">
                {{ busyId === item.id ? "Speichere..." : "Speichern" }}
              </button>
              <button v-if="!item.is_system_defined" class="btn ghost tiny danger" type="button" @click="deletePlatform(item)" :disabled="busyId === item.id">
                Löschen
              </button>
              <span v-else class="muted tiny">Automatisch erkannt</span>
            </div>
          </div>
        </div>
      </article>

      <article class="card history-card">
        <div class="history-head">
          <div>
            <h2>Letzte Änderungen</h2>
            <p class="muted">Audit-Log für Plattform-Status und Zugriffsänderungen.</p>
          </div>
          <button class="btn ghost tiny" type="button" @click="loadHistory" :disabled="historyLoading">
            {{ historyLoading ? "Lade..." : "Aktualisieren" }}
          </button>
        </div>
        <p v-if="historyLoading" class="muted">Lade Historie...</p>
        <p v-else-if="!historyEntries.length" class="muted">Noch keine Änderungen protokolliert.</p>
        <ul v-else class="history-list">
          <li v-for="entry in historyEntries" :key="entry.id" class="history-item" :data-severity="entry.severity">
            <div class="history-row">
              <strong>{{ historyTitle(entry) }}</strong>
              <span class="muted tiny">{{ formatDate(entry.created_at) }}</span>
            </div>
            <p class="muted small">{{ historyDescription(entry) }}</p>
            <div class="history-meta">
              <span v-if="entry.actor">Von {{ entry.actor.name || entry.actor.username }}</span>
              <span v-if="entry.metadata?.platform_slug">/{{ entry.metadata.platform_slug }}</span>
              <span v-if="entry.metadata?.before?.status">
                {{ entry.metadata.before.status }} -> {{ entry.metadata.status }}
              </span>
            </div>
          </li>
        </ul>
      </article>
    </section>
  </div>
</template>

<script setup>
import { onMounted, ref } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import { invalidateManagedPlatformAccessCache } from "../services/managedPlatforms";

const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const loading = ref(false);
const syncing = ref(false);
const historyLoading = ref(false);
const busyId = ref(null);
const platforms = ref([]);
const historyEntries = ref([]);

// KI-Hinweis:
// Bei jeder funktionalen Plattform-Aenderung erhoeht das Backend die Plattform-Version automatisch.
// Diese Verwaltungsseite soll Versionen nur anzeigen und niemals direkt setzen.

function formatDate(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  } catch {
    return "-";
  }
}

function historyTitle(entry) {
  return entry?.title || "Aenderung";
}

function historyDescription(entry) {
  const note = entry?.metadata?.status_note;
  if (note) return note;
  if (entry?.event_type === "managed_platform_deleted") {
    return "Plattform wurde aus der Verwaltung entfernt.";
  }
  if (entry?.metadata?.before?.status) {
    return `Statuswechsel von ${entry.metadata.before.status} zu ${entry.metadata.status}.`;
  }
  return entry?.description || "Keine weiteren Details.";
}

async function loadPlatforms() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("manage-platforms/");
    platforms.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    platforms.value = [];
    showToast("Plattformen konnten nicht geladen werden.", "error");
  } finally {
    loading.value = false;
  }
}

async function loadHistory() {
  if (!isTeam.value) return;
  historyLoading.value = true;
  try {
    const { data } = await api.get("activity-feed/", {
      params: {
        limit: 20,
        types: "managed_platform_created,managed_platform_updated,managed_platform_deleted",
      },
    });
    historyEntries.value = Array.isArray(data) ? data : [];
  } catch (err) {
    historyEntries.value = [];
    showToast("Historie konnte nicht geladen werden.", "error");
  } finally {
    historyLoading.value = false;
  }
}

async function savePlatform(item) {
  busyId.value = item.id;
  try {
    const payload = {
      status: item.status,
      allow_non_team_users: item.allow_non_team_users,
      status_note: item.status_note || "",
    };
    const { data } = await api.patch(`manage-platforms/${item.id}/`, payload);
    const idx = platforms.value.findIndex((row) => row.id === item.id);
    if (idx >= 0) platforms.value[idx] = data;
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    showToast("Plattform gespeichert.", "success");
  } catch (err) {
    showToast("Plattform konnte nicht gespeichert werden.", "error");
  } finally {
    busyId.value = null;
  }
}

async function deletePlatform(item) {
  const ok = window.confirm(`Plattform ${item.name} wirklich löschen?`);
  if (!ok) return;
  busyId.value = item.id;
  try {
    await api.delete(`manage-platforms/${item.id}/`);
    platforms.value = platforms.value.filter((row) => row.id !== item.id);
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    showToast("Plattform gelöscht.", "success");
  } catch (err) {
    showToast("Plattform konnte nicht geloescht werden.", "error");
  } finally {
    busyId.value = null;
  }
}

async function syncPlatforms() {
  syncing.value = true;
  try {
    const { data } = await api.post("manage-platforms/sync/");
    platforms.value = Array.isArray(data?.results) ? data.results : data?.results || [];
    invalidateManagedPlatformAccessCache();
    await loadHistory();
    const created = Number(data?.stats?.created || 0);
    const updated = Number(data?.stats?.updated || 0);
    showToast(`Plattformen synchronisiert (${created} neu, ${updated} aktualisiert).`, "success");
  } catch (err) {
    showToast("Plattformen konnten nicht synchronisiert werden.", "error");
  } finally {
    syncing.value = false;
  }
}

onMounted(async () => {
  await fetchProfile();
  await Promise.all([loadPlatforms(), loadHistory()]);
});
</script>

<style scoped>
.manage-platforms {
  display: grid;
  gap: 16px;
}

.head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.head h1 {
  margin: 0;
}

.eyebrow {
  margin: 0 0 4px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--brand);
}

.head-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.grid {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 16px;
}

.sync-card {
  display: grid;
  gap: 14px;
}

.sync-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.sync-pill,
.system-badge {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 4px 10px;
  font-size: 12px;
  font-weight: 700;
  background: color-mix(in srgb, var(--brand) 12%, transparent 88%);
  color: var(--brand);
}

.history-card {
  grid-column: 1 / -1;
}

.history-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

label {
  display: grid;
  gap: 6px;
  font-size: 13px;
}

.full {
  grid-column: 1 / -1;
}

.checkline {
  display: flex;
  align-items: center;
  gap: 8px;
}

.list {
  display: grid;
  gap: 12px;
}

.row {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 10px;
}

.row-title {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.row-fields {
  display: grid;
  grid-template-columns: 180px 220px 1fr;
  gap: 10px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.history-item {
  border: 1px solid var(--border);
  border-left: 4px solid #94a3b8;
  border-radius: 12px;
  padding: 12px;
  display: grid;
  gap: 6px;
}

.history-item[data-severity="INFO"] {
  border-left-color: #3b82f6;
}

.history-item[data-severity="WARNING"] {
  border-left-color: #f97316;
}

.history-item[data-severity="DANGER"] {
  border-left-color: #ef4444;
}

.history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.history-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 12px;
  color: var(--muted);
}

.small {
  font-size: 13px;
}

.danger {
  color: #b91c1c;
}

.tiny {
  font-size: 12px;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .row-fields {
    grid-template-columns: 1fr;
  }
}
</style>