<template>
  <div class="admin-all-pages-view">
    <!-- Ambient Cyber Glow -->
    <div class="ambient-glow"></div>

    <!-- Header -->
    <header class="page-header card">
      <div class="header-left">
        <div class="header-badge">👑 ADMIN PLATFORM DIRECTORY</div>
        <h1>🗺️ UNYQ Gesamt-Plattform &amp; Seiten-Verzeichnis</h1>
        <p class="subtitle">
          Vollständige Einsicht in alle Hauptseiten, Subseiten, Werkzeuge und Tabs des gesamten UNYQ-Netzwerks inklusive Routen, Zugriffsrechten und Direktzugriff.
        </p>
      </div>
      <div class="header-actions">
        <router-link to="/platforms/admin" class="btn ghost btn-sm">
          ← Zurück zum Admin Hub
        </router-link>
        <router-link to="/platforms/manage-platforms" class="btn btn-sm">
          ⚙️ Plattform-Rechte steuern
        </router-link>
      </div>
    </header>

    <!-- Key Metrics & Counter Strip -->
    <section class="metrics-grid">
      <div class="metric-card card">
        <div class="metric-icon">🌐</div>
        <div class="metric-body">
          <span class="metric-val">{{ totalPagesCount }}</span>
          <span class="metric-lbl">Registrierte Hauptseiten</span>
        </div>
      </div>
      <div class="metric-card card">
        <div class="metric-icon">📑</div>
        <div class="metric-body">
          <span class="metric-val">{{ totalSubpagesCount }}</span>
          <span class="metric-lbl">Spezialisierte Subseiten &amp; Tabs</span>
        </div>
      </div>
      <div class="metric-card card highlight-admin">
        <div class="metric-icon">👑</div>
        <div class="metric-body">
          <span class="metric-val">{{ adminProtectedCount }}</span>
          <span class="metric-lbl">Admin &amp; Team geschützt</span>
        </div>
      </div>
      <div class="metric-card card highlight-arena">
        <div class="metric-icon">⚔️</div>
        <div class="metric-body">
          <span class="metric-val">{{ arenaPagesCount }}</span>
          <span class="metric-lbl">Arena &amp; Contest Routen</span>
        </div>
      </div>
    </section>

    <!-- Filter & Search Toolbar -->
    <section class="toolbar-section card">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Seite, Subseite, Pfad (/tournaments, /platforms...) oder Stichwort suchen..."
          class="input search-input"
        />
        <button v-if="searchQuery" class="clear-search-btn" @click="searchQuery = ''">✕</button>
      </div>

      <!-- Domain Category Filter Pills -->
      <div class="filter-pills-row">
        <span class="f-lbl">Bereich:</span>
        <button
          v-for="cat in categories"
          :key="cat.key"
          class="filter-pill"
          :class="{ active: selectedCategory === cat.key }"
          @click="selectedCategory = cat.key"
        >
          <span>{{ cat.icon }}</span>
          <span>{{ cat.label }}</span>
          <span class="pill-badge">{{ getCategoryCount(cat.key) }}</span>
        </button>
      </div>

      <!-- Role Access Filter Row -->
      <div class="role-filter-row">
        <div class="rf-left">
          <span class="f-lbl">Zugriffslevel:</span>
          <button
            class="rf-pill"
            :class="{ active: selectedRoleFilter === 'ALL' }"
            @click="selectedRoleFilter = 'ALL'"
          >
            Alle Zugriffsstufen
          </button>
          <button
            class="rf-pill role-admin"
            :class="{ active: selectedRoleFilter === 'ADMIN' }"
            @click="selectedRoleFilter = 'ADMIN'"
          >
            👑 Nur Admin
          </button>
          <button
            class="rf-pill role-team"
            :class="{ active: selectedRoleFilter === 'TEAM' }"
            @click="selectedRoleFilter = 'TEAM'"
          >
            ⭐ Team-Exklusiv
          </button>
          <button
            class="rf-pill role-public"
            :class="{ active: selectedRoleFilter === 'PUBLIC' }"
            @click="selectedRoleFilter = 'PUBLIC'"
          >
            👥 Artist &amp; Öffentlich
          </button>
        </div>

        <div class="rf-right">
          <div class="view-mode-toggle">
            <button
              class="vmt-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
              title="Kartenansicht"
            >
              ▦ Detail-Karten
            </button>
            <button
              class="vmt-btn"
              :class="{ active: viewMode === 'compact' }"
              @click="viewMode = 'compact'"
              title="Kompaktansicht"
            >
              ☰ Kompakt-Tabelle
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Results Status Info -->
    <div class="results-info-bar">
      <span>
        Zeige <strong>{{ filteredPages.length }}</strong> von {{ allPages.length }} Plattformen &amp; Hauptseiten 
        (enthält <strong>{{ filteredSubpagesCount }}</strong> Subseiten / Tabs)
      </span>
      <button v-if="searchQuery || selectedCategory !== 'ALL' || selectedRoleFilter !== 'ALL'" class="btn ghost tiny" @click="resetFilters">
        Filter zurücksetzen
      </button>
    </div>

    <!-- MAIN DIRECTORY: GRID VIEW -->
    <section v-if="viewMode === 'grid'" class="pages-grid">
      <article
        v-for="page in filteredPages"
        :key="page.id"
        class="card page-card"
        :class="`domain-${page.domain.toLowerCase()}`"
      >
        <!-- Card Top Bar -->
        <div class="pc-header">
          <div class="pc-icon-wrap">
            <span class="pc-icon">{{ page.icon }}</span>
          </div>
          <div class="pc-title-col">
            <div class="pc-meta-tags">
              <span class="domain-tag" :class="`domain-${page.domain.toLowerCase()}`">
                {{ domainLabel(page.domain) }}
              </span>
              <span class="role-badge" :class="`role-${page.access.toLowerCase()}`">
                {{ roleLabel(page.access) }}
              </span>
              <span v-if="page.isStandalone" class="standalone-tag">Standalone</span>
            </div>
            <h3 class="pc-title">{{ page.name }}</h3>
          </div>
        </div>

        <!-- Route Path Pill -->
        <div class="pc-route-box">
          <code class="route-code">{{ page.route }}</code>
          <button class="btn-copy-route" @click="copyRoute(page.route)" title="Pfad kopieren">
            📋
          </button>
        </div>

        <!-- Description -->
        <p class="pc-desc">{{ page.description }}</p>

        <!-- Subpages Section (if available) -->
        <div v-if="page.subpages && page.subpages.length" class="pc-subpages-box">
          <div class="subpages-header">
            <span class="sh-title">📑 Subseiten &amp; Werkzeuge ({{ page.subpages.length }})</span>
          </div>
          <ul class="subpages-list">
            <li
              v-for="sub in page.subpages"
              :key="sub.name"
              class="subpage-item"
            >
              <div class="sub-info">
                <span class="sub-icon">{{ sub.icon || '▪' }}</span>
                <span class="sub-name">{{ sub.name }}</span>
                <code class="sub-route">{{ sub.route }}</code>
              </div>
              <button
                class="btn-open-sub"
                @click="navigateTo(sub.route)"
                title="Subseite direkt öffnen"
              >
                Öffnen ↗
              </button>
            </li>
          </ul>
        </div>

        <!-- Card Footer Actions -->
        <div class="pc-footer">
          <button
            class="btn btn-sm btn-open-main"
            @click="navigateTo(page.route)"
          >
            <span>Seite direkt aufrufen</span>
            <span class="arrow">↗</span>
          </button>
        </div>
      </article>
    </section>

    <!-- COMPACT TABLE VIEW -->
    <section v-else class="compact-table-section card">
      <div class="table-responsive">
        <table class="all-pages-table">
          <thead>
            <tr>
              <th>Plattform / Seite</th>
              <th>Bereich</th>
              <th>Primärer Pfad</th>
              <th>Zugriffslevel</th>
              <th>Subseiten &amp; Tabs</th>
              <th style="text-align: right;">Aktion</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="page in filteredPages" :key="page.id">
              <td>
                <div class="tbl-name-cell">
                  <span class="tbl-icon">{{ page.icon }}</span>
                  <div>
                    <strong>{{ page.name }}</strong>
                    <p class="muted tiny">{{ page.shortDesc || page.description }}</p>
                  </div>
                </div>
              </td>
              <td>
                <span class="domain-tag" :class="`domain-${page.domain.toLowerCase()}`">
                  {{ domainLabel(page.domain) }}
                </span>
              </td>
              <td>
                <code class="route-code-small">{{ page.route }}</code>
              </td>
              <td>
                <span class="role-badge" :class="`role-${page.access.toLowerCase()}`">
                  {{ roleLabel(page.access) }}
                </span>
              </td>
              <td>
                <div v-if="page.subpages && page.subpages.length" class="tbl-sub-chips">
                  <span
                    v-for="sub in page.subpages"
                    :key="sub.name"
                    class="sub-chip"
                    @click="navigateTo(sub.route)"
                    :title="`Zu: ${sub.route}`"
                  >
                    {{ sub.icon || '•' }} {{ sub.name }} ↗
                  </span>
                </div>
                <span v-else class="muted tiny">-</span>
              </td>
              <td style="text-align: right;">
                <button class="btn btn-micro btn-accent" @click="navigateTo(page.route)">
                  Öffnen ↗
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";
import { useRouter } from "vue-router";
import { useToast } from "../composables/useToast";

