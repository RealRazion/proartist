<template>
  <div class="finance-tool">
    <div class="finance-header">
      <h2>Finanzübersicht</h2>
      <p>Verwalte Einkommen, Ausgaben und Schulden für eine bessere finanzielle Planung.</p>
    </div>

    <div class="finance-grid">
      <!-- Einkommen Übersicht -->
      <div class="finance-card income-card">
        <div class="card-header">
          <h3>Einkommen</h3>
          <button class="btn small" @click="showIncomeModal = true">Hinzufügen</button>
        </div>
        <div class="income-list">
          <div v-for="income in incomes" :key="income.id" class="income-item">
            <div class="income-info">
              <strong>{{ income.name }}</strong>
              <span class="income-amount">{{ formatCurrency(income.amount) }}</span>
              <small v-if="income.frequency">{{ income.frequency }}</small>
            </div>
            <button class="btn ghost tiny" @click="editIncome(income)">Bearbeiten</button>
          </div>
        </div>
        <div class="total-income">
          <strong>Gesamt: {{ formatCurrency(totalIncome) }}</strong>
        </div>
      </div>

      <!-- Schulden Übersicht -->
      <div class="finance-card debt-card">
        <div class="card-header">
          <h3>Schulden</h3>
          <button class="btn small" @click="showDebtModal = true">Hinzufügen</button>
        </div>
        <div class="debt-list">
          <div v-for="debt in debts" :key="debt.id" class="debt-item" :class="{ 'paid-off': debt.paidOff }">
            <div class="debt-info">
              <strong>{{ debt.name }}</strong>
              <span class="debt-amount">{{ formatCurrency(debt.amount) }}</span>
              <small>Zins: {{ debt.interestRate }}%</small>
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: debtProgress(debt) + '%' }"></div>
              </div>
              <small>{{ formatCurrency(debt.paidAmount) }} / {{ formatCurrency(debt.amount) }}</small>
            </div>
            <div class="debt-actions">
              <button class="btn ghost tiny" @click="addPayment(debt)">Zahlung</button>
              <button class="btn ghost tiny" @click="editDebt(debt)">Bearbeiten</button>
            </div>
          </div>
        </div>
        <div class="total-debt">
          <strong>Gesamt Schulden: {{ formatCurrency(totalDebt) }}</strong>
          <br>
          <small>Bezahlt: {{ formatCurrency(totalPaid) }}</small>
        </div>
      </div>

      <!-- Kalender für Zahlungen -->
      <div class="finance-card calendar-card">
        <div class="card-header">
          <h3>Zahlungskalender</h3>
        </div>
        <div class="calendar">
          <div class="calendar-header">
            <button @click="prevMonth">&lt;</button>
            <h4>{{ currentMonthName }} {{ currentYear }}</h4>
            <button @click="nextMonth">&gt;</button>
          </div>
          <div class="calendar-grid">
            <div v-for="day in calendarDays" :key="day.date" class="calendar-day" :class="{ today: day.isToday, hasPayment: day.hasPayment }">
              <span>{{ day.day }}</span>
              <div v-if="day.payments" class="day-payments">
                <div v-for="payment in day.payments" :key="payment.id" class="payment-dot" :class="payment.type"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Statistiken -->
      <div class="finance-card stats-card">
        <div class="card-header">
          <h3>Statistiken</h3>
        </div>
        <div class="stats">
          <div class="stat-item">
            <span class="stat-label">Monatliches Einkommen</span>
            <span class="stat-value">{{ formatCurrency(monthlyIncome) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Monatliche Schuldenzahlungen</span>
            <span class="stat-value">{{ formatCurrency(monthlyDebtPayments) }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Verfügbares Budget</span>
            <span class="stat-value" :class="{ negative: monthlyIncome - monthlyDebtPayments < 0 }">
              {{ formatCurrency(monthlyIncome - monthlyDebtPayments) }}
            </span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Schuldenfrei in</span>
            <span class="stat-value">{{ debtFreeMonths }} Monaten</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showIncomeModal" class="modal-overlay" @click="showIncomeModal = false">
      <div class="modal" @click.stop>
        <h3>{{ editingIncome ? 'Einkommen bearbeiten' : 'Neues Einkommen' }}</h3>
        <form @submit.prevent="saveIncome">
          <div class="form-group">
            <label>Name</label>
            <input v-model="incomeForm.name" type="text" required>
          </div>
          <div class="form-group">
            <label>Betrag</label>
            <input v-model.number="incomeForm.amount" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Häufigkeit</label>
            <select v-model="incomeForm.frequency">
              <option value="">Einmalig</option>
              <option value="monatlich">Monatlich</option>
              <option value="wöchentlich">Wöchentlich</option>
              <option value="jährlich">Jährlich</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showIncomeModal = false">Abbrechen</button>
            <button type="submit" class="btn">Speichern</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showDebtModal" class="modal-overlay" @click="showDebtModal = false">
      <div class="modal" @click.stop>
        <h3>{{ editingDebt ? 'Schuld bearbeiten' : 'Neue Schuld' }}</h3>
        <form @submit.prevent="saveDebt">
          <div class="form-group">
            <label>Name</label>
            <input v-model="debtForm.name" type="text" required>
          </div>
          <div class="form-group">
            <label>Gesamtbetrag</label>
            <input v-model.number="debtForm.amount" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Zinssatz (%)</label>
            <input v-model.number="debtForm.interestRate" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Bereits bezahlt</label>
            <input v-model.number="debtForm.paidAmount" type="number" step="0.01">
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showDebtModal = false">Abbrechen</button>
            <button type="submit" class="btn">Speichern</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showPaymentModal" class="modal-overlay" @click="showPaymentModal = false">
      <div class="modal" @click.stop>
        <h3>Zahlung hinzufügen</h3>
        <form @submit.prevent="savePayment">
          <div class="form-group">
            <label>Betrag</label>
            <input v-model.number="paymentForm.amount" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Datum</label>
            <input v-model="paymentForm.date" type="date" required>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showPaymentModal = false">Abbrechen</button>
            <button type="submit" class="btn">Speichern</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';

// Reactive data
const incomes = ref([]);
const debts = ref([]);
const payments = ref([]);

const showIncomeModal = ref(false);
const showDebtModal = ref(false);
const showPaymentModal = ref(false);

const editingIncome = ref(null);
const editingDebt = ref(null);
const currentDebt = ref(null);

const incomeForm = ref({
  name: '',
  amount: 0,
  frequency: ''
});

const debtForm = ref({
  name: '',
  amount: 0,
  interestRate: 0,
  paidAmount: 0
});

const paymentForm = ref({
  amount: 0,
  date: new Date().toISOString().split('T')[0]
});

// Calendar
const currentDate = ref(new Date());

const currentMonthName = computed(() => {
  return currentDate.value.toLocaleDateString('de-DE', { month: 'long' });
});

const currentYear = computed(() => {
  return currentDate.value.getFullYear();
});

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month + 1, 0);
  const daysInMonth = lastDay.getDate();
  const startingDayOfWeek = firstDay.getDay() || 7; // 1 = Monday, 7 = Sunday

  const days = [];

  // Add empty cells for days before the first day of the month
  for (let i = 1; i < startingDayOfWeek; i++) {
    days.push({ day: '', date: null, isToday: false, hasPayment: false });
  }

  // Add days of the month
  for (let day = 1; day <= daysInMonth; day++) {
    const date = new Date(year, month, day);
    const isToday = date.toDateString() === new Date().toDateString();
    const dayPayments = payments.value.filter(p => {
      const paymentDate = new Date(p.date);
      return paymentDate.toDateString() === date.toDateString();
    });
    const hasPayment = dayPayments.length > 0;

    days.push({
      day,
      date,
      isToday,
      hasPayment,
      payments: dayPayments
    });
  }

  return days;
});

