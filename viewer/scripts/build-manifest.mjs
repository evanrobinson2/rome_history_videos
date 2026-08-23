#!/usr/bin/env node
/**
 * Compiles production markdown + batch_generate.sh into viewer/public/data/manifest.json
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "../..");
const OUT = path.resolve(__dirname, "../public/data/manifest.json");

const STYLE_SUFFIX =
  "Layered cut-paper illustration, late-antique 376 CE, stacked paper planes soft drop shadows, handmade paper fibre, scissor-cut edges torn deckle for damage, light as flat translucent wedges, palette deep indigo bone iron grey tarnished gold gold only for light heat fire sun, 16:9 horizontal with crop headroom, no text no watermark no invented heraldry no medieval plate no mail hauberks, named principals stylized visible cut-paper faces, crowds faceless silhouettes, same dignity Gothic and Roman, not Batman not black void silhouettes, off-center composition.";

function read(file) {
  return fs.readFileSync(path.join(ROOT, file), "utf8");
}

function parseShotList(md) {
  const shots = [];
  let section = "";
  let sectionTitle = "";
  let sectionNarrative = "";

  for (const line of md.split("\n")) {
    const sec = line.match(/^## ([A-F])\.\s+(.+)$/);
    if (sec) {
      section = sec[1];
      sectionTitle = sec[2].trim();
      continue;
    }
    if (line.startsWith("**") && section && !line.startsWith("|")) {
      sectionNarrative = line.replace(/\*\*/g, "").trim();
    }
    const row = line.match(
      /^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*([^|]+)\|\s*([^|]+)\|/
    );
    if (!row) continue;

    const filename = row[2].trim();
    const moodRaw = row[3].trim();
    const description = row[4].trim().replace(/\*\*/g, "");

    const moodMatch = moodRaw.match(/^(\d+)\s+(.+)$/);
    const register = filename.includes("-R3") ? "R3" : "R1";

    shots.push({
      shotNumber: Number(row[1]),
      id: filename.replace(/\.png$/, ""),
      filename,
      section,
      sectionTitle,
      sectionNarrative,
      mood: moodMatch
        ? { number: Number(moodMatch[1]), name: moodMatch[2].trim() }
        : { number: 0, name: moodRaw },
      register,
      description,
      category: filename.startsWith("VAL-") ? "character" : "scene",
      imagePath:
        filename.startsWith("VAL-")
          ? `/assets/characters/${filename}`
          : `/assets/scenes/${filename}`,
    });
  }
  return shots;
}

function parseReview(md) {
  const review = {};
  let mode = null;

  for (const line of md.split("\n")) {
    if (line.startsWith("## PASS")) mode = "pass";
    else if (line.startsWith("## REJECT")) mode = "reject";
    else if (line.startsWith("## v2 iteration")) mode = null;
    else if (line.includes("Still flag for your eye")) mode = "flags";

    if (mode === "pass" || mode === "reject") {
      const row = line.match(/^\|\s*`?([^`|]+)`?\s*\|\s*([^|]*)\|/);
      if (!row || row[1] === "File" || row[1].includes("---")) continue;
      const file = row[1].trim();
      if (mode === "pass") {
        review[file] = {
          status: "pass",
          notes: row[2].trim() || undefined,
        };
      } else {
        const fixRow = line.match(
          /^\|\s*`?([^`|]+)`?\s*\|\s*([^|]+)\|\s*([^|]+)\|/
        );
        if (fixRow) {
          review[fixRow[1].trim()] = {
            status: "reject",
            rejectReason: fixRow[2].trim(),
            v2Fix: fixRow[3].trim(),
          };
        }
      }
    }

    if (mode === "flags") {
      const flag = line.match(/^-\s*`([^`]+)`\s*—\s*(.+)$/);
      if (flag) {
        review[flag[1]] = {
          ...(review[flag[1]] || { status: "pass" }),
          flagged: true,
          notes: flag[2].trim(),
        };
      }
    }
  }
  return review;
}

function parsePrompts(sh) {
  const prompts = {};
  const lines = sh.split("\n");
  let pendingOut = null;

  for (let i = 0; i < lines.length; i++) {
    const gen = lines[i].match(
      /generate\s+"\$ROOT\/assets\/(characters|scenes)\/([^"]+)"\s*\\?$/
    );
    if (gen) {
      pendingOut = gen[2];
      continue;
    }
    if (pendingOut) {
      const desc = lines[i].match(/^\s*"([^"]+)"/);
      if (desc) {
        prompts[pendingOut] = `${desc[1]}. ${STYLE_SUFFIX}`;
        pendingOut = null;
      }
    }
    const r3 = lines[i].match(
      /--output "\$ROOT\/assets\/scenes\/([^"]+)"\s*\\?$/
    );
    if (r3 && lines[i + 1]?.includes("--prompt")) {
      const pm = lines[i + 1].match(/--prompt "([^"]+)"/);
      if (pm) prompts[r3[1]] = pm[1];
    }
  }
  return prompts;
}

function fileExists(relPath) {
  return fs.existsSync(path.join(ROOT, relPath.replace(/^\//, "assets/").replace(/^assets\//, "assets/")));
}

function main() {
  const shotList = read("assets/production/SHOT-LIST-50.md");
  const reviewMd = read("assets/production/REVIEW-v1.md");
  const batchSh = read("scripts/batch_generate.sh");

  const review = parseReview(reviewMd);
  const prompts = parsePrompts(batchSh);
  const shots = parseShotList(shotList);

  const items = shots.map((shot) => {
    const rev = review[shot.filename] || { status: "unreviewed" };
    const diskPath =
      shot.category === "character"
        ? `assets/characters/${shot.filename}`
        : `assets/scenes/${shot.filename}`;
    const archived = fs.existsSync(
      path.join(ROOT, "assets/rejected/v1", shot.filename)
    )
      ? `/assets/rejected/v1/${shot.filename}`
      : undefined;

    return {
      ...shot,
      prompt: prompts[shot.filename] || `${shot.description}. ${STYLE_SUFFIX}`,
      storyBeat: shot.description,
      storyPart: `${shot.section}. ${shot.sectionTitle}`,
      review: rev,
      archivedPath: archived,
      exists: fs.existsSync(path.join(ROOT, diskPath)),
    };
  });

  const manifest = {
    generatedAt: new Date().toISOString(),
    title: "Gothic Invasion — Frame Review",
    styleSuffix: STYLE_SUFFIX,
    totalShots: items.length,
    items,
  };

  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(manifest, null, 2));
  console.log(`Wrote ${items.length} shots → ${OUT}`);
}

main();
