<template>
  <div class="api-center">
    <header class="card hero">
      <div>
        <p class="eyebrow">API</p>
        <h1>Automation & Integrationen</h1>
        <p class="muted">Verwalte Regeln und interne API-Keys fuer neue Systeme.</p>
      </div>
      <div class="mode-toggle">
        <button
          v-for="option in modeOptions"
          :key="option.key"
          class="chip"
          :class="{ active: mode === option.key }"
          type="button"
          @click="mode = option.key"
        >
          {{ option.label }}
        </button>
      </div>
    </header>

    <section v-if="!isTeam" class="card info">
      <h2>Zugriff nur fuer Team</h2>
      <p class="muted">Diese Seite ist nur fuer Team-Mitglieder sichtbar.</p>
    </section>

    <section v-else class="grid">
      <article class="card panel">
        <div class="panel-head">
          <div>
            <h2>System Integrationen</h2>
            <p class="muted small">Interne API-Keys und Scopes.</p>
          </div>
          <button class="btn ghost tiny" type="button" @click="loadIntegrations" :disabled="loadingIntegrations">
            {{ loadingIntegrations ? "Lade..." : "Neu laden" }}
          </button>
        </div>

        <div class="form">
          <h3>Neue Integration</h3>
          <div class="form-grid">
            <label>
              Name
              <input class="input" v-model.trim="integrationForm.name" placeholder="z. B. PA-Automation" />
            </label>
            <label>
              Slug
              <input class="input" v-model.trim="integrationForm.slug" placeholder="pa-automation" />
            </label>
            <label class="full">
              Scopes
              <input
                v-if="mode === 'simple'"
                class="input"
                v-model.trim="integrationForm.scopes"
                placeholder="tasks.read, tasks.write"
              />
              <textarea
                v-else
                class="input textarea"
                v-model.trim="integrationForm.scopes"
                placeholder='["tasks.read", "tasks.write"]'
              ></textarea>
            </label>
          </div>
          <div class="actions">
            <button class="btn" type="button" @click="createIntegration">Integration anlegen</button>
          </div>
        </div>

        <div class="list">
          <article v-for="integration in integrations" :key="integration.id" class="list-item">
            <div>
              <strong>{{ integration.name }}</strong>
              <p class="muted small">Slug: {{ integration.slug }}</p>
              <p class="muted tiny">Scopes: {{ formatScopes(integration.scopes) }}</p>
            </div>
            <div class="item-actions">
              <button class="btn ghost tiny" type="button" @click="toggleIntegration(integration)">
                {{ integration.is_active ? "Deaktivieren" : "Aktivieren" }}
              </button>
              <button class="btn ghost tiny" type="button" @click="toggleKey(integration.id)">
                {{ showKeys[integration.id] ? "Key verbergen" : "Key anzeigen" }}
              </button>
            </div>
            <p v-if="showKeys[integration.id]" class="api-key">{{ integration.api_key }}</p>
          </article>
          <p v-if="!integrations.length" class="muted small">Keine Integrationen vorhanden.</p>
        </div>
      </article>

      <article class="card panel">
        <div class="panel-head">
          <div>
            <h2>Automation Rules</h2>
            <p class="muted small">Regeln fuer interne Automationen.</p>
          </div>
          <button class="btn ghost tiny" type="button" @click="loadRules" :disabled="loadingRules">
            {{ loadingRules ? "Lade..." : "Neu laden" }}
          </button>
        </div>

        <div class="form">
          <h3>Neue Regel</h3>
          <div class="form-grid">
            <label>
              Name
              <input class="input" v-model.trim="ruleForm.name" placeholder="z. B. Review Reminder" />
            </label>
            <label>
              Trigger
              <select class="input" v-model="ruleForm.trigger">
                <option v-for="opt in triggerOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
            </label>
            <label>
              Action
              <select class="input" v-model="ruleForm.action">
                <option v-for="opt in actionOptions" :key="opt" :value="opt">{{ opt }}</option>
              </select>
            </label>
            <label class="full" v-if="mode === 'complex'">
              Config (JSON)
              <textarea
                class="input textarea"
                v-model.trim="ruleForm.config"
                placeholder='{"channel":"email"}'
              ></textarea>
            </label>
          </div>
          <div class="actions">
            <button class="btn" type="button" @click="createRule">Regel anlegen</button>
          </div>
        </div>

        <div class="list">
          <article v-for="rule in rules" :key="rule.id" class="list-item">
            <div>
              <strong>{{ rule.name }}</strong>
              <p class="muted small">{{ rule.trigger }} → {{ rule.action }}</p>
              <p v-if="mode === 'complex'" class="muted tiny">Config: {{ formatConfig(rule.config) }}</p>
            </div>
            <div class="item-actions">
              <button class="btn ghost tiny" type="button" @click="toggleRule(rule)">
                {{ rule.is_active ? "Deaktivieren" : "Aktivieren" }}
              </button>
            </div>
          </article>
          <p v-if="!rules.length" class="muted small">Keine Regeln vorhanden.</p>
        </div>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const { isTeam } = useCurrentProfile();
const { showToast } = useToast();

const mode = ref("simple");
const modeOptions = [
  { key: "simple", label: "Einfach" },
  { key: "complex", label: "Komplex" },
];

const integrations = ref([]);
const rules = ref([]);
const loadingIntegrations = ref(false);
const loadingRules = ref(false);
const showKeys = ref({});

const integrationForm = ref({ name: "", slug: "", scopes: "" });
const ruleForm = ref({ name: "", trigger: "TASK_STATUS", action: "NOTIFY", config: "{}" });

