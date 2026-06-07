<template>
  <div :class="['todo-platform', `preset-${designPreset}`]">
    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Nur Team-Mitglieder können die Todo-Plattform nutzen.</p>
    </section>

    <section v-else class="card board">
      <div class="board-head">
        <div>
          <p class="eyebrow">Todo</p>
          <h1>Todo Platform <span class="version-pill">v0.2</span></h1>
        </div>
        <div class="header-actions">
          <button class="btn ghost" type="button" @click="openCategoryModal">Kategorien</button>
          <button class="btn ghost" type="button" @click="openFinishedModal">Erledigte</button>
          <button class="btn" type="button" @click="openCreateModal">Todo anlegen</button>
        </div>
      </div>

      <div class="preset-switch" role="group" aria-label="Design Preset">
        <button
          v-for="preset in presetOptions"
          :key="preset.key"
          class="preset-chip"
          :class="{ active: designPreset === preset.key }"
          type="button"
          @click="setDesignPreset(preset.key)"
        >
          {{ preset.label }}
        </button>
      </div>

      <div class="summary-row">
        <article class="summary-card">
          <span>Offen</span>
          <strong>{{ openTodos.length }}</strong>
        </article>
        <article class="summary-card">
          <span>Erledigt</span>
          <strong>{{ completedTodos.length }}</strong>
        </article>
        <article class="summary-card">
          <span>Kategorien</span>
          <strong>{{ orderedCategorySections.length }}</strong>
        </article>
      </div>

      <div class="view-mode-switch">
        <button
          class="iconbtn tiny"
          type="button"
          :class="{ active: categoryViewMode === 'accordion' }"
          @click="categoryViewMode = 'accordion'"
          title="Kategorien untereinander"
        >
          ☰
        </button>
        <button
          class="iconbtn tiny"
          type="button"
          :class="{ active: categoryViewMode === 'slideshow' }"
          @click="categoryViewMode = 'slideshow'"
          title="Kategorien als Diashow"
        >
          ◉
        </button>
      </div>

      <div v-if="categoryViewMode === 'accordion'" class="accordion-wrap">
        <article class="category-group" v-for="category in orderedCategorySections" :key="`cat-${category.id}`" :style="categoryTone(category.id)">
          <button class="category-header" type="button" @click="toggleCategory(category.id)">
            <span>
              <strong>{{ category.name }}</strong>
              <small>{{ openTodosByCategory(category.id).length }} Todos</small>
            </span>
            <span class="toggle-icon">{{ isCategoryCollapsed(category.id) ? "+" : "-" }}</span>
          </button>

          <div v-if="!isCategoryCollapsed(category.id)" class="category-content">
            <ul v-if="openTodosByCategory(category.id).length" class="todo-list">
              <li
                v-for="todo in openTodosByCategory(category.id)"
                :key="todo.id"
                class="todo-item"
                :class="{ overdue: dueState(todo) === 'overdue', soon: dueState(todo) === 'soon' }"
              >
                <div>
                  <strong>{{ todo.title }}</strong>
                  <p class="muted small">{{ todo.due_date ? `Datum: ${formatDate(todo.due_date)}` : "Ohne Datum" }}</p>
                  <p class="todo-state" :class="dueState(todo)">{{ dueLabel(todo) }}</p>
                </div>

                <div class="todo-actions">
                  <select class="input small-select" :value="todo.category_id" @change="setTodoCategory(todo.id, $event.target.value)">
                    <option v-for="option in categoryOptions" :key="`opt-${option.id}`" :value="option.id">{{ option.name }}</option>
                  </select>
                  <button class="btn ghost tiny" type="button" :disabled="!todo.due_date" @click="addTodoToCalendar(todo)">
                    Zum Kalender
                  </button>
                  <button class="btn tiny" type="button" @click="markDone(todo.id)">Erledigt</button>
                </div>
              </li>
            </ul>
            <p v-else class="muted empty">Keine offenen Todos</p>
          </div>
        </article>
      </div>

      <article v-else-if="activeCategory" class="category-group slideshow-group" :style="categoryTone(activeCategory.id)">
        <div class="slideshow-head">
          <button class="iconbtn tiny" type="button" @click="prevCategory" title="Vorherige Kategorie">◀</button>
          <button class="category-header static" type="button">
            <span>
              <strong>{{ activeCategory.name }}</strong>
              <small>{{ openTodosByCategory(activeCategory.id).length }} Todos</small>
            </span>
          </button>
          <button class="iconbtn tiny" type="button" @click="nextCategory" title="Nächste Kategorie">▶</button>
        </div>
        <div class="slideshow-indicators">
          <button
            v-for="(category, index) in orderedCategorySections"
            :key="`slide-dot-${category.id}`"
            class="slide-dot"
            :class="{ active: index === activeCategoryIndex }"
            type="button"
            @click="setActiveCategory(index)"
            :title="category.name"
          ></button>
        </div>
        <div class="category-content">
          <ul v-if="activeCategoryTodos.length" class="todo-list">
            <li
              v-for="todo in activeCategoryTodos"
              :key="todo.id"
              class="todo-item"
              :class="{ overdue: dueState(todo) === 'overdue', soon: dueState(todo) === 'soon' }"
            >
              <div>
                <strong>{{ todo.title }}</strong>
                <p class="muted small">{{ todo.due_date ? `Datum: ${formatDate(todo.due_date)}` : "Ohne Datum" }}</p>
                <p class="todo-state" :class="dueState(todo)">{{ dueLabel(todo) }}</p>
              </div>

              <div class="todo-actions">
                <select class="input small-select" :value="todo.category_id" @change="setTodoCategory(todo.id, $event.target.value)">
                  <option v-for="option in categoryOptions" :key="`opt-${option.id}`" :value="option.id">{{ option.name }}</option>
                </select>
                <button class="btn ghost tiny" type="button" :disabled="!todo.due_date" @click="addTodoToCalendar(todo)">
                  Zum Kalender
                </button>
                <button class="btn tiny" type="button" @click="markDone(todo.id)">Erledigt</button>
              </div>
            </li>
          </ul>
          <p v-else class="muted empty">Keine offenen Todos</p>
        </div>
      </article>
    </section>

    <div v-if="showCreateModal" class="modal-backdrop" @click.self="closeCreateModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Neues Todo</h3>
          <button class="btn ghost tiny" type="button" @click="closeCreateModal">Schliessen</button>
        </div>

        <form class="form" @submit.prevent="createTodo">
          <label>
            Titel
            <input v-model.trim="draft.title" class="input" required placeholder="z. B. Song-Mix abgeben" />
          </label>
          <label>
            Datum (optional)
            <input v-model="draft.due_date" class="input" type="date" />
          </label>
          <label>
            Kategorie
            <select v-model="draft.category_id" class="input">
              <option v-for="option in categoryOptions" :key="`create-${option.id}`" :value="option.id">{{ option.name }}</option>
            </select>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeCreateModal">Abbrechen</button>
            <button class="btn" type="submit">Anlegen</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showCategoryModal" class="modal-backdrop" @click.self="closeCategoryModal">
      <div class="modal card">
        <div class="modal-head">
          <h3>Kategorien</h3>
          <button class="btn ghost tiny" type="button" @click="closeCategoryModal">Schliessen</button>
        </div>

        <form class="form" @submit.prevent="addCategory">
          <label>
            Neue Kategorie
            <div class="create-row">
              <input class="input" v-model.trim="newCategoryName" placeholder="z. B. Recording" />
              <button class="btn tiny" type="submit">Anlegen</button>
            </div>
          </label>
        </form>

        <div class="category-order-list">
          <article class="category-order-item" v-for="(category, index) in categories" :key="`manage-${category.id}`">
            <strong><span class="category-swatch" :style="categoryTone(category.id)" aria-hidden="true"></span>{{ category.name }}</strong>
            <div class="todo-actions">
              <button class="btn ghost tiny" type="button" @click="moveCategory(category.id, -1)" :disabled="index === 0">Hoch</button>
              <button class="btn ghost tiny" type="button" @click="moveCategory(category.id, 1)" :disabled="index === categories.length - 1">Runter</button>
              <button class="btn ghost danger tiny" type="button" @click="removeCategory(category.id)">Loeschen</button>
            </div>
          </article>
        </div>
      </div>
    </div>

    <div v-if="showFinishedModal" class="modal-backdrop" @click.self="closeFinishedModal">
      <div class="modal card wide">
        <div class="modal-head">
          <h3>Erledigte Todos</h3>
          <button class="btn ghost tiny" type="button" @click="closeFinishedModal">Schliessen</button>
        </div>

        <div v-if="!completedTodos.length" class="muted">Noch keine erledigten Todos.</div>
        <div v-else class="finished-list">
          <article class="finished-item" v-for="todo in completedTodos" :key="`done-${todo.id}`">
            <div>
              <strong>{{ todo.title }}</strong>
              <p class="muted small">{{ todo.completed_at ? `Erledigt: ${formatDateTime(todo.completed_at)}` : "Ohne Zeit" }}</p>
              <p class="muted small">{{ todo.due_date ? `Termin: ${formatDate(todo.due_date)}` : "Ohne Termin" }}</p>
            </div>
            <button class="btn ghost tiny" type="button" @click="reopenTodo(todo.id)">Wieder oeffnen</button>
          </article>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const TODO_STORAGE_KEY = "unyq_todo_platform_items";
