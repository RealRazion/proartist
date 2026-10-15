<template>
  <div class="tournament-detail-page">
    <!-- Ambient Cyber Glow -->
    <div class="ambient-glow"></div>

    <!-- Floating Reaction Particles -->
    <div class="floating-reactions-layer" pointer-events="none">
      <div
        v-for="p in activeParticles"
        :key="p.id"
        class="reaction-particle"
        :style="{ left: p.x + 'px', top: p.y + 'px', animationDuration: p.duration + 's' }"
      >
        {{ p.emoji }}
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- HEADER: HERO BANNER -->
    <!-- ================================================================= -->
    <header class="detail-header card">
      <div class="header-top-row">
        <button class="btn ghost btn-sm btn-back-arena" @click="goBack">
          ← Zurück zur Contest-Arena
        </button>
        <div class="top-status-pills">
          <span class="badge-status-pill" :class="`status-${(tournament?.status || 'draft').toLowerCase()}`">
            {{ statusLabel(tournament?.status) }}
          </span>
          <span v-if="tournament?.is_no_loss" class="badge-no-loss">
            🛡️ No Loss Bracket
          </span>
          <span class="badge-genre-tag">{{ tournament?.genre || 'Trap & 808' }}</span>
        </div>
      </div>

      <div class="hero-detail-grid">
        <div class="hero-main-info">
          <div class="kicker-league">
            <span class="live-dot"></span>
            <span>UNYQ CIRCUIT // TOURNAMENT DETAIL</span>
          </div>
          <div class="title-with-actions">
            <h1 class="tournament-title">{{ tournament?.title || "UNYQ Beat Battle" }}</h1>
            <button v-if="isTeam" class="btn ghost btn-sm btn-edit-meta" @click="openEditModal" title="Turnierdaten bearbeiten">
              ✏️ Bearbeiten
            </button>
          </div>
          <p class="tournament-description">
            {{ cleanDescription(tournament?.description) || "Der ultimative Battle-Wettbewerb im UNYQ Circuit. Kämpfe um Ruhm, Ranked Points und Preisgeld." }}
          </p>

          <div class="stats-ribbon">
            <div class="sr-item">
              <span class="sr-icon">💰</span>
              <div>
                <strong class="sr-val">{{ tournament?.prize_pool || "1.500 € Cash" }}</strong>
                <span class="sr-lbl">Preispool Gesamt</span>
              </div>
            </div>
            <div class="sr-item">
              <span class="sr-icon">👥</span>
              <div>
                <strong class="sr-val">{{ applicationRows.length }} Artists</strong>
                <span class="sr-lbl">Bewerber / Teilnehmer</span>
              </div>
            </div>
            <div class="sr-item">
              <span class="sr-icon">📤</span>
              <div>
                <strong class="sr-val">{{ submissionRows.length }} Runden</strong>
                <span class="sr-lbl">Eingereicht</span>
              </div>
            </div>
            <div class="sr-item">
              <span class="sr-icon">⚔️</span>
              <div>
                <strong class="sr-val">{{ battleRows.length }} Duelle</strong>
                <span class="sr-lbl">Battles</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Status & Action Box -->
        <div class="card hero-phase-action-box">
          <div v-if="tournament?.status === 'APPLICATION_OPEN'">
            <div class="phase-indicator">
              <span class="pulse-dot green"></span>
              <strong>Bewerbungsphase Aktiv</strong>
            </div>
            <p class="muted small">Reiche deine Hörprobe ein, um dich für den Turnierbaum zu qualifizieren.</p>
            <button class="btn full-w btn-action-hero" @click="showApplyModal = true">
              ✍️ Jetzt als Artist bewerben
            </button>
          </div>

          <div v-else-if="tournament?.status === 'SUBMISSION_OPEN'">
            <div class="phase-indicator">
              <span class="pulse-dot blue"></span>
              <strong>Einreichungsphase Läuft</strong>
            </div>
            <p class="muted small">Lade deinen Track oder dein Video für die anstehende Runde hoch.</p>
            <button class="btn full-w btn-action-hero" @click="showUploadModal = true">
              📤 Runde einreichen (Audio/Video)
            </button>
          </div>

          <div v-else-if="tournament?.status === 'BATTLES'">
            <div class="phase-indicator">
              <span class="pulse-dot red"></span>
              <strong>Battles &amp; Voting Live!</strong>
            </div>
            <p class="muted small">Die Duelle laufen. Höre beide Runden und vote für deinen Favoriten.</p>
            <button class="btn full-w btn-action-hero" @click="activeTab = 'battles'">
              ⚔️ Zu den Live Battles
            </button>
          </div>

          <div v-else>
            <div class="phase-indicator">
              <strong>Turnier Abgeschlossen</strong>
            </div>
            <p class="muted small">Ergebnisse und Gewinner stehen fest.</p>
          </div>

          <!-- Admin Director Quick Bar -->
          <div v-if="isTeam" class="admin-phase-stepper">
            <div class="admin-bar-head">
              <span class="admin-phase-lbl">👑 Admin Director Tools:</span>
              <button class="btn ghost btn-micro btn-danger-link" @click="confirmDeleteTournament">
                🗑️ Turnier löschen
              </button>
            </div>
            
            <div class="stepper-buttons">
              <button
                v-for="st in statusSteps"
                :key="st.value"
                class="btn ghost btn-micro"
                :class="{ active: tournament?.status === st.value }"
                @click="updateTournamentStatus(st.value)"
              >
                {{ st.label }}
              </button>
            </div>

            <div class="admin-quick-actions-row">
              <button class="btn btn-micro btn-accent" @click="generateBattles" title="Erstellt 1v1 Paarungen aus allen freigegebenen Einreichungen">
                ⚔️ Battles generieren
              </button>
              <button class="btn ghost btn-micro" @click="bulkApproveApplications" title="Nimmt alle offenen Bewerber sofort an">
                ✓ Alle Bewerbungen annehmen
              </button>
              <button class="btn ghost btn-micro btn-warn" @click="resetTournamentData" title="Battles leeren und Turnier zurücksetzen">
                ⚡ Turnier zurücksetzen
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <!-- DETAIL NAVIGATION TABS -->
    <nav class="detail-navigation-bar card">
      <div class="tabs-scroll">
        <button
          v-for="tab in tabs"
          :key="tab.key"
          class="nav-tab-btn"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span>{{ tab.label }}</span>
          <span v-if="tab.count !== undefined" class="tab-count-pill">{{ tab.count }}</span>
        </button>
      </div>
    </nav>

    <!-- ================================================================= -->
    <!-- TAB 1: BATTLES & VOTING SHOWDOWN -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'battles'" class="detail-tab-section">
      <div class="section-heading-bar">
        <div>
          <h2>⚔️ Aktive Duelle &amp; Voting ({{ battleRows.length }})</h2>
          <p class="muted">Höre beide Runden an, schalte nahtlos mit A/B um und stimme für deinen Favoriten ab.</p>
        </div>
        <div v-if="isTeam" class="heading-actions">
          <button class="btn btn-sm" @click="generateBattles">
            ⚔️ Neue Battles aus Runden generieren
          </button>
        </div>
      </div>

      <div class="battles-deck-grid" v-if="battleRows.length">
        <div v-for="b in battleRows" :key="b.id" class="card duel-card" :class="{ 'duel-closed': b.status === 'CLOSED' }">
          <div class="dc-top">
            <span class="dc-round">RUNDE {{ b.round_number || 1 }}</span>
            <span class="dc-status" :class="b.status === 'CLOSED' ? 'closed' : 'live'">
              {{ b.status === 'CLOSED' ? '🏁 Beendet' : '🔥 Voting Live' }}
            </span>
          </div>

          <div class="dc-showdown">
            <!-- Left Side -->
            <div class="dc-side left" :class="{ winner: b.winner === 'left' || b.winner_submission === b.left_submission }">
              <div class="dc-avatar" :class="{ playing: currentPlayingTrack === `battle-${b.id}-left` }">
                {{ (b.left_profile_name || 'A').charAt(0) }}
              </div>
              <strong class="dc-name">{{ b.left_profile_name }}</strong>
              <span class="dc-track-title muted small">{{ b.left_submission_title || 'Runde 1' }}</span>
              
              <button
                class="btn btn-sm btn-play-audio"
                :class="{ active: currentPlayingTrack === `battle-${b.id}-left` }"
                @click="toggleAudio(`battle-${b.id}-left`, b.left_profile_name)"
              >
                <span class="audio-wave-anim" v-if="currentPlayingTrack === `battle-${b.id}-left`">
                  <span></span><span></span><span></span>
                </span>
                <span>{{ currentPlayingTrack === `battle-${b.id}-left` ? '⏸ Pause' : '▶ Anhören' }}</span>
              </button>
              <div class="dc-votes">{{ b.votes_left || 0 }} Votes</div>
            </div>

            <!-- VS & Direct A/B Switch -->
            <div class="dc-center">
              <div class="dc-vs">VS</div>
              <button
                class="btn ghost btn-micro btn-ab-switch"
                @click="quickSwitchAB(b)"
                title="Zwischen beiden Artists nahtlos hin- und herschalten"
              >
                ⇄ A/B Switch
              </button>
            </div>

            <!-- Right Side -->
            <div class="dc-side right" :class="{ winner: b.winner === 'right' || b.winner_submission === b.right_submission }">
              <div class="dc-avatar right-av" :class="{ playing: currentPlayingTrack === `battle-${b.id}-right` }">
                {{ (b.right_profile_name || 'B').charAt(0) }}
              </div>
              <strong class="dc-name">{{ b.right_profile_name }}</strong>
              <span class="dc-track-title muted small">{{ b.right_submission_title || 'Runde 1' }}</span>

              <button
                class="btn btn-sm btn-play-audio"
                :class="{ active: currentPlayingTrack === `battle-${b.id}-right` }"
                @click="toggleAudio(`battle-${b.id}-right`, b.right_profile_name)"
              >
                <span class="audio-wave-anim" v-if="currentPlayingTrack === `battle-${b.id}-right`">
                  <span></span><span></span><span></span>
                </span>
                <span>{{ currentPlayingTrack === `battle-${b.id}-right` ? '⏸ Pause' : '▶ Anhören' }}</span>
              </button>
              <div class="dc-votes">{{ b.votes_right || 0 }} Votes</div>
            </div>
          </div>

          <!-- Vote Bar -->
          <div class="dc-meter">
            <div class="dc-bar-left" :style="{ width: getVotePct(b, 'left') + '%' }">
              {{ getVotePct(b, 'left') }}%
            </div>
            <div class="dc-bar-right" :style="{ width: getVotePct(b, 'right') + '%' }">
              {{ getVotePct(b, 'right') }}%
            </div>
          </div>

          <!-- Vote Actions -->
          <div class="dc-actions" v-if="b.status !== 'CLOSED'">
            <button
              class="btn btn-sm btn-vote-l"
              :class="{ voted: hasVotedSide(b, 'left') }"
              @click="castVote(b, 'left', $event)"
              :disabled="hasVoted(b)"
            >
              {{ hasVotedSide(b, 'left') ? '✓ Dein Vote' : `Vote ${b.left_profile_name}` }}
            </button>
            <button
              class="btn btn-sm btn-vote-r"
              :class="{ voted: hasVotedSide(b, 'right') }"
              @click="castVote(b, 'right', $event)"
              :disabled="hasVoted(b)"
            >
              {{ hasVotedSide(b, 'right') ? '✓ Dein Vote' : `Vote ${b.right_profile_name}` }}
            </button>
          </div>
          <div v-else class="dc-winner-banner">
            🏆 Sieger: <strong>{{ getWinnerName(b) }}</strong>
          </div>

          <!-- Admin Resolution Controls -->
          <div class="dc-admin-row" v-if="isTeam">
            <span class="admin-lbl">👑 Admin:</span>
            <template v-if="b.status !== 'CLOSED'">
              <button class="btn ghost btn-micro" @click="adminResolveBattle(b, 'left')">Left Win</button>
              <button class="btn ghost btn-micro" @click="adminResolveBattle(b, 'right')">Right Win</button>
              <button class="btn ghost btn-micro" @click="adminResolveBattle(b, 'auto')">Auto Close</button>
            </template>
            <button v-else class="btn ghost btn-micro" @click="reopenBattle(b)">🔄 Wieder öffnen</button>
            <button class="btn ghost btn-micro btn-danger" @click="deleteBattle(b)" title="Battle löschen">🗑️</button>
          </div>
        </div>
      </div>
      <div v-else class="card empty-state-box">
        <span class="empty-icon">⚔️</span>
        <h3>Noch keine aktiven Battles</h3>
        <p class="muted">Sobald Einreichungen vorliegen, können hier Duelle generiert werden.</p>
        <div v-if="isTeam" class="empty-actions">
          <button class="btn" @click="generateBattles">⚔️ Battles aus Teilnehmer-Runden generieren</button>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 2: INTERAKTIVER TURNIERBAUM (BRACKET TREE) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'bracket'" class="detail-tab-section">
      <div class="section-heading-bar">
        <div>
          <h2>🌳 Interaktiver Turnierbaum (Bracket)</h2>
          <p class="muted">Klicke auf ein Match, um die Runden anzuhören und Match-Details zu öffnen.</p>
        </div>
        <div v-if="isTeam" class="heading-actions">
          <button class="btn ghost btn-sm" @click="loadBracket">↻ Bracket neu laden</button>
        </div>
      </div>

      <div v-if="bracketData.quarterFinals?.length || bracketData.semiFinals?.length || bracketData.grandFinal?.artistA" class="card bracket-visual-board">
        <div class="bracket-rounds-container">
          <!-- Column 1: Viertelfinale / Runde 1 -->
          <div class="bracket-column">
            <h3 class="b-col-title">Viertelfinale / R1</h3>
            <div class="bracket-matches-list">
              <div
                v-for="m in bracketData.quarterFinals"
                :key="m.id"
                class="bracket-match-node"
                :class="{ completed: m.winner }"
                @click="inspectMatch(m)"
              >
                <div class="b-slot" :class="{ winner: m.winner === m.artistA }">
                  <span class="b-name">{{ m.artistA }}</span>
                  <span class="b-score">{{ m.scoreA }}</span>
                </div>
                <div class="b-slot" :class="{ winner: m.winner === m.artistB }">
                  <span class="b-name">{{ m.artistB }}</span>
                  <span class="b-score">{{ m.scoreB }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 2: Halbfinale / Runde 2 -->
          <div class="bracket-column">
            <h3 class="b-col-title">Halbfinale / R2</h3>
            <div class="bracket-matches-list semi-list">
              <div
                v-for="m in bracketData.semiFinals"
                :key="m.id"
                class="bracket-match-node"
                :class="{ completed: m.winner }"
                @click="inspectMatch(m)"
              >
                <div class="b-slot" :class="{ winner: m.winner === m.artistA }">
                  <span class="b-name">{{ m.artistA }}</span>
                  <span class="b-score">{{ m.scoreA }}</span>
                </div>
                <div class="b-slot" :class="{ winner: m.winner === m.artistB }">
                  <span class="b-name">{{ m.artistB }}</span>
                  <span class="b-score">{{ m.scoreB }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Column 3: Grand Final -->
          <div class="bracket-column">
            <h3 class="b-col-title final-title">👑 Grand Final</h3>
            <div class="bracket-matches-list final-list">
              <div
                class="bracket-match-node grand-final-node"
                @click="inspectMatch(bracketData.grandFinal)"
              >
                <div class="b-slot" :class="{ winner: bracketData.grandFinal?.winner === bracketData.grandFinal?.artistA }">
                  <span class="b-name">{{ bracketData.grandFinal?.artistA || 'Finalist 1' }}</span>
                  <span class="b-score">{{ bracketData.grandFinal?.scoreA || '0' }}</span>
                </div>
                <div class="b-slot" :class="{ winner: bracketData.grandFinal?.winner === bracketData.grandFinal?.artistB }">
                  <span class="b-name">{{ bracketData.grandFinal?.artistB || 'Finalist 2' }}</span>
                  <span class="b-score">{{ bracketData.grandFinal?.scoreB || '0' }}</span>
                </div>
              </div>

              <!-- Champion Trophy Box -->
              <div class="champion-crown-podium card">
                <span class="trophy-symbol">🏆</span>
                <strong>{{ bracketData.grandFinal?.winner || 'Finale läuft' }}</strong>
                <small class="champ-sub">UNYQ Circuit Champion</small>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="card empty-state-box">
        <span class="empty-icon">🌳</span>
        <h3>Noch kein Turnierbaum generiert</h3>
        <p class="muted">Der Turnierbaum wird automatisch sichtbar, sobald Duelle generiert wurden.</p>
        <div v-if="isTeam" class="empty-actions">
          <button class="btn" @click="generateBattles">⚔️ Jetzt Battles für Runde 1 generieren</button>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 3: TEILNEHMER & SUBMISSIONS -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'participants'" class="detail-tab-section">
      <div class="two-column-layout">
        <!-- Submissions Column -->
        <div class="card panel-box">
          <div class="pb-header">
            <div>
              <h3>Eingereichte Runden ({{ submissionRows.length }})</h3>
              <p class="muted small">Tracks &amp; Beats der teilnehmenden Artists</p>
            </div>
            <div class="pb-actions">
              <button v-if="isTeam && submissionRows.some(s => s.status === 'PENDING')" class="btn ghost btn-micro" @click="bulkApproveSubmissions">
                ✓ Alle freigeben
              </button>
              <button class="btn btn-sm" @click="showUploadModal = true">+ Runde einreichen</button>
            </div>
          </div>

          <div class="submissions-list" v-if="submissionRows.length">
            <div v-for="sub in submissionRows" :key="sub.id" class="sub-item-card">
              <div class="sub-info">
                <span class="sub-icon">🎵</span>
                <div>
                  <strong>{{ sub.title }}</strong>
                  <span class="sub-artist">von {{ sub.profile_name }} • Runde {{ sub.round_number || 1 }}</span>
                  <a v-if="sub.media_url" :href="sub.media_url" target="_blank" rel="noopener noreferrer" class="sub-media-link">
                    🔗 Externer Link
                  </a>
                </div>
              </div>

              <div class="sub-actions">
                <span class="badge-status-pill" :class="sub.status?.toLowerCase()">{{ sub.status }}</span>
                <button
                  class="btn ghost btn-sm btn-sub-play"
                  :class="{ active: currentPlayingTrack === `sub-${sub.id}` }"
                  @click="toggleAudio(`sub-${sub.id}`, sub.profile_name)"
                >
                  {{ currentPlayingTrack === `sub-${sub.id}` ? '⏸' : '▶ Anhören' }}
                </button>
                <template v-if="isTeam && sub.status === 'PENDING'">
                  <button class="btn btn-micro btn-accept" @click="decideSubmission(sub, 'APPROVED')">✓</button>
                  <button class="btn ghost btn-micro btn-reject" @click="decideSubmission(sub, 'REJECTED')">✕</button>
                </template>
                <button v-if="isTeam" class="btn ghost btn-micro btn-danger" @click="deleteSubmission(sub)" title="Einreichung löschen">🗑️</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted">Noch keine Runden eingereicht.</div>
        </div>

        <!-- Applications Column -->
        <div class="card panel-box">
          <div class="pb-header">
            <div>
              <h3>Bewerbungen &amp; Roster ({{ applicationRows.length }})</h3>
              <p class="muted small">Registrierte Bewerber für dieses Turnier</p>
            </div>
            <div class="pb-actions">
              <button v-if="isTeam && applicationRows.some(a => a.status === 'PENDING')" class="btn ghost btn-micro" @click="bulkApproveApplications">
                ✓ Alle annehmen
              </button>
              <button class="btn ghost btn-sm" @click="showApplyModal = true">+ Bewerben</button>
            </div>
          </div>

          <div class="applications-list" v-if="applicationRows.length">
            <div v-for="app in applicationRows" :key="app.id" class="app-item-card">
              <div class="app-info">
                <strong>{{ app.profile_name }}</strong>
                <p class="muted small">{{ app.message || 'Bewerbung eingereicht.' }}</p>
              </div>
              <div class="app-actions">
                <span class="badge-status-pill" :class="app.status?.toLowerCase()">{{ app.status }}</span>
                <template v-if="isTeam && app.status === 'PENDING'">
                  <button class="btn btn-micro btn-accept" @click="decideApplication(app, 'APPROVED')">✓</button>
                  <button class="btn ghost btn-micro btn-reject" @click="decideApplication(app, 'REJECTED')">✕</button>
                </template>
                <button v-if="isTeam" class="btn ghost btn-micro btn-danger" @click="deleteApplication(app)" title="Bewerbung löschen">🗑️</button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted">Noch keine Bewerbungen vorhanden.</div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 4: REGELN & PREISPOOL -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'rules'" class="detail-tab-section">
      <div class="rules-grid-layout">
        <div class="card rules-card">
          <h3>Offizielle Turnier-Regeln &amp; Kriterien</h3>
          <ul class="rules-bullet-list">
            <li>
              <strong>Originalität &amp; Copyright:</strong>
              Alle eingereichten Runden müssen selbst komponiert, produziert oder eingesungen sein. Samples müssen gecleared sein.
            </li>
            <li>
              <strong>Fristen &amp; Rundenabgabe:</strong>
              Runden müssen bis zur jeweiligen Runden-Deadline vollständig als Link (SoundCloud, Drive, YouTube) hochgeladen werden.
            </li>
            <li>
              <strong>48-Stunden Community Voting:</strong>
              Die Community stimmt in jedem Battle live per Web Audio Showdown ab. Verifizierte User erhalten +10 Community RP.
            </li>
            <li>
              <strong>Anti-Cheat &amp; Fair Play:</strong>
              Manipulierte Votes, IP-Spamming oder Botting führen zur sofortigen Disqualifikation.
            </li>
          </ul>
        </div>

        <div class="card prize-pool-card">
          <h3>Preispool &amp; Belohnungen</h3>
          <div class="prize-tiers-list">
            <div class="pt-item gold">
              <span class="pt-rank">1. Platz (Champion)</span>
              <strong class="pt-val">{{ tournament?.prize_pool || "1.500 € Cash + Studio Gear + VIP Pass" }}</strong>
            </div>
            <div class="pt-item silver">
              <span class="pt-rank">2. Platz (Runner-Up)</span>
              <strong class="pt-val">600 € Cash + UNYQ Sample Pack Bundle</strong>
            </div>
            <div class="pt-item bronze">
              <span class="pt-rank">3. Platz</span>
              <strong class="pt-val">400 € Cash + VIP Producer Pass</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- MODAL 1: APPLY MODAL -->
    <!-- ================================================================= -->
    <div v-if="showApplyModal" class="modal-overlay" @click.self="showApplyModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung für "{{ tournament?.title }}"</h3>
          <button class="btn ghost tiny" @click="showApplyModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitApply">
          <label>
            <span>Artist-Name *</span>
            <input v-model.trim="applyArtistName" class="input" required />
          </label>
          <label>
            <span>Demo- / Track-Link *</span>
            <input v-model.trim="applyDemoLink" class="input" required placeholder="https://soundcloud.com/..." />
          </label>
          <label>
            <span>Nachricht an die Jury</span>
            <textarea v-model.trim="applyMessage" class="input" rows="3" placeholder="Deine Motivation..."></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showApplyModal = false">Abbrechen</button>
            <button class="btn" type="submit">Bewerbung abschicken 🎤</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 2: UPLOAD ROUND MODAL -->
    <!-- ================================================================= -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Runde einreichen</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitRound">
          <label>
            <span>Runden-Nummer</span>
            <input v-model.number="uploadRoundNumber" type="number" min="1" max="8" class="input" />
          </label>
          <label>
            <span>Track-Titel für diese Runde *</span>
            <input v-model.trim="uploadRoundTitle" class="input" required placeholder="z. B. Runde 1 - Focus &amp; Flow" />
          </label>
          <label>
            <span>Audio- oder Video-Link (SoundCloud, Drive, YouTube) *</span>
            <input v-model.trim="uploadMediaUrl" class="input" required placeholder="https://..." />
          </label>
          <div class="grid-2-inputs">
            <label>
              <span>BPM</span>
              <input v-model.trim="uploadBpm" class="input" placeholder="140" />
            </label>
            <label>
              <span>Key / Tonart</span>
              <input v-model.trim="uploadKey" class="input" placeholder="C# Minor" />
            </label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showUploadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Runde einreichen 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 3: MATCH SHOWDOWN INSPECT MODAL -->
    <!-- ================================================================= -->
    <div v-if="selectedMatch" class="modal-overlay" @click.self="selectedMatch = null">
      <div class="modal card match-inspect-modal">
        <div class="modal-header">
          <h3>Match Showdown: {{ selectedMatch.artistA }} vs {{ selectedMatch.artistB }}</h3>
          <button class="btn ghost tiny" @click="selectedMatch = null">✕</button>
        </div>
        <div class="match-inspect-body">
          <div class="showdown-versus-row">
            <div class="versus-card" :class="{ winner: selectedMatch.winner === selectedMatch.artistA }">
              <div class="vc-avatar">{{ selectedMatch.artistA?.charAt(0) }}</div>
              <strong>{{ selectedMatch.artistA }}</strong>
              <span class="vc-score">{{ selectedMatch.scoreA }} Votes</span>
              <button
                class="btn ghost btn-sm"
                @click="toggleAudio(`match-${selectedMatch.id}-a`, selectedMatch.artistA)"
              >
                {{ currentPlayingTrack === `match-${selectedMatch.id}-a` ? '⏸ Pause' : '▶ Runde A hören' }}
              </button>
            </div>

            <div class="versus-divider">VS</div>

            <div class="versus-card" :class="{ winner: selectedMatch.winner === selectedMatch.artistB }">
              <div class="vc-avatar alt">{{ selectedMatch.artistB?.charAt(0) }}</div>
              <strong>{{ selectedMatch.artistB }}</strong>
              <span class="vc-score">{{ selectedMatch.scoreB }} Votes</span>
              <button
                class="btn ghost btn-sm"
                @click="toggleAudio(`match-${selectedMatch.id}-b`, selectedMatch.artistB)"
              >
                {{ currentPlayingTrack === `match-${selectedMatch.id}-b` ? '⏸ Pause' : '▶ Runde B hören' }}
              </button>
            </div>
          </div>
          <p class="muted small text-center" v-if="selectedMatch.winner">
            🏆 Sieger dieses Matches: <strong>{{ selectedMatch.winner }}</strong>
          </p>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 4: EDIT TOURNAMENT MODAL (ADMIN) -->
    <!-- ================================================================= -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Turnier bearbeiten</h3>
          <button class="btn ghost tiny" @click="showEditModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitEditTournament">
          <label>
            <span>Titel *</span>
            <input v-model.trim="editForm.title" class="input" required />
          </label>
          <label>
            <span>Preispool</span>
            <input v-model.trim="editForm.prize_pool" class="input" />
          </label>
          <label>
            <span>Genre / Sparte</span>
            <input v-model.trim="editForm.genre" class="input" />
          </label>
          <label>
            <span>Beschreibung</span>
            <textarea v-model.trim="editForm.description" class="input" rows="3"></textarea>
          </label>
          <label class="checkbox-row">
            <input v-model="editForm.is_no_loss" type="checkbox" />
            <span>🛡️ No-Loss Bracket Modus aktivieren</span>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showEditModal = false">Abbrechen</button>
            <button class="btn" type="submit">Änderungen speichern 💾</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import api from "../api";
import { battleAudio } from "../utils/battleAudioEngine";

const route = useRoute();
const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const tournament = ref(null);
const activeTab = ref("battles");
const currentPlayingTrack = ref(null);
const activeParticles = ref([]);
const userVotes = ref({});
const selectedMatch = ref(null);

const battleRows = ref([]);
const submissionRows = ref([]);
const applicationRows = ref([]);

const bracketData = ref({
  quarterFinals: [],
  semiFinals: [],
  grandFinal: null,
});

const tabs = computed(() => [
  { key: "battles", label: "⚔️ Battles & Voting", count: battleRows.value.length },
  { key: "bracket", label: "🌳 Turnierbaum" },
  { key: "participants", label: "👥 Teilnehmer & Runden", count: submissionRows.value.length },
  { key: "rules", label: "📜 Regeln & Preispool" },
]);

const statusSteps = [
  { value: "APPLICATION_OPEN", label: "Bewerbung offen" },
  { value: "SUBMISSION_OPEN", label: "Einreichung offen" },
  { value: "BATTLES", label: "Battles live" },
  { value: "CLOSED", label: "Beendet" },
];

/* Modals State */
const showApplyModal = ref(false);
const applyArtistName = ref("");
const applyDemoLink = ref("");
const applyMessage = ref("");

const showUploadModal = ref(false);
const uploadRoundNumber = ref(1);
const uploadRoundTitle = ref("");
const uploadMediaUrl = ref("");
const uploadBpm = ref("140");
const uploadKey = ref("C# Minor");

const showEditModal = ref(false);
const editForm = ref({
  title: "",
  prize_pool: "",
  genre: "",
  description: "",
  is_no_loss: false,
});

function statusLabel(status) {
  const map = {
    APPLICATION_OPEN: "🟢 Bewerbung offen",
    SUBMISSION_OPEN: "🔵 Einreichung offen",
    BATTLES: "🔴 Battles live",
    CLOSED: "⚪ Beendet",
    DRAFT: "Entwurf",
  };
  return map[status] || status || "Live";
}

function cleanDescription(desc) {
  if (!desc) return "";
  return desc.replace(/\[Preispool:[^\]]+\]/gi, "").replace(/\[Genre:[^\]]+\]/gi, "").replace(/\[Slots:[^\]]+\]/gi, "").trim();
}

