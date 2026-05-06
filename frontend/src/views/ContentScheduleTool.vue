<template>
  <div class="cs-tool">
    <!-- Top bar -->
    <header class="card topbar">
      <div class="topbar-left">
        <p class="eyebrow">Content Schedule</p>
        <h1 class="week-label">{{ weekLabel }}</h1>
      </div>
      <div class="topbar-actions">
        <div class="week-nav">
          <button class="btn ghost icon-btn" type="button" @click="prevWeek" aria-label="Vorherige Woche">‹</button>
          <button class="btn ghost" type="button" @click="goToCurrentWeek">Diese Woche</button>
          <button class="btn ghost icon-btn" type="button" @click="nextWeek" aria-label="Nächste Woche">›</button>
        </div>
        <button class="btn ghost" type="button" @click="router.push({ name: 'platform-content-schedule' })">Übersicht</button>
      </div>
    </header>

    <!-- Stats row -->
    <div class="stats-row">
      <div class="stat-chip">
        <span class="stat-val">{{ weekPostCount }}</span>
        <span class="stat-label">Posts diese Woche</span>
      </div>
      <div class="stat-chip" v-for="s in statusStats" :key="s.key">
        <span class="stat-dot" :data-status="s.key"></span>
        <span class="stat-val">{{ s.count }}</span>
        <span class="stat-label">{{ s.label }}</span>
      </div>
    </div>

    <!-- Day tabs (mobile) -->
    <div class="day-tabs" role="tablist">
      <button
        v-for="day in days"
        :key="day.dateKey"
        class="day-tab"
        :class="{ active: activeDay === day.dateKey, today: day.isToday }"
        role="tab"
        :aria-selected="activeDay === day.dateKey"
        type="button"
        :aria-label="`${day.label}, ${day.dateStr}`"
        @click="activeDay = day.dateKey"
      >
        <span class="tab-short">{{ day.short }}</span>
        <span class="tab-date">{{ day.dateNum }}</span>
        <span v-if="postsForDay(day.dateKey).length" class="tab-badge">{{ postsForDay(day.dateKey).length }}</span>
      </button>
    </div>

    <!-- Week grid -->
    <div class="week-grid">
      <div
        v-for="day in days"
        :key="day.dateKey"
        class="day-column card"
        :class="{ 'day-today': day.isToday, 'day-hidden': activeDay !== day.dateKey }"
        role="tabpanel"
      >
        <div class="day-header">
          <div class="day-meta">
            <span class="day-name" :class="{ 'is-today': day.isToday }">{{ day.label }}</span>
            <span class="day-date muted">{{ day.dateStr }}</span>
          </div>
          <button class="add-btn" type="button" @click="openAdd(day.dateKey)" aria-label="Post hinzufügen">+</button>
        </div>

        <div class="post-list">
          <div
            v-for="post in postsForDay(day.dateKey)"
            :key="post.id"
            class="post-card"
            :data-status="post.status"
            @click="openEdit(day.dateKey, post)"
          >
            <div class="post-top">
              <span class="post-platform-icon" :title="platformLabel(post.platform)">{{ platformIcon(post.platform) }}</span>
              <span class="post-title">{{ post.title || "Kein Titel" }}</span>
              <button class="post-del" type="button" @click.stop="deletePost(day.dateKey, post.id)" aria-label="Post löschen">×</button>
            </div>
            <p v-if="post.note" class="post-note muted">{{ post.note }}</p>
            <div class="post-footer">
              <span class="platform-badge" :data-platform="post.platform">{{ platformLabel(post.platform) }}</span>
              <span class="status-badge" :data-status="post.status">{{ statusLabel(post.status) }}</span>
            </div>
          </div>

          <button class="add-post-btn" type="button" @click="openAdd(day.dateKey)">
            <span class="plus">+</span> Post planen
          </button>
        </div>
      </div>
    </div>

    <!-- Add / Edit Modal -->
    <div v-if="modal.open" class="overlay" @click.self="modal.open = false">
      <div class="modal card" role="dialog" aria-modal="true" :aria-label="modal.isEdit ? 'Post bearbeiten' : 'Neuen Post planen'">
        <h2>{{ modal.isEdit ? "Post bearbeiten" : "Neuen Post planen" }}</h2>

        <label class="field-label">
          Plattform
          <div class="platform-grid">
            <button
              v-for="p in platforms"
              :key="p.key"
              class="platform-option"
              :class="{ selected: modal.form.platform === p.key }"
              :data-platform="p.key"
              type="button"
              @click="modal.form.platform = p.key"
            >
              <span class="platform-opt-icon">{{ p.icon }}</span>
              <span class="platform-opt-label">{{ p.label }}</span>
            </button>
          </div>
        </label>

        <label class="field-label">
          Titel / Thema
          <input
            v-model="modal.form.title"
            class="input"
            placeholder="z.B. Monday Motivation, Behind the Scenes…"
            type="text"
            maxlength="120"
          />
        </label>

        <label class="field-label">
          Status
          <div class="status-options">
            <button
              v-for="s in statuses"
              :key="s.key"
              class="status-option"
              :class="{ selected: modal.form.status === s.key }"
              :data-status="s.key"
              type="button"
              @click="modal.form.status = s.key"
            >{{ s.label }}</button>
          </div>
        </label>

        <label class="field-label">
          Notiz (optional)
          <textarea
            v-model="modal.form.note"
            class="input textarea"
            placeholder="Kurze Notiz, Hashtags, Uhrzeit…"
            rows="3"
            maxlength="400"
          ></textarea>
        </label>

        <div class="modal-actions">
          <button class="btn ghost" type="button" @click="modal.open = false">Abbrechen</button>
          <button v-if="modal.isEdit" class="btn danger" type="button" @click="deleteAndClose">Löschen</button>
          <button class="btn" type="button" @click="savePost">{{ modal.isEdit ? "Speichern" : "Hinzufügen" }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const STORAGE_KEY = "content_schedule_v2";

// --------------- platforms ---------------
const platforms = [
  { key: "youtube",   icon: "🎬", label: "YouTube" },
  { key: "instagram", icon: "📸", label: "Instagram" },
  { key: "tiktok",    icon: "🎵", label: "TikTok" },
  { key: "twitter",   icon: "🐦", label: "X / Twitter" },
  { key: "podcast",   icon: "🎙️", label: "Podcast" },
  { key: "blog",      icon: "✍️", label: "Blog" },
  { key: "other",     icon: "📢", label: "Sonstiges" },
];

function platformIcon(key) {
  return platforms.find((p) => p.key === key)?.icon ?? "📢";
}
function platformLabel(key) {
  return platforms.find((p) => p.key === key)?.label ?? key;
}

// --------------- statuses ---------------
const statuses = [
  { key: "draft",  label: "Entwurf" },
  { key: "ready",  label: "Bereit" },
  { key: "posted", label: "Gepostet" },
];

function statusLabel(key) {
  return statuses.find((s) => s.key === key)?.label ?? key;
}

// --------------- week navigation ---------------
const weekOffset = ref(0);
const todayDate = new Date();
todayDate.setHours(0, 0, 0, 0);

function getWeekStart(offset) {
  const d = new Date(todayDate);
  const dow = d.getDay(); // 0=Sun
  const diff = dow === 0 ? -6 : 1 - dow; // shift to Monday
  d.setDate(d.getDate() + diff + offset * 7);
  return d;
}

const DAY_NAMES  = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"];
const DAY_SHORTS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"];

const days = computed(() => {
  const start = getWeekStart(weekOffset.value);
  return DAY_NAMES.map((label, i) => {
    const d = new Date(start);
    d.setDate(start.getDate() + i);
    const isToday = d.getTime() === todayDate.getTime();
    const dateKey = d.toISOString().slice(0, 10);
    return {
      label,
      short: DAY_SHORTS[i],
      isToday,
      dateKey,
      dateStr: d.toLocaleDateString("de-DE", { day: "numeric", month: "short" }),
      dateNum: d.getDate(),
    };
  });
});

const weekLabel = computed(() => {
  const first = days.value[0];
  const last  = days.value[6];
  const y = new Date(first.dateKey).getFullYear();
  return `${first.dateStr} – ${last.dateStr} ${y}`;
});

function prevWeek() { weekOffset.value--; }
function nextWeek() { weekOffset.value++; }
function goToCurrentWeek() { weekOffset.value = 0; }

// Active day for mobile tab navigation (default = today or Monday of the current week)
const todayKey = days.value.find((d) => d.isToday)?.dateKey;
const activeDay = ref(todayKey ?? days.value[0]?.dateKey ?? "");

// Keep activeDay in sync when week changes
watch(days, (newDays) => {
  const current = newDays.find((d) => d.dateKey === activeDay.value);
  if (!current) {
    const today = newDays.find((d) => d.isToday);
    activeDay.value = today ? today.dateKey : newDays[0].dateKey;
  }
});

// --------------- schedule (keyed by YYYY-MM-DD) ---------------
function loadSchedule() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore
  }
  return {};
}

