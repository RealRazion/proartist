<template>
  <div class="promo-queue-view">
    <!-- Header -->
    <header class="queue-header card">
      <div class="header-main">
        <div class="header-text">
          <div class="title-row">
            <span class="queue-icon">🚀</span>
            <div>
              <h2>Release &amp; Promo Queue</h2>
              <p class="muted small">
                Verwalte deine Song-Releases, erstelle flexible Promo-Modelle (Daily TikToks, Collabs etc.) und behalte deine täglichen To-Dos im Blick.
              </p>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn ghost" type="button" @click="triggerReminders" :disabled="reminderSending" title="Erinnerung per E-Mail auslösen">
            <span>🔔</span>
            <span>{{ reminderSending ? "Sende..." : "19:00 Reminder testen" }}</span>
          </button>
          <button class="btn ghost" type="button" @click="fetchData" :disabled="loading" title="Aktualisieren">
            <span :class="{ spinning: loading }">↻</span>
            <span>Aktualisieren</span>
          </button>
          <button class="btn primary-glow" type="button" @click="openCreateModal">
            <span>+</span>
            <span>Neuer Release</span>
          </button>
        </div>
      </div>

      <!-- KPI Bar -->
      <div class="kpi-strip">
        <div class="kpi-item">
          <span class="kpi-label">Aktive Releases</span>
          <strong class="kpi-val">{{ releases.length }}</strong>
        </div>
        <div class="kpi-item highlight">
          <span class="kpi-label">Heute zu posten</span>
          <strong class="kpi-val">{{ todayPendingCount }}</strong>
          <small class="kpi-sub" v-if="todayPendingCount > 0">Noch offen!</small>
          <small class="kpi-sub success" v-else>Alles erledigt 🎉</small>
        </div>
        <div class="kpi-item">
          <span class="kpi-label">Heute erledigt</span>
          <strong class="kpi-val success">{{ todayCompletedCount }} / {{ todayTasks.length }}</strong>
        </div>
        <div class="kpi-item">
          <span class="kpi-label">Gesamte Promo-Tasks</span>
          <strong class="kpi-val">{{ allTasks.length }}</strong>
        </div>
        <div class="kpi-item reminder-badge">
          <span class="kpi-label">19:00 Mail-Reminder</span>
          <span class="badge-status-on">● Aktiviert</span>
        </div>
      </div>
    </header>

    <!-- Navigation Tabs -->
    <div class="tab-controls">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'today' }"
        @click="activeTab = 'today'"
      >
        <span>📅</span>
        <span>Heute zu tun</span>
        <span class="tab-badge" v-if="todayPendingCount > 0">{{ todayPendingCount }}</span>
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'releases' }"
        @click="activeTab = 'releases'"
      >
        <span>💿</span>
        <span>Releases &amp; Kampagnen</span>
        <span class="tab-count">({{ releases.length }})</span>
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'all' }"
        @click="activeTab = 'all'"
      >
        <span>🗓️</span>
        <span>Gesamte Timeline</span>
      </button>
    </div>

    <!-- TAB 1: HEUTE ZU TUN -->
    <main v-if="activeTab === 'today'" class="tab-content">
      <div class="today-banner card">
        <div class="today-date-box">
          <span class="today-day">{{ formatTodayDay() }}</span>
          <span class="today-full">{{ formatTodayDate() }}</span>
        </div>
        <div class="today-status-info">
          <h3>Tages-Promo Fokus</h3>
          <p class="muted small" v-if="todayPendingCount > 0">
            Du hast für heute <strong>{{ todayPendingCount }}</strong> offene Promo-Aufgaben. Falls bis 19:00 Uhr noch etwas offen ist, schicken wir dir eine automatische Erinnerung!
          </p>
          <p class="muted small success-text" v-else-if="todayTasks.length > 0">
            Großartig! Alle für heute geplanten Promo-Posts sind erledigt. Dein Release gewinnt Momentum! 🚀
          </p>
          <p class="muted small" v-else>
            Für heute stehen keine Promo-Posts an. Plane neue Releases oder genieße deinen Fokus!
          </p>
        </div>
      </div>

      <!-- Filter pills -->
      <div class="filter-row">
        <div class="filter-pills">
          <button
            class="filter-pill"
            :class="{ active: todayFilter === 'all' }"
            @click="todayFilter = 'all'"
          >
            Alle ({{ todayTasks.length }})
          </button>
          <button
            class="filter-pill"
            :class="{ active: todayFilter === 'pending' }"
            @click="todayFilter = 'pending'"
          >
            Offen ({{ todayPendingCount }})
          </button>
          <button
            class="filter-pill"
            :class="{ active: todayFilter === 'completed' }"
            @click="todayFilter = 'completed'"
          >
            Erledigt ({{ todayCompletedCount }})
          </button>
        </div>
      </div>

      <!-- Today's Tasks List -->
      <div class="promo-task-list" v-if="filteredTodayTasks.length">
        <article
          v-for="task in filteredTodayTasks"
          :key="task.id"
          class="promo-task-card card"
          :class="{ completed: task.is_completed }"
        >
          <div class="task-checkbox-col">
            <label class="custom-check-container" :title="task.is_completed ? 'Als offen markieren' : 'Als gepostet markieren'">
              <input
                type="checkbox"
                :checked="task.is_completed"
                @change="toggleTaskDone(task)"
              />
              <span class="checkmark"></span>
            </label>
          </div>

          <div class="task-body">
            <div class="task-meta-top">
              <span class="category-pill" :data-cat="task.category">{{ categoryLabel(task.category) }}</span>
              <span class="platform-pill">{{ task.platform || 'TikTok / Reels' }}</span>
              <span class="release-pill" v-if="task.release_title">
                💿 {{ task.release_title }}
              </span>
              <span class="artist-pill" v-if="task.artist_name">
                👤 {{ task.artist_name }}
              </span>
            </div>

            <h4 class="task-headline" :class="{ strike: task.is_completed }">
              {{ task.title }}
            </h4>

            <p class="task-notes muted" v-if="task.notes">
              💡 {{ task.notes }}
            </p>
          </div>

          <div class="task-action-col">
            <button
              class="btn tiny"
              :class="task.is_completed ? 'ghost' : 'success-btn'"
              type="button"
              @click="toggleTaskDone(task)"
            >
              {{ task.is_completed ? "Wieder öffnen" : "✓ Gepostet!" }}
            </button>
          </div>
        </article>
      </div>

      <div class="empty-state card" v-else>
        <div class="empty-icon">🎉</div>
        <h3>Keine Promo-Aufgaben in dieser Ansicht</h3>
        <p class="muted">Alle Posts für heute sind abgehakt oder es wurde noch kein Release für diesen Tag angelegt.</p>
        <button class="btn ghost" type="button" @click="openCreateModal">+ Neuen Release anlegen</button>
      </div>
    </main>

    <!-- TAB 2: RELEASES & KAMPAGNEN -->
    <main v-if="activeTab === 'releases'" class="tab-content">
      <div class="releases-controls">
        <div class="search-box">
          <input
            class="input"
            v-model.trim="releaseSearch"
            placeholder="Releases durchsuchen nach Titel oder Artist..."
          />
        </div>
        <button class="btn" type="button" @click="openCreateModal">+ Neuer Release</button>
      </div>

      <div class="releases-grid" v-if="filteredReleases.length">
        <article
          v-for="rel in filteredReleases"
          :key="rel.id"
          class="release-card card"
        >
          <div class="rel-card-head">
            <div class="rel-icon-cover">💿</div>
            <div class="rel-info">
              <div class="rel-artist-tag" v-if="rel.artist_name">
                <span>👤 {{ rel.artist_name }}</span>
                <span class="created-by-tag" v-if="rel.created_by_name && rel.created_by_name !== rel.artist_name">
                  (vom Team: {{ rel.created_by_name }})
                </span>
              </div>
              <h3 class="rel-title">{{ rel.title }}</h3>
              <div class="rel-date-row">
                <span class="rel-date">
                  📅 {{ formatReleaseDate(rel.planned_date) }}
                </span>
                <span class="countdown-pill" :class="getCountdownClass(rel.planned_date)">
                  {{ getCountdownText(rel.planned_date) }}
                </span>
              </div>
            </div>
          </div>

          <div class="rel-meta-box">
            <div class="rel-promo-model">
              <span class="muted small">Promo-Modell:</span>
              <strong>{{ promoModelLabel(rel.promo_model) }}</strong>
            </div>
            <div class="rel-progress-wrap">
              <div class="progress-labels">
                <span class="small muted">Promo-Fortschritt</span>
                <span class="small">
                  <strong>{{ rel.completed_promo_tasks_count || 0 }}</strong> / {{ rel.promo_tasks_count || 0 }} Posts
                </span>
              </div>
              <div class="progress-bar-bg">
                <div
                  class="progress-bar-fill"
                  :style="{ width: calcPercent(rel.completed_promo_tasks_count, rel.promo_tasks_count) + '%' }"
                ></div>
              </div>
            </div>
          </div>

          <div class="rel-notes" v-if="rel.notes">
            <p class="small muted">📝 {{ rel.notes }}</p>
          </div>

          <div class="rel-card-actions">
            <button class="btn ghost tiny" type="button" @click="viewReleaseTasks(rel)">
              Tasks einsehen
            </button>
            <button class="btn ghost tiny" type="button" @click="regenerateTasks(rel)">
              Plan neu berechnen
            </button>
            <button class="btn ghost danger tiny" type="button" @click="deleteRelease(rel)">
              Löschen
            </button>
          </div>
        </article>
      </div>

      <div class="empty-state card" v-else>
        <div class="empty-icon">💿</div>
        <h3>Noch keine Releases angelegt</h3>
        <p class="muted">
          Erstelle deinen ersten Release mit Veröffentlichungsdatum und wähle dein Promo-Modell (z.B. tägliche TikToks).
        </p>
        <button class="btn" type="button" @click="openCreateModal">+ Release anlegen</button>
      </div>
    </main>

    <!-- TAB 3: GESAMTE TIMELINE -->
    <main v-if="activeTab === 'all'" class="tab-content">
      <div class="timeline-group-list" v-if="groupedTimelineTasks.length">
        <section
          v-for="group in groupedTimelineTasks"
          :key="group.dateKey"
          class="timeline-day-block"
        >
          <div class="day-divider" :class="{ 'is-today': group.isToday }">
            <span class="day-tag">{{ group.label }}</span>
            <span class="day-line"></span>
            <span class="day-count">{{ group.tasks.length }} Tasks</span>
          </div>

          <div class="promo-task-list">
            <article
              v-for="task in group.tasks"
              :key="task.id"
              class="promo-task-card card"
              :class="{ completed: task.is_completed }"
            >
              <div class="task-checkbox-col">
                <label class="custom-check-container">
                  <input
                    type="checkbox"
                    :checked="task.is_completed"
                    @change="toggleTaskDone(task)"
                  />
                  <span class="checkmark"></span>
                </label>
              </div>

              <div class="task-body">
                <div class="task-meta-top">
                  <span class="category-pill" :data-cat="task.category">{{ categoryLabel(task.category) }}</span>
                  <span class="platform-pill">{{ task.platform }}</span>
                  <span class="release-pill" v-if="task.release_title">💿 {{ task.release_title }}</span>
                  <span class="artist-pill" v-if="task.artist_name">👤 {{ task.artist_name }}</span>
                </div>
                <h4 class="task-headline" :class="{ strike: task.is_completed }">
                  {{ task.title }}
                </h4>
                <p class="task-notes muted small" v-if="task.notes">
                  💡 {{ task.notes }}
                </p>
              </div>

              <div class="task-action-col">
                <button
                  class="btn tiny"
                  :class="task.is_completed ? 'ghost' : 'success-btn'"
                  type="button"
                  @click="toggleTaskDone(task)"
                >
                  {{ task.is_completed ? "Wieder öffnen" : "Gepostet" }}
                </button>
              </div>
            </article>
          </div>
        </section>
      </div>

      <div class="empty-state card" v-else>
        <div class="empty-icon">🗓️</div>
        <h3>Keine geplanten Promo-Tasks</h3>
        <p class="muted">Sobald du einen Release anlegst, werden hier alle täglichen Aufgaben aufgelistet.</p>
      </div>
    </main>

    <!-- CREATE RELEASE MODAL -->
    <div class="modal-backdrop" v-if="showCreateModal" @click.self="showCreateModal = false">
      <div class="modal card create-modal-box">
        <div class="modal-head">
          <div>
            <h3>Neuen Release &amp; Promo-Plan anlegen</h3>
            <p class="muted small">
              Gib einfach an, wann der Track rauskommt, und wähle dein gewünschtes Promo-Modell.
            </p>
          </div>
          <button class="btn ghost tiny" type="button" @click="showCreateModal = false">✕</button>
        </div>

        <form class="modal-form" @submit.prevent="submitCreateRelease">
          <!-- Title -->
          <label class="form-field">
            <span>Track- / Release-Titel *</span>
            <input
              class="input"
              v-model.trim="newRelease.title"
              placeholder="z. B. Hyperdrive, Moonlight Echoes..."
              required
            />
          </label>

          <!-- Artist selection (Available for Team or pre-filled) -->
          <div class="form-field">
            <span>Artist / Künstler *</span>
            <select
              class="input"
              v-model="newRelease.profile_id"
              v-if="isTeam && profileOptions.length"
            >
              <option v-for="p in profileOptions" :key="p.id" :value="p.id">
                {{ p.name }} ({{ p.username }})
              </option>
            </select>
            <input
              v-else
              class="input disabled-look"
              :value="currentProfileName"
              disabled
            />
            <small class="muted" v-if="isTeam">
              Als Team-Mitglied kannst du Releases direkt für jeden Artist einpflegen.
            </small>
          </div>

          <!-- Planned Release Date -->
          <label class="form-field">
            <span>Release-Datum (Wann kommt der Track raus?) *</span>
            <input
              class="input"
              type="date"
              v-model="newRelease.planned_date"
              required
            />
          </label>

          <!-- Promo Model Presets -->
          <div class="form-field">
            <span>Promo-Modell Preset</span>
            <div class="preset-buttons">
              <button
                type="button"
                class="preset-btn"
                :class="{ active: newRelease.promo_model === 'DAILY_7D' }"
                @click="applyPreset('DAILY_7D')"
              >
                <strong>🔥 7-Tage TikTok Drop</strong>
                <small>Täglich 1 TikTok + Pre-Save + Release Day</small>
              </button>
              <button
                type="button"
                class="preset-btn"
                :class="{ active: newRelease.promo_model === 'HIGH_VOLTAGE' }"
                @click="applyPreset('HIGH_VOLTAGE')"
              >
                <strong>⚡ 14-Tage High Voltage</strong>
                <small>Daily TikToks + Snippet + Collab + Push</small>
              </button>
              <button
                type="button"
                class="preset-btn"
                :class="{ active: newRelease.promo_model === 'QUICK_DROP' }"
                @click="applyPreset('QUICK_DROP')"
              >
                <strong>⚡ 3-Tage Quick Drop</strong>
                <small>Kurzer Teaser + Release Day Blast</small>
              </button>
              <button
                type="button"
                class="preset-btn"
                :class="{ active: newRelease.promo_model === 'CUSTOM' }"
                @click="newRelease.promo_model = 'CUSTOM'"
              >
                <strong>🛠️ Individuell</strong>
                <small>Bausteine manuell wählen</small>
              </button>
            </div>
          </div>

          <!-- Variable Options / Modules -->
          <div class="promo-modules-box">
            <h4>Variable Kampagnen-Bausteine</h4>

            <!-- Daily TikTok Posts -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_daily_tiktok" />
                <span>Tägliche TikTok / Reel Posts</span>
              </label>
              <div class="module-param" v-if="newRelease.plan.include_daily_tiktok">
                <label>
                  <small>Tage vor Release:</small>
                  <select class="input-inline" v-model.number="newRelease.plan.daily_tiktok_days">
                    <option :value="3">3 Tage</option>
                    <option :value="5">5 Tage</option>
                    <option :value="7">7 Tage (Standard)</option>
                    <option :value="10">10 Tage</option>
                    <option :value="14">14 Tage</option>
                  </select>
                </label>
              </div>
            </div>

            <!-- Collab Post -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_collab_post" />
                <span>Collab-Post (Partner-Einladung)</span>
              </label>
              <div class="module-param" v-if="newRelease.plan.include_collab_post">
                <input
                  class="input-inline"
                  v-model.trim="newRelease.plan.collab_partner"
                  placeholder="Partner Name / @Handle..."
                />
              </div>
            </div>

            <!-- Audio Snippet -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_snippet" />
                <span>Audio Snippet Drop (Erste 15 Sek. Hook)</span>
              </label>
            </div>

            <!-- Pre-Save -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_presave" />
                <span>Pre-Save Link &amp; Bio-Update</span>
              </label>
            </div>

            <!-- Release Day -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_release_day" />
                <span>Release Day Blast (Storys, Feed, Canvas, Bio)</span>
              </label>
            </div>

            <!-- Post Release Push -->
            <div class="module-row">
              <label class="checkbox-label">
                <input type="checkbox" v-model="newRelease.plan.include_post_push" />
                <span>Post-Release Push (Community Storys &amp; Feedback)</span>
              </label>
            </div>
          </div>

          <!-- Reminder Toggle -->
          <div class="reminder-toggle-box">
            <label class="checkbox-label">
              <input type="checkbox" v-model="newRelease.reminder_email_enabled" />
              <span>⏰ Tägliche E-Mail-Erinnerung gegen 19:00 Uhr aktivieren, falls der Post noch offen ist</span>
            </label>
          </div>

          <!-- Notes -->
          <label class="form-field">
            <span>Notizen zum Release (optional)</span>
            <textarea
              class="input textarea"
              v-model="newRelease.notes"
              rows="2"
              placeholder="z.B. Beatmaker, Song-Stimmung, wichtige Hashtags..."
            ></textarea>
          </label>

          <div class="modal-foot">
            <button class="btn ghost" type="button" @click="showCreateModal = false">Abbrechen</button>
            <button class="btn primary-glow" type="submit" :disabled="creating">
              {{ creating ? "Erstelle..." : "Release anlegen & Promo-Queue starten" }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { showToast } = useToast();
const { profile: currentProfile, isTeam } = useCurrentProfile();

const loading = ref(false);
const reminderSending = ref(false);
const creating = ref(false);
const activeTab = ref("today"); // today, releases, all
const todayFilter = ref("all"); // all, pending, completed
const releaseSearch = ref("");

const releases = ref([]);
const allTasks = ref([]);
const profiles = ref([]);
const showCreateModal = ref(false);

const newRelease = ref({
  title: "",
  profile_id: "",
  planned_date: "",
  promo_model: "DAILY_7D",
  reminder_email_enabled: true,
  notes: "",
  plan: {
    include_daily_tiktok: true,
    daily_tiktok_days: 7,
    include_collab_post: false,
    collab_partner: "",
    include_snippet: true,
    include_presave: true,
    include_release_day: true,
    include_post_push: true,
  },
});

const currentProfileName = computed(() => {
  return currentProfile.value?.name || currentProfile.value?.username || "Mein Account";
});

const profileOptions = computed(() => {
  return profiles.value || [];
});

const todayDateStr = computed(() => {
  return new Date().toISOString().slice(0, 10);
});

const todayTasks = computed(() => {
  const t = todayDateStr.value;
  return allTasks.value.filter((task) => task.scheduled_date === t);
});

const todayPendingCount = computed(() => {
  return todayTasks.value.filter((t) => !t.is_completed).length;
});

const todayCompletedCount = computed(() => {
  return todayTasks.value.filter((t) => t.is_completed).length;
});

const filteredTodayTasks = computed(() => {
  if (todayFilter.value === "pending") {
    return todayTasks.value.filter((t) => !t.is_completed);
  }
  if (todayFilter.value === "completed") {
    return todayTasks.value.filter((t) => t.is_completed);
  }
  return todayTasks.value;
});

const filteredReleases = computed(() => {
  if (!releaseSearch.value) return releases.value;
  const q = releaseSearch.value.toLowerCase();
  return releases.value.filter((r) => {
    return (
      (r.title && r.title.toLowerCase().includes(q)) ||
      (r.artist_name && r.artist_name.toLowerCase().includes(q))
    );
  });
});

const groupedTimelineTasks = computed(() => {
  const groups = {};
  const today = todayDateStr.value;

  const sorted = [...allTasks.value].sort((a, b) => {
    return (a.scheduled_date || "").localeCompare(b.scheduled_date || "");
  });

  for (const task of sorted) {
    const d = task.scheduled_date || "Kein Datum";
    if (!groups[d]) {
      groups[d] = {
        dateKey: d,
        isToday: d === today,
        label: formatTimelineDateLabel(d),
        tasks: [],
      };
    }
    groups[d].tasks.push(task);
  }

  return Object.values(groups);
});

async function fetchData() {
  loading.value = true;
  try {
    const [relRes, tasksRes, profRes] = await Promise.all([
      api.get("releases/"),
      api.get("promo-queue/"),
      isTeam.value ? api.get("profiles/") : Promise.resolve({ data: [] }),
    ]);

    releases.value = Array.isArray(relRes.data) ? relRes.data : relRes.data?.results || [];
    allTasks.value = Array.isArray(tasksRes.data) ? tasksRes.data : tasksRes.data?.results || [];
    if (profRes && profRes.data) {
      profiles.value = Array.isArray(profRes.data) ? profRes.data : profRes.data?.results || [];
    }
  } catch (err) {
    showToast("Fehler beim Laden der Releases & Promo Queue", "error");
  } finally {
    loading.value = false;
  }
}

async function toggleTaskDone(task) {
  try {
    const res = await api.post(`promo-queue/${task.id}/toggle_complete/`);
    if (res.data) {
      task.is_completed = res.data.is_completed;
      task.completed_at = res.data.completed_at;
      showToast(task.is_completed ? "✓ Promo-Post als erledigt markiert!" : "Task wieder geöffnet", "info");
      // Update release completed count
      const rel = releases.value.find((r) => r.id === task.release);
      if (rel) {
        rel.completed_promo_tasks_count = (rel.completed_promo_tasks_count || 0) + (task.is_completed ? 1 : -1);
      }
    }
  } catch (err) {
    showToast("Status konnte nicht geändert werden", "error");
  }
}

async function triggerReminders() {
  reminderSending.value = true;
  try {
    const res = await api.post("promo-queue/send_reminders/");
    const count = res.data?.pending_tasks_count || 0;
    const artists = res.data?.artists_reminded || 0;
    showToast(
      `Reminder ausgelöst! ${count} offene Posts für heute gefunden (${artists} Artists per Mail benachrichtigt).`,
      "info"
    );
  } catch (err) {
    showToast("Fehler beim Auslösen der Reminder", "error");
  } finally {
    reminderSending.value = false;
  }
}

function openCreateModal() {
  newRelease.value = {
    title: "",
    profile_id: currentProfile.value?.id || "",
    planned_date: getSuggestedReleaseDate(),
    promo_model: "DAILY_7D",
    reminder_email_enabled: true,
    notes: "",
    plan: {
      include_daily_tiktok: true,
      daily_tiktok_days: 7,
      include_collab_post: false,
      collab_partner: "",
      include_snippet: true,
      include_presave: true,
      include_release_day: true,
      include_post_push: true,
    },
  };
  showCreateModal.value = true;
}

function applyPreset(presetKey) {
  newRelease.value.promo_model = presetKey;
  if (presetKey === "DAILY_7D") {
    newRelease.value.plan.include_daily_tiktok = true;
    newRelease.value.plan.daily_tiktok_days = 7;
    newRelease.value.plan.include_collab_post = false;
    newRelease.value.plan.include_snippet = true;
    newRelease.value.plan.include_presave = true;
    newRelease.value.plan.include_release_day = true;
    newRelease.value.plan.include_post_push = true;
  } else if (presetKey === "HIGH_VOLTAGE") {
    newRelease.value.plan.include_daily_tiktok = true;
    newRelease.value.plan.daily_tiktok_days = 14;
    newRelease.value.plan.include_collab_post = true;
    newRelease.value.plan.include_snippet = true;
    newRelease.value.plan.include_presave = true;
    newRelease.value.plan.include_release_day = true;
    newRelease.value.plan.include_post_push = true;
  } else if (presetKey === "QUICK_DROP") {
    newRelease.value.plan.include_daily_tiktok = true;
    newRelease.value.plan.daily_tiktok_days = 3;
    newRelease.value.plan.include_collab_post = false;
    newRelease.value.plan.include_snippet = false;
    newRelease.value.plan.include_presave = true;
    newRelease.value.plan.include_release_day = true;
    newRelease.value.plan.include_post_push = false;
  }
}

async function submitCreateRelease() {
  if (!newRelease.value.title || !newRelease.value.planned_date) {
    showToast("Bitte Titel und Release-Datum angeben", "warning");
    return;
  }

  creating.value = true;
  try {
    const payload = {
      title: newRelease.value.title,
      planned_date: newRelease.value.planned_date,
      promo_model: newRelease.value.promo_model,
      promo_plan: newRelease.value.plan,
      reminder_email_enabled: newRelease.value.reminder_email_enabled,
      notes: newRelease.value.notes,
      profile: newRelease.value.profile_id || currentProfile.value?.id,
    };

    const res = await api.post("releases/", payload);
    showToast(`Release '${res.data.title}' erfolgreich angelegt & Promo Queue generiert!`, "info");
    showCreateModal.value = false;
    await fetchData();
    activeTab.value = "today";
  } catch (err) {
    showToast("Fehler beim Erstellen des Releases", "error");
  } finally {
    creating.value = false;
  }
}

async function regenerateTasks(rel) {
  if (!confirm(`Promo-Plan für '${rel.title}' wirklich neu generieren? Offene Aufgaben werden neu terminiert.`)) {
    return;
  }
  try {
    const res = await api.post(`releases/${rel.id}/regenerate_promo/`);
    showToast(`${res.data.generated_count} Promo-Aufgaben neu generiert!`, "info");
    await fetchData();
  } catch (err) {
    showToast("Fehler beim Neu-Berechnen", "error");
  }
}

async function deleteRelease(rel) {
  if (!confirm(`Release '${rel.title}' und alle zugehörigen Promo-Tasks wirklich löschen?`)) {
    return;
  }
  try {
    await api.delete(`releases/${rel.id}/`);
    showToast("Release gelöscht", "info");
    await fetchData();
  } catch (err) {
    showToast("Fehler beim Löschen des Releases", "error");
  }
}

function viewReleaseTasks(rel) {
  activeTab.value = "all";
}

function getSuggestedReleaseDate() {
  const d = new Date();
  d.setDate(d.getDate() + 14); // 2 weeks ahead by default
  return d.toISOString().slice(0, 10);
}

function formatTodayDay() {
  const days = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"];
  return days[new Date().getDay()];
}

function formatTodayDate() {
  return new Date().toLocaleDateString("de-DE", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function formatReleaseDate(d) {
  if (!d) return "Unbekannt";
  try {
    return new Date(d).toLocaleDateString("de-DE", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  } catch {
    return d;
  }
}

function formatTimelineDateLabel(d) {
  const today = todayDateStr.value;
  if (d === today) return `Heute (${formatReleaseDate(d)})`;
  return formatReleaseDate(d);
}

function getCountdownText(dateStr) {
  if (!dateStr) return "-";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  target.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - today) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "🚀 Heute Release!";
  if (diffDays === 1) return "Morgen!";
  if (diffDays > 1) return `Noch ${diffDays} Tage`;
  return `Vor ${Math.abs(diffDays)} Tagen`;
}

function getCountdownClass(dateStr) {
  if (!dateStr) return "";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  target.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - today) / (1000 * 60 * 60 * 24));

  if (diffDays === 0) return "drop-today";
  if (diffDays <= 3 && diffDays > 0) return "drop-soon";
  if (diffDays > 3) return "drop-future";
  return "drop-passed";
}

function categoryLabel(cat) {
  const map = {
    TIKTOK_DAILY: "TikTok Daily",
    COLLAB_POST: "Collab Post",
    SNIPPET: "Audio Snippet",
    PRE_SAVE: "Pre-Save Launch",
    RELEASE_DAY: "Release Day Blast",
    POST_PUSH: "Post-Release Push",
    CUSTOM: "Custom Promo",
  };
  return map[cat] || cat;
}

function promoModelLabel(model) {
  const map = {
    DAILY_7D: "7 Tage Daily TikTok",
    HIGH_VOLTAGE: "14 Tage High Voltage",
    QUICK_DROP: "3 Tage Quick Drop",
    CUSTOM: "Individuell",
  };
  return map[model] || model || "Standard";
}

function calcPercent(completed, total) {
  if (!total) return 0;
  return Math.min(100, Math.round(((completed || 0) / total) * 100));
}

onMounted(() => {
  fetchData();
});
</script>

<style scoped>
.promo-queue-view {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 1.5rem 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.queue-header {
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
}

.header-main {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.title-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.queue-icon {
  font-size: 2.2rem;
  background: rgba(99, 102, 241, 0.15);
  border: 1px solid rgba(99, 102, 241, 0.3);
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
}

.title-row h2 {
  margin: 0;
  font-size: 1.45rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.kpi-strip {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.kpi-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.kpi-label {
  font-size: 0.78rem;
  color: var(--muted, #94a3b8);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

.kpi-val {
  font-size: 1.4rem;
  font-weight: 700;
}

.kpi-sub {
  font-size: 0.75rem;
  color: #f59e0b;
}

.kpi-sub.success,
.kpi-val.success {
  color: #10b981;
}

.kpi-item.highlight .kpi-val {
  color: #38bdf8;
}

.badge-status-on {
  font-size: 0.8rem;
  color: #10b981;
  font-weight: 600;
}

.tab-controls {
  display: flex;
  gap: 0.75rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 0.5rem;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.2rem;
  border-radius: 10px;
  background: transparent;
  color: var(--muted, #94a3b8);
  border: none;
  font-weight: 600;
  font-size: 0.92rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--text, #f8fafc);
  background: rgba(255, 255, 255, 0.04);
}

.tab-btn.active {
  color: #fff;
  background: var(--primary, #4f46e5);
}

.tab-badge {
  background: #ef4444;
  color: white;
  border-radius: 999px;
  font-size: 0.72rem;
  padding: 0.1rem 0.5rem;
  font-weight: 700;
}

.tab-count {
  font-size: 0.8rem;
  opacity: 0.75;
}

.today-banner {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 1.25rem 1.5rem;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.12), rgba(56, 189, 248, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 14px;
}

.today-date-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 10px;
  padding: 0.6rem 1rem;
  min-width: 120px;
  text-align: center;
}

.today-day {
  font-size: 1.15rem;
  font-weight: 800;
  color: #38bdf8;
}

.today-full {
  font-size: 0.78rem;
  color: var(--muted, #94a3b8);
}

.today-status-info h3 {
  margin: 0 0 0.25rem;
  font-size: 1.1rem;
}

.success-text {
  color: #10b981 !important;
  font-weight: 500;
}

.filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 1rem 0;
}

.filter-pills {
  display: flex;
  gap: 0.5rem;
}

.filter-pill {
  padding: 0.4rem 0.85rem;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.02);
  color: var(--muted, #94a3b8);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.15s;
}

.filter-pill:hover {
  background: rgba(255, 255, 255, 0.06);
}

.filter-pill.active {
  background: rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
  color: #fff;
}

.promo-task-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.promo-task-card {
  display: flex;
  align-items: center;
  gap: 1.25rem;
  padding: 1.1rem 1.25rem;
  border-radius: 12px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.07));
  transition: transform 0.15s ease, border-color 0.15s ease;
}

.promo-task-card:hover {
  border-color: rgba(99, 102, 241, 0.4);
}

.promo-task-card.completed {
  opacity: 0.65;
  background: rgba(255, 255, 255, 0.02);
}

.custom-check-container {
  display: block;
  position: relative;
  cursor: pointer;
  user-select: none;
  width: 24px;
  height: 24px;
}

.custom-check-container input {
  opacity: 0;
  position: absolute;
  cursor: pointer;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 24px;
  width: 24px;
  background: rgba(255, 255, 255, 0.06);
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  transition: all 0.15s;
}

.custom-check-container input:checked ~ .checkmark {
  background: #10b981;
  border-color: #10b981;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
  left: 7px;
  top: 3px;
  width: 6px;
  height: 12px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.custom-check-container input:checked ~ .checkmark:after {
  display: block;
}

.task-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.task-meta-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  font-weight: 600;
}

.platform-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(236, 72, 153, 0.15);
  color: #f472b6;
  font-weight: 500;
}

.release-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(56, 189, 248, 0.15);
  color: #7dd3fc;
  font-weight: 600;
}

.artist-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted, #cbd5e1);
}

.task-headline {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text, #f8fafc);
}

.task-headline.strike {
  text-decoration: line-through;
  opacity: 0.7;
}

.task-notes {
  margin: 0;
  font-size: 0.82rem;
}

.success-btn {
  background: #10b981 !important;
  color: white !important;
  border: none !important;
  font-weight: 600;
}

.empty-state {
  padding: 3rem 1.5rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  border-radius: 14px;
}

.empty-icon {
  font-size: 2.8rem;
}

.releases-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.25rem;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  max-width: 420px;
}

.releases-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 1.25rem;
}

.release-card {
  padding: 1.25rem;
  border-radius: 14px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.rel-card-head {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.rel-icon-cover {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  background: rgba(56, 189, 248, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
}

.rel-info {
  flex: 1;
}

.rel-artist-tag {
  font-size: 0.76rem;
  color: var(--muted, #94a3b8);
  font-weight: 500;
}

.created-by-tag {
  font-size: 0.72rem;
  color: #a5b4fc;
}

.rel-title {
  margin: 0.15rem 0 0.35rem;
  font-size: 1.15rem;
  font-weight: 700;
}

.rel-date-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.rel-date {
  font-size: 0.8rem;
  color: var(--muted, #cbd5e1);
}

.countdown-pill {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-weight: 700;
}

.countdown-pill.drop-today {
  background: #10b981;
  color: white;
  animation: pulse 2s infinite;
}

.countdown-pill.drop-soon {
  background: #f59e0b;
  color: white;
}

.countdown-pill.drop-future {
  background: rgba(255, 255, 255, 0.1);
  color: var(--muted, #94a3b8);
}

.countdown-pill.drop-passed {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted, #64748b);
}

.rel-meta-box {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.85rem;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.2);
}

.rel-promo-model {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.82rem;
}

.rel-progress-wrap {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.progress-labels {
  display: flex;
  justify-content: space-between;
}

.progress-bar-bg {
  height: 6px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #38bdf8);
  border-radius: 999px;
  transition: width 0.3s ease;
}

.rel-card-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: auto;
}

.timeline-day-block {
  margin-bottom: 2rem;
}

.day-divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.day-tag {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text, #f8fafc);
  white-space: nowrap;
}

.day-divider.is-today .day-tag {
  color: #38bdf8;
}

.day-line {
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
}

.day-count {
  font-size: 0.78rem;
  color: var(--muted, #94a3b8);
  white-space: nowrap;
}

/* Modal Styling */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.create-modal-box {
  width: 100%;
  max-width: 620px;
  max-height: 90vh;
  overflow-y: auto;
  border-radius: 16px;
  background: #141821;
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 1.5rem;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.modal-head h3 {
  margin: 0 0 0.25rem;
  font-size: 1.25rem;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.88rem;
  font-weight: 500;
}

.disabled-look {
  opacity: 0.7;
  cursor: not-allowed;
}

.preset-buttons {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 0.6rem;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.65rem;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: var(--text, #f8fafc);
  text-align: left;
  cursor: pointer;
  transition: all 0.15s;
}

.preset-btn:hover {
  background: rgba(255, 255, 255, 0.08);
}

.preset-btn.active {
  border-color: #6366f1;
  background: rgba(99, 102, 241, 0.18);
}

.preset-btn small {
  font-size: 0.72rem;
  color: var(--muted, #94a3b8);
}

.promo-modules-box {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.promo-modules-box h4 {
  margin: 0 0 0.35rem;
  font-size: 0.95rem;
}

.module-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.88rem;
  flex-wrap: wrap;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.input-inline {
  padding: 0.3rem 0.5rem;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: #fff;
  font-size: 0.82rem;
}

.reminder-toggle-box {
  padding: 0.75rem;
  background: rgba(16, 185, 129, 0.08);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 10px;
  font-size: 0.86rem;
}

.modal-foot {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.primary-glow {
  background: linear-gradient(135deg, #4f46e5, #6366f1) !important;
  color: #fff !important;
  font-weight: 600;
  border: none;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
}

.spinning {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.04); }
  100% { transform: scale(1); }
}
</style>
