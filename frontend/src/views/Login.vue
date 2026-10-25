<template>
  <div class="auth-page">
    <div class="card auth-card">
      <div class="auth-header">
        <div class="brand-badge">UNYQ</div>
        <h1>Login</h1>
        <p class="subtitle">Melde dich an, um den UNYQ Hub zu öffnen.</p>
      </div>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Benutzername oder E-Mail
          <input
            class="input"
            v-model.trim="username"
            placeholder="Dein Benutzername oder E-Mail"
            autocomplete="username"
            required
          />
        </label>

        <label>
          Passwort
          <input
            class="input"
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="••••••••"
            autocomplete="current-password"
            required
          />
        </label>

        <div class="actions">
          <label class="checkbox">
            <input type="checkbox" v-model="showPassword" /> Passwort anzeigen
          </label>
          <button type="button" class="btn-text-link" @click="openForgotModal">
            Passwort vergessen?
          </button>
        </div>

        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? "Anmelden..." : "Login" }}
        </button>
      </form>

      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>

      <div class="switch">
        <span>Noch kein Zugang?</span>
        <router-link to="/register" class="highlight-link">Zugang anfragen</router-link>
      </div>
    </div>

    <!-- Passwort vergessen Modal -->
    <div v-if="showForgotModal" class="modal-backdrop" @click.self="closeForgotModal">
      <div class="modal card">
        <div class="modal-header">
          <h2>Passwort zurücksetzen</h2>
          <button type="button" class="close-btn" @click="closeForgotModal">✕</button>
        </div>
        <p class="modal-intro">
          Gib deine registrierte E-Mail-Adresse ein. Wir senden dir einen sicheren Link, mit dem du ein neues Passwort vergeben kannst.
        </p>

        <form class="auth-form" @submit.prevent="submitForgotPassword">
          <label>
            E-Mail-Adresse
            <input
              type="email"
              class="input"
              v-model.trim="forgotEmail"
              placeholder="deine-email@example.com"
              required
            />
          </label>

          <p v-if="forgotMessage" :class="['feedback', forgotMessageType]">{{ forgotMessage }}</p>

          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="closeForgotModal">Abbrechen</button>
            <button type="submit" class="btn btn-primary" :disabled="forgotLoading">
              {{ forgotLoading ? "Wird gesendet..." : "Reset-Link anfordern" }}
            </button>
          </div>
        </form>
      </div>
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

// Forgot Password Modal
const showForgotModal = ref(false);
const forgotEmail = ref("");
const forgotLoading = ref(false);
const forgotMessage = ref("");
const forgotMessageType = ref("info");

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

function openForgotModal() {
  forgotEmail.value = username.value.includes("@") ? username.value : "";
  forgotMessage.value = "";
  showForgotModal.value = true;
}

function closeForgotModal() {
  showForgotModal.value = false;
  forgotMessage.value = "";
}

async function submit() {
  if (!username.value || !password.value) {
    showMessage("Bitte Benutzername/E-Mail und Passwort eingeben.", "error");
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    const { data } = await api.post("token/", {
      username: username.value.trim(),
      password: password.value,
    });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    showMessage("Login erfolgreich, weiterleiten...", "success");
    const redirect = route.query.redirect || "/platforms";
    setTimeout(() => router.replace(redirect), 350);
  } catch (err) {
    console.error(err);
    const detail = err?.response?.data?.detail;
    showMessage(
      typeof detail === "string" && detail ? detail : "Login fehlgeschlagen. Bitte Zugangsdaten prüfen.",
      "error"
    );
  } finally {
    loading.value = false;
  }
}

async function submitForgotPassword() {
  if (!forgotEmail.value) {
    forgotMessage.value = "Bitte eine gültige E-Mail-Adresse eingeben.";
    forgotMessageType.value = "error";
    return;
  }
  forgotLoading.value = true;
  forgotMessage.value = "";
  try {
    const { data } = await api.post("request-password-reset/", {
      email: forgotEmail.value.trim(),
    });
    forgotMessage.value = data?.message || "E-Mail wurde gesendet. Bitte prüfe dein Postfach.";
    forgotMessageType.value = "success";
  } catch (err) {
    const detail = err?.response?.data?.detail;
    forgotMessage.value = typeof detail === "string" && detail ? detail : "Anfrage konnte nicht verarbeitet werden.";
    forgotMessageType.value = "error";
  } finally {
    forgotLoading.value = false;
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
  background: radial-gradient(circle at 50% 20%, rgba(99, 102, 241, 0.08) 0%, transparent 60%), #0c0d14;
}

.auth-card {
  width: 100%;
  max-width: 440px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 36px 32px;
  border-radius: 16px;
  background: #141622;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
}

.auth-header {
  text-align: center;
}

.brand-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 999px;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 2px;
  color: #c084fc;
  margin-bottom: 12px;
}

.auth-header h1 {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 8px;
  color: #fff;
  letter-spacing: -0.5px;
}

.subtitle {
  margin: 0;
  font-size: 14px;
  color: #94a3b8;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-weight: 600;
  font-size: 13px;
  color: #cbd5e1;
}

.input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 10px;
  background: #0d0e17;
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 14px;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.input:focus {
  outline: none;
  border-color: #8b5cf6;
  box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

.actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
}

.checkbox {
  display: flex;
  align-items: center;
  flex-direction: row;
  gap: 8px;
  font-weight: 400;
  color: #94a3b8;
  cursor: pointer;
}

.btn-text-link {
  background: none;
  border: none;
  color: #a78bfa;
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  text-underline-offset: 3px;
  transition: color 0.2s;
}

.btn-text-link:hover {
  color: #c084fc;
}

.btn-primary {
  padding: 13px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  transition: opacity 0.2s, transform 0.1s;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.95;
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.feedback {
  margin: 0;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 13px;
  text-align: center;
}

.feedback.error {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #f87171;
}

.feedback.success {
  background: rgba(16, 185, 129, 0.12);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #34d399;
}

.feedback.info {
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
}

.switch {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #94a3b8;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.highlight-link {
  color: #a78bfa;
  font-weight: 600;
  text-decoration: none;
}

.highlight-link:hover {
  text-decoration: underline;
}

/* Modal */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.modal {
  width: 100%;
  max-width: 420px;
  background: #181a29;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
  color: #fff;
}

.close-btn {
  background: none;
  border: none;
  color: #94a3b8;
  font-size: 18px;
  cursor: pointer;
  padding: 4px;
}

.close-btn:hover {
  color: #fff;
}

.modal-intro {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: #94a3b8;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 8px;
}

@media (max-width: 520px) {
  .actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
