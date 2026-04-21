<template>
  <div class="content-studio wide">
    <header class="card studio-header">
      <div>
        <h1>Content Studio</h1>
        <p class="muted">Zentrale Plattform fÜr Tipps, News und Plugin Tutorials.</p>
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
      <h2>{{ editingItemId ? "Beitrag bearbeiten" : "Neuen Beitrag erstellen" }}</h2>
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
        <div v-if="selectedType === 'TUTORIAL'" class="media-editor card">
          <p class="muted small">Titelbild fuer das Tutorial</p>
          <label>
            Bilddatei
            <input class="input" type="file" accept="image/*" @change="handleImageSelect" />
          </label>
          <label>
            Weitere Bilder (Galerie)
            <input class="input" type="file" accept="image/*" multiple @change="handleGallerySelect" />
          </label>
          <p v-if="imageDraft.galleryPreviewUrls.length" class="muted small">
            {{ imageDraft.galleryPreviewUrls.length }} Galerie-Bilder bereit zum Upload
          </p>
          <div v-if="imageDraft.previewUrl" class="image-workbench">
            <div class="image-preview-wrap">
              <img :src="imageDraft.editedPreviewUrl || imageDraft.previewUrl" alt="Vorschau" class="image-preview" />
            </div>
            <div class="image-controls">
              <label>
                Format
                <select v-model="imageDraft.aspect" class="input">
                  <option value="16:9">16:9 (Wide)</option>
                  <option value="1:1">1:1 (Square)</option>
                  <option value="4:5">4:5 (Portrait)</option>
                </select>
              </label>
              <label>
                Zoom ({{ imageDraft.zoom.toFixed(2) }}x)
                <input v-model.number="imageDraft.zoom" class="input" type="range" min="1" max="2.4" step="0.05" />
              </label>
              <label>
                Helligkeit ({{ imageDraft.brightness }}%)
                <input v-model.number="imageDraft.brightness" class="input" type="range" min="70" max="140" step="1" />
              </label>
              <label>
                Kontrast ({{ imageDraft.contrast }}%)
                <input v-model.number="imageDraft.contrast" class="input" type="range" min="70" max="150" step="1" />
              </label>
              <div class="image-actions">
                <button class="btn ghost tiny" type="button" @click="rotateImage(-90)">↶ Drehen</button>
                <button class="btn ghost tiny" type="button" @click="rotateImage(90)">↷ Drehen</button>
                <button class="btn ghost tiny" type="button" @click="toggleFlip('x')">↔ Spiegeln</button>
                <button class="btn ghost tiny" type="button" @click="toggleFlip('y')">↕ Spiegeln</button>
                <button class="btn tiny" type="button" @click="applyImageEdits" :disabled="processingImage">
                  {{ processingImage ? "Bearbeite..." : "Zuschnitt anwenden" }}
                </button>
                <button class="btn ghost tiny" type="button" @click="resetImageDraft">Zuruecksetzen</button>
              </div>
            </div>
          </div>
        </div>
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
        <div class="actions">
          <button class="btn" type="submit" :disabled="saving">
            {{ saving ? "Speichere..." : editingItemId ? "Aenderungen speichern" : "Beitrag speichern" }}
          </button>
          <button v-if="editingItemId" class="btn ghost" type="button" @click="cancelEditing" :disabled="saving">Abbrechen</button>
        </div>
      </form>
    </section>
    <section v-else class="card access-note">
      <h2>Nur fÜr Admins</h2>
      <p class="muted">Erstellen, Aendern und Loeschen ist nur fÜr TEAM/Admin freigeschaltet.</p>
    </section>

    <section class="card list-section">
      <div class="section-head">
        <h2>{{ selectedTypeLabel }}</h2>
        <span class="badge">{{ items.length }} EintrÄge</span>
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
          <div v-if="selectedType === 'TUTORIAL' && tutorialImages(item).length" class="item-image-wrap">
            <img :src="tutorialImages(item)[itemGalleryIndex[item.id] || 0]" :alt="item.title" class="item-image" loading="lazy" />
            <div v-if="tutorialImages(item).length > 1" class="carousel-controls">
              <button class="btn ghost tiny" type="button" @click="stepGallery(item, -1)">Zurueck</button>
              <span class="muted small">{{ (itemGalleryIndex[item.id] || 0) + 1 }} / {{ tutorialImages(item).length }}</span>
              <button class="btn ghost tiny" type="button" @click="stepGallery(item, 1)">Weiter</button>
            </div>
          </div>
          <p class="item-body">{{ item.body }}</p>
          <div v-if="isTeam" class="actions">
            <button class="btn ghost tiny" type="button" @click="togglePublish(item)" :disabled="savingIds.has(item.id)">
              {{ item.is_published ? "Auf Entwurf setzen" : "Veroeffentlichen" }}
            </button>
            <button class="btn ghost tiny" type="button" @click="startEditing(item)" :disabled="savingIds.has(item.id)">
              Bearbeiten
            </button>
            <button
              v-if="selectedType === 'TUTORIAL' && item.images?.length"
              class="btn ghost tiny"
              type="button"
              @click="removeCurrentGalleryImage(item)"
              :disabled="savingIds.has(item.id)"
            >
              Aktuelles Bild entfernen
            </button>
            <button class="btn ghost danger tiny" type="button" @click="removeItem(item)" :disabled="savingIds.has(item.id)">
              Loeschen
            </button>
          </div>
        </li>
      </ul>
      <p v-if="!loading && !items.length" class="muted empty">Noch keine EintrÄge fÜr diesen Typ.</p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
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
  { value: "REFERRAL", label: "EmpfehlungsprÄmie" },
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
const editingItemId = ref(null);
const form = ref(buildForm());
const processingImage = ref(false);
const imageDraft = ref(buildImageDraft());
const itemGalleryIndex = ref({});

