<template>
  <div class="tournament-arena-page" :class="{ 'artist-view-mode': currentRoleMode === 'ARTIST' }">
    <!-- Floating Particle FX Container -->
    <div class="reaction-particles-container" aria-hidden="true">
      <span
        v-for="p in activeParticles"
        :key="p.id"
        class="floating-particle"
        :style="{ left: p.x + 'px', top: p.y + 'px', animationDuration: p.duration + 's' }"
      >
        {{ p.emoji }}
      </span>
    </div>

    <!-- Background Cyber Ambient Lighting -->
    <div class="arena-mesh-glow"></div>
    <div class="arena-secondary-glow"></div>

    <!-- TOP HEADER: ARENA COMMAND CENTER -->
    <header class="arena-header card">
      <div class="header-main-col">
        <div class="arena-status-strip">
          <div class="league-broadcast-badge">
            <span class="live-pulse-dot"></span>
            <span class="league-text">UNYQ TOURNAMENT ARENA // SEASON '26 CIRCUIT</span>
          </div>
          <div class="ticker-pill">
            <span class="ticker-dot"></span>
            <span>{{ activeBattlesCount }} Battles live im Community-Voting</span>
          </div>
        </div>

        <h1 class="arena-title">
          Turniere &amp; <span class="gradient-text">Battle Arena</span>
        </h1>
        <p class="arena-lead">
          Tritt im 1v1 gegen die stärksten Beatmaker, Rapper und Produzenten an. 
          Reiche deine Runden ein, erklimme die Leaderboard-Ränge und sichere dir 
          Cash-Preise, Studio-Gear und exklusive UNYQ Label-Releases.
        </p>

        <!-- Role Mode Switcher & Quick CTAs -->
        <div class="header-action-toolbar">
          <div class="role-mode-box" v-if="isTeam">
            <span class="toolbar-label">Ansichtsmodus:</span>
            <div class="role-pill-group">
              <button
                type="button"
                class="role-pill-btn"
                :class="{ active: currentRoleMode === 'TEAM' }"
                @click="setRoleMode('TEAM')"
              >
                👑 Admin &amp; Jury
              </button>
              <button
                type="button"
                class="role-pill-btn"
                :class="{ active: currentRoleMode === 'ARTIST' }"
                @click="setRoleMode('ARTIST')"
              >
                🎤 Artist &amp; Contender
              </button>
            </div>
          </div>

          <div class="header-quick-buttons">
            <button
              v-if="currentRoleMode === 'TEAM'"
              class="btn btn-create-tournament"
              @click="showCreateModal = true"
            >
              <span class="btn-icon">⚡</span>
              <span>Neues Turnier erstellen</span>
            </button>
            <button
              v-else
              class="btn btn-hero-apply"
              @click="openSpotlightApply"
            >
              <span class="btn-icon">✍️</span>
              <span>Jetzt als Artist bewerben</span>
            </button>
            <button class="btn ghost btn-refresh-arena" @click="loadData" title="Daten aktualisieren">
              ↻
            </button>
          </div>
        </div>
      </div>

      <!-- Header Right: Arena Stats & Jackpot -->
      <div class="header-stats-col">
        <div class="jackpot-spotlight-card">
          <div class="jsc-top">
            <div class="jsc-badge">💰 ARENA PRIZE POOL</div>
            <span class="jsc-live-pulse"></span>
          </div>
          <div class="jsc-amount">{{ formatCurrency(totalPrizePool) }} €</div>
          <p class="jsc-sub">+ Official Vinyl Pressung &amp; Master Distribution</p>

          <div class="asc-stat-grid">
            <div class="asc-stat-box">
              <span class="stat-number">{{ tournamentsList.length }}</span>
              <span class="stat-caption">Turniere</span>
            </div>
            <div class="asc-stat-box highlight">
              <span class="stat-number">{{ activeBattlesCount }}</span>
              <span class="stat-caption">Live Battles</span>
            </div>
            <div class="asc-stat-box">
              <span class="stat-number">{{ totalRegisteredArtists }}</span>
              <span class="stat-caption">Artists</span>
            </div>
            <div class="asc-stat-box user-rank">
              <span class="stat-number">{{ userStats.rankDisplay }}</span>
              <span class="stat-caption">Dein Rang</span>
            </div>
          </div>

          <!-- User Quick Rank Progress Strip -->
          <div class="user-rp-progress-strip" @click="activeTab = 'ranks'">
            <div class="urps-info">
              <span class="urps-tier">{{ userStats.tier }} Tier</span>
              <span class="urps-rp">{{ userStats.rp }} / {{ userStats.nextTierRP }} RP</span>
            </div>
            <div class="urps-progress-bar">
              <div class="urps-progress-fill" :style="{ width: userProgressPercent + '%' }"></div>
            </div>
            <small class="urps-hint">Noch {{ userStats.nextTierRP - userStats.rp }} RP bis zum nächsten Rang</small>
          </div>
        </div>
      </div>
    </header>

    <!-- NAVIGATION TABS -->
    <nav class="arena-navigation-bar">
      <div class="tabs-scroll-container">
        <button
          v-for="tab in arenaTabs"
          :key="tab.key"
          class="nav-tab-button"
          :class="{ active: activeTab === tab.key }"
          @click="activeTab = tab.key"
        >
          <span class="tab-emoji">{{ tab.icon }}</span>
          <span class="tab-text">{{ tab.label }}</span>
          <span v-if="tab.badge" class="tab-counter-badge" :class="tab.badgeClass">
            {{ tab.badge }}
          </span>
        </button>
      </div>
    </nav>

    <!-- ================================================================= -->
    <!-- TAB 1: TURNIERE & ARENA OVERVIEW -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'tournaments'" class="tab-view-container">
      <!-- Spotlight Featured Tournament -->
      <div v-if="spotlightTournament" class="card spotlight-arena-banner">
        <div class="spotlight-visual-backdrop">
          <div class="glow-orb"></div>
        </div>

        <div class="spotlight-content-wrap">
          <div class="spotlight-badges">
            <span class="tag-gold-featured">⭐ HIGHLIGHT CONTEST</span>
            <span class="tag-status" :class="`status-${spotlightTournament.status.toLowerCase()}`">
              {{ statusLabel(spotlightTournament.status) }}
            </span>
            <span v-if="spotlightTournament.is_no_loss" class="tag-bracket-type">
              🛡️ No-Loss Double Elimination
            </span>
            <span class="tag-genre">{{ spotlightTournament.genre || 'Trap & 808' }}</span>
          </div>

          <h2 class="spotlight-heading">{{ spotlightTournament.title }}</h2>
          <p class="spotlight-description">{{ spotlightTournament.description }}</p>

          <div class="spotlight-features-row">
            <div class="sf-feature">
              <span class="sf-icon">🏆</span>
              <div class="sf-body">
                <strong class="sf-val">{{ spotlightTournament.prize_pool || '2.000 € Cash' }}</strong>
                <span class="sf-lbl">Preisgeld &amp; Gear</span>
              </div>
            </div>
            <div class="sf-feature">
              <span class="sf-icon">👥</span>
              <div class="sf-body">
                <strong class="sf-val">{{ spotlightTournament.participants_count || 16 }} Artists</strong>
                <span class="sf-lbl">Plätze im Baum</span>
              </div>
            </div>
            <div class="sf-feature">
              <span class="sf-icon">⚔️</span>
              <div class="sf-body">
                <strong class="sf-val">{{ spotlightTournament.battles_count || 8 }} Battles</strong>
                <span class="sf-lbl">Runden gesamt</span>
              </div>
            </div>
            <div class="sf-feature">
              <span class="sf-icon">⏳</span>
              <div class="sf-body">
                <strong class="sf-val">{{ formatCountdown(spotlightTournament.ends_at) }}</strong>
                <span class="sf-lbl">Runden-Deadline</span>
              </div>
            </div>
          </div>

          <div class="spotlight-cta-row">
            <button class="btn btn-hero-primary" @click="openTournamentDetail(spotlightTournament)">
              Turnierbaum &amp; Runden öffnen →
            </button>
            <button
              v-if="spotlightTournament.status === 'APPLICATION_OPEN'"
              class="btn btn-hero-secondary"
              @click="openApplicationModal(spotlightTournament)"
            >
              ✍️ Als Artist bewerben
            </button>
            <button
              v-else-if="spotlightTournament.status === 'BATTLES'"
              class="btn btn-hero-secondary"
              @click="activeTab = 'battles'"
            >
              ⚔️ Jetzt abstimmen
            </button>
          </div>
        </div>
      </div>

      <!-- Filters & Search Toolbar -->
      <div class="discovery-filter-toolbar card">
        <div class="search-input-wrapper">
          <span class="search-icon-symbol">🔍</span>
          <input
            v-model.trim="tournamentSearch"
            type="text"
            class="input discovery-search-input"
            placeholder="Turnier, Genre (Trap, Drill, Lo-Fi, Vocal) oder Preis suchen..."
          />
          <button v-if="tournamentSearch" class="search-clear-btn" @click="tournamentSearch = ''">✕</button>
        </div>

        <div class="filter-pills-row">
          <div class="pill-group">
            <button
              v-for="st in statusFilters"
              :key="st.key"
              class="filter-pill"
              :class="{ active: selectedStatusFilter === st.key }"
              @click="selectedStatusFilter = st.key"
            >
              {{ st.label }}
            </button>
          </div>

          <div class="pill-group-right">
            <button
              class="view-toggle-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
              title="Rasteransicht"
            >
              ▦
            </button>
            <button
              class="view-toggle-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
              title="Listenansicht"
            >
              ☰
            </button>
          </div>
        </div>
      </div>

      <!-- Tournaments Grid / List -->
      <div v-if="filteredTournaments.length" :class="viewMode === 'grid' ? 'tournaments-card-grid' : 'tournaments-list-view'">
        <div
          v-for="t in filteredTournaments"
          :key="t.id"
          class="card tournament-interactive-card"
          @click="openTournamentDetail(t)"
        >
          <div class="tic-header">
            <div class="tic-status-badges">
              <span class="badge-status-pill" :class="`status-${t.status.toLowerCase()}`">
                {{ statusLabel(t.status) }}
              </span>
              <span v-if="t.is_no_loss" class="badge-no-loss">No-Loss</span>
              <span class="badge-genre-tag">{{ t.genre || 'Beat Battle' }}</span>
            </div>
            <div class="tic-prize-chip">
              💰 {{ t.prize_pool || '500 €' }}
            </div>
          </div>

          <div class="tic-body">
            <h3 class="tic-title">{{ t.title }}</h3>
            <p class="tic-desc">{{ t.description || 'Spannender Battle-Wettbewerb im UNYQ Circuit.' }}</p>
          </div>

          <!-- Roster Slots Visualizer -->
          <div class="roster-slots-bar">
            <div class="rsb-labels">
              <span>Teilnehmer-Slots</span>
              <strong>{{ t.participants_count || 8 }} / 16 belegt</strong>
            </div>
            <div class="rsb-track">
              <div
                class="rsb-fill"
                :style="{ width: Math.min(100, Math.round(((t.participants_count || 8) / 16) * 100)) + '%' }"
              ></div>
            </div>
          </div>

          <div class="tic-meta-row">
            <div class="tic-meta-item">
              <span class="ico">⚔️</span>
              <span>{{ t.battles_count || 4 }} Battles</span>
            </div>
            <div class="tic-meta-item">
              <span class="ico">📅</span>
              <span>{{ formatDate(t.ends_at) }}</span>
            </div>
          </div>

          <div class="tic-actions">
            <button class="btn btn-sm btn-open-card" @click.stop="openTournamentDetail(t)">
              Details &amp; Bracket →
            </button>
            <button
              v-if="t.status === 'APPLICATION_OPEN'"
              class="btn ghost btn-sm btn-apply-card"
              @click.stop="openApplicationModal(t)"
            >
              Bewerben 🎤
            </button>
            <button
              v-else-if="t.status === 'SUBMISSION_OPEN'"
              class="btn ghost btn-sm btn-submit-card"
              @click.stop="openUploadRoundModal({ tournament_id: t.id, tournament_title: t.title })"
            >
              Runde einreichen 📤
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="card empty-tournaments-state">
        <div class="ets-icon">🔍</div>
        <h3>Keine Turniere gefunden</h3>
        <p class="muted">Versuche einen anderen Suchbegriff oder ändere deine Statusfilter.</p>
        <button class="btn ghost btn-sm" @click="resetFilters">Filter zurücksetzen</button>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 2: LIVE BATTLES & VOTING (HEAD-TO-HEAD SHOWDOWN) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'battles'" class="tab-view-container">
      <div class="section-hero-header">
        <div>
          <h2>⚔️ Live Battles &amp; Community-Voting</h2>
          <p class="muted">
            Höre dir beide Runden im direkten A/B-Vergleich an und vote für deinen Favoriten. 
            Jeder Vote bringt dir +10 Community-RP!
          </p>
        </div>
        <div class="voting-rules-pill">
          <span>🛡️ 1 Vote pro User &amp; Battle aktiv</span>
        </div>
      </div>

      <div v-if="liveBattlesList.length" class="battles-showdown-grid">
        <div
          v-for="b in liveBattlesList"
          :key="b.id"
          class="card battle-duel-card"
          :class="{ 'battle-resolved': b.status === 'CLOSED' }"
        >
          <!-- Battle Top Bar -->
          <div class="bd-top-bar">
            <div class="bd-round-tag">
              <span class="live-dot" v-if="b.status === 'OPEN'"></span>
              <span>RUNDE {{ b.round_number || 1 }}</span>
            </div>
            <span class="bd-tourney-name">{{ b.tournament_title }}</span>
            <span class="bd-status-badge" :class="b.status.toLowerCase()">
              {{ b.status === 'OPEN' ? '🔥 Voting Live' : 'Beendet' }}
            </span>
          </div>

          <!-- THE FIGHTER SHOWDOWN (LEFT VS RIGHT) -->
          <div class="duel-arena-ring">
            <!-- Left Fighter Box -->
            <div
              class="fighter-card left-fighter"
              :class="{
                winner: b.winner === 'left' || (b.status === 'CLOSED' && b.votes_left > b.votes_right),
                voted: hasVotedSide(b, 'left'),
              }"
            >
              <div class="fighter-avatar-wrap">
                <div class="fighter-avatar">
                  {{ (b.left_profile_name || 'A').charAt(0).toUpperCase() }}
                </div>
                <img :src="getTierBadge(b.left_tier || 'Gold')" class="fighter-tier-icon" alt="Tier" />
              </div>

              <div class="fighter-info">
                <strong class="fighter-name">{{ b.left_profile_name }}</strong>
                <span class="fighter-tier-label">{{ b.left_tier || 'Gold' }} Tier • {{ b.left_rp || '1.820' }} RP</span>
              </div>

              <!-- Audio Player Box Left -->
              <div class="fighter-audio-deck">
                <button
                  class="audio-play-trigger-btn"
                  :class="{ playing: currentPlayingTrack === `battle-${b.id}-left` }"
                  @click="toggleAudio(`battle-${b.id}-left`, b.left_profile_name)"
                >
                  <span v-if="currentPlayingTrack === `battle-${b.id}-left`">⏸ Pause</span>
                  <span v-else>▶ Runde anhören</span>
                </button>

                <!-- Animated Waveform Bars -->
                <div class="audio-wave-bars" :class="{ active: currentPlayingTrack === `battle-${b.id}-left` }">
                  <span v-for="i in 16" :key="i" class="wave-bar" :style="{ animationDelay: `${(i % 5) * 0.12}s` }"></span>
                </div>
              </div>

              <div class="fighter-votes-badge">
                <span class="votes-count">{{ b.votes_left }}</span>
                <span class="votes-lbl">Votes</span>
              </div>
            </div>

            <!-- Central VS Badge & A/B Switcher -->
            <div class="duel-center-divider">
              <div class="vs-emblem">VS</div>
              <button
                class="btn-ab-switch"
                @click="quickSwitchAB(b)"
                title="Zwischen beiden Runden nahtlos umschalten"
              >
                ⇄ A/B Wechsel
              </button>
            </div>

            <!-- Right Fighter Box -->
            <div
              class="fighter-card right-fighter"
              :class="{
                winner: b.winner === 'right' || (b.status === 'CLOSED' && b.votes_right > b.votes_left),
                voted: hasVotedSide(b, 'right'),
              }"
            >
              <div class="fighter-avatar-wrap">
                <div class="fighter-avatar right-avatar">
                  {{ (b.right_profile_name || 'B').charAt(0).toUpperCase() }}
                </div>
                <img :src="getTierBadge(b.right_tier || 'Platin')" class="fighter-tier-icon" alt="Tier" />
              </div>

              <div class="fighter-info">
                <strong class="fighter-name">{{ b.right_profile_name }}</strong>
                <span class="fighter-tier-label">{{ b.right_tier || 'Platin' }} Tier • {{ b.right_rp || '2.940' }} RP</span>
              </div>

              <!-- Audio Player Box Right -->
              <div class="fighter-audio-deck">
                <button
                  class="audio-play-trigger-btn"
                  :class="{ playing: currentPlayingTrack === `battle-${b.id}-right` }"
                  @click="toggleAudio(`battle-${b.id}-right`, b.right_profile_name)"
                >
                  <span v-if="currentPlayingTrack === `battle-${b.id}-right`">⏸ Pause</span>
                  <span v-else>▶ Runde anhören</span>
                </button>

                <div class="audio-wave-bars" :class="{ active: currentPlayingTrack === `battle-${b.id}-right` }">
                  <span v-for="i in 16" :key="i" class="wave-bar" :style="{ animationDelay: `${(i % 5) * 0.12}s` }"></span>
                </div>
              </div>

              <div class="fighter-votes-badge">
                <span class="votes-count">{{ b.votes_right }}</span>
                <span class="votes-lbl">Votes</span>
              </div>
            </div>
          </div>

          <!-- Dynamic Live Vote Meter -->
          <div class="live-vote-meter-container">
            <div class="lvm-bar-left" :style="{ width: getVotePct(b, 'left') + '%' }">
              <span>{{ getVotePct(b, 'left') }}%</span>
            </div>
            <div class="lvm-bar-right" :style="{ width: getVotePct(b, 'right') + '%' }">
              <span>{{ getVotePct(b, 'right') }}%</span>
            </div>
          </div>

          <!-- Voting Action Buttons -->
          <div class="battle-vote-action-bar" v-if="b.status !== 'CLOSED'">
            <button
              class="btn-vote-fighter left-vote-btn"
              :class="{ 'has-voted': hasVotedSide(b, 'left') }"
              :disabled="hasVoted(b)"
              @click="castVote(b, 'left', $event)"
            >
              <span class="vote-icon">👍</span>
              <span>Vote für {{ b.left_profile_name }}</span>
            </button>

            <button
              class="btn-vote-fighter right-vote-btn"
              :class="{ 'has-voted': hasVotedSide(b, 'right') }"
              :disabled="hasVoted(b)"
              @click="castVote(b, 'right', $event)"
            >
              <span class="vote-icon">👍</span>
              <span>Vote für {{ b.right_profile_name }}</span>
            </button>
          </div>

          <div v-else class="battle-resolved-banner">
            🏆 Sieger: 
            <strong>{{ b.votes_left >= b.votes_right ? b.left_profile_name : b.right_profile_name }}</strong>
            nach Community-Voting bestätigt!
          </div>

          <!-- Crowd Hype Reaction Floating Bar -->
          <div class="crowd-hype-toolbar">
            <span class="hype-title">Crowd Hype:</span>
            <div class="hype-buttons-group">
              <button
                v-for="emoji in ['🔥', '💥', '🤯', '👑', '👏']"
                :key="emoji"
                class="hype-react-btn"
                @click="spawnReactionParticle(emoji, $event)"
              >
                {{ emoji }}
              </button>
            </div>
          </div>

          <!-- Admin Decision Controls (Team Only) -->
          <div class="admin-decision-bar" v-if="currentRoleMode === 'TEAM' && b.status !== 'CLOSED'">
            <span class="admin-verdict-label">👑 Admin Urteil:</span>
            <div class="admin-verdict-buttons">
              <button class="btn ghost btn-sm" @click="adminResolveBattle(b, 'left')">
                🏆 {{ b.left_profile_name }} Sieg
              </button>
              <button class="btn ghost btn-sm" @click="adminResolveBattle(b, 'right')">
                🏆 {{ b.right_profile_name }} Sieg
              </button>
              <button class="btn ghost btn-sm" @click="adminResolveBattle(b, 'auto')">
                ⚡ Nach Votes schließen
              </button>
            </div>
          </div>
        </div>
      </div>
      <div v-else class="card empty-tournaments-state">
        <div class="ets-icon">⚔️</div>
        <h3>Keine aktiven Live-Battles</h3>
        <p class="muted">Sobald Turniere in die Battle-Phase wechseln und Duelle generiert wurden, kannst du hier Runden im A/B-Vergleich hören und abstimmen.</p>
        <button v-if="currentRoleMode === 'TEAM'" class="btn btn-sm" @click="activeTab = 'admin'; adminSubTab = 'tournaments'">
          👑 Zum Admin Director
        </button>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 3: LEADERBOARD & PODIUM -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'leaderboard'" class="tab-view-container">
      <div class="section-hero-header">
        <div>
          <h2>🥇 Ranked Leaderboard // Season '26</h2>
          <p class="muted">
            Punkte sammeln durch Siege in Runden, Battle-Votes und Jury-Auszeichnungen. 
            Die Top 3 qualifizieren sich direkt für die Champions Finals.
          </p>
        </div>
        <div class="leaderboard-division-select">
          <button
            v-for="div in leaderboardDivisions"
            :key="div.key"
            class="filter-pill"
            :class="{ active: selectedDivision === div.key }"
            @click="selectedDivision = div.key"
          >
            {{ div.label }}
          </button>
        </div>
      </div>

      <!-- 3D GRAND CHAMPIONS PODIUM (TOP 3) -->
      <div class="champions-podium-wrap" v-if="filteredLeaderboard.length >= 3">
        <!-- 2nd Place: Silver -->
        <div class="podium-pillar rank-2-pillar" @click="inspectArtist(filteredLeaderboard[1])">
          <div class="podium-avatar-box">
            <span class="podium-badge-silver">2</span>
            <div class="podium-avatar silver-avatar">
              {{ filteredLeaderboard[1].name.charAt(0) }}
            </div>
            <img :src="silberRank" class="podium-tier-crest" alt="Silber" />
          </div>
          <strong class="podium-artist-name">{{ filteredLeaderboard[1].name }}</strong>
          <span class="podium-rp-pill">{{ filteredLeaderboard[1].ranked_points }} RP</span>
          <span class="podium-tier-name">{{ filteredLeaderboard[1].tier }} Tier</span>
          <span class="podium-streak-tag">🔥 {{ filteredLeaderboard[1].wins }}W - {{ filteredLeaderboard[1].losses }}L</span>
          <div class="podium-stand silver-stand">
            <span class="stand-number">#2</span>
          </div>
        </div>

        <!-- 1st Place: Gold / Legendary Crown -->
        <div class="podium-pillar rank-1-pillar" @click="inspectArtist(filteredLeaderboard[0])">
          <div class="crown-animated-halo">👑</div>
          <div class="podium-avatar-box">
            <span class="podium-badge-gold">1</span>
            <div class="podium-avatar gold-avatar">
              {{ filteredLeaderboard[0].name.charAt(0) }}
            </div>
            <img :src="legendarRank" class="podium-tier-crest legendary-crest" alt="Legendär" />
          </div>
          <strong class="podium-artist-name champion">{{ filteredLeaderboard[0].name }}</strong>
          <span class="podium-rp-pill champion-rp">{{ filteredLeaderboard[0].ranked_points }} RP</span>
          <span class="podium-tier-name champion-tier">{{ filteredLeaderboard[0].tier }} Tier</span>
          <span class="podium-streak-tag champion-streak">🔥 {{ filteredLeaderboard[0].wins }}W - {{ filteredLeaderboard[0].losses }}L ({{ getWinRate(filteredLeaderboard[0]) }}%)</span>
          <div class="podium-stand gold-stand">
            <span class="stand-number">#1</span>
          </div>
        </div>

        <!-- 3rd Place: Bronze -->
        <div class="podium-pillar rank-3-pillar" @click="inspectArtist(filteredLeaderboard[2])">
          <div class="podium-avatar-box">
            <span class="podium-badge-bronze">3</span>
            <div class="podium-avatar bronze-avatar">
              {{ filteredLeaderboard[2].name.charAt(0) }}
            </div>
            <img :src="bronzeRank" class="podium-tier-crest" alt="Bronze" />
          </div>
          <strong class="podium-artist-name">{{ filteredLeaderboard[2].name }}</strong>
          <span class="podium-rp-pill">{{ filteredLeaderboard[2].ranked_points }} RP</span>
          <span class="podium-tier-name">{{ filteredLeaderboard[2].tier }} Tier</span>
          <span class="podium-streak-tag">🔥 {{ filteredLeaderboard[2].wins }}W - {{ filteredLeaderboard[2].losses }}L</span>
          <div class="podium-stand bronze-stand">
            <span class="stand-number">#3</span>
          </div>
        </div>
      </div>

      <!-- LEADERBOARD DATA TABLE -->
      <div class="card leaderboard-table-card">
        <div class="lt-header-row">
          <span class="col-rank">Rang</span>
          <span class="col-artist">Artist / Producer</span>
          <span class="col-tier">Tier</span>
          <span class="col-rp">Ranked Points</span>
          <span class="col-record">Bilanz</span>
          <span class="col-winrate">Win-Rate</span>
          <span class="col-actions">Aktion</span>
        </div>

        <div v-if="!filteredLeaderboard.length" class="empty-muted-box muted" style="padding: 36px; text-align: center;">
          <p style="font-size: 1.05rem; margin-bottom: 6px; font-weight: 700;">Keine Artists im Leaderboard</p>
          <p class="small">Sobald Runden ausgetragen oder Punkte vergeben wurden, erscheinen die Ränge hier.</p>
        </div>

        <div
          v-for="(row, idx) in filteredLeaderboard"
          :key="row.id || idx"
          class="lt-data-row"
          :class="{ 'is-user': row.isMe }"
        >
          <div class="col-rank">
            <span class="rank-pos-number">#{{ idx + 1 }}</span>
          </div>

          <div class="col-artist artist-info-cell">
            <div class="artist-thumb">{{ row.name.charAt(0) }}</div>
            <div class="artist-names">
              <strong class="name">{{ row.name }}</strong>
              <span v-if="row.isMe" class="badge-me-pill">Du</span>
              <span v-if="row.wins >= 20" class="badge-veteran">PRO</span>
            </div>
          </div>

          <div class="col-tier">
            <div class="tier-pill-display">
              <img :src="getTierBadge(row.tier)" class="table-tier-icon" :alt="row.tier" />
              <span>{{ row.tier }}</span>
            </div>
          </div>

          <div class="col-rp">
            <span class="rp-bold">{{ row.ranked_points }} RP</span>
            <small class="rp-trend positive">+{{ Math.round(row.ranked_points * 0.05) }} diese Woche</small>
          </div>

          <div class="col-record font-mono">
            {{ row.wins || 0 }}W - {{ row.losses || 0 }}L
          </div>

          <div class="col-winrate">
            <div class="winrate-bar-wrap">
              <span>{{ getWinRate(row) }}%</span>
              <div class="winrate-bar-track">
                <div class="winrate-bar-fill" :style="{ width: getWinRate(row) + '%' }"></div>
              </div>
            </div>
          </div>

          <div class="col-actions">
            <button class="btn ghost btn-micro" @click="inspectArtist(row)">
              Profil ↗
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 4: RÄNGE & TIERS SYSTEM (INSPECTOR) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'ranks'" class="tab-view-container">
      <div class="section-hero-header">
        <div>
          <h2>🛡️ UNYQ Ränge &amp; Tiers System</h2>
          <p class="muted">
            Kämpfe dich von Bronze bis Legendär hoch. Jeder Rang schaltet exklusive Vorteile, 
            höhere Preisgeld-Anteile und VIP-Events frei.
          </p>
        </div>
      </div>

      <!-- Rank Tier Cards Grid -->
      <div class="ranks-deck-grid">
        <div
          v-for="tier in tiersMasterList"
          :key="tier.key"
          class="card rank-tier-card"
          :class="{
            active: selectedTierDetail.key === tier.key,
            'is-my-tier': userStats.tier.toUpperCase() === tier.key,
          }"
          @click="selectedTierDetail = tier"
        >
          <div class="rtc-badge-top" v-if="userStats.tier.toUpperCase() === tier.key">
            DEIN AKTUELLER RANG
          </div>

          <div class="rtc-image-wrap">
            <img :src="tier.icon" :alt="tier.name" class="rtc-tier-img" />
          </div>

          <h3 class="rtc-name">{{ tier.name }}</h3>
          <span class="rtc-rp-req">ab {{ tier.minRP }} RP</span>
          <p class="rtc-perks-summary">{{ tier.shortDesc }}</p>

          <button class="btn ghost btn-sm rtc-inspect-btn">
            Details ansehen →
          </button>
        </div>
      </div>

      <!-- Selected Tier Deep Dive Panel -->
      <div class="card tier-deep-dive-panel">
        <div class="tdd-left">
          <div class="tdd-img-box">
            <img :src="selectedTierDetail.icon" :alt="selectedTierDetail.name" class="tdd-big-img" />
          </div>
          <div>
            <span class="tdd-eyebrow">RANG DETAILS</span>
            <h2>{{ selectedTierDetail.name }} Tier</h2>
            <p class="muted">Mindestanforderung: {{ selectedTierDetail.minRP }} Ranked Points</p>
          </div>
        </div>

        <div class="tdd-perks-list">
          <h4>Freigeschaltete Perks &amp; Arena Privilegien:</h4>
          <ul>
            <li v-for="(perk, i) in selectedTierDetail.perks" :key="i">
              <span class="perk-check">✓</span>
              <span>{{ perk }}</span>
            </li>
          </ul>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 5: MEIN BATTLE HUB (ARTIST PASSPORT) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'my-tournaments'" class="tab-view-container">
      <div class="section-hero-header">
        <div>
          <h2>👤 Mein Battle Hub &amp; Runden</h2>
          <p class="muted">
            Deine laufenden Bewerbungen, aktive Matches und eingereichte Runden im Überblick.
          </p>
        </div>
        <button class="btn" @click="openSpotlightApply">
          + Neue Bewerbung einreichen
        </button>
      </div>

      <!-- Quick Stats Card -->
      <div class="card artist-passport-card">
        <div class="apc-stat">
          <span class="lbl">Ranked Status</span>
          <strong class="val">{{ userStats.tier }} Tier ({{ userStats.rp }} RP)</strong>
        </div>
        <div class="apc-stat">
          <span class="lbl">Turnier-Teilnahmen</span>
          <strong class="val">{{ myApplications.length }} Contests</strong>
        </div>
        <div class="apc-stat">
          <span class="lbl">Battle-Bilanz</span>
          <strong class="val">8 Wins / 2 Losses (80%)</strong>
        </div>
        <div class="apc-stat">
          <span class="lbl">Gewonnene Preisgelder</span>
          <strong class="val highlight">750,00 €</strong>
        </div>
      </div>

      <!-- HUB SUB-TABS: BEWERBUNGEN & RUNDEN -->
      <div class="hub-tabs-row">
        <button
          type="button"
          class="hub-tab-btn"
          :class="{ active: myHubSubTab === 'applications' }"
          @click="myHubSubTab = 'applications'"
        >
          <span>📋 Meine Bewerbungen ({{ myApplications.length }})</span>
        </button>
        <button
          type="button"
          class="hub-tab-btn"
          :class="{ active: myHubSubTab === 'submissions' }"
          @click="myHubSubTab = 'submissions'"
        >
          <span>🎵 Meine eingereichten Runden ({{ mySubmissionsList.length }})</span>
        </button>
      </div>

      <!-- Section 1: Applications -->
      <div v-if="myHubSubTab === 'applications'">
        <div v-if="myApplications.length" class="my-battles-grid">
          <div v-for="app in myApplications" :key="app.id" class="card my-entry-card" :class="{ rejected: app.status === 'REJECTED' }">
            <div class="mec-head">
              <span class="badge-status-pill" :class="app.status.toLowerCase()">
                {{ app.status === 'APPROVED' || app.status === 'ACCEPTED' ? '✓ Zugelassen' : (app.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
              </span>
              <span class="mec-date">{{ app.created_at || 'Eingereicht' }}</span>
            </div>

            <h3 class="mec-title">{{ app.tournament_title }}</h3>
            <p class="mec-msg">"{{ app.message }}"</p>

            <!-- Prominent Rejection Reason Banner if rejected -->
            <div v-if="app.status === 'REJECTED'" class="hub-rejection-banner">
              <strong>❌ Von der Jury abgelehnt:</strong>
              <p>"{{ app.rejection_reason || 'Die Bewerbung hat die Kriterien der aktuellen Runde leider nicht erfüllt.' }}"</p>
              <small class="muted">Du kannst deine Bewerbung überarbeiten und erneut einreichen.</small>
            </div>

            <div class="mec-actions">
              <button
                v-if="app.status === 'ACCEPTED' || app.status === 'APPROVED'"
                class="btn btn-sm btn-submit-round"
                @click="openUploadRoundModal(app)"
              >
                📤 Runde einreichen (Audio/Video)
              </button>
              <button
                v-if="app.status === 'REJECTED' || app.status === 'PENDING'"
                class="btn btn-sm btn-edit-entry"
                @click="openEditApplicationModal(app)"
              >
                ✏️ Bewerbung bearbeiten / überarbeiten
              </button>
              <button
                class="btn ghost btn-sm"
                @click="openTournamentDetail({ id: app.tournament_id, title: app.tournament_title })"
              >
                Turnier ansehen →
              </button>
            </div>
          </div>
        </div>
        <div v-else class="card empty-tournaments-state">
          <div class="ets-icon">🎤</div>
          <h3>Du hast noch keine aktiven Bewerbungen</h3>
          <p class="muted">Stöbere in den offenen Turnieren und reiche deine Bewerbung als Contender ein.</p>
          <button class="btn btn-sm" @click="activeTab = 'tournaments'">Turniere ansehen →</button>
        </div>
      </div>

      <!-- Section 2: Submissions -->
      <div v-if="myHubSubTab === 'submissions'">
        <div v-if="mySubmissionsList.length" class="my-battles-grid">
          <div v-for="sub in mySubmissionsList" :key="sub.id" class="card my-entry-card" :class="{ rejected: sub.status === 'REJECTED' }">
            <div class="mec-head">
              <span class="badge-status-pill" :class="sub.status?.toLowerCase()">
                {{ sub.status === 'APPROVED' ? '✓ Freigegeben' : (sub.status === 'REJECTED' ? '✕ Abgelehnt' : '⏳ In Prüfung') }}
              </span>
              <span class="mec-round-tag">Runde {{ sub.round_number || 1 }}</span>
            </div>

            <h3 class="mec-title">{{ sub.title }}</h3>
            <p class="mec-tourney muted small">{{ sub.tournament_title }}</p>

            <!-- Rejection Reason if rejected -->
            <div v-if="sub.status === 'REJECTED'" class="hub-rejection-banner">
              <strong>❌ Runde von der Jury abgelehnt:</strong>
              <p>"{{ sub.rejection_reason || 'Kriterien nicht erfüllt.' }}"</p>
              <small class="muted">Du kannst deinen Track anpassen und die Runde erneut zur Prüfung freigeben.</small>
            </div>

            <div class="mec-actions">
              <button
                class="btn btn-sm btn-play-audio"
                :class="{ active: currentPlayingTrack === `hub-sub-${sub.id}` }"
                @click="toggleAudio(`hub-sub-${sub.id}`, sub.artist_name || 'Du')"
              >
                {{ currentPlayingTrack === `hub-sub-${sub.id}` ? '⏸ Pause' : '▶ Anhören' }}
              </button>
              <button
                class="btn ghost btn-sm btn-edit-entry"
                @click="openEditRoundModal(sub)"
              >
                ✏️ Track bearbeiten / überarbeiten
              </button>
              <button
                class="btn ghost btn-sm"
                @click="openTournamentDetail({ id: sub.tournament_id, title: sub.tournament_title })"
              >
                Zum Turnier →
              </button>
            </div>
          </div>
        </div>
        <div v-else class="card empty-tournaments-state">
          <div class="ets-icon">🎵</div>
          <h3>Noch keine Runden-Songs eingereicht</h3>
          <p class="muted">Sobald du für ein Turnier zugelassen bist, kannst du hier deine Songs pro Runde hochladen und verwalten.</p>
          <button class="btn btn-sm" @click="activeTab = 'tournaments'">Turniere durchsuchen →</button>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 6: CONTEST & ARENA SETTINGS -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'settings'" class="tab-view-container">
      <div class="section-hero-header">
        <div>
          <h2>⚙️ Arena &amp; Contest Einstellungen</h2>
          <p class="muted">
            Passe Voting-Regeln, Audio-Wiedergabe, Benachrichtigungen und dein Artist-Arena-Profil an.
          </p>
        </div>
        <button class="btn" @click="saveArenaSettings">
          Einstellungen speichern 💾
        </button>
      </div>

      <div class="settings-sections-grid">
        <!-- Panel 1: Voting & Battle Mechanics -->
        <div class="card settings-panel">
          <div class="sp-head">
            <span class="sp-icon">🗳️</span>
            <h3>Voting &amp; Battle-Regeln</h3>
          </div>

          <div class="sp-fields">
            <label class="setting-field">
              <span>Standard Voting-Dauer pro Runde</span>
              <select v-model="arenaSettings.votingDuration" class="input">
                <option value="24">24 Stunden (Blitz-Voting)</option>
                <option value="48">48 Stunden (Standard)</option>
                <option value="72">72 Stunden (Ausführlich)</option>
              </select>
            </label>

            <label class="setting-field">
              <span>Stimmen-Gewichtung (Jury vs Community)</span>
              <select v-model="arenaSettings.voteWeighting" class="input">
                <option value="100_COMMUNITY">100% Community-Voting</option>
                <option value="50_50">50% Community + 50% UNYQ Jury</option>
                <option value="100_JURY">100% Experten-Jury</option>
              </select>
            </label>

            <label class="toggle-setting-row">
              <input type="checkbox" v-model="arenaSettings.requireMinimumListening" />
              <div>
                <strong>Mindest-Hördauer voraussetzen</strong>
                <p class="muted small">User müssen min. 15 Sekunden jeder Runde hören, bevor der Vote freigeschaltet wird.</p>
              </div>
            </label>

            <label class="toggle-setting-row">
              <input type="checkbox" v-model="arenaSettings.preventSelfVoting" />
              <div>
                <strong>Eigen-Vote Sperre aktiv</strong>
                <p class="muted small">Artists können in eigenen Battles nicht für sich selbst abstimmen.</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Panel 2: Sound & Audio Experience -->
        <div class="card settings-panel">
          <div class="sp-head">
            <span class="sp-icon">🎧</span>
            <h3>Audio-Engine &amp; Player</h3>
          </div>

          <div class="sp-fields">
            <label class="setting-field">
              <span>Audio-Streaming-Qualität</span>
              <select v-model="arenaSettings.audioQuality" class="input">
                <option value="lossless">Studio Master (Hi-Fi 320 kbps / Lossless)</option>
                <option value="standard">Standard (192 kbps MP3)</option>
                <option value="data_saver">Datensparmodus (128 kbps)</option>
              </select>
            </label>

            <label class="setting-field">
              <span>Visualizer-Stil</span>
              <select v-model="arenaSettings.visualizerStyle" class="input">
                <option value="neon_bars">Neon Spectrum Equalizer</option>
                <option value="oscilloscope">Cyber Oscilloscope Wave</option>
                <option value="pulse_circle">Pulsierender Core</option>
              </select>
            </label>

            <label class="toggle-setting-row">
              <input type="checkbox" v-model="arenaSettings.autoPlayNextRound" />
              <div>
                <strong>A/B Autoplay umschalten</strong>
                <p class="muted small">Nach Ende von Runde A automatisch Runde B nahtlos abspielen.</p>
              </div>
            </label>

            <label class="toggle-setting-row">
              <input type="checkbox" v-model="arenaSettings.soundEffectsEnabled" />
              <div>
                <strong>Arena Sound FX &amp; Hype-Sounds</strong>
                <p class="muted small">Gong bei Battle-Start und Jubel-Effekt beim Abstimmen.</p>
              </div>
            </label>
          </div>
        </div>

        <!-- Panel 3: Artist Arena Profil -->
        <div class="card settings-panel">
          <div class="sp-head">
            <span class="sp-icon">🎤</span>
            <h3>Artist Arena-Profil</h3>
          </div>

          <div class="sp-fields">
            <label class="setting-field">
              <span>Battle Stage-Name</span>
              <input v-model.trim="arenaSettings.stageName" class="input" placeholder="z. B. DJ Phantom" />
            </label>

            <label class="setting-field">
              <span>Haupt-Disziplin</span>
              <select v-model="arenaSettings.primaryDiscipline" class="input">
                <option value="BEATS">Beatmaking / Produzent</option>
                <option value="RAP">Rap &amp; Lyrics</option>
                <option value="VOCAL">Melodic Vocals &amp; R&amp;B</option>
                <option value="ALLROUND">Allrounder / Singer-Songwriter</option>
              </select>
            </label>

            <label class="setting-field">
              <span>Battle Tagline / Ansage</span>
              <input v-model.trim="arenaSettings.tagline" class="input" placeholder="Härtester 808 aus Berlin..." />
            </label>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- TAB 7: ADMIN ARENA MANAGER (TEAM ONLY) -->
    <!-- ================================================================= -->
    <section v-if="activeTab === 'admin' && currentRoleMode === 'TEAM'" class="tab-view-container admin-director-section">
      <div class="section-hero-header">
        <div>
          <h2>👑 Admin Arena Director</h2>
          <p class="muted">
            Turniere steuern, Saison-Reset durchführen, Ränge und Punkte manuell feinjustieren, Bewerber-Roster verwalten und Battles kontrollieren.
          </p>
        </div>
        <div class="director-header-actions">
          <button class="btn ghost btn-sm" @click="loadData" title="Daten aktualisieren">
            ↻ Sync
          </button>
          <button class="btn btn-create-tournament" @click="showCreateModal = true">
            + Neues Turnier anlegen
          </button>
        </div>
      </div>

      <!-- Director Sub-Navigation Pills -->
      <div class="director-subtabs-row">
        <button
          type="button"
          class="director-subtab-pill"
          :class="{ active: adminSubTab === 'tournaments' }"
          @click="adminSubTab = 'tournaments'"
        >
          <span>🏆 Turniere &amp; Phasen</span>
          <span class="subtab-count">{{ tournamentsList.length }}</span>
        </button>

        <button
          type="button"
          class="director-subtab-pill"
          :class="{ active: adminSubTab === 'ranks' }"
          @click="adminSubTab = 'ranks'"
        >
          <span>🛡️ Ränge &amp; Saison-Reset</span>
          <span class="subtab-count highlight">{{ leaderboardRows.length }}</span>
        </button>

        <button
          type="button"
          class="director-subtab-pill"
          :class="{ active: adminSubTab === 'applications' }"
          @click="adminSubTab = 'applications'"
        >
          <span>✍️ Bewerber &amp; Roster</span>
          <span class="subtab-count" :class="{ 'count-alert': pendingApplications.length > 0 }">
            {{ pendingApplications.length }}
          </span>
        </button>

        <button
          type="button"
          class="director-subtab-pill"
          :class="{ active: adminSubTab === 'battles' }"
          @click="adminSubTab = 'battles'"
        >
          <span>⚔️ Battles &amp; Overrules</span>
          <span class="subtab-count">{{ allBattlesList.length || liveBattlesList.length }}</span>
        </button>

        <button
          type="button"
          class="director-subtab-pill"
          :class="{ active: adminSubTab === 'cleanup' }"
          @click="adminSubTab = 'cleanup'"
        >
          <span>🧹 Wartung &amp; Reset</span>
        </button>
      </div>

      <!-- SUB-TAB 1: TOURNAMENTS & PHASES -->
      <div v-if="adminSubTab === 'tournaments'" class="director-subtab-content">
        <div class="card admin-director-control-card">
          <div class="adcc-head">
            <div>
              <h3>Turnier-Roster &amp; Phasen-Manager</h3>
              <p class="muted small">
                Wechsle Phasen, generiere K.O.-Duelle aus Einreichungen, editiere Turnier-Details oder setze Turniere komplett zurück.
              </p>
            </div>
            <button class="btn btn-sm" @click="showCreateModal = true">
              + Neues Turnier
            </button>
          </div>

          <div class="adcc-list" v-if="tournamentsList.length">
            <div v-for="t in tournamentsList" :key="t.id" class="adcc-row">
              <div class="adcc-info">
                <div class="adcc-title-line">
                  <strong>{{ t.title }}</strong>
                  <span class="badge-genre-tag">{{ t.genre || 'Beat Battle' }}</span>
                  <span class="adcc-prize">💰 {{ t.prize_pool || '1.000 €' }}</span>
                </div>
                <div class="adcc-sub">
                  <span>Status: <strong>{{ statusLabel(t.status) }}</strong></span>
                  <span>•</span>
                  <span>Teilnehmer: {{ t.participants_count || 0 }}</span>
                  <span>•</span>
                  <span>Battles: {{ t.battles_count || 0 }}</span>
                  <span v-if="t.is_no_loss">• 🛡️ No-Loss</span>
                </div>
              </div>

              <div class="adcc-btn-group">
                <select
                  class="input input-sm adcc-status-select"
                  :value="t.status"
                  @change="adminChangeTournamentPhase(t, $event.target.value)"
                  title="Phase wechseln"
                >
                  <option value="APPLICATION_OPEN">Bewerbung offen</option>
                  <option value="SUBMISSION_OPEN">Einreichung offen</option>
                  <option value="BATTLES">Battles live</option>
                  <option value="CLOSED">Beendet</option>
                  <option value="DRAFT">Entwurf</option>
                </select>

                <button
                  class="btn btn-sm btn-generate-b"
                  @click="autoGenerateRoundBattles(t.id)"
                  title="Erzeugt 1v1 Duelle für alle freigegebenen Einreichungen"
                >
                  ⚔️ Battles generieren
                </button>

                <button
                  class="btn ghost btn-sm"
                  @click="openEditTournament(t)"
                  title="Turnierdaten, Preisgeld und Beschreibung anpassen"
                >
                  ✏️ Bearbeiten
                </button>

                <button
                  class="btn ghost btn-sm btn-reset-t"
                  @click="resetTournamentData(t)"
                  title="Battles und Einreichungen dieses Turniers zurücksetzen"
                >
                  ⚡ Reset
                </button>

                <button
                  class="btn ghost btn-sm"
                  @click="openTournamentDetail(t)"
                  title="Turnierbaum &amp; Detailseite öffnen"
                >
                  Öffnen →
                </button>

                <button
                  class="btn ghost btn-sm btn-delete-t"
                  @click="adminDeleteTournament(t)"
                  title="Turnier komplett löschen"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted" style="padding: 32px; text-align: center;">
            <p>Noch keine Turniere vorhanden.</p>
            <button class="btn btn-sm" style="margin-top: 10px;" @click="showCreateModal = true">
              + Jetzt erstes Turnier anlegen
            </button>
          </div>
        </div>
      </div>

      <!-- SUB-TAB 2: RANKS & SEASON RESET -->
      <div v-if="adminSubTab === 'ranks'" class="director-subtab-content">
        <!-- Danger Box: Season Reset -->
        <div class="card rank-danger-card">
          <div class="rdc-header">
            <div class="rdc-icon-badge">⚡</div>
            <div>
              <h3>Globaler Saison-Reset // Season Circuit '26</h3>
              <p class="muted small">
                Setzt die Ranked Points (RP) und Leaderboard-Ränge aller Artists auf 0 zurück. 
                Alle Contender starten wieder im Bronze-Tier mit einer sauberen Bilanz in die neue Saison.
              </p>
            </div>
          </div>
          <div class="rdc-action-bar">
            <div class="rdc-info-chip">
              <span>Betroffene Profile im Leaderboard:</span>
              <strong>{{ leaderboardRows.length }} Artists</strong>
            </div>
            <button class="btn btn-danger-glow" @click="showSeasonResetConfirm = true">
              ⚡ Alle Ränge auf 0 RP zurücksetzen (Season-Reset)
            </button>
          </div>
        </div>

        <!-- Artist RP Tuner (Feinjustierung einzelner Artists) -->
        <div class="card rank-tuning-card">
          <div class="rtc-header">
            <h3>🎯 Artist Ranked Points Feinjustierung</h3>
            <p class="muted small">
              Wähle einen beliebigen registrierten Artist aus, um seine Punkte (RP) manuell zu erhöhen, 
              zu verringern oder auf einen exakten Wert zu setzen — ohne Backend-Code!
            </p>
          </div>

          <div class="rtc-controls-row">
            <div class="rtc-select-artist-col">
              <label class="form-label-small">Artist auswählen:</label>
              <select v-model="selectedArtistProfileId" class="input" @change="onArtistSelectForTuning">
                <option :value="null" disabled>Artist wählen...</option>
                <option
                  v-for="artist in (registeredProfilesList.length ? registeredProfilesList : leaderboardRows)"
                  :key="artist.id"
                  :value="artist.id"
                >
                  {{ artist.name || artist.user?.username || ('Profil #' + artist.id) }} 
                  ({{ getArtistCurrentRP(artist.id) }} RP • {{ getArtistCurrentTier(artist.id) }})
                </option>
              </select>
            </div>

            <div class="rtc-points-input-col" v-if="selectedArtistProfileId">
              <label class="form-label-small">Neuer RP-Punktestand:</label>
              <div class="rtc-points-input-wrap">
                <input
                  v-model.number="tuneArtistPointsInput"
                  type="number"
                  min="0"
                  class="input rtc-rp-number-input"
                />
                <span class="rp-unit">RP</span>
              </div>
            </div>

            <div class="rtc-quick-buttons" v-if="selectedArtistProfileId">
              <button type="button" class="btn ghost btn-sm" @click="tuneArtistPointsInput += 50">+50 RP</button>
              <button type="button" class="btn ghost btn-sm" @click="tuneArtistPointsInput += 100">+100 RP</button>
              <button type="button" class="btn ghost btn-sm" @click="tuneArtistPointsInput += 500">+500 RP</button>
              <button type="button" class="btn ghost btn-sm" @click="tuneArtistPointsInput = Math.max(0, tuneArtistPointsInput - 50)">-50 RP</button>
              <button type="button" class="btn ghost btn-sm btn-quick-zero" @click="tuneArtistPointsInput = 0">Auf 0</button>
            </div>

            <div class="rtc-save-col" v-if="selectedArtistProfileId">
              <button class="btn btn-save-rp" @click="saveArtistPoints(selectedArtistProfileId, tuneArtistPointsInput)">
                💾 Punkte speichern
              </button>
            </div>
          </div>

          <!-- Current Selected Artist Snapshot -->
          <div class="selected-artist-snapshot-card" v-if="selectedArtistProfileId && getSelectedArtistObj()">
            <div class="sasc-avatar">{{ getSelectedArtistObj().name ? getSelectedArtistObj().name.charAt(0) : 'A' }}</div>
            <div class="sasc-meta">
              <h4>{{ getSelectedArtistObj().name }}</h4>
              <span class="sasc-tier-tag">
                <img :src="getTierBadge(getSelectedArtistObj().tier)" class="tiny-tier-icon" alt="" />
                Aktuell: {{ getSelectedArtistObj().tier || 'Bronze' }} ({{ getSelectedArtistObj().ranked_points || 0 }} RP)
              </span>
            </div>
            <div class="sasc-target-preview">
              <span>Vorschau nach Speichern:</span>
              <strong class="highlight-target-rp">{{ tuneArtistPointsInput }} RP</strong>
            </div>
          </div>
        </div>

        <!-- Tier Formula & Thresholds Config -->
        <div class="card rank-formulas-card">
          <div class="rfc-header">
            <h3>⚙️ Tier Schwellenwerte &amp; Punkteregeln</h3>
            <p class="muted small">Passe die Mindest-RP-Grenzen der Tiers sowie Standard-Punkte für Siege und Votes an.</p>
          </div>

          <div class="tier-threshold-grid">
            <div class="tt-item">
              <span class="tt-name">🥉 Bronze</span>
              <input v-model.number="tierConfigForm.bronzeMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
            <div class="tt-item">
              <span class="tt-name">🥈 Silber</span>
              <input v-model.number="tierConfigForm.silberMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
            <div class="tt-item">
              <span class="tt-name">🥇 Gold</span>
              <input v-model.number="tierConfigForm.goldMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
            <div class="tt-item">
              <span class="tt-name">💠 Platin</span>
              <input v-model.number="tierConfigForm.platinMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
            <div class="tt-item">
              <span class="tt-name">💎 Rubin</span>
              <input v-model.number="tierConfigForm.rubinMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
            <div class="tt-item">
              <span class="tt-name">👑 Legendär</span>
              <input v-model.number="tierConfigForm.legendarMin" type="number" class="input input-sm" />
              <span class="tt-lbl">Min. RP</span>
            </div>
          </div>

          <div class="split-form-row" style="margin-top: 18px;">
            <label class="setting-field">
              <span>Battle-Sieg Bonus RP</span>
              <input v-model.number="tierConfigForm.winRP" type="number" class="input" />
            </label>
            <label class="setting-field">
              <span>Battle-Niederlage RP-Abzug</span>
              <input v-model.number="tierConfigForm.lossRP" type="number" class="input" />
            </label>
            <label class="setting-field">
              <span>Community Vote XP</span>
              <input v-model.number="tierConfigForm.voteRP" type="number" class="input" />
            </label>
          </div>

          <div class="rfc-footer">
            <button class="btn btn-sm" @click="saveTierConfig">
              💾 Tier-Regeln speichern
            </button>
          </div>
        </div>
      </div>

      <!-- SUB-TAB 3: APPLICATIONS & ROSTER -->
      <div v-if="adminSubTab === 'applications'" class="director-subtab-content">
        <div class="card admin-applications-manager-card">
          <div class="aamc-head">
            <div>
              <h3>Bewerber-Roster &amp; Zulassung</h3>
              <p class="muted small">
                Prüfe eingegangene Bewerbungen, lasse Artists für das Turnier zu, lehne unpassende Bewerbungen ab oder lösche Test-Einträge restlos.
              </p>
            </div>
            <button class="btn btn-sm" @click="openManualEnroll">
              ➕ Artist manuell einschreiben
            </button>
          </div>

          <!-- Filters Row -->
          <div class="aamc-filters-bar">
            <div class="aamc-filter-col">
              <span class="filter-lbl">Turnier:</span>
              <select v-model="appTournamentFilter" class="input input-sm">
                <option value="ALL">Alle Turniere</option>
                <option v-for="t in tournamentsList" :key="t.id" :value="t.id">
                  {{ t.title }}
                </option>
              </select>
            </div>

            <div class="aamc-filter-col">
              <span class="filter-lbl">Status:</span>
              <div class="pill-group">
                <button
                  type="button"
                  class="filter-pill"
                  :class="{ active: appStatusFilter === 'ALL' }"
                  @click="appStatusFilter = 'ALL'"
                >
                  Alle ({{ allApplicationsList.length }})
                </button>
                <button
                  type="button"
                  class="filter-pill"
                  :class="{ active: appStatusFilter === 'PENDING' }"
                  @click="appStatusFilter = 'PENDING'"
                >
                  Ausstehend ({{ pendingApplications.length }})
                </button>
                <button
                  type="button"
                  class="filter-pill"
                  :class="{ active: appStatusFilter === 'APPROVED' }"
                  @click="appStatusFilter = 'APPROVED'"
                >
                  Zugelassen
                </button>
                <button
                  type="button"
                  class="filter-pill"
                  :class="{ active: appStatusFilter === 'REJECTED' }"
                  @click="appStatusFilter = 'REJECTED'"
                >
                  Abgelehnt
                </button>
              </div>
            </div>
          </div>

          <!-- Applications List -->
          <div class="aamc-list" v-if="filteredAdminApplications.length">
            <div v-for="app in filteredAdminApplications" :key="app.id" class="aamc-row">
              <div class="aamc-avatar">{{ app.artist_name ? app.artist_name.charAt(0) : 'A' }}</div>
              <div class="aamc-info">
                <div class="aamc-title-line">
                  <strong>{{ app.artist_name }}</strong>
                  <span class="badge-status-pill" :class="app.status.toLowerCase()">{{ app.status }}</span>
                  <span class="aamc-tourney-tag">{{ app.tournament_title }}</span>
                  <span class="aamc-time">{{ app.created_at }}</span>
                </div>
                <p class="aamc-msg">"{{ app.message || 'Keine Nachricht hinterlassen' }}"</p>
                <div v-if="app.rejection_reason" class="item-rejection-tag">
                  ❌ Begründung: "{{ app.rejection_reason }}"
                </div>
              </div>

              <div class="aamc-actions">
                <button
                  v-if="app.status === 'PENDING'"
                  class="btn btn-sm btn-accept"
                  @click="handleApplicationDecision(app, 'ACCEPTED')"
                >
                  ✓ Zulassen
                </button>
                <button
                  v-if="app.status === 'PENDING'"
                  class="btn ghost btn-sm btn-reject"
                  @click="promptRejectApplication(app)"
                >
                  ✕ Ablehnen
                </button>
                <button
                  class="btn ghost btn-sm btn-delete-app"
                  @click="deleteApplication(app)"
                  title="Bewerbung restlos löschen"
                >
                  🗑️ Löschen
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted" style="padding: 32px; text-align: center;">
            Keine Bewerbungen mit diesem Filter gefunden.
          </div>
        </div>
      </div>

      <!-- SUB-TAB 4: BATTLES & OVERRULES -->
      <div v-if="adminSubTab === 'battles'" class="director-subtab-content">
        <div class="card admin-battles-manager-card">
          <div class="abmc-head">
            <div>
              <h3>Battles &amp; Jury Overrules</h3>
              <p class="muted small">
                Alle Matchups aller Runden einsehen, Stimmen überwachen, Gewinner manuell bestimmen oder Battles löschen.
              </p>
            </div>
            <div class="abmc-filter">
              <select v-model="battleTournamentFilter" class="input input-sm">
                <option value="ALL">Alle Turniere</option>
                <option v-for="t in tournamentsList" :key="t.id" :value="t.id">
                  {{ t.title }}
                </option>
              </select>
            </div>
          </div>

          <div class="abmc-list" v-if="filteredAdminBattles.length">
            <div v-for="b in filteredAdminBattles" :key="b.id" class="abmc-row">
              <div class="abmc-col-tourney">
                <span class="round-badge">Runde {{ b.round_number || 1 }}</span>
                <strong class="tourney-title">{{ b.tournament_title }}</strong>
                <span class="badge-status-pill" :class="b.status.toLowerCase()">{{ b.status }}</span>
              </div>

              <div class="abmc-col-matchup">
                <div class="fighter fighter-left" :class="{ is_winner: b.winner === 'left' }">
                  <span class="f-name">{{ b.left_profile_name || 'Contender 1' }}</span>
                  <span class="f-votes">{{ b.votes_left || 0 }} Votes</span>
                </div>
                <span class="vs-text">VS</span>
                <div class="fighter fighter-right" :class="{ is_winner: b.winner === 'right' }">
                  <span class="f-name">{{ b.right_profile_name || 'Contender 2' }}</span>
                  <span class="f-votes">{{ b.votes_right || 0 }} Votes</span>
                </div>
              </div>

              <div class="abmc-col-actions">
                <div class="overrule-btn-group" v-if="b.status !== 'CLOSED'">
                  <button class="btn ghost btn-micro" @click="adminResolveBattle(b, 'left')" title="Links zum Sieger erklären">
                    🏆 Left Win
                  </button>
                  <button class="btn ghost btn-micro" @click="adminResolveBattle(b, 'right')" title="Rechts zum Sieger erklären">
                    🏆 Right Win
                  </button>
                </div>
                <button
                  v-if="b.status === 'CLOSED'"
                  class="btn ghost btn-micro btn-reopen"
                  @click="reopenBattle(b)"
                  title="Abgeschlossenes Battle wieder für Voting öffnen"
                >
                  ↺ Neu öffnen
                </button>
                <button
                  class="btn ghost btn-micro btn-delete-b"
                  @click="deleteBattle(b)"
                  title="Battle löschen"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
          <div v-else class="empty-muted-box muted" style="padding: 32px; text-align: center;">
            Keine Battles für die gewählte Auswahl vorhanden.
          </div>
        </div>
      </div>

      <!-- SUB-TAB 5: CLEANUP & TOOLS -->
      <div v-if="adminSubTab === 'cleanup'" class="director-subtab-content">
        <div class="cleanup-cards-grid">
          <div class="card cleanup-tool-card">
            <div class="ctc-icon">🧹</div>
            <h4>Lokalen Browser-Cache &amp; Testdaten bereinigen</h4>
            <p class="muted small">
              Entfernt gespeicherte Votes, Test-Zustände und lokale Mock-Reste aus dem Browser-Speicher und lädt die echten Serverdaten neu.
            </p>
            <button class="btn btn-sm" @click="cleanTestData">
              Cache jetzt leeren &amp; Reload
            </button>
          </div>

          <div class="card cleanup-tool-card">
            <div class="ctc-icon">🗑️</div>
            <h4>Abgelehnte Bewerbungen löschen</h4>
            <p class="muted small">
              Entfernt alle archivierten und abgelehnten Bewerbungen auf einen Klick aus der Datenbank, um den Roster sauber zu halten.
            </p>
            <button class="btn ghost btn-sm" @click="cleanRejectedApplications">
              Abgelehnte Bewerbungen säubern
            </button>
          </div>

          <div class="card cleanup-tool-card">
            <div class="ctc-icon">🔊</div>
            <h4>Audio-Engine Cache zurücksetzen</h4>
            <p class="muted small">
              Stoppt alle aktiven WebAudio Oszillatoren und Audio-Loops, falls ein Sound im Hintergrund hängen geblieben ist.
            </p>
            <button class="btn ghost btn-sm" @click="resetAudioEngine">
              Audio-Engine stoppen &amp; resetten
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- ================================================================= -->
    <!-- MODAL 1: CREATE TOURNAMENT MODAL -->
    <!-- ================================================================= -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal card create-tourney-modal">
        <div class="modal-header">
          <h3>Neues Turnier erstellen</h3>
          <button class="btn ghost tiny" @click="showCreateModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitCreateTournament">
          <label>
            <span>Turnier-Titel *</span>
            <input v-model.trim="newTournament.title" class="input" required placeholder="z. B. UNYQ Beat Battle Season 2" />
          </label>

          <div class="split-form-row">
            <label>
              <span>Turnier-Format *</span>
              <select v-model="newTournament.format" class="input" @change="onFormatChange">
                <option value="SINGLE_ELIMINATION">K.O.-System (Single Elimination)</option>
                <option value="GROUP_STAGE">Gruppenphase + K.O.-Finals ⭐</option>
                <option value="DOUBLE_ELIMINATION">No-Loss Bracket (Double Elimination)</option>
                <option value="ROUND_ROBIN">Liga (Round Robin)</option>
              </select>
            </label>

            <label>
              <span>Teilnehmer-Slots</span>
              <select v-model.number="newTournament.slots" class="input">
                <option :value="4">4 Artists</option>
                <option :value="8">8 Artists</option>
                <option :value="16">16 Artists (Standard)</option>
                <option :value="24">24 Artists</option>
                <option :value="32">32 Artists</option>
                <option :value="64">64 Artists</option>
              </select>
            </label>
          </div>

          <!-- Gruppenphase Einstellungen wenn Format == GROUP_STAGE -->
          <div v-if="newTournament.format === 'GROUP_STAGE'" class="group-stage-config-box">
            <span class="gsc-title">⚙️ Gruppenphase Konfiguration:</span>
            <div class="split-form-row">
              <label>
                <span>Anzahl Gruppen</span>
                <select v-model.number="newTournament.groups_count" class="input" @change="updateGroupSlots">
                  <option :value="2">2 Gruppen</option>
                  <option :value="4">4 Gruppen (Standard)</option>
                  <option :value="8">8 Gruppen</option>
                </select>
              </label>
              <label>
                <span>Artists pro Gruppe</span>
                <select v-model.number="newTournament.group_size" class="input" @change="updateGroupSlots">
                  <option :value="3">3 Artists</option>
                  <option :value="4">4 Artists (Standard)</option>
                  <option :value="6">6 Artists</option>
                </select>
              </label>
            </div>
            <div class="group-stage-calc-banner">
              💡 <strong>Berechnung:</strong> {{ newTournament.groups_count }} Gruppen à {{ newTournament.group_size }} Artists = <strong>{{ newTournament.groups_count * newTournament.group_size }} Plätze</strong>. Top 2 jeder Gruppe rücken in die K.O.-Endrunde vor.
            </div>
          </div>

          <div class="split-form-row">
            <label>
              <span>Preispool *</span>
              <input v-model.trim="newTournament.prize_pool" class="input" required placeholder="1.500 € Cash + Vinyl Edition" />
            </label>
            <label>
              <span>Genre / Kategorie</span>
              <input v-model.trim="newTournament.genre" class="input" placeholder="Trap / Drill / Lo-Fi" />
            </label>
          </div>

          <div class="split-form-row">
            <label>
              <span>Start-Status</span>
              <select v-model="newTournament.status" class="input">
                <option value="APPLICATION_OPEN">Bewerbung offen</option>
                <option value="SUBMISSION_OPEN">Einreichung offen</option>
                <option value="BATTLES">Battles live</option>
                <option value="DRAFT">Entwurf</option>
              </select>
            </label>
            <label>
              <span>Geplante Rundenanzahl</span>
              <select v-model.number="newTournament.total_rounds" class="input">
                <option :value="1">1 Runde (Direktes Finale)</option>
                <option :value="2">2 Runden (Halbfinale &amp; Finale)</option>
                <option :value="3">3 Runden (Viertelfinale bis Finale)</option>
                <option :value="4">4 Runden (Achtelfinale bis Finale)</option>
                <option :value="5">5 Runden (Grand Tournament)</option>
              </select>
            </label>
          </div>

          <label>
            <span>Beschreibung &amp; Vorgaben</span>
            <textarea v-model.trim="newTournament.description" class="input" rows="3" placeholder="Genre, Sample-Regeln, Rundendauer..."></textarea>
          </label>

          <div class="checkbox-row" v-if="newTournament.format !== 'GROUP_STAGE'">
            <label class="check-label">
              <input type="checkbox" v-model="newTournament.is_no_loss" />
              <span>No-Loss Bracket (Doppelter Ausscheidungsbaum)</span>
            </label>
          </div>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showCreateModal = false">Abbrechen</button>
            <button class="btn" type="submit">Turnier jetzt live schalten 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL: REJECT APPLICATION WITH REASON PROMPT (ADMIN) -->
    <!-- ================================================================= -->
    <div v-if="showRejectModal" class="modal-overlay" @click.self="showRejectModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung ablehnen</h3>
          <button class="btn ghost tiny" @click="showRejectModal = false">✕</button>
        </div>
        <div class="modal-body">
          <p class="muted small">
            Gib dem Künstler <strong>{{ rejectingAppTarget?.artist_name || 'Artist' }}</strong> eine transparente Begründung. Diese wird ihm in seinem Battle Hub und auf der Turnierseite angezeigt.
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
              placeholder="z. B. Hörprobe entspricht nicht den Tempo-/Genre-Vorgaben..."
              required
            ></textarea>
          </label>
        </div>
        <div class="modal-actions">
          <button class="btn ghost" type="button" @click="showRejectModal = false">Abbrechen</button>
          <button class="btn btn-danger" type="button" @click="confirmRejectApplication">Ablehnen &amp; Begründung senden ✕</button>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 2: ARTIST APPLICATION MODAL -->
    <!-- ================================================================= -->
    <div v-if="showApplyModal" class="modal-overlay" @click.self="showApplyModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung für "{{ applyingTournament?.title }}"</h3>
          <button class="btn ghost tiny" @click="showApplyModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitArtistApplication">
          <label>
            <span>Dein Artist- / Producer-Name *</span>
            <input v-model.trim="applicationForm.artist_name" class="input" required />
          </label>
          <label>
            <span>Hörprobe / Demo-Link (SoundCloud, Spotify, Dropbox) *</span>
            <input v-model.trim="applicationForm.demo_link" class="input" required placeholder="https://..." />
          </label>
          <label>
            <span>Nachricht an die Jury (optional)</span>
            <textarea v-model.trim="applicationForm.message" class="input" rows="3" placeholder="Warum möchtest du antreten? Dein Style..."></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showApplyModal = false">Abbrechen</button>
            <button class="btn" type="submit">Bewerbung abschicken 🎤</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 3: SUBMIT ROUND MODAL -->
    <!-- ================================================================= -->
    <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Runde einreichen</h3>
          <button class="btn ghost tiny" @click="showUploadModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitRoundFile">
          <label>
            <span>Track-Titel für diese Runde *</span>
            <input v-model.trim="roundUploadForm.title" class="input" required placeholder="z. B. Runde 1 - Dark Heat" />
          </label>
          <label>
            <span>Audio- / Video-URL (SoundCloud, YouTube, Drive) *</span>
            <input v-model.trim="roundUploadForm.file_url" class="input" required placeholder="https://..." />
          </label>
          <div class="split-form-row">
            <label>
              <span>BPM</span>
              <input v-model.trim="roundUploadForm.bpm" class="input" placeholder="140" />
            </label>
            <label>
              <span>Key / Tonart</span>
              <input v-model.trim="roundUploadForm.key" class="input" placeholder="C# Minor" />
            </label>
          </div>
          <label>
            <span>Lyrics / Songtext / Producer Notes</span>
            <textarea v-model.trim="roundUploadForm.notes" class="input" rows="3" placeholder="Lyrics, VSTs, Mitwirkende..."></textarea>
          </label>

          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showUploadModal = false">Abbrechen</button>
            <button class="btn" type="submit">Runde abschicken 🚀</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL: EDIT APPLICATION MODAL -->
    <!-- ================================================================= -->
    <div v-if="showEditAppModal" class="modal-overlay" @click.self="showEditAppModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Bewerbung bearbeiten &amp; aktualisieren</h3>
          <button class="btn ghost tiny" @click="showEditAppModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitEditApplication">
          <div v-if="editingAppTarget?.rejection_reason" class="hub-rejection-banner">
            <strong>❌ Bisherige Jury-Begründung:</strong>
            <p>"{{ editingAppTarget.rejection_reason }}"</p>
          </div>
          <label>
            <span>Künstler- / Producer-Name *</span>
            <input v-model.trim="editAppForm.artist_name" class="input" required />
          </label>
          <label>
            <span>Hörprobe / Demo-Link *</span>
            <input v-model.trim="editAppForm.demo_link" class="input" required placeholder="https://..." />
          </label>
          <label>
            <span>Nachricht / Überarbeitung an die Jury</span>
            <textarea v-model.trim="editAppForm.message" class="input" rows="3" placeholder="Überarbeitete Infos..."></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showEditAppModal = false">Abbrechen</button>
            <button class="btn" type="submit">Bewerbung speichern &amp; einreichen ✓</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL: EDIT ROUND SUBMISSION MODAL -->
    <!-- ================================================================= -->
    <div v-if="showEditSubModal" class="modal-overlay" @click.self="showEditSubModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Runde {{ editingSubTarget?.round_number || 1 }} bearbeiten</h3>
          <button class="btn ghost tiny" @click="showEditSubModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitEditRound">
          <div v-if="editingSubTarget?.rejection_reason" class="hub-rejection-banner">
            <strong>❌ Bisherige Jury-Begründung:</strong>
            <p>"{{ editingSubTarget.rejection_reason }}"</p>
          </div>
          <label>
            <span>Track-Titel *</span>
            <input v-model.trim="editSubForm.title" class="input" required />
          </label>
          <label>
            <span>Audio- / Video-URL (SoundCloud, YouTube, Drive) *</span>
            <input v-model.trim="editSubForm.file_url" class="input" required />
          </label>
          <label>
            <span>Producer Notes / Lyrics / Feedback-Änderungen</span>
            <textarea v-model.trim="editSubForm.notes" class="input" rows="3"></textarea>
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showEditSubModal = false">Abbrechen</button>
            <button class="btn" type="submit">Runde aktualisieren ✓</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 4: ARTIST INSPECT MODAL -->
    <!-- ================================================================= -->
    <div v-if="inspectedArtist" class="modal-overlay" @click.self="inspectedArtist = null">
      <div class="modal card artist-profile-modal">
        <div class="modal-header">
          <h3>Artist Dossier</h3>
          <button class="btn ghost tiny" @click="inspectedArtist = null">✕</button>
        </div>
        <div class="apm-body">
          <div class="apm-top">
            <div class="apm-avatar">{{ inspectedArtist.name.charAt(0) }}</div>
            <div>
              <h2>{{ inspectedArtist.name }}</h2>
              <span class="apm-tier">{{ inspectedArtist.tier }} Tier • {{ inspectedArtist.ranked_points }} RP</span>
            </div>
            <img :src="getTierBadge(inspectedArtist.tier)" class="apm-badge-img" alt="Badge" />
          </div>

          <div class="apm-stats-grid">
            <div class="apm-stat-box">
              <span class="num">{{ inspectedArtist.wins }}</span>
              <span class="lbl">Siege</span>
            </div>
            <div class="apm-stat-box">
              <span class="num">{{ inspectedArtist.losses }}</span>
              <span class="lbl">Niederlagen</span>
            </div>
            <div class="apm-stat-box">
              <span class="num">{{ getWinRate(inspectedArtist) }}%</span>
              <span class="lbl">Win Rate</span>
            </div>
          </div>

          <div class="apm-achievements">
            <h4>Auszeichnungen in Season '26:</h4>
            <div class="achieve-tags">
              <span class="achieve-pill">⚡ {{ inspectedArtist.wins > 10 ? 'Elite Veteran' : 'Aufsteiger' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 5: EDIT TOURNAMENT MODAL (ADMIN) -->
    <!-- ================================================================= -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Turnier bearbeiten</h3>
          <button class="btn ghost tiny" @click="showEditModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitEditTournament">
          <label>
            <span>Turnier-Titel *</span>
            <input v-model.trim="editTournamentForm.title" class="input" required />
          </label>
          <label>
            <span>Beschreibung &amp; Vorgaben</span>
            <textarea v-model.trim="editTournamentForm.description" class="input" rows="3"></textarea>
          </label>
          <div class="split-form-row">
            <label>
              <span>Preispool Text</span>
              <input v-model.trim="editTournamentForm.prize_pool" class="input" placeholder="z. B. 2.000 € Cash" />
            </label>
            <label>
              <span>Genre / Sparte</span>
              <input v-model.trim="editTournamentForm.genre" class="input" placeholder="z. B. Trap &amp; 808" />
            </label>
          </div>
          <div class="split-form-row">
            <label>
              <span>Status</span>
              <select v-model="editTournamentForm.status" class="input">
                <option value="APPLICATION_OPEN">Bewerbung offen</option>
                <option value="SUBMISSION_OPEN">Einreichung offen</option>
                <option value="BATTLES">Battles live</option>
                <option value="CLOSED">Beendet</option>
                <option value="DRAFT">Entwurf</option>
              </select>
            </label>
            <label>
              <span>End-Datum / Deadline</span>
              <input v-model="editTournamentForm.ends_at" type="datetime-local" class="input" />
            </label>
          </div>
          <div class="checkbox-row">
            <label class="check-label">
              <input type="checkbox" v-model="editTournamentForm.is_no_loss" />
              <span>No-Loss Double Elimination Bracket</span>
            </label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showEditModal = false">Abbrechen</button>
            <button class="btn" type="submit">Änderungen speichern 💾</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 6: MANUAL ARTIST ENROLLMENT (ADMIN) -->
    <!-- ================================================================= -->
    <div v-if="showManualEnrollModal" class="modal-overlay" @click.self="showManualEnrollModal = false">
      <div class="modal card">
        <div class="modal-header">
          <h3>Artist direkt ins Turnier einschreiben</h3>
          <button class="btn ghost tiny" @click="showManualEnrollModal = false">✕</button>
        </div>
        <form class="modal-form" @submit.prevent="submitManualEnroll">
          <label>
            <span>Turnier auswählen *</span>
            <select v-model="manualEnrollForm.tournament_id" class="input" required>
              <option :value="null" disabled>Turnier wählen...</option>
              <option v-for="t in tournamentsList" :key="t.id" :value="t.id">
                {{ t.title }} ({{ statusLabel(t.status) }})
              </option>
            </select>
          </label>
          <label>
            <span>Artist-Profil auswählen *</span>
            <select v-model="manualEnrollForm.profile_id" class="input" required>
              <option :value="null" disabled>Artist wählen...</option>
              <option
                v-for="p in (registeredProfilesList.length ? registeredProfilesList : leaderboardRows)"
                :key="p.id"
                :value="p.id"
              >
                {{ p.name || p.user?.username || ('Profil #' + p.id) }} ({{ p.roles?.join(', ') || 'Artist' }})
              </option>
            </select>
          </label>
          <label>
            <span>Notiz / Jury-Vermerk</span>
            <input v-model.trim="manualEnrollForm.message" class="input" placeholder="Direktzulassung durch Admin" />
          </label>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showManualEnrollModal = false">Abbrechen</button>
            <button class="btn" type="submit">Einschreiben &amp; Freischalten ✓</button>
          </div>
        </form>
      </div>
    </div>

    <!-- ================================================================= -->
    <!-- MODAL 7: SEASON RESET CONFIRMATION (ADMIN DANGER) -->
    <!-- ================================================================= -->
    <div v-if="showSeasonResetConfirm" class="modal-overlay" @click.self="showSeasonResetConfirm = false">
      <div class="modal card modal-danger">
        <div class="modal-header">
          <h3 class="danger-title">⚠️ Globaler Saison-Reset Bestätigung</h3>
          <button class="btn ghost tiny" @click="showSeasonResetConfirm = false">✕</button>
        </div>
        <div class="modal-body-danger">
          <p>
            Möchtest du wirklich <strong>alle Ranked Points (RP) und Leaderboard-Ränge aller Artists auf 0 zurücksetzen</strong>?
          </p>
          <p class="small muted">
            Dieser Schritt startet die neue Saison '26. Alle Contender beginnen wieder mit 0 RP in der Bronze-Division.
          </p>
          <div class="confirm-input-wrap">
            <label>
              <span>Tippe <code>RESET</code> ein, um zu bestätigen:</span>
              <input v-model.trim="seasonResetConfirmText" class="input input-danger" placeholder="RESET" />
            </label>
          </div>
          <div class="modal-actions">
            <button class="btn ghost" type="button" @click="showSeasonResetConfirm = false">Abbrechen</button>
            <button
              class="btn btn-danger"
              :disabled="seasonResetConfirmText.toUpperCase() !== 'RESET' || isResettingRanks"
              @click="confirmResetAllRanks"
            >
              {{ isResettingRanks ? 'Wird zurückgesetzt...' : '⚡ Ja, alle Ränge jetzt auf 0 setzen' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useCurrentProfile } from "../composables/useCurrentProfile";
import { useToast } from "../composables/useToast";
import api from "../api";
import { battleAudio } from "../utils/battleAudioEngine";

/* High-res Vector Rank Badges */
import bronzeRank from "../assets/ranks/bronze-icon.svg";
import silberRank from "../assets/ranks/silber-icon.svg";
import goldRank from "../assets/ranks/gold-icon.svg";
import platinRank from "../assets/ranks/platin-icon.svg";
import rubinRank from "../assets/ranks/rubin.svg";
import legendarRank from "../assets/ranks/legendaer-icon.svg";

const router = useRouter();
const route = useRoute();
const { profile: me, isTeam, fetchProfile } = useCurrentProfile();
const { showToast } = useToast();

const currentRoleMode = ref("TEAM");
const activeTab = ref("tournaments");
const viewMode = ref("grid");

const tournamentSearch = ref("");
const selectedStatusFilter = ref("ALL");
const selectedDivision = ref("ALL");

const showCreateModal = ref(false);
const showApplyModal = ref(false);
const applyingTournament = ref(null);
const showUploadModal = ref(false);
const inspectedArtist = ref(null);

/* Hub & Submissions State */
const myHubSubTab = ref("applications");
const mySubmissionsList = ref([]);
const allSubmissionsList = ref([]);

/* Rejection Modal State */
const showRejectModal = ref(false);
const rejectingAppTarget = ref(null);
const rejectReasonInput = ref("");
const rejectPresets = [
  "Audio-Qualität nicht ausreichend",
  "Genre/Vorgabe verfehlt",
  "Falsches Format oder ungültiger Link",
  "Teilnehmerlimit für diese Division erreicht",
  "Plagiat oder unzulässige Samples",
];

/* Edit Application Modal State */
const showEditAppModal = ref(false);
const editingAppTarget = ref(null);
const editAppForm = ref({
  artist_name: "",
  demo_link: "",
  message: "",
});

/* Edit Round Submission Modal State */
const showEditSubModal = ref(false);
const editingSubTarget = ref(null);
const editSubForm = ref({
  title: "",
  file_url: "",
  notes: "",
});

/* Active audio tracking */
const currentPlayingTrack = ref(null);
const activeParticles = ref([]);

/* Persisted user votes: battleId -> 'left'|'right' */
const userVotes = ref({});

/* User RP & stats */
const userStats = ref({
  rankDisplay: "-",
  tier: "Bronze",
  rp: 0,
  nextTierRP: 800,
});

const userProgressPercent = computed(() => {
  const min = 0;
  const max = userStats.value.nextTierRP || 800;
  const pct = Math.round(((userStats.value.rp - min) / (max - min)) * 100);
  return Math.max(0, Math.min(100, isNaN(pct) ? 0 : pct));
});

/* Arena Navigation Tabs */
const arenaTabs = computed(() => {
  const tabs = [
    { key: "tournaments", label: "Turniere & Arena", icon: "🏆" },
    {
      key: "battles",
      label: "Live Battles",
      icon: "⚔️",
      badge: activeBattlesCount.value ? `${activeBattlesCount.value}` : null,
      badgeClass: "badge-live",
    },
    { key: "leaderboard", label: "Ranked Leaderboard", icon: "🥇" },
    { key: "ranks", label: "Ränge & Tiers", icon: "🛡️" },
    {
      key: "my-tournaments",
      label: "Mein Battle Hub",
      icon: "👤",
      badge: myApplications.value.length ? `${myApplications.value.length}` : null,
    },
    { key: "settings", label: "Arena Settings", icon: "⚙️" },
  ];
  if (currentRoleMode.value === "TEAM") {
    tabs.push({
      key: "admin",
      label: "Admin Director",
      icon: "👑",
      badge: pendingApplications.value.length ? `${pendingApplications.value.length}` : null,
      badgeClass: "badge-warn",
    });
  }
  return tabs;
});

const statusFilters = [
  { key: "ALL", label: "Alle Turniere" },
  { key: "APPLICATION_OPEN", label: "Bewerbung offen" },
  { key: "SUBMISSION_OPEN", label: "Einreichung offen" },
  { key: "BATTLES", label: "Battles live" },
  { key: "CLOSED", label: "Beendet" },
];

const leaderboardDivisions = [
  { key: "ALL", label: "Alle Divisionen" },
  { key: "BEATS", label: "Beat Producers" },
  { key: "VOCAL", label: "Vocalists & Rappers" },
];

/* Tiers Master List */
const tiersMasterList = [
  {
    key: "BRONZE",
    name: "Bronze",
    minRP: 0,
    icon: bronzeRank,
    shortDesc: "Einstieg in den UNYQ Circuit. Sammle erste Siege und Reputation.",
    perks: [
      "Teilnahmeberechtigt an allen offenen Rookie-Turnieren",
      "Community Voting Rechte (+10 RP pro Vote)",
      "Basis Artist-Profil in der UNYQ Arena",
    ],
  },
  {
    key: "SILBER",
    name: "Silber",
    minRP: 800,
    icon: silberRank,
    shortDesc: "Aufsteiger-Klasse mit nachgewiesener Battle-Erfahrung.",
    perks: [
      "Zugang zu silbernen Preisgeld-Turnieren",
      "Erweitertes Waveform-Audio-Profil",
      "10% Rabatt auf UNYQ Sample Packs & Plugins",
    ],
  },
  {
    key: "GOLD",
    name: "Gold",
    minRP: 1600,
    icon: goldRank,
    shortDesc: "Erprobte Battle-Veteranen mit konstanter Win-Rate.",
    perks: [
      "Freilos in Runde 1 bei ausgewählten Turnieren (Bye Seeding)",
      "Jury-Stimmrecht bei Community Showdowns",
      "Exklusives Discord Champion-Badge & Sound-Kits",
    ],
  },
  {
    key: "PLATIN",
    name: "Platin",
    minRP: 2800,
    icon: platinRank,
    shortDesc: "Elite-Produzenten und Top-Tier Artists.",
    perks: [
      "Direkte Qualifikation für Major Turniere",
      "A&R Feedback von UNYQ Records zu jeder Runde",
      "Garantierte Auszahlung bei Erreichen der Top 4",
    ],
  },
  {
    key: "RUBIN",
    name: "Rubin",
    minRP: 4200,
    icon: rubinRank,
    shortDesc: "Apex Champions des UNYQ Circuits.",
    perks: [
      "Offizielle UNYQ Release-Option & Playlist Pitching",
      "Erhöhter Preispool-Anteil (+15% Bonus)",
      "Eigenes Jurymitglied bei Season Finals",
    ],
  },
  {
    key: "LEGENDAER",
    name: "Legendär",
    minRP: 6000,
    icon: legendarRank,
    shortDesc: "Die Hall of Fame der Musikproduktion. Absolute Spitze.",
    perks: [
      "Lebenslanger Champion-Status & Custom 3D Avatar Halo",
      "Vollständige Album-Finanzierung & Vinyl Pressung",
      "Direkter Beteiligungs-Anteil am Arena Gesamt-Jackpot",
    ],
  },
];

const selectedTierDetail = ref(tiersMasterList[2]);

/* Admin Director Navigation & Filters */
const adminSubTab = ref("tournaments");
const appStatusFilter = ref("ALL");
const appTournamentFilter = ref("ALL");
const battleTournamentFilter = ref("ALL");

/* Rank Tuning State */
const selectedArtistProfileId = ref(null);
const tuneArtistPointsInput = ref(0);
const isResettingRanks = ref(false);
const showSeasonResetConfirm = ref(false);
const seasonResetConfirmText = ref("");

/* Tier Formulas & Rules Configuration */
const tierConfigForm = ref({
  bronzeMin: 0,
  silberMin: 800,
  goldMin: 1600,
  platinMin: 2800,
  rubinMin: 4200,
  legendarMin: 6000,
  winRP: 100,
  lossRP: 30,
  voteRP: 10,
});

/* Edit Tournament Modal State */
const showEditModal = ref(false);
const editTournamentForm = ref({
  id: null,
  title: "",
  description: "",
  prize_pool: "",
  genre: "",
  status: "APPLICATION_OPEN",
  is_no_loss: false,
  slots: 16,
  ends_at: "",
});

/* Manual Artist Enrollment Modal State */
const showManualEnrollModal = ref(false);
const manualEnrollForm = ref({
  tournament_id: null,
  profile_id: null,
  message: "Manuell durch Admin zugelassen.",
});

/* Clean Arena Datasets (Zero Mock Fallbacks) */
const tournamentsList = ref([]);
const liveBattlesList = ref([]);
const allBattlesList = ref([]);
const leaderboardRows = ref([]);
const myApplications = ref([]);
const pendingApplications = ref([]);
const allApplicationsList = ref([]);
const registeredProfilesList = ref([]);

/* Arena Settings State */
const arenaSettings = ref({
  votingDuration: "48",
  voteWeighting: "50_50",
  requireMinimumListening: true,
  preventSelfVoting: true,
  audioQuality: "lossless",
  visualizerStyle: "neon_bars",
  autoPlayNextRound: true,
  soundEffectsEnabled: true,
  stageName: "",
  primaryDiscipline: "BEATS",
  tagline: "",
});

/* Computeds */
const activeBattlesCount = computed(() => {
  return liveBattlesList.value.filter((b) => b.status === "OPEN" || b.status === "LIVE").length;
});

const totalPrizePool = computed(() => {
  return tournamentsList.value.reduce((sum, t) => {
    const raw = String(t.prize_pool || "");
    const match = raw.match(/(\d[\d.,]*)/);
    if (!match) return sum;
    const cleanNum = parseInt(match[1].replace(/[.,]/g, ""), 10);
    return sum + (isNaN(cleanNum) ? 0 : cleanNum);
  }, 0);
});

const totalRegisteredArtists = computed(() => {
  return leaderboardRows.value.length || registeredProfilesList.value.length || 0;
});

const spotlightTournament = computed(() => {
  return tournamentsList.value[0] || null;
});

const filteredTournaments = computed(() => {
  return tournamentsList.value.filter((t) => {
    const matchStatus =
      selectedStatusFilter.value === "ALL" || t.status === selectedStatusFilter.value;
    const q = tournamentSearch.value.toLowerCase();
    const matchQuery =
      !q ||
      t.title.toLowerCase().includes(q) ||
      (t.description && t.description.toLowerCase().includes(q)) ||
      (t.genre && t.genre.toLowerCase().includes(q));
    return matchStatus && matchQuery;
  });
});

const filteredLeaderboard = computed(() => {
  return leaderboardRows.value.filter((row) => {
    if (selectedDivision.value === "ALL") return true;
    return row.division === selectedDivision.value;
  });
});

const filteredAdminApplications = computed(() => {
  return allApplicationsList.value.filter((app) => {
    const matchTournament =
      appTournamentFilter.value === "ALL" || app.tournament_id === appTournamentFilter.value;
    let matchStatus = true;
    if (appStatusFilter.value !== "ALL") {
      if (appStatusFilter.value === "APPROVED") {
        matchStatus = app.status === "APPROVED" || app.status === "ACCEPTED";
      } else {
        matchStatus = app.status === appStatusFilter.value;
      }
    }
    return matchTournament && matchStatus;
  });
});

const filteredAdminBattles = computed(() => {
  return allBattlesList.value.filter((b) => {
    if (battleTournamentFilter.value === "ALL") return true;
    return b.tournament_id === battleTournamentFilter.value;
  });
});

/* Helper Methods */
function getTierBadge(tierName) {
  const norm = (tierName || "").toUpperCase();
  if (norm.includes("LEGEN")) return legendarRank;
  if (norm.includes("RUBIN")) return rubinRank;
  if (norm.includes("PLATIN")) return platinRank;
  if (norm.includes("GOLD")) return goldRank;
  if (norm.includes("SILBER")) return silberRank;
  return bronzeRank;
}

function getWinRate(artist) {
  const total = (artist.wins || 0) + (artist.losses || 0);
  if (!total) return 100;
  return Math.round(((artist.wins || 0) / total) * 100);
}

function statusLabel(status) {
  const map = {
    APPLICATION_OPEN: "🟢 Bewerbung offen",
    SUBMISSION_OPEN: "🔵 Einreichung offen",
    BATTLES: "🔴 Battles live",
    CLOSED: "⚪ Beendet",
    DRAFT: "Entwurf",
  };
  return map[status] || status;
}

function formatDate(iso) {
  if (!iso) return "Demnächst";
  return new Date(iso).toLocaleDateString("de-DE", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatCountdown(iso) {
  if (!iso) return "Noch 4 Tage";
  const diff = new Date(iso).getTime() - Date.now();
  if (diff <= 0) return "Abgelaufen";
  const days = Math.floor(diff / 86400000);
  const hours = Math.floor((diff % 86400000) / 3600000);
  return `${days}d ${hours}h verbleibend`;
}

function formatCurrency(val) {
  return new Intl.NumberFormat("de-DE").format(val);
}

function resetFilters() {
  tournamentSearch.value = "";
  selectedStatusFilter.value = "ALL";
}

function setRoleMode(mode) {
  currentRoleMode.value = mode;
  localStorage.setItem("unyq_arena_role_mode", mode);
  showToast(
    mode === "TEAM" ? "👑 Admin & Jury Modus aktiv" : "🎤 Artist & Contender Modus aktiv",
    "info"
  );
}

function openTournamentDetail(tournament) {
  if (!tournament?.id) return;
  battleAudio.stopPlayback();
  currentPlayingTrack.value = null;
  if (route.path.includes("platforms")) {
    router.push({ name: "platform-contest-detail", params: { tournamentId: tournament.id } });
  } else {
    router.push({ name: "tournament-detail", params: { tournamentId: tournament.id } });
  }
}

/* Audio Player Synthesizer / Player Engine */
function toggleAudio(trackKey, artistName) {
  if (currentPlayingTrack.value === trackKey) {
    currentPlayingTrack.value = null;
    battleAudio.stopPlayback();
    showToast(`Wiedergabe pausiert`, "info");
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

async function castVote(battle, side, event) {
  if (hasVoted(battle)) {
    showToast("Du hast für dieses Battle bereits abgestimmt!", "warning");
    return;
  }

  if (side === "left") {
    battle.votes_left++;
  } else {
    battle.votes_right++;
  }

  userVotes.value[battle.id] = side;
  localStorage.setItem("unyq_arena_votes", JSON.stringify(userVotes.value));

  // Audio & Particle FX
  battleAudio.playVoteChime();
  spawnReactionParticle("🗳️", event);
  spawnReactionParticle("🔥", event);

  // User XP
  userStats.value.rp += 10;
  showToast(
    `Vote gezählt für ${side === "left" ? battle.left_profile_name : battle.right_profile_name}! +10 Community RP erhalten ⚡`,
    "success"
  );

  // Backend Sync
  try {
    const subId = side === "left" ? (battle.left_submission || battle.left_submission_id) : (battle.right_submission || battle.right_submission_id);
    if (subId) {
      await api.post("tournament-votes/", {
        battle: battle.id,
        selected_submission: subId,
      });
    }
  } catch {
    // fallback gracefully
  }
}

/* Floating Reactions */
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
    const winner = battle.votes_left >= battle.votes_right ? battle.left_profile_name : battle.right_profile_name;
    battle.winner = battle.votes_left >= battle.votes_right ? "left" : "right";
    showToast(`Battle geschlossen: ${winner} gewinnt durch Stimmenmehrheit! ✨`, "success");
  }

  try {
    await api.post(`tournament-battles/${battle.id}/close/`, winnerSub ? { winner_submission: winnerSub } : {});
  } catch {
    // fallback
  }
}

async function handleApplicationDecision(app, decision) {
  const idx = pendingApplications.value.findIndex((a) => a.id === app.id);
  if (idx !== -1) {
    pendingApplications.value.splice(idx, 1);
  }
  const backendDecision = decision === "ACCEPTED" ? "APPROVED" : "REJECTED";
  try {
    await api.post(`tournament-applications/${app.id}/decision/`, {
      decision: backendDecision,
    });
  } catch {
    // fallback
  }

  if (decision === "ACCEPTED") {
    showToast(`Bewerbung von ${app.artist_name || 'Artist'} angenommen! 🎉`, "success");
  } else {
    showToast(`Bewerbung von ${app.artist_name || 'Artist'} abgelehnt.`, "info");
  }
}

async function autoGenerateRoundBattles(tournamentId) {
  try {
    const { data } = await api.post(`tournaments/${tournamentId}/generate-round-battles/`, {
      round_number: 1,
      auto_approve: true,
    });
    if (data.created_battles_count > 0) {
      showToast(`${data.created_battles_count} Battles automatisch generiert! Turnier ist jetzt live! ⚔️`, "success");
      await loadData();
    } else {
      showToast("Keine Battles erzeugt: Es werden mindestens 2 eingereichte Runden benötigt.", "warning");
    }
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Battles nicht generieren.", "warning");
  }
}

async function adminChangeTournamentPhase(tournament, newStatus) {
  tournament.status = newStatus;
  try {
    await api.patch(`tournaments/${tournament.id}/`, { status: newStatus });
    showToast(`Status für "${tournament.title}" auf "${statusLabel(newStatus)}" geändert.`, "success");
  } catch {
    showToast("Status lokal geändert.", "info");
  }
}

async function adminDeleteTournament(tournament) {
  if (!window.confirm(`Turnier "${tournament.title}" wirklich unwiderruflich löschen?`)) return;
  tournamentsList.value = tournamentsList.value.filter((t) => t.id !== tournament.id);
  try {
    await api.delete(`tournaments/${tournament.id}/`);
    showToast("Turnier gelöscht.", "success");
  } catch {
    showToast("Turnier lokal entfernt.", "info");
  }
}

/* Modals & Creation */
const newTournament = ref({
  title: "",
  description: "",
  prize_pool: "1.500 € Cash + Studio Gear",
  genre: "Trap & 808",
  status: "APPLICATION_OPEN",
  format: "SINGLE_ELIMINATION",
  slots: 16,
  total_rounds: 4,
  groups_count: 4,
  group_size: 4,
  is_no_loss: false,
});

function onFormatChange() {
  if (newTournament.value.format === "GROUP_STAGE") {
    newTournament.value.slots = (newTournament.value.groups_count || 4) * (newTournament.value.group_size || 4);
    newTournament.value.is_no_loss = false;
  } else if (newTournament.value.format === "DOUBLE_ELIMINATION") {
    newTournament.value.is_no_loss = true;
  } else {
    newTournament.value.is_no_loss = false;
  }
}

function updateGroupSlots() {
  if (newTournament.value.format === "GROUP_STAGE") {
    newTournament.value.slots = (newTournament.value.groups_count || 4) * (newTournament.value.group_size || 4);
  }
}

async function submitCreateTournament() {
  const title = newTournament.value.title.trim();
  if (!title) return;

  const startsAt = new Date().toISOString();
  const endsAt = new Date(Date.now() + 14 * 86400000).toISOString();
  const prizeText = newTournament.value.prize_pool || "1.000 € Cash";
  const genreText = newTournament.value.genre || "Trap & 808";
  const formatText = newTournament.value.format || "SINGLE_ELIMINATION";
  const slotsNum = newTournament.value.slots || 16;
  const roundsNum = newTournament.value.total_rounds || 4;
  const groupsCount = newTournament.value.groups_count || 4;
  const groupSize = newTournament.value.group_size || 4;

  const metaDesc = `[Preispool: ${prizeText}] [Genre: ${genreText}] [Format: ${formatText}] [Slots: ${slotsNum}] [TotalRounds: ${roundsNum}] [GroupsCount: ${groupsCount}] [GroupSize: ${groupSize}]\n\n${newTournament.value.description || ""}`;

  const payload = {
    title,
    description: metaDesc,
    status: newTournament.value.status || "APPLICATION_OPEN",
    is_no_loss: Boolean(newTournament.value.is_no_loss || formatText === "DOUBLE_ELIMINATION"),
    voting_mode: "COMMUNITY",
    starts_at: startsAt,
    ends_at: endsAt,
  };

  try {
    const { data } = await api.post("tournaments/", payload);
    tournamentsList.value.unshift({
      ...data,
      prize_pool: prizeText,
      genre: genreText,
      format: formatText,
      slots: slotsNum,
      total_rounds: roundsNum,
      groups_count: groupsCount,
      group_size: groupSize,
      participants_count: 0,
      battles_count: 0,
    });
  } catch {
    tournamentsList.value.unshift({
      id: Date.now(),
      title,
      description: metaDesc,
      prize_pool: prizeText,
      genre: genreText,
      format: formatText,
      slots: slotsNum,
      total_rounds: roundsNum,
      groups_count: groupsCount,
      group_size: groupSize,
      status: newTournament.value.status || "APPLICATION_OPEN",
      is_no_loss: newTournament.value.is_no_loss,
      participants_count: 0,
      battles_count: 0,
      ends_at: endsAt,
    });
  }

  battleAudio.playGong();
  showCreateModal.value = false;
  showToast("Turnier erfolgreich erstellt & live geschaltet! 🏆", "success");
}

const applicationForm = ref({
  artist_name: "",
  demo_link: "",
  message: "",
});

function openSpotlightApply() {
  if (spotlightTournament.value) {
    openApplicationModal(spotlightTournament.value);
  }
}

function openApplicationModal(tournament) {
  applyingTournament.value = tournament;
  applicationForm.value.artist_name =
    arenaSettings.value.stageName || me.value?.name || me.value?.username || "";
  showApplyModal.value = true;
}

async function submitArtistApplication() {
  const tId = applyingTournament.value?.id;
  const artistName = applicationForm.value.artist_name || me.value?.name || "Artist";
  const msg = `Artist: ${artistName} | Demo: ${applicationForm.value.demo_link} | ${applicationForm.value.message || ""}`;

  try {
    const { data } = await api.post("tournament-applications/", {
      tournament: tId,
      message: msg,
    });
    myApplications.value.unshift({
      ...data,
      tournament_title: applyingTournament.value?.title || "Turnier",
    });
  } catch {
    myApplications.value.unshift({
      id: Date.now(),
      tournament_id: tId,
      tournament_title: applyingTournament.value?.title || "Turnier",
      status: "PENDING",
      message: msg,
    });
  }

  showApplyModal.value = false;
  showToast("Bewerbung erfolgreich eingereicht! Viel Erfolg! 🎤", "success");
}

const roundUploadForm = ref({
  tournament_id: null,
  title: "",
  file_url: "",
  bpm: "140",
  key: "C# Minor",
  notes: "",
});

function openUploadRoundModal(app) {
  roundUploadForm.value.tournament_id = app.tournament_id || (tournamentsList.value[0]?.id);
  roundUploadForm.value.title = `${app.tournament_title || 'Turnier'} - Runde`;
  showUploadModal.value = true;
}

async function submitRoundFile() {
  const tId = roundUploadForm.value.tournament_id || (tournamentsList.value[0]?.id);
  const notes = `BPM: ${roundUploadForm.value.bpm} | Key: ${roundUploadForm.value.key} | ${roundUploadForm.value.notes || ""}`;

  try {
    await api.post("tournament-submissions/", {
      tournament: tId,
      round_number: 1,
      title: roundUploadForm.value.title,
      media_url: roundUploadForm.value.file_url,
      notes,
    });
    showToast("Runde erfolgreich eingereicht! Deine Einreichung ist jetzt aktiv. 🚀", "success");
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Runde nicht einreichen.", "warning");
  }

  showUploadModal.value = false;
}

/* Application Rejection with Reason Prompt (Admin) */
function promptRejectApplication(app) {
  rejectingAppTarget.value = app;
  rejectReasonInput.value = "";
  showRejectModal.value = true;
}

async function confirmRejectApplication() {
  if (!rejectingAppTarget.value) return;
  const app = rejectingAppTarget.value;
  const reason = rejectReasonInput.value.trim() || "Kriterien der aktuellen Phase leider nicht erfüllt.";
  try {
    await api.post(`tournament-applications/${app.id}/decision/`, {
      decision: "REJECTED",
      reason: reason,
    });
    app.status = "REJECTED";
    app.rejection_reason = reason;
    showToast(`Bewerbung von ${app.artist_name || 'Artist'} abgelehnt. Begründung übermittelt.`, "info");
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Bewerbung nicht ablehnen.", "warning");
  } finally {
    showRejectModal.value = false;
    rejectingAppTarget.value = null;
    await loadData();
  }
}

/* Edit Application (Artist) */
function openEditApplicationModal(app) {
  editingAppTarget.value = app;
  let demo = "";
  let artist = app.artist_name || "";
  let msg = app.message || "";
  const demoMatch = msg.match(/Demo:\s*([^|]+)/i);
  if (demoMatch) demo = demoMatch[1].trim();
  const artistMatch = msg.match(/Artist:\s*([^|]+)/i);
  if (artistMatch) artist = artistMatch[1].trim();
  const cleanMsg = msg
    .replace(/Artist:\s*[^|]+\|\s*/i, "")
    .replace(/Demo:\s*[^|]+\|\s*/i, "")
    .replace(/\[Jury-Begründung:[^\]]+\]/i, "")
    .trim();

  editAppForm.value = {
    artist_name: artist || arenaSettings.value.stageName || me.value?.name || "",
    demo_link: demo,
    message: cleanMsg,
  };
  showEditAppModal.value = true;
}

async function submitEditApplication() {
  if (!editingAppTarget.value) return;
  const app = editingAppTarget.value;
  const artist = editAppForm.value.artist_name || me.value?.name || "Artist";
  const msg = `Artist: ${artist} | Demo: ${editAppForm.value.demo_link} | ${editAppForm.value.message || ""}`;
  try {
    await api.patch(`tournament-applications/${app.id}/`, {
      message: msg,
    });
    showToast("Bewerbung erfolgreich aktualisiert! Die Jury prüft deine Änderungen. ✓", "success");
    showEditAppModal.value = false;
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Bewerbung nicht aktualisieren.", "warning");
  }
}

/* Edit Round Song Submission (Artist) */
function openEditRoundModal(sub) {
  editingSubTarget.value = sub;
  const cleanNotes = (sub.notes || "").replace(/\[Jury-Begründung:[^\]]+\]/i, "").trim();
  editSubForm.value = {
    title: sub.title || "",
    file_url: sub.media_url || "",
    notes: cleanNotes,
  };
  showEditSubModal.value = true;
}

async function submitEditRound() {
  if (!editingSubTarget.value) return;
  const sub = editingSubTarget.value;
  try {
    await api.patch(`tournament-submissions/${sub.id}/`, {
      title: editSubForm.value.title,
      media_url: editSubForm.value.file_url,
      notes: editSubForm.value.notes,
    });
    showToast("Runde erfolgreich aktualisiert! Status auf Prüfung zurückgestellt. ✓", "success");
    showEditSubModal.value = false;
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Runde nicht aktualisieren.", "warning");
  }
}

function inspectArtist(artist) {
  inspectedArtist.value = artist;
}

async function saveArenaSettings() {
  localStorage.setItem("unyq_arena_settings", JSON.stringify(arenaSettings.value));
  if (isTeam.value) {
    try {
      await api.patch("tournaments/ranked-config/", {
        season: {
          duration_months: 3,
        },
      });
    } catch {
      // fallback
    }
  }
  showToast("Arena Einstellungen erfolgreich gespeichert! 💾", "success");
}

/* Rank Tuning & Artist Selection Helpers */
function getArtistCurrentRP(profileId) {
  const row = leaderboardRows.value.find((r) => r.id === profileId);
  return row ? row.ranked_points : 0;
}

function getArtistCurrentTier(profileId) {
  const row = leaderboardRows.value.find((r) => r.id === profileId);
  return row ? row.tier : "Bronze";
}

function getSelectedArtistObj() {
  if (!selectedArtistProfileId.value) return null;
  const fromLB = leaderboardRows.value.find((r) => r.id === selectedArtistProfileId.value);
  if (fromLB) return fromLB;
  const fromProf = registeredProfilesList.value.find((p) => p.id === selectedArtistProfileId.value);
  if (fromProf) {
    return {
      id: fromProf.id,
      name: fromProf.name || fromProf.user?.username || `Profil #${fromProf.id}`,
      tier: "Bronze",
      ranked_points: 0,
    };
  }
  return null;
}

function onArtistSelectForTuning() {
  const obj = getSelectedArtistObj();
  if (obj) {
    tuneArtistPointsInput.value = obj.ranked_points || 0;
  }
}

/* Admin Rank Actions: Global Season Reset & Individual Tuning */
async function confirmResetAllRanks() {
  isResettingRanks.value = true;
  try {
    const { data } = await api.post("tournaments/reset-ranks/", { mode: "ALL" });
    showToast(data?.message || "⚡ Alle Ränge erfolgreich auf 0 RP zurückgesetzt!", "success");
    showSeasonResetConfirm.value = false;
    seasonResetConfirmText.value = "";
    userStats.value.rp = 0;
    userStats.value.tier = "Bronze";
    userStats.value.rankDisplay = "-";
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Ränge nicht zurücksetzen.", "warning");
  } finally {
    isResettingRanks.value = false;
  }
}

async function saveArtistPoints(profileId, points) {
  if (!profileId) return;
  try {
    await api.post("tournaments/reset-ranks/", {
      profile_id: profileId,
      points: Math.max(0, parseInt(points, 10) || 0),
    });
    showToast(`Punkte erfolgreich auf ${points} RP aktualisiert! 💾`, "success");
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Punkte nicht speichern.", "warning");
  }
}

async function saveTierConfig() {
  localStorage.setItem("unyq_arena_tier_config", JSON.stringify(tierConfigForm.value));
  try {
    await api.patch("tournaments/ranked-config/", {
      tier_thresholds: {
        silber: tierConfigForm.value.silberMin,
        gold: tierConfigForm.value.goldMin,
        platin: tierConfigForm.value.platinMin,
        rubin: tierConfigForm.value.rubinMin,
        legendar: tierConfigForm.value.legendarMin,
      },
    });
  } catch {
    // fallback
  }
  showToast("Rang- und Tier-Regeln erfolgreich gespeichert! 💾", "success");
}

/* Tournament Editing & Reset */
function openEditTournament(t) {
  editTournamentForm.value = {
    id: t.id,
    title: t.title,
    description: t.description || "",
    prize_pool: t.prize_pool || "1.000 €",
    genre: t.genre || "Trap & 808",
    status: t.status || "APPLICATION_OPEN",
    is_no_loss: Boolean(t.is_no_loss),
    slots: t.participants_count || 16,
    ends_at: t.ends_at ? t.ends_at.slice(0, 16) : "",
  };
  showEditModal.value = true;
}

async function submitEditTournament() {
  const tId = editTournamentForm.value.id;
  if (!tId) return;
  const metaDesc = `[Preispool: ${editTournamentForm.value.prize_pool || "1.000 €"}] [Genre: ${editTournamentForm.value.genre || "Beat Battle"}] [Slots: ${editTournamentForm.value.slots || 16}]\n\n${editTournamentForm.value.description || ""}`;
  const payload = {
    title: editTournamentForm.value.title,
    description: metaDesc,
    status: editTournamentForm.value.status,
    is_no_loss: editTournamentForm.value.is_no_loss,
  };
  if (editTournamentForm.value.ends_at) {
    payload.ends_at = new Date(editTournamentForm.value.ends_at).toISOString();
  }
  try {
    await api.patch(`tournaments/${tId}/`, payload);
    showToast("Turnierdaten erfolgreich gespeichert! 💾", "success");
    showEditModal.value = false;
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Turnier nicht aktualisieren.", "warning");
  }
}

async function resetTournamentData(t) {
  if (
    !window.confirm(
      `Turnier "${t.title}" wirklich zurücksetzen?\n\nAlle bisherigen Battles werden gelöscht und Einreichungen auf 'Ausstehend' zurückgestellt.`
    )
  )
    return;
  try {
    const { data } = await api.post(`tournaments/${t.id}/reset-tournament/`, {
      delete_battles: true,
      reset_applications: true,
      new_status: "APPLICATION_OPEN",
    });
    showToast(data?.message || "Turnier zurückgesetzt!", "success");
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Turnier nicht zurücksetzen.", "warning");
  }
}

/* Manual Artist Enrollment */
function openManualEnroll() {
  manualEnrollForm.value = {
    tournament_id: tournamentsList.value[0]?.id || null,
    profile_id: (registeredProfilesList.value[0] || leaderboardRows.value[0])?.id || null,
    message: "Manuell durch Admin zugelassen.",
  };
  showManualEnrollModal.value = true;
}

async function submitManualEnroll() {
  if (!manualEnrollForm.value.tournament_id || !manualEnrollForm.value.profile_id) {
    showToast("Bitte Turnier und Artist auswählen.", "warning");
    return;
  }
  try {
    await api.post("tournament-applications/", {
      tournament: manualEnrollForm.value.tournament_id,
      profile_id: manualEnrollForm.value.profile_id,
      message: manualEnrollForm.value.message || "Direktzulassung durch Admin",
    });
    showToast("Artist erfolgreich ins Turnier eingeschrieben und freigeschaltet! ✓", "success");
    showManualEnrollModal.value = false;
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Artist nicht einschreiben.", "warning");
  }
}

/* Applications and Battles Management */
async function deleteApplication(app) {
  if (!window.confirm(`Bewerbung von "${app.artist_name}" unwiderruflich löschen?`)) return;
  try {
    await api.delete(`tournament-applications/${app.id}/`);
    allApplicationsList.value = allApplicationsList.value.filter((a) => a.id !== app.id);
    pendingApplications.value = pendingApplications.value.filter((a) => a.id !== app.id);
    myApplications.value = myApplications.value.filter((a) => a.id !== app.id);
    showToast("Bewerbung gelöscht. 🗑️", "success");
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Bewerbung nicht löschen.", "warning");
  }
}

async function deleteBattle(battle) {
  if (
    !window.confirm(
      `Battle #${battle.id} (${battle.left_profile_name} vs ${battle.right_profile_name}) wirklich löschen?`
    )
  )
    return;
  try {
    await api.delete(`tournament-battles/${battle.id}/`);
    allBattlesList.value = allBattlesList.value.filter((b) => b.id !== battle.id);
    liveBattlesList.value = liveBattlesList.value.filter((b) => b.id !== battle.id);
    showToast("Battle gelöscht. 🗑️", "success");
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Battle nicht löschen.", "warning");
  }
}

async function reopenBattle(battle) {
  try {
    await api.post(`tournament-battles/${battle.id}/reopen/`);
    battle.status = "OPEN";
    showToast("Battle wieder für Community-Voting geöffnet! ⚔️", "success");
    await loadData();
  } catch (err) {
    showToast(err?.response?.data?.detail || "Konnte Battle nicht wiedereröffnen.", "warning");
  }
}

/* Cleanup Tools */
function cleanTestData() {
  localStorage.removeItem("unyq_arena_votes");
  localStorage.removeItem("unyq_arena_settings");
  userVotes.value = {};
  showToast("Lokaler Cache bereinigt! Lade Daten neu...", "info");
  loadData();
}

async function cleanRejectedApplications() {
  const rejected = allApplicationsList.value.filter((a) => a.status === "REJECTED");
  if (!rejected.length) {
    showToast("Keine abgelehnten Bewerbungen vorhanden.", "info");
    return;
  }
  if (!window.confirm(`${rejected.length} abgelehnte Bewerbungen wirklich endgültig löschen?`))
    return;
  for (const app of rejected) {
    try {
      await api.delete(`tournament-applications/${app.id}/`);
    } catch {
      // ignore
    }
  }
  showToast(`${rejected.length} abgelehnte Bewerbungen bereinigt! 🧹`, "success");
  await loadData();
}

function resetAudioEngine() {
  battleAudio.stopPlayback();
  currentPlayingTrack.value = null;
  showToast("Audio-Engine zurückgesetzt & gestoppt. 🔇", "info");
}

/* Lifecycle & Clean Data Fetching */
async function loadData() {
  // Tournaments
  try {
    const { data } = await api.get("tournaments/");
    const list = Array.isArray(data) ? data : data?.results || [];
    tournamentsList.value = list.map((t) => {
      let prize = t.meta_settings?.prize_pool || "1.000 € Cash";
      let genre = t.meta_settings?.genre || "Trap & 808";
      let format = t.meta_settings?.format || "SINGLE_ELIMINATION";
      let slots = t.meta_settings?.slots || 16;
      let total_rounds = t.meta_settings?.total_rounds || 4;
      let groups_count = t.meta_settings?.groups_count || 4;
      let group_size = t.meta_settings?.group_size || 4;
      if (t.description) {
        const pMatch = t.description.match(/\[Preispool:\s*([^\]]+)\]/i);
        if (pMatch) prize = pMatch[1];
        const gMatch = t.description.match(/\[Genre:\s*([^\]]+)\]/i);
        if (gMatch) genre = gMatch[1];
        const fMatch = t.description.match(/\[Format:\s*([^\]]+)\]/i);
        if (fMatch) format = fMatch[1];
        const sMatch = t.description.match(/\[Slots:\s*(\d+)\]/i);
        if (sMatch) slots = parseInt(sMatch[1], 10);
        const rMatch = t.description.match(/\[TotalRounds:\s*(\d+)\]/i);
        if (rMatch) total_rounds = parseInt(rMatch[1], 10);
        const gcMatch = t.description.match(/\[GroupsCount:\s*(\d+)\]/i);
        if (gcMatch) groups_count = parseInt(gcMatch[1], 10);
        const gsMatch = t.description.match(/\[GroupSize:\s*(\d+)\]/i);
        if (gsMatch) group_size = parseInt(gsMatch[1], 10);
      }
      return {
        ...t,
        prize_pool: prize,
        genre: genre,
        format: format,
        slots: slots,
        total_rounds: total_rounds,
        groups_count: groups_count,
        group_size: group_size,
        participants_count: t.applications_count || 0,
        battles_count: t.battles_count || 0,
      };
    });
  } catch {
    tournamentsList.value = [];
  }

  // Ranked Leaderboard
  try {
    const { data: rankData } = await api.get("tournaments/ranked-overview/");
    const rows = rankData?.rows || [];
    leaderboardRows.value = rows.map((r) => ({
      id: r.profile_id,
      name: r.name || "Artist",
      division: r.roles?.some(
        (role) =>
          role.toLowerCase().includes("vocal") || role.toLowerCase().includes("singer")
      )
        ? "VOCAL"
        : "BEATS",
      tier: r.tier?.label || r.tier?.key || "Bronze",
      ranked_points: r.ranked_points || 0,
      wins: r.wins || 0,
      losses: r.losses || 0,
      isMe: Boolean(rankData.my_profile_id && r.profile_id === rankData.my_profile_id),
    }));

    if (rankData?.my_rank) {
      userStats.value.rankDisplay = `#${rankData.my_rank}`;
    } else {
      userStats.value.rankDisplay = "-";
    }

    const myRow = rows.find((r) => r.profile_id === rankData?.my_profile_id);
    if (myRow) {
      userStats.value.rp = myRow.ranked_points || 0;
      userStats.value.tier = myRow.tier?.label || myRow.tier?.key || "Bronze";
      userStats.value.nextTierRP = myRow.tier?.next_tier_points || 800;
    } else {
      userStats.value.rp = 0;
      userStats.value.tier = "Bronze";
      userStats.value.nextTierRP = 800;
    }
  } catch {
    leaderboardRows.value = [];
  }

  // Battles
  try {
    const { data: battlesData } = await api.get("tournament-battles/");
    const bList = Array.isArray(battlesData) ? battlesData : battlesData?.results || [];
    allBattlesList.value = bList.map((b) => ({
      id: b.id,
      tournament_id: b.tournament,
      tournament_title: b.tournament_title || "Arena Battle",
      round_number: b.round_number || 1,
      status: b.status || "OPEN",
      left_submission: b.left_submission,
      right_submission: b.right_submission,
      left_profile_name: b.left_profile_name || "Artist A",
      left_tier: "Gold",
      left_rp: 1600,
      votes_left: b.votes_left || 0,
      right_profile_name: b.right_profile_name || "Artist B",
      right_tier: "Silber",
      right_rp: 800,
      votes_right: b.votes_right || 0,
      winner: b.winner ? (b.winner === b.left_submission ? "left" : "right") : null,
    }));
    liveBattlesList.value = allBattlesList.value.filter(
      (b) => b.status === "LIVE" || b.status === "OPEN"
    );
  } catch {
    allBattlesList.value = [];
    liveBattlesList.value = [];
  }

  // Applications
  try {
    const { data: appsData } = await api.get("tournament-applications/");
    const aList = Array.isArray(appsData) ? appsData : appsData?.results || [];
    allApplicationsList.value = aList.map((a) => {
      let reason = a.rejection_reason || null;
      if (!reason && a.message) {
        const m = a.message.match(/\[Jury-Begründung:\s*([^\]]+)\]/i);
        if (m) reason = m[1].trim();
      }
      return {
        id: a.id,
        tournament_id: a.tournament,
        tournament_title: a.tournament_title || "Turnier",
        artist_name:
          a.artist_name || a.profile?.name || a.profile?.user?.username || `Artist #${a.profile?.id || a.id}`,
        profile_id: a.profile?.id || a.profile,
        status: a.status || "PENDING",
        message: a.message || "",
        rejection_reason: reason,
        created_at: formatDate(a.created_at),
      };
    });
    pendingApplications.value = allApplicationsList.value.filter(
      (a) => a.status === "PENDING" || a.status === "SUBMITTED"
    );
    myApplications.value = allApplicationsList.value.filter(
      (a) =>
        me.value?.id &&
        (a.profile_id === me.value.id || a.profile?.id === me.value.id)
    );
  } catch {
    allApplicationsList.value = [];
    pendingApplications.value = [];
    myApplications.value = [];
  }

  // Submissions (My submitted round songs & all submissions)
  try {
    const { data: subData } = await api.get("tournament-submissions/");
    const sList = Array.isArray(subData) ? subData : subData?.results || [];
    allSubmissionsList.value = sList.map((s) => {
      let reason = s.rejection_reason || null;
      if (!reason && s.notes) {
        const m = s.notes.match(/\[Jury-Begründung:\s*([^\]]+)\]/i);
        if (m) reason = m[1].trim();
      }
      return {
        ...s,
        rejection_reason: reason,
        tournament_title:
          s.tournament_title ||
          (tournamentsList.value.find((t) => t.id === (s.tournament || s.tournament_id))?.title) ||
          "Turnier",
      };
    });
    mySubmissionsList.value = allSubmissionsList.value.filter(
      (s) =>
        me.value?.id &&
        (s.profile === me.value.id || s.profile?.id === me.value.id || s.profile_id === me.value.id)
    );
  } catch {
    allSubmissionsList.value = [];
    mySubmissionsList.value = [];
  }

  // Registered Profiles for Admin
  if (isTeam.value) {
    try {
      const { data: pData } = await api.get("profiles/");
      const pList = Array.isArray(pData) ? pData : pData?.results || [];
      registeredProfilesList.value = pList;
    } catch {
      registeredProfilesList.value = [];
    }
  }
}

onMounted(async () => {
  await fetchProfile();

  const savedRole = localStorage.getItem("unyq_arena_role_mode");
  if (savedRole) {
    currentRoleMode.value = savedRole;
  } else {
    currentRoleMode.value = isTeam.value ? "TEAM" : "ARTIST";
  }

  // Route query overrides (e.g. from AdminPlatform hub: /platforms/contests?tab=admin)
  if (route.query.tab === "admin") {
    activeTab.value = "admin";
    currentRoleMode.value = "TEAM";
  }
  if (route.query.subtab) {
    adminSubTab.value = route.query.subtab;
  }

  // Load persisted votes, settings, and tier config
  try {
    const savedVotes = localStorage.getItem("unyq_arena_votes");
    if (savedVotes) userVotes.value = JSON.parse(savedVotes);

    const savedSettings = localStorage.getItem("unyq_arena_settings");
    if (savedSettings)
      arenaSettings.value = { ...arenaSettings.value, ...JSON.parse(savedSettings) };

    const savedTierConfig = localStorage.getItem("unyq_arena_tier_config");
    if (savedTierConfig)
      tierConfigForm.value = { ...tierConfigForm.value, ...JSON.parse(savedTierConfig) };
  } catch {
    // ignore
  }

  await loadData();
});
</script>

<style scoped>
/* =========================================================================
   ARENA BASE & AMBIENCE
   ========================================================================= */
.tournament-arena-page {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 1360px;
  margin: 0 auto;
  padding: 8px 16px 90px;
  position: relative;
  min-height: 100vh;
}

.arena-mesh-glow {
  position: absolute;
  top: 0;
  left: 15%;
  width: 70%;
  height: 380px;
  background: radial-gradient(circle at 50% 30%, rgba(245, 158, 11, 0.16) 0%, rgba(59, 130, 246, 0.12) 45%, transparent 75%);
  pointer-events: none;
  z-index: 0;
}

.arena-secondary-glow {
  position: absolute;
  top: 250px;
  right: 5%;
  width: 450px;
  height: 450px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.08) 0%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Floating Particles */
.reaction-particles-container {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  overflow: hidden;
}

.floating-particle {
  position: absolute;
  font-size: 26px;
  user-select: none;
  animation: floatUpFade 1.6s ease-out forwards;
}

@keyframes floatUpFade {
  0% { transform: translateY(0) scale(0.6); opacity: 1; }
  50% { transform: translateY(-70px) scale(1.3); opacity: 0.9; }
  100% { transform: translateY(-160px) scale(1); opacity: 0; }
}

/* =========================================================================
   ARENA HERO HEADER
   ========================================================================= */
.arena-header {
  display: grid;
  grid-template-columns: 1.35fr 0.95fr;
  gap: 32px;
  align-items: center;
  padding: 38px 36px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.16), transparent 55%),
    radial-gradient(circle at bottom left, rgba(59, 130, 246, 0.12), transparent 45%),
    linear-gradient(135deg, rgba(24, 21, 40, 0.92), rgba(12, 19, 36, 0.96));
  border: 1px solid rgba(245, 158, 11, 0.28);
  border-radius: 28px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.35);
  position: relative;
  overflow: hidden;
  z-index: 1;
}

