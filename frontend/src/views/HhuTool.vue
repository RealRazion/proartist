<template>
  <div class="hhu-tool-page">
    <!-- ACCESS DENIED STATE FOR NON-TEAM USERS -->
    <section v-if="!isTeam" class="hhu-access-denied card">
      <div class="ad-icon">🔒</div>
      <h2>Exklusives Team-Werkzeug</h2>
      <p class="muted">
        Das HHU Mathe-Werkzeug ist exklusiv für Mitglieder des UNYQ-Teams freigeschaltet.
      </p>
      <div class="ad-actions">
        <button class="btn" @click="router.push('/platforms')">
          Zurück zum UNYQ Hub
        </button>
      </div>
    </section>

    <!-- FULL HHU TOOL (FOR TEAM MEMBERS) -->
    <div v-else class="hhu-shell">
      <!-- Hero Header -->
      <header class="hhu-hero card">
        <div class="hhu-hero-left">
          <div class="hhu-badge-row">
            <span class="hhu-chip team-chip">🔒 EXKLUSIVES TEAM-WERKZEUG</span>
            <span class="hhu-chip uni-chip">🏛️ HHU DÜSSELDORF</span>
          </div>
          <h1 class="hhu-title">HHU – Mathe für Informatik 1</h1>
          <p class="hhu-subtitle">
            Interaktiver Lernbegleiter: Vorlesungen 1–4 &amp; Anwesenheitsblätter 1–2. Mengenlehre, De-Morgan, Relationen, Hüllen-Generator, Äquivalenzklassen &amp; Abbildungen.
          </p>
        </div>

        <div class="hhu-hero-right">
          <div class="hhu-score-box">
            <span class="score-label">Quiz-Fortschritt</span>
            <span class="score-val">{{ correctAnswersCount }} / {{ quizData.length }}</span>
            <div class="score-bar-mini">
              <div class="score-fill" :style="{ width: `${(answeredCount / quizData.length) * 100}%` }"></div>
            </div>
            <small class="muted tiny">{{ answeredCount }} von {{ quizData.length }} gelöst</small>
          </div>
        </div>
      </header>

      <!-- Main Navigation Tabs -->
      <nav class="hhu-tabs-nav">
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'theorie' }"
          @click="selectTab('theorie')"
        >
          <span class="tab-icon">📖</span>
          <span>Theorie &amp; Definitionen</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'trainer' }"
          @click="selectTab('trainer')"
        >
          <span class="tab-icon">📝</span>
          <span>Wissens-Check (Quiz)</span>
          <span class="tab-badge" v-if="answeredCount">{{ answeredCount }}/{{ quizData.length }}</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'sandbox' }"
          @click="selectTab('sandbox')"
        >
          <span class="tab-icon">⚡</span>
          <span>Interaktive Werkzeuge</span>
        </button>
        <button
          class="tab-btn"
          :class="{ active: currentTab === 'aufgaben' }"
          @click="selectTab('aufgaben')"
        >
          <span class="tab-icon">🎓</span>
          <span>Übungsblatt-Trainer (HHU)</span>
        </button>
      </nav>

      <!-- ======================================================== -->
      <!-- TAB 1: THEORIE & DEFINITIONEN                            -->
      <!-- ======================================================== -->
      <section v-show="currentTab === 'theorie'" class="tab-pane theorie-pane">
        <div class="pane-intro-banner">
          <div>
            <span class="intro-tag">Exakter Vorlesungsstoff</span>
            <h2>Grundlagen, Sätze &amp; Definitionen</h2>
            <p>
              Strukturiert aufbereitet für die HHU-Vorlesung: Mengen, Teilmengenbeweise, De-Morgan, kartesische Produkte, binäre Relationen, Hüllenbildung, Äquivalenzklassen, Halbordnungen &amp; Abbildungen.
            </p>
          </div>
        </div>

        <div class="theorie-grid">
          <!-- Card 1: Mengen & Element vs. Teilmenge -->
          <article class="theorie-card card">
            <div class="tc-header">
              <span class="tc-icon">📦</span>
              <h3>1. Mengen &amp; Der feine Unterschied</h3>
            </div>
            <div class="tc-body">
              <p>
                <strong>Element vs. Teilmenge:</strong> $x \in M$ bedeutet, dass $x$ ein Element in der Menge $M$ ist. $A \subset M$ bedeutet, dass <em>jedes</em> Element von $A$ auch in $M$ liegt.
              </p>
              <div class="tc-callout warn">
                <strong>Typische Stolperfalle aus der Vorlesung:</strong>
                <p>Für $X = \{1, 2\}$ gilt:</p>
                <ul>
                  <li>$1 \in X$, aber $\{1\} \subset X$ und $\{1\} \in \mathcal{P}(X)$.</li>
                  <li>$\emptyset \subset X$ gilt immer! Aber $\emptyset \in X$ gilt hier <em>nicht</em>.</li>
                  <li>Bei $Y = \{\emptyset\}$ gilt: $\emptyset \in Y$ und $\emptyset \subset Y$.</li>
                </ul>
              </div>
              <p>
                <strong>Potenzmenge $\mathcal{P}(X)$:</strong> Die Menge aller Teilmengen. $|\mathcal{P}(X)| = 2^{|X|}$. Es gilt stets $\emptyset \in \mathcal{P}(X)$ und $X \in \mathcal{P}(X)$.
              </p>
            </div>
          </article>

          <!-- Card 2: Mengenoperationen & De Morgan -->
          <article class="theorie-card card">
            <div class="tc-header">
              <span class="tc-icon">🔄</span>
              <h3>2. Operationen &amp; De-Morgansche Gesetze</h3>
            </div>
            <div class="tc-body">
              <div class="math-list-box">
                <div><strong>Vereinigung:</strong> $A \cup B = \{x : x \in A \lor x \in B\}$</div>
                <div><strong>Schnitt:</strong> $A \cap B = \{x : x \in A \land x \in B\}$</div>
                <div><strong>Differenz (Ohne):</strong> $A \setminus B = \{x : x \in A \land x \notin B\}$</div>
                <div><strong>Kartesisches Produkt:</strong> $X \times Y = \{(x,y) : x \in X, y \in Y\}$</div>
              </div>
              <div class="tc-callout info">
                <strong>De-Morgansche Gesetze (Satz 1.1.14):</strong>
                <p>1. $X \setminus (A \cap B) = (X \setminus A) \cup (X \setminus B)$</p>
                <p>2. $X \setminus (A \cup B) = (X \setminus A) \cap (X \setminus B)$</p>
                <p class="callout-hint">Beweis-Tipp: Immer beide Inklusionen ($\subset$ und $\supset$) separat zeigen!</p>
              </div>
            </div>
          </article>

          <!-- Card 3: Relationen & Eigenschaften -->
          <article class="theorie-card card">
            <div class="tc-header">
              <span class="tc-icon">↔️</span>
              <h3>3. Relationen &amp; Eigenschaften (Def. 1.2.6)</h3>
            </div>
            <div class="tc-body">
              <p>Eine Relation $R$ auf $X$ ist $R \subset X \times X$. Eigenschaften für alle $x,y,z \in X$:</p>
              <div class="props-mini-grid">
                <div class="prop-chip">
                  <strong>Reflexiv:</strong>
                  <span>$\forall x \in X: (x,x) \in R$</span>
                </div>
                <div class="prop-chip">
                  <strong>Symmetrisch:</strong>
                  <span>$(x,y) \in R \implies (y,x) \in R$</span>
                </div>
                <div class="prop-chip">
                  <strong>Antisymmetrisch:</strong>
                  <span>$(x,y) \in R \land (y,x) \in R \implies x = y$</span>
                </div>
                <div class="prop-chip">
                  <strong>Asymmetrisch:</strong>
                  <span>$(x,y) \in R \implies (y,x) \notin R$ (verbietet auch $(x,x)$!)</span>
                </div>
                <div class="prop-chip full">
                  <strong>Transitiv:</strong>
                  <span>$(x,y) \in R \land (y,z) \in R \implies (x,z) \in R$</span>
                </div>
              </div>
              <p class="muted tiny italic">
                Merkregel: Asymmetrisch = Antisymmetrisch + Irreflexiv ($R \cap R^{-1} = \emptyset$).
              </p>
            </div>
          </article>

          <!-- Card 4: Hüllen, Äquivalenz & Ordnungen -->
          <article class="theorie-card card">
            <div class="tc-header">
              <span class="tc-icon">🔀</span>
              <h3>4. Hüllen, Äquivalenz &amp; Ordnungen</h3>
            </div>
            <div class="tc-body">
              <div class="section-sub">
                <strong>Hüllen einer Relation:</strong>
                <ul>
                  <li><strong>Reflexive Hülle:</strong> $R_{\text{refl}} = R \cup I_X$ mit $I_X = \{(x,x) : x \in X\}$</li>
                  <li><strong>Symmetrische Hülle:</strong> $R_{\text{sym}} = R \cup R^{-1}$ mit $R^{-1} = \{(y,x) : (x,y) \in R\}$</li>
                  <li><strong>Transitive Hülle:</strong> $R_{\text{trans}} = \bigcup_{n \ge 1} R^n$ (alle Pfade beliebiger Länge)</li>
                </ul>
              </div>
              <div class="section-sub border-top">
                <strong>Spezielle Relationen:</strong>
                <ul>
                  <li><strong>Äquivalenzrelation:</strong> reflexiv, symmetrisch, transitiv. Äquivalenzklassen $[x] = \{y \in X : (x,y) \in R\}$ bilden eine Partition von $X$.</li>
                  <li><strong>Partielle Ordnung (Halbordnung):</strong> reflexiv, antisymmetrisch, transitiv (z. B. $\le$ oder $\subseteq$).</li>
                  <li><strong>Totalordnung:</strong> Partielle Ordnung, bei der je zwei Elemente vergleichbar sind ($x \le y \lor y \le x$).</li>
                </ul>
              </div>
            </div>
          </article>

          <!-- Card 5: Abbildungen (Span 2) -->
          <article class="theorie-card card span-2">
            <div class="tc-header">
              <span class="tc-icon">🎯</span>
              <h3>5. Abbildungen: Bild, Urbild, Injektiv, Surjektiv &amp; Bijektiv (Def. 1.3.2 – 1.3.8)</h3>
            </div>
            <div class="tc-subgrid">
              <div class="sub-col">
                <strong>Bild &amp; Urbild</strong>
                <p>Für $f: X \to Y$, $A \subseteq X$, $B \subseteq Y$:</p>
                <ul>
                  <li><strong>Bild:</strong> $f(A) = \{f(x) : x \in A\} \subseteq Y$</li>
                  <li><strong>Urbild:</strong> $f^{-1}(B) = \{x \in X : f(x) \in B\} \subseteq X$</li>
                </ul>
                <p class="muted tiny">
                  <em>Wichtig:</em> Das Urbild $f^{-1}(B)$ existiert für <strong>jede</strong> Abbildung, auch wenn $f$ nicht umkehrbar ist!
                </p>
              </div>

              <div class="sub-col">
                <strong>Injektiv &amp; Surjektiv</strong>
                <ul>
                  <li><strong>Injektiv:</strong> $f(x_1) = f(x_2) \implies x_1 = x_2$. (Höchstens ein Urbild pro $y$).</li>
                  <li><strong>Surjektiv:</strong> $\forall y \in Y \ \exists x \in X: f(x) = y$. (Mindestens ein Urbild pro $y$).</li>
                  <li><strong>Bijektiv:</strong> Injektiv UND surjektiv (genau ein Urbild, umkehrbar).</li>
                </ul>
              </div>

              <div class="sub-col">
                <strong>Verkettung (Komposition)</strong>
                <p>Für $f: X \to Y$ und $g: Y \to Z$ ist $(g \circ f): X \to Z$ definiert durch:</p>
                <div class="code-box">$(g \circ f)(x) = g(f(x))$</div>
                <p class="muted tiny">
                  <em>Satz 1.3.12:</em> Ist $g \circ f$ injektiv $\implies f$ injektiv. Ist $g \circ f$ surjektiv $\implies g$ surjektiv.
                </p>
              </div>
            </div>
          </article>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- TAB 2: WISSENS-CHECK (QUIZ)                              -->
      <!-- ======================================================== -->
      <section v-show="currentTab === 'trainer'" class="tab-pane trainer-pane">
        <div class="quiz-panel card">
          <div class="qp-header">
            <div>
              <h2>Interaktiver Wissens-Check</h2>
              <p class="muted small">
                Prüfe dein Verständnis zu Mengen, Relationen, Hüllen und Abbildungen mit sofortiger Rückmeldung.
              </p>
            </div>
            <div class="qp-actions">
              <button class="btn ghost btn-sm" @click="resetQuiz">
                🔄 Quiz zurücksetzen
              </button>
            </div>
          </div>

          <!-- Progress Bar -->
          <div class="quiz-progress-section">
            <div class="progress-labels">
              <span>Fortschritt</span>
              <span>{{ answeredCount }} von {{ quizData.length }} Fragen beantwortet ({{ correctAnswersCount }} richtig)</span>
            </div>
            <div class="progress-track">
              <div
                class="progress-bar-fill"
                :style="{ width: `${(answeredCount / quizData.length) * 100}%` }"
              ></div>
            </div>
          </div>

          <!-- Questions List -->
          <div class="questions-list">
            <article
              v-for="(q, qIndex) in quizData"
              :key="q.id"
              class="question-card card"
              :class="{
                answered: userAnswers[q.id] !== undefined,
                correct: userAnswers[q.id] !== undefined && q.options[userAnswers[q.id]].correct,
                wrong: userAnswers[q.id] !== undefined && !q.options[userAnswers[q.id]].correct
              }"
            >
              <div class="qc-top">
                <span class="qc-tag">{{ q.topic }} • Frage {{ qIndex + 1 }}</span>
                <span
                  class="qc-status"
                  :class="{
                    'status-ok': userAnswers[q.id] !== undefined && q.options[userAnswers[q.id]].correct,
                    'status-fail': userAnswers[q.id] !== undefined && !q.options[userAnswers[q.id]].correct
                  }"
                >
                  <template v-if="userAnswers[q.id] === undefined">Offen</template>
                  <template v-else-if="q.options[userAnswers[q.id]].correct">✓ Richtig!</template>
                  <template v-else>✗ Falsch</template>
                </span>
              </div>

              <h3 class="qc-question">{{ q.question }}</h3>

              <div class="qc-options">
                <button
                  v-for="(opt, optIndex) in q.options"
                  :key="optIndex"
                  class="qc-opt-btn"
                  :class="{
                    'opt-correct': userAnswers[q.id] !== undefined && opt.correct,
                    'opt-selected-wrong': userAnswers[q.id] === optIndex && !opt.correct,
                    'opt-dimmed': userAnswers[q.id] !== undefined && userAnswers[q.id] !== optIndex && !opt.correct
                  }"
                  :disabled="userAnswers[q.id] !== undefined"
                  @click="handleSelectOption(q.id, optIndex)"
                >
                  <span class="opt-badge">
                    <template v-if="userAnswers[q.id] !== undefined && opt.correct">✓</template>
                    <template v-else-if="userAnswers[q.id] === optIndex && !opt.correct">✗</template>
                    <template v-else>{{ String.fromCharCode(65 + optIndex) }}</template>
                  </span>
                  <span class="opt-text">{{ opt.text }}</span>
                </button>
              </div>

              <!-- Explanation Box -->
              <div
                v-if="userAnswers[q.id] !== undefined"
                class="qc-explanation"
                :class="q.options[userAnswers[q.id]].correct ? 'exp-correct' : 'exp-wrong'"
              >
                <strong>{{ q.options[userAnswers[q.id]].correct ? 'Richtig!' : 'Leider nicht ganz:' }}</strong>
                <p>{{ q.explanation }}</p>
              </div>
            </article>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- TAB 3: INTERAKTIVE WERKZEUGE / SANDBOX                   -->
      <!-- ======================================================== -->
      <section v-show="currentTab === 'sandbox'" class="tab-pane sandbox-pane">
        <!-- Tool 1: Relationen-Prüfer & Hüllen-Rechner -->
        <div class="tool-box card">
          <div class="tb-header">
            <span class="tb-icon">⚙️</span>
            <div>
              <h2>Relationen-Analyzer &amp; Hüllen-Generator</h2>
              <p class="muted small">
                Analysiert Eigenschaften (Reflexiv, Symmetrisch, Antisymmetrisch, Asymmetrisch, Transitiv) mit Gegenbeispielen und berechnet Hüllen &amp; Äquivalenzklassen.
              </p>
            </div>
          </div>

          <div class="tool-content-grid">
            <!-- Inputs -->
            <div class="inputs-col card">
              <div class="form-group">
                <label>Grundmenge $X$ (kommagetrennt):</label>
                <input
                  type="text"
                  v-model="relSetInput"
                  placeholder="z. B. 1, 2, 3, 4"
                  class="hhu-input"
                />
                <small class="muted tiny">Beispiel: 1, 2, 3, 4 oder a, b, c</small>
              </div>

              <div class="form-group">
                <label>Paare in $R$ (Format: (a,b)):</label>
                <textarea
                  v-model="relPairsInput"
                  rows="3"
                  class="hhu-textarea font-mono"
                  placeholder="(1,2), (2,3), (3,4)"
                ></textarea>
                <small class="muted tiny">Trennbar durch Kommas oder Zeilenumbruch</small>
              </div>

              <div class="btn-row">
                <button class="btn btn-sm" @click="runRelationAnalysis">
                  Relation analysieren
                </button>
                <button class="btn ghost btn-sm" @click="loadPresetRelation(1)" title="Beispiel 1: Kette">
                  Bsp 1
                </button>
                <button class="btn ghost btn-sm" @click="loadPresetRelation(2)" title="Beispiel 2: Äquivalenz">
                  Bsp 2
                </button>
              </div>
            </div>

            <!-- Properties Output -->
            <div class="results-col card">
              <h3>Eigenschaften &amp; Begründungen</h3>
              <div class="props-status-list" v-if="relationAnalysisResult">
                <div
                  class="prop-row"
                  :class="relationAnalysisResult.isReflexive ? 'ok' : 'fail'"
                >
                  <div class="pr-info">
                    <strong>Reflexiv:</strong> {{ relationAnalysisResult.isReflexive ? 'Ja' : 'Nein' }}
                    <small class="muted tiny">
                      {{ relationAnalysisResult.isReflexive ? 'Für alle x in X gilt (x,x) in R.' : 'Fehlt: ' + relationAnalysisResult.reflMissing.join(', ') }}
                    </small>
                  </div>
                  <span class="pr-mark">{{ relationAnalysisResult.isReflexive ? '✓' : '✗' }}</span>
                </div>

                <div
                  class="prop-row"
                  :class="relationAnalysisResult.isSymmetric ? 'ok' : 'fail'"
                >
                  <div class="pr-info">
                    <strong>Symmetrisch:</strong> {{ relationAnalysisResult.isSymmetric ? 'Ja' : 'Nein' }}
                    <small class="muted tiny">
                      {{ relationAnalysisResult.isSymmetric ? 'R = R^{-1}' : 'Gegenbeispiel: ' + relationAnalysisResult.symCounter }}
                    </small>
                  </div>
                  <span class="pr-mark">{{ relationAnalysisResult.isSymmetric ? '✓' : '✗' }}</span>
                </div>

                <div
                  class="prop-row"
                  :class="relationAnalysisResult.isAntisymmetric ? 'ok' : 'fail'"
                >
                  <div class="pr-info">
                    <strong>Antisymmetrisch:</strong> {{ relationAnalysisResult.isAntisymmetric ? 'Ja' : 'Nein' }}
                    <small class="muted tiny">
                      {{ relationAnalysisResult.isAntisymmetric ? 'Symmetrische Paare nur auf der Diagonale' : 'Gegenbeispiel: ' + relationAnalysisResult.antiCounter }}
                    </small>
                  </div>
                  <span class="pr-mark">{{ relationAnalysisResult.isAntisymmetric ? '✓' : '✗' }}</span>
                </div>

                <div
                  class="prop-row"
                  :class="relationAnalysisResult.isAsymmetric ? 'ok' : 'neutral'"
                >
                  <div class="pr-info">
                    <strong>Asymmetrisch:</strong> {{ relationAnalysisResult.isAsymmetric ? 'Ja' : 'Nein' }}
                    <small class="muted tiny">
                      {{ relationAnalysisResult.isAsymmetric ? 'R ∩ R^{-1} = ∅' : (relationAnalysisResult.asymCounter ? 'Gegenbeispiel: ' + relationAnalysisResult.asymCounter : 'Nicht asymmetrisch') }}
                    </small>
                  </div>
                  <span class="pr-mark">{{ relationAnalysisResult.isAsymmetric ? '✓' : '–' }}</span>
                </div>

                <div
                  class="prop-row"
                  :class="relationAnalysisResult.isTransitive ? 'ok' : 'fail'"
                >
                  <div class="pr-info">
                    <strong>Transitiv:</strong> {{ relationAnalysisResult.isTransitive ? 'Ja' : 'Nein' }}
                    <small class="muted tiny">
                      {{ relationAnalysisResult.isTransitive ? 'R ∘ R ⊆ R' : 'Gegenbeispiel: ' + relationAnalysisResult.transCounter }}
                    </small>
                  </div>
                  <span class="pr-mark">{{ relationAnalysisResult.isTransitive ? '✓' : '✗' }}</span>
                </div>

                <div class="special-labels-row">
                  <span
                    class="hhu-pill"
                    :class="relationAnalysisResult.isEquiv ? 'pill-success' : 'pill-muted'"
                  >
                    {{ relationAnalysisResult.isEquiv ? '✓ Äquivalenzrelation' : 'Keine Äquivalenzrelation' }}
                  </span>
                  <span
                    class="hhu-pill"
                    :class="relationAnalysisResult.isPartialOrder ? 'pill-info' : 'pill-muted'"
                  >
                    {{ relationAnalysisResult.isPartialOrder ? '✓ Partielle Ordnung' : 'Keine Ordnung' }}
                  </span>
                </div>
              </div>
              <div v-else class="muted small italic placeholder-text">
                Klicke auf „Relation analysieren“, um die Auswertung zu starten.
              </div>
            </div>

            <!-- Closures Output -->
            <div class="closures-col card">
              <h3>Berechnete Hüllen</h3>
              <div class="closure-blocks" v-if="relationAnalysisResult">
                <div class="cb-item">
                  <span class="cb-label">Reflexive Hülle $R_{\text{refl}}$:</span>
                  <p class="cb-val font-mono">{{ relationAnalysisResult.reflStr }}</p>
                </div>
                <div class="cb-item">
                  <span class="cb-label">Symmetrische Hülle $R_{\text{sym}}$:</span>
                  <p class="cb-val font-mono">{{ relationAnalysisResult.symStr }}</p>
                </div>
                <div class="cb-item">
                  <span class="cb-label">Transitive Hülle $R_{\text{trans}}$:</span>
                  <p class="cb-val font-mono">{{ relationAnalysisResult.transStr }}</p>
                </div>

                <div class="cb-item equiv-box" v-if="relationAnalysisResult.isEquiv">
                  <span class="cb-label highlight">Äquivalenzklassen:</span>
                  <p class="cb-val font-mono highlight">{{ relationAnalysisResult.equivClassesStr }}</p>
                </div>
              </div>
              <div v-else class="muted small italic placeholder-text">
                Hüllen werden zusammen mit der Relation berechnet.
              </div>
            </div>
          </div>
        </div>

        <!-- Tool 2: Kompositions-Rechner S ∘ R -->
        <div class="tool-box card">
          <div class="tb-header">
            <span class="tb-icon">🔗</span>
            <div>
              <h2>Verkettungs-Rechner ($S \circ R$)</h2>
              <p class="muted small">
                Erinnere: $(x,z) \in S \circ R \iff \exists y: (x,y) \in R \land (y,z) \in S$. Zuerst $R$, dann $S$!
              </p>
            </div>
          </div>

          <div class="comp-inputs-grid">
            <div class="form-group">
              <label>Relation $R$:</label>
              <input
                type="text"
                v-model="compRInput"
                class="hhu-input font-mono"
                placeholder="(a,b), (b,c)"
              />
              <small class="muted tiny">Beispiel aus Blatt 2: (a,b), (b,c)</small>
            </div>

            <div class="form-group">
              <label>Relation $S$:</label>
              <input
                type="text"
                v-model="compSInput"
                class="hhu-input font-mono"
                placeholder="(b,a), (c,b), (c,a)"
              />
              <small class="muted tiny">Beispiel aus Blatt 2: (b,a), (c,b), (c,a)</small>
            </div>

            <div class="form-group action-align">
              <button class="btn btn-sm" @click="runComposition">
                $S \circ R$ und $R^{-1}$ berechnen
              </button>
            </div>
          </div>

          <!-- Composition Results -->
          <div class="comp-results-box card" v-if="compositionResult">
            <div class="comp-summary-row">
              <div class="cs-item">
                <span class="cs-label">Inverse Relation $R^{-1}$:</span>
                <p class="cs-val font-mono">{{ compositionResult.rInvStr }}</p>
              </div>
              <div class="cs-item">
                <span class="cs-label">Verkettung $S \circ R$:</span>
                <p class="cs-val font-mono highlight">{{ compositionResult.compStr }}</p>
              </div>
            </div>

            <div class="comp-steps-section">
              <strong>Verkettungsschritte im Detail:</strong>
              <ul v-if="compositionResult.steps.length">
                <li v-for="(step, sIdx) in compositionResult.steps" :key="sIdx">
                  {{ step }}
                </li>
              </ul>
              <p v-else class="muted italic tiny">
                Keine verknüpfbaren Paare vorhanden (Schnittmenge der Zwischenknoten leer).
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- ======================================================== -->
      <!-- TAB 4: ÜBUNGSBLATT-TRAINER (HHU ORIGINALS)               -->
      <!-- ======================================================== -->
      <section v-show="currentTab === 'aufgaben'" class="tab-pane aufgaben-pane">
        <div class="aufgaben-card card">
          <div class="ac-header">
            <div>
              <span class="hhu-chip uni-chip">Präsenzübungen HHU</span>
              <h2>Aufgaben aus Anwesenheitsblatt 1 &amp; 2</h2>
              <p class="muted small">
                Originalaufgaben aller Übungsgruppen. Versuche sie zuerst selbst zu lösen und klappe dann Schritt für Schritt die vollständige Musterbegründung auf!
              </p>
            </div>

            <!-- Filter Buttons -->
            <div class="ac-filters">
              <button
                class="filter-chip"
                :class="{ active: sheetFilter === 0 }"
                @click="setSheetFilter(0)"
              >
                Alle Blätter
              </button>
              <button
                class="filter-chip"
                :class="{ active: sheetFilter === 1 }"
                @click="setSheetFilter(1)"
              >
                Blatt 1: Mengen &amp; Beweise
              </button>
              <button
                class="filter-chip"
                :class="{ active: sheetFilter === 2 }"
                @click="setSheetFilter(2)"
              >
                Blatt 2: Relationen &amp; Abbildungen
              </button>
            </div>
          </div>

          <!-- Task Accordions -->
          <div class="task-accordions-list">
            <article
              v-for="task in filteredTasks"
              :key="task.id"
              class="task-item card"
            >
              <button class="task-head-btn" @click="toggleTaskAccordion(task.id)">
                <div class="th-left">
                  <div class="th-meta">
                    <span class="sheet-tag">Blatt {{ task.sheet }}</span>
                    <span class="group-tag">{{ task.group }}</span>
                  </div>
                  <h3 class="task-title">{{ task.title }}</h3>
                </div>
                <span class="th-arrow" :class="{ open: openTaskIds.has(task.id) }">▼</span>
              </button>

              <div v-show="openTaskIds.has(task.id)" class="task-body">
                <div class="problem-box">
                  <strong class="pb-title">Aufgabenstellung:</strong>
                  <div class="pb-content" v-html="task.problemHtml"></div>
                </div>

                <div class="solution-box">
                  <strong class="sb-title">Ausführliche Musterlösung &amp; Begründung:</strong>
                  <div class="sb-content" v-html="task.solutionHtml"></div>
                </div>
              </div>
            </article>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from "vue";
import { useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();

// Tabs: 'theorie', 'trainer', 'sandbox', 'aufgaben'
const currentTab = ref("theorie");

function selectTab(tab) {
  currentTab.value = tab;
  triggerMathJax();
}

/* =========================================================================
   MATHJAX DYNAMIC LOADER & TYPESETTING
   ========================================================================= */
function ensureMathJaxLoaded() {
  if (typeof window === "undefined") return;

  if (!window.MathJax) {
    window.MathJax = {
      tex: {
        inlineMath: [
          ["$", "$"],
          ["\\(", "\\)"],
        ],
        displayMath: [
          ["$$", "$$"],
          ["\\[", "\\]"],
        ],
      },
      svg: { fontCache: "global" },
      startup: {
        typeset: false,
      },
    };
  }

  if (!document.getElementById("mathjax-script")) {
    const script = document.createElement("script");
    script.id = "mathjax-script";
    script.src = "https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js";
    script.async = true;
    script.onload = () => {
      triggerMathJax();
    };
    document.head.appendChild(script);
  } else {
    triggerMathJax();
  }
}

function triggerMathJax() {
  nextTick(() => {
    if (window.MathJax && window.MathJax.typesetPromise) {
      window.MathJax.typesetPromise().catch((err) => {
        console.warn("MathJax typeset error:", err);
      });
    }
  });
}

/* =========================================================================
   QUIZ ENGINE & DATA
   ========================================================================= */
const quizData = [
  {
    id: 1,
    topic: "Mengenlehre",
    question: "Gegeben sei U = {∅}. Welche der folgenden Aussagen ist WAHR?",
    options: [
      { text: "∅ ∈ U", correct: true },
      { text: "{∅} ⊂ ∅", correct: false },
      { text: "∅ = {∅}", correct: false },
      { text: "|U| = 0", correct: false },
    ],
    explanation:
      "U enthält genau ein einziges Element, nämlich das Symbol bzw. Objekt der leeren Menge ∅. Daher gilt ∅ ∈ U und |U| = 1. Aber ∅ ≠ {∅}!",
  },
  {
    id: 2,
    topic: "Mengenlehre",
    question: "Sei X = {1, 2}. Welche Aussage über die Potenzmenge P(X) ist FALSCH?",
    options: [
      { text: "1 ∈ P(X)", correct: true },
      { text: "{1} ∈ P(X)", correct: false },
      { text: "∅ ∈ P(X)", correct: false },
      { text: "{1, 2} ∈ P(X)", correct: false },
    ],
    explanation:
      "Die Elemente von P(X) sind Teilmengen von X. 1 ist eine Zahl (ein Element von X), aber keine Teilmenge. Richtig ist hingegen {1} ∈ P(X).",
  },
  {
    id: 3,
    topic: "De-Morgan",
    question: "Welche Mengengleichheit entspricht dem De-Morganschen Gesetz für das Komplement des Schnitts?",
    options: [
      { text: "X \\ (A ∩ B) = (X \\ A) ∪ (X \\ B)", correct: true },
      { text: "X \\ (A ∩ B) = (X \\ A) ∩ (X \\ B)", correct: false },
      { text: "X \\ (A ∩ B) = X \\ (A ∪ B)", correct: false },
      { text: "X \\ (A ∩ B) = A ∪ B", correct: false },
    ],
    explanation:
      "Nach Satz 1.1.14 (i) dreht sich beim Komplementieren der Schnitt ∩ zur Vereinigung ∪ um: X \\ (A ∩ B) = (X \\ A) ∪ (X \\ B).",
  },
  {
    id: 4,
    topic: "Relationen",
    question: "Wann heißt eine Relation R auf einer Menge X antisymmetrisch?",
    options: [
      { text: "Wenn für alle x, y ∈ X gilt: Aus (x,y) ∈ R und (y,x) ∈ R folgt x = y.", correct: true },
      { text: "Wenn für alle x, y ∈ X gilt: Aus (x,y) ∈ R folgt (y,x) ∉ R.", correct: false },
      { text: "Wenn für kein x ∈ X das Paar (x,x) ∈ R ist.", correct: false },
      { text: "Wenn (x,y) ∈ R niemals (y,x) ∈ R erlaubt.", correct: false },
    ],
    explanation:
      "Genau das ist Definition 1.2.6: Symmetrische Paare dürfen nur auf der Diagonale auftreten (x = y). Die Aussage 'Aus (x,y) ∈ R folgt (y,x) ∉ R' beschreibt hingegen Asymmetrie.",
  },
  {
    id: 5,
    topic: "Relationen",
    question: "Kann eine Relation gleichzeitig symmetrisch und antisymmetrisch sein?",
    options: [
      { text: "Ja, z. B. die Gleichheitsrelation I_X = {(x,x) : x ∈ X} oder die leere Relation ∅.", correct: true },
      { text: "Nein, Symmetrie und Antisymmetrie schließen sich logisch gegenseitig aus.", correct: false },
      { text: "Nur wenn die Grundmenge unendlich viele Elemente hat.", correct: false },
    ],
    explanation:
      "Gilt R ⊆ I_X (also nur Paare der Form (x,x)), so ist R sowohl symmetrisch (denn (x,x) ∈ R ⇒ (x,x) ∈ R) als auch antisymmetrisch!",
  },
  {
    id: 6,
    topic: "Relationen",
    question: "Betrachte R = {(x,y) ∈ Z × Z : y = x + 1}. Welche Eigenschaft besitzt R?",
    options: [
      { text: "Asymmetrisch und antisymmetrisch", correct: true },
      { text: "Reflexiv", correct: false },
      { text: "Transitiv", correct: false },
      { text: "Symmetrisch", correct: false },
    ],
    explanation:
      "Aus y = x + 1 folgt x = y - 1 ≠ y + 1. Also kann (y,x) niemals in R sein ⇒ Asymmetrisch (und damit automatisch antisymmetrisch). Nicht reflexiv, da x ≠ x + 1. Nicht transitiv, da (0,1) ∈ R, (1,2) ∈ R, aber (0,2) ∉ R.",
  },
  {
    id: 7,
    topic: "Hüllen",
    question: "Auf X = {1, 2, 3} sei R = {(1,2), (2,3)}. Wie viele Paare enthält die transitive Hülle R_trans?",
    options: [
      { text: "3 Paare: {(1,2), (2,3), (1,3)}", correct: true },
      { text: "2 Paare: {(1,2), (2,3)}", correct: false },
      { text: "6 Paare: alle Paare mit x < y plus Diagonale", correct: false },
      { text: "9 Paare: ganz X × X", correct: false },
    ],
    explanation:
      "Der Pfad 1 → 2 → 3 erfordert das neue Paar (1,3). Damit ist R_trans = {(1,2), (2,3), (1,3)} bereits transitiv (3 Elemente).",
  },
  {
    id: 8,
    topic: "Äquivalenz & Ordnung",
    question: "Was ist der entscheidende Unterschied zwischen einer Äquivalenzrelation und einer partiellen Ordnung?",
    options: [
      { text: "Eine Äquivalenzrelation ist symmetrisch, eine partielle Ordnung ist antisymmetrisch.", correct: true },
      { text: "Eine Äquivalenzrelation ist transitiv, eine Ordnung nicht.", correct: false },
      { text: "Eine partielle Ordnung ist stets total, eine Äquivalenzrelation nicht.", correct: false },
      { text: "Es gibt keinen Unterschied, die Begriffe sind synonym.", correct: false },
    ],
    explanation:
      "Beide sind reflexiv und transitiv. Der einzige definierende Unterschied ist: Äquivalenzrelation = symmetrisch; partielle Ordnung = antisymmetrisch!",
  },
  {
    id: 9,
    topic: "Abbildungen",
    question: "Sei f: Z → Z, n ↦ 2n + 1. Welche Eigenschaft hat f?",
    options: [
      { text: "Injektiv, aber nicht surjektiv", correct: true },
      { text: "Surjektiv, aber nicht injektiv", correct: false },
      { text: "Bijektiv", correct: false },
      { text: "Weder injektiv noch surjektiv", correct: false },
    ],
    explanation:
      "Injektiv: 2n_1 + 1 = 2n_2 + 1 ⇒ 2n_1 = 2n_2 ⇒ n_1 = n_2. Nicht surjektiv, da die geraden Zahlen (z. B. 0 oder 2) niemals als Funktionswert 2n + 1 für ein ganzes n angenommen werden.",
  },
  {
    id: 10,
    topic: "Abbildungen",
    question: "Für f: Z → N_0, n ↦ n^2 und B = {0, 1, 4}: Was ist das Urbild f^{-1}(B)?",
    options: [
      { text: "{-2, -1, 0, 1, 2}", correct: true },
      { text: "{0, 1, 2}", correct: false },
      { text: "{0, 1, 16}", correct: false },
      { text: "∅", correct: false },
    ],
    explanation:
      "f^{-1}(B) = {n ∈ Z : n^2 ∈ {0, 1, 4}}. Da 0^2 = 0, (±1)^2 = 1 und (±2)^2 = 4, gehören alle 5 ganzen Zahlen {-2, -1, 0, 1, 2} zum Urbild!",
  },
  {
    id: 11,
    topic: "Abbildungen",
    question: "Seien f: X → Y und g: Y → Z. Welche Aussage aus Satz 1.3.12 ist korrekt?",
    options: [
      { text: "Wenn g ∘ f injektiv ist, dann ist f injektiv.", correct: true },
      { text: "Wenn g ∘ f injektiv ist, dann ist g injektiv.", correct: false },
      { text: "Wenn g ∘ f surjektiv ist, dann ist f surjektiv.", correct: false },
      { text: "g ∘ f ist nur definiert, wenn X = Z.", correct: false },
    ],
    explanation:
      "Wäre f nicht injektiv (f(x_1) = f(x_2) mit x_1 ≠ x_2), dann wäre auch g(f(x_1)) = g(f(x_2)), also g ∘ f nicht injektiv. Widerspruch! Daher muss f zwingend injektiv sein.",
  },
  {
    id: 12,
    topic: "Relationale Algebra",
    question: "Was bewirkt die Projektion π_{Name}(R) in der relationalen Algebra mathematisch bei Duplikaten?",
    options: [
      { text: "Da eine Relation eine Menge von Tupeln ist, werden Duplikate automatisch entfernt.", correct: true },
      { text: "Duplikate bleiben erhalten wie in einer SQL-Tabelle ohne DISTINCT.", correct: false },
      { text: "Die Operation bricht mit einem Fehler ab.", correct: false },
      { text: "Sie selektiert nur Zeilen mit Primärschlüssel.", correct: false },
    ],
    explanation:
      "Bemerkung 1.2.22 aus der Vorlesung: Eine mathematische Relation ist eine Menge. In Mengen gibt es keine Duplikate (z. B. {a, a} = {a}), sodass die Projektion doppelte Werte vereinigt.",
  },
];

const userAnswers = ref({});

const answeredCount = computed(() => Object.keys(userAnswers.value).length);
const correctAnswersCount = computed(() => {
  let count = 0;
  for (const [qIdStr, optIdx] of Object.entries(userAnswers.value)) {
    const q = quizData.find((item) => item.id === parseInt(qIdStr));
    if (q && q.options[optIdx]?.correct) {
      count++;
    }
  }
  return count;
});

function handleSelectOption(qId, optIndex) {
  if (userAnswers.value[qId] !== undefined) return;
  userAnswers.value = { ...userAnswers.value, [qId]: optIndex };
  triggerMathJax();
}

function resetQuiz() {
  userAnswers.value = {};
  triggerMathJax();
}

/* =========================================================================
   TOOL 1: RELATIONEN-ANALYZER & HÜLLEN-GENERATOR
   ========================================================================= */
const relSetInput = ref("1, 2, 3, 4");
const relPairsInput = ref("(1,2), (2,3), (3,4)");
const relationAnalysisResult = ref(null);

function parseSet(str) {
  return str
    .split(",")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
}

function parsePairs(str) {
  const pairs = [];
  const regex = /\(\s*([^,]+?)\s*,\s*([^)]+?)\s*\)/g;
  let match;
  while ((match = regex.exec(str)) !== null) {
    pairs.push([match[1].trim(), match[2].trim()]);
  }
  return pairs;
}

