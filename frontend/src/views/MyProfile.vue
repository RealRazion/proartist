<template>
  <div class="profile">
    <section class="card grid-two">
      <div class="left">
        <h1>Mein Profil</h1>
        <p class="muted">Aktualisiere deine Angaben, damit dich andere leichter finden.</p>

        <form class="form" @submit.prevent="saveProfile">
          <label>
            Name / Künstlername
            <input class="input" v-model.trim="form.name" placeholder="z. B. LUNA" />
          </label>
          <label>
            Stadt
            <input class="input" v-model.trim="form.city" placeholder="z. B. Berlin" />
          </label>
          <label>
            Genre
            <input class="input" v-model.trim="form.genre" placeholder="z. B. Hip-Hop, R&B" />
          </label>
          <label>
            IBAN (optional)
            <input class="input" v-model.trim="form.iban" placeholder="DE00 0000 0000 0000 0000 00" />
          </label>

          <div>
            <p class="section-title">Rollen</p>
            <div class="roles">
              <label v-for="role in visibleRoles" :key="role.id">
                <input type="checkbox" :value="role.id" v-model="form.role_ids" />
                {{ roleLabels[role.key] || role.key }}
              </label>
            </div>
            <small v-if="!isTeam" class="hint muted">Team-Rollen werden vom Admin vergeben.</small>
          </div>

          <div>
            <p class="section-title">Social Links</p>
            <div class="socials">
              <label v-for="key in socialKeys" :key="key">
                {{ socialLabels[key] }}
                <input
                  class="input"
                  v-model.trim="form.socials[key]"
                  :placeholder="socialPlaceholders[key]"
                />
              </label>
            </div>
          </div>

          <button class="btn" type="submit" :disabled="saving">
            {{ saving ? "Speichere…" : "Profil speichern" }}
          </button>
          <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
        </form>
      </div>

      <aside class="card examples">
        <h2>Beispiele</h2>
        <form class="upload" @submit.prevent="uploadExample">
          <input class="input" v-model.trim="example.title" placeholder="Titel" />
          <input class="input" v-model.trim="example.link" placeholder="Link (YouTube, SoundCloud…)" />
          <label class="file">
            <input type="file" @change="onFile" />
            {{ example.file ? example.file.name : "Datei auswählen" }}
          </label>
          <button class="btn" type="submit" :disabled="uploading">
            {{ uploading ? "Lädt…" : "Beispiel hinzufügen" }}
          </button>
        </form>
        <ul>
          <li v-for="item in examples" :key="item.id">
            <div>
              <strong>{{ item.title || "Ohne Titel" }}</strong>
              <p class="muted">
                <span v-if="item.link">{{ item.link }}</span>
                <span v-else-if="item.file">Datei hochgeladen</span>
                <span v-else>Keine zusätzlichen Infos</span>
              </p>
            </div>
            <a v-if="item.link" class="link" :href="item.link" target="_blank" rel="noopener">Ansehen</a>
            <a v-else-if="item.file" class="link" :href="item.file" target="_blank" rel="noopener">Download</a>
          </li>
        </ul>
        <p v-if="!examples.length" class="muted empty">Noch keine Beispiele hochgeladen.</p>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref, onMounted, computed } from "vue";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { profile: me, fetchProfile, isTeam } = useCurrentProfile();

const roles = ref([]);
const examples = ref([]);
const saving = ref(false);
const uploading = ref(false);
const message = ref("");
const messageType = ref("info");
const visibleRoles = computed(() =>
  roles.value.filter((role) => isTeam.value || role.key !== "TEAM")
);

const socialKeys = ["instagram", "youtube", "soundcloud", "tiktok", "spotify"];
const socialLabels = {
  instagram: "Instagram",
  youtube: "YouTube",
  soundcloud: "SoundCloud",
  tiktok: "TikTok",
  spotify: "Spotify",
};
const socialPlaceholders = {
  instagram: "@deinhandle",
  youtube: "https://youtube.com/…",
  soundcloud: "https://soundcloud.com/…",
  tiktok: "@deinhandle",
  spotify: "https://open.spotify.com/…",
};

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
  socials: {},
  role_ids: [],
});

