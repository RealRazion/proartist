<template>
  <div class="auth-page">
    <div class="card auth-card">
      <h1>Konto erstellen</h1>
      <p class="subtitle">Registriere dich und werde Teil der ProArtist Community.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          Benutzername
          <input
            :class="['input', { invalid: touched.username && usernameError }]"
            v-model.trim="form.username"
            placeholder="z. B. beatmaster"
            autocomplete="username"
            @blur="markTouched('username')"
          />
          <small v-if="touched.username && usernameError" class="hint error">{{ usernameError }}</small>
        </label>

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
          Passwort
          <input
            :class="['input', { invalid: touched.password && passwordError }]"
            v-model.trim="form.password"
            type="password"
            placeholder="Mindestens 8 Zeichen"
            autocomplete="new-password"
            @blur="markTouched('password')"
          />
          <div class="password-strength">
            <div class="bar">
              <div class="fill" :style="{ width: `${passwordStrength.percent}%` }" :data-strength="passwordStrength.level"></div>
            </div>
            <span class="strength-label">{{ passwordStrength.label }}</span>
          </div>
          <ul class="password-rules">
            <li v-for="rule in passwordRules" :key="rule.key" :class="{ ok: rule.ok }">{{ rule.label }}</li>
          </ul>
          <small v-if="touched.password && passwordError" class="hint error">{{ passwordError }}</small>
        </label>

        <div>
          <p class="roles-title">Ich bin ...</p>
          <div class="roles">
            <label v-for="role in roles" :key="role.id" class="role-option">
              <input type="checkbox" :value="role.key" v-model="form.roles" @change="markTouched('roles')" />
              {{ labelForRole(role.key) }}
            </label>
          </div>
          <small class="hint muted">Team-Mitgliedschaften werden intern vergeben.</small>
          <small v-if="touched.roles && rolesError" class="hint error">{{ rolesError }}</small>
        </div>

        <button class="btn" type="submit" :disabled="!canSubmit">
          {{ loading ? "Registriere..." : "Konto erstellen" }}
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
import { ref, computed, onMounted } from "vue";
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
const touched = ref({
  username: false,
  email: false,
  password: false,
  roles: false,
});
const loading = ref(false);
const message = ref("");
const messageType = ref("info");

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const usernameError = computed(() => {
  const value = form.value.username.trim();
  if (!value) return "Benutzername wird benoetigt.";
  if (value.length < 3) return "Mindestens 3 Zeichen.";
  if (!/^[a-zA-Z0-9._-]+$/.test(value)) return "Nur Buchstaben, Zahlen, Punkt, Unterstrich.";
  return "";
});

const emailError = computed(() => {
  const value = form.value.email.trim();
  if (!value) return "E-Mail wird benoetigt.";
  if (!emailPattern.test(value)) return "Bitte gueltige E-Mail eingeben.";
  return "";
});

const passwordRules = computed(() => {
  const value = form.value.password || "";
  return [
    { key: "length", label: "Mindestens 8 Zeichen", ok: value.length >= 8 },
    { key: "number", label: "Mindestens eine Zahl", ok: /\d/.test(value) },
    { key: "upper", label: "Mindestens ein Grossbuchstabe", ok: /[A-Z]/.test(value) },
    { key: "special", label: "Mindestens ein Sonderzeichen", ok: /[^A-Za-z0-9]/.test(value) },
  ];
});

const passwordError = computed(() => {
  if (!form.value.password) return "Passwort wird benoetigt.";
  const allRulesMet = passwordRules.value.every((rule) => rule.ok);
  return allRulesMet ? "" : "Passwort erfuellt noch nicht alle Regeln.";
});

const passwordStrength = computed(() => {
  const rules = passwordRules.value;
  const passed = rules.filter((rule) => rule.ok).length;
  const percent = form.value.password ? Math.round((passed / rules.length) * 100) : 0;
  let level = "weak";
  let label = "Sehr schwach";
  if (percent >= 75) {
    level = "strong";
    label = "Sehr stark";
  } else if (percent >= 50) {
    level = "ok";
    label = "Stark";
  } else if (percent >= 25) {
    level = "mid";
    label = "Mittel";
  }
  return { percent, level, label };
});

const rolesError = computed(() =>
  form.value.roles.length ? "" : "Bitte mindestens eine Rolle auswaehlen."
);

const canSubmit = computed(
  () =>
    !loading.value &&
    !usernameError.value &&
    !emailError.value &&
    !passwordError.value &&
    !rolesError.value
);

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

async function loadRoles() {
  try {
    const { data } = await api.get("roles/");
    roles.value = data.filter((role) => role.key !== "TEAM");
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

function markTouched(field) {
  touched.value[field] = true;
}

async function submit() {
  ["username", "email", "password", "roles"].forEach((field) => markTouched(field));
  if (!canSubmit.value) {
    showMessage("Bitte korrigiere die markierten Felder.", "error");
    return;
  }
  loading.value = true;
  showMessage("");
  try {
    const payload = {
      ...form.value,
      username: form.value.username.trim(),
      email: form.value.email.trim(),
    };
    await api.post("register/", payload);
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
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 6px 0 8px;
  font-size: 12px;
  color: var(--muted);
}
.password-strength .bar {
  flex: 1;
  height: 6px;
  border-radius: 999px;
  background: var(--border);
  overflow: hidden;
}
.password-strength .fill {
  height: 100%;
  border-radius: inherit;
  width: 0;
  background: #ef4444;
  transition: width 0.2s ease, background 0.2s ease;
}
.password-strength .fill[data-strength="mid"] {
  background: #f97316;
}
.password-strength .fill[data-strength="ok"] {
  background: #fbbf24;
}
.password-strength .fill[data-strength="strong"] {
  background: #22c55e;
}
.strength-label {
  min-width: 80px;
  text-align: right;
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
