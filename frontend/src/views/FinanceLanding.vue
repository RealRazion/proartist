<template>
  <div class="platform-page finance-page">
    <header class="page-hero card">
      <div>
        <p class="eyebrow">UNYQ Finance</p>
        <h1>Finanzielle Freiheit erreichen</h1>
        <p class="lead">
          Ein umfassendes Finanzmanagement-Tool für Einnahmen, Ausgaben, Schulden und Budgetplanung.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="goHome">Zurück zum Hub</button>
        <button class="btn secondary" type="button" @click="goToTool">Zum Finanzplaner</button>
      </div>
    </header>

    <section class="highlights card">
      <article>
        <h2>Einnahmen & Ausgaben</h2>
        <p>Verfolge regelmäßige und einmalige Einnahmen sowie alle Arten von Ausgaben.</p>
      </article>
      <article>
        <h2>Schuldenmanagement</h2>
        <p>Behalte Schulden, Ratenzahlungen und Tilgungspläne im Blick.</p>
      </article>
      <article>
        <h2>Budgetplanung</h2>
        <p>Erstelle monatliche Budgets und verfolge deine finanziellen Ziele.</p>
      </article>
    </section>

    <section class="cards-grid">
      <article class="card feature-card income">
        <h3>Einnahmen-Tracker</h3>
        <p>Regelmäßige Gehälter, Freelance-Jobs, einmalige Zahlungen und mehr.</p>
      </article>
      <article class="card feature-card expenses">
        <h3>Ausgaben-Kategorien</h3>
        <p>Fixe Kosten, Abos, variable Ausgaben und Ratenzahlungen.</p>
      </article>
      <article class="card feature-card debt">
        <h3>Schulden-Übersicht</h3>
        <p>Verfolge Tilgungsfortschritt und plane deine Schuldenfreiheit.</p>
      </article>
      <article class="card feature-card budget">
        <h3>Budget-Planer</h3>
        <p>Setze Sparziele und überwache deine monatlichen Budgets.</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
const router = useRouter();

function goHome() {
  router.push({ name: "platforms" });
}

function goToTool() {
  router.push({ name: "finance" });
}
</script>

<style scoped>
.platform-page {
  display: grid;
  gap: 20px;
}
.page-hero {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 28px;
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.14), rgba(52, 211, 153, 0.12));
  border: 1px solid rgba(52, 211, 153, 0.24);
}
.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.18em;
  font-size: 12px;
  margin-bottom: 8px;
  color: var(--brand);
}
.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}
.hero-actions {
  display: grid;
  gap: 10px;
  align-items: center;
}
.highlights {
  display: grid;
  gap: 14px;
  padding: 20px;
}
.highlights article {
  padding: 18px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid rgba(15, 23, 42, 0.08);
}
.cards-grid {
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}
.feature-card {
  padding: 24px;
  border-radius: 20px;
  background: var(--surface);
  border: 1px solid var(--border);
}
.feature-card.income {
  background: rgba(34, 197, 94, 0.08);
}
.feature-card.expenses {
  background: rgba(239, 68, 68, 0.08);
}
.feature-card.debt {
  background: rgba(245, 158, 11, 0.08);
}
.feature-card.budget {
  background: rgba(59, 130, 246, 0.08);
}
.btn.secondary {
  background: rgba(255, 255, 255, 0.9);
  color: var(--text);
  border: 1px solid var(--border);
}
.btn.secondary:hover {
  background: var(--surface);
}
</style>