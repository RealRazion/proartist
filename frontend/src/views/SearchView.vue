<template>
  <div class="search-view">
    <header class="card hero">
      <div>
        <h1>Erweiterte Suche</h1>
        <p class="muted">Suche nach Tasks, Projekten, Dateien und mehr</p>
      </div>
    </header>

    <div class="search-controls card">
      <form @submit.prevent="performSearch">
        <input v-model="query" type="text" placeholder="Suchbegriff eingeben..." class="input" />
        <select v-model="searchType" class="input">
          <option value="all">Alles</option>
          <option value="tasks">Tasks</option>
          <option value="projects">Projekte</option>
          <option value="files">Dateien</option>
          <option value="users">Benutzer</option>
        </select>
        <select v-model="dateFilter" class="input">
          <option value="">Alle Zeiten</option>
          <option value="today">Heute</option>
          <option value="week">Diese Woche</option>
          <option value="month">Dieser Monat</option>
          <option value="year">Dieses Jahr</option>
        </select>
        <button type="submit" class="btn" :disabled="loading">Suchen</button>
      </form>
    </div>

    <section v-if="results.length" class="results">
      <article v-for="result in results" :key="result.id" class="card result-item" :data-type="result.type">
        <div>
          <strong>{{ result.title }}</strong>
          <p class="muted">{{ result.description }}</p>
        </div>
        <div class="result-meta">
          <span class="badge">{{ result.typeLabel }}</span>
          <span class="badge">{{ formatDate(result.created_at) }}</span>
          <button class="btn ghost tiny" @click="openResult(result)">Öffnen</button>
        </div>
      </article>
    </section>

    <p v-else-if="searched" class="muted">Keine Ergebnisse gefunden.</p>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();

const query = ref("");
const searchType = ref("all");
const dateFilter = ref("");
const loading = ref(false);
const results = ref([]);
const searched = ref(false);

async function performSearch() {
  if (!query.value.trim()) return;
  loading.value = true;
  try {
    const params = {
      q: query.value,
      type: searchType.value,
      date: dateFilter.value
    };
    const response = await api.get("search/", { params });
    results.value = response.data.results || [];
    searched.value = true;
  } catch (error) {
    console.error("Search failed:", error);
    results.value = [];
  } finally {
    loading.value = false;
  }
}

function openResult(result) {
  if (result.type === "task") {
    router.push({ name: "tasks", query: { taskId: result.id } });
  } else if (result.type === "project") {
    router.push({ name: "project-detail", params: { projectId: result.id } });
  } // Add more types as needed
}

function formatDate(date) {
  return new Date(date).toLocaleDateString("de-DE");
}
</script>

<style scoped>
.search-controls {
  margin-bottom: 2rem;
}

.search-controls form {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.results {
  display: grid;
  gap: 1rem;
}

.result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.result-meta {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
</style>