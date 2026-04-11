<template>
  <div class="finance-tool">
    <h2>Finanzplaner</h2>
    <p>Umfassende Verwaltung deiner Finanzen</p>
    
    <div class="tabs">
      <button @click="activeTab = 'dashboard'" :class="{ active: activeTab === 'dashboard' }">Dashboard</button>
      <button @click="activeTab = 'income'" :class="{ active: activeTab === 'income' }">Einnahmen</button>
      <button @click="activeTab = 'expenses'" :class="{ active: activeTab === 'expenses' }">Ausgaben</button>
      <button @click="activeTab = 'debt'" :class="{ active: activeTab === 'debt' }">Schulden</button>
      <button @click="activeTab = 'budget'" :class="{ active: activeTab === 'budget' }">Budget</button>
    </div>

    <div class="tab-content">
      <p>Die vollständige Finanzverwaltung wird bald verfügbar sein.</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

const activeTab = ref('dashboard');
</script>

<style scoped>
.finance-tool {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.tabs button {
  padding: 10px 20px;
  border: 1px solid var(--border);
  background: var(--surface);
  color: var(--text);
  cursor: pointer;
  border-radius: 6px;
}

.tabs button.active {
  background: var(--brand);
  color: white;
}

.tab-content {
  padding: 20px;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--card);
}
</style>
