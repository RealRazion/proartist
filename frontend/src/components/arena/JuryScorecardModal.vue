<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-card jury-modal-card card">
      <!-- Modal Header -->
      <div class="modal-header">
        <div>
          <span class="jury-sub-badge">⚖️ UNYQ OFFICIAL JURY SCORECARD</span>
          <h3 class="modal-title">Jury-Bewertung & Punktentscheid</h3>
          <p class="muted small">
            Bewerte beide Kontrahenten nach den 4 offiziellen UNYQ Kriterien (max. 40 Punkte).
          </p>
        </div>
        <button class="modal-close-btn" @click="$emit('close')">✕</button>
      </div>

      <!-- Battle Match Header -->
      <div class="battle-pairing-header">
        <div class="pairing-contender left">
          <span class="contender-name">{{ battle.left_profile_name || 'Artist Links' }}</span>
          <span class="contender-total" :class="{ leading: leftTotalScore > rightTotalScore }">
            {{ leftTotalScore }} / 40 Pkt
          </span>
        </div>
        <div class="pairing-vs-center">
          <span class="vs-label">VS</span>
          <span v-if="scoreDiff !== 0" class="score-diff-badge" :class="leftTotalScore > rightTotalScore ? 'left-lead' : 'right-lead'">
            {{ leftTotalScore > rightTotalScore ? `+${scoreDiff} ${battle.left_profile_name || 'Links'}` : `+${scoreDiff} ${battle.right_profile_name || 'Rechts'}` }}
          </span>
          <span v-else class="score-diff-badge tie">Unentschieden</span>
        </div>
        <div class="pairing-contender right">
          <span class="contender-name">{{ battle.right_profile_name || 'Artist Rechts' }}</span>
          <span class="contender-total" :class="{ leading: rightTotalScore > leftTotalScore }">
            {{ rightTotalScore }} / 40 Pkt
          </span>
        </div>
      </div>

      <!-- Evaluation Grid -->
      <div class="criteria-evaluation-body">
        <div
          v-for="criterion in criteriaList"
          :key="criterion.key"
          class="criterion-row card"
        >
          <div class="criterion-info">
            <span class="criterion-icon">{{ criterion.icon }}</span>
            <div class="criterion-texts">
              <strong class="criterion-name">{{ criterion.label }}</strong>
              <small class="muted criterion-desc">{{ criterion.desc }}</small>
            </div>
          </div>

          <!-- Dual Sliders: Left vs Right -->
          <div class="criterion-sliders-wrap">
            <!-- Left Contender Rating -->
            <div class="slider-box left-slider-box">
              <div class="slider-meta">
                <span class="artist-mini-tag">{{ battle.left_profile_name || 'Links' }}</span>
                <span class="score-value">{{ leftScores[criterion.key] }} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                v-model.number="leftScores[criterion.key]"
                class="score-range range-amber"
              />
            </div>

            <!-- Right Contender Rating -->
            <div class="slider-box right-slider-box">
              <div class="slider-meta">
                <span class="artist-mini-tag right-tag">{{ battle.right_profile_name || 'Rechts' }}</span>
                <span class="score-value">{{ rightScores[criterion.key] }} / 10</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                step="1"
                v-model.number="rightScores[criterion.key]"
                class="score-range range-blue"
              />
            </div>
          </div>
        </div>

        <!-- Jury Comments & Feedback -->
        <div class="jury-feedback-field">
          <label class="field-label">
            📝 Offizielle Jury-Begründung / Feedback:
          </label>
          <textarea
            v-model="juryNotes"
            rows="3"
            placeholder="z. B. Artist A überzeugte mit sauberem 808-Mix und kreativem Switch in Hook, Artist B hatte starke Delivery..."
            class="input-field-area"
          ></textarea>
        </div>
      </div>

      <!-- Modal Footer & Decision Actions -->
      <div class="modal-footer">
        <button class="btn ghost btn-sm" @click="$emit('close')">Abbrechen</button>
        <div class="decision-buttons-group">
          <!-- Point Verdict Button -->
          <button
            class="btn btn-points-verdict"
            :disabled="leftTotalScore === rightTotalScore"
            @click="submitPointsDecision"
          >
            🏆 Nach Punkten entscheiden ({{ recommendedWinnerName }})
          </button>

          <!-- Manual Overrides -->
          <button
            class="btn ghost btn-sm"
            @click="submitManualDecision('left')"
          >
            Manuell: {{ battle.left_profile_name || 'Links' }} Sieg
          </button>
          <button
            class="btn ghost btn-sm"
            @click="submitManualDecision('right')"
          >
            Manuell: {{ battle.right_profile_name || 'Rechts' }} Sieg
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from "vue";

const props = defineProps({
  show: {
    type: Boolean,
    default: false,
  },
  battle: {
    type: Object,
    required: true,
  },
});

const emit = defineEmits(["close", "submitScorecard"]);

const criteriaList = [
  {
    key: "flow",
    icon: "🎤",
    label: "Flow, Delivery & Rhythmus",
    desc: "Taktgefühl, Energie, Dynamik und Stimmführung bzw. Hook",
  },
  {
    key: "sound",
    icon: "🎛️",
    label: "Sound-Design & Mix / Master",
    desc: "Frequenz-Balance, 808-Druck, Transparenz und Stereo-Breite",
  },
  {
    key: "arrangement",
    icon: "🎼",
    label: "Arrangement & Songwriting",
    desc: "Spannungsbogen, Übergänge, Melodieführung und Beat-Struktur",
  },
  {
    key: "creativity",
    icon: "⚡",
    label: "Kreativität & Punchlines / Vibe",
    desc: "Originalität, Überraschungsmomente und Wiedererkennungswert",
  },
];

