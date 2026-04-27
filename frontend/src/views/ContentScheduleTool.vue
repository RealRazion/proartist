<template>
  <div class="cs-tool">
    <!-- Top bar -->
    <header class="card topbar">
      <div class="topbar-left">
        <p class="eyebrow">Content Schedule</p>
        <h1>Wochenplaner</h1>
      </div>
      <div class="topbar-actions">
        <button class="btn ghost" type="button" @click="clearAll">Alles löschen</button>
        <button class="btn ghost" type="button" @click="router.push({ name: 'platform-content-schedule' })">Landingpage</button>
      </div>
    </header>

    <div class="workspace">
      <!-- Left palette -->
      <aside class="palette card">
        <h2 class="palette-title">Bausteine</h2>
        <p class="muted palette-hint">Ziehe einen Block in einen Wochentag.</p>

        <draggable
          :list="palette"
          :group="{ name: 'blocks', pull: 'clone', put: false }"
          :sort="false"
          item-key="type"
          class="palette-list"
        >
          <template #item="{ element }">
            <div class="palette-item" :data-btype="element.type">
              <span class="palette-icon">{{ element.icon }}</span>
              <div>
                <strong>{{ element.label }}</strong>
                <p class="muted">{{ element.hint }}</p>
              </div>
            </div>
          </template>
        </draggable>

        <!-- Legend -->
        <div class="palette-legend">
          <div class="legend-item" v-for="p in palette" :key="p.type" :data-btype="p.type">
            <span class="dot"></span>{{ p.label }}
          </div>
        </div>
      </aside>

      <!-- Weekly grid -->
      <div class="week-grid">
        <div
          v-for="day in days"
          :key="day.key"
          class="day-column card"
        >
          <div class="day-header">
            <span class="day-name">{{ day.label }}</span>
            <span class="day-count" v-if="schedule[day.key].length">{{ schedule[day.key].length }}</span>
          </div>

          <!-- Drop zone for headers into this day -->
          <draggable
            v-model="schedule[day.key]"
            group="blocks"
            item-key="id"
            class="day-drop"
            ghost-class="ghost-block"
            :animation="150"
            @add="onAdd($event, day.key)"
          >
            <template #item="{ element: block, index: bi }">
              <!-- HEADER block -->
              <div v-if="block.type === 'header'" class="block header-block" :style="{ borderColor: block.color }">
                <div class="block-row">
                  <span class="block-icon">📌</span>
                  <input
                    v-if="block.editing"
                    v-model="block.label"
                    class="block-input"
                    placeholder="Serienname…"
                    @blur="block.editing = false"
                    @keydown.enter="block.editing = false"
                    autofocus
                  />
                  <span v-else class="block-label" @dblclick="block.editing = true" :title="'Doppelklick zum Bearbeiten'">
                    {{ block.label || "Neue Reihe" }}
                  </span>
                  <button class="block-del" type="button" @click="removeBlock(schedule[day.key], bi)" aria-label="Block entfernen">×</button>
                </div>

                <!-- Parts inside this header -->
                <draggable
                  v-model="block.parts"
                  group="blocks"
                  item-key="id"
                  class="parts-drop"
                  ghost-class="ghost-block"
                  :animation="150"
                  @add="onAddPart($event, block)"
                >
                  <template #item="{ element: part, index: pi }">
                    <!-- PART block -->
                    <div v-if="part.type === 'part'" class="block part-block">
                      <div class="block-row">
                        <span class="block-icon">📄</span>
                        <input
                          v-if="part.editing"
                          v-model="part.label"
                          class="block-input"
                          placeholder="Part-Name…"
                          @blur="part.editing = false"
                          @keydown.enter="part.editing = false"
                          autofocus
                        />
                        <span v-else class="block-label" @dblclick="part.editing = true" :title="'Doppelklick zum Bearbeiten'">
                          {{ part.label || "Neuer Part" }}
                        </span>
                        <button class="block-del" type="button" @click="removeBlock(block.parts, pi)" aria-label="Part entfernen">×</button>
                      </div>

                      <!-- Links inside this part -->
                      <draggable
                        v-model="part.links"
                        group="blocks"
                        item-key="id"
                        class="links-drop"
                        ghost-class="ghost-block"
                        :animation="150"
                        @add="onAddLink($event, part)"
                      >
                        <template #item="{ element: link, index: li }">
                          <!-- LINK block -->
                          <div v-if="link.type === 'link'" class="block link-block">
                            <div class="block-row">
                              <span class="block-icon">🔗</span>
                              <input
                                v-model="link.label"
                                class="block-input"
                                placeholder="Beschreibung…"
                              />
                              <button class="block-del" type="button" @click="removeBlock(part.links, li)" aria-label="Link entfernen">×</button>
                            </div>
                            <input
                              v-model="link.url"
                              class="block-input url-input"
                              placeholder="https://…"
                              type="url"
                            />
                          </div>
                          <!-- Wrong block type dropped into links zone -->
                          <div v-else class="block wrong-block">
                            <span class="muted">Hier nur 🔗 Links platzieren</span>
                            <button class="block-del" type="button" @click="removeBlock(part.links, li)">×</button>
                          </div>
                        </template>
                      </draggable>

                      <div class="add-hint muted" v-if="!part.links.length">← 🔗 Link hier fallen lassen</div>
                    </div>
                    <!-- Wrong block type dropped into parts zone -->
                    <div v-else class="block wrong-block">
                      <span class="muted">Hier nur 📄 Parts oder 🔗 Links platzieren</span>
                      <button class="block-del" type="button" @click="removeBlock(block.parts, pi)">×</button>
                    </div>
                  </template>
                </draggable>

                <div class="add-hint muted" v-if="!block.parts.length">← 📄 Part hier fallen lassen</div>
              </div>

              <!-- Wrong block type dropped at day level (not header) -->
              <div v-else class="block wrong-block">
                <span class="muted">Hier zuerst einen 📌 Header platzieren</span>
                <button class="block-del" type="button" @click="removeBlock(schedule[day.key], bi)">×</button>
              </div>
            </template>
          </draggable>

          <div class="drop-hint muted" v-if="!schedule[day.key].length">📌 Header hier ablegen</div>
        </div>
      </div>
    </div>

    <!-- Confirm clear dialog -->
    <div v-if="showClearConfirm" class="overlay" @click.self="showClearConfirm = false">
      <div class="modal card">
        <h2>Plan löschen?</h2>
        <p class="muted">Alle Blöcke werden unwiderruflich entfernt. Fortfahren?</p>
        <div class="modal-actions">
          <button class="btn ghost" type="button" @click="showClearConfirm = false">Abbrechen</button>
          <button class="btn danger" type="button" @click="confirmClear">Löschen</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { VueDraggableNext as draggable } from "vue-draggable-next";

