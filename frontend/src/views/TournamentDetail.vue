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
    <!-- ================================================================= -->
    <!-- COMPACT, HIGH-END TOURNAMENT HEADER -->
    <!-- ================================================================= -->
    <header class="detail-header card compact-tourney-header">
      <!-- Top Navigation & Badges Line -->
      <div class="header-top-row">
        <button class="btn ghost btn-sm btn-back-arena" @click="goBack">
          ← Zurück zur Contest-Arena
        </button>
        <div class="top-status-pills">
          <span class="badge-status-pill" :class="`status-${(tournament?.status || 'draft').toLowerCase()}`">
            {{ statusLabel(tournament?.status) }}
          </span>
          <span class="badge-format-tag">
            {{ formatLabel(tournament?.format) }}
          </span>
          <span v-if="tournament?.is_no_loss" class="badge-no-loss">
            🛡️ No Loss
          </span>
          <span class="badge-genre-tag">{{ tournament?.genre || 'Allround' }}</span>
        </div>
      </div>

      <!-- Admin Micro-Toolbar (Only for Team/Admin, ultra-clean and discreet) -->
      <div v-if="isTeam" class="admin-compact-toolbar">
        <div class="act-phase-picker">
          <span class="act-label">👑 Admin Phase:</span>
          <select
            :value="tournament?.status"
            @change="updateTournamentStatus($event.target.value)"
            class="input input-sm act-select"
          >
            <option v-for="st in statusSteps" :key="st.value" :value="st.value">
              {{ st.label }}
            </option>
          </select>
        </div>
        <div class="act-actions">
          <button class="btn btn-micro btn-accent" @click="generateBattles" title="Paarungen aus Einreichungen generieren">
            ⚔️ Battles generieren
          </button>
          <button class="btn ghost btn-micro" @click="bulkApproveApplications" title="Alle offenen Bewerber sofort freischalten">
            ✓ Alle annehmen
          </button>
          <button class="btn ghost btn-micro btn-warn" @click="resetTournamentData" title="Battles leeren & zurücksetzen">
            ⚡ Reset
          </button>
          <button class="btn ghost btn-micro btn-danger-link" @click="confirmDeleteTournament" title="Turnier löschen">
            🗑️ Löschen
          </button>
        </div>
      </div>

      <!-- Main Title & Primary Action Strip -->
      <div class="header-center-strip">
        <div class="hcs-title-col">
          <div class="title-line">
            <h1 class="tournament-title">{{ displayTitle(tournament?.title) }}</h1>
            <button v-if="isTeam" class="btn ghost btn-micro btn-edit-meta" @click="openEditModal" title="Turnierdaten anpassen">
              ✏️ Bearbeiten
            </button>
          </div>
          <p class="tournament-desc">{{ displayDescription(tournament?.description) }}</p>
        </div>

        <!-- Single Contextual Action Button (Only what is needed right now!) -->
        <div class="hcs-action-col">
          <!-- Phase: APPLICATION_OPEN -->
          <template v-if="tournament?.status === 'APPLICATION_OPEN'">
            <div v-if="myApplication" class="user-inline-status" :class="`status-${myApplication.status?.toLowerCase()}`">
              <span class="badge-status-pill" :class="myApplication.status?.toLowerCase()">
                {{ myApplication.status === 'APPROVED' ? '✓ Zugelassen' : (myApplication.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
              </span>
              <button class="btn ghost btn-sm" @click="openApplyModal">
                ✏️ Bewerbung bearbeiten
              </button>
            </div>
            <button v-else class="btn btn-primary btn-cta-pulse" @click="openApplyModal">
              ✍️ Als Artist bewerben
            </button>
          </template>

          <!-- Phase: SUBMISSION_OPEN -->
          <template v-else-if="tournament?.status === 'SUBMISSION_OPEN'">
            <div v-if="myCurrentSubmission" class="user-inline-status" :class="`status-${myCurrentSubmission.status?.toLowerCase()}`">
              <button
                class="btn ghost btn-micro btn-play-mini"
                @click="toggleAudio(`sub-${myCurrentSubmission.id}`, myCurrentSubmission.profile_name)"
              >
                {{ currentPlayingTrack === `sub-${myCurrentSubmission.id}` ? '⏸' : '▶' }} {{ myCurrentSubmission.title || 'Mein Track' }}
              </button>
              <button class="btn ghost btn-sm" @click="openUploadRoundModal(myCurrentSubmission.round_number || 1)">
                ✏️ Track bearbeiten
              </button>
            </div>
            <button v-else class="btn btn-primary btn-cta-pulse" @click="openUploadRoundModal(1)">
              📤 Runde 1 einreichen (Audio/Video)
            </button>
          </template>

          <!-- Phase: BATTLES -->
          <template v-else-if="tournament?.status === 'BATTLES'">
            <button class="btn btn-accent" @click="activeTab = 'battles'">
              ⚔️ Zu den Live Battles ({{ battleRows.length }})
            </button>
          </template>

          <!-- Phase: CLOSED -->
          <template v-else>
            <button class="btn ghost" @click="activeTab = 'bracket'">
              🏆 Turnierbaum &amp; Champion
            </button>
          </template>
        </div>
      </div>

      <!-- Prominent Rejection Banner if rejected -->
      <div v-if="tournament?.status === 'APPLICATION_OPEN' && myApplication?.status === 'REJECTED'" class="hero-rejection-banner">
        <strong>❌ Jury-Begründung für Ablehnung:</strong>
        <p>"{{ myApplication.rejection_reason || 'Die Bewerbung hat die Kriterien der aktuellen Runde leider nicht erfüllt.' }}"</p>
        <button class="btn ghost btn-micro" @click="openApplyModal">✏️ Bewerbung überarbeiten &amp; neu einreichen</button>
      </div>
      <div v-if="tournament?.status === 'SUBMISSION_OPEN' && myCurrentSubmission?.status === 'REJECTED'" class="hero-rejection-banner">
        <strong>❌ Jury-Begründung für Track-Ablehnung:</strong>
        <p>"{{ myCurrentSubmission.rejection_reason || 'Kriterien nicht erfüllt.' }}"</p>
        <button class="btn ghost btn-micro" @click="openUploadRoundModal(myCurrentSubmission.round_number || 1)">✏️ Track überarbeiten &amp; neu hochladen</button>
      </div>

      <!-- Horizontal Compact Metadata Ribbon -->
      <div class="metadata-chips-strip">
        <div class="meta-chip">
          <span class="mc-icon">💰</span>
          <span class="mc-val">{{ displayPrizePool(tournament) }}</span>
        </div>
        <div class="meta-chip">
          <span class="mc-icon">👥</span>
          <span class="mc-val">{{ participantsCount }} / {{ tournament?.slots || 16 }} {{ participantsCount === 1 ? 'Artist' : 'Artists' }}</span>
        </div>
        <div class="meta-chip">
          <span class="mc-icon">🎯</span>
          <span class="mc-val">{{ tournament?.total_rounds || 4 }} {{ (tournament?.total_rounds || 4) === 1 ? 'Runde' : 'Runden' }}</span>
        </div>
        <div class="meta-chip" v-if="battlesCount > 0 || tournament?.status === 'BATTLES'">
          <span class="mc-icon">⚔️</span>
          <span class="mc-val">{{ battlesCount }} {{ battlesCount === 1 ? 'Duell' : 'Duelle' }}</span>
        </div>
      </div>
    </header>

    <!-- DETAIL NAVIGATION TABS (PROGRESSIVE DISCLOSURE) -->
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
    <!-- TAB: OVERVIEW & APPLICATION (PROGRESSIVE DISCLOSURE) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'overview'" class="detail-tab-section">
      <div class="overview-grid-layout">
        <!-- Main Column -->
        <div class="overview-main-col">
          <!-- Format & Rules Banner -->
          <div class="card format-highlight-card">
            <div class="fhc-header">
              <span class="fhc-icon">🏆</span>
              <div>
                <h3>Turnierformat: {{ formatLabel(tournament?.format) }}</h3>
                <p class="muted small">{{ formatDescription(tournament?.format) }}</p>
              </div>
            </div>

            <!-- Group Stage Specifics if format is GROUP_STAGE -->
            <div v-if="tournament?.format === 'GROUP_STAGE'" class="group-stage-spec-box">
              <div class="gs-spec-item">
                <span class="gs-label">Gruppen-Aufteilung:</span>
                <strong class="gs-value">{{ tournament?.groups_count || 4 }} Gruppen à {{ tournament?.group_size || 4 }} Artists</strong>
              </div>
              <div class="gs-spec-item">
                <span class="gs-label">K.O.-Qualifikation:</span>
                <strong class="gs-value">Top 2 jeder Gruppe rücken in die K.O.-Finals vor</strong>
              </div>
              <div class="gs-spec-item">
                <span class="gs-label">Geplante Runden:</span>
                <strong class="gs-value">{{ tournament?.total_rounds || 4 }} Runden bis zum Champion</strong>
              </div>
            </div>

            <div v-else class="general-format-pills">
              <span class="pill-meta">🎯 {{ tournament?.slots || 16 }} Teilnehmer-Slots</span>
              <span class="pill-meta">⚔️ {{ tournament?.total_rounds || 4 }} Runden-Stadien</span>
              <span class="pill-meta">🛡️ {{ tournament?.is_no_loss ? 'Double Elimination (No-Loss)' : 'Single Elimination K.O.' }}</span>
            </div>
          </div>

          <!-- Artist Personal Application Card -->
          <div class="card my-application-status-card" v-if="myApplication">
            <div class="masc-header">
              <span class="masc-icon">👤</span>
              <div>
                <h4>Dein Bewerbungsstatus für dieses Turnier</h4>
                <span class="muted small">Eingereicht unter: <strong>{{ myApplication.profile_name }}</strong></span>
              </div>
              <span class="badge-status-pill" :class="myApplication.status?.toLowerCase()">
                {{ myApplication.status === 'APPROVED' ? '✓ Zugelassen' : (myApplication.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
              </span>
            </div>

            <!-- Rejection reason if rejected -->
            <div v-if="myApplication.status === 'REJECTED'" class="rejection-reason-box">
              <div class="rrb-title">❌ Ablehnungsgrund der Jury:</div>
              <p class="rrb-text">"{{ myApplication.rejection_reason || 'Die Bewerbung hat die Kriterien der aktuellen Runde leider nicht erfüllt.' }}"</p>
              <small class="muted">Du kannst deine Bewerbung jederzeit bearbeiten, einen neuen Demo-Link hinterlegen und erneut einreichen.</small>
            </div>

            <div v-else-if="myApplication.status === 'APPROVED'" class="approved-box">
              🎉 <strong>Du bist dabei!</strong> Deine Bewerbung wurde angenommen. Halte dich für die Einreichungsphase bereit.
            </div>

            <div v-else class="pending-box">
              ⏳ <strong>In Begutachtung.</strong> Die UNYQ Jury prüft aktuell deine Hörprobe. Du kannst deine Angaben weiterhin anpassen.
            </div>

            <div class="masc-body">
              <p class="masc-message"><strong>Nachricht / Link:</strong> "{{ myApplication.message }}"</p>
            </div>

            <div class="masc-actions">
              <button class="btn ghost btn-sm" @click="openApplyModal">
                ✏️ Bewerbung bearbeiten / überarbeiten
              </button>
            </div>
          </div>

          <!-- If Not Applied Yet -->
          <div class="card apply-cta-card" v-else>
            <div class="acc-body">
              <span class="acc-icon">✍️</span>
              <div>
                <h3>Jetzt als Contender bewerben</h3>
                <p class="muted">
                  Bewerbungsschluss beachten. Reiche deine stärkste Demo oder ein Soundcloud-Profil ein.
                </p>
              </div>
            </div>
            <button class="btn btn-action-hero" @click="openApplyModal">
              ✍️ Jetzt bewerben
            </button>
          </div>
        </div>

        <!-- Sidebar Column: Roster Preview -->
        <div class="overview-side-col">
          <div class="card panel-box">
            <div class="pb-header">
              <div>
                <h3>Bewerber-Roster ({{ isTeam ? applicationRows.length : totalApplicationsCount }})</h3>
                <p class="muted small">{{ isTeam ? 'Teilnehmer im Auswahlprozess' : 'Aktueller Anmeldestand' }}</p>
              </div>
              <button class="btn ghost btn-micro" @click="activeTab = 'participants'">{{ isTeam ? 'Alle ansehen →' : 'Status ansehen →' }}</button>
            </div>

            <!-- Team View: Names and Avatars -->
            <template v-if="isTeam">
              <div class="roster-preview-list" v-if="applicationRows.length">
                <div v-for="app in applicationRows.slice(0, 6)" :key="app.id" class="roster-preview-item">
                  <div class="rp-avatar">{{ app.profile_name?.charAt(0) || 'A' }}</div>
                  <div class="rp-info">
                    <strong>{{ app.profile_name }}</strong>
                    <span class="badge-status-pill tiny" :class="app.status?.toLowerCase()">{{ app.status }}</span>
                  </div>
                </div>
              </div>
              <div v-else class="empty-muted-box muted">Noch keine Bewerbungen eingegangen.</div>
            </template>

            <!-- Artist View: Anonymized counts & Privacy protection -->
            <template v-else>
              <div class="roster-privacy-overview">
                <div class="rpo-stat-row">
                  <div class="rpo-stat-item">
                    <span class="rpo-val">{{ approvedCount }} / {{ tournament?.slots || 16 }}</span>
                    <span class="rpo-lbl">Plätze belegt</span>
                  </div>
                  <div class="rpo-stat-item">
                    <span class="rpo-val">{{ totalApplicationsCount }}</span>
                    <span class="rpo-lbl">Bewerber gesamt</span>
                  </div>
                </div>

                <!-- My Own Application if applied -->
                <div v-if="myApplication" class="rpo-my-app-box">
                  <span class="rpo-my-app-title">Dein Bewerbungs-Status:</span>
                  <div class="app-head-line">
                    <strong>{{ myApplication.profile_name || 'Du' }}</strong>
                    <span class="badge-status-pill tiny" :class="myApplication.status?.toLowerCase()">
                      {{ myApplication.status === 'APPROVED' ? '✓ Zugelassen' : (myApplication.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
                    </span>
                  </div>
                </div>

                <p class="rpo-privacy-note">
                  🔒 Zum Schutz der Chancengleichheit bleiben die Namen der Mitbewerber bis zum Turnierstart geheim.
                </p>
              </div>
            </template>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB: SUBMISSIONS & RUNDEN (1 SONG PER ROUND ENFORCED) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'submissions'" class="detail-tab-section">
      <!-- Round Filter Bar -->
      <div class="round-picker-nav card">
        <div class="rpn-left">
          <span class="rpn-lbl">Runde auswählen:</span>
          <div class="round-pills-row">
            <button
              v-for="r in (tournament?.total_rounds || 4)"
              :key="r"
              class="round-pill-btn"
              :class="{ active: selectedRoundFilter === r }"
              @click="selectedRoundFilter = r"
            >
              Runde {{ r }}
              <span class="count-chip">{{ getSubmissionsCountForRound(r) }}</span>
            </button>
          </div>
        </div>
        <div class="rpn-actions">
          <button class="btn btn-sm" @click="openUploadRoundModal(selectedRoundFilter)">
            + Runde {{ selectedRoundFilter }} einreichen / bearbeiten
          </button>
        </div>
      </div>

      <!-- User's Own Round Submission (One Song per Round & Editable) -->
      <div class="card my-round-submission-card" v-if="mySubmissionForSelectedRound">
        <div class="mrsc-header">
          <div class="mrsc-title-block">
            <span class="mrsc-icon">🎵</span>
            <div>
              <h3>Deine Einreichung für Runde {{ selectedRoundFilter }}</h3>
              <span class="muted small">1 Song pro Runde erlaubt • Jederzeit während der Phase bearbeitbar</span>
            </div>
          </div>
          <span class="badge-status-pill" :class="mySubmissionForSelectedRound.status?.toLowerCase()">
            {{ mySubmissionForSelectedRound.status === 'APPROVED' ? '✓ Freigegeben' : (mySubmissionForSelectedRound.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
          </span>
        </div>

        <!-- Rejection Reason Banner if rejected -->
        <div v-if="mySubmissionForSelectedRound.status === 'REJECTED'" class="rejection-reason-box">
          <div class="rrb-title">❌ Von der Jury abgelehnt:</div>
          <p class="rrb-text">"{{ mySubmissionForSelectedRound.rejection_reason || 'Track entspricht nicht den Vorgaben dieser Runde.' }}"</p>
          <small class="muted">Du kannst deinen Track austauschen oder anpassen und die Runde erneut zur Prüfung freigeben.</small>
        </div>

        <div class="mrsc-track-details">
          <div class="track-main-line">
            <strong class="track-title-text">{{ mySubmissionForSelectedRound.title }}</strong>
            <a v-if="mySubmissionForSelectedRound.media_url" :href="mySubmissionForSelectedRound.media_url" target="_blank" rel="noopener noreferrer" class="link-external">
              🔗 {{ mySubmissionForSelectedRound.media_url }}
            </a>
          </div>
          <p class="track-notes muted small" v-if="mySubmissionForSelectedRound.notes">
            {{ mySubmissionForSelectedRound.notes }}
          </p>
        </div>

        <div class="mrsc-actions-row">
          <button
            class="btn btn-sm btn-play-audio"
            :class="{ active: currentPlayingTrack === `sub-${mySubmissionForSelectedRound.id}` }"
            @click="toggleAudio(`sub-${mySubmissionForSelectedRound.id}`, mySubmissionForSelectedRound.profile_name)"
          >
            {{ currentPlayingTrack === `sub-${mySubmissionForSelectedRound.id}` ? '⏸ Pause' : '▶ Track anhören' }}
          </button>
          <button class="btn ghost btn-sm" @click="openUploadRoundModal(selectedRoundFilter)">
            ✏️ Runde {{ selectedRoundFilter }} bearbeiten / neu einreichen
          </button>
        </div>
      </div>

      <div class="card empty-round-user-cta" v-else>
        <div class="eruc-content">
          <span class="eruc-icon">📤</span>
          <div>
            <h4>Du hast für Runde {{ selectedRoundFilter }} noch keinen Song eingereicht</h4>
            <p class="muted small">Lade deinen Beat oder Track für Runde {{ selectedRoundFilter }} hoch, um dich für das Duell zu qualifizieren.</p>
          </div>
        </div>
        <button class="btn btn-sm" @click="openUploadRoundModal(selectedRoundFilter)">
          📤 Track für Runde {{ selectedRoundFilter }} einreichen
        </button>
      </div>

      <!-- All Submissions for Selected Round -->
      <div class="card panel-box mt-4">
        <div class="pb-header">
          <div>
            <h3>Alle Einreichungen für Runde {{ selectedRoundFilter }} ({{ filteredSubmissionsForRound.length }})</h3>
            <p class="muted small">Höre die Tracks aller qualifizierten Artists an.</p>
          </div>
          <div class="pb-actions" v-if="isTeam">
            <button class="btn ghost btn-micro" @click="bulkApproveSubmissions">
              ✓ Alle Runden freigeben
            </button>
          </div>
        </div>

        <div class="submissions-list" v-if="filteredSubmissionsForRound.length">
          <div v-for="sub in filteredSubmissionsForRound" :key="sub.id" class="sub-item-card">
            <div class="sub-info">
              <span class="sub-icon">🎵</span>
              <div>
                <strong>{{ sub.title }}</strong>
                <span class="sub-artist">von {{ sub.profile_name }} • Runde {{ sub.round_number || 1 }}</span>
                <a v-if="sub.media_url" :href="sub.media_url" target="_blank" rel="noopener noreferrer" class="sub-media-link">
                  🔗 Externer Link
                </a>
                <div v-if="sub.rejection_reason" class="item-rejection-tag">
                  ❌ Begründung: "{{ sub.rejection_reason }}"
                </div>
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
              <template v-if="isTeam">
                <button v-if="sub.status !== 'APPROVED'" class="btn btn-micro btn-accept" @click="decideSubmission(sub, 'APPROVED')" title="Freigeben">✓</button>
                <button class="btn ghost btn-micro btn-reject" @click="promptRejectSubmission(sub)" title="Mit Begründung ablehnen">✕</button>
                <button class="btn ghost btn-micro btn-danger" @click="deleteSubmission(sub)" title="Einreichung löschen">🗑️</button>
              </template>
            </div>
          </div>
        </div>
        <div v-else class="empty-muted-box muted">Noch keine Einreichungen für Runde {{ selectedRoundFilter }} vorhanden.</div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB: BATTLES & VOTING SHOWDOWN -->
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
    <!-- TAB: INTERAKTIVER TURNIERBAUM (BRACKET TREE) -->
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
    <!-- TAB: BEWERBER & ROSTER (TRANSPARENT STATUS & REJECTION REASONS) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'participants'" class="detail-tab-section">
      <div class="card panel-box">
        <div class="pb-header">
          <div>
            <h3>Bewerbungen &amp; Roster ({{ isTeam ? applicationRows.length : totalApplicationsCount }})</h3>
            <p class="muted small">{{ isTeam ? 'Alle registrierten Artists für dieses Turnier inklusive Jury-Status und Begründungen' : 'Aktueller Roster-Status und deine persönliche Bewerbung' }}</p>
          </div>
          <div class="pb-actions">
            <button v-if="isTeam && applicationRows.some(a => a.status === 'PENDING')" class="btn ghost btn-micro" @click="bulkApproveApplications">
              ✓ Alle annehmen
            </button>
            <button class="btn btn-sm" @click="openApplyModal">+ Bewerben</button>
          </div>
        </div>

        <!-- Team View: Full management list -->
        <template v-if="isTeam">
          <div class="applications-list" v-if="applicationRows.length">
            <div v-for="app in applicationRows" :key="app.id" class="app-item-card">
              <div class="app-info">
                <div class="app-head-line">
                  <strong>{{ app.profile_name }}</strong>
                  <span class="badge-status-pill" :class="app.status?.toLowerCase()">
                    {{ app.status === 'APPROVED' ? 'Zugelassen' : (app.status === 'REJECTED' ? 'Abgelehnt' : 'In Prüfung') }}
                  </span>
                </div>
                <p class="muted small">{{ app.message || 'Bewerbung eingereicht.' }}</p>

                <!-- Rejection Reason if rejected -->
                <div v-if="app.rejection_reason" class="item-rejection-tag">
                  ❌ Begründung der Jury: "{{ app.rejection_reason }}"
                </div>
              </div>

              <div class="app-actions">
                <button v-if="app.status !== 'APPROVED'" class="btn btn-micro btn-accept" @click="decideApplication(app, 'APPROVED')" title="Zulassen">✓</button>
                <button class="btn ghost btn-micro btn-reject" @click="promptRejectApplication(app)" title="Mit Begründung ablehnen">✕</button>
                <button class="btn ghost btn-micro btn-danger" @click="deleteApplication(app)" title="Bewerbung löschen">🗑️</button>
                <button
                  v-if="myApplication?.id === app.id"
                  class="btn ghost btn-micro"
                  @click="openApplyModal"
                >
                  ✏️ Bearbeiten
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted">Noch keine Bewerbungen vorhanden.</div>
        </template>

        <!-- Artist View: Privacy Protection -->
        <template v-else>
          <div class="artist-roster-privacy-card">
            <div class="arpc-stats-grid">
              <div class="arpc-stat-box">
                <span class="arpc-stat-icon">👥</span>
                <div class="arpc-stat-info">
                  <strong>{{ totalApplicationsCount }}</strong>
                  <span>Bewerber eingegangen</span>
                </div>
              </div>
              <div class="arpc-stat-box success">
                <span class="arpc-stat-icon">✅</span>
                <div class="arpc-stat-info">
                  <strong>{{ approvedCount }} / {{ tournament?.slots || 16 }}</strong>
                  <span>Plätze fest vergeben</span>
                </div>
              </div>
              <div class="arpc-stat-box warn">
                <span class="arpc-stat-icon">⏳</span>
                <div class="arpc-stat-info">
                  <strong>{{ Math.max(0, totalApplicationsCount - approvedCount) }}</strong>
                  <span>In Jury-Prüfung</span>
                </div>
              </div>
            </div>

            <!-- My Application Card -->
            <div v-if="myApplication" class="my-application-detail-card card">
              <div class="madc-header">
                <div>
                  <h4>Deine Bewerbung</h4>
                  <p class="muted small">Eingereicht für dieses Turnier</p>
                </div>
                <span class="badge-status-pill" :class="myApplication.status?.toLowerCase()">
                  {{ myApplication.status === 'APPROVED' ? '✓ Zugelassen' : (myApplication.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
                </span>
              </div>
              <p class="madc-message">{{ myApplication.message || 'Keine Nachricht angegeben.' }}</p>
              <div v-if="myApplication.rejection_reason" class="item-rejection-tag">
                ❌ Begründung der Jury: "{{ myApplication.rejection_reason }}"
              </div>
              <div class="madc-footer">
                <button class="btn ghost btn-sm" @click="openApplyModal">✏️ Bewerbung bearbeiten</button>
              </div>
            </div>

            <div v-else class="empty-not-applied-banner">
              <p>Du hast dich noch nicht für dieses Turnier beworben.</p>
              <button class="btn btn-sm btn-primary" @click="openApplyModal">Jetzt bewerben</button>
            </div>

            <div class="roster-fairplay-notice">
              <span class="rfn-icon">🛡️</span>
              <p>
                <strong>Fair-Play &amp; Artist-Privatsphäre:</strong>
                Die Identitäten und Song-Einreichungen anderer Teilnehmer werden bis zum offiziellen Battle-Start geheim gehalten, um taktische Absprachen zu verhindern und faire Bewertung sicherzustellen.
              </p>
            </div>
          </div>
        </template>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB: REGELN & PREISPOOL -->
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
              <strong>1 Song pro Runde:</strong>
              Jeder Künstler darf pro Runde maximal einen Track einreichen. Während der offenen Phase kann dieser jederzeit aktualisiert oder überarbeitet werden.
            </li>
            <li>
              <strong>Format &amp; Struktur:</strong>
              Modus: {{ formatLabel(tournament?.format) }}. Geplante Runden: {{ tournament?.total_rounds || 4 }}. Teilnehmer-Slots: {{ tournament?.slots || 16 }}.
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
              <strong class="pt-val">{{ tournament?.prize_pool_1 || tournament?.meta_settings?.prize_pool_1 || tournament?.prize_pool || "1.000 € Cash + Champion Trophy" }}</strong>
            </div>
            <div class="pt-item silver">
              <span class="pt-rank">2. Platz (Runner-Up)</span>
              <strong class="pt-val">{{ tournament?.prize_pool_2 || tournament?.meta_settings?.prize_pool_2 || "500 € Cash + UNYQ Sample Pack Bundle" }}</strong>
            </div>
            <div class="pt-item bronze">
              <span class="pt-rank">3. Platz</span>
              <strong class="pt-val">{{ tournament?.prize_pool_3 || tournament?.meta_settings?.prize_pool_3 || "250 € Cash + VIP Producer Pass" }}</strong>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- MODAL 1: APPLY MODAL (WITH EDITING & STATUS AWARENESS) -->
    <!-- ================================================================= -->
    <div v-if="showApplyModal" class="modal-overlay" @click.self="showApplyModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>{{ myApplication ? 'Bewerbung bearbeiten' : `Bewerbung für "${tournament?.title}"` }}</h3>
          <button class="btn ghost tiny" @click="showApplyModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitApply">
          <div v-if="myApplication?.rejection_reason" class="rejection-reason-box mb-2">
            <strong>Vorherige Jury-Rückmeldung:</strong>
            <p>"{{ myApplication.rejection_reason }}"</p>
          </div>

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
            <textarea v-model.trim="applyMessage" class="input" rows="3" placeholder="Deine Motivation, Genre, Vorstellung..."></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showApplyModal = false">Abbrechen</button>
            <button class="btn" type="submit">{{ myApplication ? 'Bewerbung aktualisieren 💾' : 'Bewerbung abschicken 🎤' }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 2: UPLOAD / EDIT ROUND MODAL (ONE SONG PER ROUND) -->
    <!-- ================================================================= -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>{{ editingSubmissionId ? `Runde ${uploadRoundNumber} bearbeiten` : `Runde ${uploadRoundNumber} einreichen` }}</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitRound">
          <label>
            <span>Runden-Nummer</span>
            <input v-model.number="uploadRoundNumber" type="number" min="1" :max="tournament?.total_rounds || 8" class="input" />
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
            <button class="btn" type="submit">{{ editingSubmissionId ? 'Änderungen speichern & neu einreichen 🚀' : 'Runde jetzt einreichen 🚀' }}</button>
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
    <!-- MODAL 4: EDIT TOURNAMENT MODAL (WITH FORMAT, SLOTS, GROUPS) -->
    <!-- ================================================================= -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Turnierdaten &amp; Format anpassen</h3>
          <button class="btn ghost tiny" @click="showEditModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitEditTournament">
          <label>
            <span>Titel *</span>
            <input v-model.trim="editForm.title" class="input" required />
          </label>

          <div class="split-form-row">
            <label>
              <span>Turnier-Format *</span>
              <select v-model="editForm.format" class="input">
                <option value="SINGLE_ELIMINATION">K.O.-System (Single Elimination)</option>
                <option value="GROUP_STAGE">Gruppenphase + K.O.-Finals ⭐</option>
                <option value="DOUBLE_ELIMINATION">No-Loss Bracket (Double Elimination)</option>
                <option value="ROUND_ROBIN">Liga (Jeder gegen Jeden)</option>
              </select>
            </label>
            <label>
              <span>Teilnehmer-Slots</span>
              <select v-model.number="editForm.slots" class="input">
                <option :value="4">4 Artists</option>
                <option :value="8">8 Artists</option>
                <option :value="16">16 Artists</option>
                <option :value="24">24 Artists</option>
                <option :value="32">32 Artists</option>
                <option :value="64">64 Artists</option>
              </select>
            </label>
          </div>

          <!-- Group Stage Configuration if GROUP_STAGE is selected -->
          <div v-if="editForm.format === 'GROUP_STAGE'" class="group-stage-config-box">
            <span class="gsc-title">⚙️ Gruppenphase Konfiguration:</span>
            <div class="split-form-row">
              <label>
                <span>Anzahl Gruppen</span>
                <select v-model.number="editForm.groups_count" class="input">
                  <option :value="2">2 Gruppen</option>
                  <option :value="4">4 Gruppen (Standard)</option>
                  <option :value="8">8 Gruppen</option>
                </select>
              </label>
              <label>
                <span>Artists pro Gruppe</span>
                <select v-model.number="editForm.group_size" class="input">
                  <option :value="3">3 Artists</option>
                  <option :value="4">4 Artists (Standard)</option>
                  <option :value="6">6 Artists</option>
                </select>
              </label>
            </div>
          </div>

          <div class="prize-pool-designer-box">
            <span class="ppd-title">💰 Preispool Staffelung (1. / 2. / 3. Platz):</span>
            <div class="split-form-row">
              <label>
                <span>1. Platz (Champion) *</span>
                <input v-model.trim="editForm.prize_pool_1" class="input" required placeholder="1.000 € Cash" />
                <div class="preset-pill-row">
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_1 = '100 € Cash'">100 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_1 = '250 € Cash'">250 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_1 = '500 € Cash'">500 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_1 = '1.000 € Cash'">1.000 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_1 = '2.000 € Cash'">2.000 €</button>
                </div>
              </label>
              <label>
                <span>2. Platz (Runner-Up)</span>
                <input v-model.trim="editForm.prize_pool_2" class="input" placeholder="500 € Cash" />
                <div class="preset-pill-row">
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_2 = '50 € Cash'">50 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_2 = '100 € Cash'">100 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_2 = '250 € Cash'">250 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_2 = '500 € Cash'">500 €</button>
                </div>
              </label>
              <label>
                <span>3. Platz</span>
                <input v-model.trim="editForm.prize_pool_3" class="input" placeholder="250 € Cash" />
                <div class="preset-pill-row">
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_3 = '25 € Cash'">25 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_3 = '50 € Cash'">50 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_3 = '100 € Cash'">100 €</button>
                  <button type="button" class="preset-btn" @click="editForm.prize_pool_3 = '250 € Cash'">250 €</button>
                </div>
              </label>
            </div>
          </div>

          <div class="split-form-row">
            <label>
              <span>Genre / Sparte</span>
              <input v-model.trim="editForm.genre" class="input" />
            </label>
          </div>

          <label>
            <span>Geplante Runden-Anzahl</span>
            <select v-model.number="editForm.total_rounds" class="input">
              <option :value="1">1 Runde (Direktes Finale)</option>
              <option :value="2">2 Runden (Halbfinale &amp; Finale)</option>
              <option :value="3">3 Runden (Viertelfinale bis Finale)</option>
              <option :value="4">4 Runden (Achtelfinale bis Finale)</option>
              <option :value="5">5 Runden (Grand Tournament)</option>
            </select>
          </label>

          <label>
            <span>Beschreibung &amp; Vorgaben</span>
            <textarea v-model.trim="editForm.description" class="input" rows="3"></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showEditModal = false">Abbrechen</button>
            <button class="btn" type="submit">Änderungen speichern 💾</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 5: REJECT MODAL WITH REASON PROMPT (ADMIN) -->
    <!-- ================================================================= -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Ablehnung mit Begründung</h3>
          <button class="btn ghost tiny" @click="showRejectModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="muted small">
            Gib dem Künstler <strong>{{ rejectingTarget?.profile_name || 'Artist' }}</strong> eine Begründung für die Ablehnung. Diese ist für den Künstler transparent einsehbar.
          </p>

          <div class="reject-presets-wrap">
            <span class="preset-label">Schnellauswahl:</span>
            <div class="reject-presets-pills">
              <button
                v-for="p in rejectPresets"
                :key="p"
                type="button"
                class="btn ghost btn-micro"
                @click="rejectReasonInput = p"
              >
                {{ p }}
              </button>
            </div>
          </div>

          <label class="mt-3">
            <span>Begründung / Feedback *</span>
            <textarea
              v-model.trim="rejectReasonInput"
              class="input"
              rows="3"
              placeholder="z. B. Mixdown übersteuert, Track entspricht nicht dem geforderten Genre..."
              required
            ></textarea>
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn ghost" type="button" @click="showRejectModal = false">Abbrechen</button>
          <button class="btn btn-danger" type="button" @click="confirmReject">Ablehnen &amp; Begründung senden ✕</button>
        </div>
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
const activeTab = ref("overview");
const currentPlayingTrack = ref(null);
const activeParticles = ref([]);
const userVotes = ref({});
const selectedMatch = ref(null);

const battleRows = ref([]);
const submissionRows = ref([]);
const applicationRows = ref([]);

const approvedCount = computed(() => {
  if (isTeam.value && applicationRows.value.length > 0) {
    return applicationRows.value.filter((a) => a.status === "APPROVED").length;
  }
  return tournament.value?.approved_applications_count || 0;
});

const totalApplicationsCount = computed(() => {
  if (isTeam.value && applicationRows.value.length > 0) {
    return applicationRows.value.length;
  }
  return tournament.value?.applications_count || (myApplication.value ? 1 : 0);
});

const participantsCount = computed(() => {
  return approvedCount.value || tournament.value?.approved_applications_count || (tournament.value?.slots ? 0 : 0);
});

const battlesCount = computed(() => {
  if (battleRows.value.length > 0) return battleRows.value.length;
  return tournament.value?.battles_count || 0;
});

const bracketData = ref({
  quarterFinals: [],
  semiFinals: [],
  grandFinal: null,
});

const selectedRoundFilter = ref(1);
const editingSubmissionId = ref(null);

const showRejectModal = ref(false);
const rejectTargetType = ref("application");
const rejectingTarget = ref(null);
const rejectReasonInput = ref("");

const rejectPresets = [
  "Audio-Qualität unzureichend (Mix/Mastering)",
  "Vorgaben & Genre-Kriterien nicht eingehalten",
  "Beat nicht gecleart / Urheberrechtskonflikt",
  "Fehlerhafter Audio- oder Video-Link",
  "Vocal-Performance / Timing nicht ausreichend",
  "Deadline für diese Phase überschritten",
];

/* Dynamic Progressive Disclosure Tabs */
const tabs = computed(() => {
  const status = tournament.value?.status || "APPLICATION_OPEN";
  const list = [];

  if (status === "APPLICATION_OPEN") {
    list.push(
      { key: "overview", label: "📋 Übersicht & Bewerbung" },
      { key: "participants", label: "👥 Bewerber & Roster", count: participantsCount.value },
      { key: "rules", label: "📜 Regeln & Preispool" },
    );
  } else if (status === "SUBMISSION_OPEN") {
    list.push(
      { key: "submissions", label: "🎵 Runden & Einreichungen", count: submissionRows.value.length },
      { key: "participants", label: "👥 Teilnehmer-Roster", count: participantsCount.value },
      { key: "bracket", label: "🌳 Vorläufiger Turnierbaum" },
      { key: "rules", label: "📜 Regeln & Preispool" },
    );
  } else if (status === "BATTLES") {
    list.push(
      { key: "battles", label: "⚔️ Battles & Voting", count: battlesCount.value },
      { key: "bracket", label: "🌳 Turnierbaum & Bracket" },
      { key: "submissions", label: "🎵 Alle Runden", count: submissionRows.value.length },
      { key: "rules", label: "📜 Regeln & Preispool" },
    );
  } else {
    // CLOSED / DRAFT
    list.push(
      { key: "bracket", label: "🏆 Turnierbaum & Sieger" },
      { key: "battles", label: "⚔️ Alle Duelle", count: battlesCount.value },
      { key: "submissions", label: "🎵 Runden-Archiv", count: submissionRows.value.length },
      { key: "rules", label: "📜 Regeln & Preispool" },
    );
  }
  return list;
});

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
  prize_pool_1: "1.000 € Cash",
  prize_pool_2: "500 € Cash",
  prize_pool_3: "250 € Cash",
  genre: "",
  format: "SINGLE_ELIMINATION",
  slots: 16,
  total_rounds: 4,
  groups_count: 4,
  group_size: 4,
  description: "",
  is_no_loss: false,
});

/* Artist Identity & Submissions Helpers (Single Song per Round) */
const myApplication = computed(() => {
  if (!me.value?.id && !me.value?.name && !me.value?.username) return null;
  return applicationRows.value.find(
    (a) =>
      a.profile === me.value?.id ||
      (me.value?.name && a.profile_name === me.value?.name) ||
      (me.value?.username && a.profile_name === me.value?.username)
  ) || null;
});

const mySubmissions = computed(() => {
  if (!me.value?.id && !me.value?.name && !me.value?.username) return [];
  return submissionRows.value.filter(
    (s) =>
      s.profile === me.value?.id ||
      (me.value?.name && s.profile_name === me.value?.name) ||
      (me.value?.username && s.profile_name === me.value?.username)
  );
});

const myCurrentSubmission = computed(() => {
  return mySubmissions.value[0] || null;
});

const mySubmissionForSelectedRound = computed(() => {
  return mySubmissions.value.find((s) => s.round_number === selectedRoundFilter.value) || null;
});

const filteredSubmissionsForRound = computed(() => {
  return submissionRows.value.filter((s) => (s.round_number || 1) === selectedRoundFilter.value);
});

function getSubmissionsCountForRound(round) {
  return submissionRows.value.filter((s) => (s.round_number || 1) === round).length;
}

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

function formatLabel(fmt) {
  const map = {
    SINGLE_ELIMINATION: "K.O.-System",
    GROUP_STAGE: "Gruppenphase + K.O. ⭐",
    DOUBLE_ELIMINATION: "No-Loss Bracket",
    ROUND_ROBIN: "Liga-Modus",
  };
  return map[fmt] || fmt || "K.O.-System";
}

function formatDescription(fmt) {
  const map = {
    SINGLE_ELIMINATION: "Klassisches K.O.-Turnier: Wer verliert scheidet direkt aus.",
    GROUP_STAGE: "Vorrunde in Gruppen mit Hinspielen. Die Gruppenbesten ziehen in die K.O.-Finals ein.",
    DOUBLE_ELIMINATION: "Kein direktes Ausscheiden nach einer Niederlage dank Loser-Bracket.",
    ROUND_ROBIN: "Jeder Teilnehmer battlet gegen jeden anderen Teilnehmer dieser Liga.",
  };
  return map[fmt] || "Spannender Battle-Wettbewerb im UNYQ Circuit.";
}

function cleanDescription(desc) {
  if (!desc) return "";
  return desc
    .replace(/\[Preispool[^\]]*\]/gi, "")
    .replace(/\[Genre:[^\]]+\]/gi, "")
    .replace(/\[Slots:[^\]]+\]/gi, "")
    .replace(/\[Format:[^\]]+\]/gi, "")
    .replace(/\[GroupsCount:[^\]]+\]/gi, "")
    .replace(/\[GroupSize:[^\]]+\]/gi, "")
    .replace(/\[TotalRounds:[^\]]+\]/gi, "")
    .replace(/\[EntryRules:[^\]]+\]/gi, "")
    .trim();
}

function displayTitle(title) {
  if (!title || title.trim() === "1" || title.trim() === "Turnier #1") {
    return "UNYQ Beat Battle Arena";
  }
  return title;
}

function displayDescription(desc) {
  const cleaned = cleanDescription(desc);
  if (!cleaned || cleaned.trim() === "1" || cleaned.trim().length < 3) {
    return "Offizielles UNYQ Battle Turnier. Tritt im 1v1 an, sammle RP und kämpfe um den Sieg.";
  }
  return cleaned;
}

function displayPrizePool(t) {
  if (!t?.prize_pool || t.prize_pool.toLowerCase().includes("kein") || t.prize_pool.toLowerCase().includes("festgelegt")) {
    return "Community Cup & RP";
  }
  return t.prize_pool;
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

async function decideApplication(app, decision, reason = "") {
  app.status = decision;
  if (reason) app.rejection_reason = reason;
  try {
    await api.post(`tournament-applications/${app.id}/decision/`, { decision, reason });
    showToast(`Bewerbung ${decision === 'APPROVED' ? 'angenommen' : 'abgelehnt'}.`, "info");
  } catch {
    // fallback
  }
}

async function decideSubmission(sub, decision, reason = "") {
  sub.status = decision;
  if (reason) sub.rejection_reason = reason;
  try {
    await api.post(`tournament-submissions/${sub.id}/decision/`, { decision, reason });
    showToast(`Einreichung ${decision === 'APPROVED' ? 'freigegeben' : 'abgelehnt'}.`, "info");
  } catch {
    // fallback
  }
}

function promptRejectApplication(app) {
  rejectTargetType.value = "application";
  rejectingTarget.value = app;
  rejectReasonInput.value = "";
  showRejectModal.value = true;
}

function promptRejectSubmission(sub) {
  rejectTargetType.value = "submission";
  rejectingTarget.value = sub;
  rejectReasonInput.value = "";
  showRejectModal.value = true;
}

async function confirmReject() {
  const target = rejectingTarget.value;
  const reason = rejectReasonInput.value.trim();
  if (!target) return;

  if (rejectTargetType.value === "application") {
    await decideApplication(target, "REJECTED", reason);
  } else {
    await decideSubmission(target, "REJECTED", reason);
  }
  showRejectModal.value = false;
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
  let prize1 = tournament.value.prize_pool_1 || tournament.value.meta_settings?.prize_pool_1 || tournament.value.prize_pool || "1.000 € Cash";
  let prize2 = tournament.value.prize_pool_2 || tournament.value.meta_settings?.prize_pool_2 || "500 € Cash";
  let prize3 = tournament.value.prize_pool_3 || tournament.value.meta_settings?.prize_pool_3 || "250 € Cash";
  if (tournament.value.description) {
    const p1 = tournament.value.description.match(/\[Preispool:\s*([^\]]+)\]/i);
    if (p1) prize1 = p1[1];
    const p2 = tournament.value.description.match(/\[Preispool2:\s*([^\]]+)\]/i);
    if (p2) prize2 = p2[1];
    const p3 = tournament.value.description.match(/\[Preispool3:\s*([^\]]+)\]/i);
    if (p3) prize3 = p3[1];
  }

  editForm.value = {
    title: tournament.value.title || "",
    prize_pool: prize1,
    prize_pool_1: prize1,
    prize_pool_2: prize2,
    prize_pool_3: prize3,
    genre: tournament.value.genre || "Trap & 808",
    format: tournament.value.format || "SINGLE_ELIMINATION",
    slots: tournament.value.slots || 16,
    total_rounds: tournament.value.total_rounds || 4,
    groups_count: tournament.value.groups_count || 4,
    group_size: tournament.value.group_size || 4,
    description: cleanDescription(tournament.value.description) || "",
    is_no_loss: tournament.value.format === "DOUBLE_ELIMINATION" || Boolean(tournament.value.is_no_loss),
  };
  showEditModal.value = true;
}

async function submitEditTournament() {
  const id = tournament.value?.id;
  if (!id) return;

  const prize1 = editForm.value.prize_pool_1 || editForm.value.prize_pool || "1.000 € Cash";
  const prize2 = editForm.value.prize_pool_2 || "500 € Cash";
  const prize3 = editForm.value.prize_pool_3 || "250 € Cash";
  const genreText = editForm.value.genre || "Trap & 808";
  const formatText = editForm.value.format || "SINGLE_ELIMINATION";
  const slotsNum = editForm.value.slots || 16;
  const totalRoundsNum = editForm.value.total_rounds || 4;
  const groupsCountNum = editForm.value.groups_count || 4;
  const groupSizeNum = editForm.value.group_size || 4;
  const cleanDesc = cleanDescription(editForm.value.description);

  const metaDesc = `[Preispool: ${prize1}] [Preispool2: ${prize2}] [Preispool3: ${prize3}] [Genre: ${genreText}] [Format: ${formatText}] [Slots: ${slotsNum}] [TotalRounds: ${totalRoundsNum}] [GroupsCount: ${groupsCountNum}] [GroupSize: ${groupSizeNum}]\n\n${cleanDesc}`;

  const payload = {
    title: editForm.value.title,
    description: metaDesc,
    is_no_loss: formatText === "DOUBLE_ELIMINATION",
    meta_settings: {
      prize_pool: prize1,
      prize_pool_1: prize1,
      prize_pool_2: prize2,
      prize_pool_3: prize3,
      genre: genreText,
      format: formatText,
      slots: slotsNum,
      total_rounds: totalRoundsNum,
      groups_count: groupsCountNum,
      group_size: groupSizeNum,
    },
  };

  try {
    const { data } = await api.patch(`tournaments/${id}/`, payload);
    tournament.value = {
      ...tournament.value,
      ...data,
      prize_pool: prize1,
      prize_pool_1: prize1,
      prize_pool_2: prize2,
      prize_pool_3: prize3,
      genre: genreText,
      format: formatText,
      slots: slotsNum,
      total_rounds: totalRoundsNum,
      groups_count: groupsCountNum,
      group_size: groupSizeNum,
      is_no_loss: formatText === "DOUBLE_ELIMINATION",
    };
    showToast("Turnierdaten erfolgreich aktualisiert! 💾", "success");
  } catch {
    tournament.value.title = editForm.value.title;
    tournament.value.prize_pool = prize1;
    tournament.value.prize_pool_1 = prize1;
    tournament.value.prize_pool_2 = prize2;
    tournament.value.prize_pool_3 = prize3;
    tournament.value.genre = genreText;
    tournament.value.format = formatText;
    tournament.value.slots = slotsNum;
    tournament.value.total_rounds = totalRoundsNum;
    tournament.value.groups_count = groupsCountNum;
    tournament.value.group_size = groupSizeNum;
    tournament.value.description = metaDesc;
    tournament.value.is_no_loss = formatText === "DOUBLE_ELIMINATION";
    showToast("Turnierdaten lokal aktualisiert.", "success");
  }
  showEditModal.value = false;
}

/* Submitting Application & Round */
function openApplyModal() {
  if (myApplication.value) {
    applyArtistName.value = myApplication.value.profile_name || me.value?.name || "";
    const demoMatch = myApplication.value.message?.match(/Demo:\s*([^|]+)/i);
    applyDemoLink.value = demoMatch ? demoMatch[1].trim() : "";
    const rawParts = (myApplication.value.message || "").split("|");
    const rawMsg = rawParts.length > 2 ? rawParts.slice(2).join("|") : (rawParts[1] || "");
    applyMessage.value = rawMsg.split("[Jury-Begründung:")[0].trim();
  } else {
    applyArtistName.value = me.value?.name || me.value?.username || "";
    applyDemoLink.value = "";
    applyMessage.value = "";
  }
  showApplyModal.value = true;
}

async function submitApply() {
  const tId = tournament.value?.id;
  const msg = `Artist: ${applyArtistName.value} | Demo: ${applyDemoLink.value} | ${applyMessage.value}`;

  try {
    if (myApplication.value?.id) {
      const { data } = await api.patch(`tournament-applications/${myApplication.value.id}/`, {
        message: msg,
      });
      const idx = applicationRows.value.findIndex(a => a.id === myApplication.value.id);
      if (idx !== -1) {
        applicationRows.value[idx] = {
          ...applicationRows.value[idx],
          profile_name: applyArtistName.value,
          message: msg,
          status: "PENDING",
          rejection_reason: "",
        };
      }
      showToast("Bewerbung erfolgreich aktualisiert & neu eingereicht! 🎤", "success");
    } else {
      const { data } = await api.post("tournament-applications/", {
        tournament: tId,
        message: msg,
      });
      applicationRows.value.unshift({
        id: data.id,
        profile: me.value?.id,
        profile_name: applyArtistName.value,
        status: "PENDING",
        message: msg,
        rejection_reason: "",
      });
      showToast("Bewerbung erfolgreich eingereicht! 🎤", "success");
    }
  } catch (err) {
    showToast(err?.response?.data?.detail || "Bewerbung gespeichert.", "info");
  }

  showApplyModal.value = false;
  await loadApplications();
}

function openUploadRoundModal(round = 1) {
  selectedRoundFilter.value = round;
  uploadRoundNumber.value = round;
  const existing = mySubmissions.value.find((s) => (s.round_number || 1) === round);
  if (existing) {
    editingSubmissionId.value = existing.id;
    uploadRoundTitle.value = existing.title || "";
    uploadMediaUrl.value = existing.media_url || "";
    const bpmMatch = existing.notes?.match(/BPM:\s*([^|]+)/i);
    const keyMatch = existing.notes?.match(/Key:\s*([^|]+)/i);
    uploadBpm.value = bpmMatch ? bpmMatch[1].trim() : "140";
    uploadKey.value = keyMatch ? keyMatch[1].trim() : "C# Minor";
  } else {
    editingSubmissionId.value = null;
    uploadRoundTitle.value = `${tournament.value?.title || 'Contest'} - Runde ${round}`;
    uploadMediaUrl.value = "";
    uploadBpm.value = "140";
    uploadKey.value = "C# Minor";
  }
  showUploadModal.value = true;
}

async function submitRound() {
  const tId = tournament.value?.id;
  const roundNum = uploadRoundNumber.value || 1;
  const notes = `BPM: ${uploadBpm.value} | Key: ${uploadKey.value}`;

  const payload = {
    tournament: tId,
    round_number: roundNum,
    title: uploadRoundTitle.value,
    media_url: uploadMediaUrl.value,
    notes,
  };

  try {
    if (editingSubmissionId.value) {
      const { data } = await api.patch(`tournament-submissions/${editingSubmissionId.value}/`, payload);
      const idx = submissionRows.value.findIndex(s => s.id === editingSubmissionId.value);
      if (idx !== -1) {
        submissionRows.value[idx] = {
          ...submissionRows.value[idx],
          title: uploadRoundTitle.value,
          media_url: uploadMediaUrl.value,
          notes,
          status: "PENDING",
          rejection_reason: "",
        };
      }
      showToast("Runde erfolgreich aktualisiert & neu eingereicht! 🚀", "success");
    } else {
      const { data } = await api.post("tournament-submissions/", payload);
      submissionRows.value = submissionRows.value.filter(
        s => !(s.round_number === roundNum && (s.profile === me.value?.id || s.profile_name === me.value?.name))
      );
      submissionRows.value.unshift({
        id: data.id,
        title: uploadRoundTitle.value,
        profile: me.value?.id,
        profile_name: me.value?.name || me.value?.username || "Du",
        round_number: roundNum,
        status: "PENDING",
        media_url: uploadMediaUrl.value,
        notes,
        rejection_reason: "",
      });
      showToast("Runde erfolgreich eingereicht! 🚀", "success");
    }
  } catch (err) {
    showToast(err?.response?.data?.detail || "Runde übermittelt.", "info");
  }

  showUploadModal.value = false;
  await loadSubmissions();
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
    let prize1 = data.meta_settings?.prize_pool_1 || data.meta_settings?.prize_pool || "1.000 € Cash";
    let prize2 = data.meta_settings?.prize_pool_2 || "500 € Cash";
    let prize3 = data.meta_settings?.prize_pool_3 || "250 € Cash";
    let genre = "Allround";
    let format = "SINGLE_ELIMINATION";
    let slots = 16;
    let totalRounds = 4;
    let groupsCount = 4;
    let groupSize = 4;

    if (data.meta_settings) {
      prize1 = data.meta_settings.prize_pool_1 || data.meta_settings.prize_pool || prize1;
      prize2 = data.meta_settings.prize_pool_2 || prize2;
      prize3 = data.meta_settings.prize_pool_3 || prize3;
      genre = data.meta_settings.genre || genre;
      format = data.meta_settings.format || format;
      slots = data.meta_settings.slots || slots;
      totalRounds = data.meta_settings.total_rounds || totalRounds;
      groupsCount = data.meta_settings.groups_count || groupsCount;
      groupSize = data.meta_settings.group_size || groupSize;
    }
    if (data.description) {
      const pMatch = data.description.match(/\[Preispool:\s*([^\]]+)\]/i);
      if (pMatch) prize1 = pMatch[1];
      const p2Match = data.description.match(/\[Preispool2:\s*([^\]]+)\]/i);
      if (p2Match) prize2 = p2Match[1];
      const p3Match = data.description.match(/\[Preispool3:\s*([^\]]+)\]/i);
      if (p3Match) prize3 = p3Match[1];
      const gMatch = data.description.match(/\[Genre:\s*([^\]]+)\]/i);
      if (gMatch) genre = gMatch[1];
      const fMatch = data.description.match(/\[Format:\s*([^\]]+)\]/i);
      if (fMatch) format = fMatch[1];
      const sMatch = data.description.match(/\[Slots:\s*(\d+)\]/i);
      if (sMatch) slots = parseInt(sMatch[1], 10);
      const rMatch = data.description.match(/\[TotalRounds:\s*(\d+)\]/i);
      if (rMatch) totalRounds = parseInt(rMatch[1], 10);
      const gcMatch = data.description.match(/\[GroupsCount:\s*(\d+)\]/i);
      if (gcMatch) groupsCount = parseInt(gcMatch[1], 10);
      const gsMatch = data.description.match(/\[GroupSize:\s*(\d+)\]/i);
      if (gsMatch) groupSize = parseInt(gsMatch[1], 10);
    }

    tournament.value = {
      ...data,
      prize_pool: prize1,
      prize_pool_1: prize1,
      prize_pool_2: prize2,
      prize_pool_3: prize3,
      genre,
      format,
      slots,
      total_rounds: totalRounds,
      groups_count: groupsCount,
      group_size: groupSize,
    };

    // Set default tab based on tournament status if not explicitly requested in query
    if (route.query.tab && tabs.value.some(t => t.key === route.query.tab)) {
      activeTab.value = route.query.tab;
    } else {
      if (tournament.value?.status === "APPLICATION_OPEN") activeTab.value = "overview";
      else if (tournament.value?.status === "SUBMISSION_OPEN") activeTab.value = "submissions";
      else if (tournament.value?.status === "BATTLES") activeTab.value = "battles";
      else if (tournament.value?.status === "CLOSED") activeTab.value = "bracket";
      else activeTab.value = tabs.value[0]?.key || "overview";
    }
  } catch {
    tournament.value = {
      id,
      title: "Turnier #" + id,
      description: "Turnier-Informationen werden geladen.",
      status: "DRAFT",
      genre: "Allround",
      prize_pool: "Kein Preispool festgelegt",
      format: "SINGLE_ELIMINATION",
      slots: 16,
      total_rounds: 4,
      groups_count: 4,
      group_size: 4,
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
      profile: s.profile?.id || s.profile,
      title: s.title || `Runde ${s.round_number}`,
      profile_name: s.profile?.name || s.profile?.user?.username || s.artist_name || "Artist",
      round_number: s.round_number || 1,
      status: s.status,
      media_url: s.media_url,
      notes: s.notes,
      rejection_reason: s.rejection_reason || "",
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
      profile: a.profile?.id || a.profile,
      profile_name: a.profile?.name || a.profile?.user?.username || a.artist_name || "Artist",
      status: a.status,
      message: a.message,
      rejection_reason: a.rejection_reason || "",
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
  width: 100%;
  max-width: 100%;
  margin: 0;
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

/* Compact High-End Tournament Header */
.compact-tourney-header {
  padding: 18px 24px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.header-top-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.top-status-pills {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.badge-format-tag {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.35);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}

.badge-no-loss {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.35);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 700;
}

.badge-genre-tag {
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
  border: 1px solid rgba(255, 255, 255, 0.1);
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  font-weight: 600;
}

/* Admin Micro-Toolbar */
.admin-compact-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 7px 12px;
  border-radius: 10px;
  background: rgba(245, 158, 11, 0.06);
  border: 1px solid rgba(245, 158, 11, 0.22);
  flex-wrap: wrap;
}

.act-phase-picker {
  display: flex;
  align-items: center;
  gap: 8px;
}

.act-label {
  font-size: 11.5px;
  font-weight: 700;
  color: #fbbf24;
}

.act-select {
  padding: 3px 8px;
  font-size: 12px;
  border-radius: 7px;
  background: rgba(15, 23, 42, 0.9);
  color: #fff;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.act-actions {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-micro {
  padding: 4px 10px;
  font-size: 11px;
  font-weight: 700;
  border-radius: 6px;
}

.btn-danger-link {
  color: #f87171 !important;
}

/* Main Title & Action Row */
.header-center-strip {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.hcs-title-col {
  flex: 1;
  min-width: 260px;
}

.title-line {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.tournament-title {
  font-size: 1.55rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
  line-height: 1.2;
}

.tournament-desc {
  font-size: 13px;
  color: var(--muted);
  margin: 4px 0 0;
  max-width: 680px;
  line-height: 1.45;
}

.hcs-action-col {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-cta-pulse {
  padding: 10px 22px;
  font-size: 13.5px;
  font-weight: 800;
  border-radius: 10px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  box-shadow: 0 4px 14px rgba(245, 158, 11, 0.35);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-cta-pulse:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(245, 158, 11, 0.45);
}

.user-inline-status {
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(255, 255, 255, 0.04);
  padding: 6px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.btn-play-mini {
  color: #60a5fa !important;
  font-size: 12px;
}

/* Rejection Banners */
.hero-rejection-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 10px;
  padding: 10px 14px;
  color: #fca5a5;
  font-size: 12.5px;
  gap: 10px;
  flex-wrap: wrap;
}

.hero-rejection-banner p {
  margin: 0;
  font-style: italic;
  color: #fff;
}

/* Metadata Chips Ribbon */
.metadata-chips-strip {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.meta-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.035);
  border: 1px solid rgba(255, 255, 255, 0.07);
  font-size: 12px;
  font-weight: 700;
  color: #cbd5e1;
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

/* Compact Admin Bar */
.admin-compact-header-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(245, 158, 11, 0.35);
  border-radius: 14px;
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.ach-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.ach-badge {
  font-size: 12px;
  font-weight: 800;
  color: #fbbf24;
}

.ach-select {
  padding: 4px 10px;
  font-size: 12px;
  border-radius: 8px;
  background: rgba(0, 0, 0, 0.4);
  color: #fff;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.ach-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

/* Badge Format */
.badge-format-tag {
  background: rgba(168, 85, 247, 0.2);
  color: #d8b4fe;
  border: 1px solid rgba(168, 85, 247, 0.4);
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
}

/* User Contest Status Cards in Hero */
.user-contest-status-card {
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.user-contest-status-card.status-approved {
  border-color: rgba(52, 211, 153, 0.35);
  background: rgba(52, 211, 153, 0.05);
}

.user-contest-status-card.status-rejected {
  border-color: rgba(239, 68, 68, 0.4);
  background: rgba(239, 68, 68, 0.06);
}

.ucs-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.ucs-title {
  font-size: 13px;
  font-weight: 800;
  color: #fff;
}

.ucs-song-preview {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(0, 0, 0, 0.25);
  padding: 8px 12px;
  border-radius: 10px;
  font-size: 13px;
  color: #f1f5f9;
}

/* Rejection Reason Alert Box */
.rejection-reason-box {
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.35);
  border-radius: 12px;
  padding: 12px 14px;
  color: #fca5a5;
  font-size: 13px;
  line-height: 1.5;
}

.rrb-title {
  font-weight: 800;
  color: #f87171;
  margin-bottom: 4px;
}

.rrb-text {
  margin: 0 0 6px;
  color: #fff;
  font-style: italic;
}

.item-rejection-tag {
  margin-top: 6px;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(239, 68, 68, 0.15);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 12px;
  font-style: italic;
}

.approved-box {
  color: #34d399;
  font-size: 13px;
  line-height: 1.4;
}

.pending-box {
  color: #fbbf24;
  font-size: 13px;
  line-height: 1.4;
}

/* TAB: Overview */
.overview-grid-layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 24px;
}

.overview-main-col {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.format-highlight-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.fhc-header {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 16px;
}

.fhc-icon {
  font-size: 32px;
}

.fhc-header h3 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  color: #fff;
}

.group-stage-spec-box {
  background: rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.25);
  border-radius: 14px;
  padding: 14px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gs-spec-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13.5px;
}

.gs-label {
  color: var(--muted);
}

.gs-value {
  color: #e9d5ff;
}

.general-format-pills {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.pill-meta {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 12.5px;
  font-weight: 700;
  color: #e2e8f0;
}

.my-application-status-card {
  padding: 22px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.25);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.masc-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.masc-icon {
  font-size: 26px;
}

.masc-header h4 {
  margin: 0 0 2px;
  color: #fff;
}

.masc-body {
  background: rgba(0, 0, 0, 0.2);
  padding: 12px 14px;
  border-radius: 10px;
}

.masc-message {
  margin: 0;
  color: #cbd5e1;
  font-size: 13.5px;
}

.apply-cta-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(52, 211, 153, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.acc-body {
  display: flex;
  align-items: center;
  gap: 16px;
}

.acc-icon {
  font-size: 34px;
}

.acc-body h3 {
  margin: 0 0 4px;
  color: #fff;
}

.roster-preview-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.roster-preview-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.03);
}

.rp-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #3b82f6;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 13px;
}

.rp-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  justify-content: space-between;
}

/* Roster Privacy for Artists */
.roster-privacy-overview {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rpo-stat-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.rpo-stat-item {
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  padding: 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}

.rpo-val {
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
}

.rpo-lbl {
  font-size: 11px;
  color: var(--muted);
}

.rpo-my-app-box {
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.25);
  border-radius: 10px;
  padding: 10px 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.rpo-my-app-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #93c5fd;
  font-weight: 700;
}

.rpo-privacy-note {
  font-size: 11.5px;
  color: #94a3b8;
  line-height: 1.45;
  margin: 0;
  padding: 8px 10px;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 8px;
  border-left: 3px solid #ffaa00;
}

.artist-roster-privacy-card {
  display: flex;
  flex-direction: column;
  gap: 18px;
  padding: 8px 0;
}

.arpc-stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 14px;
}

