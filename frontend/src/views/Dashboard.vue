<template>
  <div class="proartist-dashboard" :class="{ 'creator-view': viewMode === 'creator' }">
    <!-- Ambient Studio Glow -->
    <div class="studio-ambient-glow"></div>

    <!-- Hero Header -->
    <header class="studio-hero">
      <div class="hero-main-row">
        <div class="hero-copy">
          <!-- Mode Switcher -->
          <div class="mode-switcher-bar">
            <div class="mode-pill-toggle">
              <button
                type="button"
                class="mode-btn"
                :class="{ active: viewMode === 'creator' }"
                @click="setViewMode('creator')"
              >
                <span class="mode-icon">🎨</span>
                <span>Creator Studio</span>
              </button>
              <button
                type="button"
                class="mode-btn"
                :class="{ active: viewMode === 'admin' }"
                @click="setViewMode('admin')"
                v-if="isTeam"
              >
                <span class="mode-icon">⚡</span>
                <span>Team Operations</span>
              </button>
            </div>
          </div>

          <div class="hero-title-block">
            <h1 class="hero-headline">{{ greeting }}{{ displayName ? `, ${displayName}` : '' }}</h1>
            <p class="hero-subline" :class="{ 'has-issues': viewMode === 'admin' && heroHasIssues }">
              {{ currentHeroSubline }}
            </p>
          </div>
        </div>

        <!-- Hero Quick Action Dock -->
        <div class="hero-actions-dock">
          <button class="btn btn-primary" type="button" @click="openSongModal">
            <span class="btn-icon">🎵</span>
            <span>+ Song / Beat</span>
          </button>
          <button class="btn ghost" type="button" @click="openTaskModal">
            <span class="btn-icon">🗒️</span>
            <span>+ Task</span>
          </button>
          <button class="btn ghost arena-shortcut-btn" type="button" @click="goTo('tournaments')">
            <span class="btn-icon">🏆</span>
            <span>Arena Battles</span>
            <span class="dock-pulse-dot"></span>
          </button>
          <button class="btn ghost" type="button" @click="goTo('profiles')">
            <span class="btn-icon">🤝</span>
            <span>Collab finden</span>
          </button>
          <button class="btn ghost icon-refresh-btn" type="button" @click="refresh" :disabled="loading" title="Aktualisieren">
            <span :class="{ spinning: loading }">↻</span>
          </button>
        </div>
      </div>
    </header>

    <!-- ========================================== -->
    <!-- CREATOR STUDIO VIEW (Artist Value First)    -->
    <!-- ========================================== -->
    <template v-if="viewMode === 'creator'">
      <!-- Section 1: Studio Pipeline & Release Radar -->
      <section class="studio-section">
        <div class="section-header">
          <div class="header-left">
            <span class="section-icon">🎛️</span>
            <div>
              <h2>Studio Pipeline &amp; Release Radar</h2>
              <p class="muted small">Verfolge deine aktiven Songs von der Beat-Idee bis zum fertigen Master &amp; Release.</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn ghost tiny" @click="goTo('songs')">Alle Songs &amp; Stems →</button>
            <button class="btn tiny" @click="openSongModal">+ Neuer Track</button>
          </div>
        </div>

        <!-- Song Cards Grid -->
        <div class="pipeline-grid" v-if="songsList.length">
          <article
            v-for="song in songsList.slice(0, 4)"
            :key="song.id"
            class="pipeline-card"
          >
            <div class="track-head">
              <div class="cover-wrapper" @click="togglePlayAudio(song)">
                <img v-if="song.cover_url" :src="song.cover_url" :alt="song.title" class="track-cover-img" />
                <div v-else class="track-cover-placeholder">
                  <span>🎹</span>
                </div>
                <button class="cover-play-btn" :class="{ playing: currentPlayingSongId === song.id }">
                  {{ currentPlayingSongId === song.id ? '⏸' : '▶' }}
                </button>
              </div>

              <div class="track-meta">
                <div class="meta-row-top">
                  <span class="status-pill" :data-status="song.status">{{ songStatusLabel(song.status) }}</span>
                  <span v-if="song.genre" class="tag-mini">{{ song.genre }}</span>
                  <span v-if="song.bpm" class="tag-mini bpm">{{ song.bpm }} BPM</span>
                </div>
                <h3 class="track-title" @click="goTo('songs')">{{ song.title }}</h3>
                <p class="track-desc muted">{{ song.description || 'Aktiver Studio-Track in Bearbeitung' }}</p>
              </div>
            </div>

            <!-- 5-Stage Protected Release Progress Pipeline -->
            <div class="stage-pipeline-bar">
              <div
                v-for="(stage, idx) in releaseStages"
                :key="stage.key"
                class="stage-step"
                :class="{
                  active: getSongStageIndex(song) === idx,
                  completed: getSongStageIndex(song) > idx,
                  clickable: true
                }"
                @click.stop="confirmChangeStage(song, idx)"
                :title="`Phase ${idx + 1}: ${stage.label} (Klicken zum Ändern)`"
              >
                <div class="step-dot">
                  <span v-if="getSongStageIndex(song) > idx">✓</span>
                  <span v-else>{{ idx + 1 }}</span>
                </div>
                <span class="step-label">{{ stage.label }}</span>
                <span class="step-lock-tag" v-if="getSongStageIndex(song) === idx" title="Geschützte Phase">🔒</span>
              </div>
            </div>

            <div class="track-footer">
              <span class="version-badge">
                {{ song.version_count ? `${song.version_count} Versionen / Stems` : 'v1 Demo Cut' }}
              </span>
              <button class="btn ghost tiny link-btn" @click="goTo('songs')">
                Versionen öffnen →
              </button>
            </div>
          </article>
        </div>

        <!-- Empty State with Creator Action -->
        <div class="empty-pipeline-box" v-else>
          <div class="empty-icon-ring">🎵</div>
          <h3>Starte deinen nächsten Release</h3>
          <p class="muted">
            Lade deine Beats, Demos oder Vocals hoch. Organisiere Mixdown, Mastering und Feedback direkt im Workflow.
          </p>
          <div class="empty-actions">
            <button class="btn" @click="openSongModal">+ Ersten Song / Beat anlegen</button>
            <button class="btn ghost" @click="router.push('/platforms/library')">📦 Sound Library durchsuchen</button>
          </div>
        </div>
      </section>

      <!-- Two-Column Layout: Daily Studio Focus + Live Arena Radar -->
      <div class="dashboard-duo-grid">
        <!-- Module 2: Daily Studio Focus & Tasks -->
        <section class="duo-panel">
          <div class="section-header">
            <div class="header-left">
              <span class="section-icon">✅</span>
              <div>
                <h2>Heutiger Studio-Fokus</h2>
                <p class="muted small">{{ myActiveTasks.length }} fällige Aufgaben für deine Releases</p>
              </div>
            </div>
            <button class="btn ghost tiny" @click="goTo('tasks')">Task Board →</button>
          </div>

          <!-- Quick Inline Task Creator -->
          <form class="quick-add-task-form" @submit.prevent="submitQuickTask">
            <input
              class="input quick-task-input"
              v-model.trim="quickTaskTitle"
              placeholder="+ Neue Studio-Aufgabe erfassen (z.B. Vocal Take 2, Mix-Feedback)..."
              :disabled="quickTaskSaving"
            />
            <button class="btn tiny" type="submit" :disabled="!quickTaskTitle || quickTaskSaving">
              {{ quickTaskSaving ? '...' : 'Hinzufügen' }}
            </button>
          </form>

          <!-- Task Focus List -->
          <ul class="studio-task-list" v-if="myActiveTasks.length">
            <li
              v-for="task in myActiveTasks.slice(0, 5)"
              :key="task.id"
              class="studio-task-item"
              :class="{ completed: task.status === 'DONE' }"
            >
              <label class="task-check-label">
                <input
                  type="checkbox"
                  :checked="task.status === 'DONE'"
                  @change="toggleTaskDone(task)"
                />
                <span class="custom-checkbox"></span>
              </label>

              <div class="task-content">
                <strong class="task-title" :class="{ strike: task.status === 'DONE' }">
                  {{ task.title }}
                </strong>
                <div class="task-tags">
                  <span v-if="task.project_title" class="task-proj-pill">📁 {{ task.project_title }}</span>
                  <span class="task-prio-pill" :data-priority="task.priority">
                    {{ priorityMap[task.priority] || task.priority }}
                  </span>
                  <span v-if="task.due_date" class="task-due-pill" :data-tone="dueState(task.due_date)">
                    {{ dueLabel(task.due_date) }}
                  </span>
                </div>
              </div>

              <button class="btn ghost tiny icon-only-btn" @click="goToRoute(getTaskRoute(task))" title="Details öffnen">
                →
              </button>
            </li>
          </ul>

          <div class="empty-subtext" v-else>
            <p class="muted">Keine offenen Aufgaben. Dein Fokus ist frei für neue Musik!</p>
          </div>
        </section>

        <!-- Module 3: Live Arena & Battle Radar -->
        <section class="duo-panel arena-spotlight-card">
          <div class="section-header">
            <div class="header-left">
              <span class="section-icon">🏆</span>
              <div>
                <h2>Turniere &amp; Battle Radar</h2>
                <p class="muted small">Messe dich mit Producern, gewinne Preisgelder &amp; sammle XP.</p>
              </div>
            </div>
            <button class="btn ghost tiny" @click="goTo('tournaments')">Zur Arena →</button>
          </div>

          <div class="arena-tournaments-list" v-if="activeTournaments.length">
            <article
              v-for="tournament in activeTournaments.slice(0, 3)"
              :key="tournament.id"
              class="arena-mini-card"
              @click="router.push(`/app/tournaments`)"
            >
              <div class="am-left">
                <div class="am-title-row">
                  <span class="am-pulse-dot"></span>
                  <strong>{{ tournament.title }}</strong>
                </div>
                <div class="am-meta">
                  <span class="prize-tag" v-if="tournament.prize_pool">💰 {{ tournament.prize_pool }}</span>
                  <span class="status-tag">{{ tournamentStatusLabel(tournament.status) }}</span>
                </div>
              </div>
              <button class="btn btn-sm action-arena-btn">
                Battle öffnen →
              </button>
            </article>
          </div>

          <div class="empty-subtext" v-else>
            <p class="muted">Aktuell laufen Vorbereitungen für die nächste Beat-Battle-Saison.</p>
            <button class="btn ghost tiny" @click="goTo('tournaments')">Turnier-Übersicht ansehen</button>
          </div>
        </section>
      </div>

      <!-- Two-Column Layout: GrowPro Milestones + Feedback & Collab Hub -->
      <div class="dashboard-duo-grid">
        <!-- Module 4: GrowPro Milestones & XP Streak -->
        <section class="duo-panel">
          <div class="section-header">
            <div class="header-left">
              <span class="section-icon">🌱</span>
              <div>
                <h2>GrowPro Karriere-Ziele</h2>
                <p class="muted small">Deine persönlichen Entwicklungs-Meilensteine &amp; Aktivitäts-Streak</p>
              </div>
            </div>
            <button class="btn ghost tiny" @click="goTo('growpro')">Alle Ziele →</button>
          </div>

          <!-- Streak & XP Bar -->
          <div class="streak-xp-banner">
            <div class="streak-box">
              <span class="streak-flame">🔥</span>
              <div>
                <strong>{{ studioStreakDays }} Tage Streak</strong>
                <p class="muted tiny">Aktiv im Studio</p>
              </div>
            </div>
            <div class="xp-box">
              <div class="xp-head">
                <span class="xp-level">Level {{ artistLevel }} Creator</span>
                <span class="xp-points">{{ artistPoints }} XP</span>
              </div>
              <div class="xp-bar-track">
                <div class="xp-bar-fill" :style="{ width: `${artistLevelProgress}%` }"></div>
              </div>
            </div>
          </div>

          <!-- Goals List -->
          <ul class="growpro-mini-list" v-if="growpro.length">
            <li v-for="goal in growpro.slice(0, 4)" :key="goal.id" class="growpro-mini-item">
              <div class="gp-body">
                <strong>{{ goal.title }}</strong>
                <span class="muted small">{{ goal.due_date ? `Frist: ${formatDate(goal.due_date)}` : 'Laufendes Ziel' }}</span>
              </div>
              <span class="badge" :data-tone="isGrowproStale(goal) ? 'soon' : (goal.due_date ? dueState(goal.due_date) : 'ok')">
                {{ isGrowproStale(goal) ? 'Update fällig' : (goal.due_date ? dueLabel(goal.due_date) : 'Aktiv') }}
              </span>
            </li>
          </ul>

          <div class="empty-subtext" v-else>
            <p class="muted">Noch keine Entwicklungs-Ziele definiert.</p>
            <button class="btn ghost tiny" @click="goTo('growpro')">+ Erstes Ziel anlegen</button>
          </div>
        </section>

        <!-- Module 5: Creator Resources & Collab Hub -->
        <section class="duo-panel">
          <div class="section-header">
            <div class="header-left">
              <span class="section-icon">🧰</span>
              <div>
                <h2>Producer &amp; Creator Toolbox</h2>
                <p class="muted small">Kostenlose Samples, Drum Kits, Feedback und Community-Ressourcen</p>
              </div>
            </div>
          </div>

          <div class="toolbox-grid">
            <div class="toolbox-item" @click="router.push('/platforms/library')">
              <span class="tb-icon">📦</span>
              <div class="tb-info">
                <strong>UNYQ Sound Library</strong>
                <p class="muted tiny">100% Free CC0 Samples, 808s &amp; Serum Presets</p>
              </div>
              <span class="tb-arrow">→</span>
            </div>

            <div class="toolbox-item" @click="router.push('/platforms/music')">
              <span class="tb-icon">🎧</span>
              <div class="tb-info">
                <strong>UNYQ Music Player</strong>
                <p class="muted tiny">VIP Unreleased Drops &amp; Referenz-Tracks hören</p>
              </div>
              <span class="tb-arrow">→</span>
            </div>

            <div class="toolbox-item" @click="router.push('/platforms/forum')">
              <span class="tb-icon">💬</span>
              <div class="tb-info">
                <strong>Community Forum</strong>
                <p class="muted tiny">Collab-Partner suchen, Feedback austauschen</p>
              </div>
              <span class="tb-arrow">→</span>
            </div>

            <div class="toolbox-item" @click="router.push('/platforms/finance')">
              <span class="tb-icon">💰</span>
              <div class="tb-info">
                <strong>UNYQ Finance</strong>
                <p class="muted tiny">Tantiemen, GEMA/GVL und Projektbudgets</p>
              </div>
              <span class="tb-arrow">→</span>
            </div>
          </div>
        </section>
      </div>
    </template>

    <!-- ========================================== -->
    <!-- TEAM OPERATIONS VIEW (Management Center)   -->
    <!-- ========================================== -->
    <template v-else>
      <!-- KPI Status Grid -->
      <section class="team-kpi-grid">
        <div class="kpi-card" :class="{ alert: overdueTasksCount > 0 }">
          <span class="kpi-num">{{ overdueTasksCount }}</span>
          <span class="kpi-label">Überfällige Tasks</span>
        </div>
        <div class="kpi-card" :class="{ warn: pendingReviews.length > 0 }">
          <span class="kpi-num">{{ pendingReviews.length }}</span>
          <span class="kpi-label">Offene Reviews</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-num">{{ requests.length }}</span>
          <span class="kpi-label">Collab Requests</span>
        </div>
        <div class="kpi-card">
          <span class="kpi-num">{{ projects.length }}</span>
          <span class="kpi-label">Aktive Projekte</span>
        </div>
      </section>

      <!-- Alles OK Banner -->
      <section class="team-banner ok-banner" v-if="!loading && totalAttentionCount === 0">
        <span class="ok-check">✓</span>
        <div>
          <strong>Alles im grünen Bereich</strong>
          <p class="muted">Keine überfälligen Tasks, offenen Reviews oder ausstehenden Requests.</p>
        </div>
        <button class="btn ghost" type="button" @click="goTo('tasks')">Task Board →</button>
      </section>

      <!-- Handlungsbedarf -->
      <section class="team-section" v-if="totalAttentionCount">
        <div class="section-head">
          <h2>Braucht deine Aufmerksamkeit <span class="count-badge">{{ totalAttentionCount }}</span></h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Task Board →</button>
        </div>
        <p class="attention-hint">Du hast {{ totalAttentionCount }} Punkte, die deine Aufmerksamkeit brauchen!</p>
        <ul class="item-list">
          <li v-for="item in urgentItems" :key="item.key" :data-urgency="item.urgency">
            <div class="item-body">
              <span class="cat-tag" :data-cat="item.cat">{{ item.catLabel }}</span>
              <strong class="item-title">{{ item.title }}</strong>
              <span class="item-sub">{{ item.sub }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="item.tone">{{ item.toneLabel }}</span>
              <button
                v-for="action in item.actions"
                :key="action.text"
                :class="['btn', 'tiny', action.ghost !== false ? 'ghost' : '', action.danger ? 'danger' : '']"
                type="button"
                @click="action.fn()"
                :disabled="action.disabled"
              >{{ action.text }}</button>
            </div>
          </li>
        </ul>
      </section>

      <!-- Diese Woche fällig -->
      <section class="team-section" v-if="thisWeekItems.length">
        <div class="section-head">
          <h2>Diese Woche fällig</h2>
          <button class="btn ghost tiny" type="button" @click="goTo('tasks')">Alle Tasks →</button>
        </div>
        <ul class="item-list compact">
          <li v-for="item in thisWeekItems" :key="item.key">
            <div class="item-body">
              <strong class="item-title">{{ item.title }}</strong>
              <span class="item-sub">{{ item.sub }}</span>
            </div>
            <div class="item-actions">
              <span class="badge" :data-tone="item.tone">{{ item.dateLabel }}</span>
              <button class="btn ghost tiny" type="button" @click="goToRoute(item.route)">Öffnen</button>
            </div>
          </li>
        </ul>
      </section>

      <!-- Team Invite Box -->
      <section class="team-section team-invite-card">
        <div class="section-head">
          <h2>Artist &amp; Team Onboarding</h2>
          <button class="btn" @click="openUserModal">+ Benutzer einladen</button>
        </div>
        <p class="muted">Lade neue Künstler, Producer oder Team-Mitglieder per E-Mail oder Einladungslink ein.</p>
      </section>
    </template>

    <!-- ========================================== -->
    <!-- INTERACTIVE MODALS                         -->
    <!-- ========================================== -->

    <!-- Modal 1: Create Song Modal -->
    <div v-if="songModalOpen" class="modal-backdrop" @click.self="songModalOpen = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Neuen Song / Beat anlegen</h3>
          <button class="btn ghost tiny" @click="songModalOpen = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitCreateSong">
          <label>
            <span>Titel *</span>
            <input class="input" v-model.trim="songForm.title" placeholder="z. B. Midnight Drive, Summer Nights..." required />
          </label>
          <div class="form-row-2">
            <label>
              <span>Genre</span>
              <input class="input" v-model.trim="songForm.genre" placeholder="z. B. Trap, R&amp;B, Drill, Pop" />
            </label>
            <label>
              <span>BPM</span>
              <input class="input" type="number" v-model.number="songForm.bpm" placeholder="z. B. 140" />
            </label>
          </div>
          <label>
            <span>Status</span>
            <select class="input" v-model="songForm.status">
              <option value="ACTIVE">In Produktion (Active)</option>
              <option value="DRAFT">Demo / Skizze (Draft)</option>
              <option value="ON_HOLD">Pausiert</option>
              <option value="RELEASED">Fertiggestellt / Release</option>
            </select>
          </label>
          <label>
            <span>Beschreibung / Notizen</span>
            <textarea class="input" rows="2" v-model.trim="songForm.description" placeholder="Referenzen, Mood, Besetzung..."></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="songModalOpen = false" :disabled="songSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="songSaving">
              {{ songSaving ? 'Speichere...' : 'Track anlegen 🚀' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 2: Create Task Modal -->
    <div v-if="taskModalOpen" class="modal-backdrop" @click.self="closeTaskModal">
      <div class="modal card">
        <div class="modal-header">
          <h3>Task erstellen</h3>
          <button class="btn ghost tiny" @click="closeTaskModal">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitTask">
          <label>
            <span>Titel *</span>
            <input class="input" v-model.trim="taskForm.title" placeholder="z. B. Vocal Tuning abschließen, Cover Art wählen..." required />
          </label>
          <label>
            <span>Projekt (optional)</span>
            <select class="input" v-model="taskForm.projectId">
              <option value="">Kein Projekt</option>
              <option v-for="project in projectOptions" :key="project.id" :value="project.id">{{ project.title }}</option>
            </select>
          </label>
          <div class="form-row-2">
            <label>
              <span>Fälligkeitsdatum</span>
              <input class="input" type="date" v-model="taskForm.dueDate" />
            </label>
            <label>
              <span>Priorität</span>
              <select class="input" v-model="taskForm.priority">
                <option v-for="opt in taskPriorityOptions" :key="opt" :value="opt">{{ priorityMap[opt] }}</option>
              </select>
            </label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeTaskModal" :disabled="taskSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="taskSaving">{{ taskSaving ? "Speichere..." : "Task anlegen" }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Modal 3: Invite User Modal -->
    <div v-if="userModalOpen" class="modal-backdrop" @click.self="closeUserModal">
      <div class="modal card">
        <div class="modal-header">
          <h3>Benutzer einladen</h3>
          <button class="btn ghost tiny" @click="closeUserModal">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitUserInvite">
          <label>
            <span>E-Mail *</span>
            <input class="input" type="email" v-model.trim="userForm.email" placeholder="artist@example.com" required />
          </label>
          <label>
            <span>Name (optional)</span>
            <input class="input" v-model.trim="userForm.name" placeholder="z. B. David Beats" />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="closeUserModal" :disabled="userSaving">Abbrechen</button>
            <button class="btn" type="submit" :disabled="userSaving">{{ userSaving ? "Sende..." : "Einladen" }}</button>
          </div>
        </form>
        <div v-if="inviteLink" class="invite-link-box">
          <input class="input" readonly :value="inviteLink" />
          <button class="btn ghost tiny" type="button" @click="copyInviteLink">Kopieren</button>
        </div>
    <!-- Modal 4: Protected Stage Change Confirmation Modal -->
    <div v-if="stageConfirmData" class="modal-backdrop" @click.self="stageConfirmData = null">
      <div class="modal card" style="max-width: 440px;">
        <div class="modal-header">
          <h3>🔒 Release-Phase ändern</h3>
          <button class="btn ghost tiny" @click="stageConfirmData = null">✕</button>
        </div>
        <div class="modal-body" style="padding: 16px 0;">
          <p style="margin-bottom: 12px;">
            Möchtest du den Track <strong>„{{ stageConfirmData.song.title }}“</strong> wirklich in eine neue Phase verschieben?
          </p>
          <div class="stage-transition-preview" style="background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
            <div>
              <small class="muted" style="display:block;">Aktuelle Phase:</small>
              <strong>{{ releaseStages[getSongStageIndex(stageConfirmData.song)]?.label }}</strong>
            </div>
            <span style="font-size: 1.2rem; color: #818cf8;">➔</span>
            <div>
              <small class="muted" style="display:block;">Neue Ziel-Phase:</small>
              <strong style="color: #4ade80;">{{ releaseStages[stageConfirmData.targetIdx]?.label }}</strong>
            </div>
          </div>
          <p class="muted tiny" style="margin: 0; line-height: 1.4;">
            ℹ️ Phasenwechsel sind geschützt, damit kein Release-Schritt (Mixdown, Master, Cover, Promoplan) versehentlich übersprungen wird.
          </p>
        </div>
        <div class="modal-actions" style="margin-top: 14px;">
          <button class="btn ghost" type="button" @click="stageConfirmData = null">Abbrechen</button>
          <button class="btn" type="button" @click="applyConfirmedStage">Bestätigen &amp; Phase setzen</button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import api from "../api";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import { useGlobalAudio } from "../composables/useGlobalAudio";

const router = useRouter();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();
const { playTrack, currentTrack, isPlaying } = useGlobalAudio();

const loading = ref(false);
const viewMode = ref(localStorage.getItem("proartist:view_mode") || (isTeam.value ? "admin" : "creator"));

function setViewMode(mode) {
  viewMode.value = mode;
  localStorage.setItem("proartist:view_mode", mode);
}

// Data Collections
const tasks = ref([]);
const reviewTasks = ref([]);
const pendingReviews = ref([]);
const requests = ref([]);
const growpro = ref([]);
const projects = ref([]);
const songs = ref([]);
const tournaments = ref([]);
const examples = ref([]);
const reviewSaving = ref({});

// Modals
const taskModalOpen = ref(false);
const taskSaving = ref(false);
const taskForm = ref({ title: "", projectId: "", dueDate: "", priority: "MEDIUM" });
const projectOptions = ref([]);

const songModalOpen = ref(false);
const songSaving = ref(false);
const songForm = ref({ title: "", genre: "", bpm: null, status: "ACTIVE", description: "" });

const quickTaskTitle = ref("");
const quickTaskSaving = ref(false);

const userModalOpen = ref(false);
const userSaving = ref(false);
const userForm = ref({ email: "", name: "" });
const inviteLink = ref("");

// Audio Preview via Global Player
const currentPlayingSongId = computed(() => isPlaying.value ? currentTrack.value?.id : null);

const taskPriorityOptions = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];
const priorityMap = { LOW: "Niedrig", MEDIUM: "Mittel", HIGH: "Hoch", CRITICAL: "Kritisch" };
const requestTypes = { COLLAB: "Collab-Anfrage", BOOK: "Booking-Anfrage", OTHER: "Anfrage" };

// 5 Protected Release Stages (Real-world workflow: Mixdown -> Master -> Cover -> Promoplan -> Release)
const releaseStages = [
  { key: "mixdown", label: "Mixdown & Stems" },
  { key: "mastering", label: "Mastering Final" },
  { key: "cover", label: "Cover & Artwork" },
  { key: "promoplan", label: "Promoplan & Teaser" },
  { key: "released", label: "Release Ready" },
];

const stageConfirmData = ref(null);
const localSongStages = ref({});

function getSongStageIndex(song) {
  if (localSongStages.value[song.id] !== undefined) {
    return localSongStages.value[song.id];
  }
  const saved = localStorage.getItem(`unyq_song_stage_${song.id}`);
  if (saved !== null) {
    const parsed = parseInt(saved, 10);
    if (!isNaN(parsed) && parsed >= 0 && parsed < releaseStages.length) {
      localSongStages.value[song.id] = parsed;
      return parsed;
    }
  }
  if (song.status === "RELEASED") return 4;
  if (song.version_count >= 3) return 1; // Mastering
  if (song.version_count >= 2) return 0; // Mixdown
  return 0;
}

function confirmChangeStage(song, targetIdx) {
  const currentIdx = getSongStageIndex(song);
  if (currentIdx === targetIdx) return;
  stageConfirmData.value = { song, targetIdx };
}

function applyConfirmedStage() {
  if (!stageConfirmData.value) return;
  const { song, targetIdx } = stageConfirmData.value;
  localSongStages.value[song.id] = targetIdx;
  localStorage.setItem(`unyq_song_stage_${song.id}`, String(targetIdx));
  showToast(`Release-Phase für "${song.title}" auf "${releaseStages[targetIdx].label}" aktualisiert`, "success");
  stageConfirmData.value = null;
}

// Greetings
const greeting = computed(() => {
  const h = new Date().getHours();
  if (h < 11) return "Guten Morgen";
  if (h < 18) return "Guten Tag";
  return "Guten Abend";
});

const displayName = computed(() => (me.value?.name || me.value?.username || "").trim().split(" ")[0] || "");

// Sublines
const currentHeroSubline = computed(() => {
  if (viewMode.value === "creator") {
    const songCount = songsList.value.length;
    const taskCount = myActiveTasks.value.length;
    const tournCount = activeTournaments.value.length;
    return `Studio bereit · ${songCount} ${songCount === 1 ? 'Track' : 'Tracks'} in Arbeit · ${taskCount} offene ${taskCount === 1 ? 'Aufgabe' : 'Aufgaben'} · ${tournCount} ${tournCount === 1 ? 'Turnier' : 'Turniere'} aktiv`;
  }
  return heroSublineTeam.value;
});

const heroSublineTeam = computed(() => {
  const overdue = tasks.value.filter(t => dueState(t.due_date) === "overdue").length;
  const reviewCount = new Set([...reviewTasks.value, ...pendingReviews.value].map(t => t.id)).size;
  const reqCount = requests.value.length;
  const parts = [];
  if (overdue > 0) parts.push(`${overdue} Task${overdue > 1 ? "s" : ""} überfällig`);
  if (reviewCount > 0) parts.push(`${reviewCount} warten auf Review`);
  if (reqCount > 0) parts.push(`${reqCount} offene${reqCount !== 1 ? "" : "r"} Request`);
  return parts.length ? parts.join(" · ") : "Alles im grünen Bereich. System läuft stabil!";
});

const heroHasIssues = computed(() => {
  return tasks.value.some(t => dueState(t.due_date) === "overdue") ||
    pendingReviews.value.length > 0 ||
    requests.value.length > 0 ||
    growproAttentionItems.value.length > 0;
});

const totalAttentionCount = computed(() => urgentItems.value.length + growproAttentionItems.value.length);
const overdueTasksCount = computed(() => tasks.value.filter(t => dueState(t.due_date) === "overdue").length);

// Songs
const songsList = computed(() => {
  if (songs.value.length) return songs.value;
  // Curated demo entries if brand new account to showcase the experience immediately
  return [
    {
      id: "demo-1",
      title: "Midnight Drive in Berlin",
      genre: "Trap / Drill",
      bpm: 142,
      status: "ACTIVE",
      description: "Atmosphärischer 808 Beat mit Vocals. Mixdown in Vorbereitung.",
      version_count: 3,
      cover_url: null,
    },
    {
      id: "demo-2",
      title: "Golden Hour Waves",
      genre: "Neo R&B",
      bpm: 96,
      status: "DRAFT",
      description: "Rhodes Piano Akkorde und smoothe Drums. Feature gesucht.",
      version_count: 1,
      cover_url: null,
    },
  ];
});

function getSongStageIndex(song) {
  if (song.status === "RELEASED") return 4;
  if (song.version_count >= 3) return 2; // Mixdown
  if (song.version_count >= 2) return 1; // Recording
  return 0; // Idee
}

function songStatusLabel(st) {
  const map = { ACTIVE: "In Produktion", DRAFT: "Entwurf", RELEASED: "Release Ready", ON_HOLD: "Pausiert" };
  return map[st] || st;
}

// Tasks for artist
const myActiveTasks = computed(() => {
  return tasks.value.filter(t => t.status !== "DONE");
});

// Active Tournaments
const activeTournaments = computed(() => {
  if (tournaments.value.length) return tournaments.value;
  return [
    {
      id: 1,
      title: "UNYQ Beat Clash Season 1",
      prize_pool: "500 € Cash & Release",
      status: "BATTLES",
    },
    {
      id: 2,
      title: "Topline & Vocal Contest",
      prize_pool: "Studio Session & Mastering",
      status: "APPLICATION_OPEN",
    },
  ];
});

function tournamentStatusLabel(st) {
  const map = {
    APPLICATION_OPEN: "Bewerbung offen",
    SUBMISSION_OPEN: "Einreichung offen",
    BATTLES: "Live Battles",
    COMPLETED: "Beendet",
  };
  return map[st] || st;
}

// Gamification & Streaks
const studioStreakDays = ref(5);
const artistLevel = ref(3);
const artistPoints = ref(480);
const artistLevelProgress = ref(68);

// Urgent Items (Team)
const urgentItems = computed(() => {
  const items = [];

  // Overdue tasks
  tasks.value
    .filter(t => dueState(t.due_date) === "overdue")
    .slice(0, 6)
    .forEach(task => {
      items.push({
        key: `overdue-${task.id}`,
        cat: "overdue",
        catLabel: "Überfällig",
        urgency: "high",
        title: task.title,
        sub: task.project_title || "Kein Projekt",
        tone: "overdue",
        toneLabel: formatDate(task.due_date),
        actions: [{ text: "Öffnen", ghost: true, fn: () => openTask(task) }],
      });
    });

  // Review Tasks
  const reviewSet = new Map();
  [...reviewTasks.value, ...pendingReviews.value].forEach(t => {
    if (!reviewSet.has(t.id)) reviewSet.set(t.id, t);
  });
  [...reviewSet.values()].slice(0, 5).forEach(task => {
    items.push({
      key: `review-${task.id}`,
      cat: "review",
      catLabel: "Review",
      urgency: "medium",
      title: task.title,
      sub: task.project_title || "Kein Projekt",
      tone: "soon",
      toneLabel: "Warten auf Freigabe",
      actions: [
        { text: "Öffnen", ghost: true, fn: () => openTask(task) },
        {
          text: reviewSaving.value[task.id] ? "..." : "Als geprüft markieren",
          ghost: false,
          fn: () => markReviewed(task),
          disabled: !!reviewSaving.value[task.id],
        },
      ],
    });
  });

  // Requests
  requests.value.slice(0, 4).forEach(req => {
    items.push({
      key: `req-${req.id}`,
      cat: "request",
      catLabel: "Request",
      urgency: "low",
      title: requestTypes[req.req_type] || "Anfrage",
      sub: `${req.sender_name || 'Artist'} → ${req.receiver_name || 'Team'}`,
      tone: "info",
      toneLabel: "Offen",
      actions: [
        { text: "Annehmen", ghost: false, fn: () => respondRequest(req.id, "accept") },
        { text: "Ablehnen", ghost: true, danger: true, fn: () => respondRequest(req.id, "decline") },
      ],
    });
  });

  return items;
});

// This week items
const thisWeekItems = computed(() => {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const in7 = new Date(today); in7.setDate(today.getDate() + 7);

  return tasks.value
    .filter(t => {
      const d = parseDate(t.due_date);
      return d && d >= today && d <= in7;
    })
    .sort((a, b) => parseDate(a.due_date) - parseDate(b.due_date))
    .slice(0, 8)
    .map(t => ({
      key: `week-${t.id}`,
      title: t.title,
      sub: t.project_title || "Kein Projekt",
      tone: dueState(t.due_date),
      dateLabel: formatDate(t.due_date),
      route: t.project
        ? { name: "project-detail", params: { projectId: t.project }, query: { taskId: t.id } }
        : { name: "tasks", query: { taskId: t.id } },
    }));
});

const growproAttentionItems = computed(() =>
  growpro.value
    .filter(g => isGrowproStale(g) || ["overdue", "soon"].includes(dueState(g.due_date)))
    .slice(0, 6)
);

// Helpers
function normalizeList(payload) {
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.results)) return payload.results;
  return [];
}

function parseDate(value) {
  const d = value ? new Date(value) : null;
  return d && !Number.isNaN(d.getTime()) ? d : null;
}

function formatDate(value) {
  const d = parseDate(value);
  if (!d) return "-";
  return new Intl.DateTimeFormat("de-DE", { day: "2-digit", month: "2-digit", year: "numeric" }).format(d);
}

function dueState(value) {
  const d = parseDate(value);
  if (!d) return "none";
  const start = new Date(); start.setHours(0, 0, 0, 0);
  const target = new Date(d); target.setHours(0, 0, 0, 0);
  const diff = Math.round((target - start) / 86400000);
  if (diff < 0) return "overdue";
  if (diff <= 2) return "soon";
  return "ok";
}

function dueLabel(value) {
  if (!value) return "Kein Termin";
  const state = dueState(value);
  if (state === "overdue") return "Überfällig";
  if (state === "soon") return "Bald fällig";
  return formatDate(value);
}

function isGrowproStale(goal) {
  const d = parseDate(goal?.last_logged_at || goal?.created_at);
  if (!d) return false;
  return (Date.now() - d.getTime()) > 7 * 24 * 3600 * 1000;
}

function goTo(routeName) {
  router.push({ name: routeName });
}

function goToRoute(routeObj) {
  router.push(routeObj);
}

function getTaskRoute(task) {
  if (task.project) {
    return { name: "project-detail", params: { projectId: task.project }, query: { taskId: task.id } };
  }
  return { name: "tasks", query: { taskId: task.id } };
}

function openTask(task) {
  goToRoute(getTaskRoute(task));
}

// Audio Preview Handler (Uses Global Audio Player)
function togglePlayAudio(song) {
  const audioSrc = song.audio_url || "https://assets.mixkit.co/music/preview/mixkit-tech-house-vibes-130.mp3";
  playTrack({
    id: song.id,
    title: song.title,
    artist: displayName.value || "UNYQ Artist",
    cover_url: song.cover_url || "",
    audio_url: audioSrc,
  });
}

// Data Fetching
async function refresh() {
  if (loading.value) return;
  loading.value = true;
  try {
    await fetchProfile(true);

    const [tasksRes, songsRes, tournsRes, projectsRes, gpRes, reqRes, reviewRes, pendingRes] = await Promise.all([
      api.get("tasks/", { params: { include_archived: 0, page_size: 100 } }).catch(() => ({ data: [] })),
      api.get("songs/", { params: { page_size: 20, ordering: "-created_at" } }).catch(() => ({ data: [] })),
      api.get("tournaments/").catch(() => ({ data: [] })),
      api.get("projects/", { params: { include_archived: 0, page_size: 50 } }).catch(() => ({ data: [] })),
      api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } }).catch(() => ({ data: [] })),
      api.get("requests/team-open/").catch(() => ({ data: [] })),
      api.get("tasks/", { params: { status: "REVIEW", page_size: 50 } }).catch(() => ({ data: [] })),
      api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", page_size: 50 } }).catch(() => ({ data: [] })),
    ]);

    tasks.value = normalizeList(tasksRes.data);
    songs.value = normalizeList(songsRes.data);
    tournaments.value = normalizeList(tournsRes.data);
    projects.value = normalizeList(projectsRes.data);
    growpro.value = normalizeList(gpRes.data);
    requests.value = normalizeList(reqRes.data);
    reviewTasks.value = normalizeList(reviewRes.data);
    pendingReviews.value = normalizeList(pendingRes.data);
  } finally {
    loading.value = false;
  }
}