const router = useRouter();
const STORAGE_KEY = "content_schedule_v1";
const showClearConfirm = ref(false);

// --------------- palette ---------------
const palette = [
  { type: "header", icon: "📌", label: "Header", hint: "Neue Content-Reihe anlegen" },
  { type: "part",   icon: "📄", label: "Part",   hint: "Inhaltsteil (z.B. Review)" },
  { type: "link",   icon: "🔗", label: "Link",   hint: "Verlinkung / URL hinzufügen" },
];

// --------------- days ---------------
const days = [
  { key: "mon", label: "Montag" },
  { key: "tue", label: "Dienstag" },
  { key: "wed", label: "Mittwoch" },
  { key: "thu", label: "Donnerstag" },
  { key: "fri", label: "Freitag" },
  { key: "sat", label: "Samstag" },
  { key: "sun", label: "Sonntag" },
];

// --------------- schedule ---------------
function emptySchedule() {
  return Object.fromEntries(days.map((d) => [d.key, []]));
}

function loadSchedule() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    // ignore
  }
  return emptySchedule();
}

const schedule = ref(loadSchedule());

watch(schedule, (val) => {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(val));
  } catch {
    // storage full – silently ignore
  }
}, { deep: true });

// --------------- id helper ---------------
function uid() {
  return crypto.randomUUID ? crypto.randomUUID() : `b${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

// --------------- block factories ---------------
function makeHeader() {
  return { id: uid(), type: "header", label: "", color: randomColor(), editing: true, parts: [] };
}

function makePart() {
  return { id: uid(), type: "part", label: "", editing: true, links: [] };
}

function makeLink() {
  return { id: uid(), type: "link", label: "", url: "" };
}

const COLORS = ["#2f63ff", "#06b6d4", "#10b981", "#f59e0b", "#ef4444", "#a855f7", "#ec4899"];
let _colorIdx = 0;
function randomColor() {
  return COLORS[_colorIdx++ % COLORS.length];
}

// --------------- drop handlers ---------------
// When a block is dropped into a day column (top-level)
function onAdd(evt, dayKey) {
  const added = schedule.value[dayKey][evt.newIndex];
  if (!added) return;
  // Always replace the dropped item with a fresh header instance
  // (palette items lack parts/id; moved blocks already have them)
  if (!Array.isArray(added.parts)) {
    const fresh = makeHeader();
    schedule.value[dayKey].splice(evt.newIndex, 1, fresh);
  }
}

// When a block is dropped into a header's parts zone
function onAddPart(evt, header) {
  const added = header.parts[evt.newIndex];
  if (!added) return;
  if (added.type === "part" && !Array.isArray(added.links)) {
    // came from palette – replace with fresh part
    const fresh = makePart();
    header.parts.splice(evt.newIndex, 1, fresh);
  } else if (added.type !== "part" && added.type !== "link") {
    // wrong type – remove
    header.parts.splice(evt.newIndex, 1);
  }
}

// When a block is dropped into a part's links zone
function onAddLink(evt, part) {
  const added = part.links[evt.newIndex];
  if (!added) return;
  if (added.type === "link" && !added.url && !added.label && !added.id) {
    // came from palette – replace with fresh link
    const fresh = makeLink();
    part.links.splice(evt.newIndex, 1, fresh);
  } else if (added.type !== "link") {
    part.links.splice(evt.newIndex, 1);
  }
}

// --------------- remove helpers ---------------
function removeBlock(arr, idx) {
  arr.splice(idx, 1);
}

// --------------- clear ---------------
function clearAll() {
  showClearConfirm.value = true;
}

function confirmClear() {
  schedule.value = emptySchedule();
  showClearConfirm.value = false;
}
</script>

<style scoped>
.cs-tool {
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  min-height: 100vh;
}

/* ---- Top bar ---- */
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 28px;
  flex-shrink: 0;
}

.topbar-left .eyebrow {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--brand);
  margin: 0 0 4px;
}

.topbar-left h1 {
  font-size: 1.4rem;
  font-weight: 800;
  margin: 0;
}

.topbar-actions {
  display: flex;
  gap: 10px;
}

/* ---- Workspace ---- */
.workspace {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 20px;
  align-items: start;
  min-height: 0;
}

/* ---- Palette ---- */
.palette {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: sticky;
  top: 20px;
}

.palette-title {
  font-size: 1rem;
  font-weight: 700;
  margin: 0;
}

.palette-hint {
  font-size: 0.82rem;
  margin: 0;
}

.palette-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.palette-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1.5px dashed var(--border);
  cursor: grab;
  background: var(--bg-soft);
  transition: border-color 0.2s, background 0.2s;
  user-select: none;
}

.palette-item:active {
  cursor: grabbing;
}

.palette-item[data-btype="header"] { border-color: #2f63ff; }
.palette-item[data-btype="part"]   { border-color: #10b981; }
.palette-item[data-btype="link"]   { border-color: #a855f7; }

.palette-item:hover {
  background: var(--card);
}

.palette-icon {
  font-size: 1.4rem;
  flex-shrink: 0;
}

.palette-item strong {
  font-size: 0.9rem;
  display: block;
}

.palette-item p {
  margin: 2px 0 0;
  font-size: 0.78rem;
}

.palette-legend {
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-top: 1px solid var(--border);
  padding-top: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.82rem;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-item[data-btype="header"] .dot { background: #2f63ff; }
.legend-item[data-btype="part"]   .dot { background: #10b981; }
.legend-item[data-btype="link"]   .dot { background: #a855f7; }

/* ---- Week grid ---- */
.week-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 12px;
  align-items: start;
}

.day-column {
  padding: 14px 10px;
  min-height: 300px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.day-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 4px;
}

.day-name {
  font-size: 0.82rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--brand);
}

.day-count {
  background: var(--brand);
  color: #fff;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
}

.day-drop {
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-height: 80px;
  flex: 1;
}

/* ---- Generic block ---- */
.block {
  border-radius: 10px;
  border: 1.5px solid var(--border);
  background: var(--card);
  padding: 10px 10px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  box-shadow: var(--shadow-soft);
  transition: box-shadow 0.2s;
}

.block:hover {
  box-shadow: var(--shadow-strong);
}

.block-row {
  display: flex;
  align-items: center;
  gap: 6px;
}

.block-icon {
  font-size: 1rem;
  flex-shrink: 0;
}

.block-label {
  flex: 1;
  font-size: 0.88rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: text;
}

.block-input {
  flex: 1;
  background: var(--input-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 4px 8px;
  font-size: 0.85rem;
  color: var(--text);
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
  min-width: 0;
}

.block-input:focus {
  border-color: var(--brand);
  background: var(--input-bg-focus);
}

.url-input {
  width: 100%;
}

.block-del {
  background: none;
  border: none;
  color: var(--muted);
  font-size: 1rem;
  cursor: pointer;
  padding: 0 4px;
  line-height: 1;
  flex-shrink: 0;
  border-radius: 4px;
  transition: color 0.2s, background 0.2s;
}

.block-del:hover {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
}

/* ---- Header block ---- */
.header-block {
  border-left: 4px solid var(--brand);
}

/* ---- Parts drop zone ---- */
.parts-drop {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 6px 0 2px 8px;
  min-height: 32px;
}

/* ---- Part block ---- */
.part-block {
  background: var(--bg-soft);
  border-color: #10b981;
}

/* ---- Links drop zone ---- */
.links-drop {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 4px 0 2px 8px;
  min-height: 24px;
}

/* ---- Link block ---- */
.link-block {
  background: var(--surface);
  border-color: #a855f7;
  gap: 4px;
}

/* ---- Wrong block ---- */
.wrong-block {
  border-color: #ef4444;
  background: rgba(239, 68, 68, 0.05);
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
  font-size: 0.8rem;
  padding: 8px 10px;
}

/* ---- Hints ---- */
.add-hint,
.drop-hint {
  font-size: 0.75rem;
  text-align: center;
  padding: 6px;
  border: 1.5px dashed var(--border);
  border-radius: 8px;
  user-select: none;
}

.drop-hint {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60px;
}

/* ---- Ghost (drag preview) ---- */
.ghost-block {
  opacity: 0.4;
  background: rgba(47, 99, 255, 0.08);
  border: 1.5px dashed var(--brand) !important;
}

/* ---- Modal / Confirm ---- */
.overlay {
  position: fixed;
  inset: 0;
  background: var(--modal-overlay);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  padding: 36px;
  max-width: 420px;
  width: 90%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal h2 {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
}

.modal p {
  margin: 0;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

/* ---- Responsive ---- */
@media (max-width: 1280px) {
  .week-grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
  }
}

@media (max-width: 900px) {
  .workspace {
    grid-template-columns: 1fr;
  }

  .palette {
    position: static;
    flex-direction: row;
    flex-wrap: wrap;
    gap: 8px;
  }

  .palette-title,
  .palette-hint,
  .palette-legend {
    flex-basis: 100%;
  }

  .palette-list {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .week-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 600px) {
  .cs-tool {
    padding: 12px;
  }

  .topbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 16px;
  }

  .week-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