const TODO_CATEGORY_KEY = "unyq_todo_platform_categories";
const TODO_COLLAPSED_KEY = "unyq_todo_platform_collapsed";
const TODO_DESIGN_PRESET_KEY = "unyq_todo_platform_design_preset";
const TODO_PROFILE_SETTINGS_KEY = "todo_platform";
const UNCATEGORIZED_ID = "uncategorized";
const CATEGORY_PALETTE = [
  { accent: "#2563eb", soft: "rgba(37, 99, 235, 0.18)", strong: "rgba(37, 99, 235, 0.26)" },
  { accent: "#dc2626", soft: "rgba(220, 38, 38, 0.16)", strong: "rgba(220, 38, 38, 0.24)" },
  { accent: "#059669", soft: "rgba(5, 150, 105, 0.17)", strong: "rgba(5, 150, 105, 0.24)" },
  { accent: "#d97706", soft: "rgba(217, 119, 6, 0.18)", strong: "rgba(217, 119, 6, 0.25)" },
  { accent: "#7c3aed", soft: "rgba(124, 58, 237, 0.18)", strong: "rgba(124, 58, 237, 0.26)" },
  { accent: "#0f766e", soft: "rgba(15, 118, 110, 0.17)", strong: "rgba(15, 118, 110, 0.24)" },
];