const schedule = ref(loadSchedule());

watch(schedule, (val) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val));
  } catch {
    // storage full – silently ignore
  }
}, { deep: true });

function postsForDay(dateKey) {
  return schedule.value[dateKey] ?? [];
}

// --------------- stats ---------------
const weekPostCount = computed(() =>
  days.value.reduce((sum, d) => sum + postsForDay(d.dateKey).length, 0)
);

const statusStats = computed(() =>
  statuses.map((s) => ({
    key: s.key,
    label: s.label,
    count: days.value.reduce(
      (sum, d) => sum + postsForDay(d.dateKey).filter((p) => p.status === s.key).length,
      0
    ),
  })).filter((s) => s.count > 0)
);

// --------------- uid ---------------
let _uidCounter = 0;
function uid() {
  return crypto.randomUUID
    ? crypto.randomUUID()
    : `p${Date.now()}-${++_uidCounter}-${Math.random().toString(36).slice(2)}`;
}

// --------------- modal ---------------
const modal = ref({
  open: false,
  isEdit: false,
  dateKey: null,
  editId: null,
  form: { platform: "youtube", title: "", status: "draft", note: "" },
});

function freshForm() {
  return { platform: "youtube", title: "", status: "draft", note: "" };
}

function openAdd(dateKey) {
  modal.value = { open: true, isEdit: false, dateKey, editId: null, form: freshForm() };
}