function pairsToString(pairs) {
  if (!pairs || pairs.length === 0) return "∅";
  const formatted = pairs.map((p) => `(${p[0]}, ${p[1]})`).join(", ");
  return `{${formatted}}`;
}

function runRelationAnalysis() {
  const X = parseSet(relSetInput.value);
  const R_raw = parsePairs(relPairsInput.value);

  const pairSet = new Set();
  R_raw.forEach((p) => pairSet.add(`${p[0]}###${p[1]}`));

  const hasPair = (a, b) => pairSet.has(`${a}###${b}`);

  // 1. Reflexiv
  let isReflexive = true;
  const reflMissing = [];
  X.forEach((x) => {
    if (!hasPair(x, x)) {
      isReflexive = false;
      reflMissing.push(`(${x},${x})`);
    }
  });

  // 2. Symmetrisch
  let isSymmetric = true;
  let symCounter = "";
  for (const item of pairSet) {
    const [a, b] = item.split("###");
    if (!hasPair(b, a)) {
      isSymmetric = false;
      if (!symCounter) symCounter = `(${a},${b}) ∈ R, aber (${b},${a}) ∉ R`;
    }
  }

  // 3. Antisymmetrisch
  let isAntisymmetric = true;
  let antiCounter = "";
  for (const item of pairSet) {
    const [a, b] = item.split("###");
    if (a !== b && hasPair(b, a)) {
      isAntisymmetric = false;
      if (!antiCounter) antiCounter = `(${a},${b}) ∈ R und (${b},${a}) ∈ R mit ${a} ≠ ${b}`;
    }
  }

  // 4. Asymmetrisch
  let isAsymmetric = true;
  let asymCounter = "";
  for (const item of pairSet) {
    const [a, b] = item.split("###");
    if (hasPair(b, a)) {
      isAsymmetric = false;
      if (!asymCounter) asymCounter = `(${a},${b}) ∈ R und (${b},${a}) ∈ R`;
    }
  }

  // 5. Transitiv
  let isTransitive = true;
  let transCounter = "";
  for (const item1 of pairSet) {
    const [a, b] = item1.split("###");
    for (const item2 of pairSet) {
      const [c, d] = item2.split("###");
      if (b === c && !hasPair(a, d)) {
        isTransitive = false;
        if (!transCounter) transCounter = `(${a},${b}) ∈ R und (${b},${d}) ∈ R, aber (${a},${d}) ∉ R`;
      }
    }
  }

  const isEquiv = isReflexive && isSymmetric && isTransitive;
  const isPartialOrder = isReflexive && isAntisymmetric && isTransitive;

  // Closures
  // 1. Reflexive Hülle
  const reflPairs = new Set(pairSet);
  X.forEach((x) => reflPairs.add(`${x}###${x}`));
  const reflArr = Array.from(reflPairs).map((s) => s.split("###"));

  // 2. Symmetrische Hülle
  const symPairs = new Set(pairSet);
  pairSet.forEach((item) => {
    const [a, b] = item.split("###");
    symPairs.add(`${b}###${a}`);
  });
  const symArr = Array.from(symPairs).map((s) => s.split("###"));

  // 3. Transitive Hülle (Warshall)
  const transPairs = new Set(pairSet);
  let changed = true;
  while (changed) {
    changed = false;
    const currentItems = Array.from(transPairs);
    for (let i = 0; i < currentItems.length; i++) {
      const [a, b] = currentItems[i].split("###");
      for (let j = 0; j < currentItems.length; j++) {
        const [c, d] = currentItems[j].split("###");
        if (b === c) {
          const newPair = `${a}###${d}`;
          if (!transPairs.has(newPair)) {
            transPairs.add(newPair);
            changed = true;
          }
        }
      }
    }
  }
  const transArr = Array.from(transPairs).map((s) => s.split("###"));

  // Äquivalenzklassen
  let equivClassesStr = "-";
  if (isEquiv) {
    const classes = [];
    const visited = new Set();
    X.forEach((x) => {
      if (!visited.has(x)) {
        const eqClass = [];
        X.forEach((y) => {
          if (hasPair(x, y)) {
            eqClass.push(y);
            visited.add(y);
          }
        });
        classes.push(`[${x}] = {${eqClass.join(", ")}}`);
      }
    });
    equivClassesStr = classes.join(", ");
  }

  relationAnalysisResult.value = {
    isReflexive,
    reflMissing,
    isSymmetric,
    symCounter,
    isAntisymmetric,
    antiCounter,
    isAsymmetric,
    asymCounter,
    isTransitive,
    transCounter,
    isEquiv,
    isPartialOrder,
    reflStr: pairsToString(reflArr),
    symStr: pairsToString(symArr),
    transStr: pairsToString(transArr),
    equivClassesStr,
  };

  triggerMathJax();
}