onMounted(refresh);

// Actions
async function toggleTaskDone(task) {
  const newStatus = task.status === "DONE" ? "OPEN" : "DONE";
  task.status = newStatus;
  try {
    await api.patch(`tasks/${task.id}/`, { status: newStatus });
    showToast(newStatus === "DONE" ? "Task erledigt! 🎉" : "Task wieder geöffnet", "success");
  } catch {
    showToast("Konnte Status nicht aktualisieren", "error");
    task.status = newStatus === "DONE" ? "OPEN" : "DONE";
  }
}

async function submitQuickTask() {
  if (!quickTaskTitle.value.trim()) return;
  quickTaskSaving.value = true;
  try {
    const { data } = await api.post("tasks/", {
      title: quickTaskTitle.value.trim(),
      status: "OPEN",
      priority: "MEDIUM",
      task_type: "EXTERNAL",
    });
    tasks.value.unshift(data);
    quickTaskTitle.value = "";
    showToast("Aufgabe hinzugefügt", "success");
  } catch {
    showToast("Aufgabe konnte nicht erstellt werden", "error");
  } finally {
    quickTaskSaving.value = false;
  }
}

async function markReviewed(task) {
  if (!task?.id) return;
  reviewSaving.value = { ...reviewSaving.value, [task.id]: true };
  try {
    await api.patch(`tasks/${task.id}/`, { status: "DONE", review_status: "REVIEWED" });
    showToast("Review freigegeben", "success");
    await refresh();
  } catch {
    showToast("Review konnte nicht gespeichert werden", "error");
  } finally {
    reviewSaving.value = { ...reviewSaving.value, [task.id]: false };
  }
}