function openEdit(dateKey, post) {
  modal.value = {
    open: true,
    isEdit: true,
    dateKey,
    editId: post.id,
    form: { platform: post.platform, title: post.title, status: post.status, note: post.note ?? "" },
  };
}

function savePost() {
  const { dateKey, isEdit, editId, form } = modal.value;
  if (!schedule.value[dateKey]) schedule.value[dateKey] = [];

  if (isEdit) {
    const idx = schedule.value[dateKey].findIndex((p) => p.id === editId);
    if (idx !== -1) {
      schedule.value[dateKey].splice(idx, 1, { ...schedule.value[dateKey][idx], ...form });
    }
  } else {
    schedule.value[dateKey].push({ id: uid(), ...form });
  }

  modal.value.open = false;
}

function deletePost(dateKey, postId) {
  if (!schedule.value[dateKey]) return;
  schedule.value[dateKey] = schedule.value[dateKey].filter((p) => p.id !== postId);
}

function deleteAndClose() {
  deletePost(modal.value.dateKey, modal.value.editId);
  modal.value.open = false;
}
</script>

<style scoped>
/* ---- Shell ---- */
.cs-tool {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  min-height: 100vh;
}

/* ---- Top bar ---- */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 18px 24px;
  flex-shrink: 0;
  gap: 12px;
  flex-wrap: wrap;
}

.topbar-left .eyebrow {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brand);
  margin: 0 0 2px;
}

.week-label {
  font-size: 1.15rem;
  font-weight: 800;
  margin: 0;
}

.topbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.week-nav {
  display: flex;
  align-items: center;
  gap: 4px;
}

.icon-btn {
  font-size: 1.2rem;
  padding: 6px 12px;
  min-width: 36px;
}

/* ---- Stats row ---- */
.stats-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.stat-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 6px 14px;
  font-size: 0.82rem;
  box-shadow: var(--shadow-soft);
}

