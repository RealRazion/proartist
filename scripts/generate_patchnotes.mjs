import fs from "fs";
import path from "path";
import { execSync } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const repoRoot = path.resolve(__dirname, "..");

const patchnotesJsonPath = path.join(repoRoot, "frontend", "src", "config", "patchnotes.json");
const versionJsPath = path.join(repoRoot, "frontend", "src", "config", "version.js");
const packageJsonPath = path.join(repoRoot, "frontend", "package.json");

// Read current version
let currentVersion = "2.11.0.2-beta";
if (fs.existsSync(versionJsPath)) {
  const versionJsContent = fs.readFileSync(versionJsPath, "utf-8");
  const match = versionJsContent.match(/export\s+const\s+APP_VERSION\s*=\s*["']([^"']+)["']/);
  if (match) currentVersion = match[1];
}

// Read patchnotes
let patchnotes = [];
if (fs.existsSync(patchnotesJsonPath)) {
  try {
    patchnotes = JSON.parse(fs.readFileSync(patchnotesJsonPath, "utf-8"));
  } catch {}
}

// Fetch commits
let commits = [];
try {
  let rawLog = "";
  try {
    rawLog = execSync("git log origin/master..HEAD --oneline", { encoding: "utf-8" });
  } catch {
    rawLog = execSync("git log -n 3 --oneline", { encoding: "utf-8" });
  }
  commits = rawLog
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l && !l.includes("chore(patch):") && !l.includes("Merge branch"))
    .map(l => l.replace(/^[a-f0-9]+\s+/, ""));
} catch {}

const shouldCommit = process.argv.includes("--commit");
const isForce = process.argv.includes("--force");

const latestRecorded = patchnotes[0]?.version;
if (!isForce && latestRecorded === currentVersion && commits.length === 0) {
  console.log("[UNYQ Patchnotes] Keine neuen Commits gefunden.");
  process.exit(0);
}

// Calculate next version: 2.11.0.2-beta -> 2.11.0.3-beta
let newVersion = currentVersion;
const verMatch = currentVersion.match(/^(.*?)(\d+)(-.*)?$/);
if (verMatch) {
  const prefix = verMatch[1];
  const patchNum = parseInt(verMatch[2], 10) + 1;
  const suffix = verMatch[3] || "";
  newVersion = `${prefix}${patchNum}${suffix}`;
} else {
  newVersion = `${currentVersion}.1`;
}

const today = new Date().toISOString().split("T")[0];
const highlights = [];
const changes = [];

for (const c of commits) {
  changes.push(c);
  const convMatch = c.match(/^(feat|fix|style|refactor|perf)(\([^)]+\))?:\s*(.+)$/i);
  if (convMatch && highlights.length < 3) {
    const title = convMatch[3].charAt(0).toUpperCase() + convMatch[3].slice(1);
    highlights.push(title);
  }
}

if (highlights.length === 0) {
  highlights.push("Allgemeine Verbesserungen und Performance-Updates");
  highlights.push("UI- und Workflow-Optimierungen");
}
if (changes.length === 0) {
  changes.push(`Automatischer Patch Release ${newVersion}`);
}

const newPatch = {
  version: newVersion,
  date: today,
  title: `Patch ${newVersion}`,
  tagline: "Automatisches Update",
  highlights,
  changes,
};

patchnotes.unshift(newPatch);

fs.writeFileSync(patchnotesJsonPath, JSON.stringify(patchnotes, null, 2) + "\n", "utf-8");
fs.writeFileSync(versionJsPath, `// UI version label. package.json keeps the SemVer-compatible variant.\nexport const APP_VERSION = "${newVersion}";\n`, "utf-8");

if (fs.existsSync(packageJsonPath)) {
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8"));
  pkg.version = newVersion;
  fs.writeFileSync(packageJsonPath, JSON.stringify(pkg, null, 2) + "\n", "utf-8");
}

console.log(`✅ [UNYQ Patchnotes] Neuer Patch ${newVersion} erfolgreich generiert!`);

if (shouldCommit) {
  execSync(`git add "${patchnotesJsonPath}" "${versionJsPath}" "${packageJsonPath}"`);
  execSync(`git commit -m "chore(patch): bump version to ${newVersion} & generate patch notes [auto]"`);
  process.exit(2);
}

process.exit(0);
