/**
 * URL Validation & Normalization Utility
 * Validates whether a string is a real web URL (SoundCloud, Spotify, YouTube, web link, etc.)
 * rather than arbitrary plain text.
 */

export function isValidWebUrl(input) {
  if (!input || typeof input !== "string") return false;
  const trimmed = input.trim();
  if (!trimmed || /\s/.test(trimmed)) return false;

  // Prepend https:// if protocol is omitted to test domain structure
  const toTest = /^https?:\/\//i.test(trimmed) ? trimmed : `https://${trimmed}`;

  try {
    const parsed = new URL(toTest);
    if (!["http:", "https:"].includes(parsed.protocol)) return false;

    const hostname = parsed.hostname;
    // Hostname must contain at least one dot (domain.tld), cannot start or end with a dot
    if (!hostname || hostname.startsWith(".") || hostname.endsWith(".")) return false;

    const parts = hostname.split(".");
    if (parts.length < 2) return false;

    // TLD must be alphabetic and at least 2 characters long
    const tld = parts[parts.length - 1];
    if (!tld || tld.length < 2 || !/^[a-zA-Z]+$/.test(tld)) return false;

    // Reject localhost / non-routable dummy names unless explicit
    if (hostname.includes("..")) return false;

    return true;
  } catch {
    return false;
  }
}

export function normalizeWebUrl(input) {
  if (!input || typeof input !== "string") return "";
  const trimmed = input.trim();
  if (!trimmed) return "";
  if (!/^https?:\/\//i.test(trimmed)) {
    return `https://${trimmed}`;
  }
  return trimmed;
}
