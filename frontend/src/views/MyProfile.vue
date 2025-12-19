<template>
  <div class="profile-page">
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />

    <header class="card hero">
      <div>
        <p class="eyebrow">Mein Profil</p>
        <h1>{{ form.name || me?.name || me?.username || "Profil" }}</h1>
        <p class="muted">
          Sorge dafür, dass dein Team und Partner sofort wissen, wie sie dich erreichen und wofür man dich buchen kann.
        </p>
        <div class="hero-meta">
          <div>
            <span class="label">E-Mail</span>
            <strong>{{ me?.email || "–" }}</strong>
          </div>
          <div>
            <span class="label">Benutzername</span>
            <strong>{{ me?.username || "–" }}</strong>
          </div>
          <div>
            <span class="label">Rollen</span>
            <strong>{{ roleSummary }}</strong>
          </div>
        </div>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="hydrateForm" :disabled="saving">Zurücksetzen</button>
        <button class="btn" type="button" @click="saveProfile" :disabled="saving">
          {{ saving ? "Speichere..." : "Profil speichern" }}
        </button>
      </div>
    </header>

    <form class="card profile-form" @submit.prevent="saveProfile">
      <div class="form-section">
        <div class="section-head">
          <h2>Basisdaten</h2>
          <p class="muted small">Kurze Angaben helfen beim Matching mit Projekten.</p>
        </div>
        <div class="field-grid two">
          <label>
            <span>Name / Künstlername</span>
            <input class="input" v-model.trim="form.name" placeholder="z. B. LUNA" />
          </label>
          <label>
            <span>Stadt</span>
            <input class="input" v-model.trim="form.city" placeholder="z. B. Berlin" />
          </label>
          <label>
            <span>Genre</span>
            <input class="input" v-model.trim="form.genre" placeholder="z. B. Hip-Hop, R&B" />
          </label>
          <label>
            <span>IBAN (optional)</span>
            <input class="input" v-model.trim="form.iban" placeholder="DE00 0000 0000 0000 0000 00" />
          </label>
        </div>
      </div>

      <div class="form-section">
        <div class="section-head">
          <h2>Rollen</h2>
          <p class="muted small">Wähle mehrere Rollen aus – Team-Rollen werden nur von Admins vergeben.</p>
        </div>
        <div class="role-grid">
          <button
            type="button"
            v-for="role in visibleRoles"
            :key="role.id"
            class="role-chip"
            :class="{ active: form.role_ids.includes(role.id) }"
            @click="toggleRole(role.id)"
          >
            {{ roleLabels[role.key] || role.key }}
          </button>
        </div>
      </div>

      <div class="form-section">
        <div class="section-head">
          <h2>Social Links</h2>
          <p class="muted small">Nur ausgefüllte Links werden angezeigt.</p>
        </div>
        <div class="field-grid two">
          <label v-for="key in socialKeys" :key="key">
            <span>{{ socialMeta[key].label }}</span>
            <input
              class="input"
              v-model.trim="form.socials[key]"
              :placeholder="socialMeta[key].placeholder"
            />
          </label>
      </div>
    </div>

      <div class="form-section">
        <div class="section-head">
          <h2>Benachrichtigungen</h2>
          <p class="muted small">Steuere, wann du E-Mail-Updates erhältst.</p>
        </div>
        <div class="notification-grid">
          <label v-for="option in notificationOptions" :key="option.key" class="notification-toggle">
            <div>
              <strong>{{ option.label }}</strong>
              <p class="muted small">{{ option.hint }}</p>
            </div>
            <input type="checkbox" v-model="form.notifications[option.key]" />
          </label>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn ghost" type="button" @click="hydrateForm" :disabled="saving">Abbrechen</button>
        <button class="btn" type="submit" :disabled="saving">
          {{ saving ? "Speichere..." : "Speichern" }}
        </button>
      </div>
    </form>

    <section class="card examples-card">
      <div class="section-head">
        <div>
          <h2>Referenzen & Beispiele</h2>
          <p class="muted small">Zeig dein Portfolio mit Links oder Dateien.</p>
        </div>
        <span class="count-pill">{{ examples.length }} Einträge</span>
      </div>
      <form class="example-form" @submit.prevent="uploadExample">
        <input class="input" v-model.trim="example.title" placeholder="Titel (optional)" />
        <input class="input" v-model.trim="example.link" placeholder="Link (YouTube, SoundCloud ...)" />
        <label class="file-picker">
          <input type="file" @change="onExampleFile" />
          {{ example.file ? example.file.name : "Datei wählen" }}
        </label>
        <div class="example-actions">
          <button class="btn ghost" type="button" @click="resetExample" :disabled="uploading">Zurücksetzen</button>
          <button class="btn" type="submit" :disabled="uploading">
            {{ uploading ? "Lädt..." : "Beispiel hinzufügen" }}
          </button>
        </div>
      </form>
      <ul class="example-list" v-if="examples.length">
        <li v-for="item in examples" :key="item.id">
          <div>
            <strong>{{ item.title || "Ohne Titel" }}</strong>
            <p class="muted">
              <span v-if="item.link">{{ item.link }}</span>
              <span v-else-if="item.file">Datei hochgeladen</span>
              <span v-else>Keine zusätzlichen Infos</span>
            </p>
          </div>
          <div class="example-links">
            <a v-if="item.link" class="btn ghost tiny" :href="item.link" target="_blank" rel="noopener">Ansehen</a>
            <a
              v-else-if="item.file"
              class="btn ghost tiny"
              :href="item.file"
              target="_blank"
              rel="noopener"
            >
              Download
            </a>
          </div>
        </li>
      </ul>
      <p v-else-if="!loadingExamples" class="muted empty">Noch keine Beispiele hinterlegt.</p>
      <p v-if="loadingExamples" class="muted">Lade Beispiele...</p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed, watch } from "vue";
