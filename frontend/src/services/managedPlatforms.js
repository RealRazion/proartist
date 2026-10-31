import api from "../api";

const CACHE_KEY = "unyq_manage_platform_access_state";
const CACHE_TTL_MS = 30 * 1000;

export const PLATFORMS_CATALOG = [
  {
    slug: "dashboard",
    name: "Dashboard & Studio",
    category: "Studio & Workspace",
    icon: "🏠",
    description: "ProArtist Studio-Dashboard, Schnellübersicht, Projekte und Tasks.",
    route: "/dashboard",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "tournaments",
    name: "Turnier & Battle Arena",
    category: "Wettbewerb & Arena",
    icon: "🏆",
    description: "Arena für Musik-Battles, K.O.-Turniere, Votings und Preisgelder.",
    route: "/tournaments",
    allow_non_team_users: true,
    version: "2.0-live",
  },
  {
    slug: "contests",
    name: "Contests",
    category: "Wettbewerb & Arena",
    icon: "⚔️",
    description: "Wettbewerbe, Preispools und Contest-Bewerbungen.",
    route: "/tournaments",
    allow_non_team_users: true,
    version: "2.0-live",
  },
  {
    slug: "music",
    name: "Music Player",
    category: "Audio & Streaming",
    icon: "🎧",
    description: "UNYQ VIP Music Player, Stream-Releases, VIP Drops und Playlists.",
    route: "/platforms/music",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "songs",
    name: "Song-Bibliothek",
    category: "Studio & Workspace",
    icon: "🎵",
    description: "Song-Katalog, Masterings, Versionen, Lyrics und STEM-Verwaltung.",
    route: "/platforms/songs",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "finance",
    name: "Finance & Budgeting",
    category: "Finanzen & Business",
    icon: "💰",
    description: "Finanzplaner, Monatsabschlüsse, Einnahmen, Schulden und Budgets.",
    route: "/platforms/finance",
    allow_non_team_users: true,
    version: "1.2",
  },
  {
    slug: "earn",
    name: "Earn & Bounties",
    category: "Finanzen & Business",
    icon: "💎",
    description: "Partner- & Affiliate-Programm mit Lifetime-Provisionen.",
    route: "/platforms/earn",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "designs",
    name: "Cover- & Grafik-Studio",
    category: "Kreativ & Merch",
    icon: "🎨",
    description: "Heavyweight Streetwear, Merch Drops und Cover-Artwork.",
    route: "/platforms/designs",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "library",
    name: "ProArtist Library",
    category: "Produktion & Sound",
    icon: "📦",
    description: "Open Source Sound Bank, Drumkits, Sample Packs und Presets.",
    route: "/platforms/library",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "forum",
    name: "Community Forum",
    category: "Community & Collabs",
    icon: "💬",
    description: "Artist-Austausch, Songwriting, Collabs und Producer-Feedback.",
    route: "/platforms/forum",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "todo",
    name: "Todo",
    category: "Aufgaben & Tasks",
    icon: "📝",
    description: "Schnelle Notizen, Todo-Listen und tägliche Aufgaben.",
    route: "/platforms/todo",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "team-tasks",
    name: "Team Tasks",
    category: "Aufgaben & Tasks",
    icon: "🛠️",
    description: "Interne Team-Tasks, operative Sprints und Aufgabenverteilung.",
    route: "/platforms/team-tasks",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "promo-queue",
    name: "Release & Promo Queue",
    category: "Marketing & Release",
    icon: "🚀",
    description: "Planung und Durchführung von Kampagnen und Promo-Wellen.",
    route: "/promo-queue",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "locations",
    name: "Locations",
    category: "Events & Booking",
    icon: "📍",
    description: "Studio-Räume, Aufnahme-Locations, Events und Buchungen.",
    route: "/platforms/locations",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "content-studio",
    name: "Content Studio",
    category: "Content & Media",
    icon: "🎬",
    description: "Academy, News, Tutorials, Tipps und Social Content Material.",
    route: "/platforms/content-studio",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "content-schedule",
    name: "Content Schedule",
    category: "Content & Media",
    icon: "📅",
    description: "Veröffentlichungs- und Social-Media-Kalender für Artists.",
    route: "/platforms/content-schedule",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "fitness",
    name: "Fitness",
    category: "Lifestyle & Health",
    icon: "⚡",
    description: "Workouts, Vitalitäts-Tracker und Gesundheit für Artists.",
    route: "/platforms/fitness",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "plugin-guides",
    name: "Plugin Guides",
    category: "Tutorials & Know-How",
    icon: "🎛️",
    description: "VST-Anleitungen, Mixing-Tipps und Studio-Software-Guides.",
    route: "/platforms/plugin-guides",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "api-center",
    name: "API Center",
    category: "Entwickler & Tech",
    icon: "🔌",
    description: "API-Dokumentation, Webhooks und Token-Verwaltung.",
    route: "/platforms/api-center",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "admin",
    name: "Admin Control Hub",
    category: "Administration",
    icon: "👑",
    description: "Zentraler Administrations-Hub für Systeme und Dienste.",
    route: "/platforms/admin",
    allow_non_team_users: false,
    version: "2.0",
  },
  {
    slug: "manage-platforms",
    name: "Platform Control",
    category: "Administration",
    icon: "🛡️",
    description: "Plattform-Manager: Status, Versionen, Wartung und Rechte.",
    route: "/platforms/manage-platforms",
    allow_non_team_users: false,
    version: "2.0",
  },
  {
    slug: "admin-stats-manager",
    name: "Admin Stats Manager",
    category: "Administration",
    icon: "📊",
    description: "Spieler-Stats, Ranked RP, Battle-Bilanzen und Entwicklungs-Resets.",
    route: "/platforms/admin/stats-manager",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "admin-user-role-management",
    name: "Nutzer- & Rollenverwaltung",
    category: "Administration",
    icon: "👥",
    description: "Rollen, Berechtigungen und Zugriffs-Matrix für alle Nutzer.",
    route: "/platforms/admin/user-role-management",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "admin-tournament-animations",
    name: "Turnier Animation Lab",
    category: "Administration",
    icon: "🎭",
    description: "Labor für Arena-Animationen, Motion-Tests und Effekte.",
    route: "/platforms/admin/tournament-animations",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "hub",
    name: "Creator Hub",
    category: "Übersicht",
    icon: "🌐",
    description: "Haupt-Plattform Hub für alle UNYQ Plattformen und Apps.",
    route: "/platforms",
    allow_non_team_users: true,
    version: "2.0",
  },
  {
    slug: "extra",
    name: "Extra Tools & Module",
    category: "Tools",
    icon: "🧰",
    description: "Verzeichnis aller zusätzlichen externen und internen Werkzeuge.",
    route: "/platforms/extra",
    allow_non_team_users: true,
    version: "1.0",
  },
  {
    slug: "hhu",
    name: "HHU Uni-Tool",
    category: "Sonder-Tools",
    icon: "🎓",
    description: "HHU Universitäts- und Modul-Tool.",
    route: "/platforms/hhu",
    allow_non_team_users: false,
    version: "1.0",
  },
  {
    slug: "testing",
    name: "Testing Lab",
    category: "Diagnose",
    icon: "🧪",
    description: "Testumgebung für neue Features und API-Endpunkte.",
    route: "/testing",
    allow_non_team_users: false,
    version: "0.9",
  },
];