const router = useRouter();
const { showToast } = useToast();

const searchQuery = ref("");
const selectedCategory = ref("ALL");
const selectedRoleFilter = ref("ALL");
const viewMode = ref("grid");

const categories = [
  { key: "ALL", label: "Alle Bereiche", icon: "🌐" },
  { key: "STUDIO", label: "Studio Workspace", icon: "🎛️" },
  { key: "ARENA", label: "Contest & Arena", icon: "⚔️" },
  { key: "PLATFORMS", label: "Plattformen & Tools", icon: "🚀" },
  { key: "ADMIN", label: "Admin Control", icon: "👑" },
  { key: "AUTH", label: "Auth & Entry", icon: "🔑" },
];

const allPages = [
  /* =========================================================================
     DOMAIN: STUDIO WORKSPACE CORE
     ========================================================================= */
  {
    id: "studio-dashboard",
    name: "Dashboard & Studio HQ",
    domain: "STUDIO",
    icon: "🎛️",
    route: "/dashboard",
    access: "AUTH",
    description: "Zentrales Studio-Cockpit mit Live-Widgets, aktiven Aufgaben, Release-Fortschritt, Mini-Arena und unterbrechungsfreiem Studio-Audioplayer.",
    subpages: [
      { name: "Arena Mini-Tracker", route: "/tournaments", icon: "⚔️" },
      { name: "Task-Schnellansicht", route: "/tasks", icon: "📋" },
      { name: "Projekt-Schnellzugriff", route: "/projects", icon: "📁" },
    ],
  },
  {
    id: "studio-projects",
    name: "Projekte & Produktionen",
    domain: "STUDIO",
    icon: "📁",
    route: "/projects",
    access: "AUTH",
    description: "Vollständige Übersicht aller Musik-, Album- und Content-Projekte mit Fortschrittsanzeige, Deadlines und Team-Zuweisungen.",
    subpages: [
      { name: "Projekt-Detailseite", route: "/projects/1", icon: "🔍" },
      { name: "Projekt-Dateien & Audio", route: "/projects/1?tab=attachments", icon: "🎵" },
      { name: "Projekt-Finanzen", route: "/platforms/finance/planner/1", icon: "💰" },
    ],
  },
  {
    id: "studio-project-detail",
    name: "Projekt-Detailansicht",
    domain: "STUDIO",
    icon: "🔎",
    route: "/projects/:projectId",
    access: "AUTH",
    description: "Detailansicht eines spezifischen Projekts mit Meilensteinen, Song-Versionen, Notizen, Dateianhängen und Team-Diskussionen.",
    subpages: [
      { name: "Übersicht & Meilensteine", route: "/projects/:projectId", icon: "🚩" },
      { name: "Dateien & Audio-Stems", route: "/projects/:projectId?tab=attachments", icon: "📦" },
    ],
  },
  {
    id: "studio-tasks",
    name: "Aufgaben & Tasks Board",
    domain: "STUDIO",
    icon: "📋",
    route: "/tasks",
    access: "AUTH",
    description: "Interaktives Kanban-Task-Board mit Spalten für Offen, In Arbeit, Feedback und Erledigt inklusive Fälligkeitsdaten.",
    subpages: [
      { name: "Erledigte Aufgaben", route: "/tasks?filter=done", icon: "✓" },
      { name: "Meine Aufgaben", route: "/tasks?filter=mine", icon: "👤" },
      { name: "Team-Aufgaben", route: "/platforms/team-tasks", icon: "👥" },
    ],
  },
  {
    id: "studio-promo-queue",
    name: "Promo Queue & Releases",
    domain: "STUDIO",
    icon: "🚀",
    route: "/promo-queue",
    access: "AUTH",
    description: "Release-Vorbereitungsstraße für Single- und Album-Veröffentlichungen mit Presave-Links, DSP-Checklisten und Kampagnen.",
    subpages: [
      { name: "Release-Kalender", route: "/timeline", icon: "📅" },
      { name: "Social Content Plan", route: "/platforms/content-schedule", icon: "📱" },
    ],
  },
  {
    id: "studio-reviews",
    name: "Review & Freigabe-Queue",
    domain: "STUDIO",
    icon: "🎧",
    route: "/reviews",
    access: "AUTH",
    description: "Kollaborative Feedback- und Freigabeschleife für Song-Entwürfe, Abmischungen, Master und visuelle Artworks.",
    subpages: [
      { name: "Offene Reviews", route: "/reviews?status=pending", icon: "⏳" },
      { name: "Freigegebene Songs", route: "/songs", icon: "✓" },
    ],
  },
  {
    id: "studio-timeline",
    name: "Timeline & Studio-Roadmap",
    domain: "STUDIO",
    icon: "📅",
    route: "/timeline",
    access: "AUTH",
    description: "Visuelle chronologische Roadmap über alle anstehenden Studio-Deadlines, Release-Termine und Team-Events.",
    subpages: [
      { name: "Kalender-Export (iCal)", route: "/timeline?action=export", icon: "📆" },
    ],
  },
  {
    id: "studio-activity",
    name: "Aktivitäts-Feed (Audit)",
    domain: "STUDIO",
    icon: "⚡",
    route: "/activity",
    access: "AUTH",
    description: "Echtzeit-Feed über alle Datei-Uploads, Status-Änderungen, Kommentare und System-Ereignisse im ProArtist-Workspace.",
    subpages: [],
  },
  {
    id: "studio-notifications",
    name: "Benachrichtigungs-Zentrale",
    domain: "STUDIO",
    icon: "🔔",
    route: "/notifications",
    access: "AUTH",
    description: "Zentrale für alle persönlichen Benachrichtigungen, Review-Anfragen, Battle-Ergebnisse und administrative Hinweise.",
    subpages: [],
  },
  {
    id: "studio-points",
    name: "Punkte, Abzeichen & Rewards",
    domain: "STUDIO",
    icon: "⭐",
    route: "/points",
    access: "AUTH",
    description: "UNYQ Team-Punkte, Aktivitäts-Badges, Level-Aufstiege und Belohnungen für aktive Mitarbeit in Produktionen.",
    subpages: [],
  },
  {
    id: "studio-growpro",
    name: "GrowPro Künstler-Entwicklung",
    domain: "STUDIO",
    icon: "📈",
    route: "/growpro",
    access: "AUTH",
    description: "Strategische Zielverfolgung für Artists: Streaming-Meilensteine, Hörer-Ziele und individuelles Karriere-Coaching.",
    subpages: [],
  },
  {
    id: "studio-songs",
    name: "Song-Bibliothek & Stem-Archiv",
    domain: "STUDIO",
    icon: "🎵",
    route: "/songs",
    access: "AUTH",
    description: "Umfassendes Musik-Archiv mit Track-Versionen, BPM/Key-Metadaten, ISRC-Codes, Stems und Wiedergabe-Links.",
    subpages: [
      { name: "Music Player Platform", route: "/platforms/music", icon: "🎧" },
      { name: "Song-Katalog", route: "/platforms/songs", icon: "🎶" },
    ],
  },
  {
    id: "studio-profiles",
    name: "Team-Rollen & Profile",
    domain: "STUDIO",
    icon: "👥",
    route: "/profiles",
    access: "AUTH",
    description: "Mitglieder-Verzeichnis aller Team-Kollegen, Produzenten, Songwriter und Artists inklusive Kontakt und Fähigkeiten.",
    subpages: [
      { name: "Rollen-Verwaltung (Admin)", route: "/platforms/admin/user-role-management", icon: "👑" },
    ],
  },
  {
    id: "studio-chats",
    name: "Chats & Direktnachrichten",
    domain: "STUDIO",
    icon: "💬",
    route: "/chats",
    access: "AUTH",
    description: "Echtzeit-Kommunikation für Produktionen: Projekt-Channels, 1-zu-1 Direktnachrichten und Dateifreigabe.",
    subpages: [],
  },
  {
    id: "studio-search",
    name: "Universelle Studiosuche",
    domain: "STUDIO",
    icon: "🔍",
    route: "/search",
    access: "AUTH",
    description: "Plattformweite Suche über alle Songs, Aufgaben, Projekte, Artists, Dokumente und Notizen.",
    subpages: [],
  },
  {
    id: "studio-me",
    name: "Mein Studio-Profil & Passport",
    domain: "STUDIO",
    icon: "👤",
    route: "/me",
    access: "AUTH",
    description: "Eigenes Künstlerprofil, Bio, verknüpfte Rollen, Achievements, Arena-Bilanz und persönliche Kontoeinstellungen.",
    subpages: [],
  },

  /* =========================================================================
     DOMAIN: ARENA & CONTESTS (DECOUPLED STANDALONE)
     ========================================================================= */
  {
    id: "arena-main",
    name: "UNYQ Arena & Contests Landing",
    domain: "ARENA",
    icon: "🏆",
    route: "/tournaments",
    access: "AUTH",
    isStandalone: true,
    description: "Eigenständige Wettbewerbs-Plattform für Beat Battles, Rap Duells, Community-Voting, Elo-Divisionen und Preisgeld-Ausschüttungen.",
    subpages: [
      { name: "Turnier-Übersicht", route: "/tournaments?tab=tournaments", icon: "🏆" },
      { name: "Live Battles & A/B Votings", route: "/tournaments?tab=battles", icon: "⚔️" },
      { name: "Ranked Leaderboard", route: "/tournaments?tab=leaderboard", icon: "📊" },
      { name: "Battler Passport & Ränge", route: "/tournaments?tab=ranks", icon: "🛡️" },
      { name: "Tournament Director (Admin)", route: "/tournaments?tab=admin", icon: "👑" },
    ],
  },
  {
    id: "arena-detail",
    name: "Turnier-Detailseite & K.O.-Bracket",
    domain: "ARENA",
    icon: "⚔️",
    route: "/tournaments/:tournamentId",
    access: "AUTH",
    isStandalone: true,
    description: "Zentrale Detailansicht eines spezifischen Turniers mit K.O.-Baum, Runden-Einreichungen, Duelle, Jury-Notizen und Phasensteuerung.",
    subpages: [
      { name: "Übersicht & Preispool", route: "/tournaments/:tournamentId?tab=overview", icon: "💰" },
      { name: "Runden-Einreichungen", route: "/tournaments/:tournamentId?tab=submissions", icon: "📤" },
      { name: "Aktive Duelle & Battles", route: "/tournaments/:tournamentId?tab=battles", icon: "⚔️" },
      { name: "Turnierbaum / Bracket", route: "/tournaments/:tournamentId?tab=bracket", icon: "🌿" },
      { name: "Bewerber-Prüfung (Admin)", route: "/tournaments/:tournamentId?tab=applications", icon: "👑" },
    ],
  },

  /* =========================================================================
     DOMAIN: STANDALONE PLATFORM MODULES (/platforms)
     ========================================================================= */
  {
    id: "platform-hub",
    name: "UNYQ Plattform-Center",
    domain: "PLATFORMS",
    icon: "🚀",
    route: "/platforms",
    access: "AUTH",
    description: "Visueller Dock-Launcher für alle spezialisierten Web-Apps und Plattform-Tools des UNYQ-Ökosystems.",
    subpages: [],
  },
  {
    id: "platform-music",
    name: "Music Player Platform",
    domain: "PLATFORMS",
    icon: "🎧",
    route: "/platforms/music",
    access: "AUTH",
    description: "Professioneller Studio-Audioplayer mit Live-Visualizer, Playlists, Waveform-Seeking und unterbrechungsfreier Wiedergabe.",
    subpages: [],
  },
  {
    id: "platform-songs",
    name: "Song- & Beat-Katalog",
    domain: "PLATFORMS",
    icon: "🎶",
    route: "/platforms/songs",
    access: "AUTH",
    description: "Plattformweiter Song- und Beatkatalog mit Genre-Filtern, Lizenz-Status und Direktstreaming.",
    subpages: [],
  },
  {
    id: "platform-team-tasks",
    name: "Team Tasks Platform",
    domain: "PLATFORMS",
    icon: "📋",
    route: "/platforms/team-tasks",
    access: "AUTH",
    description: "Kollaboratives Aufgaben- und Sprintmanagement für teamübergreifende Großprojekte.",
    subpages: [],
  },
  {
    id: "platform-finance",
    name: "UNYQ Finance 2.0",
    domain: "PLATFORMS",
    icon: "💰",
    route: "/platforms/finance",
    access: "AUTH",
    description: "Tag-für-Tag Soll-Besitz-Planer, Zeitraum-Tagesbudget- & Spar-Simulator, Langzeit-Entschuldungs-Analyse und Schulden-Management.",
    subpages: [
      { name: "Cockpit (Übersicht)", route: "/platforms/finance", icon: "🏠" },
      { name: "Tag-für-Tag Besitz-Plan", route: "/platforms/finance?tab=daily", icon: "📅" },
      { name: "Simulator & Smart Tools", route: "/platforms/finance?tab=simulator", icon: "🧮" },
      { name: "Langzeit-Analyse (12–36M)", route: "/platforms/finance?tab=longterm", icon: "📈" },
      { name: "Schulden & Raten", route: "/platforms/finance?tab=debts", icon: "💳" },
      { name: "Buchungen & Alltag", route: "/platforms/finance?tab=entries", icon: "🧾" },
    ],
  },
  {
    id: "platform-finance-planner",
    name: "Finance Budget Planer Tool",
    domain: "PLATFORMS",
    icon: "🧮",
    route: "/platforms/finance/planner/:projectId?",
    access: "AUTH",
    description: "Interaktives Kalkulationstool zur präzisen Modellierung von Produktionsbudgets, Mix/Master-Kosten und Promo-Ausgaben.",
    subpages: [],
  },
  {
    id: "platform-earn",
    name: "Earn & Monetarisierung",
    domain: "PLATFORMS",
    icon: "💎",
    route: "/platforms/earn",
    access: "AUTH",
    description: "Monetarisierungs-Möglichkeiten für Artists: Sync-Deals, Live-Auftritte, Beat-Sales und Tantiemen-Abrechnungen.",
    subpages: [],
  },
  {
    id: "platform-designs",
    name: "Design Studio & Visuals",
    domain: "PLATFORMS",
    icon: "🎨",
    route: "/platforms/designs",
    access: "AUTH",
    description: "Zentrale für Artworks, Single-Cover, Social Banners, Schriftzüge und Corporate Identity des Labels.",
    subpages: [],
  },
  {
    id: "platform-library",
    name: "Knowledge Library",
    domain: "PLATFORMS",
    icon: "📚",
    route: "/platforms/library",
    access: "AUTH",
    description: "Wissensdatenbank mit Musterverträgen, Split-Sheet-Vorlagen, GEMA-Anleitungen und Studio-Richtlinien.",
    subpages: [],
  },
  {
    id: "platform-forum",
    name: "Community Forum",
    domain: "PLATFORMS",
    icon: "🗣️",
    route: "/platforms/forum",
    access: "AUTH",
    description: "Diskussionsforum für Artists, Producer und Teammitglieder zu Produktionstricks, Collabs und Gear-Empfehlungen.",
    subpages: [],
  },
  {
    id: "platform-locations",
    name: "Locations & Studio Scout",
    domain: "PLATFORMS",
    icon: "📍",
    route: "/platforms/locations",
    access: "AUTH",
    description: "Scout-Verzeichnis für Aufnahmestudios, Drehkulissen, Mastering-Suites und Proberäume mit Buchungsanfragen.",
    subpages: [],
  },
  {
    id: "platform-content-studio",
    name: "Content Studio",
    domain: "PLATFORMS",
    icon: "🎬",
    route: "/platforms/content-studio",
    access: "AUTH",
    description: "Social-Media-Produktionssuite für TikTok-Hooks, Instagram Reels, Short-Videos und Promo-Content.",
    subpages: [],
  },
  {
    id: "platform-content-schedule",
    name: "Content Schedule Planner",
    domain: "PLATFORMS",
    icon: "📱",
    route: "/platforms/content-schedule",
    access: "AUTH",
    description: "Zentraler Redaktions- und Veröffentlichungskalender für Medienbeiträge, Teaser und Single-Drops.",
    subpages: [
      { name: "Drag & Drop Wochenplaner", route: "/platforms/content-schedule/planner", icon: "📅" },
    ],
  },
  {
    id: "platform-plugin-guides",
    name: "Plugin Guides & Tutorials",
    domain: "PLATFORMS",
    icon: "🎚️",
    route: "/platforms/plugin-guides",
    access: "AUTH",
    description: "Mixing- und Sounddesign-Guides für EQ, Kompression, Reverb, Saturation und moderne Vocal-Ketten.",
    subpages: [],
  },
  {
    id: "platform-api-center",
    name: "API Center & Integrations",
    domain: "PLATFORMS",
    icon: "🔌",
    route: "/platforms/api-center",
    access: "AUTH",
    description: "Schnittstellen-Verwaltung, API-Token, Webhooks, externe Cloud-Synchronisation und System-Health-Checks.",
    subpages: [],
  },
  {
    id: "platform-fitness",
    name: "Fitness & Vitalität Hub",
    domain: "PLATFORMS",
    icon: "💪",
    route: "/platforms/fitness",
    access: "AUTH",
    description: "Gesundheits- und Vitalitäts-Tracking für Artists: Trainingspläne, Regeneration und körperliche Fitness für Tour und Studio.",
    subpages: [
      { name: "Workout & Tracker Tool", route: "/platforms/fitness/tracker", icon: "🏋️" },
    ],
  },
  {
    id: "platform-todo",
    name: "Todo & Quick-Checklisten",
    domain: "PLATFORMS",
    icon: "✅",
    route: "/platforms/todo",
    access: "AUTH",
    description: "Schnelle persönliche To-Do-Listen, Notizen und Sofort-Aufgaben ohne Projekt-Overhead.",
    subpages: [],
  },
  {
    id: "platform-hhu",
    name: "HHU Lernbegleiter (Mathe 1)",
    domain: "PLATFORMS",
    icon: "🎓",
    route: "/platforms/hhu",
    access: "TEAM",
    description: "Mathe für Informatik 1 an der HHU: Relationen-Analyzer, Äquivalenzhüllen-Generator, Quiz und Klausur-Trainingswerkzeuge.",
    subpages: [],
  },
  {
    id: "platform-extra",
    name: "Extra Plattform-Verzeichnis",
    domain: "PLATFORMS",
    icon: "🧭",
    route: "/platforms/extra",
    access: "AUTH",
    description: "Übersicht aller ergänzenden Plattformen und alternativer Zugangswege im UNYQ-Netzwerk.",
    subpages: [],
  },

  /* =========================================================================
     DOMAIN: ADMIN & GOVERNANCE SUITE
     ========================================================================= */
  {
    id: "admin-hub",
    name: "Admin Control Hub",
    domain: "ADMIN",
    icon: "👑",
    route: "/platforms/admin",
    access: "ADMIN",
    description: "Zentrales Nervenzentrum für Administratoren: System-Metriken, Nutzer-Zahlen, Registrierungsanfragen und Audio-Player-Steuerung.",
    subpages: [
      { name: "Stats- & Reset-Zentrale", route: "/platforms/admin/stats-manager", icon: "📊" },
      { name: "Nutzer- & Rollenverwaltung", route: "/platforms/admin/user-role-management", icon: "👥" },
      { name: "Plattform-Rechte & Sichtbarkeit", route: "/platforms/manage-platforms", icon: "⚙️" },
      { name: "Tournament Animation Lab", route: "/platforms/admin/tournament-animations", icon: "🎬" },
      { name: "Gesamt-Plattform Seitenverzeichnis", route: "/platforms/admin/all-pages", icon: "🗺️" },
      { name: "Tournament Director", route: "/tournaments?tab=admin", icon: "🏆" },
    ],
  },
  {
    id: "admin-all-pages",
    name: "Gesamt-Plattform & Seiten-Verzeichnis",
    domain: "ADMIN",
    icon: "🗺️",
    route: "/platforms/admin/all-pages",
    access: "ADMIN",
    description: "Dieses interaktive Verzeichnis aller 45+ Haupt- und Subseiten mit Live-Routing, Zugriffsfiltern und Direktstart.",
    subpages: [],
  },
  {
    id: "admin-manage-platforms",
    name: "Plattform-Steuerung & Sichtbarkeit",
    domain: "ADMIN",
    icon: "🌐",
    route: "/platforms/manage-platforms",
    access: "ADMIN",
    description: "Modulare Aktivierung/Deaktivierung von Plattformen, Team-Schutz-Policies, Status-Badges und Trennung von Turnier- vs. UNYQ-Studio-Artists.",
    subpages: [],
  },
  {
    id: "admin-user-roles",
    name: "Nutzer- & Rollenverwaltung",
    domain: "ADMIN",
    icon: "👥",
    route: "/platforms/admin/user-role-management",
    access: "ADMIN",
    description: "Eigenständige Plattform zur Vergabe von Rollen, Administrations-Hierarchien (Admin > Team > Contender) und Rechte-Matrizen.",
    subpages: [],
  },
  {
    id: "admin-stats-manager",
    name: "Nutzer-Daten & Stats-Manager",
    domain: "ADMIN",
    icon: "📊",
    route: "/platforms/admin/stats-manager",
    access: "ADMIN",
    description: "Einsicht in reale Nutzerstatistiken, Ranked-RP, Siege/Niederlagen und granularer Reset einzelner Spieler oder der gesamten Saison.",
    subpages: [],
  },
  {
    id: "admin-tournament-animations",
    name: "Tournament Animation Lab",
    domain: "ADMIN",
    icon: "🎬",
    route: "/platforms/admin/tournament-animations",
    access: "ADMIN",
    description: "Admin-Testlabor für Arena-Animationen, Partikel-Effekte, Battle-Showdown-Transitions und Keyframe-Checks.",
    subpages: [],
  },

  /* =========================================================================
     DOMAIN: AUTH & ONBOARDING
     ========================================================================= */
  {
    id: "auth-home",
    name: "Startseite & Welcome Landing",
    domain: "AUTH",
    icon: "🏠",
    route: "/",
    access: "PUBLIC",
    description: "Öffentliche Willkommensseite der UNYQ ProArtist Plattform.",
    subpages: [],
  },
  {
    id: "auth-login",
    name: "Login / Anmelden",
    domain: "AUTH",
    icon: "🔑",
    route: "/login",
    access: "PUBLIC",
    description: "Sicherer Zugang für Artists, Producer und Teammitglieder.",
    subpages: [],
  },
  {
    id: "auth-register",
    name: "Registrierung & Bewerbung",
    domain: "AUTH",
    icon: "✍️",
    route: "/register",
    access: "PUBLIC",
    description: "Registrierungsanfrage für neue Contender, Produzenten oder Studio-Artists.",
    subpages: [],
  },
  {
    id: "auth-set-password",
    name: "Passwort festlegen & Onboarding",
    domain: "AUTH",
    icon: "🛡️",
    route: "/set-password",
    access: "PUBLIC",
    description: "Passwort-Initialisierung nach Team-Einladung oder Passwort-Zurücksetzung.",
    subpages: [],
  },
];

