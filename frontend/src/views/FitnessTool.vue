<template>
  <div class="fitness-tool">
    <header class="card hero">
      <div class="hero-copy">
        <p class="eyebrow">Fitness Tracker</p>
        <h1>Kalorien, Verbrauch und Essensideen in einer Ansicht.</h1>
        <p class="muted">
          Der Rechner schätzt deinen Grundumsatz und Tagesverbrauch. Dazu kannst du deinen Tag tracken,
          mit einem Plus/Minus-Rechner spielen und dir grobe Meal-Ideen direkt in den Tracker ziehen.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn ghost" type="button" @click="resetTracker">Zurücksetzen</button>
        <button class="btn" type="button" @click="router.push({ name: 'platform-fitness' })">Zur Landingpage</button>
      </div>
    </header>

    <section class="summary-grid">
      <article class="card summary-card">
        <span class="label">Grundumsatz</span>
        <strong>{{ formatNumber(metrics.bmr) }} kcal</strong>
        <small class="muted">ohne Aktivität</small>
      </article>
      <article class="card summary-card">
        <span class="label">Tagesverbrauch</span>
        <strong>{{ formatNumber(metrics.tdee) }} kcal</strong>
        <small class="muted">inklusive Aktivität</small>
      </article>
      <article class="card summary-card">
        <span class="label">Tagesziel</span>
        <strong>{{ formatNumber(metrics.targetCalories) }} kcal</strong>
        <small class="muted">{{ goalLabel }}</small>
      </article>
      <article class="card summary-card" :class="{ positive: caloriesRemaining >= 0, warning: caloriesRemaining < 0 }">
        <span class="label">Heute übrig</span>
        <strong>{{ formatSigned(caloriesRemaining) }} kcal</strong>
        <small class="muted">gegessen: {{ formatNumber(totalConsumed) }} kcal</small>
      </article>
    </section>

    <section class="layout">
      <div class="main-column">
        <article class="card profile-card">
          <div class="section-head">
            <div>
              <h2>Dein Tagesprofil</h2>
              <p class="muted">Die Eingaben reichen für eine brauchbare Schätzung.</p>
            </div>
          </div>

          <div class="grid profile-grid">
            <label>
              Geschlecht
              <select v-model="profile.sex" class="input">
                <option value="female">weiblich</option>
                <option value="male">männlich</option>
              </select>
            </label>
            <label>
              Alter
              <input v-model="profile.age" class="input" type="number" min="12" max="100" />
            </label>
            <label>
              Gewicht in kg
              <input v-model="profile.weight" class="input" type="number" step="0.1" min="30" max="250" />
            </label>
            <label>
              Größe in cm
              <input v-model="profile.height" class="input" type="number" min="120" max="230" />
            </label>
            <label>
              Aktivität
              <select v-model="profile.activity" class="input">
                <option v-for="item in activityOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
              </select>
            </label>
            <label>
              Ziel
              <select v-model="profile.goal" class="input">
                <option value="cut">Fett verlieren</option>
                <option value="maintain">Gewicht halten</option>
                <option value="gain">Aufbauen</option>
              </select>
            </label>
            <label>
              Kcal Anpassung
              <input v-model="profile.goalDelta" class="input" type="number" step="10" min="-800" max="800" />
            </label>
            <label>
              Tagesdatum
              <input v-model="selectedDay" class="input" type="date" />
            </label>
          </div>
        </article>

        <article class="card tracker-card">
          <div class="section-head">
            <div>
              <h2>Kcal Tracker</h2>
              <p class="muted">Eigene Mahlzeiten ergänzen oder Ideen direkt übernehmen.</p>
            </div>
            <div class="day-balance">
              <span>{{ formatNumber(totalConsumed) }} / {{ formatNumber(metrics.targetCalories) }} kcal</span>
            </div>
          </div>

          <div class="progress-wrap">
            <div class="progress-bar">
              <span :style="{ width: `${consumptionPercent}%` }"></span>
            </div>
          </div>

          <div class="meal-summary-grid">
            <div v-for="type in mealTypes" :key="type.value" class="meal-summary">
              <span class="label">{{ type.label }}</span>
              <strong>{{ formatNumber(caloriesByMeal[type.value]) }} kcal</strong>
            </div>
          </div>

          <form class="entry-form" @submit.prevent="addEntry">
            <div class="grid entry-grid">
              <label>
                Mahlzeit
                <select v-model="draft.type" class="input">
                  <option v-for="type in mealTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
                </select>
              </label>
              <label>
                Titel
                <input v-model.trim="draft.title" class="input" placeholder="z. B. Skyr mit Beeren" required />
              </label>
              <label>
                kcal
                <input v-model="draft.kcal" class="input" type="number" min="0" step="1" required />
              </label>
              <label>
                Protein in g
                <input v-model="draft.protein" class="input" type="number" min="0" step="1" />
              </label>
            </div>
            <div class="entry-actions">
              <button class="btn" type="submit">{{ editingEntryId ? "Eintrag speichern" : "Eintrag hinzufügen" }}</button>
              <button v-if="editingEntryId" class="btn ghost" type="button" @click="cancelEdit">Abbrechen</button>
            </div>
          </form>

          <div class="entry-list">
            <article v-for="entry in dayEntries" :key="entry.id" class="entry-row">
              <div>
                <strong>{{ entry.title }}</strong>
                <p class="muted small">
                  {{ mealTypeMap[entry.type] }} · Protein {{ formatNumber(entry.protein || 0) }} g
                </p>
              </div>
              <div class="entry-side">
                <strong>{{ formatNumber(entry.kcal) }} kcal</strong>
                <div class="tiny-actions">
                  <button class="btn ghost tiny" type="button" @click="startEdit(entry)">Bearbeiten</button>
                  <button class="btn ghost tiny danger" type="button" @click="removeEntry(entry.id)">Löschen</button>
                </div>
              </div>
            </article>
            <p v-if="!dayEntries.length" class="muted empty-hint">Für diesen Tag ist noch nichts eingetragen.</p>
          </div>
        </article>

        <article class="card ideas-card">
          <div class="section-head">
            <div>
              <h2>Essensideen</h2>
              <p class="muted">Große Genauigkeit brauchst du hier noch nicht. Die Werte sind als brauchbare Startwerte gedacht.</p>
            </div>
            <div class="idea-filters">
              <select v-model="ideaMealType" class="input compact">
                <option v-for="type in mealTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
              </select>
              <select v-model="ideaStyle" class="input compact">
                <option value="all">alle</option>
                <option value="light">leicht</option>
                <option value="balanced">ausgewogen</option>
                <option value="protein">proteinreich</option>
              </select>
            </div>
          </div>

          <div class="ideas-grid">
            <article v-for="idea in filteredIdeas" :key="idea.id" class="idea-card">
              <div class="idea-top">
                <div>
                  <h3>{{ idea.title }}</h3>
                  <p class="muted small">{{ idea.note }}</p>
                </div>
                <span class="idea-tag">{{ idea.tags.join(" · ") }}</span>
              </div>
              <div class="idea-stats">
                <span>{{ idea.kcal }} kcal</span>
                <span>{{ idea.protein }} g Protein</span>
              </div>
              <button class="btn ghost" type="button" @click="addIdeaToTracker(idea)">
                In Tracker übernehmen
              </button>
            </article>
          </div>
        </article>
      </div>

      <aside class="side-column">
        <article class="card calc-card">
          <div class="section-head">
            <div>
              <h2>+ / - Rechner</h2>
              <p class="muted">Was passiert bei einem täglichen Überschuss oder Defizit?</p>
            </div>
          </div>

          <label>
            Tägliche Abweichung in kcal
            <input v-model="deltaInput" class="input" type="number" step="10" min="-1500" max="1500" />
          </label>

          <div class="mini-grid">
            <div class="mini-card">
              <span class="label">pro Woche</span>
              <strong>{{ formatSigned(deltaMetrics.weeklyCalories) }} kcal</strong>
            </div>
            <div class="mini-card">
              <span class="label">Gewicht / Woche</span>
              <strong>{{ formatSigned(deltaMetrics.weeklyKg) }} kg</strong>
            </div>
            <div class="mini-card">
              <span class="label">pro 30 Tage</span>
              <strong>{{ formatSigned(deltaMetrics.monthlyCalories) }} kcal</strong>
            </div>
            <div class="mini-card">
              <span class="label">Gewicht / 30 Tage</span>
              <strong>{{ formatSigned(deltaMetrics.monthlyKg) }} kg</strong>
            </div>
          </div>
        </article>

        <article class="card macro-card">
          <div class="section-head">
            <div>
              <h2>Schnelle Einordnung</h2>
              <p class="muted">Grobe Orientierung für deinen Tag.</p>
            </div>
          </div>

          <ul class="metric-list">
            <li>
              <span>Protein-Fokus</span>
              <strong>{{ formatNumber(metrics.proteinTarget) }} g</strong>
            </li>
            <li>
              <span>Aktivitätsfaktor</span>
              <strong>{{ activityMap[profile.activity].factor.toFixed(2) }}</strong>
            </li>
            <li>
              <span>Essensideen aktuell</span>
              <strong>{{ filteredIdeas.length }}</strong>
            </li>
            <li>
              <span>Einträge heute</span>
              <strong>{{ dayEntries.length }}</strong>
            </li>
          </ul>
        </article>
      </aside>
    </section>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();