import api from "../api";
import Toast from "../components/Toast.vue";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { toast, showToast, hideToast } = useToast();
const { profile: me, fetchProfile, isTeam } = useCurrentProfile();

const roles = ref([]);
const examples = ref([]);
const loadingExamples = ref(false);
const saving = ref(false);
const uploading = ref(false);

const socialKeys = ["instagram", "youtube", "soundcloud", "tiktok", "spotify"];
const socialMeta = {
  instagram: { label: "Instagram", placeholder: "@deinhandle" },
  youtube: { label: "YouTube", placeholder: "https://youtube.com/..." },
  soundcloud: { label: "SoundCloud", placeholder: "https://soundcloud.com/..." },
  tiktok: { label: "TikTok", placeholder: "@deinhandle" },
  spotify: { label: "Spotify", placeholder: "https://open.spotify.com/..." },
};
const notificationOptions = [
  {
    key: "task_assigned",
    label: "Neue Task-Zuweisungen",
    hint: "E-Mail, wenn du als Verantwortliche:r eingetragen wirst.",
  },
  {
    key: "task_mentioned",
    label: "@-Mentions in Kommentaren",
    hint: "Hinweis, sobald dich jemand in einem Kommentar markiert.",
  },
  {
    key: "project_updates",
    label: "Projekt-Updates",
    hint: "Status- oder Team-?nderungen bei Projekten, an denen du beteiligt bist.",
  },
  {
    key: "digest",
    label: "Täglicher Digest",
    hint: "Eine tägliche Zusammenfassung zu Tasks und Projekten.",
  },
];

const roleLabels = {
  ARTIST: "Artist",
  PROD: "Producer",
  VIDEO: "Videograf",
  MERCH: "Merchandiser",
  MKT: "Marketing / Management",
  LOC: "Location",
  TEAM: "Team",
};

const form = reactive({
  name: "",
  city: "",
  genre: "",
  iban: "",
  socials: createDefaultSocials(),
  role_ids: [],
  notifications: createDefaultNotifications(),
});

const example = reactive({
  title: "",
  link: "",
  file: null,
});

const visibleRoles = computed(() =>
  roles.value.filter((role) => isTeam.value || role.key !== "TEAM")
);

const roleSummary = computed(() => {
  if (!form.role_ids.length) return "Keine";
  const selected = roles.value
    .filter((role) => form.role_ids.includes(role.id))
    .map((role) => roleLabels[role.key] || role.key);
  if (!selected.length) return "Keine";
  return selected.join(", ");
});

function createDefaultSocials() {
  return socialKeys.reduce((acc, key) => {
    acc[key] = "";
    return acc;
  }, {});
}

function createDefaultNotifications() {
  return {
    task_assigned: true,
    task_mentioned: true,
    project_updates: true,
    digest: false,
  };
}

function hydrateForm() {
  if (!me.value) return;
  form.name = me.value.name || "";
  form.city = me.value.city || "";
  form.genre = me.value.genre || "";
  form.iban = me.value.iban || "";
  form.socials = { ...createDefaultSocials(), ...(me.value.socials || {}) };
  form.role_ids = (me.value.roles || []).map((role) => role.id);
  form.notifications = {
    ...createDefaultNotifications(),
    ...(me.value.notification_settings || {}),
  };
}