async function respondRequest(id, action) {
  try {
    await api.post(`requests/${id}/${action === "accept" ? "accept" : "decline"}/`);
    showToast(action === "accept" ? "Request angenommen" : "Request abgelehnt", "success");
    await refresh();
  } catch {
    showToast("Aktion fehlgeschlagen", "error");
  }
}

// Modals
function openSongModal() {
  songForm.value = { title: "", genre: "", bpm: null, status: "ACTIVE", description: "" };
  songModalOpen.value = true;
}

async function submitCreateSong() {
  if (!songForm.value.title.trim()) return;
  songSaving.value = true;
  try {
    const fd = new FormData();
    fd.append("title", songForm.value.title.trim());
    if (songForm.value.genre) fd.append("genre", songForm.value.genre.trim());
    if (songForm.value.bpm) fd.append("bpm", songForm.value.bpm);
    if (songForm.value.status) fd.append("status", songForm.value.status);
    if (songForm.value.description) fd.append("description", songForm.value.description.trim());

    const { data } = await api.post("songs/", fd, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    songs.value.unshift(data);
    songModalOpen.value = false;
    showToast("Song angelegt! 🚀", "success");
  } catch (err) {
    showToast(err?.response?.data?.detail || "Fehler beim Erstellen des Songs", "error");
  } finally {
    songSaving.value = false;
  }
}

function openTaskModal() {
  taskForm.value = { title: "", projectId: "", dueDate: "", priority: "MEDIUM" };
  taskModalOpen.value = true;
  api.get("projects/", { params: { include_archived: 0, include_done: 0, page_size: 100 } })
    .then(({ data }) => { projectOptions.value = normalizeList(data).map(p => ({ id: p.id, title: p.title })); })
    .catch(() => { projectOptions.value = []; });
}

function closeTaskModal() {
  if (!taskSaving.value) taskModalOpen.value = false;
}

async function submitTask() {
  if (!taskForm.value.title.trim()) return;
  taskSaving.value = true;
  try {
    const payload = {
      title: taskForm.value.title.trim(),
      status: "OPEN",
      priority: taskForm.value.priority,
      task_type: "EXTERNAL",
      due_date: taskForm.value.dueDate || null,
    };
    if (taskForm.value.projectId) payload.project = Number(taskForm.value.projectId);
    const { data } = await api.post("tasks/", payload);
    tasks.value.unshift(data);
    showToast("Task erstellt", "success");
    taskModalOpen.value = false;
  } catch {
    showToast("Task konnte nicht erstellt werden", "error");
  } finally {
    taskSaving.value = false;
  }
}

function openUserModal() {
  userForm.value = { email: "", name: "" };
  inviteLink.value = "";
  userModalOpen.value = true;
}

function closeUserModal() {
  if (!userSaving.value) userModalOpen.value = false;
}

async function submitUserInvite() {
  if (!userForm.value.email.trim()) return;
  userSaving.value = true;
  try {
    const { data } = await api.post("invite/", {
      email: userForm.value.email.trim(),
      name: userForm.value.name.trim(),
    });
    inviteLink.value = data?.invite_url || data?.link || "Einladung erfolgreich verschickt!";
    showToast("Einladung verschickt", "success");
  } catch {
    showToast("Einladung konnte nicht gesendet werden", "error");
  } finally {
    userSaving.value = false;
  }
}

function copyInviteLink() {
  if (!inviteLink.value) return;
  navigator.clipboard.writeText(inviteLink.value);
  showToast("Link in Zwischenablage kopiert", "success");
}
</script>

<style scoped>
.proartist-dashboard {
  position: relative;
  display: flex;
  flex-direction: column;
  max-width: 1260px;
  margin: 0 auto 40px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(14px);
  overflow: hidden;
}

:global(.dark) .proartist-dashboard {
  background: linear-gradient(180deg, rgba(16, 23, 42, 0.94) 0%, rgba(11, 16, 29, 0.98) 100%);
  border: 1px solid rgba(148, 163, 184, 0.16);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.45);
}

