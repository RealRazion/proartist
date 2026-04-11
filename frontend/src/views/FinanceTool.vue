<template>
  <div class="finance-tool">
    <div class="finance-header">
      <h2>Finanzübersicht</h2>
      <p>Umfassendes Finanzmanagement für Einnahmen, Ausgaben und Schulden.</p>
    </div>

    <div class="finance-tabs">
      <button :class="{ active: activeTab === 'overview' }" @click="activeTab = 'overview'">Übersicht</button>
      <button :class="{ active: activeTab === 'income' }" @click="activeTab = 'income'">Einnahmen</button>
      <button :class="{ active: activeTab === 'expenses' }" @click="activeTab = 'expenses'">Ausgaben</button>
      <button :class="{ active: activeTab === 'debt' }" @click="activeTab = 'debt'">Schulden</button>
      <button :class="{ active: activeTab === 'budget' }" @click="activeTab = 'budget'">Budget</button>
    </div>

    <!-- Übersicht Tab -->
    <div v-if="activeTab === 'overview'" class="finance-grid">
      <div class="finance-card summary-card">
        <h3>Monatliche Zusammenfassung</h3>
        <div class="summary-stats">
          <div class="stat">
            <span class="label">Einnahmen</span>
            <span class="value positive">{{ formatCurrency(monthlyIncome) }}</span>
          </div>
          <div class="stat">
            <span class="label">Ausgaben</span>
            <span class="value negative">{{ formatCurrency(monthlyExpenses) }}</span>
          </div>
          <div class="stat">
            <span class="label">Saldo</span>
            <span :class="['value', monthlyIncome - monthlyExpenses >= 0 ? 'positive' : 'negative']">
              {{ formatCurrency(monthlyIncome - monthlyExpenses) }}
            </span>
          </div>
        </div>
      </div>

      <div class="finance-card chart-card">
        <h3>Ausgaben nach Kategorie</h3>
        <div class="expense-breakdown">
          <div v-for="category in expenseCategories" :key="category.key" class="category-item">
            <span class="category-name">{{ category.name }}</span>
            <span class="category-amount">{{ formatCurrency(category.amount) }}</span>
            <div class="category-bar">
              <div class="bar-fill" :style="{ width: (category.amount / totalMonthlyExpenses * 100) + '%' }"></div>
            </div>
          </div>
        </div>
      </div>

      <div class="finance-card goals-card">
        <h3>Sparziele</h3>
        <div class="goals-list">
          <div v-for="goal in savingsGoals" :key="goal.id" class="goal-item">
            <div class="goal-info">
              <strong>{{ goal.name }}</strong>
              <span>{{ formatCurrency(goal.current) }} / {{ formatCurrency(goal.target) }}</span>
            </div>
            <div class="goal-progress">
              <div class="progress-bar">
                <div class="progress-fill" :style="{ width: (goal.current / goal.target * 100) + '%' }"></div>
              </div>
              <small>{{ Math.round(goal.current / goal.target * 100) }}%</small>
            </div>
          </div>
        </div>
        <button class="btn small" @click="showGoalModal = true">Neues Ziel</button>
      </div>
    </div>

    <!-- Einnahmen Tab -->
    <div v-if="activeTab === 'income'" class="tab-content">
      <div class="section-header">
        <h3>Einnahmen verwalten</h3>
        <button class="btn" @click="showIncomeModal = true">Einnahme hinzufügen</button>
      </div>
      <div class="items-grid">
        <div v-for="income in incomes" :key="income.id" class="item-card">
          <div class="item-header">
            <h4>{{ income.name }}</h4>
            <span class="amount positive">{{ formatCurrency(income.amount) }}</span>
          </div>
          <div class="item-details">
            <span class="frequency">{{ income.frequency || 'Einmalig' }}</span>
            <div class="item-actions">
              <button @click="editIncome(income)">Bearbeiten</button>
              <button @click="deleteIncome(income)">Löschen</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Ausgaben Tab -->
    <div v-if="activeTab === 'expenses'" class="tab-content">
      <div class="section-header">
        <h3>Ausgaben verwalten</h3>
        <button class="btn" @click="showExpenseModal = true">Ausgabe hinzufügen</button>
      </div>
      <div class="expense-categories">
        <button v-for="cat in expenseCategoryTypes" :key="cat.key" 
                :class="['category-tab', { active: selectedCategory === cat.key }]" 
                @click="selectedCategory = cat.key">
          {{ cat.name }}
        </button>
      </div>
      <div class="items-grid">
        <div v-for="expense in filteredExpenses" :key="expense.id" class="item-card">
          <div class="item-header">
            <h4>{{ expense.name }}</h4>
            <span class="amount negative">{{ formatCurrency(expense.amount) }}</span>
          </div>
          <div class="item-details">
            <span class="category">{{ getCategoryName(expense.category) }}</span>
            <span class="frequency">{{ expense.frequency || 'Einmalig' }}</span>
            <div class="item-actions">
              <button @click="editExpense(expense)">Bearbeiten</button>
              <button @click="deleteExpense(expense)">Löschen</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Schulden Tab -->
    <div v-if="activeTab === 'debt'" class="tab-content">
      <div class="section-header">
        <h3>Schulden verwalten</h3>
        <button class="btn" @click="showDebtModal = true">Schuld hinzufügen</button>
      </div>
      <div class="debt-summary">
        <div class="summary-item">
          <span>Gesamtschulden</span>
          <span class="amount">{{ formatCurrency(totalDebt) }}</span>
        </div>
        <div class="summary-item">
          <span>Bezahlt</span>
          <span class="amount positive">{{ formatCurrency(totalPaid) }}</span>
        </div>
        <div class="summary-item">
          <span>Verbleibend</span>
          <span class="amount">{{ formatCurrency(totalDebt - totalPaid) }}</span>
        </div>
      </div>
      <div class="items-grid">
        <div v-for="debt in debts" :key="debt.id" class="item-card debt-card" :class="{ 'paid-off': debt.paidAmount >= debt.amount }">
          <div class="item-header">
            <h4>{{ debt.name }}</h4>
            <span class="amount">{{ formatCurrency(debt.amount - debt.paidAmount) }}</span>
          </div>
          <div class="debt-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: (debt.paidAmount / debt.amount * 100) + '%' }"></div>
            </div>
            <small>{{ formatCurrency(debt.paidAmount) }} / {{ formatCurrency(debt.amount) }}</small>
          </div>
          <div class="item-details">
            <span>Zins: {{ debt.interestRate }}%</span>
            <div class="item-actions">
              <button @click="addPayment(debt)">Zahlung</button>
              <button @click="editDebt(debt)">Bearbeiten</button>
              <button @click="deleteDebt(debt)">Löschen</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Budget Tab -->
    <div v-if="activeTab === 'budget'" class="tab-content">
      <div class="section-header">
        <h3>Budget planen</h3>
        <button class="btn" @click="showBudgetModal = true">Budget setzen</button>
      </div>
      <div class="budget-overview">
        <div class="budget-item">
          <span>Monatliches Budget</span>
          <span>{{ formatCurrency(monthlyBudget) }}</span>
        </div>
        <div class="budget-item">
          <span>Ausgaben bisher</span>
          <span>{{ formatCurrency(currentMonthExpenses) }}</span>
        </div>
        <div class="budget-item">
          <span>Verbleibend</span>
          <span :class="monthlyBudget - currentMonthExpenses >= 0 ? 'positive' : 'negative'">
            {{ formatCurrency(monthlyBudget - currentMonthExpenses) }}
          </span>
        </div>
      </div>
      <div class="budget-breakdown">
        <h4>Budget nach Kategorie</h4>
        <div v-for="budget in categoryBudgets" :key="budget.category" class="budget-category">
          <div class="category-header">
            <span>{{ getCategoryName(budget.category) }}</span>
            <span>{{ formatCurrency(budget.allocated) }}</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" :style="{ width: Math.min((getCategorySpent(budget.category) / budget.allocated * 100), 100) + '%' }"></div>
          </div>
          <small>Ausgegeben: {{ formatCurrency(getCategorySpent(budget.category)) }}</small>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <div v-if="showIncomeModal" class="modal-overlay" @click="showIncomeModal = false">
      <div class="modal" @click.stop>
        <h3>{{ editingIncome ? 'Einnahme bearbeiten' : 'Neue Einnahme' }}</h3>
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

    <div v-if="showExpenseModal" class="modal-overlay" @click="showExpenseModal = false">
      <div class="modal" @click.stop>
        <h3>{{ editingExpense ? 'Ausgabe bearbeiten' : 'Neue Ausgabe' }}</h3>
        <form @submit.prevent="saveExpense">
          <div class="form-group">
            <label>Name</label>
            <input v-model="expenseForm.name" type="text" required>
          </div>
          <div class="form-group">
            <label>Betrag</label>
            <input v-model.number="expenseForm.amount" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Kategorie</label>
            <select v-model="expenseForm.category" required>
              <option v-for="cat in expenseCategoryTypes" :key="cat.key" :value="cat.key">{{ cat.name }}</option>
            </select>
          </div>
          <div class="form-group">
            <label>Häufigkeit</label>
            <select v-model="expenseForm.frequency">
              <option value="">Einmalig</option>
              <option value="monatlich">Monatlich</option>
              <option value="wöchentlich">Wöchentlich</option>
              <option value="jährlich">Jährlich</option>
            </select>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showExpenseModal = false">Abbrechen</button>
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

    <div v-if="showGoalModal" class="modal-overlay" @click="showGoalModal = false">
      <div class="modal" @click.stop>
        <h3>Neues Sparziel</h3>
        <form @submit.prevent="saveGoal">
          <div class="form-group">
            <label>Name</label>
            <input v-model="goalForm.name" type="text" required>
          </div>
          <div class="form-group">
            <label>Zielbetrag</label>
            <input v-model.number="goalForm.target" type="number" step="0.01" required>
          </div>
          <div class="form-group">
            <label>Aktuell gespart</label>
            <input v-model.number="goalForm.current" type="number" step="0.01">
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showGoalModal = false">Abbrechen</button>
            <button type="submit" class="btn">Speichern</button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showBudgetModal" class="modal-overlay" @click="showBudgetModal = false">
      <div class="modal" @click.stop>
        <h3>Monatliches Budget setzen</h3>
        <form @submit.prevent="saveBudget">
          <div class="form-group">
            <label>Gesamtbudget</label>
            <input v-model.number="budgetForm.total" type="number" step="0.01" required>
          </div>
          <div class="category-budgets">
            <h4>Budget pro Kategorie</h4>
            <div v-for="cat in expenseCategoryTypes" :key="cat.key" class="budget-input">
              <label>{{ cat.name }}</label>
              <input v-model.number="budgetForm.categories[cat.key]" type="number" step="0.01">
            </div>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn ghost" @click="showBudgetModal = false">Abbrechen</button>
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
const activeTab = ref('overview');
const incomes = ref([]);
const expenses = ref([]);
const debts = ref([]);
const payments = ref([]);
const savingsGoals = ref([]);
const categoryBudgets = ref([]);

