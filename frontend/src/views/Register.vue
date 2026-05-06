<template>
  <div class="auth-page">
    <div class="card auth-card">

      <!-- Step 1: Email + Description -->
      <template v-if="step === 1">
        <h1>Registrierung</h1>
        <p class="subtitle">
          Trage deine E-Mail und eine kurze Beschreibung ein. Wir senden dir einen Bestätigungscode.
        </p>

        <form class="auth-form" @submit.prevent="submitEmail">
          <label>
            E-Mail
            <input
              :class="['input', { invalid: touched.email && emailError }]"
              v-model.trim="form.email"
              placeholder="du@example.com"
              autocomplete="email"
              type="email"
              @blur="markTouched('email')"
            />
            <small v-if="touched.email && emailError" class="hint error">{{ emailError }}</small>
          </label>

          <label>
            Kurzbeschreibung
            <textarea
              :class="['input', 'textarea', { invalid: touched.description && descriptionError }]"
              v-model.trim="form.description"
              placeholder="Erzähl kurz, wer du bist und was du suchst."
              rows="4"
              @blur="markTouched('description')"
            ></textarea>
            <small v-if="touched.description && descriptionError" class="hint error">{{ descriptionError }}</small>
          </label>

          <button class="btn" type="submit" :disabled="!canSubmitEmail || loading">
            {{ loading ? "Sende Code…" : "Code anfordern" }}
          </button>
        </form>
      </template>

      <!-- Step 2: Code Input -->
      <template v-if="step === 2">
        <h1>Code bestätigen</h1>
        <p class="subtitle">
          Wir haben einen 6-stelligen Code an <strong>{{ form.email }}</strong> gesendet.
          Gib ihn hier ein.
        </p>

        <form class="auth-form" @submit.prevent="submitCode">
          <label>
            Bestätigungscode
            <input
              class="input code-input"
              v-model.trim="code"
              placeholder="123456"
              maxlength="6"
              inputmode="numeric"
              autocomplete="one-time-code"
            />
          </label>

          <button class="btn" type="submit" :disabled="code.length < 6 || loading">
            {{ loading ? "Prüfe Code…" : "Bestätigen" }}
          </button>

          <button type="button" class="btn-link" @click="resendCode" :disabled="resendCooldown > 0">
            {{ resendCooldown > 0 ? `Erneut senden in ${resendCooldown}s` : "Code erneut senden" }}
          </button>
        </form>
      </template>

      <!-- Step 3: Success -->
      <template v-if="step === 3">
        <div class="success-state">
          <div class="success-icon">✅</div>
          <h1>Account erstellt!</h1>
          <p class="subtitle">
            Dein Benutzername ist <strong>{{ username }}</strong>.<br/>
            Wir haben dir einen Link geschickt, um dein Passwort zu setzen. Bitte prüfe dein Postfach.
          </p>
          <router-link class="btn" to="/login">Zum Login</router-link>
        </div>
      </template>

      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>

      <p v-if="step < 3" class="switch">
        Bereits registriert?
        <router-link to="/login">Zum Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from "vue";
import api from "../api";

const step = ref(1);
const loading = ref(false);
const message = ref("");
const messageType = ref("info");
const code = ref("");
const username = ref("");
const resendCooldown = ref(0);
let cooldownTimer = null;

const form = ref({ email: "", description: "" });
const touched = ref({ email: false, description: false });

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const emailError = computed(() => {
  const v = form.value.email.trim();
  if (!v) return "E-Mail wird benötigt.";
  if (!emailPattern.test(v)) return "Bitte gültige E-Mail eingeben.";
  return "";
});

const descriptionError = computed(() => {
  const v = form.value.description.trim();
  if (!v) return "Beschreibung wird benötigt.";
  if (v.length < 10) return "Bitte etwas ausführlicher beschreiben.";
  return "";
});

const canSubmitEmail = computed(() => !emailError.value && !descriptionError.value);

function markTouched(field) {
  touched.value[field] = true;
}

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

function startCooldown(seconds = 60) {
  resendCooldown.value = seconds;
  cooldownTimer = setInterval(() => {
    resendCooldown.value--;
    if (resendCooldown.value <= 0) {
      clearInterval(cooldownTimer);
    }
  }, 1000);
}

async function submitEmail() {
  ["email", "description"].forEach((f) => markTouched(f));
  if (!canSubmitEmail.value) return;
  loading.value = true;
  showMessage("");
  try {
    await api.post("register/", {
      email: form.value.email.trim(),
      description: form.value.description.trim(),
    });
    step.value = 2;
    startCooldown(60);
    showMessage("");
  } catch (err) {
    const detail = err?.response?.data?.detail || "Anfrage konnte nicht gesendet werden.";
    showMessage(detail, "error");
  } finally {
    loading.value = false;
  }
}

async function resendCode() {
  if (resendCooldown.value > 0) return;
  loading.value = true;
  showMessage("");
  try {
    await api.post("register/", {
      email: form.value.email.trim(),
      description: form.value.description.trim(),
    });
    showMessage("Neuer Code gesendet.", "info");
    startCooldown(60);
  } catch (err) {
    showMessage("Code konnte nicht gesendet werden.", "error");
  } finally {
    loading.value = false;
  }
}

async function submitCode() {
  if (code.value.length < 6) return;
  loading.value = true;
  showMessage("");
  try {
    const res = await api.post("verify-registration/", {
      email: form.value.email.trim(),
      code: code.value.trim(),
    });
    username.value = res.data.username || "Nutzer";
    step.value = 3;
  } catch (err) {
    const detail = err?.response?.data?.detail || "Code ungültig oder abgelaufen.";
    showMessage(detail, "error");
  } finally {
    loading.value = false;
  }
}

onUnmounted(() => {
  if (cooldownTimer) clearInterval(cooldownTimer);
});
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
  max-width: 520px;
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
  gap: 16px;
}
label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-weight: 600;
  color: var(--text);
}
.textarea {
  min-height: 110px;
  resize: vertical;
}
.code-input {
  font-size: 1.5rem;
  letter-spacing: 0.4em;
  text-align: center;
  font-weight: 700;
}
.input.invalid {
  border-color: #f97316;
}
.hint {
  font-size: 12px;
  margin-top: 4px;
  display: inline-block;
}
.hint.error { color: #f97316; }
.feedback {
  margin: 0;
  font-size: 14px;
  text-align: center;
}
.feedback.error { color: #f87171; }
.feedback.info { color: #93c5fd; }
.feedback.success { color: #34d399; }
.switch {
  text-align: center;
  margin-top: -6px;
  color: var(--muted);
}
.btn-link {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 0.875rem;
  cursor: pointer;
  text-align: center;
  padding: 4px;
  text-decoration: underline;
}
.btn-link:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  text-decoration: none;
}
.success-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  text-align: center;
  padding: 16px 0;
}
.success-icon {
  font-size: 3rem;
}
</style>

