#!/usr/bin/env node
/**
 * Build prep: always rebuild local manifest.
 * Only link/copy heavy assets when NOT using remote Blob catalog.
 */
import { spawnSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");

function run(script) {
  const r = spawnSync(process.execPath, [path.join(__dirname, script)], {
    stdio: "inherit",
  });
  if (r.status) process.exit(r.status ?? 1);
}

function runPython(script) {
  const r = spawnSync("python3", [path.join(ROOT, "scripts", script)], {
    stdio: "inherit",
  });
  if (r.status) process.exit(r.status ?? 1);
}

if (process.env.NEXT_PUBLIC_CATALOG_URL) {
  console.log("NEXT_PUBLIC_CATALOG_URL set — skipping local manifest build and asset copy (using Blob).");
} else {
  // Use new Python manifest builder (handles new OpenAI asset structure)
  // Falls back to old mjs if Python unavailable
  const newChaptersExist = fs.existsSync(path.join(ROOT, "assets/chapters/ch01"));
  if (newChaptersExist) {
    console.log("Using build-local-manifest.py for new asset structure...");
    runPython("build-local-manifest.py");
  } else {
    run("build-manifest.mjs");
  }
  run("link-assets.mjs");
}
