<template>
  <div>
    <router-view />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
    <PatchnotesModal />
  </div>
</template>

<script setup>
import { onMounted, watch } from "vue";
import { useRoute } from "vue-router";
import Toast from "./components/Toast.vue";
import PatchnotesModal from "./components/PatchnotesModal.vue";
import { useToast } from "./composables/useToast";
import { usePatchnotes } from "./composables/usePatchnotes";

const { toast, hideToast } = useToast();
const { checkFirstLoginNotice } = usePatchnotes();
const route = useRoute();

onMounted(() => {
  checkFirstLoginNotice();
});

// Whenever route changes (e.g. redirect after login), check if the patch notes should be shown
watch(
  () => route.path,
  () => {
    checkFirstLoginNotice();
  }
);
</script>