const STORAGE_KEY = "unyq-fitness-tracker-v1";

const activityMap = {
  sedentary: { label: "wenig Bewegung", factor: 1.2 },
  light: { label: "leicht aktiv", factor: 1.375 },
  moderate: { label: "moderat aktiv", factor: 1.55 },
  active: { label: "sehr aktiv", factor: 1.725 },
  athlete: { label: "extrem aktiv", factor: 1.9 },
};

const activityOptions = Object.entries(activityMap).map(([value, meta]) => ({
  value,
  label: meta.label,
}));

const mealTypes = [
  { value: "breakfast", label: "Frühstück" },
  { value: "lunch", label: "Lunch" },
  { value: "dinner", label: "Dinner" },
  { value: "snack", label: "Snack" },
];

const mealTypeMap = Object.fromEntries(mealTypes.map((item) => [item.value, item.label]));

const mealIdeas = [
  { id: "b1", type: "breakfast", title: "Skyr mit Beeren und Haferflocken", kcal: 410, protein: 31, tags: ["balanced", "protein"], note: "Satt, schnell und gut für einen klaren Start." },
  { id: "b2", type: "breakfast", title: "Rührei mit Vollkornbrot", kcal: 460, protein: 28, tags: ["balanced", "protein"], note: "Solider Klassiker mit gutem Protein-Fundament." },
  { id: "b3", type: "breakfast", title: "Overnight Oats mit Banane", kcal: 390, protein: 18, tags: ["light", "balanced"], note: "Einfach vorzubereiten und alltagstauglich." },
  { id: "b4", type: "breakfast", title: "Quark Bowl mit Apfel und Nüssen", kcal: 430, protein: 29, tags: ["protein"], note: "Etwas cremiger und trotzdem kontrollierbar." },
  { id: "l1", type: "lunch", title: "Chicken Rice Bowl", kcal: 620, protein: 46, tags: ["balanced", "protein"], note: "Guter Standard für Trainingstage und Routine." },
  { id: "l2", type: "lunch", title: "Linsensalat mit Feta", kcal: 540, protein: 24, tags: ["balanced"], note: "Sättigend ohne schwer zu werden." },
  { id: "l3", type: "lunch", title: "Wrap mit Pute und Gemüse", kcal: 510, protein: 34, tags: ["light", "protein"], note: "Praktisch unterwegs und gut planbar." },
  { id: "l4", type: "lunch", title: "Ofenkartoffel mit Kräuterquark", kcal: 480, protein: 21, tags: ["light"], note: "Günstig, simpel und erstaunlich stabil." },
  { id: "d1", type: "dinner", title: "Lachs mit Reis und Brokkoli", kcal: 690, protein: 42, tags: ["balanced", "protein"], note: "Etwas höher in kcal, aber sehr rund." },
  { id: "d2", type: "dinner", title: "Hackfleischpfanne mit Gemüse", kcal: 610, protein: 39, tags: ["protein"], note: "Passt gut für Low-Fuss am Abend." },
  { id: "d3", type: "dinner", title: "Pasta mit Tomate und Mozzarella", kcal: 560, protein: 22, tags: ["balanced"], note: "Einfach und angenehm, wenn es schnell gehen soll." },
  { id: "d4", type: "dinner", title: "Tofu Wok mit Reis", kcal: 530, protein: 27, tags: ["light", "balanced"], note: "Pflanzlich und trotzdem ordentlich." },
  { id: "s1", type: "snack", title: "Banane und Proteinshake", kcal: 260, protein: 27, tags: ["protein"], note: "Schneller Snack rund ums Training." },
  { id: "s2", type: "snack", title: "Apfel mit Erdnussmus", kcal: 220, protein: 6, tags: ["light"], note: "Klein, aber für viele genug." },
  { id: "s3", type: "snack", title: "Hüttenkäse mit Gurke", kcal: 180, protein: 22, tags: ["light", "protein"], note: "Sehr kalorienarm und proteinbetont." },
  { id: "s4", type: "snack", title: "Reiswaffeln mit Frischkäse und Pute", kcal: 230, protein: 18, tags: ["balanced", "protein"], note: "Leicht, aber nicht komplett leer." },
];