function goBack() {
  battleAudio.stopPlayback();
  currentPlayingTrack.value = null;
  if (route.path.includes("platforms")) {
    router.push({ name: "platform-contests" });
  } else {
    router.push({ name: "tournaments" });
  }
}

/* Audio Player Synthesizer / Player Engine */
function toggleAudio(trackKey, artistName) {
  if (currentPlayingTrack.value === trackKey) {
    currentPlayingTrack.value = null;
    battleAudio.stopPlayback();
    showToast("Wiedergabe pausiert", "info");
  } else {
    currentPlayingTrack.value = trackKey;
    battleAudio.startBeatLoop(trackKey);
    showToast(`▶ Spiele Runde von ${artistName} ab (320 kbps Studio Stream)`, "info");
  }
}

function quickSwitchAB(battle) {
  const current = currentPlayingTrack.value;
  const leftKey = `battle-${battle.id}-left`;
  const rightKey = `battle-${battle.id}-right`;

  if (current === leftKey) {
    currentPlayingTrack.value = rightKey;
    battleAudio.startBeatLoop(rightKey);
    showToast(`⇄ Umschalten auf ${battle.right_profile_name} Runde`, "info");
  } else {
    currentPlayingTrack.value = leftKey;
    battleAudio.startBeatLoop(leftKey);
    showToast(`⇄ Umschalten auf ${battle.left_profile_name} Runde`, "info");
  }
}