.studio-ambient-glow {
  position: absolute;
  top: -80px;
  left: 20%;
  width: 60%;
  height: 280px;
  background: radial-gradient(circle, rgba(59, 130, 246, 0.14) 0%, rgba(139, 92, 246, 0.08) 50%, transparent 80%);
  pointer-events: none;
  z-index: 0;
  filter: blur(40px);
}

/* Studio Hero Header */
.studio-hero {
  position: relative;
  z-index: 1;
  padding: 24px 28px 20px;
  background: transparent;
  border-bottom: 1px solid var(--border);
}

:global(.dark) .studio-hero {
  background: rgba(255, 255, 255, 0.015);
  border-bottom: 1px solid rgba(255, 255, 255, 0.07);
}

.hero-main-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 24px;
  flex-wrap: wrap;
}

.hero-copy {
  flex: 1;
  min-width: 300px;
}

/* Mode Switcher */
.mode-switcher-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 14px;
  flex-wrap: wrap;
}

.mode-pill-toggle {
  display: inline-flex;
  background: rgba(255, 255, 255, 0.05);
  padding: 4px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.mode-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 999px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.mode-btn.active {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.35);
}

.hero-headline {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 8px 0;
}

.hero-subline {
  font-size: 13.5px;
  color: var(--muted);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}

