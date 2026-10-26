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
          <button class="btn btn-primary" type="button" @click="goTo('promo-queue')">
            <span class="btn-icon">🚀</span>
            <span>+ Release</span>
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
      <!-- Section 1: Release & Promo Radar (Daily Action & Upcoming Drops) -->
      <section class="studio-section promo-radar-section">
        <div class="section-header">
          <div class="header-left">
            <span class="section-icon">🚀</span>
            <div>
              <h2>Release &amp; Promo Radar</h2>
              <p class="muted small">Tägliche Promo-Aufgaben (TikToks, Collabs &amp; Pre-Saves) und anstehende Veröffentlichungstermine.</p>
            </div>
          </div>
          <div class="header-actions">
            <button class="btn ghost tiny" @click="goTo('promo-queue')">Zur Promo-Queue →</button>
            <button class="btn tiny" @click="goTo('promo-queue')">+ Neuer Release</button>
          </div>
        </div>

        <!-- Today's Promo Posts Focus Bar -->
        <div class="daily-promo-banner card" v-if="todayPromoTasks.length">
          <div class="dp-head">
            <div class="dp-title">
              <span class="dp-badge">HEUTE ZU POSTEN</span>
              <strong>{{ todayPendingPromoCount }} offene Promo-Aufgaben für heute</strong>
            </div>
            <small class="muted">Tägliche Erinnerung um 19:00 Uhr aktiv</small>
          </div>
          <div class="dp-task-grid">
            <div
              v-for="ptask in todayPromoTasks"
              :key="ptask.id"
              class="dp-item card"
              :class="{ done: ptask.is_completed }"
            >
              <label class="dp-check">
                <input
                  type="checkbox"
                  :checked="ptask.is_completed"
                  @change="togglePromoDone(ptask)"
                />
                <span class="checkmark"></span>
              </label>
              <div class="dp-info">
                <div class="dp-tags">
                  <span class="dp-plat">{{ ptask.platform || 'TikTok' }}</span>
                  <span class="dp-rel" v-if="ptask.release_title">💿 {{ ptask.release_title }}</span>
                </div>
                <strong class="dp-name" :class="{ strike: ptask.is_completed }">{{ ptask.title }}</strong>
                <p class="dp-notes muted small" v-if="ptask.notes">💡 {{ ptask.notes }}</p>
              </div>
              <button
                class="btn ghost tiny dp-action-btn"
                type="button"
                @click="togglePromoDone(ptask)"
              >
                {{ ptask.is_completed ? "Wieder öffnen" : "✓ Gepostet" }}
              </button>
            </div>
          </div>
        </div>

        <!-- Upcoming Releases Grid -->
        <div class="releases-radar-grid" v-if="activeReleases.length">
          <article
            v-for="rel in activeReleases.slice(0, 3)"
            :key="rel.id"
            class="rel-radar-card card"
          >
            <div class="rel-radar-top">
              <div class="rel-cover-mini">💿</div>
              <div class="rel-meta">
                <span class="rel-artist-lbl" v-if="rel.artist_name">👤 {{ rel.artist_name }}</span>
                <h3 class="rel-heading" @click="goTo('promo-queue')">{{ rel.title }}</h3>
                <div class="rel-countdown-tag" :class="getCountdownClass(rel.planned_date)">
                  📅 {{ formatReleaseDate(rel.planned_date) }} &middot; {{ getCountdownText(rel.planned_date) }}
                </div>
              </div>
            </div>

            <div class="rel-radar-progress">
              <div class="rel-prog-text">
                <small class="muted">Promo-Fortschritt</small>
                <small><strong>{{ rel.completed_promo_tasks_count || 0 }}</strong> / {{ rel.promo_tasks_count || 0 }} Posts</small>
              </div>
              <div class="rel-prog-bar">
                <div
                  class="rel-prog-fill"
                  :style="{ width: calcPercent(rel.completed_promo_tasks_count, rel.promo_tasks_count) + '%' }"
                ></div>
              </div>
            </div>

            <div class="rel-radar-footer">
              <span class="rel-model-tag">{{ promoModelLabel(rel.promo_model) }}</span>
              <button class="btn ghost tiny" @click="goTo('promo-queue')">Plan ansehen →</button>
            </div>
          </article>
        </div>

        <div class="empty-pipeline-box" v-else-if="!todayPromoTasks.length">
          <div class="empty-icon-ring">🚀</div>
          <h3>Plane deinen nächsten Release &amp; Promo-Push</h3>
          <p class="muted">
            Trage einfach das Veröffentlichungsdatum ein und wähle dein Promo-Modell (z.B. 7 Tage tägliche TikToks, Collab-Posts, Snippets).
          </p>
          <div class="empty-actions">
            <button class="btn" @click="goTo('promo-queue')">+ Neuen Release &amp; Promo-Plan anlegen</button>
          </div>
        </div>
      </section>

      <!-- Section: Team & Tool Tasks (Quick View Shortcut) -->
      <section class="team-tasks-widget card" v-if="!hideTeamTasksWidget && (isTeam || teamTasksList.length)">
        <div class="tt-widget-head">
          <div class="tt-head-left">
            <span class="tt-icon">🛠️</span>
            <div>
              <h3>Team &amp; Tool Tasks <span class="tt-pill">Quick View</span></h3>
              <p class="muted small">Die nächsten anstehenden Entwicklungs- und Plattform-Aufgaben.</p>
            </div>
          </div>
          <div class="tt-head-actions">
            <button class="btn ghost tiny" @click="goToRoute({ name: 'platform-team-tasks' })">
              Zur Team-Plattform →
            </button>
            <button class="btn ghost tiny close-widget-btn" @click="toggleHideTeamWidget" title="Fenster für mich ausblenden">
              ✕ Ausblenden
            </button>
          </div>
        </div>

        <div class="tt-tasks-list" v-if="teamTasksList.length">
          <div
            v-for="tt in teamTasksList.slice(0, 3)"
            :key="tt.id"
            class="tt-task-row"
            :class="{ done: tt.status === 'DONE' }"
          >
            <label class="tt-check">
              <input
                type="checkbox"
                :checked="tt.status === 'DONE'"
                @change="toggleTaskDone(tt)"
              />
              <span class="checkmark"></span>
            </label>
            <div class="tt-details">
              <div class="tt-tags">
                <span class="prio-tag" :data-prio="tt.priority">{{ priorityMap[tt.priority] || tt.priority }}</span>
                <span class="tt-due" v-if="tt.due_date" :class="dueState(tt.due_date)">
                  📅 {{ formatDate(tt.due_date) }}
                </span>
                <span class="tt-assignee" v-if="tt.assignees && tt.assignees.length">
                  👤 {{ tt.assignees[0].name }}
                </span>
              </div>
              <strong class="tt-title" :class="{ strike: tt.status === 'DONE' }">{{ tt.title }}</strong>
              <p class="tt-desc muted small" v-if="tt.description">{{ tt.description.slice(0, 100) }}</p>
            </div>
          </div>
        </div>
        <div class="empty-subtext" v-else>
          <p class="muted small">Keine offenen Team-Tasks. Alle Tools laufen reibungslos!</p>
        </div>
      </section>

      <!-- Restore Team Widget Banner if hidden -->
      <div class="tt-restore-bar" v-else-if="hideTeamTasksWidget && isTeam">
        <span class="muted small">🛠️ Team &amp; Tools Quick View ist ausgeblendet</span>
        <button class="btn ghost tiny" @click="toggleHideTeamWidget">Einblenden</button>
      </div>

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
              @click="router.push('/tournaments')"
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
      </div>
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
          <div class="stage-transition-preview" style="background: var(--surface); border: 1px solid var(--border); border-radius: 8px; padding: 12px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
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