/* Voting Mechanics */
function getVotePct(battle, side) {
  const total = (battle.votes_left || 0) + (battle.votes_right || 0);
  if (!total) return 50;
  const count = side === "left" ? battle.votes_left : battle.votes_right;
  return Math.round((count / total) * 100);
}

function hasVoted(battle) {
  return Boolean(userVotes.value[battle.id]);
}

function hasVotedSide(battle, side) {
  return userVotes.value[battle.id] === side;
}

function getWinnerName(battle) {
  if (battle.winner === "left" || battle.winner_submission === battle.left_submission) {
    return battle.left_profile_name;
  }
  if (battle.winner === "right" || battle.winner_submission === battle.right_submission) {
    return battle.right_profile_name;
  }
  return battle.votes_left >= battle.votes_right ? battle.left_profile_name : battle.right_profile_name;
}

async function castVote(battle, side, event) {
  if (hasVoted(battle)) {
    showToast("Du hast für dieses Battle bereits abgestimmt!", "warning");
    return;
  }

  if (side === "left") {
    battle.votes_left = (battle.votes_left || 0) + 1;
  } else {
    battle.votes_right = (battle.votes_right || 0) + 1;
  }

  userVotes.value[battle.id] = side;
  localStorage.setItem("unyq_arena_votes", JSON.stringify(userVotes.value));

  battleAudio.playVoteChime();
  spawnReactionParticle("🗳️", event);
  spawnReactionParticle("⚡", event);

  showToast(
    `Vote gezählt für ${side === 'left' ? battle.left_profile_name : battle.right_profile_name}! +10 Community RP erhalten ⚡`,
    "success"
  );

  try {
    const subId = side === "left"
      ? (battle.left_submission || battle.left_submission_id)
      : (battle.right_submission || battle.right_submission_id);

    if (subId) {
      await api.post("tournament-votes/", {
        battle: battle.id,
        selected_submission: subId,
      });
    }
  } catch {
    // fallback
  }
}

