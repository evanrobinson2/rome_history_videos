#!/usr/bin/env python3
"""Apply manifests/legacy-map.json approved/tentative assets into episode.yaml."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
MAP = EPISODE / "manifests" / "legacy-map.json"
YAML = EPISODE / "episode.yaml"


def main() -> None:
    mapping = {m["shot_id"]: m for m in json.loads(MAP.read_text())["mappings"]}
    text = YAML.read_text(encoding="utf-8")
    for shot_id, entry in mapping.items():
        block = re.search(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  approved_asset: ).*",
            text,
        )
        if not block:
            continue
        replacement = f"{block.group(1)}{entry['path']}"
        text = text[: block.start()] + replacement + text[block.end() :]
        status = "approved" if entry["status"] == "approved" else "legacy_tentative"
        text = re.sub(
            rf"(- id: {re.escape(shot_id)}\n(?:  .+\n)*?  image_status: ).*",
            rf"\g<1>{status}",
            text,
            count=1,
        )
    YAML.write_text(text, encoding="utf-8")
    print(f"Updated {YAML} from {MAP}")


if __name__ == "__main__":
    main()