function todayString() {
  return new Date().toISOString().slice(0, 10);
}

function createDefaultState() {
  return {
    profile: {
      sex: "male",
      age: 28,
      weight: 82,
      height: 180,
      activity: "moderate",
      goal: "maintain",
      goalDelta: 0,
    },
    selectedDay: todayString(),
    entries: [],
    deltaInput: 0,
  };
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return createDefaultState();
    return { ...createDefaultState(), ...JSON.parse(raw) };
  } catch {
    return createDefaultState();
  }
}

const initialState = loadState();

const profile = reactive({ ...initialState.profile });
const selectedDay = ref(initialState.selectedDay);
const deltaInput = ref(initialState.deltaInput ?? 0);
const state = reactive({
  entries: Array.isArray(initialState.entries) ? initialState.entries : [],
});

const draft = reactive({
  type: "breakfast",
  title: "",
  kcal: "",
  protein: "",
});

const editingEntryId = ref(null);
const ideaMealType = ref("breakfast");
const ideaStyle = ref("all");

const metrics = computed(() => {
  const weight = Number(profile.weight || 0);
  const height = Number(profile.height || 0);
  const age = Number(profile.age || 0);
  const base = profile.sex === "female"
    ? 10 * weight + 6.25 * height - 5 * age - 161
    : 10 * weight + 6.25 * height - 5 * age + 5;
  const bmr = Math.max(0, Math.round(base));
  const factor = activityMap[profile.activity]?.factor || 1.55;
  const tdee = Math.round(bmr * factor);
  const goalDelta = Number(profile.goalDelta || 0);
  let defaultDelta = 0;
  if (profile.goal === "cut") defaultDelta = -350;
  if (profile.goal === "gain") defaultDelta = 250;
  const targetCalories = Math.max(1200, tdee + defaultDelta + goalDelta);
  const proteinTarget = Math.round(weight * (profile.goal === "gain" ? 2 : 1.8));
  return { bmr, tdee, targetCalories, proteinTarget };
});

