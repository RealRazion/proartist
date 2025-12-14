<template>
  <div class="news wide">
    <header class="card header">
      <div>
        <h1>News & Updates</h1>
        <p class="muted">Bleib auf dem Laufenden, was das Team teilt.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadNews" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section v-if="isTeam" class="card editor">
      <h2>Neuen Post erstellen</h2>
      <form class="form" @submit.prevent="createPost">
        <label>
          Titel
          <input class="input" v-model.trim="form.title" placeholder="Kurzer Titel" />
        </label>
        <label>
          Inhalt
          <textarea class="input textarea" v-model.trim="form.body" placeholder="Infos fuer alle Nutzer"></textarea>
        </label>
        <label class="toggle">
          <input type="checkbox" v-model="form.is_published" />
          Sofort veroeffentlichen
        </label>
        <button class="btn" type="submit" :disabled="saving">
          {{ saving ? "Speichere..." : "Post speichern" }}
        </button>
      </form>
    </section>

    <section class="card posts">
      <h2>Aktuelle Meldungen</h2>
      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-card" v-for="n in 3" :key="`sk-${n}`"></div>
      </div>
      <ul v-else>
        <li v-for="post in posts" :key="post.id">
          <div class="post-head">
            <h3>{{ post.title }}</h3>
            <span class="badge" :class="{ draft: !post.is_published }">
              {{ post.is_published ? "Live" : "Entwurf" }}
            </span>
          </div>
          <p class="muted">{{ formatDate(post.created_at) }} von {{ post.author?.name || post.author?.username }}</p>
          <p>{{ post.body }}</p>
          <div v-if="isTeam" class="actions">
            <button class="btn ghost tiny" type="button" @click="togglePublish(post)" :disabled="savingIds.has(post.id)">
              {{ post.is_published ? "Auf Entwurf setzen" : "Veroeffentlichen" }}
            </button>
            <button class="btn ghost danger tiny" type="button" @click="removePost(post)" :disabled="savingIds.has(post.id)">
              Loeschen
            </button>
          </div>
        </li>
      </ul>
      <p v-if="!loading && !posts.length" class="muted empty">Noch keine News vorhanden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam, fetchProfile } = useCurrentProfile();
const posts = ref([]);
const loading = ref(false);
const saving = ref(false);
const savingIds = ref(new Set());
const form = ref({
  title: "",
  body: "",
  is_published: true,
});

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

async function loadNews() {
  loading.value = true;
  try {
    const { data } = await api.get("news/");
    posts.value = data;
  } catch (err) {
    console.error("News konnten nicht geladen werden", err);
    posts.value = [];
  } finally {
    loading.value = false;
  }
}

async function createPost() {
  if (!form.value.title || !form.value.body) return;
  saving.value = true;
  try {
    await api.post("news/", form.value);
    form.value = { title: "", body: "", is_published: true };
    await loadNews();
  } catch (err) {
    console.error("Post konnte nicht gespeichert werden", err);
  } finally {
    saving.value = false;
  }
}

async function togglePublish(post) {
  savingIds.value.add(post.id);
  try {
    await api.post(`news/${post.id}/publish/`, { publish: !post.is_published });
    await loadNews();
  } catch (err) {
    console.error("Statuswechsel fehlgeschlagen", err);
  } finally {
    savingIds.value.delete(post.id);
  }
}

async function removePost(post) {
  if (!confirm(`Post "${post.title}" wirklich loeschen?`)) return;
  savingIds.value.add(post.id);
  try {
    await api.delete(`news/${post.id}/`);
    await loadNews();
  } catch (err) {
    console.error("Post konnte nicht geloescht werden", err);
  } finally {
    savingIds.value.delete(post.id);
  }
}

onMounted(async () => {
  await fetchProfile();
  await loadNews();
});
</script>

<style scoped>
.news {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.editor .form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}
.posts ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
}
.posts li {
  border: 1px solid rgba(148, 163, 184, 0.3);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.post-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.badge {
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(34, 197, 94, 0.15);
  color: #15803d;
}
.badge.draft {
  background: rgba(248, 113, 113, 0.2);
  color: #b91c1c;
}
.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.btn.tiny {
  padding: 4px 10px;
  font-size: 12px;
}
.skeleton-list {
  display: grid;
  gap: 10px;
}
.skeleton-card {
  height: 120px;
  border-radius: 12px;
  background: linear-gradient(90deg, rgba(148, 163, 184, 0.2), rgba(148, 163, 184, 0.08), rgba(148, 163, 184, 0.2));
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
.empty {
  text-align: center;
  margin: 0;
}
@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}
</style>