const selectedCategory = ref('all');

const showIncomeModal = ref(false);
const showExpenseModal = ref(false);
const showDebtModal = ref(false);
const showPaymentModal = ref(false);
const showGoalModal = ref(false);
const showBudgetModal = ref(false);

const editingIncome = ref(null);
const editingExpense = ref(null);
const editingDebt = ref(null);
const currentDebt = ref(null);

const incomeForm = ref({
  name: '',
  amount: 0,
  frequency: ''
});

const expenseForm = ref({
  name: '',
  amount: 0,
  category: '',
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

const goalForm = ref({
  name: '',
  target: 0,
  current: 0
});

const budgetForm = ref({
  total: 0,
  categories: {}
});

const expenseCategoryTypes = [
  { key: 'fixed', name: 'Fixe Kosten' },
  { key: 'subscriptions', name: 'Abos' },
  { key: 'installments', name: 'Ratenzahlungen' },
  { key: 'variable', name: 'Variable Ausgaben' },
  { key: 'entertainment', name: 'Unterhaltung' },
  { key: 'food', name: 'Essen' },
  { key: 'transport', name: 'Transport' },
  { key: 'other', name: 'Sonstiges' }
];

// Computed properties
const totalIncome = computed(() => {
  return incomes.value.reduce((sum, income) => sum + income.amount, 0);
});

const totalExpenses = computed(() => {
  return expenses.value.reduce((sum, expense) => sum + expense.amount, 0);
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

const monthlyExpenses = computed(() => {
  return expenses.value
    .filter(expense => expense.frequency === 'monatlich')
    .reduce((sum, expense) => sum + expense.amount, 0);
});

const totalMonthlyExpenses = computed(() => monthlyExpenses.value);

const expenseCategories = computed(() => {
  const categories = {};
  expenses.value.forEach(expense => {
    if (!categories[expense.category]) {
      categories[expense.category] = { amount: 0, name: getCategoryName(expense.category) };
    }
    categories[expense.category].amount += expense.amount;
  });
  return Object.values(categories);
});

const filteredExpenses = computed(() => {
  if (selectedCategory.value === 'all') return expenses.value;
  return expenses.value.filter(expense => expense.category === selectedCategory.value);
});

const monthlyBudget = computed(() => {
  return categoryBudgets.value.reduce((sum, budget) => sum + budget.allocated, 0);
});

const currentMonthExpenses = computed(() => {
  const now = new Date();
  const currentMonth = now.getMonth();
  const currentYear = now.getFullYear();
  
  return expenses.value
    .filter(expense => {
      if (!expense.frequency || expense.frequency === 'monatlich') return true;
      // For simplicity, assume monthly for now
      return true;
    })
    .reduce((sum, expense) => sum + expense.amount, 0);
});

// Methods
function formatCurrency(amount) {
  return new Intl.NumberFormat('de-DE', {
    style: 'currency',
    currency: 'EUR'
  }).format(amount);
}

function getCategoryName(key) {
  const cat = expenseCategoryTypes.find(c => c.key === key);
  return cat ? cat.name : key;
}

function getCategorySpent(category) {
  return expenses.value
    .filter(expense => expense.category === category)
    .reduce((sum, expense) => sum + expense.amount, 0);
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

function deleteIncome(income) {
  const index = incomes.value.indexOf(income);
  if (index > -1) incomes.value.splice(index, 1);
}

function saveExpense() {
  if (editingExpense.value) {
    Object.assign(editingExpense.value, expenseForm.value);
  } else {
    expenses.value.push({
      id: Date.now(),
      ...expenseForm.value
    });
  }
  resetExpenseForm();
  showExpenseModal.value = false;
}

function editExpense(expense) {
  editingExpense.value = expense;
  expenseForm.value = { ...expense };
  showExpenseModal.value = true;
}

function deleteExpense(expense) {
  const index = expenses.value.indexOf(expense);
  if (index > -1) expenses.value.splice(index, 1);
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

function deleteDebt(debt) {
  const index = debts.value.indexOf(debt);
  if (index > -1) debts.value.splice(index, 1);
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

function saveGoal() {
  savingsGoals.value.push({
    id: Date.now(),
    ...goalForm.value
  });
  resetGoalForm();
  showGoalModal.value = false;
}

function saveBudget() {
  categoryBudgets.value = Object.keys(budgetForm.value.categories).map(key => ({
    category: key,
    allocated: budgetForm.value.categories[key] || 0
  }));
  showBudgetModal.value = false;
}

function resetIncomeForm() {
  incomeForm.value = {
    name: '',
    amount: 0,
    frequency: ''
  };
  editingIncome.value = null;
}

function resetExpenseForm() {
  expenseForm.value = {
    name: '',
    amount: 0,
    category: '',
    frequency: ''
  };
  editingExpense.value = null;
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

function resetGoalForm() {
  goalForm.value = {
    name: '',
    target: 0,
    current: 0
  };
}

// Load data from localStorage
onMounted(() => {
  const savedIncomes = localStorage.getItem('finance-incomes');
  const savedExpenses = localStorage.getItem('finance-expenses');
  const savedDebts = localStorage.getItem('finance-debts');
  const savedPayments = localStorage.getItem('finance-payments');
  const savedGoals = localStorage.getItem('finance-goals');
  const savedBudgets = localStorage.getItem('finance-budgets');

  if (savedIncomes) incomes.value = JSON.parse(savedIncomes);
  if (savedExpenses) expenses.value = JSON.parse(savedExpenses);
  if (savedDebts) debts.value = JSON.parse(savedDebts);
  if (savedPayments) payments.value = JSON.parse(savedPayments);
  if (savedGoals) savingsGoals.value = JSON.parse(savedGoals);
  if (savedBudgets) categoryBudgets.value = JSON.parse(savedBudgets);

  // Watch for changes and save to localStorage
  watch(incomes, (newIncomes) => {
    localStorage.setItem('finance-incomes', JSON.stringify(newIncomes));
  }, { deep: true });

  watch(expenses, (newExpenses) => {
    localStorage.setItem('finance-expenses', JSON.stringify(newExpenses));
  }, { deep: true });

  watch(debts, (newDebts) => {
    localStorage.setItem('finance-debts', JSON.stringify(newDebts));
  }, { deep: true });

  watch(payments, (newPayments) => {
    localStorage.setItem('finance-payments', JSON.stringify(newPayments));
  }, { deep: true });

  watch(savingsGoals, (newGoals) => {
    localStorage.setItem('finance-goals', JSON.stringify(newGoals));
  }, { deep: true });

  watch(categoryBudgets, (newBudgets) => {
    localStorage.setItem('finance-budgets', JSON.stringify(newBudgets));
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

.finance-tabs {
  display: flex;
  gap: 5px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border);
}

.finance-tabs button {
  padding: 10px 20px;
  border: none;
  background: transparent;
  color: var(--muted);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.finance-tabs button.active {
  color: var(--brand);
  border-bottom-color: var(--brand);
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

.tab-content {
  padding: 20px 0;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h3 {
  margin: 0;
}

.items-grid {
  display: grid;
  gap: 15px;
}

.item-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 15px;
}

.item-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.item-header h4 {
  margin: 0;
}

.amount {
  font-weight: bold;
  font-size: 1.1rem;
}

.amount.positive {
  color: #10b981;
}

.amount.negative {
  color: #ef4444;
}

.item-details {
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: var(--muted);
  font-size: 0.9rem;
}

.item-actions {
  display: flex;
  gap: 5px;
}

.expense-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 20px;
}

.category-tab {
  padding: 8px 12px;
  border: 1px solid var(--border);
  background: var(--surface);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.category-tab.active {
  background: var(--brand);
  color: white;
  border-color: var(--brand);
}

.debt-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 15px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.summary-item span:first-child {
  display: block;
  color: var(--muted);
  font-size: 0.9rem;
  margin-bottom: 5px;
}

.debt-progress {
  margin: 10px 0;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
  margin: 5px 0;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
  transition: width 0.3s ease;
}

.budget-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
}

.budget-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.budget-breakdown {
  display: grid;
  gap: 15px;
}

.budget-category {
  padding: 15px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.category-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.summary-stats {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat .label {
  color: var(--muted);
}

.stat .value {
  font-weight: bold;
  font-size: 1.1rem;
}

.value.positive {
  color: #10b981;
}

.value.negative {
  color: #ef4444;
}

.expense-breakdown {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.category-name {
  flex: 1;
  font-weight: 500;
}

.category-amount {
  font-weight: bold;
  color: var(--brand);
}

.category-bar {
  flex: 2;
  height: 8px;
  background: var(--border);
  border-radius: 4px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--brand), var(--brand-2));
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
  margin-bottom: 20px;
}

.goal-item {
  padding: 15px;
  background: var(--surface);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.goal-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.goal-progress {
  display: flex;
  align-items: center;
  gap: 10px;
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

.category-budgets {
  margin-top: 20px;
}

.budget-input {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.budget-input label {
  flex: 1;
}

.budget-input input {
  width: 120px;
}

.btn.small {
  padding: 6px 12px;
  font-size: 0.9rem;
}

.btn.tiny {
  padding: 4px 8px;
  font-size: 0.8rem;
}

.debt-card.paid-off {
  opacity: 0.7;
  border-color: #10b981;
}
</style>