.arena-status-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 14px;
}

.league-broadcast-badge {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.14);
  border: 1px solid rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.live-pulse-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #f59e0b;
  box-shadow: 0 0 10px #f59e0b;
  animation: arenaPulse 1.6s infinite ease-in-out;
}

@keyframes arenaPulse {
  0%, 100% { transform: scale(0.9); opacity: 0.8; }
  50% { transform: scale(1.3); opacity: 1; box-shadow: 0 0 16px #f59e0b; }
}

.ticker-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 5px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--muted);
  font-size: 12px;
}

.ticker-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #34d399;
}

.arena-title {
  font-size: clamp(2.1rem, 4vw, 3.2rem);
  font-weight: 900;
  margin: 0 0 14px;
  line-height: 1.1;
  color: #fff;
  letter-spacing: -0.02em;
}

.gradient-text {
  background: linear-gradient(120deg, #fbbf24 0%, #f59e0b 50%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.arena-lead {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 24px;
  max-width: 640px;
}

.header-action-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.role-mode-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.toolbar-label {
  font-size: 12px;
  color: var(--muted);
}

.role-pill-group {
  display: inline-flex;
  background: rgba(0, 0, 0, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 999px;
  padding: 4px;
  gap: 4px;
}

.role-pill-btn {
  border: none;
  background: transparent;
  color: var(--muted);
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.role-pill-btn.active {
  background: linear-gradient(135deg, #fbbf24, #f59e0b);
  color: #0f172a;
  box-shadow: 0 2px 10px rgba(245, 158, 11, 0.4);
}

.header-quick-buttons {
  display: flex;
  align-items: center;
  gap: 10px;
}

.btn-create-tournament,
.btn-hero-apply {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-weight: 700;
  border-radius: 12px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 18px rgba(245, 158, 11, 0.4);
  transition: all 0.2s ease;
}

.btn-create-tournament:hover,
.btn-hero-apply:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(245, 158, 11, 0.6);
}

.btn-refresh-arena {
  padding: 8px 14px;
  font-size: 16px;
}

/* Jackpot Card */
.jackpot-spotlight-card {
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 20px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.4);
}

.jsc-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.jsc-badge {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #fbbf24;
}

.jsc-amount {
  font-size: clamp(2rem, 3.2vw, 2.7rem);
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.02em;
  background: linear-gradient(120deg, #fff 30%, #fde68a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.jsc-sub {
  font-size: 12px;
  color: #34d399;
  font-weight: 600;
  margin: -6px 0 0;
}

.asc-stat-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 6px;
}

.asc-stat-box {
  background: rgba(255, 255, 255, 0.04);
  border-radius: 12px;
  padding: 10px 4px;
  text-align: center;
  display: flex;
  flex-direction: column;
}

.asc-stat-box .stat-number {
  font-size: 1.35rem;
  font-weight: 800;
  color: #fff;
}

.asc-stat-box.highlight .stat-number {
  color: #fbbf24;
}

.asc-stat-box.user-rank .stat-number {
  color: #38bdf8;
}

.asc-stat-box .stat-caption {
  font-size: 10px;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.04em;
}

/* User RP Strip */
.user-rp-progress-strip {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-rp-progress-strip:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(245, 158, 11, 0.4);
}

.urps-info {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 6px;
}

.urps-tier {
  color: #fbbf24;
}

.urps-progress-bar {
  width: 100%;
  height: 7px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

.urps-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #38bdf8);
  border-radius: 999px;
  transition: width 0.4s ease;
}

.urps-hint {
  display: block;
  font-size: 10.5px;
  color: var(--muted);
  margin-top: 6px;
  text-align: right;
}

/* =========================================================================
   NAVIGATION TABS
   ========================================================================= */
.arena-navigation-bar {
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 8px 12px;
  position: sticky;
  top: 12px;
  backdrop-filter: blur(16px);
  z-index: 50;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
}

.tabs-scroll-container {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  width: 100%;
  scrollbar-width: none;
}

.tabs-scroll-container::-webkit-scrollbar {
  display: none;
}

.nav-tab-button {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  border: none;
  background: transparent;
  color: var(--muted);
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.nav-tab-button:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.nav-tab-button.active {
  background: #fff;
  color: #0f172a;
  box-shadow: 0 4px 14px rgba(255, 255, 255, 0.2);
}

.tab-counter-badge {
  padding: 2px 7px;
  border-radius: 999px;
  font-size: 10.5px;
  font-weight: 800;
}

.tab-counter-badge.badge-live {
  background: #ef4444;
  color: #fff;
}

.tab-counter-badge.badge-warn {
  background: #f59e0b;
  color: #0f172a;
}

/* =========================================================================
   TAB 1: SPOTLIGHT & TOURNAMENTS
   ========================================================================= */
.spotlight-arena-banner {
  display: flex;
  position: relative;
  overflow: hidden;
  border-radius: 24px;
  padding: 36px 34px;
  margin-bottom: 24px;
  background: 
    radial-gradient(circle at top right, rgba(245, 158, 11, 0.22), transparent 50%),
    linear-gradient(135deg, rgba(28, 22, 45, 0.95), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.spotlight-content-wrap {
  position: relative;
  z-index: 2;
  max-width: 820px;
}

.spotlight-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.tag-gold-featured {
  background: rgba(245, 158, 11, 0.2);
  border: 1px solid rgba(245, 158, 11, 0.5);
  color: #fbbf24;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 999px;
  letter-spacing: 0.05em;
}

.tag-status {
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.tag-bracket-type {
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.35);
  color: #60a5fa;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.tag-genre {
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.35);
  color: #c084fc;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.spotlight-heading {
  font-size: clamp(1.8rem, 3vw, 2.4rem);
  font-weight: 900;
  margin: 0 0 10px;
  color: #fff;
}

.spotlight-description {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.6;
  margin: 0 0 22px;
}

.spotlight-features-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 26px;
}

.sf-feature {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 12px 14px;
}

.sf-icon {
  font-size: 24px;
}

.sf-val {
  display: block;
  font-size: 14px;
  font-weight: 800;
  color: #fff;
}

.sf-lbl {
  font-size: 11px;
  color: var(--muted);
}

.spotlight-cta-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-hero-primary {
  padding: 12px 24px;
  font-weight: 800;
  border-radius: 14px;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 20px rgba(245, 158, 11, 0.4);
}

.btn-hero-secondary {
  padding: 12px 22px;
  font-weight: 700;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  color: #fff;
  cursor: pointer;
}

/* Discovery Filter Toolbar */
.discovery-filter-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  margin-bottom: 24px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  flex-wrap: wrap;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 280px;
}

.search-icon-symbol {
  position: absolute;
  left: 14px;
  font-size: 14px;
  pointer-events: none;
  opacity: 0.6;
}

.discovery-search-input {
  width: 100%;
  padding-left: 38px;
  padding-right: 32px;
  height: 42px;
  border-radius: 12px;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  font-size: 13.5px;
}

.search-clear-btn {
  position: absolute;
  right: 12px;
  background: none;
  border: none;
  color: var(--muted);
  cursor: pointer;
  font-size: 12px;
}

.filter-pills-row {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.pill-group {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.filter-pill {
  padding: 8px 14px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.04);
  color: var(--muted);
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill.active {
  background: #fff;
  color: #0f172a;
  border-color: #fff;
}

.pill-group-right {
  display: flex;
  gap: 4px;
  background: rgba(0, 0, 0, 0.35);
  padding: 4px;
  border-radius: 10px;
}

.view-toggle-btn {
  border: none;
  background: transparent;
  color: var(--muted);
  padding: 6px 10px;
  border-radius: 8px;
  cursor: pointer;
}

.view-toggle-btn.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* Tournaments Grid */
.tournaments-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
  gap: 20px;
}

.tournament-interactive-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: all 0.25s ease;
}

.tournament-interactive-card:hover {
  transform: translateY(-4px);
  border-color: rgba(245, 158, 11, 0.4);
  box-shadow: 0 14px 36px rgba(0, 0, 0, 0.4);
}

.tic-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
}

.tic-status-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.badge-status-pill {
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
}

.badge-status-pill.status-battles {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.badge-status-pill.status-application_open {
  background: rgba(34, 197, 94, 0.15);
  color: #4ade80;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.badge-status-pill.status-submission_open {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.badge-no-loss {
  background: rgba(245, 158, 11, 0.15);
  color: #fbbf24;
  font-size: 10.5px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
}

.badge-genre-tag {
  background: rgba(255, 255, 255, 0.05);
  color: var(--muted);
  font-size: 10.5px;
  padding: 3px 8px;
  border-radius: 999px;
}

.tic-prize-chip {
  font-size: 12.5px;
  font-weight: 800;
  color: #34d399;
}

.tic-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 6px;
  line-height: 1.3;
}

.tic-desc {
  font-size: 13px;
  color: var(--muted);
  line-height: 1.5;
  margin: 0;
}

.roster-slots-bar {
  background: rgba(255, 255, 255, 0.03);
  border-radius: 10px;
  padding: 10px 12px;
}

.rsb-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
  color: var(--muted);
  margin-bottom: 6px;
}