const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const todos = ref([]);
const categories = ref([]);
const collapsedCategories = ref({});

const showCreateModal = ref(false);
const showCategoryModal = ref(false);
const showFinishedModal = ref(false);
const newCategoryName = ref("");
const categoryViewMode = ref("accordion");
const activeCategoryIndex = ref(0);
const designPreset = ref("minimal");
const presetOptions = [
  { key: "soft", label: "Soft" },
  { key: "bold", label: "Bold" },
  { key: "minimal", label: "Minimal" },
];

const draft = ref({
  title: "",
  due_date: "",
  category_id: UNCATEGORIZED_ID,
});

function readStorageJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch {
    return fallback;
  }
}

function readProfileTodoState() {
  const payload = me.value?.notification_settings?.[TODO_PROFILE_SETTINGS_KEY];
  if (!payload || typeof payload !== "object") return null;
  return {
    todos: Array.isArray(payload.todos) ? payload.todos : null,
    categories: Array.isArray(payload.categories) ? payload.categories : null,
    collapsedCategories:
      payload.collapsedCategories && typeof payload.collapsedCategories === "object"
        ? payload.collapsedCategories
        : null,
    designPreset: ["soft", "bold", "minimal"].includes(payload.designPreset) ? payload.designPreset : null,
  };
}

