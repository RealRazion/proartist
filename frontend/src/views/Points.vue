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

    <section v-if="isTeam" class="grid">
      <article v-for="member in members" :key="member.profile.id" class="card member">
        <div class="member-head">
          <div>
            <h2>{{ member.profile.name }}</h2>
            <p class="muted small">@{{ member.profile.username }}</p>
          </div>
          <div class="score">
            <span class="label">Punkte</span>
            <strong>{{ member.total }}</strong>
          </div>
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
        <div class="today-details">
          <div>
            <span class="label">Heute +</span>
            <ul v-if="sliceDetails(member.daily?.today_plus_details).length" class="detail-list">
              <li v-for="item in sliceDetails(member.daily?.today_plus_details)" :key="`plus-${item.type}-${item.title}`">
                <span>{{ item.title }}</span>
                <span class="badge">+{{ item.points }}</span>
              </li>
            </ul>
            <p v-else class="muted small">Keine Plus-Punkte heute.</p>
          </div>
          <div>
            <span class="label">Heute -</span>
            <ul v-if="sliceDetails(member.daily?.today_minus_details).length" class="detail-list">
              <li v-for="item in sliceDetails(member.daily?.today_minus_details)" :key="`minus-${item.type}-${item.title}`">
                <span>{{ item.title }}</span>
                <span class="badge danger">-{{ item.points }}</span>
              </li>
            </ul>
            <p v-else class="muted small">Keine Minus-Punkte heute.</p>
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
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();
const { showToast } = useToast();

const members = ref([]);
const rules = ref(null);
const loading = ref(false);

async function loadPoints() {
  if (!isTeam.value) return;
  loading.value = true;
  try {
    const { data } = await api.get("team-points/");
    const payload = Array.isArray(data) ? { members: data, rules: null } : data || {};
    members.value = payload.members || [];
    rules.value = payload.rules || null;
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

onMounted(() => {
  loadPoints();
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
.grid {
  display: grid;
  gap: 18px;
}
.member {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.member-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
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
