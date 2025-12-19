<template>
  <div class="chat">
    <aside class="card">
      <div class="aside-header">
        <h3>Chats</h3>
        <button class="btn ghost" type="button" @click="loadThreads" :disabled="loadingThreads">
          Aktualisieren
        </button>
      </div>
      <div class="list">
        <div
          v-for="t in threads"
          :key="t.id"
          class="thread"
          :class="{ active: t.id === activeId }"
          role="button"
          tabindex="0"
          @click="select(t)"
          @keydown.enter.prevent="select(t)"
        >
          <div class="avatar">{{ initial(t) }}</div>
          <div>
            <div class="name">{{ threadTitle(t) }}</div>
            <div class="muted">{{ threadPreview(t) }}</div>
          </div>
        </div>
        <div v-if="!threads.length && !loadingThreads" class="empty muted">Noch keine Konversationen.</div>
      </div>
    </aside>

    <section class="card conversation">
      <div class="conversation-body">
        <header v-if="activeThread" class="thread-header">
          <div class="avatar large">{{ initial(activeThread) }}</div>
          <div>
            <div class="name">{{ threadTitle(activeThread) }}</div>
            <div class="muted">{{ threadPreview(activeThread) }}</div>
          </div>
        </header>

        <div class="messages" ref="msgBox">
          <div v-if="!messages.length" class="empty muted">
            Noch keine Nachrichten ? starte die Unterhaltung.
          </div>
          <div
            v-for="m in messages"
            :key="m.id"
            class="msg"
            :class="m.sender === meId ? 'me' : 'other'"
          >
            <div class="meta">
              <span class="author">{{ m.sender === meId ? "Du" : m.sender_name || "Kontakt" }}</span>
              <span class="time">{{ formatMessageTime(m.created_at) }}</span>
            </div>
            <div v-if="m.file_url" class="file">
              <a :href="m.file_url" target="_blank" rel="noopener" class="link">
                ?? {{ m.file_name || extractFilename(m.file_url) }}
              </a>
              <span v-if="m.file_size" class="file-meta">{{ formatFileSize(m.file_size) }}</span>
            </div>
            <div v-if="m.text" class="text">{{ m.text }}</div>
            <div v-if="m.sender === meId" class="read-indicator" :class="{ seen: m.read }">
              {{ m.read ? "Gelesen" : "Gesendet" }}
            </div>
          </div>
        </div>

        <p v-if="typingDisplay" class="typing-indicator">{{ typingDisplay }}</p>

        <div class="send">
          <textarea
            ref="composerRef"
            class="input"
            :disabled="!activeId"
            rows="2"
            v-model="text"
            @keydown="handleInputKeydown"
            @input="handleComposerInput"
            @blur="handleComposerBlur"
            placeholder="Nachricht schreiben..."
          ></textarea>
          <div class="actions">
            <label class="file-btn" :class="{ disabled: !activeId || uploading }">
              <input type="file" :disabled="!activeId || uploading" @change="sendFile" />
              <span>??</span>
            </label>
            <button class="btn" type="button" @click="sendWS" :disabled="!canSend">
              {{ isWsReady ? "Senden" : "Verbinde..." }}
            </button>
          </div>
        </div>
        <p v-if="activeId && !isWsReady" class="status muted">Verbindung wird hergestellt...</p>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount, nextTick } from "vue";
import { useRoute, useRouter } from "vue-router";
import api from "../api";

const POLL_INTERVAL = 20000;
const PENDING_THREAD_KEY = "chat:pendingThread";

const route = useRoute();
const router = useRouter();

const meId = ref(null);
const threads = ref([]);
const activeId = ref(null);
const messages = ref([]);
const text = ref("");
const ws = ref(null);
const msgBox = ref(null);
const composerRef = ref(null);
const isWsReady = ref(false);
const loadingThreads = ref(false);
const uploading = ref(false);
const typingInfo = ref({});

let pollHandle = null;
let reconnectHandle = null;
let typingNotifyTimer = null;
let readReceiptTimer = null;
let readReceiptQueued = false;
const typingTimers = new Map();
let composerTyping = false;

const activeThread = computed(() => threads.value.find((t) => t.id === activeId.value) || null);
const canSend = computed(() => Boolean(text.value.trim()) && isWsReady.value && Boolean(activeId.value));
const typingDisplay = computed(() => {
  const thread = activeThread.value;
  if (!thread) return "";
  const others = participantList(thread).filter((p) => p.id !== meId.value && typingInfo.value[p.id]);
  if (!others.length) return "";
  const names = others.map((p) => p.name || "Kontakt");
  if (names.length === 1) return `${names[0]} tippt...`;
  if (names.length === 2) return `${names[0]} und ${names[1]} tippen...`;
  return "Mehrere tippen...";
});