const selectedTypeLabel = computed(() => typeConfig[selectedType.value]?.title || "EintrÄge");

function buildForm() {
  return {
    title: "",
    body: "",
    tip_type: "CASHBACK",
    is_published: true,
  };
}

function buildImageDraft() {
  return {
    file: null,
    previewUrl: "",
    editedBlob: null,
    editedPreviewUrl: "",
    galleryFiles: [],
    galleryPreviewUrls: [],
    zoom: 1,
    aspect: "16:9",
    rotation: 0,
    brightness: 100,
    contrast: 100,
    flipX: false,
    flipY: false,
  };
}

function cleanupImageDraftUrls() {
  if (imageDraft.value.previewUrl) URL.revokeObjectURL(imageDraft.value.previewUrl);
  if (imageDraft.value.editedPreviewUrl) URL.revokeObjectURL(imageDraft.value.editedPreviewUrl);
  imageDraft.value.galleryPreviewUrls.forEach((url) => URL.revokeObjectURL(url));
}

function resetImageDraft() {
  cleanupImageDraftUrls();
  imageDraft.value = buildImageDraft();
}

function handleImageSelect(event) {
  const [file] = event?.target?.files || [];
  if (!file) return;
  if (!file.type?.startsWith("image/")) {
    showToast("Bitte nur Bilddateien auswaehlen", "error");
    return;
  }
  cleanupImageDraftUrls();
  imageDraft.value = {
    ...buildImageDraft(),
    file,
    previewUrl: URL.createObjectURL(file),
  };
}

function rotateImage(delta) {
  imageDraft.value.rotation = (imageDraft.value.rotation + delta + 360) % 360;
}

function toggleFlip(axis) {
  if (axis === "x") imageDraft.value.flipX = !imageDraft.value.flipX;
  if (axis === "y") imageDraft.value.flipY = !imageDraft.value.flipY;
}