.arpc-stat-box {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
}

.arpc-stat-box.success {
  background: rgba(16, 185, 129, 0.06);
  border-color: rgba(16, 185, 129, 0.2);
}

.arpc-stat-box.warn {
  background: rgba(245, 158, 11, 0.06);
  border-color: rgba(245, 158, 11, 0.2);
}

.arpc-stat-icon {
  font-size: 24px;
}

.arpc-stat-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.arpc-stat-info strong {
  font-size: 1.25rem;
  color: #fff;
  font-weight: 800;
}

.arpc-stat-info span {
  font-size: 12px;
  color: var(--muted);
}

.my-application-detail-card {
  padding: 18px 20px;
  border-radius: 14px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.madc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.madc-header h4 {
  margin: 0;
  font-size: 1.05rem;
  color: #fff;
}

.madc-message {
  margin: 0;
  font-size: 13.5px;
  color: #cbd5e1;
  background: rgba(0, 0, 0, 0.3);
  padding: 10px 14px;
  border-radius: 8px;
}

.madc-footer {
  display: flex;
  justify-content: flex-end;
}

.empty-not-applied-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px dashed rgba(255, 255, 255, 0.15);
  color: var(--muted);
}

.empty-not-applied-banner p {
  margin: 0;
  font-size: 14px;
}

