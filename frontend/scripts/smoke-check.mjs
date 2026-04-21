import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const requiredFiles = [
  "src/router/index.js",
  "src/views/Dashboard.vue",
  "src/views/FinanceTool.vue",
  "src/views/ContentStudio.vue",
  "src/api.js",
];

const requiredRouteNames = [
  "dashboard",
  "tasks",
  "reviews",
  "finance",
  "platform-content-studio",
];

let failed = false;
for (const rel of requiredFiles) {
  const abs = path.join(root, rel);
  if (!fs.existsSync(abs)) {
    console.error(`[SMOKE] Missing file: ${rel}`);
    failed = true;
  }
}

const routerPath = path.join(root, "src/router/index.js");
if (fs.existsSync(routerPath)) {
  const text = fs.readFileSync(routerPath, "utf8");
  for (const name of requiredRouteNames) {
    if (!text.includes(`name: \"${name}\"`) && !text.includes(`name: '${name}'`)) {
      console.error(`[SMOKE] Missing route name: ${name}`);
      failed = true;
    }
  }
}

if (failed) {
  process.exit(1);
}

console.log("[SMOKE] Basic route/file checks passed.");
