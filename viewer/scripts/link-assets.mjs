#!/usr/bin/env node
/**
 * Symlinks repo assets into viewer/public/assets for local dev + Vercel build.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PUBLIC_ASSETS = path.resolve(__dirname, "../public/assets");
const REPO_ASSETS = path.resolve(__dirname, "../../assets");

function linkOrCopy(src, dest) {
  if (fs.existsSync(dest)) {
    const stat = fs.lstatSync(dest);
    if (stat.isSymbolicLink() || stat.isDirectory()) return;
    fs.unlinkSync(dest);
  }
  try {
    fs.symlinkSync(src, dest, "dir");
    console.log(`Linked ${dest} → ${src}`);
  } catch {
    fs.cpSync(src, dest, { recursive: true });
    console.log(`Copied ${src} → ${dest}`);
  }
}

linkOrCopy(REPO_ASSETS, PUBLIC_ASSETS);