const goalLabel = computed(() => {
  if (profile.goal === "cut") return "mit Defizit";
  if (profile.goal === "gain") return "mit Überschuss";
  return "Gewicht halten";
});

const dayEntries = computed(() =>
  state.entries.filter((entry) => entry.day === selectedDay.value).sort((a, b) => a.createdAt.localeCompare(b.createdAt))
);

const totalConsumed = computed(() =>
  dayEntries.value.reduce((sum, entry) => sum + Number(entry.kcal || 0), 0)
);

const caloriesRemaining = computed(() => Math.round(metrics.value.targetCalories - totalConsumed.value));

const caloriesByMeal = computed(() => {
  const totals = { breakfast: 0, lunch: 0, dinner: 0, snack: 0 };
  dayEntries.value.forEach((entry) => {
    totals[entry.type] += Number(entry.kcal || 0);
  });
  return totals;
});

const consumptionPercent = computed(() => {
  const target = Number(metrics.value.targetCalories || 1);
  return Math.min(100, Math.max(0, (Number(totalConsumed.value) / target) * 100));
});

const filteredIdeas = computed(() =>
  mealIdeas.filter((idea) => {
    const matchesType = idea.type === ideaMealType.value;
    const matchesStyle = ideaStyle.value === "all" || idea.tags.includes(ideaStyle.value);
    return matchesType && matchesStyle;
  })
);