function spawnReactionParticle(emoji, event) {
  const x = event?.clientX || window.innerWidth / 2;
  const y = event?.clientY || window.innerHeight / 2;
  const id = Date.now() + Math.random();

  activeParticles.value.push({
    id,
    emoji,
    x: x - 16 + (Math.random() * 40 - 20),
    y: y - 20,
    duration: 1.2 + Math.random() * 0.6,
  });

  setTimeout(() => {
    activeParticles.value = activeParticles.value.filter((p) => p.id !== id);
  }, 1800);
}

/* Admin Actions */
async function adminResolveBattle(battle, resolution) {
  battle.status = "CLOSED";
  const winnerSub = resolution === "left"
    ? (battle.left_submission || battle.left_submission_id)
    : (resolution === "right" ? (battle.right_submission || battle.right_submission_id) : null);

  if (resolution === "left") {
    battle.winner = "left";
    showToast(`🏆 ${battle.left_profile_name} offiziell zum Sieger erklärt!`, "success");
  } else if (resolution === "right") {
    battle.winner = "right";
    showToast(`🏆 ${battle.right_profile_name} offiziell zum Sieger erklärt!`, "success");
  } else {
    battle.winner = (battle.votes_left || 0) >= (battle.votes_right || 0) ? "left" : "right";
    showToast(`Battle geschlossen: ${getWinnerName(battle)} gewinnt! ✨`, "success");
  }

  try {
    await api.post(`tournament-battles/${battle.id}/close/`, winnerSub ? { winner_submission: winnerSub } : {});
    await loadBracket();
  } catch {
    // fallback
  }
}

