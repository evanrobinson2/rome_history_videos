#!/usr/bin/env python3
"""Sync manifests/shots.json from episode.yaml."""

from __future__ import annotations

import json
import re
from pathlib import Path

import yaml

EPISODE = Path(__file__).resolve().parents[2]
YAML = EPISODE / "episode.yaml"
OUT = EPISODE / "manifests" / "shots.json"


def main() -> None:
    data = yaml.safe_load(YAML.read_text(encoding="utf-8"))
    payload = {
        "schemaVersion": "1.0.0",
        "episode": {k: v for k, v in data["episode"].items()},
        "shots": data["shots"],
    }
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(data['shots'])} shots to {OUT}")


if __name__ == "__main__":
    main()