.rsb-labels strong {
  color: #fff;
}

.rsb-track {
  width: 100%;
  height: 6px;
  background: rgba(255, 255, 255, 0.08);
  border-radius: 999px;
  overflow: hidden;
}

.rsb-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #38bdf8);
  border-radius: 999px;
}

.tic-meta-row {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--muted);
}

.tic-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.btn-open-card {
  flex: 1;
  font-weight: 700;
}

/* =========================================================================
   TAB 2: BATTLE SHOWDOWN ARENA
   ========================================================================= */
.battles-showdown-grid {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.battle-duel-card {
  padding: 28px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 20px;
  box-shadow: 0 14px 40px rgba(0, 0, 0, 0.3);
}

.bd-top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.bd-round-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 11.5px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #fbbf24;
  background: rgba(245, 158, 11, 0.12);
  padding: 4px 10px;
  border-radius: 999px;
}

.bd-tourney-name {
  font-size: 13.5px;
  font-weight: 700;
  color: #fff;
}

.bd-status-badge {
  font-size: 11px;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 999px;
}

.bd-status-badge.open {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

/* Duel Ring */
.duel-arena-ring {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 24px;
}

.fighter-card {
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 12px;
  position: relative;
  transition: all 0.25s ease;
}

.fighter-card.winner {
  border-color: rgba(52, 211, 153, 0.6);
  background: rgba(52, 211, 153, 0.06);
}

.fighter-card.voted {
  border-color: rgba(245, 158, 11, 0.6);
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.fighter-avatar-wrap {
  position: relative;
}

.fighter-avatar {
  width: 68px;
  height: 68px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 900;
  border: 3px solid rgba(255, 255, 255, 0.15);
}

.fighter-avatar.right-avatar {
  background: linear-gradient(135deg, #a855f7, #6d28d9);
}

.fighter-tier-icon {
  position: absolute;
  bottom: -6px;
  right: -8px;
  width: 28px;
  height: 28px;
  filter: drop-shadow(0 2px 6px rgba(0, 0, 0, 0.5));
}

.fighter-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
}

.fighter-tier-label {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
  margin-top: 2px;
}

/* Audio Deck */
.fighter-audio-deck {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 4px;
}

.audio-play-trigger-btn {
  width: 100%;
  padding: 8px 12px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  background: rgba(255, 255, 255, 0.06);
  color: #fff;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.audio-play-trigger-btn.playing {
  background: #f59e0b;
  color: #0f172a;
  border-color: #f59e0b;
}

/* Waveform Bars */
.audio-wave-bars {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3px;
  height: 24px;
}

.wave-bar {
  width: 3px;
  height: 6px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 999px;
  transition: height 0.2s ease;
}

.audio-wave-bars.active .wave-bar {
  background: #38bdf8;
  animation: bounceBar 0.8s infinite ease-in-out alternate;
}

@keyframes bounceBar {
  0% { height: 4px; }
  100% { height: 22px; }
}

.fighter-votes-badge {
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.votes-count {
  font-size: 1.3rem;
  font-weight: 900;
  color: #fff;
}

.votes-lbl {
  font-size: 11px;
  color: var(--muted);
}

/* Duel Center */
.duel-center-divider {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.vs-emblem {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 900;
  color: #fbbf24;
  box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
}

.btn-ab-switch {
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.15);
  color: var(--muted);
  font-size: 11px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ab-switch:hover {
  color: #fff;
  border-color: #38bdf8;
}

/* Live Vote Meter */
.live-vote-meter-container {
  display: flex;
  height: 18px;
  border-radius: 999px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.08);
  font-size: 11px;
  font-weight: 800;
  color: #fff;
}

.lvm-bar-left {
  background: linear-gradient(90deg, #3b82f6, #60a5fa);
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding-left: 12px;
  transition: width 0.4s ease;
}

.lvm-bar-right {
  background: linear-gradient(90deg, #c084fc, #a855f7);
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding-right: 12px;
  transition: width 0.4s ease;
}

/* Vote Action Buttons */
.battle-vote-action-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.btn-vote-fighter {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 800;
  border: 1px solid rgba(255, 255, 255, 0.15);
  cursor: pointer;
  transition: all 0.2s ease;
}

.left-vote-btn {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.35);
}

.left-vote-btn:hover:not(:disabled) {
  background: #3b82f6;
  color: #fff;
  box-shadow: 0 4px 18px rgba(59, 130, 246, 0.4);
}

.right-vote-btn {
  background: rgba(168, 85, 247, 0.15);
  color: #c084fc;
  border-color: rgba(168, 85, 247, 0.35);
}

.right-vote-btn:hover:not(:disabled) {
  background: #a855f7;
  color: #fff;
  box-shadow: 0 4px 18px rgba(168, 85, 247, 0.4);
}

.btn-vote-fighter:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-vote-fighter.has-voted {
  background: #34d399 !important;
  color: #0f172a !important;
  border-color: #34d399 !important;
}

/* Crowd Hype Toolbar */
.crowd-hype-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  padding-top: 14px;
}

.hype-title {
  font-size: 12px;
  color: var(--muted);
}

.hype-buttons-group {
  display: flex;
  gap: 8px;
}

.hype-react-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 16px;
  cursor: pointer;
  transition: transform 0.15s ease;
}

.hype-react-btn:hover {
  transform: scale(1.25);
  background: rgba(255, 255, 255, 0.12);
}

/* Admin Bar */
.admin-decision-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  background: rgba(0, 0, 0, 0.35);
  border-radius: 12px;
  padding: 10px 14px;
  flex-wrap: wrap;
}

.admin-verdict-label {
  font-size: 12px;
  font-weight: 700;
  color: #fbbf24;
}

.admin-verdict-buttons {
  display: flex;
  gap: 8px;
}

/* =========================================================================
   TAB 3: LEADERBOARD & PODIUM
   ========================================================================= */
.champions-podium-wrap {
  display: grid;
  grid-template-columns: 1fr 1.25fr 1fr;
  align-items: flex-end;
  gap: 20px;
  margin: 32px 0 40px;
  padding: 0 20px;
}

.podium-pillar {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  cursor: pointer;
  transition: transform 0.25s ease;
}

.podium-pillar:hover {
  transform: translateY(-6px);
}

.podium-avatar-box {
  position: relative;
  margin-bottom: 12px;
}

.podium-avatar {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 900;
  color: #fff;
  border: 3px solid rgba(255, 255, 255, 0.2);
}

.gold-avatar {
  width: 90px;
  height: 90px;
  font-size: 34px;
  background: linear-gradient(135deg, #fbbf24, #b45309);
  border-color: #fef08a;
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.5);
}

.silver-avatar {
  background: linear-gradient(135deg, #cbd5e1, #475569);
  border-color: #f8fafc;
}

.bronze-avatar {
  background: linear-gradient(135deg, #d97706, #78350f);
  border-color: #fed7aa;
}

.podium-badge-gold,
.podium-badge-silver,
.podium-badge-bronze {
  position: absolute;
  top: -6px;
  left: -6px;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 900;
  color: #0f172a;
}

.podium-badge-gold { background: #fef08a; }
.podium-badge-silver { background: #f8fafc; }
.podium-badge-bronze { background: #fed7aa; }

.podium-tier-crest {
  position: absolute;
  bottom: -8px;
  right: -8px;
  width: 32px;
  height: 32px;
}

.podium-tier-crest.legendary-crest {
  width: 42px;
  height: 42px;
  bottom: -10px;
  right: -10px;
}

.crown-animated-halo {
  font-size: 32px;
  margin-bottom: -10px;
  animation: floatCrown 2s infinite ease-in-out;
}

@keyframes floatCrown {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-8px); }
}

.podium-artist-name {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin-bottom: 4px;
}

.podium-artist-name.champion {
  font-size: 1.45rem;
  color: #fef08a;
}

.podium-rp-pill {
  font-size: 12.5px;
  font-weight: 800;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  margin-bottom: 4px;
}

.podium-rp-pill.champion-rp {
  background: rgba(245, 158, 11, 0.25);
  color: #fbbf24;
}

.podium-tier-name {
  font-size: 11px;
  color: var(--muted);
}

.podium-streak-tag {
  font-size: 11px;
  font-weight: 700;
  color: #fbbf24;
  margin: 4px 0 10px;
}

.podium-stand {
  width: 100%;
  border-radius: 18px 18px 0 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255, 255, 255, 0.4);
  font-size: 1.6rem;
  font-weight: 900;
}

.gold-stand {
  height: 140px;
  background: linear-gradient(180deg, rgba(245, 158, 11, 0.35), rgba(15, 23, 42, 0.8));
  border-top: 2px solid #fbbf24;
}

.silver-stand {
  height: 100px;
  background: linear-gradient(180deg, rgba(148, 163, 184, 0.25), rgba(15, 23, 42, 0.8));
  border-top: 2px solid #cbd5e1;
}

.bronze-stand {
  height: 75px;
  background: linear-gradient(180deg, rgba(217, 119, 6, 0.2), rgba(15, 23, 42, 0.8));
  border-top: 2px solid #d97706;
}

/* Leaderboard Table */
.leaderboard-table-card {
  border-radius: 20px;
  padding: 8px 16px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.lt-header-row,
.lt-data-row {
  display: grid;
  grid-template-columns: 80px 2.2fr 1.3fr 1.5fr 1.2fr 1.5fr 90px;
  align-items: center;
  padding: 14px 12px;
}

.lt-header-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--muted);
  letter-spacing: 0.04em;
}

.lt-data-row {
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  transition: background 0.15s ease;
}

.lt-data-row:hover {
  background: rgba(255, 255, 255, 0.03);
}

.lt-data-row.is-user {
  background: rgba(59, 130, 246, 0.1);
  border-left: 3px solid #3b82f6;
}

.rank-pos-number {
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
}

.artist-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.artist-thumb {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: #fff;
}

.artist-names {
  display: flex;
  align-items: center;
  gap: 6px;
}

.artist-names .name {
  color: #fff;
  font-size: 14px;
}

.badge-me-pill {
  background: #3b82f6;
  color: #fff;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 999px;
}

.badge-veteran {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  font-size: 10px;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 999px;
}

.tier-pill-display {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12.5px;
  font-weight: 700;
  color: #fff;
}

.table-tier-icon {
  width: 22px;
  height: 22px;
}

.rp-bold {
  font-size: 14px;
  font-weight: 800;
  color: #fff;
}

.rp-trend {
  display: block;
  font-size: 10.5px;
  color: #34d399;
}

.winrate-bar-wrap {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
}

.winrate-bar-track {
  width: 70px;
  height: 5px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 999px;
  overflow: hidden;
}

.winrate-bar-fill {
  height: 100%;
  background: #34d399;
  border-radius: 999px;
}

/* =========================================================================
   TAB 4: RÄNGE & TIERS SYSTEM
   ========================================================================= */
.ranks-deck-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 18px;
  margin-bottom: 28px;
}

.rank-tier-card {
  padding: 22px 18px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  gap: 10px;
  cursor: pointer;
  position: relative;
  transition: all 0.25s ease;
}

.rank-tier-card:hover {
  transform: translateY(-4px);
  border-color: rgba(245, 158, 11, 0.4);
}

.rank-tier-card.active {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.06);
  box-shadow: 0 0 24px rgba(56, 189, 248, 0.2);
}