// Release & Promo Queue Collections
const activeReleases = ref([]);
const todayPromoTasks = ref([]);
const teamTasksList = ref([]);
const hideTeamTasksWidget = ref(localStorage.getItem("unyq_hide_team_tasks_widget") === "true");

const todayPendingPromoCount = computed(() => {
  return todayPromoTasks.value.filter((t) => !t.is_completed).length;
});

function toggleHideTeamWidget() {
  hideTeamTasksWidget.value = !hideTeamTasksWidget.value;
  localStorage.setItem("unyq_hide_team_tasks_widget", String(hideTeamTasksWidget.value));
}

async function togglePromoDone(ptask) {
  try {
    const res = await api.post(`promo-queue/${ptask.id}/toggle_complete/`);
    ptask.is_completed = res.data.is_completed;
    ptask.completed_at = res.data.completed_at;
    showToast(ptask.is_completed ? "✓ Promo-Post erledigt!" : "Post wieder geöffnet", "info");
  } catch {
    showToast("Konnte Status nicht aktualisieren", "error");
  }
}

function formatReleaseDate(d) {
  if (!d) return "";
  try {
    return new Date(d).toLocaleDateString("de-DE", { day: "2-digit", month: "2-digit" });
  } catch {
    return d;
  }
}

function getCountdownText(dateStr) {
  if (!dateStr) return "";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  target.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - today) / 86400000);
  if (diffDays === 0) return "🚀 Heute Release!";
  if (diffDays === 1) return "Morgen!";
  if (diffDays > 1) return `In ${diffDays} Tagen`;
  return `Vor ${Math.abs(diffDays)} Tagen`;
}