function loadPresetRelation(presetId) {
  if (presetId === 1) {
    relSetInput.value = "1, 2, 3, 4";
    relPairsInput.value = "(1,2), (2,3), (3,4)";
  } else if (presetId === 2) {
    relSetInput.value = "1, 2, 3";
    relPairsInput.value = "(1,1), (1,2), (2,1), (2,2), (3,3)";
  }
  runRelationAnalysis();
}

/* =========================================================================
   TOOL 2: KOMPOSITIONS-RECHNER S ∘ R
   ========================================================================= */
const compRInput = ref("(a,b), (b,c)");
const compSInput = ref("(b,a), (c,b), (c,a)");
const compositionResult = ref(null);

function runComposition() {
  const R_pairs = parsePairs(compRInput.value);
  const S_pairs = parsePairs(compSInput.value);

  // R^-1
  const R_inv = R_pairs.map((p) => [p[1], p[0]]);
  const rInvSet = new Set(R_inv.map((p) => `${p[0]}###${p[1]}`));
  const rInvFinal = Array.from(rInvSet).map((s) => s.split("###"));

  // S ∘ R: (x, z) such that (x, y) in R and (y, z) in S
  const compPairs = new Set();
  const steps = [];

  R_pairs.forEach(([x, y]) => {
    S_pairs.forEach(([y2, z]) => {
      if (y === y2) {
        compPairs.add(`${x}###${z}`);
        steps.push(`Aus (${x}, ${y}) ∈ R und (${y2}, ${z}) ∈ S folgt (${x}, ${z}) ∈ S ∘ R.`);
      }
    });
  });

  const compArr = Array.from(compPairs).map((s) => s.split("###"));

  compositionResult.value = {
    rInvStr: pairsToString(rInvFinal),
    compStr: pairsToString(compArr),
    steps,
  };

  triggerMathJax();
}