.rank-tier-card.is-my-tier {
  border-color: #f59e0b;
}

.rtc-badge-top {
  position: absolute;
  top: -10px;
  background: #f59e0b;
  color: #0f172a;
  font-size: 9.5px;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 999px;
  letter-spacing: 0.04em;
}

.rtc-image-wrap {
  width: 90px;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.rtc-tier-img {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 6px 16px rgba(0, 0, 0, 0.5));
  transition: transform 0.25s ease;
}

.rank-tier-card:hover .rtc-tier-img {
  transform: scale(1.1);
}

.rtc-name {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.rtc-rp-req {
  font-size: 12px;
  font-weight: 700;
  color: #fbbf24;
}

.rtc-perks-summary {
  font-size: 11.5px;
  color: var(--muted);
  line-height: 1.4;
  margin: 0;
}

.rtc-inspect-btn {
  margin-top: auto;
  font-size: 11.5px;
}

/* Deep Dive */
.tier-deep-dive-panel {
  display: grid;
  grid-template-columns: 1fr 1.4fr;
  gap: 32px;
  padding: 36px;
  border-radius: 24px;
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.tdd-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.tdd-img-box {
  width: 130px;
  height: 130px;
}

.tdd-big-img {
  width: 100%;
  height: 100%;
  filter: drop-shadow(0 8px 24px rgba(0, 0, 0, 0.6));
}

.tdd-eyebrow {
  font-size: 11px;
  font-weight: 800;
  color: #38bdf8;
  letter-spacing: 0.06em;
}

.tdd-perks-list h4 {
  font-size: 14px;
  color: #fff;
  margin: 0 0 12px;
}

.tdd-perks-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.tdd-perks-list li {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 13.5px;
  color: #e2e8f0;
}

.perk-check {
  color: #34d399;
  font-weight: 900;
}

/* =========================================================================
   TAB 5: ARTIST HUB & PASSPORT
   ========================================================================= */
.artist-passport-card {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  padding: 24px;
  border-radius: 20px;
  margin-bottom: 24px;
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.apc-stat .lbl {
  display: block;
  font-size: 11.5px;
  color: var(--muted);
  text-transform: uppercase;
  margin-bottom: 4px;
}

.apc-stat .val {
  font-size: 1.3rem;
  font-weight: 800;
  color: #fff;
}

.apc-stat .val.highlight {
  color: #34d399;
}

.my-battles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
}

.my-entry-card {
  padding: 22px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mec-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.mec-date {
  font-size: 11px;
  color: var(--muted);
}

.mec-title {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.mec-msg {
  font-size: 12.5px;
  color: var(--muted);
  line-height: 1.4;
  margin: 0;
}

.mec-actions {
  display: flex;
  gap: 10px;
  margin-top: auto;
}

/* Admin Director Active Tournaments Control Card */
.admin-director-control-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  margin-top: 24px;
}

.adcc-head {
  margin-bottom: 16px;
}

.adcc-head h3 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin: 0 0 4px;
}

.adcc-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.adcc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  padding: 12px 16px;
  gap: 16px;
  flex-wrap: wrap;
}

.adcc-info strong {
  display: block;
  font-size: 14px;
  color: #fff;
}

.adcc-sub {
  font-size: 11.5px;
  color: var(--muted);
}

.adcc-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.adcc-status-select {
  padding: 6px 10px;
  font-size: 12px;
  border-radius: 8px;
  background: rgba(15, 23, 42, 0.85);
  color: #fbbf24;
  border: 1px solid rgba(245, 158, 11, 0.3);
  font-weight: 700;
}

.btn-delete-t {
  color: #f87171 !important;
  padding: 6px 10px;
}

/* =========================================================================
   TAB 6: SETTINGS
   ========================================================================= */
.settings-sections-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
  gap: 22px;
}