function normalizeMessage(msg) {
  return {
    ...msg,
    read: Boolean(msg.read),
    file_name: msg.file_name || null,
    file_size: typeof msg.file_size === "number" ? msg.file_size : msg.file_size ? Number(msg.file_size) : null,
  };
}

function normalizeThread(thread) {
  const normalized = {
    ...thread,
    messages: [...(thread.messages || [])].map(normalizeMessage),
  };
  normalized.messages.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  return normalized;
}

function lastActivity(thread) {
  const last = thread.messages?.[thread.messages.length - 1];
  const ts = last?.created_at || thread.created_at;
  return ts ? new Date(ts).getTime() : 0;
}

function sortThreads(list) {
  return [...list].sort((a, b) => lastActivity(b) - lastActivity(a));
}

function upsertThread(thread) {
  const normalized = normalizeThread(thread);
  const others = threads.value.filter((t) => t.id !== normalized.id);
  threads.value = sortThreads([...others, normalized]);
  if (activeId.value === normalized.id) {
    messages.value = normalized.messages;
  }
}

function participantList(thread) {
  return Array.isArray(thread.participants) ? thread.participants : [];
}

function otherParticipant(thread) {
  const participants = participantList(thread);
  if (!participants.length) return null;
  if (!meId.value) return participants[0];
  return participants.find((p) => p.id !== meId.value) || participants[0];
}

function threadTitle(thread) {
  const other = otherParticipant(thread);
  return (other?.name || "").trim() || `Chat #${thread.id}`;
}

function initial(thread) {
  const name = threadTitle(thread);
  return (name || "#").charAt(0).toUpperCase();
}

function threadPreview(thread) {
  const last = thread.messages?.[thread.messages.length - 1];
  if (!last) return "Noch keine Nachrichten";
  if (last.text) {
    return last.text.length > 60 ? `${last.text.slice(0, 57)}...` : last.text;
  }
  if (last.file_url) return "Anhang gesendet";
  return "Neue Aktivität";
}

function extractFilename(url) {
  if (!url) return "Anhang";
  try {
    return decodeURIComponent(url.split("/").pop() || "Anhang");
  } catch {
    return "Anhang";
  }
}