const deltaMetrics = computed(() => {
  const dailyDelta = Number(deltaInput.value || 0);
  const weeklyCalories = dailyDelta * 7;
  const monthlyCalories = dailyDelta * 30;
  const weeklyKg = weeklyCalories / 7700;
  const monthlyKg = monthlyCalories / 7700;
  return {
    weeklyCalories,
    monthlyCalories,
    weeklyKg,
    monthlyKg,
  };
});

watch(
  () => ({
    profile: { ...profile },
    selectedDay: selectedDay.value,
    deltaInput: deltaInput.value,
    entries: state.entries,
  }),
  (value) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(value));
  },
  { deep: true }
);

function formatNumber(value) {
  return new Intl.NumberFormat("de-DE", {
    maximumFractionDigits: Math.abs(Number(value || 0)) < 10 ? 1 : 0,
  }).format(Number(value || 0));
}

function formatSigned(value) {
  const num = Number(value || 0);
  const formatted = new Intl.NumberFormat("de-DE", {
    maximumFractionDigits: Math.abs(num) < 10 ? 2 : 0,
    signDisplay: "always",
  }).format(num);
  return formatted;
}

function resetDraft() {
  draft.type = "breakfast";
  draft.title = "";
  draft.kcal = "";
  draft.protein = "";
}

function addEntry() {
  const entryPayload = {
    id: editingEntryId.value || `entry-${Date.now()}`,
    day: selectedDay.value,
    type: draft.type,
    title: draft.title,
    kcal: Number(draft.kcal || 0),
    protein: Number(draft.protein || 0),
    createdAt: editingEntryId.value
      ? state.entries.find((entry) => entry.id === editingEntryId.value)?.createdAt || new Date().toISOString()
      : new Date().toISOString(),
  };

  if (editingEntryId.value) {
    const index = state.entries.findIndex((entry) => entry.id === editingEntryId.value);
    if (index >= 0) state.entries[index] = entryPayload;
  } else {
    state.entries.push(entryPayload);
  }
  cancelEdit();
}

function startEdit(entry) {
  editingEntryId.value = entry.id;
  draft.type = entry.type;
  draft.title = entry.title;
  draft.kcal = entry.kcal;
  draft.protein = entry.protein;
}

function cancelEdit() {
  editingEntryId.value = null;
  resetDraft();
}

function removeEntry(entryId) {
  state.entries = state.entries.filter((entry) => entry.id !== entryId);
  if (editingEntryId.value === entryId) cancelEdit();
}