.settings-panel {
  padding: 26px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.sp-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 12px;
}

.sp-icon {
  font-size: 20px;
}

.sp-head h3 {
  font-size: 1.15rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.sp-fields {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.setting-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.setting-field span {
  font-size: 12.5px;
  font-weight: 700;
  color: #cbd5e1;
}

.toggle-setting-row {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  cursor: pointer;
  padding: 6px 0;
}

.toggle-setting-row input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-top: 2px;
}

.toggle-setting-row strong {
  display: block;
  font-size: 13px;
  color: #fff;
}

/* =========================================================================
   MODALS & DOSSIER
   ========================================================================= */
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
  max-width: 540px;
  background: rgba(15, 23, 42, 0.98);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 24px;
  padding: 28px;
  box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
}

.modal-header h3 {
  font-size: 1.25rem;
  font-weight: 800;
  color: #fff;
  margin: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.split-form-row {
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

/* Dossier Modal */
.artist-profile-modal {
  max-width: 480px;
}

.apm-top {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.apm-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: linear-gradient(135deg, #f59e0b, #d97706);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 26px;
  font-weight: 900;
  color: #fff;
}

.apm-badge-img {
  width: 50px;
  height: 50px;
  margin-left: auto;
}

.apm-stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  text-align: center;
  margin-bottom: 20px;
}

.apm-stat-box {
  background: rgba(255, 255, 255, 0.04);
  padding: 12px 6px;
  border-radius: 12px;
}

.apm-stat-box .num {
  display: block;
  font-size: 1.35rem;
  font-weight: 800;
  color: #fff;
}

.apm-stat-box .lbl {
  font-size: 11px;
  color: var(--muted);
}

.achieve-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: 6px;
}

.achieve-pill {
  background: rgba(255, 255, 255, 0.06);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11.5px;
  color: #fbbf24;
}

/* =========================================================================
   ADMIN ARENA DIRECTOR STYLES & SUBTABS
   ========================================================================= */
.admin-director-section {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

.director-header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.director-subtabs-row {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  padding: 6px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
}

.director-subtab-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border-radius: 12px;
  background: transparent;
  border: 1px solid transparent;
  color: #94a3b8;
  font-size: 13.5px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
}

.director-subtab-pill:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.05);
}

