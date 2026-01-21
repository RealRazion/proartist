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
          <textarea class="input textarea" v-model.trim="form.body" placeholder="Infos für alle Nutzer"></textarea>
        </label>
        <label class="toggle">
          <input type="checkbox" v-model="form.is_published" />
          Sofort veröffentlichen
        </label>
        <label class="file-picker">
          <input type="file" accept="image/*" @change="onImageSelect" />
          <span>{{ imageFile ? imageFile.name : "Bild auswaehlen" }}</span>
        </label>
        <div v-if="cropPreviewUrl" class="cropper">
          <div ref="cropFrame" class="crop-frame" @pointerdown="startCropDrag">
            <img ref="cropImage" :src="cropPreviewUrl" :style="cropImageStyle" @load="onCropImageLoad" />
          </div>
          <div class="crop-controls">
            <label>
              Zoom
              <input
                type="range"
                :min="minScale"
                :max="maxScale"
                step="0.01"
                v-model.number="cropState.scale"
                @input="onCropZoom"
              />
            </label>
            <button class="btn ghost tiny" type="button" @click="initializeCrop">Zuruecksetzen</button>
            <button class="btn ghost tiny" type="button" @click="clearImage">Bild entfernen</button>
          </div>
          <p class="muted small">Ziehe das Bild, um den Ausschnitt anzupassen.</p>
        </div>
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
          <img v-if="post.image || post.image_url" class="post-image" :src="post.image || post.image_url" :alt="post.title" />
          <p>{{ post.body }}</p>
          <div v-if="isTeam" class="actions">
            <button class="btn ghost tiny" type="button" @click="togglePublish(post)" :disabled="savingIds.has(post.id)">
              {{ post.is_published ? "Auf Entwurf setzen" : "Veröffentlichen" }}
            </button>
            <button class="btn ghost danger tiny" type="button" @click="removePost(post)" :disabled="savingIds.has(post.id)">
              Löschen
            </button>
          </div>
        </li>
      </ul>
      <p v-if="!loading && !posts.length" class="muted empty">Noch keine News vorhanden.</p>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, nextTick, onBeforeUnmount, onMounted } from "vue";
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
const imageFile = ref(null);
const cropPreviewUrl = ref("");
const cropFrame = ref(null);
const cropImage = ref(null);
const cropMeta = ref({ naturalWidth: 0, naturalHeight: 0 });
const cropState = ref({ scale: 1, offsetX: 0, offsetY: 0 });
const minScale = ref(1);
let dragStart = null;

const cropImageStyle = computed(() => ({
  transform: `translate(${cropState.value.offsetX}px, ${cropState.value.offsetY}px) scale(${cropState.value.scale})`,
}));

const maxScale = computed(() => Math.max(minScale.value * 3, minScale.value + 1));

