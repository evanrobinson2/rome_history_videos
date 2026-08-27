#!/usr/bin/env python3
"""Inventory repo assets for S01E02 and update manifests/assets.json."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
MANIFEST = EPISODE / "manifests" / "assets.json"
GENERATIONS = EPISODE / "manifests" / "generations.jsonl"

SCAN_DIRS = [
    ROOT / "assets" / "scenes",
    ROOT / "assets" / "characters",
    ROOT / "feedback" / "inbox",
    EPISODE / "assets" / "source-images",
    EPISODE / "assets" / "selected-images",
    EPISODE / "assets" / "music",
]

MEDIA_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".mp3", ".wav", ".m4a", ".flac"}


def sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def load_existing() -> dict:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text(encoding="utf-8"))
    return {"schemaVersion": "1.0.0", "assets": []}


def merge_assets(existing: dict) -> dict:
    by_path = {a["path"]: a for a in existing.get("assets", [])}
    scanned: list[dict] = []

    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in MEDIA_EXTS:
                continue
            rel = path.relative_to(ROOT).as_posix()
            prior = by_path.get(rel, {})
            scanned.append(
                {
                    "path": rel,
                    "bytes": path.stat().st_size,
                    "sha256": sha256_prefix(path),
                    "shot_id": prior.get("shot_id"),
                    "status": prior.get("status", "inventory"),
                    "notes": prior.get("notes"),
                }
            )

    return {
        "schemaVersion": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "assets": scanned,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    existing = load_existing()
    merged = merge_assets(existing)
    print(f"Found {len(merged['assets'])} media assets")

    if args.dry_run:
        print(json.dumps(merged, indent=2)[:4000])
        return

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    if not GENERATIONS.exists():
        GENERATIONS.write_text("", encoding="utf-8")
    print(f"Wrote {MANIFEST}")


if __name__ == "__main__":
    main()