async function updateTournamentStatus(newStatus) {
  if (!tournament.value?.id) return;
  tournament.value.status = newStatus;
  try {
    await api.patch(`tournaments/${tournament.value.id}/`, { status: newStatus });
    showToast(`Status auf "${statusLabel(newStatus)}" gesetzt! ⚡`, "success");
  } catch {
    showToast("Status lokal aktualisiert.", "info");
  }
}

async function generateBattles() {
  const id = tournament.value?.id;
  if (!id) return;

  try {
    const { data } = await api.post(`tournaments/${id}/generate-round-battles/`, {
      round_number: 1,
      auto_approve: true,
    });
    if (data.created_battles_count > 0) {
      showToast(`${data.created_battles_count} Battles automatisch generiert! ⚔️`, "success");
      activeTab.value = "battles";
      await loadBattles();
      await loadBracket();
    } else {
      showToast("Keine Battles erzeugt: Es werden mindestens 2 eingereichte Runden benötigt.", "warning");
    }
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Battles nicht generieren.", "warning");
  }
}

async function bulkApproveApplications() {
  const id = tournament.value?.id;
  if (!id) return;

  try {
    const { data } = await api.post(`tournaments/${id}/accept-all-applications/`);
    showToast(`${data.approved_count || 'Alle'} Bewerbungen freigegeben! 🎉`, "success");
    await loadApplications();
  } catch {
    applicationRows.value.forEach(a => a.status = "APPROVED");
    showToast("Bewerbungen freigegeben.", "success");
  }
}

async function bulkApproveSubmissions() {
  const id = tournament.value?.id;
  if (!id) return;

  try {
    const { data } = await api.post(`tournaments/${id}/submissions/bulk-decision/`, {
      decision: "APPROVED",
    });
    showToast(`${data.updated_count || 'Alle'} Runden freigegeben! 🚀`, "success");
    await loadSubmissions();
  } catch {
    submissionRows.value.forEach(s => s.status = "APPROVED");
    showToast("Runden freigegeben.", "success");
  }
}

async function decideApplication(app, decision) {
  app.status = decision;
  try {
    await api.post(`tournament-applications/${app.id}/decision/`, { decision });
    showToast(`Bewerbung ${decision === 'APPROVED' ? 'angenommen' : 'abgelehnt'}.`, "info");
  } catch {
    // fallback
  }
}

