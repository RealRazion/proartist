<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Konto erstellen</h1>
      <p class="subtitle">Registriere dich und werde Teil der ProArtist Community.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Benutzername
          <input
            class="input"
            v-model.trim="form.username"
            placeholder="z. B. beatmaster"
            autocomplete="username"
          />
        </label>

        <label>
          E-Mail
          <input
            class="input"
            v-model.trim="form.email"
            placeholder="du@example.com"
            autocomplete="email"
            :class="{ invalid: emailTouched && !isEmailValid }"
            @blur="emailTouched = true"
          />
          <small v-if="emailTouched && !isEmailValid" class="hint error">Bitte gueltige E-Mail angeben.</small>
        </label>

        <label>
          Passwort
          <input
            class="input"
            v-model.trim="form.password"
            type="password"
            placeholder="Mindestens 8 Zeichen"
            autocomplete="new-password"
            :class="{ invalid: passwordTouched && passwordScore < 3 }"
            @input="handlePasswordInput"
            @blur="passwordTouched = true"
          />
        </label>
        <p class="password-strength" :data-score="passwordScore">{{ passwordStrengthText }}</p>
        <ul class="password-rules">
          <li
            v-for="rule in passwordRules"
            :key="rule.key"
            :class="{ ok: passwordChecks[rule.key] }"
          >
            {{ rule.label }}
          </li>
        </ul>

        <div>
          <p class="roles-title">Ich bin ...</p>
          <div class="roles">
            <label v-for="role in roles" :key="role.id" class="role-option">
              <input type="checkbox" :value="role.key" v-model="form.roles" />
              {{ labelForRole(role.key) }}
            </label>
          </div>
        </div>

        <button class="btn" type="submit" :disabled="loading || !canSubmit">
          {{ loading ? "Registrieren..." : "Konto erstellen" }}
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
import { ref, onMounted, computed } from "vue";
import { useRouter } from "vue-router";
import api from "../api";

const router = useRouter();

const roles = ref([]);
const form = ref({
  username: "",
  email: "",
  password: "",
  roles: [],
});
const loading = ref(false);
const message = ref("");
const messageType = ref("info");
const emailTouched = ref(false);
const passwordTouched = ref(false);

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const passwordRules = [
  { key: "length", label: "Mindestens 8 Zeichen" },
  { key: "upper", label: "Ein Grossbuchstabe" },
  { key: "lower", label: "Ein Kleinbuchstabe" },
  { key: "number", label: "Eine Zahl" },
];

const isEmailValid = computed(() => emailPattern.test((form.value.email || "").trim()));

const passwordChecks = computed(() => {
  const value = form.value.password || "";
  return {
    length: value.length >= 8,
    upper: /[A-Z]/.test(value),
    lower: /[a-z]/.test(value),
    number: /\d/.test(value),
  };
});

const passwordScore = computed(() => Object.values(passwordChecks.value).filter(Boolean).length);

const passwordStrengthText = computed(() => {
  const score = passwordScore.value;
  if (!form.value.password) return "Noch kein Passwort eingegeben";
  if (score <= 1) return "Passwort ist sehr schwach";
  if (score === 2) return "Passwort ist mittel";
  if (score === 3) return "Passwort ist gut";
  return "Passwort ist stark";
});

const canSubmit = computed(() => {
  return (
    form.value.username.trim().length > 0 &&
    isEmailValid.value &&
    passwordScore.value >= 3
  );
});

function labelForRole(key) {
  const map = {
    ARTIST: "Artist / Saenger*in",
    PROD: "Producer",
    VIDEO: "Videograf*in",
    MERCH: "Merchandiser",
    MKT: "Marketing / Management",
    LOC: "Location",
    TEAM: "Team / Admin",
  };
  return map[key] || key;
}

function showMessage(text, type = "info") {
  message.value = text;
  messageType.value = type;
}

function handlePasswordInput() {
  passwordTouched.value = true;
}

async function loadRoles() {
  try {
    const { data } = await api.get("roles/");
    roles.value = data;
  } catch (err) {
    console.error("Rollen konnten nicht geladen werden", err);
    roles.value = [
      { id: "ARTIST", key: "ARTIST" },
      { id: "PROD", key: "PROD" },
      { id: "VIDEO", key: "VIDEO" },
      { id: "MERCH", key: "MERCH" },
      { id: "MKT", key: "MKT" },
      { id: "LOC", key: "LOC" },
    ];
  }
}

async function submit() {
  if (!form.value.username || !form.value.password) {
    showMessage("Bitte Benutzername und Passwort ausfuellen.", "error");
    return;
  }
  if (!isEmailValid.value) {
    showMessage("Bitte eine gueltige E-Mail-Adresse eingeben.", "error");
    emailTouched.value = true;
    return;
  }
  if (!canSubmit.value) {
    showMessage("Passwort nicht stark genug.", "error");
    passwordTouched.value = true;
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    await api.post("register/", form.value);
    showMessage("Registrierung erfolgreich - bitte einloggen.", "success");
    setTimeout(() => router.replace({ name: "login" }), 600);
  } catch (err) {
    console.error(err);
    const detail = err?.response?.data?.error || "Registrierung fehlgeschlagen.";
    showMessage(detail, "error");
  } finally {
    loading.value = false;
  }
}

onMounted(loadRoles);
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
.roles-title {
  margin: 0 0 10px;
  font-weight: 600;
}
.roles {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 8px 12px;
}
.role-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
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
.password-strength {
  font-size: 13px;
  margin: 4px 0;
  color: var(--muted);
}
.password-rules {
  list-style: none;
  padding: 0;
  margin: 0 0 8px;
  display: grid;
  gap: 4px;
}
.password-rules li {
  font-size: 12px;
  color: var(--muted);
}
.password-rules li.ok {
  color: #22c55e;
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
