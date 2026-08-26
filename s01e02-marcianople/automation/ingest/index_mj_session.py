#!/usr/bin/env python3
"""Index Midjourney session dump and suggest S01E02 shot mappings."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SESSION = ROOT / "feedback" / "inbox" / "2026-08-26-midjourney-session"
OUT = ROOT / "s01e02-marcianople" / "manifests" / "mj-session-index.json"

JOB_RE = re.compile(
    r"^(?P<prefix>.+?)_(?P<job>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})_(?P<idx>\d+)\.(?P<ext>png|mp4)$",
    re.I,
)

# Ordered rules: first match wins. More specific rules MUST come before general ones.
SHOT_RULES: list[tuple[str, list[str], str]] = [
    ("H01", ["hidden_roman_preparation_chamber"], "Roman blades/restraints prepared"),
    ("H02", ["assassination_banquet", "feast_prepared_as_an_execution"], "Banquet trap / entry"),
    ("H03", ["hostage_scene", "fritigern_holdi", "fritigern_pow"], "Fritigern holds Lupicinus"),
    ("H04", ["banquet_collapsing_into_panic"], "Banquet chaos"),
    ("H05", ["narrow_service_passage", "service_passage_behind"], "Corridor / guard kill"),
    ("H09", ["outside_the_fortified_roman_gate", "rear_gate"], "Postern / gate extraction"),
    ("H10", ["cloaked_gothic_riders_escorting", "moonless_night_beyond_marcianople"], "Indigo escape"),
    ("H11", ["suspended_moment_inside_the_marcianople_banquet"], "Fritigern exits with Lupicinus alive"),
    ("B14", ["fritigern_and_lupicinus_fighting_beside"], "Fritigern vs Lupicinus at wagons"),
    ("B15", ["three_figure_scene_beside_a_covered_wagon", "three_figures_beside_a_covered_wagon", "clean_three_figure_composition_beside_a_covered_wagon"], "Mercy — canonical candidate"),
    ("B17", ["young_gothic_boy_alaric_stands_alone_after_the_battle"], "Child Alaric alone + helmet"),
    ("B01", ["wooded_clearing_hungry_but_trained"], "Weapon wagons reach clearing"),
    ("B02", ["refugees_prepar"], "Families concealed / preparation"),
    ("B03", ["refugees_transform_into"], "Cloaks fall / defenders appear"),
    ("B05", ["roman_infantry_approaching_a_wooded_refug"], "Romans approach overconfidently"),
    ("B06", ["young_roman_infantryman_as_confidence"], "Roman first realization"),
    ("B07", ["formation_as_the_fir"], "Arrow volley / first shock"),
    ("B09", ["junior_officer_shouting_an_order"], "Command failure"),
    ("B10", ["older_roman_veteran_pressed_among_coll"], "Older Roman sees children"),
    ("B11", ["alaric_peering_from_beneath"], "Alaric under wagon canvas"),
    ("B16", ["wounded_fritiger"], "Aftermath at wagon refuge"),
    ("H04", ["banquet_hall_at_marcianople"], "Banquet hall panic (alt)"),
]

# Prefer these job IDs when multiple jobs map to the same shot (grid 0 png).
PREFERRED_JOBS: dict[str, str] = {
    "B15": "7bd5f5ff-9057-4f02-b584-f621806e5e34",  # Three_figure_scene… mercy
    "B17": "47823736-ecbd-4269-83a4-1bbf333faa6b",  # Young_Gothic_boy_Alaric_stands_alone…
}

OFF_EPISODE = [
    "adrianople",
    "empty_late-roman_ar",
    "empty_armor",
    "empty_gothic_armor",
    "two_versions_of_the_same_man",
    "vertical_diptych",
    "continuous_vertical_composition_same_person",
    "continuous_vertical_composition_with_no_hard_split",
    "pasta_brand_packaging",
    "catastrophic_defeat_on_a_barren",
    "aftermath_of_catastrophic_defeat",
    "headles",
    "locked-off_tripod_shot",
    "nightmare_of_the_marcianople_banquet",
    "graphic_digital_animation_illustration_of_fritigern_overpower",
]


def sha256_prefix(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def normalize_prefix(prefix: str) -> str:
    return prefix.lower().replace("-", "_")


def suggest_shot(prefix_norm: str) -> tuple[str | None, str | None]:
    for off in OFF_EPISODE:
        if off in prefix_norm:
            return None, f"off_episode:{off}"
    for shot_id, keys, note in SHOT_RULES:
        for key in keys:
            if key in prefix_norm:
                return shot_id, note
    return None, None


def main() -> None:
    if not SESSION.exists():
        raise SystemExit(f"Missing session dir: {SESSION}")

    jobs: dict[str, dict] = {}
    for path in sorted(SESSION.iterdir()):
        if not path.is_file():
            continue
        m = JOB_RE.match(path.name)
        if not m:
            continue
        rel = path.relative_to(ROOT).as_posix()
        job_id = m.group("job")
        prefix_norm = normalize_prefix(m.group("prefix"))
        shot_id, reason = suggest_shot(prefix_norm)
        entry = {
            "path": rel,
            "grid_index": int(m.group("idx")),
            "ext": m.group("ext").lower(),
            "bytes": path.stat().st_size,
            "sha256": sha256_prefix(path),
            "prefix": m.group("prefix"),
            "suggested_shot_id": shot_id,
            "mapping_reason": reason,
        }
        job = jobs.setdefault(
            job_id,
            {
                "job_id": job_id,
                "prefix": m.group("prefix"),
                "prefix_norm": prefix_norm,
                "suggested_shot_id": shot_id,
                "mapping_reason": reason,
                "variants": [],
            },
        )
        if shot_id and not job["suggested_shot_id"]:
            job["suggested_shot_id"] = shot_id
            job["mapping_reason"] = reason
        job["variants"].append(entry)

    # Pick default variant (grid 0 png preferred) per mapped shot
    shot_picks: dict[str, dict] = {}
    unmapped: list[str] = []
    off_episode: list[str] = []
    for job in jobs.values():
        sid = job["suggested_shot_id"]
        if not sid:
            reason = job.get("mapping_reason")
            if isinstance(reason, str) and reason.startswith("off_episode"):
                off_episode.append(job["job_id"])
            else:
                unmapped.append(job["job_id"])
            continue
        preferred = PREFERRED_JOBS.get(sid)
        if preferred and job["job_id"] == preferred:
            pngs = [v for v in job["variants"] if v["ext"] == "png"]
            pick = next((v for v in pngs if v["grid_index"] == 0), pngs[0] if pngs else job["variants"][0])
            shot_picks[sid] = {
                "shot_id": sid,
                "default_variant": pick,
                "job_id": job["job_id"],
                "all_variant_paths": [v["path"] for v in job["variants"]],
                "pick_reason": "preferred_job",
            }
            continue
        pngs = [v for v in job["variants"] if v["ext"] == "png"]
        pick = next((v for v in pngs if v["grid_index"] == 0), pngs[0] if pngs else job["variants"][0])
        prev = shot_picks.get(sid)
        if prev and prev.get("pick_reason") == "preferred_job":
            continue
        if not prev or pick["bytes"] > prev["default_variant"]["bytes"]:
            shot_picks[sid] = {
                "shot_id": sid,
                "default_variant": pick,
                "job_id": job["job_id"],
                "all_variant_paths": [v["path"] for v in job["variants"]],
            }

    payload = {
        "schemaVersion": "1.0.0",
        "source_commit": "b05c11d",
        "session_dir": SESSION.relative_to(ROOT).as_posix(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "jobs": len(jobs),
            "files": sum(len(j["variants"]) for j in jobs.values()),
            "mapped_shots": len(shot_picks),
            "unmapped_jobs": len(unmapped),
            "off_episode_jobs": len(off_episode),
        },
        "shot_picks": shot_picks,
        "jobs": jobs,
        "unmapped_job_ids": unmapped,
        "off_episode_job_ids": off_episode,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2))
    print("Mapped shots:", sorted(shot_picks.keys()))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
