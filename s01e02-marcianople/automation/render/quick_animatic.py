#!/usr/bin/env python3
"""Quick-pass S01E02 slideshow: images + music + draft captions."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import textwrap
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
MUSIC = EPISODE / "assets" / "music"
OUT_DIR = EPISODE / "renders" / "animatics"
WORK = OUT_DIR / "_work"

W, H, FPS = 1920, 1080, 24

MOVEMENT_MUSIC = {
    "crossing": "crossing_open.mp3",
    "heist": "heist_groove.mp3",
    "battle": "battle.mp3",
}

MOVEMENT_INTROS = {
    "crossing": "376 CE. The Goths cross the Danube seeking land and peace.",
    "heist": "Marcianople. The banquet is a trap — but Fritigern entered with a plan.",
    "battle": "They believed hunger had made us helpless.",
}

SHOT_CAPTIONS: dict[str, str] = {
    "C01": "Families look across the Danube toward promised Roman refuge.",
    "C04": "Weapons surrendered at the landing — the bargain Rome will break.",
    "C06": "The barrier closes. Granaries remain visible beyond the fence.",
    "C07": "Mud, empty bowls, guarded grain.",
    "C08": "A bronze clasp offered for bread.",
    "C10": "Brothers pulled apart.",
    "C12": "Bread becomes grief and survival.",
    "C13": "Lupicinus offers reconciliation.",
    "H01": "Roman blades prepared beneath the hall.",
    "H02": "The assassination banquet.",
    "H03": "Fritigern takes Lupicinus hostage.",
    "H04": "The hall erupts.",
    "H05": "The counteroperation moves through the corridors.",
    "H09": "Wagons cross the postern gate.",
    "H10": "Weapons ride into the indigo night.",
    "H11": "Fritigern leaves with Lupicinus alive.",
    "B01": "Weapon wagons reach the wooded clearing.",
    "B02": "Families concealed among the wagons.",
    "B03": "Travel cloaks fall. Trained defenders appear.",
    "B05": "Romans approach, overconfident.",
    "B06": "A young Roman soldier realizes what is forming ahead.",
    "B07": "Arrows strike Roman shields.",
    "B08": "Gothic shields drive the line backward.",
    "B09": "Orders vanish in chaos.",
    "B10": "An older Roman sees children in the wagons.",
    "B11": "Alaric watches from beneath the canvas.",
    "B13": "The Roman formation fractures.",
    "B14": "Fritigern and Lupicinus fight toward the wagons.",
    "B15": "He had taken up the knife for his child. He would not teach the child to worship it.",
    "B16": "Flowers and sunlight continue as sound falls away.",
    "B17": "The helmet becomes inheritance.",
}


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(cmd[:8]), ("..." if len(cmd) > 8 else ""))
    subprocess.run(cmd, check=True, **kw)


def sec_to_srt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def load_shots() -> list[dict]:
    data = yaml.safe_load((EPISODE / "episode.yaml").read_text(encoding="utf-8"))
    shots = [s for s in data["shots"] if s.get("approved_asset")]
    for s in shots:
        p = ROOT / s["approved_asset"]
        if not p.exists():
            raise FileNotFoundError(p)
    return shots


def build_srt(shots: list[dict], path: Path) -> float:
    lines: list[str] = []
    idx = 1
    t = 0.0
    last_movement = None
    for shot in shots:
        mov = shot["movement"]
        dur = float(shot["duration_target_sec"])
        end = t + dur
        cap_parts: list[str] = []
        if mov != last_movement:
            intro = MOVEMENT_INTROS.get(mov, "")
            if intro:
                cap_parts.append(intro)
            last_movement = mov
        cap_parts.append(f"[{shot['id']}] {SHOT_CAPTIONS.get(shot['id'], shot.get('purpose', shot['id']))}")
        lines += [
            str(idx),
            f"{sec_to_srt(t)} --> {sec_to_srt(end)}",
            "\n".join(cap_parts),
            "",
        ]
        idx += 1
        t = end
    disc_end = t + 4.0
    lines += [
        str(idx),
        f"{sec_to_srt(t)} --> {sec_to_srt(disc_end)}",
        "Inspired by the Gothic migration and war of 376–382 CE. Some characters, relationships, chronology, and events have been dramatized.",
        "",
    ]
    t = disc_end
    path.write_text("\n".join(lines), encoding="utf-8")
    return t


def segment_from_shot(shot: dict, out: Path) -> None:
    src = ROOT / shot["approved_asset"]
    dur = shot["duration_target_sec"]
    label = f"{shot['id']} {shot['movement']}".replace(":", "\\:").replace("'", "\\'")
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
        f"drawtext=text='{label}':fontsize=28:fontcolor=white@0.55:"
        f"x=40:y=h-60:box=1:boxcolor=black@0.35:boxborderw=8,"
        f"fps={FPS},format=yuv420p"
    )
    if src.suffix.lower() == ".mp4":
        run([
            "ffmpeg", "-y", "-i", str(src),
            "-t", str(dur), "-an",
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            str(out),
        ])
    else:
        run([
            "ffmpeg", "-y", "-loop", "1", "-i", str(src),
            "-t", str(dur),
            "-vf", vf,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
            str(out),
        ])


def concat_video(segments: list[Path], out: Path) -> None:
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segments), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", str(out),
    ])


def build_music(shots: list[dict], total: float, out: Path) -> None:
    """Stitch movement music beds to match visual runtime."""
    spans: list[tuple[str, float, float]] = []
    t = 0.0
    cur_mov = None
    start = 0.0
    for shot in shots:
        mov = shot["movement"]
        dur = float(shot["duration_target_sec"])
        if mov != cur_mov:
            if cur_mov is not None:
                spans.append((cur_mov, start, t))
            cur_mov = mov
            start = t
        t += dur
    if cur_mov is not None:
        spans.append((cur_mov, start, t))

    # battle ends into denouement for last ~20s
    denouement_tail = 20.0
    parts: list[Path] = []
    for i, (mov, start, end) in enumerate(spans):
        bed = MUSIC / MOVEMENT_MUSIC[mov]
        length = end - start
        if mov == "battle" and length > denouement_tail + 5:
            battle_len = length - denouement_tail
            p1 = WORK / f"music_{i}a.mp3"
            p2 = WORK / f"music_{i}b.mp3"
            run(["ffmpeg", "-y", "-i", str(bed), "-t", str(battle_len), "-c", "copy", str(p1)])
            run([
                "ffmpeg", "-y", "-i", str(MUSIC / "denouement.mp3"),
                "-t", str(denouement_tail), "-c", "copy", str(p2),
            ])
            parts.extend([p1, p2])
        else:
            p = WORK / f"music_{i}.mp3"
            run(["ffmpeg", "-y", "-i", str(bed), "-t", str(length), "-c", "copy", str(p)])
            parts.append(p)

    lst = WORK / "music_concat.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", str(out),
    ])


def mux(video: Path, audio: Path, srt: Path, out_mp4: Path, out_m4a: Path) -> None:
    srt_esc = str(srt).replace(":", "\\:").replace("'", "\\'")
    run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-vf", f"subtitles='{srt_esc}':force_style='Fontsize=22,PrimaryColour=&HFFFFFF,OutlineColour=&H000000,BorderStyle=3,Outline=2,Shadow=0,MarginV=40'",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_mp4),
    ])
    run([
        "ffmpeg", "-y", "-i", str(out_mp4),
        "-vn", "-c:a", "copy",
        str(out_m4a),
    ])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="S01E02_quick_pass")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    shots = load_shots()
    srt = OUT_DIR / f"{args.name}.srt"
    total = build_srt(shots, srt)

    segments: list[Path] = []
    for shot in shots:
        seg = WORK / f"{shot['id']}.mp4"
        segment_from_shot(shot, seg)
        segments.append(seg)

    # Hold last frame for disclosure caption
    hold = WORK / "hold.mp4"
    run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(segments[-1]),
        "-t", "4", "-c", "copy", str(hold),
    ])
    segments.append(hold)

    silent = WORK / "silent.mp4"
    concat_video(segments, silent)

    music = WORK / "music.mp3"
    build_music(shots, total, music)
    # pad music to disclosure hold if needed
    run([
        "ffmpeg", "-y", "-i", str(music), "-af", "apad=pad_dur=4", "-c:a", "libmp3lame", "-q:a", "2",
        str(WORK / "music_padded.mp3"),
    ])
    music = WORK / "music_padded.mp3"

    out_mp4 = OUT_DIR / f"{args.name}.mp4"
    out_m4a = OUT_DIR / f"{args.name}.m4a"
    mux(silent, music, srt, out_mp4, out_m4a)

    meta = {
        "shots": len(shots),
        "duration_sec": total,
        "outputs": {
            "mp4": str(out_mp4.relative_to(ROOT)),
            "m4a": str(out_m4a.relative_to(ROOT)),
            "srt": str(srt.relative_to(ROOT)),
        },
    }
    (OUT_DIR / f"{args.name}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