function getCountdownClass(dateStr) {
  if (!dateStr) return "";
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const target = new Date(dateStr);
  target.setHours(0, 0, 0, 0);
  const diffDays = Math.round((target - today) / 86400000);
  if (diffDays === 0) return "tag-today";
  if (diffDays <= 3 && diffDays > 0) return "tag-soon";
  return "tag-future";
}

function promoModelLabel(m) {
  const map = {
    DAILY_7D: "7 Tage Daily TikTok",
    HIGH_VOLTAGE: "14 Tage High Voltage",
    QUICK_DROP: "3 Tage Quick Drop",
    CUSTOM: "Individuell",
  };
  return map[m] || m || "Standard";
}

function calcPercent(completed, total) {
  if (!total) return 0;
  return Math.min(100, Math.round(((completed || 0) / total) * 100));
}

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

    const [tasksRes, songsRes, tournsRes, projectsRes, gpRes, reqRes, reviewRes, pendingRes, relRes, promoRes, teamRes] = await Promise.all([
      api.get("tasks/", { params: { include_archived: 0, page_size: 100 } }).catch(() => ({ data: [] })),
      api.get("songs/", { params: { page_size: 20, ordering: "-created_at" } }).catch(() => ({ data: [] })),
      api.get("tournaments/").catch(() => ({ data: [] })),
      api.get("projects/", { params: { include_archived: 0, page_size: 50 } }).catch(() => ({ data: [] })),
      api.get("growpro/", { params: { status: "ACTIVE,ON_HOLD", page_size: 50, ordering: "due_date" } }).catch(() => ({ data: [] })),
      api.get("requests/team-open/").catch(() => ({ data: [] })),
      api.get("tasks/", { params: { status: "REVIEW", page_size: 50 } }).catch(() => ({ data: [] })),
      api.get("tasks/", { params: { status: "DONE", review_status: "NOT_REVIEWED", page_size: 50 } }).catch(() => ({ data: [] })),
      api.get("releases/").catch(() => ({ data: [] })),
      api.get("promo-queue/", { params: { date: "today" } }).catch(() => ({ data: [] })),
      api.get("tasks/", { params: { task_type: "INTERNAL", include_done: 0, page_size: 5 } }).catch(() => ({ data: [] })),
    ]);

    tasks.value = normalizeList(tasksRes.data);
    songs.value = normalizeList(songsRes.data);
    tournaments.value = normalizeList(tournsRes.data);
    projects.value = normalizeList(projectsRes.data);
    growpro.value = normalizeList(gpRes.data);
    requests.value = normalizeList(reqRes.data);
    reviewTasks.value = normalizeList(reviewRes.data);
    pendingReviews.value = normalizeList(pendingRes.data);
    activeReleases.value = normalizeList(relRes.data);
    todayPromoTasks.value = normalizeList(promoRes.data);
    teamTasksList.value = normalizeList(teamRes.data);
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
  gap: 24px;
  padding: 8px 4px 64px;
  max-width: 1240px;
  margin: 0 auto;
}

.studio-ambient-glow {
  display: none;
}

/* Studio Hero Header */
.studio-hero {
  position: relative;
  z-index: 1;
  padding: 26px 30px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
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
  background: var(--surface);
  padding: 4px;
  border-radius: 999px;
  border: 1px solid var(--border);
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
  background: var(--brand);
  color: #ffffff !important;
  box-shadow: 0 4px 12px rgba(47, 99, 255, 0.35);
}

.mode-btn.active span {
  color: #ffffff !important;
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
  color: #ffffff !important;
  border: none;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.4);
}

.btn-primary span {
  color: #ffffff !important;
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
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
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
  padding: 18px;
  border-radius: 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.pipeline-card:hover {
  border-color: var(--brand);
  transform: translateY(-2px);
  box-shadow: var(--shadow-strong);
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
  background: var(--surface);
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
  background: var(--border);
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
  border: 1.5px solid var(--border);
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
  color: #ffffff !important;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.6);
}

.stage-step.active .step-dot * {
  color: #ffffff !important;
}

.stage-step.completed .step-dot {
  background: #10b981;
  border-color: #34d399;
  color: #ffffff !important;
}

.stage-step.completed .step-dot * {
  color: #ffffff !important;
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
  border-top: 1px solid var(--border);
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
  background: var(--surface);
  border-radius: 14px;
  border: 1px dashed var(--border);
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
}

.duo-panel {
  position: relative;
  z-index: 1;
  padding: 24px 26px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-soft);
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
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
}