function handleGallerySelect(event) {
  const files = Array.from(event?.target?.files || []);
  if (!files.length) return;
  const valid = files.filter((file) => file.type?.startsWith("image/"));
  if (!valid.length) {
    showToast("Bitte nur Bilddateien fuer die Galerie auswaehlen", "error");
    return;
  }
  imageDraft.value.galleryPreviewUrls.forEach((url) => URL.revokeObjectURL(url));
  imageDraft.value.galleryFiles = valid;
  imageDraft.value.galleryPreviewUrls = valid.map((file) => URL.createObjectURL(file));
}

function canvasSizeForAspect(aspect) {
  if (aspect === "1:1") return { width: 1200, height: 1200 };
  if (aspect === "4:5") return { width: 1200, height: 1500 };
  return { width: 1600, height: 900 };
}

function loadImageFromFile(file) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = URL.createObjectURL(file);
  });
}

async function applyImageEdits() {
  if (!imageDraft.value.file) return;
  processingImage.value = true;
  try {
    const img = await loadImageFromFile(imageDraft.value.file);
    const { width, height } = canvasSizeForAspect(imageDraft.value.aspect);
    const canvas = document.createElement("canvas");
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Canvas context unavailable");

    ctx.fillStyle = "#ffffff";
    ctx.fillRect(0, 0, width, height);
    ctx.save();
    ctx.translate(width / 2, height / 2);
    const rotation = (imageDraft.value.rotation * Math.PI) / 180;
    ctx.rotate(rotation);
    ctx.scale(imageDraft.value.flipX ? -1 : 1, imageDraft.value.flipY ? -1 : 1);
    ctx.filter = `brightness(${imageDraft.value.brightness}%) contrast(${imageDraft.value.contrast}%)`;

    const rotated = imageDraft.value.rotation % 180 !== 0;
    const imgW = rotated ? img.height : img.width;
    const imgH = rotated ? img.width : img.height;
    const baseScale = Math.max(width / imgW, height / imgH);
    const finalScale = baseScale * imageDraft.value.zoom;
    const drawW = img.width * finalScale;
    const drawH = img.height * finalScale;
    ctx.drawImage(img, -drawW / 2, -drawH / 2, drawW, drawH);
    ctx.restore();

    const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.92));
    if (!blob) throw new Error("Image processing failed");
    if (imageDraft.value.editedPreviewUrl) URL.revokeObjectURL(imageDraft.value.editedPreviewUrl);
    imageDraft.value.editedBlob = blob;
    imageDraft.value.editedPreviewUrl = URL.createObjectURL(blob);
    showToast("Bild bearbeitet", "success");
  } catch (err) {
    console.error("Bildbearbeitung fehlgeschlagen", err);
    showToast("Bildbearbeitung fehlgeschlagen", "error");
  } finally {
    processingImage.value = false;
  }
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
    let createdItemId = editingItemId.value;
    if (selectedType.value === "TIP") {
      const payload = {
        title: form.value.title,
        body: form.value.body,
        tip_type: form.value.tip_type,
        is_published: form.value.is_published,
      };
      if (editingItemId.value) {
        await api.patch(`${endpoint}${editingItemId.value}/`, payload);
      } else {
        const { data } = await api.post(endpoint, payload);
        createdItemId = data?.id || null;
      }
    } else if (selectedType.value === "TUTORIAL") {
      const payload = new FormData();
      payload.append("title", form.value.title);
      payload.append("body", form.value.body);
      payload.append("is_published", form.value.is_published ? "true" : "false");
      const imageBlob = imageDraft.value.editedBlob;
      const sourceFile = imageDraft.value.file;
      if (imageBlob) {
        const nameBase = sourceFile?.name?.replace(/\.[^.]+$/, "") || "tutorial-image";
        payload.append("image", imageBlob, `${nameBase}-edited.jpg`);
      } else if (sourceFile) {
        payload.append("image", sourceFile);
      }
      if (editingItemId.value) {
        await api.patch(`${endpoint}${editingItemId.value}/`, payload, { headers: { "Content-Type": "multipart/form-data" } });
      } else {
        const { data } = await api.post(endpoint, payload, { headers: { "Content-Type": "multipart/form-data" } });
        createdItemId = data?.id || null;
      }
      if (imageDraft.value.galleryFiles.length && createdItemId) {
        const galleryPayload = new FormData();
        imageDraft.value.galleryFiles.forEach((file) => galleryPayload.append("images", file));
        await api.post(`${endpoint}${createdItemId}/upload-images/`, galleryPayload, {
          headers: { "Content-Type": "multipart/form-data" },
        });
      }
    } else {
      const payload = {
        title: form.value.title,
        body: form.value.body,
        is_published: form.value.is_published,
      };
      if (editingItemId.value) {
        await api.patch(`${endpoint}${editingItemId.value}/`, payload);
      } else {
        const { data } = await api.post(endpoint, payload);
        createdItemId = data?.id || null;
      }
    }
    form.value = buildForm();
    editingItemId.value = null;
    resetImageDraft();
    await loadItems();
  } catch (err) {
    console.error("Beitrag konnte nicht gespeichert werden", err);
    showToast("Beitrag konnte nicht gespeichert werden", "error");
  } finally {
    saving.value = false;
  }
}