const ROUTE_TO_PLATFORM_SLUG = {
  dashboard: "dashboard",
  analytics: "dashboard",
  profiles: "dashboard",
  projects: "dashboard",
  "project-detail": "dashboard",
  tasks: "dashboard",
  reviews: "dashboard",
  timeline: "dashboard",
  notifications: "dashboard",
  admin: "admin",
  points: "dashboard",
  growpro: "dashboard",
  songs: "songs",
  "platform-songs": "songs",
  me: "dashboard",
  search: "dashboard",
  chats: "dashboard",
  activity: "dashboard",
  testing: "testing",
  tournaments: "contests",
  "tournament-detail": "contests",
  "platform-contests": "contests",
  "platform-contest-detail": "contests",
  "platform-music": "music",
  "platform-locations": "locations",
  "platform-finance": "finance",
  finance: "finance",
  "platform-earn": "earn",
  "platform-designs": "designs",
  "platform-library": "library",
  "platform-forum": "forum",
  "platform-extra": "extra",
  "platform-content-studio": "content-studio",
  "platform-content-schedule": "content-schedule",
  "content-schedule": "content-schedule",
  "platform-fitness": "fitness",
  fitness: "fitness",
  "platform-todo": "todo",
  "platform-plugin-guides": "plugin-guides",
  "platform-api-center": "api-center",
  "admin-platform": "admin",
  "admin-user-role-management": "admin-user-role-management",
  "admin-stats-manager": "admin-stats-manager",
  "admin-tournament-animations": "admin-tournament-animations",
  "manage-platforms": "manage-platforms",
  "platform-team-tasks": "team-tasks",
  "promo-queue": "promo-queue",
  "platform-hhu": "hhu",
  platforms: "hub",
};

function toList(payload) {
  if (Array.isArray(payload)) return payload;
  return payload?.results || [];
}

function readCache() {
  try {
    const raw = sessionStorage.getItem(CACHE_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw);
    if (!parsed || !parsed.ts || !Array.isArray(parsed.rows)) return null;
    if (Date.now() - parsed.ts > CACHE_TTL_MS) return null;
    return parsed.rows;
  } catch {
    return null;
  }
}

function writeCache(rows) {
  try {
    sessionStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), rows }));
  } catch {
    // ignore storage quota or availability issues
  }
}

export function routeNameToPlatformSlug(routeName) {
  return ROUTE_TO_PLATFORM_SLUG[routeName] || null;
}

export async function fetchManagedPlatformAccessState({ force = false } = {}) {
  if (!force) {
    const cached = readCache();
    if (cached) return cached;
  }
  const { data } = await api.get("manage-platforms/access-state/");
  const rows = toList(data);
  writeCache(rows);
  return rows;
}

export function mapAccessStateRows(rows) {
  return (rows || []).reduce((acc, row) => {
    if (row?.slug) acc[row.slug] = row;
    return acc;
  }, {});
}

export function invalidateManagedPlatformAccessCache() {
  try {
    sessionStorage.removeItem(CACHE_KEY);
  } catch {
    // ignore
  }
}
