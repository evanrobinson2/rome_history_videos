#!/usr/bin/env python3
"""Midjourney dispatch stub — dry-run validates and prints intended actions."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROMPTS = ROOT / "s01e02-marcianople" / "prompts" / "images"
VALIDATOR = ROOT / "s01e02-marcianople" / "automation" / "validate" / "validate_prompts.py"


def load_prompt(shot_id: str) -> dict | None:
    for jsonl in sorted(PROMPTS.glob("*.jsonl")):
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("shot_id") == shot_id:
                return row
    return None


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:12]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot", required=True, help="Shot ID e.g. C01")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    row = load_prompt(args.shot)
    if not row:
        print(f"No prompt found for {args.shot}", file=sys.stderr)
        return 1

    code = subprocess.call([sys.executable, str(VALIDATOR), str(PROMPTS)])
    if code != 0:
        return code

    ph = prompt_hash(row["prompt"])
    print(json.dumps({
        "action": "midjourney_submit" if not args.dry_run else "dry_run",
        "shot_id": args.shot,
        "prompt_hash": ph,
        "aspect_ratio": row.get("aspect_ratio", "16:9"),
        "stylize": row.get("stylize"),
        "chaos": row.get("chaos"),
        "force": args.force,
        "prompt_preview": row["prompt"][:120] + "…",
    }, indent=2))

    if args.dry_run:
        print("\nDry-run only. Set --no-dry-run when browser profile is configured locally.")
    else:
        print("\nLive submission not implemented in cloud agent — run on laptop with authenticated profile.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