/* Computed Metric Stats */
const totalPagesCount = computed(() => allPages.length);

const totalSubpagesCount = computed(() => {
  return allPages.reduce((acc, p) => acc + (p.subpages ? p.subpages.length : 0), 0);
});

const adminProtectedCount = computed(() => {
  return allPages.filter(p => p.access === "ADMIN" || p.access === "TEAM").length;
});

const arenaPagesCount = computed(() => {
  return allPages.filter(p => p.domain === "ARENA").length;
});

/* Category Count Helper */
function getCategoryCount(catKey) {
  if (catKey === "ALL") return allPages.length;
  return allPages.filter(p => p.domain === catKey).length;
}

/* Filtering */
const filteredPages = computed(() => {
  return allPages.filter((page) => {
    // 1. Category filter
    if (selectedCategory.value !== "ALL" && page.domain !== selectedCategory.value) {
      return false;
    }

    // 2. Role filter
    if (selectedRoleFilter.value !== "ALL") {
      if (selectedRoleFilter.value === "ADMIN" && page.access !== "ADMIN") return false;
      if (selectedRoleFilter.value === "TEAM" && page.access !== "TEAM" && page.access !== "ADMIN") return false;
      if (selectedRoleFilter.value === "PUBLIC" && page.access === "ADMIN") return false;
    }

    // 3. Search query
    const q = searchQuery.value.trim().toLowerCase();
    if (!q) return true;

    const inName = page.name.toLowerCase().includes(q);
    const inRoute = page.route.toLowerCase().includes(q);
    const inDesc = page.description.toLowerCase().includes(q);
    const inDomain = page.domain.toLowerCase().includes(q);
    const inSubpages = page.subpages?.some(
      (s) => s.name.toLowerCase().includes(q) || s.route.toLowerCase().includes(q)
    );

    return inName || inRoute || inDesc || inDomain || inSubpages;
  });
});