.studio-task-item:hover {
  border-color: var(--brand);
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
  border: 1.5px solid var(--border);
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
  background: var(--surface);
  border: 1px solid var(--border);
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
  background: var(--border);
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
  background: var(--surface);
  border: 1px solid var(--border);
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
  background: var(--surface);
  border: 1px solid var(--border);
  cursor: pointer;
  transition: all 0.2s ease;
}

.toolbox-item:hover {
  background: var(--card);
  border-color: var(--brand);
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
}

.team-section {
  position: relative;
  z-index: 1;
  padding: 26px 28px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 20px;
  box-shadow: var(--shadow-soft);
}

.team-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 22px;
  border-radius: 14px;
  border: 1px solid rgba(16, 185, 129, 0.25);
  background: rgba(16, 185, 129, 0.08);
}

.kpi-card {
  padding: 18px;
  border-radius: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
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
  background: var(--modal-overlay);
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
  background: var(--modal-bg);
  border: 1px solid var(--border);
  box-shadow: var(--modal-shadow);
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

/* Promo Radar & Daily Focus */
.daily-promo-banner {
  padding: 1.15rem 1.35rem;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(56, 189, 248, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 14px;
  margin-bottom: 1.25rem;
}

.dp-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.dp-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.dp-badge {
  font-size: 0.7rem;
  background: #38bdf8;
  color: #0f172a;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  font-weight: 800;
}

.dp-task-grid {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.dp-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 10px;
}

.dp-item.done {
  opacity: 0.6;
}

.dp-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.dp-tags {
  display: flex;
  gap: 0.4rem;
}

.dp-plat {
  font-size: 0.68rem;
  background: rgba(236, 72, 153, 0.2);
  color: #f472b6;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  font-weight: 600;
}

.dp-rel {
  font-size: 0.68rem;
  background: rgba(56, 189, 248, 0.15);
  color: #7dd3fc;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.dp-name {
  font-size: 0.92rem;
  font-weight: 600;
}

.dp-name.strike {
  text-decoration: line-through;
}

.dp-notes {
  margin: 0;
}

/* Releases Radar Grid */
.releases-radar-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}

.rel-radar-card {
  padding: 1rem 1.15rem;
  border-radius: 12px;
  background: var(--card, #161a23);
  border: 1px solid var(--border, rgba(255, 255, 255, 0.08));
  display: flex;
  flex-direction: column;
  gap: 0.85rem;
}

.rel-radar-top {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.rel-cover-mini {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  background: rgba(56, 189, 248, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
}

.rel-heading {
  margin: 0.1rem 0 0.25rem;
  font-size: 1.05rem;
  font-weight: 700;
  cursor: pointer;
}

.rel-countdown-tag {
  font-size: 0.72rem;
  padding: 0.15rem 0.5rem;
  border-radius: 6px;
  display: inline-block;
  font-weight: 600;
}

.rel-countdown-tag.tag-today {
  background: #10b981;
  color: white;
}

.rel-countdown-tag.tag-soon {
  background: #f59e0b;
  color: white;
}

.rel-countdown-tag.tag-future {
  background: rgba(255, 255, 255, 0.08);
  color: var(--muted, #94a3b8);
}

.rel-prog-text {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
}

.rel-prog-bar {
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}

.rel-prog-fill {
  height: 100%;
  background: linear-gradient(90deg, #4f46e5, #38bdf8);
}

.rel-radar-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.rel-model-tag {
  font-size: 0.72rem;
  color: var(--muted, #94a3b8);
}

/* Team Tasks Widget */
.team-tasks-widget {
  padding: 1.15rem 1.35rem;
  border-radius: 14px;
  background: var(--card, #161a23);
  border: 1px solid rgba(245, 158, 11, 0.25);
  margin-bottom: 1.5rem;
}

.tt-widget-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tt-head-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.tt-head-left h3 {
  margin: 0;
  font-size: 1.1rem;
}

.tt-pill {
  font-size: 0.68rem;
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-weight: 700;
  margin-left: 0.35rem;
}

.tt-icon {
  font-size: 1.6rem;
}

.tt-head-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.tt-tasks-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.tt-task-row {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.65rem 0.85rem;
  background: rgba(0, 0, 0, 0.25);
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.05);
}

.tt-task-row.done {
  opacity: 0.6;
}

.tt-tags {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.tt-title {
  font-size: 0.9rem;
}

.tt-title.strike {
  text-decoration: line-through;
}

.tt-restore-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 1rem;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.02);
  border: 1px dashed rgba(255, 255, 255, 0.1);
  margin-bottom: 1.25rem;
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
