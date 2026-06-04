<template>
  <div class="todo-platform">
    <header class="card header">
      <div>
        <p class="eyebrow">Todo</p>
        <h1>Todo Platform</h1>
        <p class="muted">Erstelle Todos mit optionalem Datum und füge sie per Button zum Kalender hinzu.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadTodos" :disabled="loadingTodos">
        {{ loadingTodos ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur für Team</h2>
      <p class="muted">Die Todo Plattform nutzt die Team-Task-Funktionen.</p>
    </section>

    <section v-else class="grid">
      <article class="card create">
        <h2>Neues Todo</h2>
        <form class="form" @submit.prevent="createTodo">
          <label>
            Titel
            <input v-model.trim="draft.title" class="input" required placeholder="z. B. Song-Mix abgeben" />
          </label>
          <label>
            Datum (optional)
            <input v-model="draft.due_date" class="input" type="date" />
          </label>
          <button class="btn" type="submit" :disabled="savingTodo">
            {{ savingTodo ? "Speichere..." : "Todo hinzufügen" }}
          </button>
        </form>
      </article>

      <article class="card list">
        <h2>Todos</h2>
        <p v-if="loadingTodos" class="muted">Lade Todos...</p>
        <p v-else-if="!todos.length" class="muted">Noch keine Todos vorhanden.</p>
        <ul v-else>
          <li v-for="todo in todos" :key="todo.id" class="todo-item">
            <div>
              <strong>{{ todo.title }}</strong>
              <p class="muted small">{{ todo.due_date ? `Datum: ${formatDate(todo.due_date)}` : "Ohne Datum" }}</p>
            </div>
            <button
              class="btn ghost tiny"
              type="button"
              :disabled="!todo.due_date"
              @click="addTodoToCalendar(todo)"
            >
              Zum Kalender hinzufügen
            </button>
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

const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const todos = ref([]);
const loadingTodos = ref(false);
const savingTodo = ref(false);
const draft = ref({
  title: "",
  due_date: "",
});

function toList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
}

function formatDate(value) {
  if (!value) return "-";
  try {
    return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium" }).format(new Date(value));
  } catch {
    return value;
  }
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

async function loadTodos() {
  if (!isTeam.value) return;
  loadingTodos.value = true;
  try {
    const { data } = await api.get("tasks/", {
      params: {
        include_archived: 0,
        include_done: 1,
        ordering: "-created_at",
        page_size: 100,
      },
    });
    todos.value = toList(data);
  } catch (err) {
    todos.value = [];
    showToast("Todos konnten nicht geladen werden.", "error");
  } finally {
    loadingTodos.value = false;
  }
}

async function createTodo() {
  const title = draft.value.title.trim();
  if (!title) return;
  savingTodo.value = true;
  try {
    await api.post("tasks/", {
      title,
      status: "OPEN",
      priority: "MEDIUM",
      task_type: "EXTERNAL",
      due_date: draft.value.due_date || null,
    });
    draft.value = { title: "", due_date: "" };
    await loadTodos();
    showToast("Todo wurde erstellt.", "success");
  } catch (err) {
    showToast("Todo konnte nicht erstellt werden.", "error");
  } finally {
    savingTodo.value = false;
  }
}

function addTodoToCalendar(todo) {
  if (!todo?.due_date) {
    showToast("Dieses Todo hat kein Datum.", "warning");
    return;
  }
  const start = toICSDate(todo.due_date);
  if (!start) {
    showToast("Ungültiges Datum.", "error");
    return;
  }
  const endDate = new Date(todo.due_date);
  endDate.setDate(endDate.getDate() + 1);
  const end = toICSDate(endDate.toISOString().slice(0, 10));
  const stamp = new Date().toISOString().replace(/[-:]/g, "").replace(/\.\d+Z$/, "Z");
  const lines = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//UNYQ//Todo Platform//DE",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "BEGIN:VEVENT",
    `UID:todo-${todo.id}@unyq.local`,
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
  link.download = `todo-${todo.id}.ics`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}

onMounted(async () => {
  await fetchProfile();
  await loadTodos();
});
</script>

<style scoped>
.todo-platform {
  display: grid;
  gap: 16px;
}

.header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.eyebrow {
  margin: 0 0 4px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--brand);
}

.grid {
  display: grid;
  gap: 16px;
  grid-template-columns: 320px 1fr;
}

.form {
  display: grid;
  gap: 10px;
}

.todo-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px 12px;
}

.list ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 10px;
}

.small {
  margin: 4px 0 0;
  font-size: 12px;
}

@media (max-width: 980px) {
  .grid {
    grid-template-columns: 1fr;
  }

  .todo-item {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