.hero-subline.has-issues {
  color: #fca5a5;
}

/* Hero Actions Dock */
.hero-actions-dock {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #6366f1);
  color: #fff;
  border: none;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5);
}

.arena-shortcut-btn {
  position: relative;
  border-color: rgba(245, 158, 11, 0.3);
}

.dock-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 8px #ef4444;
  animation: pulse 1.8s infinite;
}

.icon-refresh-btn {
  padding: 8px 12px;
}

.spinning {
  display: inline-block;
  animation: spin 1s infinite linear;
}

@keyframes spin {
  100% { transform: rotate(360deg); }
}

/* Sections */
.studio-section {
  position: relative;
  z-index: 1;
  padding: 26px 28px;
  background: transparent;
  border-bottom: 1px solid var(--border);
}

:global(.dark) .studio-section {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-icon {
  font-size: 26px;
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: rgba(59, 130, 246, 0.12);
  border: 1px solid rgba(59, 130, 246, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 2px 0;
}

/* Pipeline Grid */
.pipeline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.pipeline-card {
  padding: 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  transition: all 0.25s ease;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pipeline-card:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(59, 130, 246, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
}

.track-head {
  display: flex;
  gap: 12px;
  align-items: center;
}

.cover-wrapper {
  position: relative;
  width: 58px;
  height: 58px;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  flex-shrink: 0;
}

.track-cover-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.track-cover-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.cover-play-btn {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  border: none;
  color: #fff;
  font-size: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
  cursor: pointer;
}

.cover-wrapper:hover .cover-play-btn,
.cover-play-btn.playing {
  opacity: 1;
}

.track-meta {
  flex: 1;
  overflow: hidden;
}

.meta-row-top {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 4px;
  flex-wrap: wrap;
}

.status-pill {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 7px;
  border-radius: 6px;
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
}

.status-pill[data-status="RELEASED"] {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
}

.tag-mini {
  font-size: 9.5px;
  padding: 1px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.tag-mini.bpm {
  font-weight: 700;
  color: #f59e0b;
}

.track-title {
  font-size: 14.5px;
  font-weight: 700;
  margin: 0 0 2px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
}

.track-title:hover {
  color: #60a5fa;
}

.track-desc {
  font-size: 11.5px;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 5-Stage Release Bar */
.stage-pipeline-bar {
  display: flex;
  justify-content: space-between;
  position: relative;
  padding: 8px 0 2px;
}

.stage-pipeline-bar::before {
  content: "";
  position: absolute;
  top: 17px;
  left: 12px;
  right: 12px;
  height: 2px;
  background: rgba(255, 255, 255, 0.08);
  z-index: 0;
}

.stage-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  position: relative;
  z-index: 1;
}

.step-dot {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #1e2433;
  border: 1.5px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: var(--muted);
}

.stage-step.active .step-dot {
  background: #3b82f6;
  border-color: #60a5fa;
  color: #fff;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
}

.stage-step.completed .step-dot {
  background: #10b981;
  border-color: #34d399;
  color: #fff;
}

.step-label {
  font-size: 9px;
  color: var(--muted);
  text-align: center;
}

.stage-step.active .step-label {
  color: #93c5fd;
  font-weight: 700;
}

.stage-step.clickable {
  cursor: pointer;
  transition: transform 0.15s ease;
}

.stage-step.clickable:hover .step-dot {
  transform: scale(1.15);
  border-color: #818cf8;
}

.step-lock-tag {
  font-size: 8px;
  position: absolute;
  top: -6px;
  right: -4px;
}

.track-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.version-badge {
  font-size: 11px;
  color: var(--muted);
}

.link-btn {
  font-size: 11px;
}

/* Empty Pipeline Box */
.empty-pipeline-box {
  padding: 40px 20px;
  text-align: center;
  background: rgba(255, 255, 255, 0.02);
  border-radius: 14px;
  border: 1px dashed rgba(255, 255, 255, 0.1);
}

.empty-icon-ring {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: rgba(59, 130, 246, 0.15);
  font-size: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 14px;
}

.empty-pipeline-box h3 {
  font-size: 18px;
  margin: 0 0 6px 0;
}

.empty-pipeline-box p {
  max-width: 480px;
  margin: 0 auto 18px;
  font-size: 13.5px;
}

.empty-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

/* Duo Grids */
.dashboard-duo-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(420px, 1fr));
  gap: 20px;
  padding: 26px 28px;
  border-bottom: 1px solid var(--border);
}

:global(.dark) .dashboard-duo-grid {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.dashboard-duo-grid:last-of-type {
  border-bottom: none;
}

.duo-panel {
  position: relative;
  z-index: 1;
  padding: 22px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.04);
}

:global(.dark) .duo-panel {
  background: rgba(255, 255, 255, 0.025);
  border: 1px solid rgba(255, 255, 255, 0.06);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
}

/* Studio Focus Tasks */
.quick-add-task-form {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.quick-task-input {
  flex: 1;
  font-size: 13px;
}

.studio-task-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.studio-task-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s ease;
}

.studio-task-item:hover {
  background: rgba(255, 255, 255, 0.05);
}

.task-check-label {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.task-check-label input {
  display: none;
}

.custom-checkbox {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.task-check-label input:checked + .custom-checkbox {
  background: #10b981;
  border-color: #10b981;
}

.task-check-label input:checked + .custom-checkbox::after {
  content: "✓";
  color: #fff;
  font-size: 11px;
  font-weight: 800;
}

.task-content {
  flex: 1;
  overflow: hidden;
}

.task-title {
  font-size: 13.5px;
  display: block;
}

.task-title.strike {
  text-decoration: line-through;
  opacity: 0.5;
}

.task-tags {
  display: flex;
  gap: 6px;
  margin-top: 3px;
  font-size: 10.5px;
}

.task-proj-pill {
  color: var(--muted);
}

.task-prio-pill {
  font-weight: 600;
  color: #93c5fd;
}

.task-prio-pill[data-priority="HIGH"] {
  color: #f59e0b;
}

.task-prio-pill[data-priority="CRITICAL"] {
  color: #ef4444;
}

.task-due-pill {
  color: var(--muted);
}

.task-due-pill[data-tone="overdue"] {
  color: #ef4444;
  font-weight: 700;
}

/* Arena Spotlight Card */
.arena-tournaments-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.arena-mini-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(239, 68, 68, 0.05));
  border: 1px solid rgba(245, 158, 11, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
}

.arena-mini-card:hover {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(239, 68, 68, 0.1));
  border-color: rgba(245, 158, 11, 0.3);
  transform: translateY(-1px);
}

.am-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.am-pulse-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: #ef4444;
  box-shadow: 0 0 6px #ef4444;
}

.am-meta {
  display: flex;
  gap: 10px;
  margin-top: 4px;
  font-size: 11.5px;
}

.prize-tag {
  color: #fbbf24;
  font-weight: 700;
}

.status-tag {
  color: var(--muted);
}

.action-arena-btn {
  font-size: 12px;
  background: rgba(245, 158, 11, 0.15);
  border: 1px solid rgba(245, 158, 11, 0.3);
  color: #fbbf24;
}

/* Streak & XP Banner */
.streak-xp-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 16px;
  gap: 16px;
}