// Computed properties
const totalIncome = computed(() => {
  return incomes.value.reduce((sum, income) => sum + income.amount, 0);
});

const totalDebt = computed(() => {
  return debts.value.reduce((sum, debt) => sum + debt.amount, 0);
});

const totalPaid = computed(() => {
  return debts.value.reduce((sum, debt) => sum + (debt.paidAmount || 0), 0);
});

const monthlyIncome = computed(() => {
  return incomes.value
    .filter(income => income.frequency === 'monatlich')
    .reduce((sum, income) => sum + income.amount, 0);
});

const monthlyDebtPayments = computed(() => {
  // Simplified: assume minimum payments based on debt amount and interest
  return debts.value.reduce((sum, debt) => {
    const remaining = debt.amount - (debt.paidAmount || 0);
    return sum + Math.max(remaining * 0.02, 50); // 2% or minimum 50€
  }, 0);
});

const debtFreeMonths = computed(() => {
  const monthlySurplus = monthlyIncome.value - monthlyDebtPayments.value;
  if (monthlySurplus <= 0) return 'Unendlich';
  const remainingDebt = totalDebt.value - totalPaid.value;
  return Math.ceil(remainingDebt / monthlySurplus);
});

// Methods
function formatCurrency(amount) {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
}

function debtProgress(debt) {
  return ((debt.paidAmount || 0) / debt.amount) * 100;
}

function saveIncome() {
  if (editingIncome.value) {
    Object.assign(editingIncome.value, incomeForm.value);
  } else {
    incomes.value.push({
      id: Date.now(),
      ...incomeForm.value
    });
  }
  resetIncomeForm();
  showIncomeModal.value = false;
}

function editIncome(income) {
  editingIncome.value = income;
  incomeForm.value = { ...income };
  showIncomeModal.value = true;
}

