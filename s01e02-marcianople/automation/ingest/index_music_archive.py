#!/usr/bin/env python3
"""Index music files for S01E02 and map to episode cues."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INBOX_DIRS = [
    ROOT / "feedback" / "inbox" / "2026-08-26-archive-music",
    ROOT / "feedback" / "inbox",
]
OUT = ROOT / "s01e02-marcianople" / "manifests" / "music-manifest.json"
ASSET_DIR = ROOT / "s01e02-marcianople" / "assets" / "music"

MEDIA = {".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg"}

# cue_id -> substring patterns (normalized filename)
CUE_RULES: list[tuple[str, list[str], str]] = [
    ("battle", ["the_gothic_fracture", "gothic_fracture"], "The Gothic Fracture — primary battle cue"),
    ("denouement", ["frozen_plain_thrace", "frozen-plain-thrace"], "Frozen Plain Thrace — denouement"),
    ("crossing_reference", ["dust_on_the_steppe", "dust-on-the-steppe"], "Dust on the Steppe — crossing reference"),
    ("crossing_open", ["the_first_step_across", "warm_steps"], "Crossing opening"),
    ("family_memory", ["exile_lullaby", "exile-lullaby"], "Exile Lullaby — family / memory"),
    ("heist_groove", ["wah_step_pulse", "wah-step_pulse", "the_iron_vault", "a_wild_evening"], "Banquet / heist groove"),
]

# Prefer specific filenames when multiple variants match a cue (basename substring).
PREFERRED_FILES: dict[str, str] = {
    "battle": "The Gothic Fracture (1)",
    "denouement": "Frozen Plain Thrace (1)",
    "family_memory": "Exile Lullaby (1)",
    "heist_groove": "Wah-Step Pulse (Remastered) (1)",
    "crossing_open": "The First Step Across the (1)",
    "crossing_reference": "Dust on the Steppe (1)",
}


def sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def suggest_cue(stem_norm: str) -> tuple[str | None, str | None]:
    for cue_id, keys, note in CUE_RULES:
        for key in keys:
            if key in stem_norm:
                return cue_id, note
    return None, None


def collect_files() -> list[Path]:
    seen: set[str] = set()
    files: list[Path] = []
    for base in INBOX_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in MEDIA:
                continue
            rel = path.relative_to(ROOT).as_posix()
            if rel in seen:
                continue
            seen.add(rel)
            files.append(path)
    return files


def main() -> None:
    files = collect_files()
    entries = []
    cue_picks: dict[str, dict] = {}

    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        stem_norm = norm(path.stem)
        cue_id, cue_note = suggest_cue(stem_norm)
        entry = {
            "path": rel,
            "filename": path.name,
            "bytes": path.stat().st_size,
            "sha256": sha256_prefix(path),
            "suggested_cue": cue_id,
            "cue_note": cue_note,
        }
        entries.append(entry)
        if cue_id:
            preferred = PREFERRED_FILES.get(cue_id)
            if preferred and preferred in path.name:
                pick = dict(entry)
                pick["pick_reason"] = "preferred_filename"
                cue_picks[cue_id] = pick
                continue
            prev = cue_picks.get(cue_id)
            if prev and prev.get("pick_reason") == "preferred_filename":
                continue
            if not prev or entry["bytes"] > prev["bytes"]:
                cue_picks[cue_id] = entry

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    for cue_id, entry in cue_picks.items():
        dest = ASSET_DIR / f"{cue_id}{Path(entry['path']).suffix.lower()}"
        src = ROOT / entry["path"]
        if src.exists():
            if not dest.exists() or sha256_prefix(src) != sha256_prefix(dest):
                shutil.copy2(src, dest)
            entry["asset_copy"] = dest.relative_to(ROOT).as_posix()

    payload = {
        "schemaVersion": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_dirs": [d.relative_to(ROOT).as_posix() for d in INBOX_DIRS],
        "summary": {
            "files": len(entries),
            "mapped_cues": len(cue_picks),
            "unmapped": len([e for e in entries if not e["suggested_cue"]]),
        },
        "episode_cues": {
            "battle": {"music_cue": "gothic_fracture", "required": True},
            "denouement": {"music_cue": "frozen_thrace", "required": True},
            "crossing_open": {"music_cue": "crossing_open", "required": False},
            "heist_groove": {"music_cue": "heist_groove", "required": True},
            "family_memory": {"music_cue": "exile_lullaby", "required": False},
        },
        "cue_picks": cue_picks,
        "files": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    if cue_picks:
        print("Mapped cues:", {k: v["filename"] for k, v in cue_picks.items()})
    else:
        print("No music files found — drop unzipped Archive into feedback/inbox/2026-08-26-music-archive/")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
