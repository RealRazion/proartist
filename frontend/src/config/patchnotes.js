import patchnotesData from "./patchnotes.json";
import { APP_VERSION } from "./version";

export const PATCH_NOTES = patchnotesData;
export const LATEST_PATCH = patchnotesData[0] || null;

/**
 * Parses a version string like "2.11.0.2-beta" into:
 * - majorMinor: "2.11" (shown in bold)
 * - patchRest: ".0.2-beta" (shown in thinner/smaller font)
 * - prefix: "v" (optional)
 */
export function parseVersionParts(versionStr = APP_VERSION) {
  const clean = (versionStr || "").trim();
  const match = clean.match(/^([vV]?)(\d+\.\d+)(.*)$/);
  if (match) {
    return {
      prefix: match[1] || "",
      majorMinor: match[2],
      patchRest: match[3] || ""
    };
  }

  const parts = clean.split(".");
  if (parts.length >= 2) {
    return {
      prefix: "",
      majorMinor: `${parts[0]}.${parts[1]}`,
      patchRest: parts.slice(2).length ? `.${parts.slice(2).join(".")}` : ""
    };
  }

  return {
    prefix: "",
    majorMinor: clean,
    patchRest: ""
  };
}