/* =========================================================================
   TAB 4: ÜBUNGSBLATT-TRAINER (HHU CONTENT)
   ========================================================================= */
const sheetFilter = ref(0); // 0 = all, 1 = sheet 1, 2 = sheet 2
const openTaskIds = ref(new Set([1])); // First task open by default

function setSheetFilter(num) {
  sheetFilter.value = num;
  triggerMathJax();
}

function toggleTaskAccordion(id) {
  if (openTaskIds.value.has(id)) {
    openTaskIds.value.delete(id);
  } else {
    openTaskIds.value.add(id);
  }
  triggerMathJax();
}

const hhuTasks = [
  {
    id: 1,
    sheet: 1,
    title: "Aufgabe 1 (Blatt 1): Mengen vergleichen",
    group: "Gruppe 1 (HHU)",
    problemHtml: `Vergleichen Sie alle Paare der Mengen $A = \\{1,2,3\\}$, $B = \\{3,2,1,1\\}$, $C = \\{1,2\\}$ und $D = \\{\\{2\\}, \\{3\\}\\}$.`,
    solutionHtml: `
      <ul>
        <li><strong>A und B:</strong> Es gilt $A = B$. Begründung: Mehrfachnennung von Elementen ändert die Menge nicht ($\\{3,2,1,1\\} = \\{1,2,3\\}$).</li>
        <li><strong>C und A:</strong> $C \\subset A$ ist eine echte Teilmenge ($C \\subsetneq A$), denn $1, 2 \\in A$, aber $3 \\notin C$. Da $A=B$, gilt auch $C \\subsetneq B$.</li>
        <li><strong>D im Vergleich zu allen anderen:</strong> Keine Inklusion! $D$ enthält zwei Mengen als Elemente ($\\{2\\}$ und $\\{3\\}$), während $A, B, C$ Zahlen als Elemente enthalten. Weder $\\{2\\} \\in A$ noch $1 \\in D$.</li>
      </ul>
    `,
  },
  {
    id: 2,
    sheet: 1,
    title: "Aufgabe 2 (Blatt 1): Element oder Teilmenge?",
    group: "Gruppe 1 & 2 (HHU)",
    problemHtml: `Gegeben $U = \\{\\emptyset\\}$ und $V = \\{\\emptyset, \\{\\emptyset\\}\\}$. Welche der Aussagen $\\emptyset \\in U$, $\\emptyset \\subset U$, $U \\in V$, $U \\subset V$ sind wahr? Bestimmen Sie $U \\cap V$, $V \\setminus U$, $U \\times V$ und $\\mathcal{P}(U)$.`,
    solutionHtml: `
      <p><strong>Wahrheitswerte der vier Aussagen:</strong></p>
      <ul>
        <li>$\\emptyset \\in U$: <strong>Wahr</strong>, da $\\emptyset$ explizit in den Mengenklammern von $U$ aufgelistet ist.</li>
        <li>$\\emptyset \\subset U$: <strong>Wahr</strong>, die leere Menge ist Teilmenge jeder beliebigen Menge.</li>
        <li>$U \\in V$: <strong>Wahr</strong>, da $U = \\{\\emptyset\\}$ als zweites Element in $V$ enthalten ist.</li>
        <li>$U \\subset V$: <strong>Wahr</strong>, denn das einzige Element von $U$ ist $\\emptyset$, und dieses liegt auch in $V$.</li>
      </ul>
      <p style="margin-top: 8px;"><strong>Mengenoperationen:</strong></p>
      <ul>
        <li>$U \\cap V = \\{\\emptyset\\} = U$</li>
        <li>$V \\setminus U = \\{\\{\\emptyset\\}\\}$</li>
        <li>$U \\times V = \\{(\\emptyset, \\emptyset), (\\emptyset, \\{\\emptyset\\})\\}$</li>
        <li>$\\mathcal{P}(U) = \\{\\emptyset, \\{\\emptyset\\}\\} = V$</li>
      </ul>
    `,
  },
  {
    id: 3,
    sheet: 1,
    title: "Aufgabe 3 (Blatt 1): Mengenidentität beweisen",
    group: "Gruppe 1 (HHU)",
    problemHtml: `Beweisen Sie für beliebige Mengen $X, Y, Z$ durch Nachweis beider Inklusionen: $X \\cap (Y \\cup Z) = (X \\cap Y) \\cup (X \\cap Z)$.`,
    solutionHtml: `
      <p><strong>Teil 1: Zeige $\\subset$:</strong></p>
      <p>Sei $x \\in X \\cap (Y \\cup Z)$. Nach Definition des Schnitts gilt $x \\in X$ und $x \\in Y \\cup Z$. Aus $x \\in Y \\cup Z$ folgt $x \\in Y$ oder $x \\in Z$.</p>
      <p><em>1. Fall ($x \\in Y$):</em> Da $x \\in X$ und $x \\in Y$, gilt $x \\in X \\cap Y$, also insbesondere $x \\in (X \\cap Y) \\cup (X \\cap Z)$.</p>
      <p><em>2. Fall ($x \\in Z$):</em> Da $x \\in X$ und $x \\in Z$, gilt $x \\in X \\cap Z$, also auch $x \\in (X \\cap Y) \\cup (X \\cap Z)$.</p>
      <p>In beiden Fällen folgt die Inklusion.</p>
      <p style="margin-top: 8px;"><strong>Teil 2: Zeige $\\supset$:</strong></p>
      <p>Sei $x \\in (X \\cap Y) \\cup (X \\cap Z)$. Also gilt $x \\in X \\cap Y$ oder $x \\in X \\cap Z$.</p>
      <p>In beiden Fällen ist $x \\in X$. Weiterhin gilt $x \\in Y$ oder $x \\in Z$, d. h. $x \\in Y \\cup Z$. Folglich $x \\in X \\cap (Y \\cup Z)$. $\\square$</p>
    `,
  },
  {
    id: 4,
    sheet: 2,
    title: "Aufgabe 1 (Blatt 2): Relationen verknüpfen",
    group: "Gruppe 1 (HHU)",
    problemHtml: `Sei $X = \\{a,b,c\\}$, $R = \\{(a,b), (b,c)\\}$ und $S = \\{(b,a), (c,b), (c,a)\\}$. Bestimmen Sie $R^{-1}$ und $S \\circ R$.`,
    solutionHtml: `
      <p><strong>Inverse Relation $R^{-1}$ (Pfeile umkehren):</strong></p>
      <p class="font-mono" style="color: var(--brand);">$R^{-1} = \\{(b,a), (c,b)\\}$</p>
      <p style="margin-top: 8px;"><strong>Verkettung $S \\circ R$ (zuerst $R$, dann $S$):</strong></p>
      <ul>
        <li>Start $(a,b) \\in R$: Suche Paare in $S$, die mit $b$ beginnen $\\implies (b,a) \\in S$. Ergibt das Paar <strong>$(a,a)$</strong>.</li>
        <li>Start $(b,c) \\in R$: Suche Paare in $S$, die mit $c$ beginnen $\\implies (c,b) \\in S$ und $(c,a) \\in S$. Ergibt <strong>$(b,b)$</strong> und <strong>$(b,a)$</strong>.</li>
      </ul>
      <p class="font-mono" style="color: var(--status-done); font-weight: bold;">$S \\circ R = \\{(a,a), (b,b), (b,a)\\}$</p>
    `,
  },
  {
    id: 5,
    sheet: 2,
    title: "Aufgabe 2 (Blatt 2): Eigenschaften von Relationen",
    group: "Gruppe 1 & 2 (HHU)",
    problemHtml: `Untersuchen Sie die Relation auf $\\mathbb{Z}$ auf Reflexivität, Symmetrie, Antisymmetrie, Asymmetrie und Transitivität:<br>Gruppe 1: $R = \\{(x,y) \\in \\mathbb{Z} \\times \\mathbb{Z} : y = x + 1\\}$<br>Gruppe 2: $R = \\{(x,y) \\in \\mathbb{Z} \\times \\mathbb{Z} : 2 \\mid (x - y)\\}$.`,
    solutionHtml: `
      <div>
        <p><strong style="color: var(--brand);">Gruppe 1 ($y = x + 1$):</strong></p>
        <ul>
          <li><strong>Nicht reflexiv:</strong> Für kein $x \\in \\mathbb{Z}$ gilt $x = x+1$. Gegenbeispiel: $(0,0) \\notin R$.</li>
          <li><strong>Nicht symmetrisch:</strong> $(0,1) \\in R$, aber $(1,0) \\notin R$ (da $0 \\neq 1+1$).</li>
          <li><strong>Antisymmetrisch:</strong> Gilt trivialerweise, da $(x,y) \\in R$ und $(y,x) \\in R$ niemals gleichzeitig wahr sein können ($y=x+1$ und $x=y+1 \\implies x = x+2$, Widerspruch).</li>
          <li><strong>Asymmetrisch:</strong> Gilt, da aus $(x,y) \\in R$ stets $(y,x) \\notin R$ folgt.</li>
          <li><strong>Nicht transitiv:</strong> $(0,1) \\in R$ und $(1,2) \\in R$, aber $(0,2) \\notin R$ (da $2 \\neq 0+1$).</li>
        </ul>
      </div>
      <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
        <p><strong style="color: var(--brand);">Gruppe 2 ($2 \\mid (x-y)$):</strong></p>
        <ul>
          <li><strong>Reflexiv:</strong> Für jedes $x \\in \\mathbb{Z}$ ist $x - x = 0 = 2 \\cdot 0$, also $2 \\mid (x-x) \\implies (x,x) \\in R$.</li>
          <li><strong>Symmetrisch:</strong> Ist $2 \\mid (x-y)$, d. h. $x-y = 2k$, so ist $y-x = -(x-y) = 2(-k)$, also $2 \\mid (y-x)$.</li>
          <li><strong>Nicht antisymmetrisch:</strong> $(0,2) \\in R$ und $(2,0) \\in R$, aber $0 \\neq 2$.</li>
          <li><strong>Nicht asymmetrisch:</strong> Da $(0,2) \\in R$ und $(2,0) \\in R$.</li>
          <li><strong>Transitiv:</strong> Gilt $x-y = 2k$ und $y-z = 2m$, so ist $x-z = (x-y)+(y-z) = 2(k+m)$, also $2 \\mid (x-z)$.</li>
        </ul>
        <p style="color: var(--status-done); font-weight: bold; margin-top: 6px;">Fazit: Gruppe 2 ist eine Äquivalenzrelation (Parität: gerade/ungerade)!</p>
      </div>
    `,
  },
  {
    id: 6,
    sheet: 2,
    title: "Aufgabe 4 (Blatt 2): Äquivalenz- vs. Ordnungsrelationen",
    group: "Gruppe 1 (HHU)",
    problemHtml: `Sei $X = \\{1,2,3\\}$, $R = \\{(1,1), (1,2), (2,1), (2,2), (3,3)\\}$. Entscheiden Sie über Äquivalenzrelation und/oder Ordnung. Geben Sie ggf. alle Äquivalenzklassen an.`,
    solutionHtml: `
      <p><strong>1. Reflexivität:</strong> Alle Paare $(1,1), (2,2), (3,3) \\in R$. $\\implies$ <strong>Reflexiv</strong>.</p>
      <p><strong>2. Symmetrie:</strong> $(1,2) \\in R \\implies (2,1) \\in R$. Alle anderen Paare sind auf der Diagonale. $\\implies$ <strong>Symmetrisch</strong>.</p>
      <p><strong>3. Antisymmetrie:</strong> Es gilt $(1,2) \\in R$ und $(2,1) \\in R$, aber $1 \\neq 2$. $\\implies$ <strong>NICHT antisymmetrisch</strong> (daher keine Ordnung!).</p>
      <p><strong>4. Transitivität:</strong> Gilt (z. B. $(2,1)$ und $(1,2) \\implies (2,2) \\in R$).</p>
      <p style="color: var(--status-done); font-weight: bold; margin-top: 6px;">Ergebnis: $R$ ist eine Äquivalenzrelation (aber keine Ordnung!).</p>
      <p><strong>Äquivalenzklassen:</strong></p>
      <ul>
        <li>$[1] = [2] = \\{1, 2\\}$</li>
        <li>$[3] = \\{3\\}$</li>
      </ul>
      <p class="muted tiny">Partition von $X$: $\{\\{1,2\\}, \\{3\\}\}$. Ein mögliches Vertretersystem wäre $\{1, 3\}$.</p>
    `,
  },
  {
    id: 7,
    sheet: 2,
    title: "Aufgabe 5 (Blatt 2): Abbildungen: Bild und Urbild",
    group: "Gruppe 1 & 2 (HHU)",
    problemHtml: `Bestimmen Sie $f(A)$ und $f^{-1}(B)$ vollständig für:<br>Gruppe 1: $f: \\mathbb{Z} \\to \\mathbb{Z}, n \\mapsto 2n+1$ mit $A = \\{-1, 0, 2\\}$, $B = \\{-3, 1, 4\\}$.<br>Gruppe 2: $f: \\mathbb{Z} \\to \\mathbb{N}_0, n \\mapsto n^2$ mit $A = \\{-2, 1, 3\\}$, $B = \\{0, 1, 4, 9\\}$.`,
    solutionHtml: `
      <div>
        <p><strong style="color: var(--brand);">Gruppe 1:</strong></p>
        <p>• <strong>Bild $f(A)$:</strong> Setze jedes Element aus $A$ ein:</p>
        <p class="font-mono" style="margin-left: 12px;">$f(-1) = 2(-1)+1 = -1$, $f(0) = 1$, $f(2) = 5 \\implies f(A) = \\{-1, 1, 5\\}$</p>
        <p>• <strong>Urbild $f^{-1}(B)$:</strong> Löse $2n+1 = b$ für $b \\in B$ in $\\mathbb{Z}$:</p>
        <ul style="margin-left: 12px;">
          <li>$2n+1 = -3 \\implies 2n = -4 \\implies n = -2 \\in \\mathbb{Z}$</li>
          <li>$2n+1 = 1 \\implies 2n = 0 \\implies n = 0 \\in \\mathbb{Z}$</li>
          <li>$2n+1 = 4 \\implies 2n = 3 \\implies n = 1.5 \\notin \\mathbb{Z}$ (keine Lösung in $\\mathbb{Z}$)</li>
        </ul>
        <p class="font-mono" style="margin-left: 12px; color: var(--status-done); font-weight: bold;">$f^{-1}(B) = \\{-2, 0\\}$</p>
      </div>
      <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
        <p><strong style="color: var(--brand);">Gruppe 2:</strong></p>
        <p>• $f(A)$: $f(-2) = 4$, $f(1) = 1$, $f(3) = 9 \\implies f(A) = \\{1, 4, 9\\}$.</p>
        <p>• $f^{-1}(B)$: Suche alle $n \\in \\mathbb{Z}$ mit $n^2 \\in \\{0, 1, 4, 9\\}$:</p>
        <p class="font-mono" style="margin-left: 12px; color: var(--status-done); font-weight: bold;">$f^{-1}(B) = \\{-3, -2, -1, 0, 1, 2, 3\\}$</p>
      </div>
    `,
  },
  {
    id: 8,
    sheet: 2,
    title: "Aufgabe 6 (Blatt 2): Verkettung von Abbildungen",
    group: "Gruppe 1 & 3 (HHU)",
    problemHtml: `Bestimmen Sie $g \\circ f$ mit Definitions- und Wertebereich für:<br>Gruppe 1: $f: \\mathbb{R} \\to \\mathbb{R}, x \\mapsto x^2+1$ und $g: \\mathbb{R} \\to \\mathbb{R}, t \\mapsto 3t-2$.<br>Gruppe 3: $f: \\{a,b,c\\} \\to \\{1,2,3\\}, a \\mapsto 2, b \\mapsto 1, c \\mapsto 2$ und $g: \\{1,2,3\\} \\to \\{x,y,z\\}, 1 \\mapsto x, 2 \\mapsto y, 3 \\mapsto z$.`,
    solutionHtml: `
      <div>
        <p><strong style="color: var(--brand);">Gruppe 1:</strong></p>
        <p>Definitionsbereich: $\\mathbb{R}$, Wertebereich: $\\mathbb{R}$.</p>
        <p class="font-mono">$(g \\circ f)(x) = g(f(x)) = g(x^2 + 1) = 3(x^2 + 1) - 2 = 3x^2 + 3 - 2 = 3x^2 + 1$.</p>
      </div>
      <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid var(--border);">
        <p><strong style="color: var(--brand);">Gruppe 3:</strong></p>
        <p>Definitionsbereich: $\\{a,b,c\\}$, Wertebereich: $\\{x,y,z\\}$.</p>
        <ul class="font-mono" style="margin-left: 12px;">
          <li>$(g \\circ f)(a) = g(f(a)) = g(2) = y$</li>
          <li>$(g \\circ f)(b) = g(f(b)) = g(1) = x$</li>
          <li>$(g \\circ f)(c) = g(f(c)) = g(2) = y$</li>
        </ul>
      </div>
    `,
  },
];