.stat-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.stat-dot[data-status="draft"]  { background: #94a3b8; }
.stat-dot[data-status="ready"]  { background: var(--status-open); }
.stat-dot[data-status="posted"] { background: var(--status-done); }

.stat-val {
  font-weight: 700;
  color: var(--text);
}

.stat-label {
  color: var(--muted);
}

/* ---- Day tabs (shown on mobile, hidden on desktop) ---- */
.day-tabs {
  display: none;
  gap: 6px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: none;
}
.day-tabs::-webkit-scrollbar { display: none; }

.day-tab {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  min-width: 48px;
  padding: 8px 10px;
  border-radius: 12px;
  border: 1.5px solid var(--border);
  background: var(--card);
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.15s, background 0.15s;
  position: relative;
  flex-shrink: 0;
}

.day-tab.active {
  border-color: var(--brand);
  background: color-mix(in srgb, var(--brand) 10%, transparent);
}

.day-tab.today .tab-short {
  color: var(--brand);
  font-weight: 800;
}

.tab-short {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
}

.tab-date {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text);
}

.tab-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  background: var(--brand);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  min-width: 16px;
  height: 16px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

/* ---- Week grid ---- */
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 12px;
  align-items: start;
}

/* On mobile, .day-hidden hides non-active days.
   On desktop this class has no effect (overridden below). */
.day-hidden {
  display: none;
}

.day-column {
  padding: 14px 12px;
  min-height: 260px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.day-today {
  border-color: var(--brand);
  box-shadow: 0 0 0 1px var(--brand), var(--shadow-soft);
}

.day-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 6px;
}

.day-meta {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.day-name {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--muted);
}

.day-name.is-today {
  color: var(--brand);
}

.day-date {
  font-size: 0.72rem;
}

.add-btn {
  background: var(--brand);
  color: #ffffff;
  border: none;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  font-size: 1.1rem;
  line-height: 1;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: opacity 0.15s;
}

.add-btn:hover { opacity: 0.85; }

/* ---- Post list ---- */
.post-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}

/* ---- Post card ---- */
.post-card {
  border-radius: 10px;
  border: 1.5px solid var(--border);
  background: var(--card);
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
  box-shadow: var(--shadow-soft);
}

.post-card:hover {
  box-shadow: var(--shadow-strong);
}

.post-card[data-status="posted"] {
  opacity: 0.7;
}

.post-top {
  display: flex;
  align-items: center;
  gap: 6px;
}

.post-platform-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.post-title {
  flex: 1;
  font-size: 0.85rem;
  font-weight: 600;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--text);
}

.post-del {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 1rem;
  cursor: pointer;
  padding: 0 2px;
  line-height: 1;
  flex-shrink: 0;
  border-radius: 4px;
  transition: color 0.15s, background 0.15s;
}

.post-del:hover {
  color: var(--status-overdue);
  background: color-mix(in srgb, var(--status-overdue) 12%, transparent);
}

.post-note {
  font-size: 0.75rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.post-footer {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.platform-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(47, 99, 255, 0.1);
  color: var(--brand);
}

.platform-badge[data-platform="youtube"]   { background: color-mix(in srgb, var(--status-overdue) 12%, transparent);   color: var(--status-overdue); }
.platform-badge[data-platform="instagram"] { background: color-mix(in srgb, var(--status-review) 14%, transparent); color: var(--status-review); }
.platform-badge[data-platform="tiktok"]    { background: rgba(15, 23, 42, 0.1);   color: var(--text); }
.platform-badge[data-platform="twitter"]   { background: color-mix(in srgb, var(--brand) 14%, transparent); color: var(--brand); }
.platform-badge[data-platform="podcast"]   { background: color-mix(in srgb, var(--status-soon) 14%, transparent); color: var(--status-soon); }
.platform-badge[data-platform="blog"]      { background: rgba(100, 116, 139, 0.12); color: #64748b; }

.status-badge {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 6px;
}
.status-badge[data-status="draft"]  { background: rgba(148, 163, 184, 0.2); color: #64748b; }
.status-badge[data-status="ready"]  { background: color-mix(in srgb, var(--status-open) 16%, transparent); color: var(--status-open); }
.status-badge[data-status="posted"] { background: color-mix(in srgb, var(--status-done) 16%, transparent); color: var(--status-done); }

/* ---- Add post button ---- */
.add-post-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  width: 100%;
  padding: 8px;
  border-radius: 10px;
  border: 1.5px dashed var(--border);
  background: none;
  color: var(--muted);
  font-size: 0.8rem;
  font-family: inherit;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  margin-top: auto;
}

.add-post-btn:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: color-mix(in srgb, var(--brand) 7%, transparent);
}

.plus {
  font-size: 1rem;
  line-height: 1;
}

/* ---- Modal ---- */
.overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  padding: 28px;
  width: 100%;
  max-width: 480px;
  max-height: 90dvh;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.modal h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
}

