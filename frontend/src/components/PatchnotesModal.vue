<template>
  <Teleport to="body">
    <Transition name="patch-fade">
      <div v-if="isModalOpen" class="patchnotes-overlay" @click.self="handleClose">
        <div class="patchnotes-dialog" role="dialog" aria-modal="true" aria-labelledby="patchnotes-title">
          <!-- Close Button Top Right -->
          <button
            class="dialog-close-btn"
            type="button"
            @click="handleClose"
            aria-label="Schließen (ESC)"
            title="Schließen"
          >
            ✕
          </button>

          <!-- Dialog Header -->
          <header class="dialog-header">
            <div class="header-badge-row">
              <span class="badge-new-patch">🚀 PATCH RELEASE</span>
              <span class="patch-date" v-if="selectedPatch?.date">{{ formatDate(selectedPatch.date) }}</span>
            </div>
            <h2 id="patchnotes-title" class="dialog-title">
              {{ selectedPatch?.title || 'Was ist neu in UNYQ?' }}
            </h2>
            <div class="version-hero-row">
              <span class="version-pill">
                <span class="v-label">Version</span>
                <span class="v-val">
                  <strong class="v-bold">{{ selectedVersionParts.prefix }}{{ selectedVersionParts.majorMinor }}</strong>
                  <span class="v-thin">{{ selectedVersionParts.patchRest }}</span>
                </span>
              </span>
              <p class="patch-tagline" v-if="selectedPatch?.tagline">
                {{ selectedPatch.tagline }}
              </p>
            </div>
          </header>

          <!-- Version Switcher Tabs if multiple patches exist -->
          <nav v-if="allPatches.length > 1" class="version-tabs" aria-label="Versionen">
            <button
              v-for="(p, idx) in allPatches"
              :key="p.version"
              type="button"
              class="tab-btn"
              :class="{ active: activePatchIndex === idx }"
              @click="activePatchIndex = idx"
            >
              v{{ p.version }}
              <span v-if="idx === 0" class="latest-dot" title="Neueste Version"></span>
            </button>
          </nav>

          <!-- Dialog Content Body -->
          <div class="dialog-body">
            <!-- Highlights Section -->
            <section v-if="selectedPatch?.highlights && selectedPatch.highlights.length" class="patch-section highlights-box">
              <h3 class="section-title">
                <span class="sec-icon">✨</span> Die wichtigsten Neuerungen
              </h3>
              <ul class="highlights-list">
                <li v-for="(hl, i) in selectedPatch.highlights" :key="i" class="highlight-item">
                  <span class="item-check">✓</span>
                  <span>{{ hl }}</span>
                </li>
              </ul>
            </section>

            <!-- Detailed Changes List -->
            <section v-if="selectedPatch?.changes && selectedPatch.changes.length" class="patch-section changes-box">
              <h3 class="section-title">
                <span class="sec-icon">📋</span> Detail-Änderungen
              </h3>
              <ul class="changes-list">
                <li v-for="(change, i) in selectedPatch.changes" :key="i" class="change-item">
                  <span class="change-bullet">•</span>
                  <span>{{ change }}</span>
                </li>
              </ul>
            </section>
          </div>

          <!-- Dialog Footer -->
          <footer class="dialog-footer">
            <span class="footer-hint">
              Wird bei jedem neuen Patch automatisch einmalig beim Login angezeigt.
            </span>
            <button class="btn btn-understood" type="button" @click="handleUnderstood">
              Verstanden
            </button>
          </footer>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, onMounted, onUnmounted } from "vue";
import { usePatchnotes } from "../composables/usePatchnotes";

const {
  isModalOpen,
  activePatchIndex,
  latestPatch,
  allPatches,
  closePatchnotes,
  parseVersionParts
} = usePatchnotes();

const selectedPatch = computed(() => {
  return allPatches.value[activePatchIndex.value] || latestPatch.value;
});

const selectedVersionParts = computed(() => {
  return parseVersionParts(selectedPatch.value?.version || "");
});

function handleClose() {
  closePatchnotes(true);
}

function handleUnderstood() {
  closePatchnotes(true);
}

function formatDate(dateStr) {
  if (!dateStr) return "";
  try {
    const [year, month, day] = dateStr.split("-");
    if (!year || !month || !day) return dateStr;
    const months = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"];
    const mIdx = parseInt(month, 10) - 1;
    return `${parseInt(day, 10)}. ${months[mIdx] || month} ${year}`;
  } catch {
    return dateStr;
  }
}

