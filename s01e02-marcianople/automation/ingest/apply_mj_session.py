#!/usr/bin/env python3
"""Apply mj-session-index.json shot picks to episode.yaml."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
INDEX = ROOT / "s01e02-marcianople" / "manifests" / "mj-session-index.json"
YAML = ROOT / "s01e02-marcianople" / "episode.yaml"


def main() -> None:
    data = json.loads(INDEX.read_text(encoding="utf-8"))
    text = YAML.read_text(encoding="utf-8")
    applied = 0
    for shot_id, pick in data.get("shot_picks", {}).items():
        asset = pick["default_variant"]["path"]
        block = re.search(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  approved_asset: ).*",
            text,
        )
        if not block:
            continue
        text = text[: block.start()] + block.group(1) + asset + text[block.end() :]
        text = re.sub(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  image_status: ).*",
            r"\g<1>review_needed",
            text,
            count=1,
        )
        applied += 1
    YAML.write_text(text, encoding="utf-8")
    print(f"Applied {applied} MJ picks to {YAML}")


if __name__ == "__main__":
    main()