function persistTodoStateToProfile() {
  if (!me.value?.id) return;

  const notificationSettings = {
    ...(me.value.notification_settings || {}),
    [TODO_PROFILE_SETTINGS_KEY]: {
      todos: [...todos.value],
      categories: [...categories.value],
      collapsedCategories: { ...collapsedCategories.value },
      designPreset: designPreset.value,
    },
  };

  void api
    .patch(`profiles/${me.value.id}/`, { notification_settings: notificationSettings })
    .then(({ data }) => {
      me.value.notification_settings = data.notification_settings || notificationSettings;
    })
    .catch(() => {
      // Keep local persistence when profile sync is not available.
    });
}

function setDesignPreset(preset) {
  if (!["soft", "bold", "minimal"].includes(preset)) return;
  designPreset.value = preset;
  localStorage.setItem(TODO_DESIGN_PRESET_KEY, preset);
  persistTodoStateToProfile();
}

function persistTodos() {
  localStorage.setItem(TODO_STORAGE_KEY, JSON.stringify(todos.value));
  persistTodoStateToProfile();
}

function persistCategories() {
  localStorage.setItem(TODO_CATEGORY_KEY, JSON.stringify(categories.value));
  persistTodoStateToProfile();
}

function persistCollapsed() {
  localStorage.setItem(TODO_COLLAPSED_KEY, JSON.stringify(collapsedCategories.value));
  persistTodoStateToProfile();
}

const categoryOptions = computed(() => [
  { id: UNCATEGORIZED_ID, name: "Ohne Kategorie" },
  ...categories.value,
]);

const orderedCategorySections = computed(() => categoryOptions.value);

const openTodos = computed(() =>
  todos.value
    .filter((todo) => todo.status !== "DONE")
    .slice()
    .sort((a, b) => new Date(a.created_at || 0) - new Date(b.created_at || 0))
);

const completedTodos = computed(() =>
  todos.value
    .filter((todo) => todo.status === "DONE")
    .slice()
    .sort((a, b) => new Date(b.completed_at || 0) - new Date(a.completed_at || 0))
);

const activeCategory = computed(() => orderedCategorySections.value[activeCategoryIndex.value] || null);
const activeCategoryTodos = computed(() => {
  if (!activeCategory.value) return [];
  return openTodosByCategory(activeCategory.value.id);
});

function openTodosByCategory(categoryId) {
  return openTodos.value.filter((todo) => (todo.category_id || UNCATEGORIZED_ID) === categoryId);
}

function categoryTone(categoryId) {
  if (!categoryId || categoryId === UNCATEGORIZED_ID) {
    return {
      "--cat-accent": "#64748b",
      "--cat-soft": "rgba(100, 116, 139, 0.16)",
      "--cat-strong": "rgba(100, 116, 139, 0.24)",
    };
  }
  const source = String(categoryId);
  let hash = 0;
  for (let i = 0; i < source.length; i += 1) {
    hash = (hash << 5) - hash + source.charCodeAt(i);
    hash |= 0;
  }
  const palette = CATEGORY_PALETTE[Math.abs(hash) % CATEGORY_PALETTE.length];
  return {
    "--cat-accent": palette.accent,
    "--cat-soft": palette.soft,
    "--cat-strong": palette.strong,
  };
}

function setActiveCategory(index) {
  const total = orderedCategorySections.value.length;
  if (!total) {
    activeCategoryIndex.value = 0;
    return;
  }
  const safeIndex = ((Number(index) % total) + total) % total;
  activeCategoryIndex.value = safeIndex;
}

function prevCategory() {
  setActiveCategory(activeCategoryIndex.value - 1);
}

function nextCategory() {
  setActiveCategory(activeCategoryIndex.value + 1);
}

function formatDate(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" }).format(new Date(value));
  } catch {
    return value;
  }
}

function formatDateTime(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
  } catch {
    return value;
  }
}

function dueState(todo) {
  if (!todo?.due_date) return "none";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const due = new Date(todo.due_date);
  due.setHours(0, 0, 0, 0);
  const diff = Math.round((due - today) / (1000 * 60 * 60 * 24));
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "scheduled";
}

function dueLabel(todo) {
  const state = dueState(todo);
  if (state === "overdue") return "Ueberfaellig";
  if (state === "soon") return "Faellig in <= 2 Tagen";
  if (state === "scheduled") return "Geplant";
  return "Ohne Termin";
}

