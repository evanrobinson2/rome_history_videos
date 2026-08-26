#!/usr/bin/env python3
"""Quick-pass S01E02 slideshow: images + music + documentary captions + motion."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
MUSIC = EPISODE / "assets" / "music"
OUT_DIR = EPISODE / "renders" / "animatics"
WORK = OUT_DIR / "_work"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from caption_styles import build_events, write_ass, write_srt  # noqa: E402
from motion_effects import (  # noqa: E402
    FPS,
    H,
    W,
    ken_burns_from_profile,
    resolve_motion,
    slow_push_vf,
    zag_beat_vf,
    zag_beats,
)

MOVEMENT_MUSIC = {
    "crossing": "crossing_open.mp3",
    "heist": "heist_groove.mp3",
    "battle": "battle.mp3",
}


def run(cmd: list[str], **kw) -> None:
    print("+", " ".join(cmd[:8]), ("..." if len(cmd) > 8 else ""))
    subprocess.run(cmd, check=True, **kw)


def load_shots() -> list[dict]:
    data = yaml.safe_load((EPISODE / "episode.yaml").read_text(encoding="utf-8"))
    shots = [s for s in data["shots"] if s.get("approved_asset")]
    for s in shots:
        p = ROOT / s["approved_asset"]
        if not p.exists():
            raise FileNotFoundError(p)
    return shots


def _watermark_vf(review_watermark: bool, shot: dict) -> str:
    if not review_watermark:
        return ""
    label = f"{shot['id']}".replace(":", "\\:").replace("'", "\\'")
    return (
        f"drawtext=text='{label}':fontsize=22:fontcolor=white@0.35:"
        f"x=24:y=h-44:box=1:boxcolor=black@0.25:boxborderw=6,"
    )


def _encode_still(src: Path, dur: float, vf: str, out: Path) -> None:
    run([
        "ffmpeg", "-y", "-loop", "1", "-i", str(src),
        "-t", str(dur),
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
        str(out),
    ])


def _encode_video(src: Path, dur: float, vf: str, out: Path) -> None:
    run([
        "ffmpeg", "-y", "-i", str(src),
        "-t", str(dur), "-an",
        "-vf", vf,
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        str(out),
    ])


def _static_vf(review_watermark: bool, shot: dict) -> str:
    vf = (
        f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
        f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black,"
    )
    vf += _watermark_vf(review_watermark, shot)
    vf += f"fps={FPS},format=yuv420p"
    return vf


def render_zag_segment(
    src: Path,
    dur: float,
    profile: dict,
    out: Path,
    *,
    review_watermark: bool,
    shot: dict,
) -> None:
    anchors = zag_beats(profile)
    beat_dur = dur / len(anchors)
    beats: list[Path] = []
    wm = _watermark_vf(review_watermark, shot)
    for i, anchor in enumerate(anchors):
        beat = out.parent / f"{out.stem}_zag{i}.mp4"
        vf = zag_beat_vf(anchor) + ("," + wm if wm else "")
        _encode_still(src, beat_dur, vf, beat)
        beats.append(beat)
    lst = out.parent / f"{out.stem}_zag.txt"
    lst.write_text("".join(f"file '{b}'\n" for b in beats), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", str(out),
    ])


def segment_from_shot(
    shot: dict,
    out: Path,
    *,
    review_watermark: bool,
    static: bool,
) -> None:
    src = ROOT / shot["approved_asset"]
    dur = float(shot["duration_target_sec"])
    is_video = src.suffix.lower() == ".mp4"

    if static or is_video:
        vf = _static_vf(review_watermark, shot)
        if is_video:
            _encode_video(src, dur, vf, out)
        else:
            _encode_still(src, dur, vf, out)
        return

    profile = resolve_motion(shot)
    motion_type = profile.get("type", "slow_push")
    wm = _watermark_vf(review_watermark, shot)

    if motion_type == "zag":
        render_zag_segment(src, dur, profile, out, review_watermark=review_watermark, shot=shot)
        return

    if motion_type == "ken_burns":
        vf = ken_burns_from_profile(dur, profile)
    elif motion_type == "hold":
        vf = _static_vf(review_watermark, shot)
        _encode_still(src, dur, vf, out)
        return
    else:
        vf = slow_push_vf(dur, float(profile.get("zoom_end", 1.08)))

    if wm:
        vf += "," + wm
    _encode_still(src, dur, vf, out)


def concat_video(segments: list[Path], out: Path) -> None:
    lst = out.parent / "concat.txt"
    lst.write_text("".join(f"file '{s}'\n" for s in segments), encoding="utf-8")
    run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst),
        "-c", "copy", str(out),
    ])


def build_music(shots: list[dict], out: Path) -> None:
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

    denouement_tail = 20.0
    parts: list[Path] = []
    for i, (mov, start, end) in enumerate(spans):
        bed = MUSIC / MOVEMENT_MUSIC[mov]
        length = end - start
        if mov == "battle" and length > denouement_tail + 5:
            p1 = WORK / f"music_{i}a.mp3"
            p2 = WORK / f"music_{i}b.mp3"
            run(["ffmpeg", "-y", "-i", str(bed), "-t", str(length - denouement_tail), "-c", "copy", str(p1)])
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
    run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])


def mux(video: Path, audio: Path, ass: Path, out_mp4: Path, out_m4a: Path) -> None:
    ass_esc = str(ass).replace(":", "\\:").replace("'", "\\'")
    run([
        "ffmpeg", "-y",
        "-i", str(video),
        "-i", str(audio),
        "-vf", f"ass='{ass_esc}'",
        "-map", "0:v:0", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k", "-shortest",
        str(out_mp4),
    ])
    run(["ffmpeg", "-y", "-i", str(out_mp4), "-vn", "-c:a", "copy", str(out_m4a)])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", default="S01E02_quick_pass_v3")
    parser.add_argument("--review-watermark", action="store_true", help="Tiny shot ID for internal review")
    parser.add_argument("--static", action="store_true", help="Disable Ken Burns / zag motion")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    shots = load_shots()
    events, total = build_events(shots)

    ass_path = OUT_DIR / f"{args.name}.ass"
    srt_path = OUT_DIR / f"{args.name}.srt"
    write_ass(events, ass_path)
    write_srt(events, srt_path)

    motion_summary: dict[str, int] = {}
    segments: list[Path] = []
    for shot in shots:
        seg = WORK / f"{shot['id']}.mp4"
        profile = resolve_motion(shot)
        mtype = "static" if args.static else profile.get("type", "slow_push")
        motion_summary[mtype] = motion_summary.get(mtype, 0) + 1
        segment_from_shot(shot, seg, review_watermark=args.review_watermark, static=args.static)
        segments.append(seg)

    hold = WORK / "hold.mp4"
    run([
        "ffmpeg", "-y", "-stream_loop", "-1", "-i", str(segments[-1]),
        "-t", "5", "-c", "copy", str(hold),
    ])
    segments.append(hold)

    silent = WORK / "silent.mp4"
    concat_video(segments, silent)

    music = WORK / "music.mp3"
    build_music(shots, music)
    run([
        "ffmpeg", "-y", "-i", str(music), "-af", "apad=pad_dur=5",
        "-c:a", "libmp3lame", "-q:a", "2", str(WORK / "music_padded.mp3"),
    ])

    out_mp4 = OUT_DIR / f"{args.name}.mp4"
    out_m4a = OUT_DIR / f"{args.name}.m4a"
    mux(silent, WORK / "music_padded.mp3", ass_path, out_mp4, out_m4a)

    meta = {
        "shots": len(shots),
        "duration_sec": total,
        "motion": motion_summary if not args.static else {"static": len(shots)},
        "caption_style": "documentary ASS — Inter, lower-third narration, chapter cards",
        "outputs": {
            "mp4": str(out_mp4.relative_to(ROOT)),
            "m4a": str(out_m4a.relative_to(ROOT)),
            "ass": str(ass_path.relative_to(ROOT)),
            "srt": str(srt_path.relative_to(ROOT)),
        },
    }
    (OUT_DIR / f"{args.name}.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))


if __name__ == "__main__":
    main()
