<template>
  <div class="content-studio wide">
    <header class="card studio-header">
      <div>
        <h1>Content Studio</h1>
        <p class="muted">Zentrale Plattform fuer Tipps, News und Plugin Tutorials.</p>
      </div>
      <button class="btn ghost" type="button" @click="loadItems" :disabled="loading">
        {{ loading ? "Lade..." : "Aktualisieren" }}
      </button>
    </header>

    <section class="card type-switcher">
      <p class="muted small">Content-Typ</p>
      <div class="chip-row">
        <button
          v-for="option in contentOptions"
          :key="option.value"
          type="button"
          class="chip"
          :class="{ active: selectedType === option.value }"
          @click="selectedType = option.value"
        >
          {{ option.label }}
        </button>
      </div>
    </section>

    <section v-if="isTeam" class="card editor">
      <h2>Neuen Beitrag erstellen</h2>
      <form class="stack-form" @submit.prevent="createItem">
        <label>
          Titel
          <input v-model.trim="form.title" class="input" placeholder="Kurzer, klarer Titel" required />
        </label>
        <label>
          Inhalt
          <textarea
            v-model.trim="form.body"
            class="input textarea"
            rows="6"
            placeholder="Hier den Beitragstext eintragen..."
            required
          ></textarea>
        </label>
        <label v-if="selectedType === 'TIP'">
          Tipp-Kategorie
          <select v-model="form.tip_type" class="input">
            <option v-for="option in tipTypeOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>
        <label class="toggle">
          <input v-model="form.is_published" type="checkbox" />
          Sofort veroeffentlichen
        </label>
        <button class="btn" type="submit" :disabled="saving">
          {{ saving ? "Speichere..." : "Beitrag speichern" }}
        </button>
      </form>
    </section>
    <section v-else class="card access-note">
      <h2>Nur fuer Admins</h2>
      <p class="muted">Erstellen, Aendern und Loeschen ist nur fuer TEAM/Admin freigeschaltet.</p>
    </section>

    <section class="card list-section">
      <div class="section-head">
        <h2>{{ selectedTypeLabel }}</h2>
        <span class="badge">{{ items.length }} Eintraege</span>
      </div>
      <div v-if="loading" class="skeleton-list">
        <div class="skeleton-card" v-for="n in 3" :key="`sk-${n}`"></div>
      </div>
      <ul v-else class="item-list">
        <li v-for="item in items" :key="item.id" class="item-card">
          <div class="item-head">
            <h3>{{ item.title }}</h3>
            <div class="badge-row">
              <span v-if="selectedType === 'TIP'" class="badge badge-soft">
                {{ tipTypeLabel(item.tip_type) }}
              </span>
              <span class="badge" :class="{ draft: !item.is_published }">
                {{ item.is_published ? "Live" : "Entwurf" }}
              </span>
            </div>
          </div>
          <p class="muted small">
            {{ formatDate(item.created_at) }} von {{ item.author?.name || item.author?.username || "System" }}
          </p>
          <p class="item-body">{{ item.body }}</p>
          <div v-if="isTeam" class="actions">
            <button class="btn ghost tiny" type="button" @click="togglePublish(item)" :disabled="savingIds.has(item.id)">
              {{ item.is_published ? "Auf Entwurf setzen" : "Veroeffentlichen" }}
            </button>
            <button class="btn ghost danger tiny" type="button" @click="removeItem(item)" :disabled="savingIds.has(item.id)">
              Loeschen
            </button>
          </div>
        </li>
      </ul>
      <p v-if="!loading && !items.length" class="muted empty">Noch keine Eintraege fuer diesen Typ.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const contentOptions = [
  { value: "TIP", label: "Tipps & Einnahmequellen" },
  { value: "NEWS", label: "News" },
  { value: "TUTORIAL", label: "Plugin Tutorials" },
];

const tipTypeOptions = [
  { value: "CASHBACK", label: "Cashback" },
  { value: "DISCOUNT", label: "Rabattaktion" },
  { value: "REFERRAL", label: "Empfehlungspraemie" },
  { value: "OTHER", label: "Sonstiges" },
];

const typeConfig = {
  TIP: { endpoint: "finance-tips/", title: "Tipps und Einnahmequellen" },
  NEWS: { endpoint: "news/", title: "News" },
  TUTORIAL: { endpoint: "plugin-guides/", title: "Plugin Tutorials" },
};