.roster-fairplay-notice {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 14px 16px;
  border-radius: 12px;
  background: rgba(255, 170, 0, 0.05);
  border: 1px solid rgba(255, 170, 0, 0.15);
  color: #cbd5e1;
  font-size: 13px;
  line-height: 1.5;
}

.rfn-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.roster-fairplay-notice strong {
  color: #ffaa00;
  display: block;
  margin-bottom: 2px;
}

.roster-fairplay-notice p {
  margin: 0;
}

/* Prize Pool Designer inside Modals */
.prize-pool-designer-box {
  background: rgba(255, 170, 0, 0.04);
  border: 1px solid rgba(255, 170, 0, 0.18);
  border-radius: 12px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.ppd-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #ffaa00;
}

.preset-pill-row {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
}

.preset-btn {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #cbd5e1;
  border-radius: 6px;
  font-size: 10.5px;
  padding: 2px 7px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.preset-btn:hover {
  background: rgba(255, 170, 0, 0.2);
  border-color: #ffaa00;
  color: #fff;
}

/* TAB: Submissions */
.round-picker-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 20px;
  border-radius: 16px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 14px;
}

.rpn-left {
  display: flex;
  align-items: center;
  gap: 14px;
}

.rpn-lbl {
  font-weight: 800;
  color: #fff;
  font-size: 13.5px;
}

