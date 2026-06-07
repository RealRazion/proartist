<template>
  <div class="platform-page locations-page">
    <header class="page-hero card">
      <div>
        <p class="eyebrow">UNYQ Locations</p>
        <h1>Orte, Events und Raumplanung</h1>
        <p class="lead">
          Eine eigene Plattform für Locationsuche, Terminplanung und Veranstaltungskoordination.
        </p>
      </div>
      <div class="hero-actions">
        <button class="btn" type="button" @click="loadData" :disabled="loading">{{ loading ? "Lädt..." : "Aktualisieren" }}</button>
        <button class="btn" type="button" @click="goHome">Zurück zum Hub</button>
      </div>
    </header>

    <section class="highlights card">
      <article>
        <h2>{{ events.length }}</h2>
        <p>Events gesamt</p>
      </article>
      <article>
        <h2>{{ appliedBookings }}</h2>
        <p>Offene Buchungen</p>
      </article>
      <article>
        <h2>{{ confirmedBookings }}</h2>
        <p>Bestätigte Buchungen</p>
      </article>
    </section>

    <section class="cards-grid">
      <article class="card feature-card maps">
        <h3>Neueste Events</h3>
        <ul v-if="events.length" class="item-list">
          <li v-for="event in events.slice(0, 4)" :key="event.id" class="item-row">
            <strong>{{ event.title }}</strong>
            <span class="muted">{{ formatDate(event.date) }} · {{ event.location }}</span>
          </li>
        </ul>
          <p v-else class="muted">Es sind derzeit keine Events verfügbar.</p>
      </article>
      <article class="card feature-card booking">
        <h3>Buchung einreichen</h3>
        <form class="booking-form" @submit.prevent="createBooking">
          <select v-model.number="bookingForm.event" class="input" required>
            <option :value="null" disabled>Event auswählen</option>
            <option v-for="event in events" :key="event.id" :value="event.id">{{ event.title }} · {{ formatDate(event.date) }}</option>
          </select>
          <input v-model.trim="bookingForm.slot_time" class="input" placeholder="Slot-Zeit (optional)" />
          <input v-model="bookingForm.payout_amount" class="input" type="number" min="0" step="0.01" />
          <button class="btn" type="submit" :disabled="savingBooking || !bookingForm.event">
            {{ savingBooking ? "Speichert..." : "Buchen" }}
          </button>
        </form>
      </article>
      <article class="card feature-card crew">
        <h3>Meine Buchungen</h3>
        <ul v-if="bookings.length" class="item-list">
          <li v-for="booking in bookings.slice(0, 4)" :key="booking.id" class="item-row">
            <strong>{{ eventName(booking.event) }}</strong>
            <span class="muted">{{ booking.slot_time || "Kein Slot" }} · {{ bookingStatusLabel(booking.status) }}</span>
          </li>
        </ul>
          <p v-else class="muted">Aktuell hast du keine Buchungen.</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useToast } from "../composables/useToast";
const router = useRouter();
const { showToast } = useToast();

const loading = ref(false);
const savingBooking = ref(false);
const events = ref([]);
const bookings = ref([]);

const bookingForm = ref({
  event: null,
  slot_time: "",
  payout_amount: "0.00",
});

const appliedBookings = computed(() => bookings.value.filter((entry) => entry.status === "APPLIED").length);
const confirmedBookings = computed(() => bookings.value.filter((entry) => entry.status === "CONFIRMED").length);
const bookingStatusMap = {
  APPLIED: "Eingereicht",
  CONFIRMED: "Bestätigt",
  CANCELLED: "Abgesagt",
  REJECTED: "Abgelehnt",
};

function asList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
}

function formatDate(value) {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }).format(parsed);
}

function eventName(eventId) {
  return events.value.find((event) => event.id === eventId)?.title || `Event #${eventId}`;
}

function bookingStatusLabel(status) {
  return bookingStatusMap[status] || status || "Unbekannt";
}

async function loadData() {
  loading.value = true;
  try {
    const [eventsRes, bookingsRes] = await Promise.all([
      api.get("events/"),
      api.get("bookings/"),
    ]);
    events.value = asList(eventsRes.data);
    bookings.value = asList(bookingsRes.data);
  } catch (err) {
    console.error("Locations-Daten konnten nicht geladen werden", err);
    showToast("Locations-Daten konnten nicht geladen werden", "error");
  } finally {
    loading.value = false;
  }
}

async function createBooking() {
  if (!bookingForm.value.event) return;
  savingBooking.value = true;
  try {
    await api.post("bookings/", {
      event: bookingForm.value.event,
      slot_time: bookingForm.value.slot_time,
      payout_amount: bookingForm.value.payout_amount || "0.00",
      status: "APPLIED",
    });
    bookingForm.value = { event: null, slot_time: "", payout_amount: "0.00" };
    showToast("Buchung erstellt", "success");
    await loadData();
  } catch (err) {
    console.error("Buchung konnte nicht erstellt werden", err);
    showToast("Buchung konnte nicht erstellt werden", "error");
  } finally {
    savingBooking.value = false;
  }
}

function goHome() {
  router.push({ name: "platforms" });
}

onMounted(loadData);
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
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.14), rgba(74, 222, 128, 0.12));
  border: 1px solid rgba(34, 197, 94, 0.24);
}
.lead {
  margin: 0;
  color: var(--muted);
  line-height: 1.7;
}
.hero-actions {
  display: flex;
  gap: 10px;
  align-items: flex-start;
}
.highlights {
  display: grid;
  gap: 14px;
  padding: 20px;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
}
.highlights article {
  padding: 18px;
  border-radius: 16px;
  background: var(--card);
  border: 1px solid var(--border);
}
.highlights article h2 {
  margin: 0;
  font-size: 1.5rem;
}
.highlights article p {
  margin: 6px 0 0;
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
.feature-card.maps {
  background: rgba(34, 197, 94, 0.08);
}
.feature-card.booking {
  background: rgba(59, 130, 246, 0.08);
}
.feature-card.crew {
  background: rgba(168, 85, 247, 0.08);
}
.item-list {
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
  display: grid;
  gap: 8px;
}
.item-row {
  display: grid;
  gap: 4px;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: color-mix(in srgb, var(--card) 80%, transparent);
}
.booking-form {
  display: grid;
  gap: 10px;
  margin-top: 10px;
}

:global(.dark) .locations-page .page-hero {
  background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(74, 222, 128, 0.12));
}
</style>
