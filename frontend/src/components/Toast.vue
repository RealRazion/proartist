<template>
  <transition name="fade">
    <div v-if="visible" class="toast" :data-type="type">
      <span class="label">{{ label }}</span>
      <span class="message">{{ message }}</span>
      <button class="close" type="button" @click="emit('close')" aria-label="Toast schliessen">x</button>
    </div>
  </transition>
</template>

<script setup>
import { computed } from "vue";

const emit = defineEmits(["close"]);

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
  border: 1px solid var(--border);
  border-left: 4px solid var(--brand);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.12);
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 8px;
  align-items: center;
  background: var(--card);
  color: var(--text);
  z-index: 999;
}
.toast[data-type="success"] { border-left-color: #22c55e; }
.toast[data-type="error"] { border-left-color: #ef4444; }
.toast[data-type="warning"] { border-left-color: #f59e0b; }
.label { font-weight: 700; }
.message { font-size: 14px; }
.close { background: transparent; border: none; color: inherit; font-size: 18px; cursor: pointer; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
