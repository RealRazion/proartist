import api from "../api";

const CACHE_KEY = "unyq_manage_platform_access_state";
const CACHE_TTL_MS = 30 * 1000;

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
  songs: "music",
  me: "dashboard",
  search: "dashboard",
  testing: "testing",
  chats: "dashboard",
  news: "proartist-news",
  "platform-contests": "contests",
  "platform-music": "music",
  "platform-locations": "locations",
  "platform-finance": "finance",
  finance: "finance",
  "platform-content-studio": "content-studio",
  "platform-content-schedule": "content-schedule",
  "content-schedule": "content-schedule",
  "platform-fitness": "fitness",
  fitness: "fitness",
  "platform-todo": "todo",
  "platform-plugin-guides": "plugin-guides",
  "platform-api-center": "api-center",
  "platform-news": "proartist-news",
  "admin-platform": "admin",
  "manage-platforms": "manage-platforms",
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
