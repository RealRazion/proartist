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
let currentVersion = "2.11.0.6-beta";
if (fs.existsSync(versionJsPath)) {
  const versionJsContent = fs.readFileSync(versionJsPath, "utf-8");
  const match = versionJsContent.match(/export\s+const\s+APP_VERSION\s*=\s*["']([^"']+)["']/);
  if (match) currentVersion = match[1];
}

// Read patchnotes
let patchnotes = [];
if (fs.existsSync(patchnotesJsonPath)) {
  try {
    const raw = JSON.parse(fs.readFileSync(patchnotesJsonPath, "utf-8"));
    patchnotes = Array.isArray(raw) ? raw : (raw.value || []);
  } catch {}
}

// Fetch unpushed commits
let commits = [];
try {
  let rawLog = "";
  try {
    rawLog = execSync("git log origin/master..HEAD --oneline", { encoding: "utf-8" });
  } catch {
    rawLog = "";
  }
  commits = rawLog
    .split(/\r?\n/)
    .map(l => l.trim())
    .filter(l => l && !l.includes("chore(patch):") && !l.includes("Merge branch"))
    .map(l => l.replace(/^[a-f0-9]+\s+/, ""));
} catch {}

const shouldCommit = process.argv.includes("--commit");
const isForce = process.argv.includes("--force");

if (!isForce && commits.length === 0) {
  console.log("[UNYQ Patchnotes] Keine neuen unpushten Commits gefunden.");
  process.exit(0);
}

// Calculate next version: e.g. 2.11.0.6-beta -> 2.11.0.7-beta
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
  if (convMatch && highlights.length < 4) {
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

const updatedList = [newPatch, ...patchnotes.filter(p => p.version !== newVersion)];

fs.writeFileSync(patchnotesJsonPath, JSON.stringify(updatedList, null, 2) + "\n", "utf-8");
fs.writeFileSync(versionJsPath, `// UI version label. package.json keeps the SemVer-compatible variant.\nexport const APP_VERSION = "${newVersion}";\n`, "utf-8");

if (fs.existsSync(packageJsonPath)) {
  const pkg = JSON.parse(fs.readFileSync(packageJsonPath, "utf-8"));
  pkg.version = newVersion;
  fs.writeFileSync(packageJsonPath, JSON.stringify(pkg, null, 2) + "\n", "utf-8");
}

const packageLockJsonPath = path.join(repoRoot, "frontend", "package-lock.json");
if (fs.existsSync(packageLockJsonPath)) {
  const lock = JSON.parse(fs.readFileSync(packageLockJsonPath, "utf-8"));
  lock.version = newVersion;
  if (lock.packages && lock.packages[""]) {
    lock.packages[""].version = newVersion;
  }
  fs.writeFileSync(packageLockJsonPath, JSON.stringify(lock, null, 2) + "\n", "utf-8");
}

console.log(`✅ [UNYQ Patchnotes] Neuer Patch ${newVersion} erfolgreich generiert!`);

if (shouldCommit) {
  execSync(`git add "${patchnotesJsonPath}" "${versionJsPath}" "${packageJsonPath}" "${packageLockJsonPath}"`);
  execSync(`git commit -m "chore(patch): bump version to ${newVersion} & generate patch notes [auto]"`);
  process.exit(2);
}

process.exit(0);