async function decideSubmission(sub, decision) {
  sub.status = decision;
  try {
    await api.post(`tournament-submissions/${sub.id}/decision/`, { decision });
    showToast(`Einreichung ${decision === 'APPROVED' ? 'freigegeben' : 'abgelehnt'}.`, "info");
  } catch {
    // fallback
  }
}

async function confirmDeleteTournament() {
  if (!window.confirm(`Turnier "${tournament.value?.title}" wirklich unwiderruflich löschen?`)) return;
  try {
    await api.delete(`tournaments/${tournament.value.id}/`);
    showToast("Turnier erfolgreich gelöscht.", "success");
    goBack();
  } catch {
    showToast("Turnier konnte nicht gelöscht werden.", "error");
  }
}

function openEditModal() {
  if (!tournament.value) return;
  editForm.value = {
    title: tournament.value.title || "",
    prize_pool: tournament.value.prize_pool || "1.500 € Cash",
    genre: tournament.value.genre || "Trap & 808",
    description: cleanDescription(tournament.value.description) || "",
    is_no_loss: Boolean(tournament.value.is_no_loss),
  };
  showEditModal.value = true;
}

async function submitEditTournament() {
  const id = tournament.value?.id;
  if (!id) return;

  const prizeText = editForm.value.prize_pool || "1.500 € Cash";
  const genreText = editForm.value.genre || "Trap & 808";
  const metaDesc = `[Preispool: ${prizeText}] [Genre: ${genreText}]\n\n${editForm.value.description}`;

  try {
    const { data } = await api.patch(`tournaments/${id}/`, {
      title: editForm.value.title,
      description: metaDesc,
      is_no_loss: editForm.value.is_no_loss,
    });
    tournament.value = {
      ...tournament.value,
      ...data,
      prize_pool: prizeText,
      genre: genreText,
    };
    showToast("Turnierdaten erfolgreich aktualisiert! 💾", "success");
  } catch {
    tournament.value.title = editForm.value.title;
    tournament.value.prize_pool = prizeText;
    tournament.value.genre = genreText;
    tournament.value.description = metaDesc;
    tournament.value.is_no_loss = editForm.value.is_no_loss;
    showToast("Turnierdaten lokal aktualisiert.", "success");
  }
  showEditModal.value = false;
}

/* Submitting Application & Round */
async function submitApply() {
  const tId = tournament.value?.id;
  const msg = `Artist: ${applyArtistName.value} | Demo: ${applyDemoLink.value} | ${applyMessage.value}`;

  try {
    const { data } = await api.post("tournament-applications/", {
      tournament: tId,
      message: msg,
    });
    applicationRows.value.unshift({
      id: data.id,
      profile_name: applyArtistName.value,
      status: "PENDING",
      message: msg,
    });
  } catch {
    applicationRows.value.unshift({
      id: Date.now(),
      profile_name: applyArtistName.value,
      status: "PENDING",
      message: msg,
    });
  }

  showApplyModal.value = false;
  showToast("Bewerbung erfolgreich eingereicht! 🎤", "success");
}

async function submitRound() {
  const tId = tournament.value?.id;
  const notes = `BPM: ${uploadBpm.value} | Key: ${uploadKey.value}`;

  try {
    const { data } = await api.post("tournament-submissions/", {
      tournament: tId,
      round_number: uploadRoundNumber.value || 1,
      title: uploadRoundTitle.value,
      media_url: uploadMediaUrl.value,
      notes,
    });
    submissionRows.value.unshift({
      id: data.id,
      title: uploadRoundTitle.value,
      profile_name: me.value?.name || "Du",
      round_number: uploadRoundNumber.value || 1,
      status: "PENDING",
      media_url: uploadMediaUrl.value,
    });
  } catch {
    submissionRows.value.unshift({
      id: Date.now(),
      title: uploadRoundTitle.value,
      profile_name: me.value?.name || "Du",
      round_number: uploadRoundNumber.value || 1,
      status: "PENDING",
      media_url: uploadMediaUrl.value,
    });
  }

  showUploadModal.value = false;
  showToast("Runde erfolgreich eingereicht! 🚀", "success");
}

function inspectMatch(match) {
  selectedMatch.value = match;
}

/* Admin Delete & Management Actions */
async function deleteApplication(app) {
  if (!window.confirm(`Bewerbung von "${app.profile_name}" wirklich löschen?`)) return;
  applicationRows.value = applicationRows.value.filter(a => a.id !== app.id);
  try {
    await api.delete(`tournament-applications/${app.id}/`);
    showToast("Bewerbung gelöscht.", "success");
  } catch {
    showToast("Bewerbung lokal entfernt.", "info");
  }
}

async function deleteSubmission(sub) {
  if (!window.confirm(`Einreichung "${sub.title}" wirklich löschen?`)) return;
  submissionRows.value = submissionRows.value.filter(s => s.id !== sub.id);
  try {
    await api.delete(`tournament-submissions/${sub.id}/`);
    showToast("Einreichung gelöscht.", "success");
  } catch {
    showToast("Einreichung lokal entfernt.", "info");
  }
}

async function deleteBattle(battle) {
  if (!window.confirm("Battle wirklich löschen?")) return;
  battleRows.value = battleRows.value.filter(b => b.id !== battle.id);
  try {
    await api.delete(`tournament-battles/${battle.id}/`);
    showToast("Battle gelöscht.", "success");
    await loadBracket();
  } catch {
    showToast("Battle lokal entfernt.", "info");
  }
}

async function reopenBattle(battle) {
  battle.status = "OPEN";
  battle.winner = null;
  try {
    await api.post(`tournament-battles/${battle.id}/reopen/`);
    showToast("Battle wieder geöffnet!", "success");
    await loadBracket();
  } catch {
    showToast("Battle lokal wieder geöffnet.", "info");
  }
}

async function resetTournamentData() {
  if (!window.confirm(`Möchtest du das Turnier "${tournament.value?.title}" wirklich zurücksetzen? Alle Battles werden gelöscht und Einreichungen zurückgesetzt.`)) return;
  try {
    await api.post(`tournaments/${tournament.value.id}/reset-tournament/`, {
      delete_battles: true,
      delete_submissions: false,
      new_status: "APPLICATION_OPEN",
    });
    showToast("Turnier erfolgreich zurückgesetzt! ⚡", "success");
    await loadTournament();
    await Promise.all([loadBattles(), loadSubmissions(), loadApplications(), loadBracket()]);
  } catch {
    battleRows.value = [];
    bracketData.value = { quarterFinals: [], semiFinals: [], grandFinal: null };
    showToast("Turnier lokal zurückgesetzt.", "info");
  }
}

/* Data Loading */
async function loadTournament() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournaments/${id}/`);
    let prize = "Noch kein Preispool festgelegt";
    let genre = "Allround";
    if (data.description) {
      const pMatch = data.description.match(/\[Preispool:\s*([^\]]+)\]/i);
      if (pMatch) prize = pMatch[1];
      const gMatch = data.description.match(/\[Genre:\s*([^\]]+)\]/i);
      if (gMatch) genre = gMatch[1];
    }
    tournament.value = {
      ...data,
      prize_pool: prize,
      genre: genre,
    };
  } catch {
    tournament.value = {
      id,
      title: "Turnier #" + id,
      description: "Turnier-Informationen werden geladen.",
      status: "DRAFT",
      genre: "Allround",
      prize_pool: "Kein Preispool festgelegt",
      is_no_loss: false,
    };
  }
}

async function loadBattles() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournament-battles/?tournament=${id}`);
    const list = Array.isArray(data) ? data : data?.results || [];
    battleRows.value = list.map(b => ({
      id: b.id,
      round_number: b.round_number || 1,
      status: b.status || "OPEN",
      left_submission: b.left_submission,
      right_submission: b.right_submission,
      left_profile_name: b.left_profile_name || "Artist A",
      right_profile_name: b.right_profile_name || "Artist B",
      left_submission_title: b.left_submission_title || "Runde 1",
      right_submission_title: b.right_submission_title || "Runde 1",
      votes_left: b.votes_left || 0,
      votes_right: b.votes_right || 0,
      winner_submission: b.winner_submission,
      winner: b.winner_submission === b.left_submission ? "left" : (b.winner_submission === b.right_submission ? "right" : null),
    }));
  } catch {
    battleRows.value = [];
  }
}

