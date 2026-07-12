<template>
  <div class="points">
    <header class="card hero">
      <div>
        <p class="eyebrow">Score</p>
        <h1>Team Points</h1>
        <p class="muted">Übersicht der Punkte und wie sie entstehen.</p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="exportCsv" :disabled="loading">
          Export CSV
        </button>
        <button class="btn ghost" type="button" @click="loadPoints" :disabled="loading">
          {{ loading ? "Lade..." : "Aktualisieren" }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Die Punkte-Übersicht ist nur für Team-Mitglieder sichtbar.</p>
    </section>

    <section v-else class="card rules">
      <h2>Regeln</h2>
      <div class="rules-grid">
        <div class="rule">
          <h3>Task Prioritaet</h3>
          <p class="muted">
            LOW/MEDIUM = {{ rules?.tasks?.LOW ?? 1 }} Punkt,
            HIGH = {{ rules?.tasks?.HIGH ?? 2 }} Punkte,
            CRITICAL = {{ rules?.tasks?.CRITICAL ?? 3 }} Punkte.
          </p>
        </div>
        <div class="rule">
          <h3>Projekt Teilnahme</h3>
          <p class="muted">Jede Projektbeteiligung zaehlt {{ rules?.project_participation ?? 2 }} Punkte.</p>
        </div>
        <div class="rule">
          <h3>GrowPro Zuteilung</h3>
          <p class="muted">Jedes zugeteilte Ziel zaehlt {{ rules?.growpro_assignment ?? 1 }} Punkt.</p>
        </div>
      </div>
    </section>

    <section v-if="isTeam" class="card list-card">
      <div v-if="!members.length" class="muted">Keine Team-Mitglieder gefunden.</div>
      <div v-else class="member-list">
        <article v-for="member in members" :key="member.profile.id" class="member-row">
          <button class="member-summary" type="button" @click="toggleExpanded(member.profile.id)">
            <div>
              <strong>{{ member.profile.name }}</strong>
              <p class="muted small">@{{ member.profile.username }}</p>
            </div>
            <div class="summary-metrics">
              <div>
                <span class="label">Aktuell</span>
                <strong>{{ member.total }}</strong>
              </div>
              <div>
                <span class="label">Ø Netto (7 Tage)</span>
                <strong>{{ member.daily?.avg_daily_net ?? 0 }}</strong>
              </div>
              <div>
                <span class="label">Cap</span>
                <strong>{{ member.profile.max_task_points ?? "-" }}</strong>
              </div>
            </div>
            <span class="expand-indicator">{{ isExpanded(member.profile.id) ? "−" : "+" }}</span>
          </button>

          <div v-if="isExpanded(member.profile.id)" class="member-details">
            <div class="cap-row">
              <label>
                Max aktive Punkte für Auto-Zuweisung
                <input
                  class="input"
                  type="number"
                  min="0"
                  step="1"
                  :value="capDraft(member.profile.id)"
                  @input="setCapDraft(member.profile.id, $event.target.value)"
                  placeholder="leer = kein Limit"
                />
              </label>
              <button class="btn tiny" type="button" @click="saveCap(member)" :disabled="capSaving[member.profile.id]">
                {{ capSaving[member.profile.id] ? "Speichere..." : "Cap speichern" }}
              </button>
            </div>
            <div class="performance">
              <div>
                <span class="label">Heute</span>
                <span class="value">+{{ member.daily?.today_plus ?? 0 }} / -{{ member.daily?.today_minus ?? 0 }}</span>
                <span class="muted tiny">Netto {{ member.daily?.today_net ?? 0 }}</span>
              </div>
              <div>
                <span class="label">Ø 7 Tage</span>
                <span class="value">+{{ member.daily?.avg_daily_plus ?? 0 }} / -{{ member.daily?.avg_daily_minus ?? 0 }}</span>
                <span class="muted tiny">Netto {{ member.daily?.avg_daily_net ?? 0 }}</span>
              </div>
            </div>
            <div class="member-grid">
              <div class="bucket">
                <h3>Tasks ({{ totalTaskPoints(member) }})</h3>
                <ul v-if="member.tasks.length" class="item-list">
                  <li v-for="task in member.tasks" :key="`task-${task.id}`">
                    <span>{{ task.title }}</span>
                    <span class="badge">+{{ task.points }}</span>
                  </li>
                </ul>
                <p v-else class="muted small">Keine aktiven Tasks.</p>
              </div>
              <div class="bucket">
                <h3>Projekte ({{ totalProjectPoints(member) }})</h3>
                <ul v-if="member.projects.length" class="item-list">
                  <li v-for="project in member.projects" :key="`project-${project.id}`">
                    <span>{{ project.title }}</span>
                    <span class="badge">+{{ project.points }}</span>
                  </li>
                </ul>
                <p v-else class="muted small">Keine Projekte zugeordnet.</p>
              </div>
              <div class="bucket">
                <h3>GrowPro ({{ totalGrowProPoints(member) }})</h3>
                <ul v-if="member.growpro.length" class="item-list">
                  <li v-for="goal in member.growpro" :key="`goal-${goal.id}`">
                    <span>{{ goal.title }}</span>
                    <span class="badge">+{{ goal.points }}</span>
                  </li>
                </ul>
                <p v-else class="muted small">Keine GrowPro Ziele zugeteilt.</p>
              </div>
            </div>
          </div>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const members = ref([]);
const rules = ref(null);
const loading = ref(false);
const expanded = ref({});
const capDrafts = ref({});
const capSaving = ref({});

async function loadPoints() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("team-points/");
    const payload = Array.isArray(data) ? { members: data, rules: null } : data || {};
    members.value = payload.members || [];
    rules.value = payload.rules || null;
    capDrafts.value = members.value.reduce((acc, member) => {
      const raw = member?.profile?.max_task_points;
      acc[member.profile.id] = raw === null || raw === undefined ? "" : String(raw);
      return acc;
    }, {});
  } catch (err) {
    console.error("Team-Punkte konnten nicht geladen werden", err);
    showToast("Team-Punkte konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function exportCsv() {
  if (!isTeam.value) return;
  try {
    const { data } = await api.get("team-points/", { params: { format: "csv" }, responseType: "blob" });
    const url = URL.createObjectURL(new Blob([data]));
    const link = document.createElement("a");
    link.href = url;
    link.download = "team_points.csv";
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (err) {
    console.error("Export konnte nicht erstellt werden", err);
    showToast("Export konnte nicht erstellt werden", "error");
  }
}

function totalTaskPoints(member) {
  return (member.tasks || []).reduce((sum, task) => sum + (task.points || 0), 0);
}

function totalProjectPoints(member) {
  return (member.projects || []).reduce((sum, project) => sum + (project.points || 0), 0);
}

function totalGrowProPoints(member) {
  return (member.growpro || []).reduce((sum, goal) => sum + (goal.points || 0), 0);
}

function sliceDetails(list) {
  if (!Array.isArray(list)) return [];
  return list.slice(0, 3);
}

function isExpanded(profileId) {
  return Boolean(expanded.value[profileId]);
}

function toggleExpanded(profileId) {
  expanded.value = { ...expanded.value, [profileId]: !expanded.value[profileId] };
}

function capDraft(profileId) {
  return capDrafts.value[profileId] ?? "";
}

function setCapDraft(profileId, value) {
  capDrafts.value = { ...capDrafts.value, [profileId]: value };
}

async function saveCap(member) {
  const profileId = member?.profile?.id;
  if (!profileId) return;
  capSaving.value = { ...capSaving.value, [profileId]: true };
  try {
    const raw = (capDrafts.value[profileId] || "").trim();
    const parsed = raw === "" ? null : Math.max(0, Number.parseInt(raw, 10) || 0);
    const { data } = await api.get(`profiles/${profileId}/`);
    const currentSettings = data?.notification_settings || {};
    const nextSettings = {
      ...currentSettings,
      task_point_cap: parsed,
      team_points: {
        ...(currentSettings.team_points || {}),
        max_active_points: parsed,
      },
    };
    await api.patch(`profiles/${profileId}/`, { notification_settings: nextSettings });
    showToast("Cap gespeichert", "success");
    await loadPoints();
  } catch (err) {
    console.error("Cap konnte nicht gespeichert werden", err);
    showToast("Cap konnte nicht gespeichert werden", "error");
  } finally {
    capSaving.value = { ...capSaving.value, [profileId]: false };
  }
}

onMounted(() => {
  fetchProfile().catch(() => null).finally(() => loadPoints());
});
</script>

<style scoped>
.points {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.hero-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.rules {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.rules-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.rule {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: color-mix(in srgb, var(--text) 3%, var(--surface));
}
.list-card {
  display: grid;
  gap: 12px;
}
.member-list {
  display: grid;
  gap: 10px;
}
.member-row {
  border: 1px solid var(--border);
  border-radius: 14px;
  background: color-mix(in srgb, var(--text) 2%, var(--surface));
}

:global(.dark) .member-row,
:global(.dark) .rule,
:global(.dark) .performance,
:global(.dark) .bucket {
  background: rgba(15, 23, 42, 0.78);
  border-color: rgba(148, 163, 184, 0.24);
}
.member-summary {
  width: 100%;
  border: none;
  background: transparent;
  text-align: left;
  padding: 12px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 14px;
  align-items: center;
  cursor: pointer;
  color: var(--text);
}

.member-summary strong,
.member-summary .small,
.member-summary .label,
.rule h3,
.rule p,
.performance .label,
.performance .value,
.bucket h3,
.bucket li span,
.bucket .muted,
.item-list li span:first-child {
  color: var(--text);
}

.member-summary .small,
.rule p.muted,
.performance .muted,
.bucket .muted {
  color: var(--muted);
}
.summary-metrics {
  display: flex;
  gap: 16px;
}
.summary-metrics .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.expand-indicator {
  font-size: 24px;
  line-height: 1;
  color: var(--brand);
}
.member-details {
  border-top: 1px dashed var(--border);
  padding: 12px;
  display: grid;
  gap: 12px;
}
.cap-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 12px;
  align-items: end;
}
.performance {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--text) 3%, var(--surface));
}
.today-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  border: 1px dashed var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: color-mix(in srgb, var(--text) 2%, var(--surface));
}
.detail-list {
  list-style: none;
  padding: 0;
  margin: 6px 0 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.detail-list li {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}
.badge.danger {
  background: color-mix(in srgb, var(--status-overdue) 18%, transparent);
  color: var(--status-overdue);
}
.performance .label {
  display: block;
  text-transform: uppercase;
  font-size: 11px;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.performance .value {
  font-weight: 600;
  margin-right: 8px;
}
.score {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}
.score .label {
  text-transform: uppercase;
  font-size: 12px;
  color: var(--muted);
  letter-spacing: 0.08em;
}
.member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.bucket {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--card);
}

:global(.dark) .bucket {
  background: rgba(15, 23, 42, 0.8);
}
.item-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.item-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
.badge {
  border-radius: 999px;
  padding: 2px 8px;
  font-size: 11px;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--brand) 14%, transparent);
  color: var(--brand);
}

:global(.dark) .member-summary strong,
:global(.dark) .member-summary .small,
:global(.dark) .member-summary .label,
:global(.dark) .rule h3,
:global(.dark) .rule p,
:global(.dark) .performance .label,
:global(.dark) .performance .value,
:global(.dark) .bucket h3,
:global(.dark) .bucket li span,
:global(.dark) .bucket .muted,
:global(.dark) .item-list li span:first-child {
  color: var(--text);
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
    align-items: stretch;
  }
  .score {
    align-items: flex-start;
  }
  .performance {
    flex-direction: column;
  }
}
</style>
