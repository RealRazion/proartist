<template>
  <div class="testing-page">
    <div class="page-header">
      <h1>🧪 Testing</h1>
      <p class="subtitle">Interne Tests für Backend-Funktionen</p>
    </div>

    <div class="test-cards">
      <!-- Email Test -->
      <div class="test-card">
        <div class="test-card-header">
          <span class="test-icon">📧</span>
          <div>
            <h2>E-Mail Test</h2>
            <p>Sendet eine Test-Email an deine hinterlegte E-Mail-Adresse.</p>
          </div>
        </div>
        <div class="test-card-body">
          <div v-if="emailResult" :class="['result-banner', emailResult.type]">
            {{ emailResult.message }}
          </div>
          <button class="btn-test" :disabled="emailLoading" @click="sendTestEmail">
            <span v-if="emailLoading" class="spinner" aria-hidden="true" />
            {{ emailLoading ? "Wird gesendet…" : "Test-Email senden" }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";
import api from "../api";
import { useToast } from "../composables/useToast";

const { showToast } = useToast();

const emailLoading = ref(false);
const emailResult = ref(null);

async function sendTestEmail() {
  emailLoading.value = true;
  emailResult.value = null;
  try {
    const res = await api.post("testing/send-email/");
    emailResult.value = { type: "success", message: res.data.message };
    showToast(res.data.message, "success");
  } catch (err) {
    const msg = err.response?.data?.detail || "E-Mail konnte nicht gesendet werden.";
    emailResult.value = { type: "error", message: msg };
    showToast(msg, "error");
  } finally {
    emailLoading.value = false;
  }
}
</script>

<style scoped>
.testing-page {
  max-width: 760px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: var(--text);
  margin: 0 0 0.25rem;
}

.subtitle {
  color: var(--muted);
  margin: 0;
}

.test-cards {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.test-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.5rem;
}

.test-card-header {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.test-icon {
  font-size: 2rem;
  line-height: 1;
  flex-shrink: 0;
}

.test-card-header h2 {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--text);
  margin: 0 0 0.25rem;
}

.test-card-header p {
  color: var(--muted);
  margin: 0;
  font-size: 0.9rem;
}

.test-card-body {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.result-banner {
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
}

.result-banner.success {
  background: color-mix(in srgb, #10b981 15%, transparent);
  color: #10b981;
  border: 1px solid color-mix(in srgb, #10b981 30%, transparent);
}

.result-banner.error {
  background: color-mix(in srgb, #ef4444 15%, transparent);
  color: #ef4444;
  border: 1px solid color-mix(in srgb, #ef4444 30%, transparent);
}

.btn-test {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.25rem;
  background: var(--brand);
  color: #fff;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.15s;
  align-self: flex-start;
}

.btn-test:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255, 255, 255, 0.4);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  display: inline-block;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