async function loadSubmissions() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournament-submissions/?tournament=${id}`);
    const list = Array.isArray(data) ? data : data?.results || [];
    submissionRows.value = list.map(s => ({
      id: s.id,
      title: s.title || `Runde ${s.round_number}`,
      profile_name: s.profile?.name || s.profile?.user?.username || "Artist",
      round_number: s.round_number || 1,
      status: s.status,
      media_url: s.media_url,
    }));
  } catch {
    submissionRows.value = [];
  }
}

async function loadApplications() {
  const id = route.params.tournamentId;
  try {
    const { data } = await api.get(`tournament-applications/?tournament=${id}`);
    const list = Array.isArray(data) ? data : data?.results || [];
    applicationRows.value = list.map(a => ({
      id: a.id,
      profile_name: a.profile?.name || a.profile?.user?.username || "Artist",
      status: a.status,
      message: a.message,
    }));
  } catch {
    applicationRows.value = [];
  }
}

async function loadBracket() {
  const id = route.params.tournamentId;
  bracketData.value = {
    quarterFinals: [],
    semiFinals: [],
    grandFinal: null,
  };
  try {
    const { data } = await api.get(`tournaments/${id}/bracket/`);
    if (data?.rounds?.length) {
      const r1 = data.rounds.find(r => r.round === 1)?.battles || [];
      const r2 = data.rounds.find(r => r.round === 2)?.battles || [];
      const r3 = data.rounds.find(r => r.round === 3)?.battles || [];

      if (r1.length) {
        bracketData.value.quarterFinals = r1.map(b => ({
          id: b.id,
          artistA: b.left_name,
          scoreA: `${b.votes_left}`,
          artistB: b.right_name,
          scoreB: `${b.votes_right}`,
          winner: b.winner_name || null,
        }));
      }

      if (r2.length) {
        bracketData.value.semiFinals = r2.map(b => ({
          id: b.id,
          artistA: b.left_name,
          scoreA: `${b.votes_left}`,
          artistB: b.right_name,
          scoreB: `${b.votes_right}`,
          winner: b.winner_name || null,
        }));
      }

      if (r3.length) {
        const f = r3[0];
        bracketData.value.grandFinal = {
          id: f.id,
          artistA: f.left_name,
          scoreA: `${f.votes_left}`,
          artistB: f.right_name,
          scoreB: `${f.votes_right}`,
          winner: f.winner_name || null,
        };
      }
    }
  } catch {
    // fallback clean
  }
}

onMounted(async () => {
  await fetchProfile();
  applyArtistName.value = me.value?.name || me.value?.username || "";

  try {
    const savedVotes = localStorage.getItem("unyq_arena_votes");
    if (savedVotes) userVotes.value = JSON.parse(savedVotes);
  } catch {
    // ignore
  }

  await loadTournament();
  await Promise.all([
    loadBattles(),
    loadSubmissions(),
    loadApplications(),
    loadBracket(),
  ]);
});

onBeforeUnmount(() => {
  battleAudio.stopPlayback();
});
</script>

<style scoped>
.tournament-detail-page {
  display: flex;
  flex-direction: column;
  gap: 26px;
  max-width: 1320px;
  margin: 0 auto;
  padding: 8px 16px 90px;
  position: relative;
}

.ambient-glow {
  position: absolute;
  top: 0;
  left: 15%;
  width: 70%;
  height: 340px;
  background: radial-gradient(circle, rgba(245, 158, 11, 0.15) 0%, rgba(59, 130, 246, 0.1) 45%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Floating Reactions */
.floating-reactions-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
}

.reaction-particle {
  position: absolute;
  font-size: 28px;
  animation: floatUpFade 1.4s ease-out forwards;
}

@keyframes floatUpFade {
  0% { transform: translateY(0) scale(0.6); opacity: 1; }
  50% { transform: translateY(-50px) scale(1.2); opacity: 0.9; }
  100% { transform: translateY(-120px) scale(1); opacity: 0; }
}

/* Header */
.detail-header {
  padding: 34px 32px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.18), transparent 50%),
    linear-gradient(135deg, rgba(28, 22, 45, 0.95), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 26px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  position: relative;
  z-index: 1;
}

.header-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-back-arena {
  font-weight: 700;
}

.top-status-pills {
  display: flex;
  gap: 8px;
}

.badge-status-pill {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
}

.badge-status-pill.status-battles,
.badge-status-pill.status-live {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-status-pill.approved {
  background: rgba(52, 211, 153, 0.15);
  color: #34d399;
}

.badge-status-pill.pending {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
}

.badge-status-pill.rejected {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.badge-no-loss {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}

.badge-genre-tag {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 999px;
}

.hero-detail-grid {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 32px;
  align-items: center;
}

.kicker-league {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #fbbf24;
  margin-bottom: 8px;
}

.live-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
}

.title-with-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.tournament-title {
  font-size: clamp(2rem, 3.5vw, 2.8rem);
  font-weight: 900;
  color: #fff;
  margin: 0;
  line-height: 1.15;
}

.btn-edit-meta {
  padding: 4px 10px;
  font-size: 11.5px;
}

.tournament-description {
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.6;
  margin: 12px 0 20px;
}

.stats-ribbon {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.sr-item {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.04);
  padding: 10px 14px;
  border-radius: 12px;
}

.sr-icon {
  font-size: 20px;
}

.sr-val {
  display: block;
  font-size: 13.5px;
  font-weight: 800;
  color: #fff;
}

.sr-lbl {
  font-size: 11px;
  color: var(--muted);
}

.hero-phase-action-box {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.25);
  border-radius: 20px;
  padding: 24px;
}

.phase-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #fff;
  margin-bottom: 8px;
}

.pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.pulse-dot.green { background: #34d399; }
.pulse-dot.blue { background: #60a5fa; }
.pulse-dot.red { background: #f87171; }

.btn-action-hero {
  padding: 12px;
  font-weight: 800;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  cursor: pointer;
  margin-top: 10px;
}

.admin-phase-stepper {
  margin-top: 16px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 12px;
}

.admin-bar-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.admin-phase-lbl {
  font-size: 11.5px;
  color: #fbbf24;
  font-weight: 700;
}

.btn-danger-link {
  color: #f87171 !important;
  font-size: 11px !important;
}

.stepper-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin-top: 8px;
}

.stepper-buttons .btn.active {
  background: #f59e0b;
  color: #0f172a;
  font-weight: 800;
}

.admin-quick-actions-row {
  display: flex;
  gap: 8px;
  margin-top: 10px;
  flex-wrap: wrap;
}

.btn-accent {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.4);
}

/* Nav */
.detail-navigation-bar {
  padding: 8px 12px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.tabs-scroll {
  display: flex;
  gap: 8px;
}

.nav-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 9px 16px;
  border-radius: 10px;
  background: transparent;
  border: none;
  color: var(--muted);
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.nav-tab-btn.active {
  background: #fff;
  color: #0f172a;
}

.tab-count-pill {
  background: rgba(0, 0, 0, 0.2);
  padding: 2px 6px;
  border-radius: 999px;
  font-size: 10px;
}

/* Section Common */
.section-heading-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.section-heading-bar h2 {
  font-size: 1.4rem;
  font-weight: 900;
  color: #fff;
  margin: 0 0 4px;
}

/* TAB 1: BATTLES */
.battles-deck-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(440px, 1fr));
  gap: 20px;
}

.duel-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
  transition: all 0.25s ease;
}

.duel-card:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.35);
}

.dc-top {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 700;
}

.dc-round {
  color: #fbbf24;
}

.dc-status.live {
  color: #f87171;
}

.dc-status.closed {
  color: var(--muted);
}

.dc-showdown {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 16px;
}

.dc-side {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 8px;
}

.dc-avatar {
  width: 54px;
  height: 54px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  font-weight: 800;
  transition: all 0.3s ease;
}

.dc-avatar.playing {
  box-shadow: 0 0 20px rgba(59, 130, 246, 0.8);
  transform: scale(1.08);
}

.dc-avatar.right-av {
  background: #a855f7;
}

.dc-avatar.right-av.playing {
  box-shadow: 0 0 20px rgba(168, 85, 247, 0.8);
}

.dc-side.winner .dc-avatar {
  border: 2px solid #fbbf24;
  box-shadow: 0 0 16px rgba(251, 191, 36, 0.5);
}

.dc-name {
  font-size: 14.5px;
  color: #fff;
}

.dc-track-title {
  max-width: 130px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.btn-play-audio {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  padding: 6px 12px;
}

.audio-wave-anim {
  display: inline-flex;
  gap: 2px;
  height: 12px;
  align-items: flex-end;
}

.audio-wave-anim span {
  width: 2px;
  background: currentColor;
  border-radius: 2px;
  animation: waveBar 0.8s ease-in-out infinite alternate;
}

.audio-wave-anim span:nth-child(2) { animation-delay: 0.2s; }
.audio-wave-anim span:nth-child(3) { animation-delay: 0.4s; }

@keyframes waveBar {
  0% { height: 3px; }
  100% { height: 12px; }
}

.dc-center {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.dc-vs {
  font-size: 16px;
  font-weight: 900;
  color: #fbbf24;
}

.btn-ab-switch {
  font-size: 10px;
  padding: 4px 8px;
}

.dc-meter {
  display: flex;
  height: 14px;
  border-radius: 999px;
  overflow: hidden;
  font-size: 9.5px;
  font-weight: 800;
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.dc-bar-left {
  background: #3b82f6;
  display: flex;
  align-items: center;
  padding-left: 8px;
  transition: width 0.4s ease;
}

.dc-bar-right {
  background: #a855f7;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 8px;
  transition: width 0.4s ease;
}

.dc-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.btn-vote-l {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.4);
}

.btn-vote-r {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.4);
}

.btn-vote-l.voted,
.btn-vote-r.voted {
  background: #10b981;
  color: #fff;
  border-color: #10b981;
}

.dc-winner-banner {
  text-align: center;
  padding: 8px;
  border-radius: 10px;
  background: rgba(251, 191, 36, 0.1);
  color: #fbbf24;
  font-size: 13px;
}

.dc-admin-row {
  display: flex;
  gap: 6px;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
  padding-top: 10px;
  flex-wrap: wrap;
}

.empty-state-box {
  padding: 48px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.empty-icon {
  font-size: 48px;
}

/* TAB 2: BRACKET */
.bracket-visual-board {
  padding: 32px 24px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  overflow-x: auto;
}

.bracket-rounds-container {
  display: grid;
  grid-template-columns: repeat(3, minmax(260px, 1fr));
  gap: 36px;
}

.b-col-title {
  font-size: 13px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.05em;
  margin: 0 0 20px;
  text-align: center;
}

.b-col-title.final-title {
  color: #fbbf24;
}

.bracket-matches-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.semi-list {
  margin-top: 36px;
  gap: 72px;
}

.final-list {
  margin-top: 90px;
  gap: 24px;
}

.bracket-match-node {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
}

.bracket-match-node:hover {
  border-color: #38bdf8;
  transform: translateY(-2px);
}

.b-slot {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  font-size: 13px;
  color: var(--muted);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.b-slot:last-child {
  border-bottom: none;
}

.b-slot.winner {
  background: rgba(52, 211, 153, 0.12);
  color: #fff;
  font-weight: 700;
}

.b-slot.winner .b-score {
  color: #34d399;
  font-weight: 900;
}

.champion-crown-podium {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(15, 23, 42, 0.8));
  border: 1px solid rgba(245, 158, 11, 0.4);
  border-radius: 16px;
  padding: 18px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.trophy-symbol {
  font-size: 32px;
}

.champ-sub {
  font-size: 11px;
  color: #fbbf24;
}

/* TAB 3: PARTICIPANTS */
.two-column-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.panel-box {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.pb-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 18px;
}

.pb-header h3 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 2px;
}

.pb-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.submissions-list,
.applications-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.sub-item-card,
.app-item-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px 14px;
  gap: 12px;
}

.sub-info {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.sub-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.sub-artist {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
}

.sub-media-link {
  font-size: 11px;
  color: #38bdf8;
  text-decoration: underline;
}

.sub-actions,
.app-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.btn-accept {
  background: rgba(52, 211, 153, 0.2);
  color: #34d399;
  border: 1px solid rgba(52, 211, 153, 0.4);
}

.btn-reject {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

/* TAB 4: RULES */
.rules-grid-layout {
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
}

.rules-card,
.prize-pool-card {
  padding: 28px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.rules-bullet-list {
  padding-left: 18px;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  margin: 16px 0 0;
  font-size: 14px;
  line-height: 1.5;
}

.prize-tiers-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 16px;
}

.pt-item {
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border-left: 4px solid var(--muted);
}

.pt-item.gold {
  border-left-color: #fbbf24;
  background: rgba(245, 158, 11, 0.08);
}

.pt-item.silver {
  border-left-color: #cbd5e1;
}

.pt-item.bronze {
  border-left-color: #d97706;
}

.pt-rank {
  display: block;
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  color: var(--muted);
  margin-bottom: 2px;
}

.pt-val {
  font-size: 13.5px;
  color: #fff;
}

/* MODALS */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.82);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  width: 100%;
  max-width: 500px;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 22px;
  padding: 26px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.modal-header h3 {
  margin: 0;
  color: #fff;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.grid-2-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.checkbox-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #cbd5e1;
  cursor: pointer;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

/* Match Inspect Modal */
.match-inspect-modal {
  max-width: 600px;
}

.showdown-versus-row {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 20px;
  margin: 20px 0;
}

.versus-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.04);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.versus-card.winner {
  border-color: #fbbf24;
  background: rgba(251, 191, 36, 0.08);
}

.vc-avatar {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 800;
}

.vc-avatar.alt {
  background: #a855f7;
}

.vc-score {
  font-size: 14px;
  color: #fbbf24;
  font-weight: 800;
}

.versus-divider {
  font-size: 20px;
  font-weight: 900;
  color: #f59e0b;
}

.text-center {
  text-align: center;
}

@media (max-width: 900px) {
  .hero-detail-grid {
    grid-template-columns: 1fr;
  }
  .two-column-layout,
  .rules-grid-layout {
    grid-template-columns: 1fr;
  }
  .battles-deck-grid {
    grid-template-columns: 1fr;
  }
}
</style>