const filteredTasks = computed(() => {
  if (sheetFilter.value === 0) return hhuTasks;
  return hhuTasks.filter((t) => t.sheet === sheetFilter.value);
});

onMounted(async () => {
  await fetchProfile();
  ensureMathJaxLoaded();
  runRelationAnalysis();
  runComposition();
});
</script>

<style scoped>
.hhu-tool-page {
  min-height: calc(100vh - 70px);
  width: 100%;
  display: flex;
  flex-direction: column;
  padding: 16px 24px 80px;
  background: var(--bg);
  color: var(--text);
}

/* Access Denied Card */
.hhu-access-denied {
  max-width: 540px;
  margin: 60px auto;
  text-align: center;
  padding: 40px 24px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}
.ad-icon {
  font-size: 3rem;
  background: rgba(248, 113, 113, 0.12);
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  border: 1px solid rgba(248, 113, 113, 0.3);
}

/* Main Shell */
.hhu-shell {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  max-width: 1360px;
  margin: 0 auto;
}

/* Hero */
.hhu-hero {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
  padding: 24px 28px;
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.16) 0%, rgba(99, 102, 241, 0.08) 50%, rgba(14, 165, 233, 0.06) 100%), var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
}
.hhu-badge-row {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.hhu-chip {
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  padding: 4px 10px;
  border-radius: 999px;
  text-transform: uppercase;
}
.team-chip {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.35);
}
.uni-chip {
  background: rgba(56, 189, 248, 0.15);
  color: #7dd3fc;
  border: 1px solid rgba(56, 189, 248, 0.3);
}
.hhu-title {
  font-size: 1.65rem;
  font-weight: 800;
  margin: 0 0 6px;
  line-height: 1.25;
  background: linear-gradient(135deg, #ffffff 30%, #c7d2fe 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.hhu-subtitle {
  font-size: 0.88rem;
  color: var(--muted);
  max-width: 760px;
  margin: 0;
  line-height: 1.45;
}
.hhu-hero-right {
  flex-shrink: 0;
}
.hhu-score-box {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 12px 18px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 140px;
}
.score-label {
  font-size: 0.72rem;
  text-transform: uppercase;
  color: var(--muted);
  font-weight: 700;
}
.score-val {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--brand);
  margin: 2px 0 6px;
}
.score-bar-mini {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 4px;
}
.score-fill {
  height: 100%;
  background: var(--brand);
  transition: width 0.3s ease;
}