const leftScores = reactive({
  flow: 8,
  sound: 8,
  arrangement: 8,
  creativity: 8,
});

const rightScores = reactive({
  flow: 7,
  sound: 7,
  arrangement: 7,
  creativity: 7,
});

const juryNotes = ref("");

// Reset defaults when battle changes
watch(
  () => props.battle?.id,
  () => {
    leftScores.flow = 8;
    leftScores.sound = 8;
    leftScores.arrangement = 8;
    leftScores.creativity = 8;
    rightScores.flow = 7;
    rightScores.sound = 7;
    rightScores.arrangement = 7;
    rightScores.creativity = 7;
    juryNotes.value = "";
  }
);

const leftTotalScore = computed(() => {
  return (
    Number(leftScores.flow) +
    Number(leftScores.sound) +
    Number(leftScores.arrangement) +
    Number(leftScores.creativity)
  );
});

const rightTotalScore = computed(() => {
  return (
    Number(rightScores.flow) +
    Number(rightScores.sound) +
    Number(rightScores.arrangement) +
    Number(rightScores.creativity)
  );
});

const scoreDiff = computed(() => {
  return Math.abs(leftTotalScore.value - rightTotalScore.value);
});

const recommendedWinner = computed(() => {
  if (leftTotalScore.value > rightTotalScore.value) return "left";
  if (rightTotalScore.value > leftTotalScore.value) return "right";
  return null;
});

const recommendedWinnerName = computed(() => {
  if (recommendedWinner.value === "left") {
    return `${props.battle.left_profile_name || 'Links'} (+${scoreDiff.value} Pkt)`;
  }
  if (recommendedWinner.value === "right") {
    return `${props.battle.right_profile_name || 'Rechts'} (+${scoreDiff.value} Pkt)`;
  }
  return "Unentschieden";
});

function submitPointsDecision() {
  if (!recommendedWinner.value) return;
  emit("submitScorecard", {
    battle: props.battle,
    decision: recommendedWinner.value,
    leftScores: { ...leftScores },
    rightScores: { ...rightScores },
    leftTotal: leftTotalScore.value,
    rightTotal: rightTotalScore.value,
    juryNotes: juryNotes.value,
  });
}

function submitManualDecision(decision) {
  emit("submitScorecard", {
    battle: props.battle,
    decision,
    leftScores: { ...leftScores },
    rightScores: { ...rightScores },
    leftTotal: leftTotalScore.value,
    rightTotal: rightTotalScore.value,
    juryNotes: juryNotes.value,
  });
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.78);
  backdrop-filter: blur(10px);
  z-index: 10000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.jury-modal-card {
  width: 100%;
  max-width: 680px;
  max-height: 90vh;
  overflow-y: auto;
  background: linear-gradient(135deg, rgba(28, 22, 45, 0.98), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 22px;
  padding: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.jury-sub-badge {
  font-size: 10px;
  font-weight: 800;
  color: #fbbf24;
  letter-spacing: 1px;
}

.modal-title {
  font-size: 20px;
  margin: 4px 0 2px;
  color: #fff;
}

.modal-close-btn {
  background: transparent;
  border: none;
  font-size: 20px;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  padding: 4px 8px;
}

/* Pairing Header */
.battle-pairing-header {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 12px;
  align-items: center;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 12px 16px;
  margin-bottom: 18px;
}

.pairing-contender {
  display: flex;
  flex-direction: column;
}

.pairing-contender.left {
  align-items: flex-start;
}

.pairing-contender.right {
  align-items: flex-end;
}

.contender-name {
  font-size: 14px;
  font-weight: 700;
  color: #fff;
}

.contender-total {
  font-size: 18px;
  font-weight: 900;
  color: var(--text-muted, #94a3b8);
}

.contender-total.leading {
  color: #fbbf24;
  text-shadow: 0 0 10px rgba(245, 158, 11, 0.5);
}

.pairing-vs-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.vs-label {
  font-size: 12px;
  font-weight: 800;
  color: var(--text-muted, #94a3b8);
}

.score-diff-badge {
  font-size: 10px;
  font-weight: 800;
  padding: 2px 8px;
  border-radius: 6px;
}

.score-diff-badge.left-lead {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

.score-diff-badge.right-lead {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.score-diff-badge.tie {
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-muted, #94a3b8);
}

/* Criteria List */
.criteria-evaluation-body {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.criterion-row {
  background: rgba(18, 21, 35, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 12px 14px;
}

.criterion-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.criterion-icon {
  font-size: 18px;
}

.criterion-texts {
  display: flex;
  flex-direction: column;
}

.criterion-name {
  font-size: 13px;
  color: #fff;
}

.criterion-desc {
  font-size: 11px;
}

.criterion-sliders-wrap {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.slider-box {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  padding: 8px 10px;
}

.slider-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 11px;
}

.artist-mini-tag {
  font-weight: 700;
  color: #fbbf24;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.artist-mini-tag.right-tag {
  color: #60a5fa;
}

.score-value {
  font-weight: 800;
  color: #fff;
}

.score-range {
  width: 100%;
  accent-color: #f59e0b;
  cursor: pointer;
}

.score-range.range-blue {
  accent-color: #3b82f6;
}

/* Jury Notes */
.jury-feedback-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}

.field-label {
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.input-field-area {
  width: 100%;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 10px;
  padding: 10px;
  color: #fff;
  font-family: inherit;
  font-size: 12px;
  resize: vertical;
}

.input-field-area:focus {
  outline: none;
  border-color: #f59e0b;
}

/* Modal Footer */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding-top: 14px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.decision-buttons-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-points-verdict {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #000;
  font-weight: 800;
  border: none;
}

.btn-points-verdict:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