const triggerOptions = ["TASK_STATUS", "TASK_DUE", "GROWPRO_DUE", "PROJECT_STATUS"];
const actionOptions = ["NOTIFY", "ASSIGN", "WEBHOOK"];

function toggleKey(id) {
  showKeys.value = { ...showKeys.value, [id]: !showKeys.value[id] };
}

function formatScopes(scopes) {
  if (!scopes || !scopes.length) return "-";
  return Array.isArray(scopes) ? scopes.join(", ") : String(scopes);
}

function formatConfig(config) {
  if (!config) return "{}";
  try {
    return JSON.stringify(config);
  } catch (err) {
    return String(config);
  }
}

function parseScopes() {
  if (mode.value === "simple") {
    return integrationForm.value.scopes
      .split(",")
      .map((entry) => entry.trim())
      .filter(Boolean);
  }
  try {
    const parsed = JSON.parse(integrationForm.value.scopes || "[]");
    if (Array.isArray(parsed)) return parsed;
  } catch (err) {
    showToast("Scopes JSON ist ungueltig", "error");
  }
  return [];
}

function parseConfig() {
  if (mode.value === "simple") return {};
  try {
    return JSON.parse(ruleForm.value.config || "{}");
  } catch (err) {
    showToast("Config JSON ist ungueltig", "error");
    return null;
  }
}

async function loadIntegrations() {
  if (!isTeam.value) return;
  loadingIntegrations.value = true;
  try {
    const { data } = await api.get("system-integrations/");
    integrations.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Integrationen konnten nicht geladen werden", err);
    showToast("Integrationen konnten nicht geladen werden", "error");
  } finally {
    loadingIntegrations.value = false;
  }
}

async function loadRules() {
  if (!isTeam.value) return;
  loadingRules.value = true;
  try {
    const { data } = await api.get("automation-rules/");
    rules.value = Array.isArray(data) ? data : data.results || [];
  } catch (err) {
    console.error("Automation Rules konnten nicht geladen werden", err);
    showToast("Automation Rules konnten nicht geladen werden", "error");
  } finally {
    loadingRules.value = false;
  }
}

async function createIntegration() {
  if (!integrationForm.value.name || !integrationForm.value.slug) {
    showToast("Name und Slug sind Pflicht", "error");
    return;
  }
  const scopes = parseScopes();
  try {
    const { data } = await api.post("system-integrations/", {
      name: integrationForm.value.name,
      slug: integrationForm.value.slug,
      scopes,
      is_active: true,
    });
    integrations.value = [data, ...integrations.value];
    integrationForm.value = { name: "", slug: "", scopes: "" };
    showToast("Integration angelegt", "success");
  } catch (err) {
    console.error("Integration konnte nicht angelegt werden", err);
    showToast("Integration konnte nicht angelegt werden", "error");
  }
}

async function createRule() {
  if (!ruleForm.value.name) {
    showToast("Name ist Pflicht", "error");
    return;
  }
  const config = parseConfig();
  if (config === null) return;
  try {
    const { data } = await api.post("automation-rules/", {
      name: ruleForm.value.name,
      trigger: ruleForm.value.trigger,
      action: ruleForm.value.action,
      config,
      is_active: true,
    });
    rules.value = [data, ...rules.value];
    ruleForm.value = { name: "", trigger: "TASK_STATUS", action: "NOTIFY", config: "{}" };
    showToast("Regel angelegt", "success");
  } catch (err) {
    console.error("Regel konnte nicht angelegt werden", err);
    showToast("Regel konnte nicht angelegt werden", "error");
  }
}

async function toggleIntegration(integration) {
  try {
    const { data } = await api.patch(`system-integrations/${integration.id}/`, {
      is_active: !integration.is_active,
    });
    integration.is_active = data.is_active;
  } catch (err) {
    console.error("Integration konnte nicht aktualisiert werden", err);
    showToast("Integration konnte nicht aktualisiert werden", "error");
  }
}

async function toggleRule(rule) {
  try {
    const { data } = await api.patch(`automation-rules/${rule.id}/`, {
      is_active: !rule.is_active,
    });
    rule.is_active = data.is_active;
  } catch (err) {
    console.error("Regel konnte nicht aktualisiert werden", err);
    showToast("Regel konnte nicht aktualisiert werden", "error");
  }
}

onMounted(() => {
  loadIntegrations();
  loadRules();
});
</script>

<style scoped>
.api-center {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  flex-wrap: wrap;
}
.mode-toggle {
  display: inline-flex;
  gap: 6px;
  padding: 4px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(15, 23, 42, 0.03);
}
.mode-toggle .chip {
  border: none;
  border-radius: 999px;
  padding: 6px 14px;
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  background: transparent;
}
.mode-toggle .chip.active {
  background: rgba(99, 102, 241, 0.12);
  color: #4338ca;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 18px;
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.form {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  background: rgba(15, 23, 42, 0.03);
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}
.form-grid .full {
  grid-column: 1 / -1;
}
.actions {
  display: flex;
  justify-content: flex-end;
}
.list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.list-item {
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 12px;
  background: var(--card);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.item-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.btn.tiny {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 10px;
}
.api-key {
  font-family: "JetBrains Mono", ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
  padding: 8px;
  border-radius: 10px;
  background: rgba(15, 23, 42, 0.06);
  word-break: break-all;
}
.textarea {
  min-height: 90px;
}
@media (max-width: 720px) {
  .hero {
    flex-direction: column;
    align-items: stretch;
  }
  .actions {
    justify-content: flex-start;
  }
}
</style>
