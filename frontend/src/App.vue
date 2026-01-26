<template>
  <div>
    <router-view />
    <Toast :visible="toast.visible" :message="toast.message" :type="toast.type" @close="hideToast" />
  </div>
</template>

<script setup>
import Toast from "./components/Toast.vue";
import { useToast } from "./composables/useToast";

const { toast, hideToast } = useToast();
</script>
