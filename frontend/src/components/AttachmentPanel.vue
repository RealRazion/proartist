<template>
  <section class="attachments-panel" v-if="entityId">
    <header>
      <div>
        <h3>{{ title }}</h3>
        <p v-if="description" class="muted description">{{ description }}</p>
      </div>
      <button class="btn ghost tiny" type="button" @click="fetchAttachments(true)" :disabled="loading">
        Neu laden
      </button>
    </header>

    <ul v-if="attachments.length" class="attachment-list">
      <li v-for="file in attachments" :key="file.id">
        <a :href="file.file_url" target="_blank" rel="noopener">
          {{ file.label || file.file_name || "Datei" }}
        </a>
        <small class="muted">{{ file.uploaded_by?.name || file.uploaded_by?.username }}</small>
        <button class="iconbtn danger" type="button" @click="removeAttachment(file.id)" :disabled="mutating">
          X
        </button>
      </li>
    </ul>
    <p v-else-if="loading" class="muted">Lade Anhänge...</p>
    <p v-else class="muted">Keine Anhänge.</p>

    <form class="upload-row" @submit.prevent="uploadAttachment">
      <input class="input" v-model.trim="draft.label" placeholder="Kurzbeschreibung" />
      <label class="file-picker">
        <input type="file" @change="onFileChange" />
        {{ draft.file ? draft.file.name : "Datei wählen" }}
      </label>
      <button class="btn tiny" type="submit" :disabled="mutating || loading">
        {{ mutating ? "Lade..." : "Hochladen" }}
      </button>
    </form>
  </section>
</template>

<script setup>
import { ref, watch, computed } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";

const props = defineProps({
  entityType: {
    type: String,
    required: true,
    validator: (value) => ["project", "task"].includes(value),
  },
  entityId: {
    type: [Number, String],
    required: true,
  },
  title: {
    type: String,
    default: "Dateianhänge",
  },
  description: {
    type: String,
    default: "",
  },
});

const attachments = ref([]);
const loading = ref(false);
const mutating = ref(false);
const draft = ref({ label: "", file: null });
const { showToast } = useToast();

const endpoint = computed(() => `${props.entityType}-attachments/`);
const payloadKey = computed(() => (props.entityType === "project" ? "project" : "task"));

async function fetchAttachments(force = false) {
  if (!props.entityId) return;
  if (loading.value && !force) return;
  loading.value = true;
  try {
    const { data } = await api.get(endpoint.value, { params: { [payloadKey.value]: props.entityId } });
    attachments.value = data;
  } catch (err) {
    console.error("Anhänge konnten nicht geladen werden", err);
    showToast("Anhänge konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

function onFileChange(event) {
  draft.value.file = event.target.files?.[0] || null;
}

async function uploadAttachment() {
  if (!draft.value.file) {
    showToast("Bitte Datei wählen", "error");
    return;
  }
  mutating.value = true;
  try {
    const formData = new FormData();
    formData.append(payloadKey.value, props.entityId);
    formData.append("label", draft.value.label);
    formData.append("file", draft.value.file);
    await api.post(endpoint.value, formData, { headers: { "Content-Type": "multipart/form-data" } });
    draft.value.label = "";
    draft.value.file = null;
    showToast("Anhang gespeichert", "success");
    await fetchAttachments(true);
  } catch (err) {
    console.error("Anhang konnte nicht gespeichert werden", err);
    showToast("Anhang konnte nicht gespeichert werden", "error");
  } finally {
    mutating.value = false;
  }
}

async function removeAttachment(attachmentId) {
  if (!confirm("Anhang entfernen?")) return;
  mutating.value = true;
  try {
    await api.delete(`${endpoint.value}${attachmentId}/`);
    showToast("Anhang gelöscht", "success");
    await fetchAttachments(true);
  } catch (err) {
    console.error("Anhang konnte nicht gelöscht werden", err);
    showToast("Anhang konnte nicht gelöscht werden", "error");
  } finally {
    mutating.value = false;
  }
}

watch(
  () => props.entityId,
  (value) => {
    attachments.value = [];
    if (value) {
      fetchAttachments(true);
    }
  },
  { immediate: true }
);
</script>

<style scoped>
.attachments-panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.attachments-panel header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.attachments-panel .description {
  margin: 2px 0 0;
  font-size: 13px;
}
.attachment-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.attachment-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}
.attachment-list a {
  font-weight: 600;
  color: var(--brand);
}
.upload-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.file-picker {
  border: 1px dashed rgba(148, 163, 184, 0.7);
  border-radius: 10px;
  padding: 6px 14px;
  font-size: 13px;
  cursor: pointer;
}
.file-picker input {
  display: none;
}
.iconbtn {
  border: none;
  background: transparent;
  cursor: pointer;
}
.iconbtn.danger {
  color: #dc2626;
}
</style>
