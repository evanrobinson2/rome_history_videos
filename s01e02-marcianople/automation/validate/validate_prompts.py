#!/usr/bin/env python3
"""Validate S01E02 image prompt JSONL files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

MAX_PROMPT_LEN = 1000
TARGET_MIN = 750
TARGET_MAX = 950

PRINCIPALS = {
    "fritigern": ["face", "beard", "brow", "nose", "scar", "cloak", "braid", "shoulder", "hand", "eye", "hair", "chin", "cheek"],
    "alaric": ["curl", "wrist", "cord", "tunic", "eye", "brow", "hood", "face", "hair", "forehead", "gray", "small", "wiry"],
    "brother": ["scarf", "rust", "red", "tooth", "ear", "notch", "wrist", "cord", "tunic", "hazel", "limb", "youth"],
    "mother": ["braid", "auburn", "clasp", "horse", "bronze", "shawl", "cheek", "scar", "thumbnail", "ochre", "dress"],
    "lupicinus": ["ring", "roman", "command", "tunic", "authority", "administrative", "face", "hand", "cloak", "officer"],
}

ANCHOR_PATTERN = re.compile(
    r"\b(face|eye|brow|nose|scar|beard|braid|cloak|tunic|scarf|clasp|curl|wrist|cord|ring|shoulder|cheek|chin|hair|hand|tooth|ear|shawl|helmet|armor)\b",
    re.I,
)


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{i}: invalid JSON: {exc}") from exc
    return rows


def principal_mentions(prompt: str) -> list[str]:
    lower = prompt.lower()
    found: list[str] = []
    for name in PRINCIPALS:
        if re.search(rf"\b{re.escape(name)}\b", lower):
            found.append(name)
    return found


def count_anchors(prompt: str, principal: str) -> int:
    keywords = PRINCIPALS[principal]
    lower = prompt.lower()
    hits = {kw for kw in keywords if kw in lower}
    hits.update(m.group(0).lower() for m in ANCHOR_PATTERN.finditer(prompt))
    return len(hits)


def validate_row(row: dict, *, strict: bool) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    shot_id = row.get("shot_id", "?")
    prompt = row.get("prompt", "")

    if not prompt:
        errors.append(f"{shot_id}: missing prompt")
        return errors, warnings

    plen = len(prompt)
    if plen > MAX_PROMPT_LEN:
        errors.append(f"{shot_id}: prompt length {plen} exceeds max {MAX_PROMPT_LEN}")
    elif plen < TARGET_MIN:
        warnings.append(f"{shot_id}: prompt length {plen} below target {TARGET_MIN}-{TARGET_MAX}")
    elif plen > TARGET_MAX:
        warnings.append(f"{shot_id}: prompt length {plen} above target {TARGET_MIN}-{TARGET_MAX}")

    banned = [
        "cinematic still",
        "movie lighting",
        "movie still",
        "tv frame",
        "actor portrait",
        "anime",
        "ghibli",
        "concept art",
        "conestoga",
        "prairie wagon",
        "white canvas bonnet",
    ]
    lower = prompt.lower()
    for phrase in banned:
        if phrase in lower:
            warnings.append(f"{shot_id}: contains discouraged phrase '{phrase}'")

    for principal in principal_mentions(prompt):
        anchors = count_anchors(prompt, principal)
        if anchors < 3:
            msg = f"{shot_id}: '{principal}' named with only {anchors} physical anchor(s); need >=3"
            if strict:
                errors.append(msg)
            else:
                warnings.append(msg)

    if row.get("aspect_ratio") not in (None, "16:9"):
        warnings.append(f"{shot_id}: unexpected aspect_ratio {row.get('aspect_ratio')}")

    return errors, warnings


def validate_file(path: Path, *, strict: bool) -> int:
    rows = load_jsonl(path)
    all_errors: list[str] = []
    all_warnings: list[str] = []
    for row in rows:
        errors, warnings = validate_row(row, strict=strict)
        all_errors.extend(errors)
        all_warnings.extend(warnings)

    for w in all_warnings:
        print(f"WARN  {w}", file=sys.stderr)
    for e in all_errors:
        print(f"ERROR {e}", file=sys.stderr)

    print(f"{path.name}: {len(rows)} prompts, {len(all_errors)} error(s), {len(all_warnings)} warning(s)")
    return 1 if all_errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate S01E02 image prompts")
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        default=[Path("s01e02-marcianople/prompts/images")],
    )
    parser.add_argument("--strict", action="store_true", help="Treat anchor warnings as errors")
    args = parser.parse_args()

    files: list[Path] = []
    for p in args.paths:
        if p.is_dir():
            files.extend(sorted(p.glob("*.jsonl")))
        elif p.is_file():
            files.append(p)

    if not files:
        print("No JSONL files found", file=sys.stderr)
        return 1

    code = 0
    for f in files:
        code |= validate_file(f, strict=args.strict)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
