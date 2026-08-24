#!/usr/bin/env node
/**
 * Seed Vercel Blob with current frames + catalog.json
 *
 * Requires: BLOB_READ_WRITE_TOKEN
 * Usage:   npm run blob:seed
 *
 * Prints NEXT_PUBLIC_CATALOG_URL to set in Vercel env (one-time).
 */
import { put, list } from "@vercel/blob";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const MANIFEST = path.resolve(__dirname, "../public/data/manifest.json");
const CATALOG_PATHNAME = "catalog/frames.json";

if (!process.env.BLOB_READ_WRITE_TOKEN) {
  console.error("Missing BLOB_READ_WRITE_TOKEN. Create a Blob store in Vercel and paste the token.");
  process.exit(1);
}

async function uploadFile(pathname, filePath, contentType) {
  const buf = fs.readFileSync(filePath);
  const blob = await put(pathname, buf, {
    access: "public",
    contentType,
    addRandomSuffix: false,
    allowOverwrite: true,
  });
  return blob.url;
}

async function main() {
  if (!fs.existsSync(MANIFEST)) {
    console.error("Run npm run manifest first.");
    process.exit(1);
  }
  const manifest = JSON.parse(fs.readFileSync(MANIFEST, "utf8"));
  const items = [];

  console.log(`Seeding ${manifest.items.length} frames…`);

  for (const item of manifest.items) {
    const rel =
      item.category === "character"
        ? path.join("assets/characters", item.filename)
        : path.join("assets/scenes", item.filename);
    const abs = path.join(ROOT, rel);
    if (!fs.existsSync(abs)) {
      console.warn(`skip missing ${rel}`);
      continue;
    }
    const pathname = `frames/${item.id}.png`;
    process.stdout.write(`  ${pathname}… `);
    const url = await uploadFile(pathname, abs, "image/png");
    console.log("ok");

    let archivedUrl;
    if (item.archivedPath) {
      const archAbs = path.join(ROOT, item.archivedPath.replace(/^\//, ""));
      // archivedPath is like /assets/rejected/v1/...
      const archRel = item.archivedPath.replace(/^\//, "");
      const archFile = path.join(ROOT, archRel.startsWith("assets/") ? archRel : path.join("assets", archRel.replace(/^assets\//, "")));
      // try rejected path
      const rejected = path.join(ROOT, "assets/rejected/v1", item.filename);
      if (fs.existsSync(rejected)) {
        archivedUrl = await uploadFile(
          `frames/archive/${item.id}.png`,
          rejected,
          "image/png"
        );
      }
    }

    items.push({
      id: item.id,
      url,
      filename: item.filename,
      shotNumber: item.shotNumber,
      storyPart: item.storyPart,
      storyBeat: item.storyBeat,
      mood: item.mood,
      register: item.register,
      category: item.category,
      description: item.description,
      prompt: item.prompt,
      review: item.review,
      archivedUrl,
      tags: [item.section, item.mood?.name].filter(Boolean),
      section: item.section,
      sectionTitle: item.sectionTitle,
    });
  }

  const catalog = {
    generatedAt: new Date().toISOString(),
    title: manifest.title,
    styleSuffix: manifest.styleSuffix,
    totalShots: items.length,
    items,
    source: "vercel-blob",
  };

  const catalogBlob = await put(CATALOG_PATHNAME, JSON.stringify(catalog, null, 2), {
    access: "public",
    contentType: "application/json",
    addRandomSuffix: false,
    allowOverwrite: true,
  });

  console.log("\nSeed complete.");
  console.log(`Frames: ${items.length}`);
  console.log(`\nSet this Vercel env var (Project → Settings → Environment Variables):`);
  console.log(`  NEXT_PUBLIC_CATALOG_URL=${catalogBlob.url}`);
  console.log(`\nThen redeploy once. After that, add frames with:`);
  console.log(`  npm run blob:add -- ./path.png --id STZ01-01 --part "1. North" --beat "Ridgeline shadows"`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
