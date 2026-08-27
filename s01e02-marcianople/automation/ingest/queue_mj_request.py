#!/usr/bin/env python3
"""Queue a Midjourney generation request for the browser agent."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
PROMPTS = EPISODE / "prompts" / "images"
PENDING = EPISODE / "agent-bus" / "queue" / "pending"
LOG = EPISODE / "agent-bus" / "log" / "visuals.ndjson"


def load_prompt(shot_id: str) -> dict | None:
    for jsonl in sorted(PROMPTS.glob("*.jsonl")):
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("shot_id") == shot_id:
                return row
    return None


def slug(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:40] or "shot"


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(prompt.encode()).hexdigest()[:8]


def existing_hash_dirs(phash: str) -> list[Path]:
    runs = ROOT / "feedback" / "inbox" / "mj-runs"
    if not runs.exists():
        return []
    return [p for p in runs.iterdir() if p.is_dir() and phash in p.name]


def append_log(event: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shot", required=True, help="Shot ID e.g. H06")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--priority", type=int, default=10)
    args = parser.parse_args()

    row = load_prompt(args.shot)
    if not row:
        print(f"No prompt for {args.shot} in {PROMPTS}", file=__import__("sys").stderr)
        return 1

    phash = prompt_hash(row["prompt"])
    if existing_hash_dirs(phash) and not args.force:
        print(f"Skip: prompt_hash {phash} already in mj-runs (use --force)")
        return 0

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    purpose = row.get("purpose", args.shot)
    out_dir = f"feedback/inbox/mj-runs/{today}-{args.shot}-{slug(purpose)}-{phash}"
    req_id = f"req-{args.shot}-{phash}"

    request = {
        "id": req_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_by": "luna-visuals",
        "shot_id": args.shot,
        "purpose": purpose,
        "visual_mode": row.get("visual_mode", "brutalist_print"),
        "action": "midjourney_generate",
        "prompt": row["prompt"],
        "prompt_hash": phash,
        "mj": {
            "aspect_ratio": row.get("aspect_ratio", "16:9"),
            "stylize": row.get("stylize", 250),
            "chaos": row.get("chaos", 4),
        },
        "output_dir": out_dir,
        "filenames": [f"{args.shot}_{i}.png" for i in range(4)],
        "priority": args.priority,
        "force": args.force,
        "status": "pending",
    }

    PENDING.mkdir(parents=True, exist_ok=True)
    out = PENDING / f"{req_id}.json"
    out.write_text(json.dumps(request, indent=2) + "\n", encoding="utf-8")

    append_log({
        "ts": datetime.now(timezone.utc).isoformat(),
        "kind": "queue",
        "request_id": req_id,
        "shot_id": args.shot,
        "text": f"Queued {purpose}",
        "output_dir": out_dir,
    })

    print(json.dumps(request, indent=2))
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