const filteredSubpagesCount = computed(() => {
  return filteredPages.value.reduce((acc, p) => acc + (p.subpages ? p.subpages.length : 0), 0);
});

function resetFilters() {
  searchQuery.value = "";
  selectedCategory.value = "ALL";
  selectedRoleFilter.value = "ALL";
}

/* Domain & Role Label Helpers */
function domainLabel(domain) {
  const map = {
    STUDIO: "Studio Workspace",
    ARENA: "Contest & Arena",
    PLATFORMS: "Plattformen & Tools",
    ADMIN: "Admin Control",
    AUTH: "Auth & Entry",
  };
  return map[domain] || domain;
}

function roleLabel(access) {
  const map = {
    ADMIN: "👑 Admin-only",
    TEAM: "⭐ Team-Zugriff",
    AUTH: "👥 Angemeldet",
    PUBLIC: "🌐 Öffentlich",
  };
  return map[access] || access;
}

/* Navigation & Copy */
function navigateTo(routePath) {
  if (!routePath) return;
  // If route has placeholder like :projectId, fallback to 1
  const cleanRoute = routePath.replace(/:projectId\??/, "1").replace(/:tournamentId/, "1");
  router.push(cleanRoute);
}

async function copyRoute(routePath) {
  try {
    await navigator.clipboard.writeText(window.location.origin + routePath);
    showToast(`Pfad ${routePath} in die Zwischenablage kopiert! 📋`, "success");
  } catch {
    showToast(`Pfad: ${routePath}`, "info");
  }
}
</script>