function icsEscape(value) {
  return String(value || "")
    .replace(/\\/g, "\\\\")
    .replace(/\n/g, "\\n")
    .replace(/,/g, "\\,")
    .replace(/;/g, "\\;");
}

function toICSDate(value) {
  if (!value) return null;
  return String(value).slice(0, 10).replaceAll("-", "");
}

function addDaysToISODate(value, days = 0) {
  const match = String(value || "").match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (!match) return null;
  const y = Number(match[1]);
  const m = Number(match[2]);
  const d = Number(match[3]);
  const date = new Date(Date.UTC(y, m - 1, d));
  date.setUTCDate(date.getUTCDate() + days);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString().slice(0, 10);
}

function toICSTimestamp(date = new Date()) {
  return date.toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
}

function openCreateModal() {
  showCreateModal.value = true;
}

function closeCreateModal() {
  showCreateModal.value = false;
}

function openCategoryModal() {
  showCategoryModal.value = true;
}

function closeCategoryModal() {
  showCategoryModal.value = false;
  newCategoryName.value = "";
}

function openFinishedModal() {
  showFinishedModal.value = true;
}

function closeFinishedModal() {
  showFinishedModal.value = false;
}

function isCategoryCollapsed(categoryId) {
  return Boolean(collapsedCategories.value[categoryId]);
}

function toggleCategory(categoryId) {
  collapsedCategories.value = {
    ...collapsedCategories.value,
    [categoryId]: !collapsedCategories.value[categoryId],
  };
  persistCollapsed();
}

function addCategory() {
  const name = newCategoryName.value.trim();
  if (!name) return;
  const exists = categories.value.some((entry) => entry.name.toLowerCase() === name.toLowerCase());
  if (exists) {
    showToast("Kategorie existiert bereits.", "warning");
    return;
  }
  categories.value = [...categories.value, { id: `cat-${Date.now()}`, name }];
  persistCategories();
  newCategoryName.value = "";
}

function moveCategory(categoryId, direction) {
  const index = categories.value.findIndex((entry) => entry.id === categoryId);
  if (index === -1) return;
  const target = index + direction;
  if (target < 0 || target >= categories.value.length) return;
  const next = [...categories.value];
  const [moved] = next.splice(index, 1);
  next.splice(target, 0, moved);
  categories.value = next;
  persistCategories();
}

function removeCategory(categoryId) {
  categories.value = categories.value.filter((entry) => entry.id !== categoryId);
  todos.value = todos.value.map((todo) =>
    (todo.category_id || UNCATEGORIZED_ID) === categoryId
      ? { ...todo, category_id: UNCATEGORIZED_ID, updated_at: new Date().toISOString() }
      : todo
  );
  delete collapsedCategories.value[categoryId];
  persistCategories();
  persistCollapsed();
  persistTodos();
}

function createTodo() {
  const title = draft.value.title.trim();
  if (!title) return;
  const now = new Date().toISOString();
  const item = {
    id: `todo-${Date.now()}`,
    title,
    due_date: draft.value.due_date || null,
    category_id: draft.value.category_id || UNCATEGORIZED_ID,
    status: "OPEN",
    created_at: now,
    updated_at: now,
    completed_at: null,
  };
  todos.value = [item, ...todos.value];
  persistTodos();
  draft.value = { title: "", due_date: "", category_id: UNCATEGORIZED_ID };
  showCreateModal.value = false;
  showToast("Todo wurde erstellt.", "success");
}

function setTodoCategory(todoId, categoryId) {
  todos.value = todos.value.map((todo) =>
    todo.id === todoId
      ? { ...todo, category_id: categoryId || UNCATEGORIZED_ID, updated_at: new Date().toISOString() }
      : todo
  );
  persistTodos();
}

function markDone(todoId) {
  const now = new Date().toISOString();
  todos.value = todos.value.map((todo) =>
    todo.id === todoId
      ? { ...todo, status: "DONE", completed_at: now, updated_at: now }
      : todo
  );
  persistTodos();
}

