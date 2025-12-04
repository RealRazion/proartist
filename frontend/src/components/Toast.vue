<template>
  <transition name="fade">
    <div v-if="visible" class="toast" :data-type="type">
      <span class="label">{{ label }}</span>
      <span class="message">{{ message }}</span>
      <button class="close" type="button" @click="('close')">×</button>
    </div>
  </transition>
</template>

<script setup>
import { computed } from "vue";

const props = defineProps({
  message: { type: String, default: "" },
  type: { type: String, default: "info" },
  visible: { type: Boolean, default: false },
});

const label = computed(() => {
  if (props.type === "error") return "Fehler";
  if (props.type === "success") return "Erfolg";
  if (props.type === "warning") return "Hinweis";
  return "Info";
});
</script>

<style scoped>
.toast {
  position: fixed;
  top: 16px;
  right: 16px;
  min-width: 260px;
  max-width: 380px;
  padding: 12px 14px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 8px;
  align-items: center;
  background: #0f172a;
  color: #e2e8f0;
  z-index: 999;
}
.toast[data-type="success"] { background: #0f2a1a; color: #c7f7df; }
.toast[data-type="error"] { background: #2a0f14; color: #fdd8d8; }
.toast[data-type="warning"] { background: #2a210f; color: #f5e7c7; }
.label { font-weight: 700; }
.message { font-size: 14px; }
.close { background: transparent; border: none; color: inherit; font-size: 18px; cursor: pointer; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
