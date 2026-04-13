<template>
  <div class="admin-invitations">
    <header>
      <h2>Eingeladene Nutzer</h2>
      <p class="muted small">Verwalte eingeladene Nutzer und deren Onboarding-Status</p>
    </header>

    <section v-if="loading" class="loading">
      <p class="muted">Laden...</p>
    </section>

    <section v-else-if="invitations.length === 0" class="empty">
      <p class="muted">Keine eingeladenen Nutzer</p>
    </section>

    <section v-else class="table-shell">
      <div class="table-container">
        <table class="invitations-table">
          <thead>
            <tr>
              <th>E-Mail</th>
              <th>Status</th>
              <th>Eingeladen am</th>
              <th>Link geöffnet</th>
              <th>Aktionen</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="invitation in invitations" :key="invitation.id" :class="`status-${invitation.status.toLowerCase()}`">
              <td class="email">
                <strong>{{ invitation.email }}</strong>
              </td>
              <td class="status">
                <span class="badge" :class="`badge-${statusClassMap[invitation.status]}`">
                  {{ statusLabelMap[invitation.status] }}
                </span>
              </td>
              <td class="date">
                <span class="muted small">{{ formatDate(invitation.created_at) }}</span>
              </td>
              <td class="link-opened">
                <span v-if="invitation.link_opened_at" class="muted small">
                  {{ formatDate(invitation.link_opened_at) }}
                </span>
                <span v-else class="muted tiny">Nicht geöffnet</span>
              </td>
              <td class="actions">
                <button v-if="invitation.status === 'OPEN'" class="btn tiny" @click="resendInvite(invitation)">
                  Erneut senden
                </button>
                <button v-if="invitation.status !== 'REJECTED'" class="btn tiny ghost danger" @click="rejectInvite(invitation)">
                  Ablehnen
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../../api";
import { useToast } from "../../composables/useToast";

const { showToast } = useToast();
const invitations = ref([]);
const loading = ref(false);

const statusLabelMap = {
  OPEN: "Offen",
  INVITED: "Eingeladen",
  REJECTED: "Abgelehnt",
};

const statusClassMap = {
  OPEN: "warning",
  INVITED: "info",
  REJECTED: "danger",
};

onMounted(async () => {
  await loadInvitations();
});

async function loadInvitations() {
  loading.value = true;
  try {
    const { data } = await api.get("registration-requests/");
    const normalized = data.results || data.items || [];
    invitations.value = Array.isArray(normalized) ? normalized : [];
  } catch (err) {
    console.error("Invitations could not be loaded", err);
    showToast("Einladungen konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function resendInvite(invitation) {
  if (!confirm(`Einladung an ${invitation.email} erneut senden?`)) return;
  
  try {
    await api.post(`registration-requests/${invitation.id}/resend-invite/`);
    showToast("Einladung erneut versendet", "success");
    await loadInvitations();
  } catch (err) {
    console.error("Invite could not be resent", err);
    showToast("Einladung konnte nicht erneut versendet werden", "error");
  }
}

async function rejectInvite(invitation) {
  if (!confirm(`Einladung für ${invitation.email} ablehnen?`)) return;
  
  try {
    await api.patch(`registration-requests/${invitation.id}/`, { status: "REJECTED" });
    showToast("Einladung abgelehnt", "success");
    await loadInvitations();
  } catch (err) {
    console.error("Invite could not be rejected", err);
    showToast("Einladung konnte nicht abgelehnt werden", "error");
  }
}

function formatDate(dateStr) {
  if (!dateStr) return "-";
  const date = new Date(dateStr);
  return date.toLocaleDateString("de-DE", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>

<style scoped>
.admin-invitations {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.loading,
.empty {
  padding: 32px 16px;
  text-align: center;
  color: var(--color-muted);
  background: var(--color-bg-secondary);
  border-radius: 8px;
}

.table-shell {
  background: var(--color-bg-secondary);
  border-radius: 8px;
  overflow: hidden;
}

.table-container {
  overflow-x: auto;
}

.invitations-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.invitations-table thead {
  background: var(--color-bg-primary);
  border-bottom: 2px solid var(--color-border);
}

.invitations-table th {
  padding: 12px 16px;
  text-align: left;
  font-weight: 600;
  color: var(--color-text-secondary);
  text-transform: uppercase;
  font-size: 12px;
  letter-spacing: 0.05em;
}

.invitations-table td {
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  vertical-align: middle;
}

.invitations-table tbody tr:hover {
  background: var(--color-bg-primary);
}

.email {
  font-weight: 500;
}

.status {
  text-align: center;
}

.date,
.link-opened {
  white-space: nowrap;
}

.actions {
  display: flex;
  gap: 6px;
  justify-content: flex-end;
  white-space: nowrap;
}

.actions .btn {
  font-size: 12px;
  padding: 4px 10px;
}

.badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.badge-warning {
  background: rgba(251, 191, 36, 0.15);
  color: #92400e;
}

.badge-info {
  background: rgba(59, 130, 246, 0.15);
  color: #1d4ed8;
}

.badge-danger {
  background: rgba(248, 113, 113, 0.15);
  color: #b91c1c;
}

@media (max-width: 768px) {
  .invitations-table {
    font-size: 12px;
  }

  .invitations-table th,
  .invitations-table td {
    padding: 8px 12px;
  }

  .actions {
    flex-direction: column;
  }
}
</style>