.field-label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--muted);
}

.input {
  background: var(--input-bg);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 9px 12px;
  font-size: 0.9rem;
  color: var(--text);
  font-family: inherit;
  outline: none;
  transition: border-color 0.15s;
  width: 100%;
}

.input:focus {
  border-color: var(--brand);
  background: var(--input-bg-focus);
}

.textarea {
  resize: vertical;
  min-height: 72px;
}

/* ---- Platform grid ---- */
.platform-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.platform-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 10px 4px;
  border-radius: 10px;
  border: 1.5px solid var(--border);
  background: var(--bg-soft);
  cursor: pointer;
  font-family: inherit;
  transition: border-color 0.15s, background 0.15s;
}

.platform-option.selected {
  border-color: var(--brand);
  background: color-mix(in srgb, var(--brand) 10%, transparent);
}

.platform-opt-icon {
  font-size: 1.3rem;
}

.platform-opt-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: var(--text);
  text-align: center;
}

/* ---- Status options ---- */
.status-options {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.status-option {
  padding: 7px 16px;
  border-radius: 20px;
  border: 1.5px solid var(--border);
  background: var(--bg-soft);
  cursor: pointer;
  font-size: 0.85rem;
  font-family: inherit;
  font-weight: 600;
  transition: border-color 0.15s, background 0.15s, color 0.15s;
  color: var(--muted);
}

.status-option.selected[data-status="draft"]  { border-color: #94a3b8; background: rgba(148,163,184,0.15); color: var(--text); }
.status-option.selected[data-status="ready"]  { border-color: var(--status-open); background: color-mix(in srgb, var(--status-open) 13%, transparent); color: var(--status-open); }
.status-option.selected[data-status="posted"] { border-color: var(--status-done); background: color-mix(in srgb, var(--status-done) 13%, transparent); color: var(--status-done); }

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
  flex-wrap: wrap;
}

/* ---- Global button helpers ---- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 18px;
  border-radius: 10px;
  border: none;
  background: var(--brand);
  color: #fff;
  font-size: 0.88rem;
  font-weight: 700;
  font-family: inherit;
  cursor: pointer;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.btn:hover { opacity: 0.88; }

.btn.ghost {
  background: var(--card);
  border: 1.5px solid var(--border);
  color: var(--text);
}

.btn.ghost:hover {
  border-color: var(--brand);
  color: var(--brand);
  background: rgba(47, 99, 255, 0.06);
  opacity: 1;
}

.btn.danger {
  background: var(--status-overdue);
}

/* ---- Desktop: show all 7 columns, hide tabs ---- */
@media (min-width: 701px) {
  .day-tabs { display: none; }

  /* Override the mobile-only hide */
  .day-hidden { display: flex !important; }
}

/* ---- Large desktop layout ---- */
@media (min-width: 701px) and (max-width: 1100px) {
  .week-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (min-width: 1101px) {
  .week-grid {
    grid-template-columns: repeat(7, minmax(0, 1fr));
  }
}

/* ---- Mobile ---- */
@media (max-width: 700px) {
  .cs-tool {
    padding: 12px;
    gap: 12px;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    padding: 14px 16px;
    gap: 10px;
  }

  .week-label {
    font-size: 0.95rem;
  }

  .topbar-actions {
    width: 100%;
    justify-content: space-between;
  }

  /* Show day tabs */
  .day-tabs {
    display: flex;
  }

  /* Week grid: single column, one panel visible at a time */
  .week-grid {
    grid-template-columns: 1fr;
  }

  .day-column {
    min-height: 200px;
  }

  .platform-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}
</style>
