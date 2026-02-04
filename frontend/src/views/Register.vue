<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Registrierung anfragen</h1>
      <p class="subtitle">Trage deine E-Mail ein und beschreibe kurz, wer du bist. Das Team prueft deine Anfrage.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          E-Mail
          <input
            :class="['input', { invalid: touched.email && emailError }]"
            v-model.trim="form.email"
            placeholder="du@example.com"
            autocomplete="email"
            @blur="markTouched('email')"
          />
          <small v-if="touched.email && emailError" class="hint error">{{ emailError }}</small>
        </label>

        <label>
          Kurzbeschreibung
          <textarea
            :class="['input', 'textarea', { invalid: touched.description && descriptionError }]"
            v-model.trim="form.description"
            placeholder="Erzaehl kurz, welche Rolle du hast und was du suchst."
            rows="4"
            @blur="markTouched('description')"
          ></textarea>
          <small class="hint muted">Die Beschreibung ist nur fuer Team/Admin sichtbar.</small>
          <small v-if="touched.description && descriptionError" class="hint error">{{ descriptionError }}</small>
        </label>

        <button class="btn" type="submit" :disabled="!canSubmit">
          {{ loading ? "Sende..." : "Anfrage senden" }}
        </button>
      </form>

      <p v-if="message" :class="['feedback', messageType]">{{ message }}</p>
      <p class="switch">
        Bereits registriert?
        <router-link to="/login">Zum Login</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import api from "../api";

const form = ref({
  email: "",
  description: "",
});

const touched = ref({
  email: false,
  description: false,
});

const loading = ref(false);
const message = ref("");
const messageType = ref("info");

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const emailError = computed(() => {
  const value = form.value.email.trim();
  if (!value) return "E-Mail wird benoetigt.";
  if (!emailPattern.test(value)) return "Bitte gueltige E-Mail eingeben.";
  return "";
});

const descriptionError = computed(() => {
  const value = form.value.description.trim();
  if (!value) return "Beschreibung wird benoetigt.";
  if (value.length < 10) return "Bitte etwas ausfuehrlicher beschreiben.";
  return "";
});

const canSubmit = computed(() => !loading.value && !emailError.value && !descriptionError.value);

function markTouched(field) {
  touched.value[field] = true;
}

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

async function submit() {
  ["email", "description"].forEach((field) => markTouched(field));
  if (!canSubmit.value) {
    showMessage("Bitte korrigiere die markierten Felder.", "error");
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    await api.post("register/", {
      email: form.value.email.trim(),
      description: form.value.description.trim(),
    });
    showMessage("Danke! Wir pruefen deine Anfrage und melden uns per E-Mail.", "success");
    form.value = { email: "", description: "" };
    touched.value = { email: false, description: false };
  } catch (err) {
    const detail = err?.response?.data?.detail || "Anfrage konnte nicht gesendet werden.";
    showMessage(detail, "error");
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
.textarea {
  min-height: 110px;
  resize: vertical;
}
.input.invalid {
  border-color: #f97316;
}
.hint {
  font-size: 12px;
  margin-top: 4px;
  display: inline-block;
}
.hint.error {
  color: #f97316;
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
