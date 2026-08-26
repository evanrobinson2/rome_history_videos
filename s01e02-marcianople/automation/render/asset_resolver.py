"""Resolve which image file to use for a shot.

Priority (animatic / preview):
  1. manifests/shot-favorites.json  — Evan's explicit pick
  2. manifests/mj-session-index.json  — auto-mapped sample from inbox dump
  3. episode.yaml approved_asset     — only when image_status == approved
  4. manifests/legacy-map.json       — placeholder stills (not for brutalist heist)

Heist banquet shots (visual_mode brutalist_print / indigo_heist) must come from
the MJ dump — never legacy cut-paper placeholders.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
FAVORITES = EPISODE / "manifests" / "shot-favorites.json"
MJ_INDEX = EPISODE / "manifests" / "mj-session-index.json"
LEGACY = EPISODE / "manifests" / "legacy-map.json"

DUMP_ONLY_MODES = frozenset({"brutalist_print", "indigo_heist"})


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _exists(rel: str | None) -> bool:
    return bool(rel and (ROOT / rel).exists())


def resolve_asset(shot: dict) -> tuple[str | None, str]:
    """Return (repo-relative path, source tag)."""
    sid = shot["id"]
    visual_mode = shot.get("visual_mode", "")
    dump_only = visual_mode in DUMP_ONLY_MODES

    favorites = _load_json(FAVORITES).get("picks", {})
    if sid in favorites:
        path = favorites[sid].get("path")
        if _exists(path):
            return path, "favored"

    mj = _load_json(MJ_INDEX)
    pick = mj.get("shot_picks", {}).get(sid)
    if pick:
        path = pick["default_variant"]["path"]
        if _exists(path):
            return path, "mj_sample"

    if shot.get("image_status") == "approved":
        path = shot.get("approved_asset")
        if _exists(path):
            return path, "approved"

    if not dump_only:
        legacy = _load_json(LEGACY)
        for m in legacy.get("mappings", []):
            if m["shot_id"] == sid and _exists(m.get("path")):
                return m["path"], "legacy"

    return None, "none"


def load_renderable_shots(episode_yaml: Path) -> list[dict]:
    """Shots that have a resolvable asset, with resolved path attached."""
    import yaml

    data = yaml.safe_load(episode_yaml.read_text(encoding="utf-8"))
    out: list[dict] = []
    for shot in data["shots"]:
        path, source = resolve_asset(shot)
        if path:
            enriched = dict(shot)
            enriched["resolved_asset"] = path
            enriched["asset_source"] = source
            out.append(enriched)
    return out