.director-subtab-pill.active {
  background: rgba(245, 158, 11, 0.16);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
  box-shadow: 0 4px 16px rgba(245, 158, 11, 0.15);
}

.subtab-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  font-size: 11px;
  font-weight: 800;
  color: #fff;
}

.subtab-count.highlight {
  background: rgba(245, 158, 11, 0.25);
  color: #fbbf24;
}

.subtab-count.count-alert {
  background: rgba(239, 68, 68, 0.3);
  color: #f87171;
  animation: pulseDot 2s infinite;
}

.director-subtab-content {
  display: flex;
  flex-direction: column;
  gap: 22px;
}

/* Rank Danger Card (Season Reset) */
.rank-danger-card {
  padding: 24px 28px;
  border-radius: 20px;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.12), rgba(15, 23, 42, 0.9));
  border: 1px solid rgba(239, 68, 68, 0.35);
  box-shadow: 0 10px 30px rgba(239, 68, 68, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rdc-header {
  display: flex;
  gap: 16px;
  align-items: center;
}

.rdc-icon-badge {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  background: rgba(239, 68, 68, 0.2);
  border: 1px solid rgba(239, 68, 68, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.rdc-header h3 {
  margin: 0 0 4px;
  font-size: 1.25rem;
  font-weight: 800;
  color: #fca5a5;
}

.rdc-action-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  padding-top: 14px;
  border-top: 1px solid rgba(239, 68, 68, 0.2);
}

.rdc-info-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #cbd5e1;
}

.rdc-info-chip strong {
  color: #fca5a5;
}

.btn-danger-glow {
  background: linear-gradient(135deg, #ef4444, #b91c1c);
  color: #fff;
  border: none;
  font-weight: 800;
  box-shadow: 0 4px 18px rgba(239, 68, 68, 0.4);
  transition: all 0.2s ease;
}

.btn-danger-glow:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(239, 68, 68, 0.6);
}

/* Rank Tuning Card */
.rank-tuning-card {
  padding: 26px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.rtc-header h3 {
  margin: 0 0 4px;
  font-size: 1.2rem;
  font-weight: 800;
  color: #fff;
}

.rtc-controls-row {
  display: flex;
  align-items: flex-end;
  gap: 14px;
  flex-wrap: wrap;
}

.form-label-small {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
  margin-bottom: 6px;
}

.rtc-select-artist-col {
  flex: 1;
  min-width: 240px;
}

.rtc-points-input-col {
  width: 150px;
}

.rtc-points-input-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.rtc-rp-number-input {
  padding-right: 38px;
  font-weight: 800;
  color: #fbbf24;
}

.rp-unit {
  position: absolute;
  right: 12px;
  font-size: 11px;
  font-weight: 800;
  color: var(--muted);
  pointer-events: none;
}

.rtc-quick-buttons {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.btn-quick-zero {
  color: #f87171 !important;
}

.btn-save-rp {
  background: linear-gradient(135deg, #10b981, #059669);
  color: #fff;
  font-weight: 800;
}

.selected-artist-snapshot-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 14px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.sasc-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 18px;
  color: #fff;
}

.sasc-meta h4 {
  margin: 0 0 4px;
  font-size: 14px;
  color: #fff;
}

.sasc-tier-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--muted);
}

.sasc-target-preview {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 13px;
  color: var(--muted);
}

.highlight-target-rp {
  font-size: 1.1rem;
  color: #34d399;
}

/* Tier Thresholds Grid */
.rank-formulas-card {
  padding: 26px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
}

.rfc-header h3 {
  margin: 0 0 4px;
  font-size: 1.2rem;
  font-weight: 800;
  color: #fff;
}

.tier-threshold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.tt-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
}