function reopenTodo(todoId) {
  const now = new Date().toISOString();
  todos.value = todos.value.map((todo) =>
    todo.id === todoId
      ? { ...todo, status: "OPEN", completed_at: null, updated_at: now }
      : todo
  );
  persistTodos();
}

function addTodoToCalendar(todo) {
  if (!todo?.due_date) {
    showToast("Dieses Todo hat kein Datum.", "warning");
    return;
  }
  const start = toICSDate(todo.due_date);
  if (!start) {
    showToast("Ungueltiges Datum.", "error");
    return;
  }
  const end = toICSDate(addDaysToISODate(todo.due_date, 1));
  const stamp = toICSTimestamp();
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//UNYQ//TodoPlatform//DE",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    `UID:${todo.id}-${stamp}@todo.unyq`,
    `DTSTAMP:${stamp}`,
    `DTSTART;VALUE=DATE:${start}`,
    `DTEND;VALUE=DATE:${end}`,
    `SUMMARY:${icsEscape(todo.title)}`,
    "END:VEVENT",
    "END:VCALENDAR",
  ];
  const blob = new Blob([lines.join("\r\n")], { type: "text/calendar;charset=utf-8" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${todo.id}.ics`;
  link.click();
  window.URL.revokeObjectURL(url);
}

onMounted(async () => {
  await fetchProfile();
  const profileState = readProfileTodoState();

  const storedPreset = localStorage.getItem(TODO_DESIGN_PRESET_KEY);
  if (profileState?.designPreset) {
    designPreset.value = profileState.designPreset;
  } else if (["soft", "bold", "minimal"].includes(storedPreset)) {
    designPreset.value = storedPreset;
  } else {
    localStorage.setItem(TODO_DESIGN_PRESET_KEY, designPreset.value);
  }

  todos.value = profileState?.todos || readStorageJSON(TODO_STORAGE_KEY, []);
  categories.value = profileState?.categories || readStorageJSON(TODO_CATEGORY_KEY, []);
  collapsedCategories.value = profileState?.collapsedCategories || readStorageJSON(TODO_COLLAPSED_KEY, {});

  if (profileState) {
    localStorage.setItem(TODO_STORAGE_KEY, JSON.stringify(todos.value));
    localStorage.setItem(TODO_CATEGORY_KEY, JSON.stringify(categories.value));
    localStorage.setItem(TODO_COLLAPSED_KEY, JSON.stringify(collapsedCategories.value));
    localStorage.setItem(TODO_DESIGN_PRESET_KEY, designPreset.value);
  }

  setActiveCategory(0);
});
</script>

<style scoped>
.todo-platform {
  display: grid;
  gap: 16px;
}

.version-pill {
  font-size: 0.76rem;
  padding: 2px 8px;
  border-radius: 999px;
  margin-left: 8px;
  vertical-align: middle;
  border: 1px solid color-mix(in srgb, var(--brand) 50%, var(--border) 50%);
  background: color-mix(in srgb, var(--brand) 18%, transparent 82%);
  color: var(--brand);
}

.preset-switch {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.preset-chip {
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--card) 88%, transparent 12%);
  color: var(--text);
  border-radius: 999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}

.preset-chip.active {
  border-color: color-mix(in srgb, var(--brand) 55%, var(--border) 45%);
  background: color-mix(in srgb, var(--brand) 22%, transparent 78%);
  color: var(--brand);
}

.board-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.eyebrow {
  margin: 0 0 4px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--brand);
}

.board {
  display: grid;
  gap: 12px;
  border-radius: 22px;
  border: 1px solid color-mix(in srgb, var(--brand) 25%, var(--border) 75%);
  background:
    radial-gradient(120% 140% at 0% -10%, color-mix(in srgb, var(--brand) 16%, transparent 84%), transparent 60%),
    linear-gradient(165deg, color-mix(in srgb, var(--card) 88%, var(--bg-soft) 12%), var(--card));
  box-shadow: 0 18px 45px rgba(2, 6, 23, 0.08);
}

.summary-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.summary-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  background: linear-gradient(160deg, color-mix(in srgb, var(--card) 88%, var(--brand) 12%), var(--card));
  display: grid;
  gap: 3px;
}

.summary-card span {
  font-size: 12px;
  color: var(--muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.summary-card strong {
  font-size: 1.1rem;
}

.view-mode-switch {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.view-mode-switch .iconbtn.active {
  border-color: var(--brand);
  color: var(--brand);
}

.slideshow-head {
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 8px;
  align-items: center;
}

.category-header.static {
  cursor: default;
}

.slideshow-indicators {
  display: flex;
  gap: 8px;
  justify-content: center;
}

.slide-dot {
  width: 9px;
  height: 9px;
  border-radius: 999px;
  border: none;
  background: color-mix(in srgb, var(--text) 30%, transparent 70%);
  cursor: pointer;
}

.slide-dot.active {
  background: var(--brand);
}

.category-group {
  border: 1px solid color-mix(in srgb, var(--cat-accent, var(--brand)) 40%, var(--border) 60%);
  border-radius: 16px;
  padding: 12px;
  display: grid;
  gap: 10px;
  background: linear-gradient(160deg, color-mix(in srgb, var(--cat-soft, rgba(37, 99, 235, 0.14)) 60%, var(--card) 40%), var(--card));
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.05);
}

.category-header {
  width: 100%;
  border: 1px solid color-mix(in srgb, var(--cat-accent, var(--brand)) 35%, var(--border) 65%);
  border-radius: 10px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--cat-strong, rgba(37, 99, 235, 0.2)) 35%, transparent 65%), var(--card));
  padding: 10px 12px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  cursor: pointer;
}

.category-header span {
  display: grid;
  text-align: left;
}

.category-header small {
  color: var(--muted);
}

.toggle-icon {
  font-size: 20px;
  line-height: 1;
  color: var(--cat-accent, var(--brand));
}

.todo-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.todo-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid color-mix(in srgb, var(--cat-accent, var(--brand)) 28%, var(--border) 72%);
  border-radius: 12px;
  padding: 12px;
  background: linear-gradient(145deg, color-mix(in srgb, var(--cat-soft, rgba(37, 99, 235, 0.13)) 30%, var(--card) 70%), var(--card));
}

.todo-item strong {
  display: block;
  font-size: 0.98rem;
  font-weight: 700;
  line-height: 1.35;
  letter-spacing: 0.01em;
}

.todo-item.overdue {
  border-color: color-mix(in srgb, #ef4444 65%, var(--border) 35%);
}

.todo-item.soon {
  border-color: color-mix(in srgb, #f59e0b 65%, var(--border) 35%);
}

.todo-state {
  margin: 8px 0 0;
  width: fit-content;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--border) 80%, transparent 20%);
  padding: 3px 9px;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
  background: color-mix(in srgb, var(--card) 88%, transparent 12%);
}

.todo-state.overdue {
  color: #b91c1c;
  border-color: color-mix(in srgb, #ef4444 58%, var(--border) 42%);
  background: color-mix(in srgb, #ef4444 16%, transparent 84%);
}

.todo-state.soon {
  color: #b45309;
  border-color: color-mix(in srgb, #f59e0b 58%, var(--border) 42%);
  background: color-mix(in srgb, #f59e0b 16%, transparent 84%);
}

.todo-state.scheduled {
  color: #0f766e;
  border-color: color-mix(in srgb, #14b8a6 58%, var(--border) 42%);
  background: color-mix(in srgb, #14b8a6 14%, transparent 86%);
}

.todo-state.none {
  border-color: color-mix(in srgb, var(--text) 22%, var(--border) 78%);
  background: color-mix(in srgb, var(--text) 8%, transparent 92%);
}

.todo-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  justify-content: flex-end;
}

.small-select {
  min-width: 160px;
}

.small {
  margin: 4px 0 0;
  font-size: 12px;
  line-height: 1.35;
}

.empty {
  margin: 0;
}

.modal-backdrop {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  z-index: 999;
}

.modal {
  max-width: 560px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal.wide {
  max-width: 900px;
}

.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.form {
  display: grid;
  gap: 12px;
}

.create-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.category-order-list {
  margin-top: 10px;
  display: grid;
  gap: 8px;
}

.category-order-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.category-order-item strong {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.category-swatch {
  width: 12px;
  height: 12px;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--cat-accent, var(--brand)) 60%, transparent 40%);
  background: var(--cat-accent, var(--brand));
  display: inline-block;
}

.finished-list {
  display: grid;
  gap: 10px;
}

.finished-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.todo-platform.preset-bold .board {
  border-color: color-mix(in srgb, var(--brand) 42%, var(--border) 58%);
  background:
    radial-gradient(130% 150% at 0% -20%, color-mix(in srgb, var(--brand) 24%, transparent 76%), transparent 62%),
    linear-gradient(165deg, color-mix(in srgb, var(--card) 78%, var(--bg-soft) 22%), var(--card));
  box-shadow: 0 22px 52px rgba(2, 6, 23, 0.12);
}

.todo-platform.preset-bold .category-group {
  border-width: 2px;
  border-radius: 18px;
  background: linear-gradient(150deg, color-mix(in srgb, var(--cat-soft) 75%, var(--card) 25%), var(--card));
}

.todo-platform.preset-bold .todo-item {
  border-width: 2px;
}

.todo-platform.preset-bold .todo-item strong {
  font-size: 1.02rem;
}

.todo-platform.preset-bold .category-header {
  border-width: 2px;
  background: linear-gradient(135deg, color-mix(in srgb, var(--cat-strong) 48%, transparent 52%), var(--card));
}

.todo-platform.preset-bold .summary-card {
  border-color: color-mix(in srgb, var(--brand) 34%, var(--border) 66%);
  background: linear-gradient(155deg, color-mix(in srgb, var(--brand) 22%, var(--card) 78%), var(--card));
}

.todo-platform.preset-bold .preset-chip.active {
  background: color-mix(in srgb, var(--brand) 30%, transparent 70%);
}

.todo-platform.preset-minimal .board {
  border-radius: 14px;
  border-color: var(--border);
  background: var(--card);
  box-shadow: none;
}

.todo-platform.preset-minimal .board-head {
  border-bottom: 1px solid color-mix(in srgb, var(--border) 85%, transparent 15%);
  padding-bottom: 10px;
}

.todo-platform.preset-minimal .summary-card,
.todo-platform.preset-minimal .category-group,
.todo-platform.preset-minimal .todo-item,
.todo-platform.preset-minimal .category-header,
.todo-platform.preset-minimal .finished-item,
.todo-platform.preset-minimal .category-order-item {
  background: var(--card);
  box-shadow: none;
}

.todo-platform.preset-minimal .category-group,
.todo-platform.preset-minimal .category-header,
.todo-platform.preset-minimal .todo-item {
  border-color: color-mix(in srgb, var(--cat-accent) 22%, var(--border) 78%);
}

.todo-platform.preset-minimal .summary-card {
  border-radius: 10px;
}

.todo-platform.preset-minimal .todo-state {
  border-radius: 8px;
}

.todo-platform.preset-minimal .preset-chip {
  border-radius: 8px;
}

.todo-platform.preset-minimal .preset-chip.active {
  background: color-mix(in srgb, var(--brand) 14%, transparent 86%);
}

:global(.dark) .board {
  box-shadow: 0 22px 50px rgba(0, 0, 0, 0.35);
}

:global(.dark) .summary-card,
:global(.dark) .category-group,
:global(.dark) .todo-item,
:global(.dark) .category-header,
:global(.dark) .finished-item,
:global(.dark) .category-order-item {
  box-shadow: none;
}

:global(.dark) .todo-state {
  background: color-mix(in srgb, var(--card) 76%, #000 24%);
  border-color: color-mix(in srgb, var(--border) 65%, #000 35%);
}

:global(.dark) .todo-platform.preset-bold .board {
  box-shadow: 0 26px 56px rgba(0, 0, 0, 0.42);
}

:global(.dark) .todo-platform.preset-minimal .board {
  background: color-mix(in srgb, var(--card) 92%, #000 8%);
}

@media (max-width: 980px) {
  .summary-row {
    grid-template-columns: 1fr;
  }

  .todo-item,
  .finished-item,
  .category-order-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .todo-actions {
    justify-content: flex-start;
  }
}
</style>