function handleKeydown(e) {
  if (e.key === "Escape" && isModalOpen.value) {
    handleClose();
  }
}

onMounted(() => {
  window.addEventListener("keydown", handleKeydown);
});

onUnmounted(() => {
  window.removeEventListener("keydown", handleKeydown);
});
</script>

<style scoped>
/* Overlay Backdrop */
.patchnotes-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: var(--modal-overlay);
}

/* Dialog Container */
.patchnotes-dialog {
  position: relative;
  width: 100%;
  max-width: 580px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  background: radial-gradient(120% 120% at 50% 0%, #151f38 0%, #0d1527 100%);
  border: 1px solid rgba(112, 130, 255, 0.28);
  border-radius: 18px;
  box-shadow: 0 24px 64px -12px rgba(0, 0, 0, 0.7), 0 0 0 1px rgba(255, 255, 255, 0.06);
  color: #f1f5f9;
  overflow: hidden;
  animation: patchZoomIn 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Close button top right */
.dialog-close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.06);
  color: #94a3b8;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  z-index: 2;
}

.dialog-close-btn:hover {
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  border-color: rgba(255, 255, 255, 0.25);
  transform: scale(1.06);
}

/* Header */
.dialog-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(79, 70, 229, 0.12) 0%, transparent 100%);
}

.header-badge-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.badge-new-patch {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #818cf8;
  background: rgba(99, 102, 241, 0.18);
  border: 1px solid rgba(99, 102, 241, 0.35);
  border-radius: 999px;
}

.patch-date {
  font-size: 12px;
  color: #94a3b8;
}

.dialog-title {
  margin: 0 0 10px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.25;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.version-hero-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.version-pill {
  display: inline-flex;
  align-items: baseline;
  gap: 6px;
  padding: 4px 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
}

.v-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #94a3b8;
}

.v-val {
  display: inline-flex;
  align-items: baseline;
  font-size: 14px;
}

.v-bold {
  font-weight: 800;
  color: #a5b4fc;
}

.v-thin {
  font-weight: 300;
  opacity: 0.7;
  font-size: 12px;
  color: #cbd5e1;
}

.patch-tagline {
  margin: 0;
  font-size: 13px;
  color: #cbd5e1;
}

/* Tabs for historical patches */
.version-tabs {
  display: flex;
  gap: 6px;
  padding: 10px 24px;
  background: rgba(10, 16, 32, 0.45);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  overflow-x: auto;
}

.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.18s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  color: #ffffff;
  background: rgba(99, 102, 241, 0.22);
  border-color: rgba(99, 102, 241, 0.4);
}

.latest-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 6px #34d399;
}

/* Body */
.dialog-body {
  padding: 20px 24px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.patch-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-title {
  margin: 0;
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #cbd5e1;
  display: flex;
  align-items: center;
  gap: 6px;
}

.sec-icon {
  font-size: 14px;
}

/* Highlights */
.highlights-box {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  padding: 14px;
}

.highlights-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.highlight-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13.5px;
  line-height: 1.45;
  color: #f8fafc;
}

.item-check {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: rgba(52, 211, 153, 0.2);
  color: #34d399;
  font-size: 11px;
  font-weight: 700;
  flex-shrink: 0;
  margin-top: 2px;
}

/* Changes */
.changes-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 7px;
}

.change-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  font-size: 13px;
  line-height: 1.45;
  color: #94a3b8;
}

.change-bullet {
  color: #6366f1;
  font-weight: 700;
}

/* Footer */
.dialog-footer {
  padding: 16px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(10, 16, 32, 0.6);
}

.footer-hint {
  font-size: 11.5px;
  color: #64748b;
  line-height: 1.35;
  max-width: 320px;
}

.btn-understood {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%);
  color: #ffffff;
  border: none;
  border-radius: 10px;
  padding: 9px 20px;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.4);
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-understood:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(79, 70, 229, 0.55);
  filter: brightness(1.1);
}

.btn-understood:active {
  transform: translateY(0);
}

/* Animations */
.patch-fade-enter-active,
.patch-fade-leave-active {
  transition: opacity 0.2s ease;
}

.patch-fade-enter-from,
.patch-fade-leave-to {
  opacity: 0;
}

@keyframes patchZoomIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(8px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

@media (max-width: 540px) {
  .dialog-footer {
    flex-direction: column;
    align-items: stretch;
  }
  .btn-understood {
    width: 100%;
  }
  .footer-hint {
    text-align: center;
    max-width: 100%;
  }
}
</style>