.tt-name {
  font-size: 12px;
  font-weight: 800;
  color: #fff;
}

.tt-lbl {
  font-size: 10.5px;
  color: var(--muted);
}

.rfc-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

/* Applications Manager Card */
.admin-applications-manager-card,
.admin-battles-manager-card {
  padding: 24px;
  border-radius: 20px;
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.aamc-head,
.abmc-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
}

.aamc-head h3,
.abmc-head h3 {
  margin: 0 0 4px;
  font-size: 1.2rem;
  font-weight: 800;
  color: #fff;
}

.aamc-filters-bar {
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: wrap;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.aamc-filter-col {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-lbl {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
}

.aamc-list,
.abmc-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.aamc-row {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.aamc-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5cf6, #6d28d9);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 16px;
  color: #fff;
}

.aamc-info {
  flex: 1;
  min-width: 260px;
}

.aamc-title-line {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 4px;
}

.aamc-tourney-tag {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: var(--muted);
}

.aamc-time {
  font-size: 11px;
  color: var(--muted);
  margin-left: auto;
}

.aamc-msg {
  font-size: 12px;
  color: #cbd5e1;
  margin: 0;
}

.aamc-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.btn-delete-app {
  color: #f87171 !important;
}

/* Battles Manager Table */
.abmc-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  padding: 12px 18px;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}

.abmc-col-tourney {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 220px;
}

.tourney-title {
  font-size: 13.5px;
  color: #fff;
}

.abmc-col-matchup {
  display: flex;
  align-items: center;
  gap: 14px;
  flex: 1;
  justify-content: center;
}

.fighter {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 110px;
  padding: 6px 12px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.02);
}