function formatFileSize(bytes) {
  if (!bytes || Number.isNaN(bytes)) return "";
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

function hasUnreadMessages() {
  return messages.value.some((msg) => msg.sender !== meId.value && !msg.read);
}

function scheduleReadReceipt(immediate = false) {
  if (!activeId.value || !hasUnreadMessages()) return;
  if (!ws.value || ws.value.readyState !== 1) {
    readReceiptQueued = true;
    return;
  }
  const send = () => {
    if (!ws.value || ws.value.readyState !== 1) {
      readReceiptQueued = true;
      return;
    }
    ws.value.send(JSON.stringify({ type: "read" }));
    readReceiptQueued = false;
  };
  if (immediate) {
    send();
    return;
  }
  if (readReceiptTimer) clearTimeout(readReceiptTimer);
  readReceiptTimer = setTimeout(send, 200);
}

function applyReadReceipt(ids) {
  if (!Array.isArray(ids) || !ids.length) return;
  const idSet = new Set(ids.map((id) => Number(id)));
  const updated = messages.value.map((msg) =>
    idSet.has(Number(msg.id)) ? { ...msg, read: true } : msg
  );
  messages.value = updated;
  const current = threads.value.find((t) => t.id === activeId.value);
  if (current) {
    upsertThread({ ...current, messages: updated });
  }
}

function setTyping(profileId, isTyping) {
  if (!profileId || profileId === meId.value) return;
  const current = { ...typingInfo.value };
  if (isTyping) {
    current[profileId] = true;
    typingInfo.value = current;
    if (typingTimers.has(profileId)) clearTimeout(typingTimers.get(profileId));
    typingTimers.set(
      profileId,
      setTimeout(() => {
        typingTimers.delete(profileId);
        const copy = { ...typingInfo.value };
        delete copy[profileId];
        typingInfo.value = copy;
      }, 2500)
    );
  } else {
    if (typingTimers.has(profileId)) {
      clearTimeout(typingTimers.get(profileId));
      typingTimers.delete(profileId);
    }
    if (current[profileId]) {
      delete current[profileId];
      typingInfo.value = { ...current };
    }
  }
}

function handleComposerInput() {
  if (!ws.value || ws.value.readyState !== 1 || !activeId.value) return;
  if (!composerTyping) {
    composerTyping = true;
    ws.value.send(JSON.stringify({ type: "typing", is_typing: true }));
  }
  if (typingNotifyTimer) clearTimeout(typingNotifyTimer);
  typingNotifyTimer = setTimeout(() => {
    if (!ws.value || ws.value.readyState !== 1) {
      composerTyping = false;
      typingNotifyTimer = null;
      return;
    }
    ws.value.send(JSON.stringify({ type: "typing", is_typing: false }));
    composerTyping = false;
    typingNotifyTimer = null;
  }, 1500);
  nextTick(resizeComposer);
}

function handleComposerBlur() {
  if (typingNotifyTimer) {
    clearTimeout(typingNotifyTimer);
    typingNotifyTimer = null;
  }
  if (composerTyping && ws.value && ws.value.readyState === 1) {
    ws.value.send(JSON.stringify({ type: "typing", is_typing: false }));
  }
  composerTyping = false;
}

function scrollBottom() {
  requestAnimationFrame(() => {
    if (msgBox.value) {
      msgBox.value.scrollTop = msgBox.value.scrollHeight;
    }
  });
}

function appendMessage(msg) {
  const normalized = normalizeMessage(msg);
  const updatedMessages = [...messages.value, normalized];
  messages.value = updatedMessages;
  const current = activeThread.value;
  if (current) {
    upsertThread({ ...current, messages: updatedMessages });
  } else {
    loadThreads();
  }
  scrollBottom();
  if (normalized.sender !== meId.value) {
    scheduleReadReceipt();
  }
}

async function loadMe() {
  try {
    const res = await api.get("profiles/me/");
    meId.value = res.data.id;
  } catch (err) {
    console.error("Profil laden fehlgeschlagen", err);
  }
}

async function loadThreads() {
  if (loadingThreads.value) return;
  loadingThreads.value = true;
  try {
    const res = await api.get("threads/");
    const normalized = res.data.map(normalizeThread);
    threads.value = sortThreads(normalized);
    if (activeId.value) {
      const current = threads.value.find((t) => t.id === activeId.value);
      if (current) {
        messages.value = current.messages;
        scheduleReadReceipt();
      }
    }
  } catch (err) {
    console.error("Threads laden fehlgeschlagen", err);
  } finally {
    loadingThreads.value = false;
  }
}

async function openThread(id, { updateRoute = true, fetchFresh = true } = {}) {
  if (!id) return;
  if (activeId.value !== id) {
    activeId.value = id;
  }
  if (updateRoute) {
    router.replace({ query: { ...route.query, thread: id } });
  }
  let thread = threads.value.find((t) => t.id === id) || null;
  if (fetchFresh) {
    try {
      const res = await api.get(`threads/${id}/`);
      thread = res.data;
    } catch (err) {
      console.error("Thread-Details laden fehlgeschlagen", err);
    }
  }
  if (thread) {
    const normalized = normalizeThread(thread);
    messages.value = normalized.messages;
    upsertThread(normalized);
  } else {
    messages.value = [];
  }
  openWS();
  scrollBottom();
  scheduleReadReceipt(isWsReady.value);
}

function select(thread) {
  if (!thread) return;
  if (thread.id === activeId.value && isWsReady.value) return;
  typingInfo.value = {};
  typingTimers.forEach((timeout) => clearTimeout(timeout));
  typingTimers.clear();
  openThread(thread.id);
}

function buildWsUrl() {
  const token = localStorage.getItem("access") || "";
  const base = new URL(api.defaults.baseURL || window.location.origin);
  const wsProto = base.protocol === "https:" ? "wss:" : "ws:";
  const wsHost = base.host;
  const wsPath = base.pathname.replace(/\/api\/?$/, "");
  const cleanedPath = wsPath.endsWith("/") ? wsPath.slice(0, -1) : wsPath;
  return `${wsProto}//${wsHost}${cleanedPath}/ws/chat/${activeId.value}/?token=${token}`;
}

function openWS() {
  if (!activeId.value) return;
  isWsReady.value = false;
  if (reconnectHandle) {
    clearTimeout(reconnectHandle);
    reconnectHandle = null;
  }
  if (ws.value) {
    ws.value.onopen = null;
    ws.value.onclose = null;
    ws.value.onmessage = null;
    ws.value.onerror = null;
    ws.value.close();
  }
  try {
    ws.value = new WebSocket(buildWsUrl());
  } catch (err) {
    console.error("WebSocket konnte nicht geöffnet werden", err);
    return;
  }
  ws.value.onopen = () => {
    isWsReady.value = true;
    if (readReceiptQueued || hasUnreadMessages()) {
      scheduleReadReceipt(true);
    }
  };
  ws.value.onmessage = (event) => {
    try {
      const payload = JSON.parse(event.data);
      if (payload && payload.event === "typing") {
        setTyping(payload.profile, payload.is_typing);
      } else if (payload && payload.event === "read") {
        applyReadReceipt(payload.message_ids || []);
      } else if (payload && payload.event === "message") {
        const msg = payload.message || payload;
        appendMessage(msg);
      } else {
        appendMessage(payload);
      }
    } catch (err) {
      console.error("Nachricht konnte nicht verarbeitet werden", err);
    }
  };
  ws.value.onclose = () => {
    isWsReady.value = false;
    if (activeId.value) {
      reconnectHandle = setTimeout(() => openWS(), 1500);
    }
  };
  ws.value.onerror = () => {
    isWsReady.value = false;
  };
}

function sendWS() {
  if (!canSend.value || !ws.value || ws.value.readyState !== 1) return;
  const payload = text.value.trim();
  if (!payload) return;
  handleComposerBlur();
  ws.value.send(JSON.stringify({ text: payload }));
  text.value = "";
  nextTick(resizeComposer);
}

async function sendFile(event) {
  const file = event.target.files?.[0];
  event.target.value = "";
  if (!file || !activeId.value) return;
  const formData = new FormData();
  formData.append("thread", activeId.value);
  formData.append("file", file);
  uploading.value = true;
  try {
    const res = await api.post("messages/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    appendMessage(res.data);
  } catch (err) {
    console.error("Datei konnte nicht gesendet werden", err);
  } finally {
    uploading.value = false;
  }
}

function resizeComposer() {
  const el = composerRef.value;
  if (!el) return;
  el.style.height = "auto";
  const nextHeight = Math.min(240, Math.max(80, el.scrollHeight));
  el.style.height = `${nextHeight}px`;
}

function handleInputKeydown(event) {
  if (event.key !== "Enter") return;
  if (event.shiftKey) return;
  event.preventDefault();
  sendWS();
}

function formatMessageTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

watch(
  () => route.query.thread,
  (threadId) => {
    const numericId = Number(threadId);
    if (!numericId) return;
    typingInfo.value = {};
    typingTimers.forEach((timeout) => clearTimeout(timeout));
    typingTimers.clear();
    if (numericId !== activeId.value) {
      openThread(numericId, { updateRoute: false });
    } else if (hasUnreadMessages()) {
      scheduleReadReceipt();
    }
  }
);

watch(
  () => text.value,
  () => nextTick(resizeComposer)
);

watch(
  () => activeId.value,
  () => nextTick(resizeComposer)
);

onMounted(async () => {
  await loadMe();
  await loadThreads();
  const initialId = Number(route.query.thread || 0);
  if (initialId) {
    await openThread(initialId, { updateRoute: false });
  } else if (threads.value.length) {
    await openThread(threads.value[0].id, { updateRoute: false, fetchFresh: false });
  }
  let storedThread = 0;
  if (typeof window !== "undefined") {
    storedThread = Number(sessionStorage.getItem(PENDING_THREAD_KEY) || 0);
  }
  if (storedThread && storedThread !== initialId) {
    sessionStorage.removeItem(PENDING_THREAD_KEY);
    await openThread(storedThread, { updateRoute: true });
  } else if (storedThread) {
    sessionStorage.removeItem(PENDING_THREAD_KEY);
  }
  pollHandle = setInterval(loadThreads, POLL_INTERVAL);
  nextTick(resizeComposer);
});

onBeforeUnmount(() => {
  if (pollHandle) clearInterval(pollHandle);
  if (reconnectHandle) clearTimeout(reconnectHandle);
  handleComposerBlur();
  typingTimers.forEach((timeout) => clearTimeout(timeout));
  typingTimers.clear();
  typingInfo.value = {};
  if (readReceiptTimer) clearTimeout(readReceiptTimer);
  readReceiptTimer = null;
  if (ws.value && ws.value.readyState === 1 && composerTyping) {
    ws.value.send(JSON.stringify({ type: "typing", is_typing: false }));
  }
  composerTyping = false;
  activeId.value = null;
  if (ws.value) {
    ws.value.close();
    ws.value = null;
  }
  if (typeof window !== "undefined") {
    sessionStorage.removeItem(PENDING_THREAD_KEY);
  }
});
</script>

<style scoped>
.chat{display:grid;grid-template-columns:minmax(220px,300px) minmax(0,1fr);gap:18px;min-height:74vh;width:100%;}
.card{background:#0f1115;border:1px solid #1c2230;border-radius:14px;padding:16px;color:#e8eaf0;display:flex;flex-direction:column;gap:16px;}
.conversation{padding:0;}
.conversation-body{display:flex;flex-direction:column;gap:16px;height:100%;padding:18px 20px;}
.aside-header{display:flex;align-items:center;justify-content:space-between;}
.list{display:flex;flex-direction:column;gap:8px;max-height:70vh;overflow:auto;padding-right:4px;}
.thread{display:flex;gap:12px;padding:10px;border-radius:10px;cursor:pointer;border:1px solid transparent;transition:background .2s,border-color .2s;}
.thread:hover{background:#131826;border-color:#1f2740;}
.thread.active{background:#151b2b;border-color:#2a3658;}
.avatar{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center;background:#23304d;color:#fff;font-weight:700;flex-shrink:0;text-transform:uppercase;}
.avatar.large{width:48px;height:48px;font-size:1.2rem;}
.name{font-weight:700;}
.muted{font-size:12px;color:#9aa3b2;}
.empty{padding:16px 8px;text-align:center;}
.thread-header{display:flex;gap:12px;align-items:center;margin-bottom:-8px;}
.chat section.card{width:100%;}
.messages{flex:1;min-height:65vh;overflow:auto;display:flex;flex-direction:column;gap:12px;padding:16px;background:#0c0f15;border-radius:10px;border:1px solid #1a2235;width:100%;}
.msg{max-width:85%;width:fit-content;padding:12px 14px;border-radius:12px;line-height:1.5;background:#1b2133;display:flex;flex-direction:column;gap:6px;}
.msg.me{align-self:flex-end;background:#243b55;}
.msg.other{align-self:flex-start;}
.msg .meta{display:flex;gap:8px;font-size:11px;color:#98a3b7;text-transform:uppercase;letter-spacing:.06em;}
.msg .file{font-size:13px;}
.msg .text{white-space:pre-wrap;word-break:break-word;}
.msg .link{color:#9eb7ff;text-decoration:none;}
.msg .link:hover{text-decoration:underline;}
.msg .file-meta{display:block;font-size:11px;color:#98a3b7;margin-top:2px;}
.msg .read-indicator{font-size:11px;align-self:flex-end;margin-top:4px;color:#9aa3b2;}
.msg .read-indicator.seen{color:#34d399;}
.msg .meta .time{margin-left:auto;opacity:.8;text-transform:none;letter-spacing:0;}
.typing-indicator{font-size:12px;color:#9aa3b2;margin:6px 0;}
.send{display:flex;gap:12px;align-items:flex-end;margin-top:12px;}
.input{flex:1;min-height:80px;max-height:220px;padding:12px 14px;border-radius:12px;border:1px solid #2a3658;background:#0f1422;color:#e8eaf0;resize:none;font:inherit;line-height:1.5;}
.input:disabled{opacity:.6;cursor:not-allowed;}
.actions{display:flex;gap:12px;align-items:center;}
.file-btn{width:44px;height:44px;border-radius:12px;border:1px solid #2a3658;background:#18213a;color:#e8eaf0;display:flex;align-items:center;justify-content:center;cursor:pointer;transition:background .2s,border-color .2s;}
.file-btn:hover{background:#1f2a4a;}
.file-btn.disabled{opacity:.5;cursor:not-allowed;}
.file-btn input{display:none;}
.btn{padding:10px 16px;border:1px solid #2a3658;background:#18213a;border-radius:12px;color:#e8eaf0;cursor:pointer;transition:background .2s,border-color .2s;}
.btn:hover:not(:disabled){background:#1f2a4a;}
.btn:disabled{opacity:.5;cursor:not-allowed;}
.btn-ghost{background:transparent;border-color:transparent;color:#9aa3b2;padding:6px 10px;}
.btn-ghost:hover:not(:disabled){color:#e8eaf0;border-color:#2a3658;background:#151b2b;}
.status{margin:0;font-size:12px;}
@media(max-width:1024px){
  .chat{grid-template-columns:1fr;}
  .aside-header{flex-direction:column;align-items:flex-start;gap:8px;}
}
</style>