function saveDebt() {
  if (editingDebt.value) {
    Object.assign(editingDebt.value, debtForm.value);
  } else {
    debts.value.push({
      id: Date.now(),
      ...debtForm.value,
      paidOff: false
    });
  }
  resetDebtForm();
  showDebtModal.value = false;
}

function editDebt(debt) {
  editingDebt.value = debt;
  debtForm.value = { ...debt };
  showDebtModal.value = true;
}

function addPayment(debt) {
  currentDebt.value = debt;
  paymentForm.value.date = new Date().toISOString().split('T')[0];
  paymentForm.value.amount = 0;
  showPaymentModal.value = true;
}

function savePayment() {
  const payment = {
    id: Date.now(),
    debtId: currentDebt.value.id,
    amount: paymentForm.value.amount,
    date: paymentForm.value.date,
    type: 'debt'
  };
  payments.value.push(payment);
  currentDebt.value.paidAmount = (currentDebt.value.paidAmount || 0) + payment.amount;
  if (currentDebt.value.paidAmount >= currentDebt.value.amount) {
    currentDebt.value.paidOff = true;
  }
  showPaymentModal.value = false;
}

function resetIncomeForm() {
  incomeForm.value = {
    name: '',
    amount: 0,
    frequency: ''
  };
  editingIncome.value = null;
}

function resetDebtForm() {
  debtForm.value = {
    name: '',
    amount: 0,
    interestRate: 0,
    paidAmount: 0
  };
  editingDebt.value = null;
}

function prevMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() - 1, 1);
}

function nextMonth() {
  currentDate.value = new Date(currentDate.value.getFullYear(), currentDate.value.getMonth() + 1, 1);
}

// Load data from localStorage
onMounted(() => {
  const savedIncomes = localStorage.getItem('finance-incomes');
  const savedDebts = localStorage.getItem('finance-debts');
  const savedPayments = localStorage.getItem('finance-payments');

  if (savedIncomes) incomes.value = JSON.parse(savedIncomes);
  if (savedDebts) debts.value = JSON.parse(savedDebts);
  if (savedPayments) payments.value = JSON.parse(savedPayments);

  // Watch for changes and save to localStorage
  watch(incomes, (newIncomes) => {
    localStorage.setItem('finance-incomes', JSON.stringify(newIncomes));
  }, { deep: true });

  watch(debts, (newDebts) => {
    localStorage.setItem('finance-debts', JSON.stringify(newDebts));
  }, { deep: true });

  watch(payments, (newPayments) => {
    localStorage.setItem('finance-payments', JSON.stringify(newPayments));
  }, { deep: true });
});
</script>

<style scoped>
.finance-tool {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.finance-header {
  margin-bottom: 30px;
}

.finance-header h2 {
  margin: 0 0 10px;
  font-size: 2rem;
}

.finance-header p {
  margin: 0;
  color: var(--muted);
}

.finance-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.finance-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  box-shadow: var(--shadow-soft);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
}

.income-list, .debt-list {
  margin-bottom: 20px;
}

.income-item, .debt-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--border);
}

.income-item:last-child, .debt-item:last-child {
  border-bottom: none;
}

.income-info, .debt-info {
  flex: 1;
}

.income-amount, .debt-amount {
  display: block;
  font-weight: bold;
  color: var(--brand);
}

.debt-item.paid-off .debt-amount {
  color: var(--muted);
  text-decoration: line-through;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  margin: 5px 0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
  transition: width 0.3s ease;
}

.debt-actions {
  display: flex;
  gap: 5px;
}

.total-income, .total-debt {
  padding-top: 15px;
  border-top: 1px solid var(--border);
  text-align: center;
}

.calendar {
  background: var(--surface);
  border-radius: 8px;
  padding: 15px;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.calendar-header h4 {
  margin: 0;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 5px;
}

.calendar-day {
  aspect-ratio: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  padding: 5px;
  border-radius: 6px;
  position: relative;
}

.calendar-day.today {
  background: rgba(47, 99, 255, 0.1);
  font-weight: bold;
}

.calendar-day.hasPayment {
  background: rgba(34, 197, 94, 0.1);
}

.day-payments {
  display: flex;
  gap: 2px;
  margin-top: 2px;
}

.payment-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.payment-dot.debt {
  background: var(--brand);
}

.stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  color: var(--muted);
}

.stat-value {
  font-weight: bold;
}

.stat-value.negative {
  color: #ef4444;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 20px;
  max-width: 400px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal h3 {
  margin-top: 0;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
}

.form-group input, .form-group select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--surface);
  color: var(--text);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.btn.small {
  padding: 6px 12px;
  font-size: 0.9rem;
}

.btn.tiny {
  padding: 4px 8px;
  font-size: 0.8rem;
}
</style>