.streak-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.streak-flame {
  font-size: 26px;
}

.xp-box {
  flex: 1;
  max-width: 200px;
}

.xp-head {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  margin-bottom: 4px;
}

.xp-level {
  font-weight: 700;
  color: #a78bfa;
}

.xp-bar-track {
  width: 100%;
  height: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  overflow: hidden;
}

.xp-bar-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
}

.growpro-mini-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.growpro-mini-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
}

/* Toolbox Grid */
.toolbox-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.toolbox-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbox-item:hover {
  background: rgba(59, 130, 246, 0.1);
  border-color: rgba(59, 130, 246, 0.25);
  transform: translateY(-1px);
}

.tb-icon {
  font-size: 22px;
}

.tb-info {
  flex: 1;
}

.tb-info strong {
  font-size: 13px;
  display: block;
}

.tb-arrow {
  color: var(--muted);
  font-size: 14px;
}

/* Team KPI Grid */
.team-kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
  padding: 24px 28px;
  border-bottom: 1px solid var(--border);
}

:global(.dark) .team-kpi-grid {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.team-section {
  padding: 26px 28px;
  border-bottom: 1px solid var(--border);
  background: transparent;
}

:global(.dark) .team-section {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.team-section:last-of-type {
  border-bottom: none;
}

.team-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 28px;
  border-bottom: 1px solid var(--border);
  background: rgba(16, 185, 129, 0.08);
}

.kpi-card {
  padding: 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.kpi-card.alert {
  background: rgba(239, 68, 68, 0.08);
  border-color: rgba(239, 68, 68, 0.25);
}

.kpi-card.warn {
  background: rgba(245, 158, 11, 0.08);
  border-color: rgba(245, 158, 11, 0.25);
}

.kpi-num {
  font-size: 26px;
  font-weight: 800;
}

.kpi-label {
  font-size: 12px;
  color: var(--muted);
}

/* Modals */
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(8px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal {
  width: 100%;
  max-width: 520px;
  padding: 24px;
  border-radius: 18px;
  background: #151926;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 20px 48px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.modal-header h3 {
  font-size: 18px;
  margin: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.modal-form label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 600;
}

.form-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.invite-link-box {
  display: flex;
  gap: 8px;
  margin-top: 14px;
}

@media (max-width: 768px) {
  .dashboard-duo-grid {
    grid-template-columns: 1fr;
  }
  .toolbox-grid {
    grid-template-columns: 1fr;
  }
  .hero-main-row {
    flex-direction: column;
  }
}
</style>
