<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Login</h1>
      <p class="subtitle">Melde dich an, um dein Dashboard zu öffnen.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Benutzername
          <input class="input" v-model.trim="username" placeholder="Dein Benutzername" autocomplete="username" />
        </label>

        <label>
          Passwort
          <input
            class="input"
            v-model.trim="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="••••••••"
            autocomplete="current-password"
          />
        </label>

        <div class="actions">
          <label class="checkbox">
            <input type="checkbox" v-model="showPassword" /> Passwort anzeigen
          </label>
          <span class="muted">Zugang nur per Einladung.</span>
        </div>

        <button class="btn" type="submit" :disabled="loading">
          {{ loading ? "Anmelden..." : "Login" }}
        </button>
      </form>

      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
      <p class="switch">
        Noch kein Zugang?
        <router-link to="/register">Zugang anfragen</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import api from "../api";

const router = useRouter();
const route = useRoute();

const username = ref("");
const password = ref("");
const showPassword = ref(false);
const loading = ref(false);
const message = ref("");
const messageType = ref("info");

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

async function submit() {
  if (!username.value || !password.value) {
    showMessage("Bitte Benutzername und Passwort eingeben.", "error");
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    const { data } = await api.post("token/", {
      username: username.value,
      password: password.value,
    });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    showMessage("Login erfolgreich, weiterleiten...", "success");
    const redirect = route.query.redirect || "/dashboard";
    setTimeout(() => router.replace(redirect), 350);
  } catch (err) {
    console.error(err);
    showMessage("Login fehlgeschlagen. Bitte Daten prüfen.", "error");
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
.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
}
.checkbox {
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 6px;
  font-weight: 400;
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
.switch {
  text-align: center;
  margin-top: -6px;
  color: var(--muted);
}
</style>
