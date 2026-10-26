<template>
  <div class="forum-page">
    <!-- Header / Banner -->
    <header class="forum-hero card">
      <div class="hero-left">
        <div class="forum-pill">
          <span class="icon">💬</span>
          <span>UNYQ Community Board</span>
        </div>
        <h1>UNYQ Forum</h1>
        <p class="hero-desc">
          Die zentrale Community für Artists, Producer, Beatmaker und Sound-Engineers. 
          Tausche Feedback aus, finde Collabs, teile dein Wissen oder reiche Feature-Wünsche ein.
        </p>

        <div class="hero-actions">
          <button class="btn" type="button" @click="showNewThreadModal = true">
            ✏️ Neues Thema erstellen
          </button>
          <button v-if="activeThread" class="btn ghost" type="button" @click="activeThread = null">
            ← Zurück zur Themenübersicht
          </button>
        </div>
      </div>

      <div class="hero-right">
        <div class="forum-stats-box">
          <div class="f-stat">
            <span class="f-val">{{ threads.length }}</span>
            <span class="f-lbl">Themen</span>
          </div>
          <div class="f-stat">
            <span class="f-val">{{ totalReplies }}</span>
            <span class="f-lbl">Antworten</span>
          </div>
          <div class="f-stat">
            <span class="f-val">Live</span>
            <span class="f-lbl">Community</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Thread Detail View (if a thread is selected) -->
    <section v-if="activeThread" class="thread-detail-section">
      <div class="thread-detail-card card">
        <div class="detail-top">
          <button class="btn ghost tiny back-btn" @click="activeThread = null">
            ← Zurück zu allen Themen
          </button>
          <div class="detail-tags">
            <span class="cat-badge">{{ activeThread.category }}</span>
            <span class="date-badge">{{ activeThread.timeAgo }}</span>
          </div>
        </div>

        <h2 class="detail-title">{{ activeThread.title }}</h2>

        <div class="author-bar">
          <div class="author-avatar">{{ activeThread.author.charAt(0).toUpperCase() }}</div>
          <div class="author-info">
            <span class="author-name">{{ activeThread.author }}</span>
            <span class="author-role">{{ activeThread.authorRole }}</span>
          </div>
          <div class="detail-actions">
            <button class="btn ghost tiny upvote-btn" @click="upvoteThread(activeThread)">
              ▲ {{ activeThread.upvotes }} Upvotes
            </button>
          </div>
        </div>

        <div class="detail-content">
          <p>{{ activeThread.content }}</p>
        </div>
      </div>

      <!-- Replies Section -->
      <div class="replies-wrapper card">
        <h3>Antworten ({{ activeThread.replies.length }})</h3>

        <div class="replies-list">
          <div v-for="reply in activeThread.replies" :key="reply.id" class="reply-card">
            <div class="reply-head">
              <div class="reply-avatar">{{ reply.author.charAt(0).toUpperCase() }}</div>
              <div class="reply-meta">
                <span class="reply-author">{{ reply.author }}</span>
                <span class="reply-time">{{ reply.timeAgo }}</span>
              </div>
            </div>
            <p class="reply-text">{{ reply.content }}</p>
          </div>

          <div v-if="!activeThread.replies.length" class="empty-replies muted">
            Noch keine Antworten. Sei der Erste, der antwortet!
          </div>
        </div>

        <!-- Add Reply Form -->
        <form class="reply-input-form" @submit.prevent="submitReply">
          <textarea
            v-model.trim="newReplyText"
            class="input reply-textarea"
            rows="3"
            placeholder="Schreibe eine hilfreiche Antwort..."
            required
          ></textarea>
          <div class="reply-form-actions">
            <button class="btn" type="submit">Antworten 🚀</button>
          </div>
        </form>
      </div>
    </section>

    <!-- Main Threads Overview List (when no thread is open) -->
    <section v-else class="forum-overview-section">
      <!-- Search and Categories -->
      <div class="forum-controls">
        <div class="cat-pill-row">
          <button
            v-for="cat in categories"
            :key="cat"
            class="cat-chip"
            :class="{ active: selectedCategory === cat }"
            @click="selectedCategory = cat"
          >
            {{ cat }}
          </button>
        </div>
        <div class="search-wrap">
          <input
            v-model.trim="searchQuery"
            type="text"
            class="input"
            placeholder="Thema, Frage oder Stichwort suchen..."
          />
        </div>
      </div>

      <!-- Threads List Cards -->
      <div class="threads-list-box card">
        <div
          v-for="thread in filteredThreads"
          :key="thread.id"
          class="thread-row"
          :class="{ pinned: thread.isPinned }"
          @click="openThread(thread)"
        >
          <div class="thread-vote-col" @click.stop="upvoteThread(thread)">
            <button class="btn-vote" :title="`Upvotes: ${thread.upvotes}`">
              ▲
              <span class="vote-count">{{ thread.upvotes }}</span>
            </button>
          </div>

          <div class="thread-main-col">
            <div class="thread-headline">
              <span v-if="thread.isPinned" class="pin-badge">📌 ANGEHEFTET</span>
              <span class="thread-cat-pill">{{ thread.category }}</span>
              <h3 class="thread-title">{{ thread.title }}</h3>
            </div>
            <p class="thread-preview">{{ thread.content }}</p>
            <div class="thread-meta-bar">
              <span class="meta-author">von <strong>{{ thread.author }}</strong> ({{ thread.authorRole }})</span>
              <span class="meta-dot">•</span>
              <span class="meta-time">{{ thread.timeAgo }}</span>
            </div>
          </div>

          <div class="thread-replies-col">
            <div class="replies-badge">
              <span class="rep-icon">💬</span>
              <span class="rep-count">{{ thread.replies.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- New Thread Modal -->
    <div v-if="showNewThreadModal" class="modal-overlay" @click.self="showNewThreadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Neues Foren-Thema erstellen</h3>
          <button class="btn ghost tiny" @click="showNewThreadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitNewThread">
          <label>
            <span>Titel des Themas *</span>
            <input v-model.trim="newThread.title" class="input" required placeholder="z. B. Wie mischt ihr eure 808s in FL Studio / Ableton?" />
          </label>

          <label>
            <span>Kategorie *</span>
            <select v-model="newThread.category" class="input">
              <option value="Musikproduktion">🎵 Musikproduktion</option>
              <option value="Collabs & Feedback">🎤 Collabs &amp; Feedback</option>
              <option value="Mixing & Mastering">🎚️ Mixing &amp; Mastering</option>
              <option value="UNYQ Features & Ideen">💡 UNYQ Features &amp; Ideen</option>
              <option value="Ankündigungen">📢 Ankündigungen</option>
              <option value="Off-Topic">☕ Off-Topic</option>
            </select>
          </label>

          <label>
            <span>Inhalt / Deine Frage oder Gedanke *</span>
            <textarea
              v-model.trim="newThread.content"
              class="input"
              rows="5"
              required
              placeholder="Beschreibe dein Anliegen ausführlich, füge Links oder Details hinzu..."
            ></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showNewThreadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Thema veröffentlichen 🚀</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";

const { profile: me } = useCurrentProfile();
const { showToast } = useToast();

const selectedCategory = ref("Alle");
const searchQuery = ref("");
const activeThread = ref(null);
const showNewThreadModal = ref(false);
const newReplyText = ref("");

const categories = [
  "Alle",
  "Musikproduktion",
  "Collabs & Feedback",
  "Mixing & Mastering",
  "UNYQ Features & Ideen",
  "Ankündigungen",
  "Off-Topic",
];

const threads = ref([
  {
    id: 1,
    title: "Willkommen im neuen UNYQ Forum: Austausch, Feedback & Release-Pläne",
    author: "UNYQ Team",
    authorRole: "Admin",
    category: "Ankündigungen",
    timeAgo: "vor 2 Stunden",
    upvotes: 42,
    isPinned: true,
    content: "Herzlich willkommen im brandneuen UNYQ Forum! Hier könnt ihr euch direkt mit anderen Artists und Producern austauschen, Beats teilen, Feedback einholen und neue Features für die Plattform diskutieren.",
    replies: [
      { id: 101, author: "Mika_Beats", timeAgo: "vor 1 Stunde", content: "Endlich ein zentrales Forum für alle Kreativen! Sieht mega clean aus." },
      { id: 102, author: "Aura Vox", timeAgo: "vor 45 Min", content: "Super Sache! Freue mich schon auf gemeinsame Collabs hier." },
    ],
  },
  {
    id: 2,
    title: "Sidechaining bei 808s: Sidechain-Kompression vs. Volume-Automation (Duck/Kickstart)?",
    author: "BasslineHero",
    authorRole: "Producer",
    category: "Mixing & Mastering",
    timeAgo: "vor 5 Stunden",
    upvotes: 18,
    isPinned: false,
    content: "Was nutzt ihr lieber, um Platz für die Kick zu machen? Klassischen Sidechain-Kompressor oder Volume-Ducking Plugins wie Duck, Shaperbox oder LFO Tool?",
    replies: [
      { id: 201, author: "NeoProducer", timeAgo: "vor 3 Stunden", content: "Ganz klar Volume-Ducking! Mit Shaperbox hat man 100% präzise Kontrolle über die Kurve ohne Compressor-Pumping Artefakte." },
    ],
  },
  {
    id: 3,
    title: "Suche R&B / Neo-Soul Sänger/in für Sommer-EP (Track ist gemischt)",
    author: "KAZA",
    authorRole: "Artist",
    category: "Collabs & Feedback",
    timeAgo: "vor 1 Tag",
    upvotes: 24,
    isPinned: false,
    content: "Hab einen warmen Beat fertig im Stil von Brent Faiyaz / SZA. Beat ist 94 BPM in Db. Meldet euch gerne per Chat oder hier mit Hörproben!",
    replies: [
      { id: 301, author: "Sarah_Soul", timeAgo: "vor 18 Stunden", content: "Hört sich spannend an! Schreib dir gleich auf UNYQ Chats." },
    ],
  },
  {
    id: 4,
    title: "Idee: Automatische BPM- & Key-Erkennung in UNYQ Music und Library",
    author: "DrillMaster99",
    authorRole: "Producer",
    category: "UNYQ Features & Ideen",
    timeAgo: "vor 2 Tagen",
    upvotes: 35,
    isPinned: false,
    content: "Wäre es möglich, dass wenn man Samples in die Library lädt, die Tonart und das Tempo automatisch per Web Audio analysiert werden? Würde super viel Zeit sparen!",
    replies: [
      { id: 401, author: "UNYQ Team", timeAgo: "vor 1 Tag", content: "Starke Idee! Wir haben das bereits auf unserer Roadmap für das nächste Release." },
    ],
  },
]);

const newThread = ref({
  title: "",
  category: "Musikproduktion",
  content: "",
});

const totalReplies = computed(() => {
  return threads.value.reduce((acc, t) => acc + t.replies.length, 0);
});

const filteredThreads = computed(() => {
  return threads.value.filter((t) => {
    const matchCat = selectedCategory.value === "Alle" || t.category === selectedCategory.value;
    const q = searchQuery.value.toLowerCase();
    const matchQuery =
      !q ||
      t.title.toLowerCase().includes(q) ||
      t.content.toLowerCase().includes(q) ||
      t.author.toLowerCase().includes(q);
    return matchCat && matchQuery;
  });
});

function openThread(thread) {
  activeThread.value = thread;
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function upvoteThread(thread) {
  thread.upvotes++;
  showToast("Upvote gezählt! 👍", "info");
}

function submitReply() {
  if (!newReplyText.value.trim() || !activeThread.value) return;
  const authorName = me.value?.name || me.value?.username || "Community Mitglied";
  activeThread.value.replies.push({
    id: Date.now(),
    author: authorName,
    timeAgo: "Gerade eben",
    content: newReplyText.value.trim(),
  });
  newReplyText.value = "";
  showToast("Antwort erfolgreich veröffentlicht! 💬", "success");
}

function submitNewThread() {
  const authorName = me.value?.name || me.value?.username || "Creator";
  const created = {
    id: Date.now(),
    title: newThread.value.title,
    author: authorName,
    authorRole: "Creator",
    category: newThread.value.category,
    timeAgo: "Gerade eben",
    upvotes: 1,
    isPinned: false,
    content: newThread.value.content,
    replies: [],
  };
  threads.value.unshift(created);
  showNewThreadModal.value = false;
  newThread.value = { title: "", category: "Musikproduktion", content: "" };
  showToast("Thema erfolgreich im Forum erstellt! 🚀", "success");
  openThread(created);
}
</script>

<style scoped>
.forum-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 8px 0 60px;
}

/* Hero */
.forum-hero {
  display: grid;
  grid-template-columns: 1.3fr 1fr;
  gap: 32px;
  align-items: center;
  padding: 36px 32px;
  background: 
    radial-gradient(circle at top right, rgba(99, 102, 241, 0.16), transparent 50%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.75), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(129, 140, 248, 0.2);
  position: relative;
  overflow: hidden;
}

.forum-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #818cf8;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
}

.forum-hero h1 {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.15;
  background: linear-gradient(120deg, #fff 40%, #a5b4fc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-desc {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 20px;
}

.hero-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.forum-stats-box {
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(129, 140, 248, 0.2);
  border-radius: 18px;
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  text-align: center;
}

.f-stat {
  display: flex;
  flex-direction: column;
}

.f-val {
  font-size: 1.8rem;
  font-weight: 800;
  color: #818cf8;
}

.f-lbl {
  font-size: 11px;
  color: var(--muted);
  text-transform: uppercase;
}

/* Controls */
.forum-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  margin-bottom: 16px;
}

.cat-pill-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.cat-chip {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border);
  color: var(--muted);
  padding: 7px 14px;
  border-radius: 999px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cat-chip.active, .cat-chip:hover {
  background: #6366f1;
  color: #fff;
  border-color: #6366f1;
}

.search-wrap {
  min-width: 280px;
}

/* Threads List */
.threads-list-box {
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.thread-row {
  display: grid;
  grid-template-columns: 56px 1fr 70px;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.thread-row:hover {
  background: rgba(255, 255, 255, 0.04);
}

.thread-row.pinned {
  background: rgba(99, 102, 241, 0.08);
  border-left: 3px solid #6366f1;
}

.thread-vote-col {
  display: flex;
  justify-content: center;
}

.btn-vote {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 6px 10px;
  color: var(--text);
  font-size: 11px;
  font-weight: 700;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-vote:hover {
  background: rgba(99, 102, 241, 0.2);
  border-color: #6366f1;
  color: #818cf8;
}

.vote-count {
  font-size: 12px;
}

.thread-main-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.thread-headline {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.pin-badge {
  background: rgba(239, 68, 68, 0.2);
  color: #f87171;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
}

.thread-cat-pill {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.thread-title {
  margin: 0;
  font-size: 1.05rem;
  line-height: 1.3;
}

.thread-preview {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.thread-meta-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--muted);
  margin-top: 4px;
}

.thread-replies-col {
  display: flex;
  justify-content: flex-end;
}

.replies-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

/* Detail Section */
.thread-detail-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.thread-detail-card {
  padding: 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cat-badge {
  background: rgba(99, 102, 241, 0.15);
  color: #818cf8;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 6px;
}

.date-badge {
  font-size: 12px;
  color: var(--muted);
  margin-left: 8px;
}

.detail-title {
  margin: 0;
  font-size: 1.6rem;
  line-height: 1.3;
}

.author-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 16px;
}

.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #fff;
}

.author-info {
  display: flex;
  flex-direction: column;
}

.author-name {
  font-weight: 700;
}

.author-role {
  font-size: 11px;
  color: var(--muted);
}

.detail-actions {
  margin-left: auto;
}

.detail-content {
  font-size: 15px;
  line-height: 1.65;
}

/* Replies */
.replies-wrapper {
  padding: 28px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.replies-wrapper h3 {
  margin: 0;
  font-size: 1.2rem;
}

.replies-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.reply-card {
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reply-head {
  display: flex;
  align-items: center;
  gap: 10px;
}

.reply-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 12px;
}

.reply-author {
  font-weight: 700;
  font-size: 13px;
}

.reply-time {
  font-size: 11px;
  color: var(--muted);
  margin-left: 8px;
}

.reply-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.5;
}

.empty-replies {
  font-size: 14px;
  padding: 16px 0;
}

.reply-input-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 8px;
}

.reply-form-actions {
  display: flex;
  justify-content: flex-end;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 20px;
}

.modal {
  max-width: 540px;
  width: 100%;
  padding: 28px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 10px;
}

@media (max-width: 900px) {
  .forum-hero {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