function toggleRole(id) {
  if (!form.role_ids.includes(id)) {
    form.role_ids = [...form.role_ids, id];
  } else {
    form.role_ids = form.role_ids.filter((roleId) => roleId !== id);
  }
}

function sanitizeIban(value) {
  return value.replace(/\s+/g, "").toUpperCase();
}

async function saveProfile() {
  if (!me.value?.id) return;
  saving.value = true;
  try {
    const socials = {};
    socialKeys.forEach((key) => {
      const value = (form.socials[key] || "").trim();
      if (value) socials[key] = value;
    });
    const payload = {
      name: form.name.trim(),
      city: form.city.trim(),
      genre: form.genre.trim(),
      iban: sanitizeIban(form.iban || ""),
      socials,
      role_ids: form.role_ids,
      notification_settings: form.notifications,
    };
    await api.put(`profiles/${me.value.id}/`, payload);
    await fetchProfile(true);
    hydrateForm();
    showToast("Profil gespeichert", "success");
  } catch (err) {
    console.error("Profil konnte nicht gespeichert werden", err);
    showToast("Profil konnte nicht gespeichert werden", "error");
  } finally {
    saving.value = false;
  }
}

function resetExample() {
  example.title = "";
  example.link = "";
  example.file = null;
}

function onExampleFile(event) {
  example.file = event.target.files?.[0] || null;
}

async function uploadExample() {
  if (!me.value?.id) return;
  if (!example.title && !example.link && !example.file) {
    showToast("Bitte gib mindestens einen Titel, Link oder eine Datei an.", "error");
    return;
  }
  const formData = new FormData();
  formData.append("profile", me.value.id);
  if (example.title) formData.append("title", example.title);
  if (example.link) formData.append("link", example.link);
  if (example.file) formData.append("file", example.file);
  uploading.value = true;
  try {
    await api.post("examples/", formData, { headers: { "Content-Type": "multipart/form-data" } });
    resetExample();
    await loadExamples();
    showToast("Beispiel gespeichert", "success");
  } catch (err) {
    console.error("Beispiel konnte nicht hochgeladen werden", err);
    showToast("Upload fehlgeschlagen", "error");
  } finally {
    uploading.value = false;
  }
}

async function loadRoles() {
  try {
    const { data } = await api.get("roles/");
    roles.value = data;
  } catch (err) {
    console.error("Rollen konnten nicht geladen werden", err);
    showToast("Rollen konnten nicht geladen werden", "error");
  }
}

async function loadExamples() {
  if (!me.value?.id) return;
  loadingExamples.value = true;
  try {
    const { data } = await api.get("examples/", { params: { profile: me.value.id } });
    examples.value = data.filter((item) => item.profile === me.value.id);
  } catch (err) {
    console.error("Beispiele konnten nicht geladen werden", err);
    showToast("Beispiele konnten nicht geladen werden", "error");
    examples.value = [];
  } finally {
    loadingExamples.value = false;
  }
}

watch(
  () => me.value,
  () => hydrateForm()
);

onMounted(async () => {
  await fetchProfile();
  hydrateForm();
  await Promise.all([loadRoles(), loadExamples()]);
});
</script>

<style scoped>
.profile-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}
.hero-meta {
  margin-top: 16px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
}
.hero-meta .label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.hero-actions {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.form-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}
.section-head h2 {
  margin: 0;
}
.section-head .small {
  margin: 4px 0 0;
  font-size: 13px;
}
.field-grid {
  display: grid;
  gap: 14px;
}
.field-grid.two {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.field-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
}
.notification-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.notification-toggle {
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 12px;
  padding: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  background: rgba(248, 250, 252, 0.6);
}
.notification-toggle input {
  transform: scale(1.2);
}
.role-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.role-chip {
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.5);
  padding: 6px 16px;
  font-size: 13px;
  background: transparent;
  cursor: pointer;
}
.role-chip.active {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.1);
  color: #1d4ed8;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
.examples-card {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.count-pill {
  align-self: flex-start;
  border: 1px solid rgba(148, 163, 184, 0.4);
  border-radius: 999px;
  padding: 4px 12px;
  font-size: 12px;
}
.example-form {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}
.file-picker {
  border: 1px dashed rgba(148, 163, 184, 0.7);
  border-radius: 10px;
  padding: 10px 14px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
}
.file-picker input {
  display: none;
}
.example-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.example-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.example-list li {
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.4);
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.example-links {
  display: flex;
  gap: 8px;
}
.empty {
  text-align: center;
  margin: 0;
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
  }
  .hero-actions {
    width: 100%;
    justify-content: flex-start;
  }
  .example-form {
    grid-template-columns: 1fr;
  }
  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