.fighter.is_winner {
  background: rgba(16, 185, 129, 0.15);
  border: 1px solid rgba(16, 185, 129, 0.4);
}

.f-name {
  font-size: 13px;
  font-weight: 700;
  color: #fff;
}

.f-votes {
  font-size: 11px;
  color: #fbbf24;
}

.vs-text {
  font-weight: 900;
  font-size: 12px;
  color: var(--muted);
}

.abmc-col-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.overrule-btn-group {
  display: flex;
  gap: 6px;
}

.btn-reopen {
  color: #38bdf8 !important;
}

.btn-delete-b {
  color: #f87171 !important;
}

/* Cleanup Cards Grid */
.cleanup-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.cleanup-tool-card {
  padding: 24px;
  border-radius: 18px;
  background: rgba(15, 23, 42, 0.78);
  border: 1px solid rgba(255, 255, 255, 0.08);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.ctc-icon {
  font-size: 32px;
}

.cleanup-tool-card h4 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 800;
  color: #fff;
}

.cleanup-tool-card button {
  margin-top: auto;
}

/* Modal Danger */
.modal-danger {
  border-color: rgba(239, 68, 68, 0.5) !important;
  box-shadow: 0 25px 60px rgba(239, 68, 68, 0.25) !important;
}

.danger-title {
  color: #f87171 !important;
}

.modal-body-danger {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.confirm-input-wrap code {
  background: rgba(239, 68, 68, 0.2);
  color: #fca5a5;
  padding: 2px 6px;
  border-radius: 4px;
  font-weight: 800;
}

.input-danger {
  border-color: rgba(239, 68, 68, 0.4) !important;
  font-weight: 800;
  color: #f87171 !important;
  margin-top: 6px;
}

.btn-danger {
  background: #ef4444 !important;
  color: #fff !important;
  font-weight: 800;
}

.btn-danger:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-reset-t {
  color: #fb923c !important;
}

.btn-generate-b {
  background: rgba(59, 130, 246, 0.2);
  border: 1px solid rgba(59, 130, 246, 0.4);
  color: #60a5fa;
}

.btn-generate-b:hover {
  background: rgba(59, 130, 246, 0.35);
}

/* Battle Hub Tabs & Entries */
.hub-tabs-row {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  padding-bottom: 12px;
}

.hub-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.07);
  color: var(--muted);
  font-weight: 700;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.hub-tab-btn:hover {
  background: rgba(255, 255, 255, 0.07);
  color: #fff;
}

.hub-tab-btn.active {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(139, 92, 246, 0.25));
  border-color: rgba(59, 130, 246, 0.5);
  color: #fff;
  box-shadow: 0 4px 16px rgba(59, 130, 246, 0.2);
}

.hub-rejection-banner {
  margin: 12px 0;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(239, 68, 68, 0.08);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-size: 13px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.hub-rejection-banner strong {
  color: #f87171;
  font-weight: 800;
}

.hub-rejection-banner p {
  margin: 0;
  font-style: italic;
  color: #fecaca;
}

.item-rejection-tag {
  display: inline-block;
  margin-top: 6px;
  font-size: 11.5px;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(239, 68, 68, 0.12);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #fca5a5;
  font-weight: 600;
}

/* Group Stage Config Box */
.group-stage-config-box {
  margin: 12px 0;
  padding: 16px;
  border-radius: 14px;
  background: rgba(59, 130, 246, 0.08);
  border: 1px solid rgba(59, 130, 246, 0.25);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.gsc-title {
  font-size: 13px;
  font-weight: 800;
  color: #93c5fd;
}

.group-stage-calc-banner {
  padding: 10px 14px;
  border-radius: 10px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  font-size: 12.5px;
  color: #6ee7b7;
}

/* Rejection Presets */
.reject-presets-wrap {
  margin-top: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preset-label {
  font-size: 12px;
  font-weight: 700;
  color: var(--muted);
}

.reject-presets-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.btn-micro {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: #cbd5e1;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-micro:hover {
  background: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.35);
  color: #fca5a5;
}

.create-tourney-modal {
  max-width: 680px;
  width: 100%;
}

.mt-3 {
  margin-top: 12px;
}

/* Responsive */
@media (max-width: 960px) {
  .arena-header {
    grid-template-columns: 1fr;
  }
  .duel-arena-ring {
    grid-template-columns: 1fr;
  }
  .champions-podium-wrap {
    grid-template-columns: 1fr;
    gap: 28px;
  }
  .tier-deep-dive-panel {
    grid-template-columns: 1fr;
  }
  .artist-passport-card {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