.round-pills-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.round-pill-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.round-pill-btn.active {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
}

.count-chip {
  background: rgba(0, 0, 0, 0.25);
  padding: 1px 6px;
  border-radius: 999px;
  font-size: 10px;
}

.my-round-submission-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.9);
  border: 1px solid rgba(245, 158, 11, 0.35);
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.mrsc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.mrsc-title-block {
  display: flex;
  gap: 14px;
  align-items: center;
}

.mrsc-icon {
  font-size: 30px;
}

.mrsc-title-block h3 {
  margin: 0 0 2px;
  color: #fff;
}

.mrsc-track-details {
  background: rgba(0, 0, 0, 0.25);
  border-radius: 12px;
  padding: 14px 18px;
}

.track-main-line {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.track-title-text {
  font-size: 1.1rem;
  color: #fff;
}

.link-external {
  color: #60a5fa;
  font-size: 12px;
}

.mrsc-actions-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.empty-round-user-cta {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px dashed rgba(245, 158, 11, 0.3);
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}

.eruc-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.eruc-icon {
  font-size: 32px;
}

.eruc-content h4 {
  margin: 0 0 4px;
  color: #fff;
}

.group-stage-config-box {
  background: rgba(168, 85, 247, 0.08);
  border: 1px solid rgba(168, 85, 247, 0.25);
  border-radius: 14px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}

.gsc-title {
  font-size: 12.5px;
  font-weight: 800;
  color: #d8b4fe;
}

.reject-presets-wrap {
  margin-top: 10px;
}

.preset-label {
  font-size: 11.5px;
  color: var(--muted);
  font-weight: 700;
  display: block;
  margin-bottom: 6px;
}

.reject-presets-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
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