function startEditing(item) {
  editingItemId.value = item.id;
  form.value = {
    title: item.title || "",
    body: item.body || "",
    tip_type: item.tip_type || "CASHBACK",
    is_published: item.is_published ?? true,
  };
  resetImageDraft();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function cancelEditing() {
  editingItemId.value = null;
  form.value = buildForm();
  resetImageDraft();
}

function tutorialImages(item) {
  const cover = item?.image_url ? [item.image_url] : [];
  const gallery = Array.isArray(item?.images) ? item.images.map((img) => img.image_url).filter(Boolean) : [];
  return [...cover, ...gallery];
}

function stepGallery(item, delta) {
  const key = item.id;
  const images = tutorialImages(item);
  if (!images.length) return;
  const current = itemGalleryIndex.value[key] || 0;
  const next = (current + delta + images.length) % images.length;
  itemGalleryIndex.value = { ...itemGalleryIndex.value, [key]: next };
}

async function removeCurrentGalleryImage(item) {
  const idx = itemGalleryIndex.value[item.id] || 0;
  if (idx === 0) {
    showToast("Titelbild bitte im Bearbeiten-Modus ersetzen.", "warning");
    return;
  }
  const image = item.images?.[idx - 1];
  if (!image?.id) return;
  savingIds.value.add(item.id);
  try {
    await api.delete(`${endpointFor()}${item.id}/images/${image.id}/`);
    itemGalleryIndex.value = { ...itemGalleryIndex.value, [item.id]: 0 };
    await loadItems();
  } catch (err) {
    console.error("Bild konnte nicht entfernt werden", err);
    showToast("Bild konnte nicht entfernt werden", "error");
  } finally {
    savingIds.value.delete(item.id);
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
    console.error("Eintrag konnte nicht gelÖscht werden", err);
    showToast("Eintrag konnte nicht gelÖscht werden", "error");
  } finally {
    savingIds.value.delete(item.id);
  }
}

watch(
  () => selectedType.value,
  async () => {
    cancelEditing();
    form.value = buildForm();
    resetImageDraft();
    await loadItems();
  }
);

onMounted(async () => {
  await fetchProfile();
  await loadItems();
});

onUnmounted(() => {
  cleanupImageDraftUrls();
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

.media-editor {
  border-radius: 14px;
  padding: 12px;
  gap: 10px;
}

.image-workbench {
  display: grid;
  gap: 10px;
}

.image-preview-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: #0f172a;
  min-height: 220px;
  display: grid;
  place-items: center;
}

.image-preview {
  width: 100%;
  max-height: 420px;
  object-fit: contain;
}

.image-controls {
  display: grid;
  gap: 8px;
}

.carousel-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  padding: 8px;
  border-top: 1px solid var(--border);
}

.image-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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

.item-image-wrap {
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: #0f172a;
}

.item-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
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

  .image-actions .btn {
    width: 100%;
  }
}
</style>