<style scoped>
.admin-all-pages-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
  width: 100%;
  max-width: 1500px;
  margin: 0 auto;
  padding: 16px 20px 80px;
  position: relative;
}

.ambient-glow {
  position: absolute;
  top: 0;
  left: 20%;
  width: 60%;
  height: 380px;
  background: radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, rgba(59, 130, 246, 0.08) 50%, transparent 70%);
  pointer-events: none;
  z-index: 0;
}

/* Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 28px 32px;
  background: 
    radial-gradient(circle at top right, rgba(168, 85, 247, 0.15), transparent 50%),
    linear-gradient(135deg, rgba(28, 22, 45, 0.95), rgba(15, 23, 42, 0.98));
  border: 1px solid rgba(168, 85, 247, 0.3);
  border-radius: 22px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.35);
  position: relative;
  z-index: 1;
  flex-wrap: wrap;
  gap: 16px;
}

.header-badge {
  display: inline-block;
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #c084fc;
  background: rgba(168, 85, 247, 0.15);
  border: 1px solid rgba(168, 85, 247, 0.3);
  padding: 4px 10px;
  border-radius: 999px;
  margin-bottom: 8px;
}

.page-header h1 {
  font-size: 26px;
  font-weight: 800;
  margin: 0 0 6px;
  background: linear-gradient(135deg, #ffffff 40%, #e2e8f0 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.subtitle {
  color: var(--text-muted, #94a3b8);
  font-size: 14px;
  max-width: 780px;
  margin: 0;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
  position: relative;
  z-index: 1;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 22px;
  background: rgba(15, 23, 42, 0.7);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  backdrop-filter: blur(12px);
  transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.18);
}

.metric-icon {
  font-size: 32px;
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.metric-body {
  display: flex;
  flex-direction: column;
}

.metric-val {
  font-size: 24px;
  font-weight: 800;
  color: #fff;
  line-height: 1.1;
}

.metric-lbl {
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  margin-top: 4px;
  font-weight: 500;
}

.highlight-admin {
  border-color: rgba(234, 179, 8, 0.35);
  background: linear-gradient(135deg, rgba(234, 179, 8, 0.08), rgba(15, 23, 42, 0.8));
}

.highlight-arena {
  border-color: rgba(245, 158, 11, 0.35);
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(15, 23, 42, 0.8));
}

/* Toolbar & Filter Section */
.toolbar-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px 24px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 18px;
  backdrop-filter: blur(14px);
  position: relative;
  z-index: 1;
}