const selectedType = ref("TIP");
const items = ref([]);
const loading = ref(false);
const saving = ref(false);
const savingIds = ref(new Set());
const form = ref(buildForm());

const selectedTypeLabel = computed(() => typeConfig[selectedType.value]?.title || "Eintraege");

function buildForm() {
  return {
    title: "",
    body: "",
    tip_type: "CASHBACK",
    is_published: true,
  };
}

function endpointFor(type = selectedType.value) {
  return typeConfig[type]?.endpoint || typeConfig.TIP.endpoint;
}

function normalizeList(data) {
  if (Array.isArray(data)) return data;
  if (Array.isArray(data?.results)) return data.results;
  return [];
}

function tipTypeLabel(value) {
  const match = tipTypeOptions.find((option) => option.value === value);
  return match?.label || "Sonstiges";
}

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", { dateStyle: "medium", timeStyle: "short" }).format(new Date(value));
}

async function loadItems() {
  loading.value = true;
  try {
    const { data } = await api.get(endpointFor());
    items.value = normalizeList(data);
  } catch (err) {
    items.value = [];
    console.error("Content konnte nicht geladen werden", err);
    showToast("Content konnte nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function createItem() {
  if (!isTeam.value) return;
  if (!form.value.title.trim() || !form.value.body.trim()) return;
  saving.value = true;
  try {
    const endpoint = endpointFor();
    if (selectedType.value === "TIP") {
      await api.post(endpoint, {
        title: form.value.title,
        body: form.value.body,
        tip_type: form.value.tip_type,
        is_published: form.value.is_published,
      });
    } else if (selectedType.value === "TUTORIAL") {
      const payload = new FormData();
      payload.append("title", form.value.title);
      payload.append("body", form.value.body);
      payload.append("is_published", form.value.is_published ? "true" : "false");
      await api.post(endpoint, payload, { headers: { "Content-Type": "multipart/form-data" } });
    } else {
      await api.post(endpoint, {
        title: form.value.title,
        body: form.value.body,
        is_published: form.value.is_published,
      });
    }
    form.value = buildForm();
    await loadItems();
  } catch (err) {
    console.error("Beitrag konnte nicht gespeichert werden", err);
    showToast("Beitrag konnte nicht gespeichert werden", "error");
  } finally {
    saving.value = false;
  }
}

async function togglePublish(item) {
  if (!isTeam.value) return;
  savingIds.value.add(item.id);
  try {
    await api.post(`${endpointFor()}${item.id}/publish/`, { publish: !item.is_published });
    await loadItems();
  } catch (err) {
    console.error("Statuswechsel fehlgeschlagen", err);
    showToast("Statuswechsel fehlgeschlagen", "error");
  } finally {
    savingIds.value.delete(item.id);
  }
}

async function removeItem(item) {
  if (!isTeam.value) return;
  if (!confirm(`Eintrag "${item.title}" wirklich loeschen?`)) return;
  savingIds.value.add(item.id);
  try {
    await api.delete(`${endpointFor()}${item.id}/`);
    await loadItems();
  } catch (err) {
    console.error("Eintrag konnte nicht geloescht werden", err);
    showToast("Eintrag konnte nicht geloescht werden", "error");
  } finally {
    savingIds.value.delete(item.id);
  }
}

watch(
  () => selectedType.value,
  async () => {
    form.value = buildForm();
    await loadItems();
  }
);

onMounted(async () => {
  await fetchProfile();
  await loadItems();
});
</script>

<style scoped>
.content-studio {
  display: grid;
  gap: 18px;
}

.studio-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.type-switcher {
  display: grid;
  gap: 10px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.editor,
.list-section,
.access-note {
  display: grid;
  gap: 14px;
}

.stack-form {
  display: grid;
  gap: 12px;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.item-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

.item-card {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  background: var(--surface);
  display: grid;
  gap: 8px;
}

.item-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.item-head h3 {
  margin: 0;
}

.badge-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.item-body {
  white-space: pre-line;
}

.actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.empty {
  margin: 0;
}

@media (max-width: 760px) {
  .item-head {
    flex-direction: column;
  }
}
</style>
