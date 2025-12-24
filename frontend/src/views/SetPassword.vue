<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Passwort setzen</h1>
      <p class="subtitle">Erstelle dein Passwort, um dich anmelden zu können.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Neues Passwort
          <input
            class="input"
            v-model.trim="password"
            type="password"
            autocomplete="new-password"
            placeholder="Mindestens 8 Zeichen"
          />
        </label>
        <label>
          Passwort bestätigen
          <input
            class="input"
            v-model.trim="confirm"
            type="password"
            autocomplete="new-password"
            placeholder="Wiederholen"
          />
        </label>
        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? "Speichere..." : "Passwort speichern" }}
        </button>
      </form>

      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api";

const router = useRouter();
const route = useRoute();

const password = ref("");
const confirm = ref("");
const loading = ref(false);
const message = ref("");
const messageType = ref("info");

const uid = computed(() => String(route.query.uid || ""));
const token = computed(() => String(route.query.token || ""));

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

async function submit() {
  if (!uid.value || !token.value) {
    showMessage("Einladungslink ungültig oder abgelaufen.", "error");
    return;
  }
  if (!password.value || password.value.length < 8) {
    showMessage("Bitte ein Passwort mit mindestens 8 Zeichen wählen.", "error");
    return;
  }
  if (password.value !== confirm.value) {
    showMessage("Die Passwörter stimmen nicht überein.", "error");
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    await api.post("set-password/", {
      uid: uid.value,
      token: token.value,
      password: password.value,
    });
    showMessage("Passwort gespeichert. Bitte jetzt einloggen.", "success");
    setTimeout(() => router.push({ name: "login" }), 600);
  } catch (err) {
    showMessage("Passwort konnte nicht gesetzt werden.", "error");
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}
.auth-card {
  width: 100%;
  max-width: 420px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.subtitle {
  margin: -8px 0 8px;
  color: var(--muted);
}
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
  color: var(--text);
}
.feedback {
  margin: 0;
  font-size: 14px;
  text-align: center;
}
.feedback.error {
  color: #f87171;
}
.feedback.success {
  color: #34d399;
}
</style>