.search-box {
  display: flex;
  align-items: center;
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  left: 14px;
  font-size: 16px;
  color: var(--text-muted, #94a3b8);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: 12px 42px 12px 42px;
  font-size: 14px;
  border-radius: 12px;
  background: rgba(2, 6, 23, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.search-input:focus {
  border-color: #a855f7;
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
  outline: none;
}

.clear-search-btn {
  position: absolute;
  right: 12px;
  background: transparent;
  border: none;
  color: var(--text-muted, #94a3b8);
  font-size: 14px;
  cursor: pointer;
  padding: 4px;
}

.clear-search-btn:hover {
  color: #fff;
}

/* Category Filter Pills */
.filter-pills-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.f-lbl {
  font-size: 12px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #94a3b8);
  margin-right: 4px;
}

.filter-pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 14px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.filter-pill.active {
  background: linear-gradient(135deg, rgba(168, 85, 247, 0.25), rgba(59, 130, 246, 0.2));
  border-color: #a855f7;
  color: #fff;
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.2);
}

.pill-badge {
  font-size: 10px;
  padding: 1px 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
}

/* Role Filter Row */
.role-filter-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  padding-top: 6px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.rf-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.rf-pill {
  padding: 5px 12px;
  border-radius: 8px;
  font-size: 11px;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  transition: all 0.2s ease;
}

.rf-pill:hover {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.rf-pill.active {
  background: rgba(255, 255, 255, 0.15);
  border-color: rgba(255, 255, 255, 0.3);
  color: #fff;
}

.rf-pill.role-admin.active {
  background: rgba(234, 179, 8, 0.2);
  border-color: #eab308;
  color: #fef08a;
}

.rf-pill.role-team.active {
  background: rgba(59, 130, 246, 0.2);
  border-color: #3b82f6;
  color: #93c5fd;
}

.rf-pill.role-public.active {
  background: rgba(34, 197, 94, 0.2);
  border-color: #22c55e;
  color: #86efac;
}

/* View Mode Switcher */
.view-mode-toggle {
  display: inline-flex;
  background: rgba(0, 0, 0, 0.3);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  padding: 2px;
}

.vmt-btn {
  background: transparent;
  border: none;
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted, #94a3b8);
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.vmt-btn.active {
  background: rgba(255, 255, 255, 0.15);
  color: #fff;
}

/* Results Info Bar */
.results-info-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: var(--text-muted, #94a3b8);
  padding: 0 4px;
}

/* Grid of Cards */
.pages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 20px;
  position: relative;
  z-index: 1;
}

.page-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  backdrop-filter: blur(14px);
  transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
  position: relative;
}

.page-card:hover {
  transform: translateY(-3px);
  border-color: rgba(168, 85, 247, 0.3);
  box-shadow: 0 16px 36px rgba(0, 0, 0, 0.4);
}

.page-card.domain-admin {
  border-color: rgba(234, 179, 8, 0.2);
}

.page-card.domain-arena {
  border-color: rgba(245, 158, 11, 0.2);
}

/* Card Header */
.pc-header {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  margin-bottom: 14px;
}

.pc-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.pc-title-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  flex: 1;
}

.pc-meta-tags {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.domain-tag {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 2px 8px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

.domain-tag.domain-studio {
  background: rgba(59, 130, 246, 0.15);
  color: #93c5fd;
}

.domain-tag.domain-arena {
  background: rgba(245, 158, 11, 0.18);
  color: #fcd34d;
}

.domain-tag.domain-platforms {
  background: rgba(168, 85, 247, 0.18);
  color: #d8b4fe;
}

.domain-tag.domain-admin {
  background: rgba(234, 179, 8, 0.2);
  color: #fef08a;
}

.role-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 8px;
  border-radius: 6px;
}

.role-badge.role-admin {
  background: rgba(234, 179, 8, 0.15);
  color: #facc15;
  border: 1px solid rgba(234, 179, 8, 0.3);
}

.role-badge.role-team {
  background: rgba(59, 130, 246, 0.15);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.role-badge.role-auth {
  background: rgba(255, 255, 255, 0.06);
  color: #cbd5e1;
}

.role-badge.role-public {
  background: rgba(34, 197, 94, 0.12);
  color: #4ade80;
}

.standalone-tag {
  font-size: 9px;
  font-weight: 800;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(236, 72, 153, 0.18);
  color: #f472b6;
  border: 1px solid rgba(236, 72, 153, 0.3);
}

.pc-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
  line-height: 1.3;
}

/* Route Box */
.pc-route-box {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: rgba(0, 0, 0, 0.35);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 8px;
  padding: 5px 10px;
  margin-bottom: 12px;
}

.route-code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-size: 12px;
  color: #38bdf8;
  word-break: break-all;
}

.btn-copy-route {
  background: transparent;
  border: none;
  font-size: 12px;
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  padding: 2px 4px;
  transition: color 0.15s ease;
}

.btn-copy-route:hover {
  color: #fff;
}

.pc-desc {
  font-size: 13px;
  color: var(--text-muted, #94a3b8);
  line-height: 1.5;
  margin: 0 0 16px;
  flex: 1;
}

/* Subpages Box */
.pc-subpages-box {
  background: rgba(2, 6, 23, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 12px;
  padding: 12px 14px;
  margin-bottom: 16px;
}

.subpages-header {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #cbd5e1;
  margin-bottom: 8px;
}

.subpages-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.subpage-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 12px;
  padding: 4px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.subpage-item:last-child {
  border-bottom: none;
}

.sub-info {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.sub-icon {
  font-size: 12px;
}

.sub-name {
  color: #e2e8f0;
  font-weight: 500;
  white-space: nowrap;
}

.sub-route {
  font-size: 10px;
  color: var(--text-muted, #94a3b8);
  font-family: ui-monospace, monospace;
}

.btn-open-sub {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 10px;
  font-weight: 600;
  padding: 2px 7px;
  border-radius: 5px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-open-sub:hover {
  background: #a855f7;
  border-color: #a855f7;
}

/* Card Footer */
.pc-footer {
  margin-top: auto;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
}

.btn-open-main {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.12);
  color: #fff;
  font-weight: 600;
  padding: 10px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-open-main:hover {
  background: linear-gradient(135deg, #a855f7, #6366f1);
  border-color: #a855f7;
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(168, 85, 247, 0.35);
}

.btn-open-main .arrow {
  transition: transform 0.2s ease;
}

.btn-open-main:hover .arrow {
  transform: translate(2px, -2px);
}

/* Compact Table View */
.compact-table-section {
  padding: 20px;
  background: rgba(15, 23, 42, 0.75);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 20px;
  backdrop-filter: blur(14px);
  position: relative;
  z-index: 1;
}

.table-responsive {
  overflow-x: auto;
}

.all-pages-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

.all-pages-table th {
  padding: 12px 14px;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted, #94a3b8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.all-pages-table td {
  padding: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  vertical-align: middle;
}

.all-pages-table tr:hover td {
  background: rgba(255, 255, 255, 0.02);
}

.tbl-name-cell {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tbl-icon {
  font-size: 20px;
}

.route-code-small {
  font-family: ui-monospace, monospace;
  font-size: 11px;
  color: #38bdf8;
  background: rgba(0, 0, 0, 0.3);
  padding: 2px 6px;
  border-radius: 5px;
}

.tbl-sub-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  max-width: 380px;
}

.sub-chip {
  font-size: 10px;
  font-weight: 500;
  color: #cbd5e1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  padding: 2px 6px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.sub-chip:hover {
  background: #a855f7;
  color: #fff;
  border-color: #a855f7;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .pages-grid {
    grid-template-columns: 1fr;
  }
}
</style>
