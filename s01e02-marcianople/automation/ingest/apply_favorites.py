#!/usr/bin/env python3
"""Apply shot-favorites.json picks to episode.yaml (sets approved + approved status)."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
FAVORITES = ROOT / "s01e02-marcianople" / "manifests" / "shot-favorites.json"
YAML = ROOT / "s01e02-marcianople" / "episode.yaml"


def main() -> None:
    data = json.loads(FAVORITES.read_text(encoding="utf-8"))
    picks = data.get("picks", {})
    if not picks:
        print("No favorites to apply.")
        return

    text = YAML.read_text(encoding="utf-8")
    applied = 0
    for shot_id, pick in picks.items():
        asset = pick.get("path")
        if not asset or not (ROOT / asset).exists():
            print(f"Skip {shot_id}: missing {asset}")
            continue
        block = re.search(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  approved_asset: ).*",
            text,
        )
        if not block:
            print(f"Skip {shot_id}: not in episode.yaml")
            continue
        text = text[: block.start()] + block.group(1) + asset + text[block.end() :]
        text = re.sub(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  image_status: ).*",
            r"\g<1>approved",
            text,
            count=1,
        )
        applied += 1

    YAML.write_text(text, encoding="utf-8")
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    FAVORITES.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Applied {applied} favorites to {YAML}")


if __name__ == "__main__":
    main()