/* Tabs Navigation */
.hhu-tabs-nav {
  display: flex;
  gap: 10px;
  border-bottom: 1px solid var(--border);
  padding-bottom: 6px;
  overflow-x: auto;
}
.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  color: var(--muted);
  font-size: 0.9rem;
  font-weight: 600;
  padding: 10px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}
.tab-btn:hover {
  color: var(--text);
}
.tab-btn.active {
  color: var(--brand);
  border-bottom-color: var(--brand);
}
.tab-badge {
  font-size: 0.7rem;
  padding: 2px 6px;
  background: rgba(99, 102, 241, 0.25);
  color: #a5b4fc;
  border-radius: 999px;
}

/* Pane Intro */
.pane-intro-banner {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.2) 0%, rgba(30, 41, 59, 0.4) 100%);
  border: 1px solid rgba(99, 102, 241, 0.25);
  padding: 18px 24px;
  border-radius: 14px;
  margin-bottom: 20px;
}
.intro-tag {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #c7d2fe;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 6px;
  display: inline-block;
  margin-bottom: 6px;
}
.pane-intro-banner h2 {
  font-size: 1.25rem;
  margin: 0 0 6px;
}
.pane-intro-banner p {
  font-size: 0.85rem;
  color: var(--muted);
  margin: 0;
  line-height: 1.45;
}

