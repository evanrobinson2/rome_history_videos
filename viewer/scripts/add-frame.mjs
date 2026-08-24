#!/usr/bin/env node
/**
 * Add or update one frame in Vercel Blob + catalog (no app redeploy).
 *
 * Requires: BLOB_READ_WRITE_TOKEN, and catalog already seeded
 *   (or NEXT_PUBLIC_CATALOG_URL / --catalog-url)
 *
 * Usage:
 *   npm run blob:add -- ./out.png \
 *     --id STZ01-05-RIDGELINE \
 *     --part "1. The North" \
 *     --beat "Horse-shadows on the ridge" \
 *     --mood "1 Dread" \
 *     --prompt "..." \
 *     --tag stanza1 --tag dread
 */
import { put } from "@vercel/blob";
import fs from "node:fs";
import path from "node:path";

function arg(name, fallback) {
  const i = process.argv.indexOf(name);
  if (i === -1) return fallback;
  return process.argv[i + 1] ?? fallback;
}

function flags(name) {
  const out = [];
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i] === name && process.argv[i + 1]) out.push(process.argv[i + 1]);
  }
  return out;
}

if (!process.env.BLOB_READ_WRITE_TOKEN) {
  console.error("Missing BLOB_READ_WRITE_TOKEN");
  process.exit(1);
}

const file = process.argv[2];
if (!file || file.startsWith("-")) {
  console.error("Usage: npm run blob:add -- <image.png> --id ID --part PART --beat BEAT [--mood MOOD] [--prompt TEXT] [--tag T]");
  process.exit(1);
}

const abs = path.resolve(file);
if (!fs.existsSync(abs)) {
  console.error(`File not found: ${abs}`);
  process.exit(1);
}

const id =
  arg("--id") ||
  path.basename(abs, path.extname(abs)).replace(/\s+/g, "-");
const storyPart = arg("--part", "Unsorted");
const storyBeat = arg("--beat", id);
const moodRaw = arg("--mood");
const prompt = arg("--prompt", "");
const stanza = arg("--stanza");
const category = arg("--category", "scene");
const register = arg("--register", "R1");
const tags = flags("--tag");
const catalogUrl =
  arg("--catalog-url") ||
  process.env.NEXT_PUBLIC_CATALOG_URL ||
  process.env.CATALOG_URL;

if (!catalogUrl) {
  console.error("Need NEXT_PUBLIC_CATALOG_URL (or --catalog-url) pointing at catalog/frames.json in Blob.");
  process.exit(1);
}

function parseMood(raw) {
  if (!raw) return undefined;
  const m = raw.match(/^(\d+)\s+(.+)$/);
  if (m) return { number: Number(m[1]), name: m[2] };
  return { number: 0, name: raw };
}

async function main() {
  const pathname = `frames/${id}.png`;
  console.log(`Uploading ${pathname}…`);
  const blob = await put(pathname, fs.readFileSync(abs), {
    access: "public",
    contentType: "image/png",
    addRandomSuffix: false,
    allowOverwrite: true,
  });

  console.log(`Fetching catalog…`);
  const res = await fetch(catalogUrl, { cache: "no-store" });
  if (!res.ok) throw new Error(`Catalog fetch failed: ${res.status}`);
  const catalog = await res.json();

  const entry = {
    id,
    url: blob.url,
    filename: path.basename(abs),
    shotNumber:
      catalog.items.find((x) => x.id === id)?.shotNumber ??
      catalog.items.length + 1,
    storyPart,
    storyBeat,
    mood: parseMood(moodRaw),
    register,
    category,
    description: storyBeat,
    prompt,
    stanza,
    tags: tags.length ? tags : undefined,
    review: { status: "unreviewed" },
  };

  const idx = catalog.items.findIndex((x) => x.id === id);
  if (idx >= 0) catalog.items[idx] = { ...catalog.items[idx], ...entry };
  else catalog.items.push(entry);

  catalog.generatedAt = new Date().toISOString();
  catalog.totalShots = catalog.items.length;
  catalog.source = "vercel-blob";

  const catalogBlob = await put(
    "catalog/frames.json",
    JSON.stringify(catalog, null, 2),
    {
      access: "public",
      contentType: "application/json",
      addRandomSuffix: false,
      allowOverwrite: true,
    }
  );

  console.log(`Done. ${idx >= 0 ? "Updated" : "Added"} ${id}`);
  console.log(`Image:   ${blob.url}`);
  console.log(`Catalog: ${catalogBlob.url}`);
  console.log(`Refresh the viewer — no redeploy needed.`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