function addIdeaToTracker(idea) {
  draft.type = idea.type;
  draft.title = idea.title;
  draft.kcal = idea.kcal;
  draft.protein = idea.protein;
  editingEntryId.value = null;
}

function resetTracker() {
  const fresh = createDefaultState();
  Object.assign(profile, fresh.profile);
  selectedDay.value = fresh.selectedDay;
  deltaInput.value = fresh.deltaInput;
  state.entries = [];
  cancelEdit();
  localStorage.setItem(STORAGE_KEY, JSON.stringify(fresh));
}
</script>

<style scoped>
.fitness-tool {
  display: grid;
  gap: 18px;
}

.hero {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: flex-start;
  padding: 22px;
  background:
    radial-gradient(circle at top right, rgba(16, 185, 129, 0.16), transparent 35%),
    linear-gradient(145deg, rgba(255, 255, 255, 0.96), rgba(243, 255, 247, 0.93));
}

.hero-copy {
  display: grid;
  gap: 10px;
  max-width: 68ch;
}

.eyebrow {
  margin: 0;
  font-size: 12px;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #15803d;
  font-weight: 700;
}

.hero-actions,
.section-head,
.entry-actions,
.tiny-actions,
.idea-filters {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.section-head {
  justify-content: space-between;
  align-items: flex-start;
}

.summary-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.summary-card {
  display: grid;
  gap: 6px;
}

.summary-card.positive {
  background: linear-gradient(160deg, rgba(16, 185, 129, 0.12), rgba(255, 255, 255, 0.94));
}

.summary-card.warning {
  background: linear-gradient(160deg, rgba(239, 68, 68, 0.12), rgba(255, 255, 255, 0.94));
}

.label {
  color: var(--muted);
  font-size: 13px;
}

.layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.85fr);
  gap: 18px;
}

.main-column,
.side-column {
  display: grid;
  gap: 18px;
  align-content: start;
}

.grid {
  display: grid;
  gap: 12px;
}

.profile-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.entry-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

.progress-wrap {
  margin: 10px 0 14px;
}

.progress-bar {
  position: relative;
  height: 12px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(16, 185, 129, 0.12);
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(135deg, #10b981, #34d399);
}

.meal-summary-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 16px;
}

.meal-summary,
.mini-card {
  padding: 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.entry-form {
  display: grid;
  gap: 12px;
  margin-bottom: 16px;
}

.entry-list {
  display: grid;
  gap: 12px;
}

.entry-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.entry-side {
  display: grid;
  gap: 8px;
  justify-items: end;
  text-align: right;
}

.tiny {
  padding: 8px 10px;
  font-size: 13px;
}

.danger {
  color: #b91c1c;
}

.ideas-grid {
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.idea-card {
  display: grid;
  gap: 12px;
  padding: 16px;
  border-radius: 18px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.idea-top {
  display: grid;
  gap: 8px;
}

.idea-top h3 {
  margin: 0;
}

.idea-tag {
  justify-self: start;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  color: #b45309;
  font-size: 12px;
  font-weight: 700;
}

.idea-stats {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-weight: 600;
}

.mini-grid {
  display: grid;
  gap: 12px;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 14px;
}

.metric-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.metric-list li {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
}

.compact {
  min-width: 160px;
}

.small {
  font-size: 13px;
}

.day-balance {
  padding: 8px 12px;
  border-radius: 999px;
  background: rgba(16, 185, 129, 0.08);
  color: #15803d;
  font-weight: 700;
}

.empty-hint {
  margin: 0;
}

@media (max-width: 1120px) {
  .summary-grid,
  .profile-grid,
  .entry-grid,
  .meal-summary-grid,
  .ideas-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .hero,
  .summary-grid,
  .profile-grid,
  .entry-grid,
  .meal-summary-grid,
  .ideas-grid,
  .mini-grid,
  .entry-row {
    grid-template-columns: 1fr;
  }

  .entry-side {
    justify-items: start;
    text-align: left;
  }
}
</style>