/* THEORIE GRID */
.theorie-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
  gap: 18px;
}
.theorie-card {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.theorie-card.span-2 {
  grid-column: 1 / -1;
}
.tc-header {
  display: flex;
  align-items: center;
  gap: 10px;
}
.tc-icon {
  font-size: 1.3rem;
  background: rgba(99, 102, 241, 0.12);
  padding: 6px;
  border-radius: 8px;
}
.tc-header h3 {
  font-size: 1rem;
  margin: 0;
}
.tc-body {
  font-size: 0.86rem;
  line-height: 1.5;
  color: var(--text);
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.tc-callout {
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 0.8rem;
  line-height: 1.45;
}
.tc-callout.warn {
  background: rgba(245, 158, 11, 0.1);
  border-left: 4px solid #f59e0b;
  color: #fef3c7;
}
.tc-callout.info {
  background: rgba(99, 102, 241, 0.1);
  border-left: 4px solid #6366f1;
  color: #e0e7ff;
}
.callout-hint {
  margin-top: 4px;
  font-style: italic;
  color: var(--muted);
}
.math-list-box {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 0.82rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.props-mini-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.prop-chip {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 8px 10px;
  border-radius: 8px;
  font-size: 0.78rem;
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.prop-chip.full {
  grid-column: 1 / -1;
}
.section-sub ul {
  margin: 6px 0 0;
  padding-left: 18px;
}
.section-sub.border-top {
  border-top: 1px solid var(--border);
  padding-top: 10px;
}
.tc-subgrid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 16px;
}
.sub-col {
  background: var(--surface);
  border: 1px solid var(--border);
  padding: 14px;
  border-radius: 10px;
  font-size: 0.82rem;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.code-box {
  background: var(--card);
  padding: 6px 8px;
  border-radius: 6px;
  border: 1px solid var(--border);
  font-family: monospace;
}

/* QUIZ PANEL */
.quiz-panel {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.qp-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid var(--border);
  padding-bottom: 14px;
}
.qp-header h2 {
  font-size: 1.25rem;
  margin: 0 0 4px;
}
.quiz-progress-section {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.progress-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--muted);
  font-weight: 600;
}
.progress-track {
  width: 100%;
  height: 8px;
  background: var(--surface);
  border-radius: 999px;
  overflow: hidden;
  border: 1px solid var(--border);
}
.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #38bdf8);
  transition: width 0.3s ease;
}
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.question-card {
  padding: 18px 20px;
  border: 1px solid var(--border);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: border-color 0.2s ease;
}
.question-card.answered.correct {
  border-color: rgba(52, 211, 153, 0.45);
}
.question-card.answered.wrong {
  border-color: rgba(248, 113, 113, 0.45);
}
.qc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.qc-tag {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  color: #a5b4fc;
  background: rgba(99, 102, 241, 0.15);
  padding: 3px 8px;
  border-radius: 6px;
}
.qc-status {
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--muted);
}
.qc-status.status-ok {
  color: #34d399;
}
.qc-status.status-fail {
  color: #f87171;
}
.qc-question {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.4;
}
.qc-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.qc-opt-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 10px;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--text);
  font-size: 0.85rem;
  cursor: pointer;
  text-align: left;
  transition: all 0.15s ease;
}
.qc-opt-btn:hover:not(:disabled) {
  border-color: var(--brand);
  background: rgba(99, 102, 241, 0.08);
}
.qc-opt-btn.opt-correct {
  background: rgba(52, 211, 153, 0.12);
  border-color: #34d399;
  color: #d1fae5;
}
.qc-opt-btn.opt-selected-wrong {
  background: rgba(248, 113, 113, 0.12);
  border-color: #f87171;
  color: #fee2e2;
}
.qc-opt-btn.opt-dimmed {
  opacity: 0.55;
  cursor: not-allowed;
}
.opt-badge {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
}
.opt-correct .opt-badge {
  background: #10b981;
  color: white;
  border-color: #10b981;
}
.opt-selected-wrong .opt-badge {
  background: #ef4444;
  color: white;
  border-color: #ef4444;
}
.qc-explanation {
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 0.82rem;
  line-height: 1.45;
}
.qc-explanation.exp-correct {
  background: rgba(52, 211, 153, 0.1);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #d1fae5;
}
.qc-explanation.exp-wrong {
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.3);
  color: #fee2e2;
}

/* TOOL BOX & SANDBOX */
.sandbox-pane {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
.tool-box {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}
.tb-header {
  display: flex;
  align-items: center;
  gap: 12px;
}
.tb-icon {
  font-size: 1.5rem;
  background: rgba(99, 102, 241, 0.15);
  padding: 8px;
  border-radius: 10px;
}
.tb-header h2 {
  font-size: 1.15rem;
  margin: 0 0 2px;
}
.tool-content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 16px;
}
.inputs-col,
.results-col,
.closures-col {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}
.inputs-col h3,
.results-col h3,
.closures-col h3 {
  font-size: 0.92rem;
  margin: 0;
  border-bottom: 1px solid var(--border);
  padding-bottom: 8px;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.form-group label {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
}
.hhu-input,
.hhu-textarea {
  background: var(--input-bg);
  border: 1px solid var(--border);
  color: var(--text);
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color 0.2s ease;
}
.hhu-input:focus,
.hhu-textarea:focus {
  border-color: var(--brand);
}
.btn-row {
  display: flex;
  gap: 8px;
  margin-top: 4px;
}
.props-status-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.prop-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 0.8rem;
  background: var(--card);
  border: 1px solid var(--border);
}
.prop-row.ok {
  background: rgba(52, 211, 153, 0.08);
  border-color: rgba(52, 211, 153, 0.3);
  color: #a7f3d0;
}
.prop-row.fail {
  background: rgba(248, 113, 113, 0.08);
  border-color: rgba(248, 113, 113, 0.3);
  color: #fecaca;
}
.prop-row.neutral {
  background: var(--card);
}
.pr-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.pr-mark {
  font-weight: 800;
  font-size: 0.95rem;
}
.special-labels-row {
  display: flex;
  gap: 8px;
  margin-top: 6px;
  flex-wrap: wrap;
}
.hhu-pill {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}
.pill-success {
  background: rgba(52, 211, 153, 0.2);
  color: #34d399;
}
.pill-info {
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}
.pill-muted {
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}
.closure-blocks {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.cb-item {
  background: var(--card);
  border: 1px solid var(--border);
  padding: 8px 12px;
  border-radius: 8px;
}
.cb-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--muted);
  display: block;
  margin-bottom: 2px;
}
.cb-val {
  margin: 0;
  font-size: 0.82rem;
  word-break: break-all;
}
.cb-item.equiv-box {
  border-color: rgba(52, 211, 153, 0.4);
  background: rgba(52, 211, 153, 0.08);
}
.cb-label.highlight,
.cb-val.highlight {
  color: #34d399;
}

/* COMPOSITION TOOL */
.comp-inputs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}
.action-align {
  justify-content: flex-end;
}
.comp-results-box {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
}
.comp-summary-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
.cs-item {
  background: var(--card);
  border: 1px solid var(--border);
  padding: 10px 14px;
  border-radius: 8px;
}
.cs-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--muted);
}
.cs-val {
  margin: 4px 0 0;
  font-size: 0.88rem;
  word-break: break-all;
}
.cs-val.highlight {
  color: #34d399;
  font-weight: 700;
}
.comp-steps-section {
  border-top: 1px solid var(--border);
  padding-top: 10px;
  font-size: 0.82rem;
}
.comp-steps-section ul {
  margin: 6px 0 0;
  padding-left: 20px;
  color: var(--text);
  line-height: 1.5;
}

/* AUFGABEN PANE */
.aufgaben-card {
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.ac-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  border-bottom: 1px solid var(--border);
  padding-bottom: 16px;
  flex-wrap: wrap;
  gap: 14px;
}
.ac-header h2 {
  font-size: 1.25rem;
  margin: 6px 0 4px;
}
.ac-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.filter-chip {
  padding: 6px 12px;
  border-radius: 8px;
  font-size: 0.78rem;
  font-weight: 600;
  background: var(--surface);
  border: 1px solid var(--border);
  color: var(--muted);
  cursor: pointer;
  transition: all 0.2s ease;
}
.filter-chip.active {
  background: var(--brand);
  color: white;
  border-color: var(--brand);
}
.task-accordions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.task-item {
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}
.task-head-btn {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  background: var(--surface);
  border: none;
  color: var(--text);
  cursor: pointer;
  text-align: left;
  transition: background 0.15s ease;
}
.task-head-btn:hover {
  background: rgba(255, 255, 255, 0.04);
}
.th-left {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.th-meta {
  display: flex;
  gap: 8px;
  align-items: center;
}
.sheet-tag {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.2);
  color: #a5b4fc;
}
.group-tag {
  font-size: 0.72rem;
  color: var(--muted);
}
.task-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}
.th-arrow {
  font-size: 0.75rem;
  color: var(--muted);
  transition: transform 0.2s ease;
}
.th-arrow.open {
  transform: rotate(180deg);
}
.task-body {
  padding: 18px;
  background: var(--card);
  border-top: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 14px;
  font-size: 0.86rem;
  line-height: 1.5;
}
.problem-box {
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  padding: 12px 16px;
  border-radius: 8px;
}
.pb-title {
  color: #c7d2fe;
  display: block;
  margin-bottom: 4px;
  font-size: 0.82rem;
}
.solution-box {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.sb-title {
  color: var(--text);
  font-size: 0.85rem;
}
.solution-box ul {
  margin: 4px 0 0;
  padding-left: 20px;
}

/* Responsive */
@media (max-width: 768px) {
  .hhu-hero {
    flex-direction: column;
    align-items: flex-start;
  }
  .hhu-hero-right {
    width: 100%;
  }
  .hhu-score-box {
    width: 100%;
  }
  .comp-summary-row {
    grid-template-columns: 1fr;
  }
}
</style>