function formatDate(value) {
  if (!value) return "";
  return new Intl.DateTimeFormat("de-DE", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function cleanupPreviewUrl() {
  if (cropPreviewUrl.value) {
    URL.revokeObjectURL(cropPreviewUrl.value);
  }
  cropPreviewUrl.value = "";
}

function resetCropper() {
  cropMeta.value = { naturalWidth: 0, naturalHeight: 0 };
  cropState.value = { scale: 1, offsetX: 0, offsetY: 0 };
  minScale.value = 1;
}

function clearImage() {
  imageFile.value = null;
  cleanupPreviewUrl();
  resetCropper();
}

async function onImageSelect(event) {
  const file = event.target.files?.[0];
  if (!file) {
    clearImage();
    return;
  }
  imageFile.value = file;
  cleanupPreviewUrl();
  cropPreviewUrl.value = URL.createObjectURL(file);
  resetCropper();
  await nextTick();
  if (cropImage.value?.complete) {
    initializeCrop();
  }
}

function onCropImageLoad() {
  if (!cropImage.value) return;
  cropMeta.value = {
    naturalWidth: cropImage.value.naturalWidth,
    naturalHeight: cropImage.value.naturalHeight,
  };
  initializeCrop();
}

function initializeCrop() {
  const frame = cropFrame.value;
  if (!frame || !cropMeta.value.naturalWidth || !cropMeta.value.naturalHeight) return;
  const frameWidth = frame.clientWidth;
  const frameHeight = frame.clientHeight;
  if (!frameWidth || !frameHeight) return;
  const scale = Math.max(frameWidth / cropMeta.value.naturalWidth, frameHeight / cropMeta.value.naturalHeight);
  minScale.value = scale;
  cropState.value.scale = scale;
  cropState.value.offsetX = (frameWidth - cropMeta.value.naturalWidth * scale) / 2;
  cropState.value.offsetY = (frameHeight - cropMeta.value.naturalHeight * scale) / 2;
  clampCropOffsets();
}

function clampCropOffsets() {
  const frame = cropFrame.value;
  if (!frame || !cropMeta.value.naturalWidth || !cropMeta.value.naturalHeight) return;
  const frameWidth = frame.clientWidth;
  const frameHeight = frame.clientHeight;
  const scaledWidth = cropMeta.value.naturalWidth * cropState.value.scale;
  const scaledHeight = cropMeta.value.naturalHeight * cropState.value.scale;
  const minX = Math.min(0, frameWidth - scaledWidth);
  const minY = Math.min(0, frameHeight - scaledHeight);
  cropState.value.offsetX = Math.min(0, Math.max(minX, cropState.value.offsetX));
  cropState.value.offsetY = Math.min(0, Math.max(minY, cropState.value.offsetY));
}

function startCropDrag(event) {
  if (!cropPreviewUrl.value) return;
  event.preventDefault();
  dragStart = {
    x: event.clientX,
    y: event.clientY,
    offsetX: cropState.value.offsetX,
    offsetY: cropState.value.offsetY,
  };
  window.addEventListener("pointermove", onCropDrag);
  window.addEventListener("pointerup", stopCropDrag);
}

function onCropDrag(event) {
  if (!dragStart) return;
  const dx = event.clientX - dragStart.x;
  const dy = event.clientY - dragStart.y;
  cropState.value.offsetX = dragStart.offsetX + dx;
  cropState.value.offsetY = dragStart.offsetY + dy;
  clampCropOffsets();
}

function stopCropDrag() {
  dragStart = null;
  window.removeEventListener("pointermove", onCropDrag);
  window.removeEventListener("pointerup", stopCropDrag);
}

function onCropZoom() {
  if (cropState.value.scale < minScale.value) {
    cropState.value.scale = minScale.value;
  }
  clampCropOffsets();
}

async function buildCroppedImage() {
  if (!cropPreviewUrl.value || !cropFrame.value || !cropImage.value) return null;
  const frameWidth = cropFrame.value.clientWidth;
  const frameHeight = cropFrame.value.clientHeight;
  if (!frameWidth || !frameHeight) return null;
  const canvas = document.createElement("canvas");
  canvas.width = Math.round(frameWidth);
  canvas.height = Math.round(frameHeight);
  const ctx = canvas.getContext("2d");
  if (!ctx) return null;
  ctx.drawImage(
    cropImage.value,
    cropState.value.offsetX,
    cropState.value.offsetY,
    cropMeta.value.naturalWidth * cropState.value.scale,
    cropMeta.value.naturalHeight * cropState.value.scale
  );
  return new Promise((resolve) => {
    canvas.toBlob((blob) => resolve(blob), "image/jpeg", 0.9);
  });
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
    if (imageFile.value) {
      const payload = new FormData();
      payload.append("title", form.value.title);
      payload.append("body", form.value.body);
      payload.append("is_published", form.value.is_published ? "true" : "false");
      const cropped = await buildCroppedImage();
      if (cropped) {
        payload.append("image", cropped, imageFile.value.name || "news-image.jpg");
      } else {
        payload.append("image", imageFile.value, imageFile.value.name);
      }
      await api.post("news/", payload, { headers: { "Content-Type": "multipart/form-data" } });
    } else {
      await api.post("news/", form.value);
    }
    form.value = { title: "", body: "", is_published: true };
    clearImage();
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
  if (!confirm(`Post "${post.title}" wirklich löschen?`)) return;
  savingIds.value.add(post.id);
  try {
    await api.delete(`news/${post.id}/`);
    await loadNews();
  } catch (err) {
    console.error("Post konnte nicht gelöscht werden", err);
  } finally {
    savingIds.value.delete(post.id);
  }
}

onMounted(async () => {
  await fetchProfile();
  await loadNews();
});

onBeforeUnmount(() => {
  stopCropDrag();
  cleanupPreviewUrl();
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
.file-picker {
  border: 1px dashed var(--border);
  border-radius: 12px;
  padding: 10px 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  background: var(--card);
  font-weight: 500;
}
.file-picker input {
  display: none;
}
.cropper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.crop-frame {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 16px;
  overflow: hidden;
  border: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.05);
  cursor: grab;
  touch-action: none;
}
.crop-frame:active {
  cursor: grabbing;
}
.crop-frame img {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: top left;
  user-select: none;
  pointer-events: none;
}
.crop-controls {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 10px;
}
.crop-controls label {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 12px;
  color: var(--muted);
}
.crop-controls input[type="range"] {
  width: 200px;
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
.post-image {
  width: 100%;
  border-radius: 12px;
  border: 1px solid var(--border);
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
:global(.dark) .news .crop-frame {
  background: rgba(15, 23, 42, 0.45);
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