const example = reactive({
  title: "",
  link: "",
  file: null,
});

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
  if (text) {
    setTimeout(() => {
      message.value = "";
    }, 2500);
  }
}

function hydrateForm() {
  if (!me.value) return;
  form.name = me.value.name || "";
  form.city = me.value.city || "";
  form.genre = me.value.genre || "";
  form.iban = me.value.iban || "";
  form.socials = { ...me.value.socials } || {};
  form.role_ids = (me.value.roles || []).map((role) => role.id);
}

function onFile(event) {
  const file = event.target.files?.[0] || null;
  example.file = file;
}

async function saveProfile() {
  if (!me.value?.id) return;
  saving.value = true;
  showMessage("");
  try {
    const payload = {
      name: form.name,
      city: form.city,
      genre: form.genre,
      iban: form.iban,
      socials: form.socials,
      role_ids: form.role_ids,
    };
    await api.put(`profiles/${me.value.id}/`, payload);
    await fetchProfile(true);
    hydrateForm();
    showMessage("Profil gespeichert!", "success");
  } catch (err) {
    console.error("Profil konnte nicht gespeichert werden", err);
    showMessage("Fehler beim Speichern. Bitte erneut versuchen.", "error");
  } finally {
    saving.value = false;
  }
}

async function uploadExample() {
  if (!me.value?.id) return;
  if (!example.title && !example.link && !example.file) {
    showMessage("Bitte gib mindestens einen Titel, Link oder eine Datei an.", "error");
    return;
  }
  const formData = new FormData();
  formData.append("profile", me.value.id);
  if (example.title) formData.append("title", example.title);
  if (example.link) formData.append("link", example.link);
  if (example.file) formData.append("file", example.file);
  uploading.value = true;
  try {
    await api.post("examples/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    example.title = "";
    example.link = "";
    example.file = null;
    await loadExamples();
    showMessage("Beispiel hochgeladen.", "success");
  } catch (err) {
    console.error("Beispiel konnte nicht hochgeladen werden", err);
    showMessage("Upload fehlgeschlagen.", "error");
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
  }
}

async function loadExamples() {
  if (!me.value?.id) return;
  try {
    const { data } = await api.get("examples/", { params: { profile: me.value.id } });
    examples.value = data.filter((item) => item.profile === me.value.id);
  } catch (err) {
    console.error("Beispiele konnten nicht geladen werden", err);
    examples.value = [];
  }
}

onMounted(async () => {
  await Promise.all([fetchProfile(), loadRoles()]);
  hydrateForm();
  await loadExamples();
});
</script>

<style scoped>
.profile {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
}
.grid-two {
  display: grid;
  grid-template-columns: 1fr minmax(260px, 340px);
  gap: 20px;
}
.left {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
}
.roles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 8px 12px;
}
.roles label {
  font-weight: 500;
  flex-direction: row;
  align-items: center;
  gap: 8px;
}
.socials {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}
.section-title {
  margin: 0 0 6px;
  font-weight: 600;
}
.feedback {
  margin: 0;
  font-size: 14px;
}
.feedback.success {
  color: #34d399;
}
.feedback.error {
  color: #f87171;
}
.examples {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.upload {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.file {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px dashed rgba(75, 91, 255, 0.4);
  cursor: pointer;
}
.file input {
  display: none;
}
.examples ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}
.examples li {
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(75, 91, 255, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.examples li .link {
  color: var(--brand);
  text-decoration: none;
  font-weight: 600;
}
.examples li .link:hover {
  text-decoration: underline;
}
.empty {
  text-align: center;
  margin: 0;
}

@media (max-width: 960px) {
  .grid-two {
    grid-template-columns: 1fr;
  }
}
</style>
