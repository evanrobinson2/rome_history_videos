"""Ken Burns + zag motion for quick animatic stills.

Per remaster directive §13: subtle push-in / lateral drift only — no warping.
"""

from __future__ import annotations

from typing import Any

W, H, FPS = 1920, 1080, 24

# Per-shot motion overrides. Fallback: slow_push (subtle center push-in).
MOTION_BY_SHOT: dict[str, dict[str, Any]] = {
    # Crossing — landscapes drift; family beats zag
    "C01": {"type": "ken_burns", "pan": "right", "zoom_end": 1.1},
    "C04": {"type": "zag", "anchors": ["left", "center", "right"]},
    "C06": {"type": "ken_burns", "pan": "right", "zoom_end": 1.12},
    "C07": {"type": "ken_burns", "pan": "left", "zoom_end": 1.1, "y_end": 0.42},
    "C08": {"type": "zag", "anchors": ["center-left", "center-right"]},
    "C10": {"type": "zag", "anchors": ["left", "center", "right"]},
    "C12": {"type": "slow_push", "zoom_end": 1.08},
    "C13": {"type": "ken_burns", "pan": "left", "zoom_end": 1.09},
    # Heist
    "H01": {"type": "slow_push", "zoom_end": 1.07},
    "H02": {"type": "ken_burns", "pan": "right", "zoom_end": 1.1},
    "H03": {"type": "zag", "anchors": ["left", "right"]},
    "H04": {"type": "hold"},  # native MP4
    "H05": {"type": "ken_burns", "pan": "left", "zoom_end": 1.1},
    "H09": {"type": "ken_burns", "pan": "right", "zoom_end": 1.12},
    "H10": {"type": "ken_burns", "pan": "left", "zoom_end": 1.14},
    "H11": {"type": "slow_push", "zoom_end": 1.08},
    # Battle
    "B01": {"type": "ken_burns", "pan": "right", "zoom_end": 1.12},
    "B02": {"type": "zag", "anchors": ["left", "center", "right"]},
    "B03": {"type": "zag", "anchors": ["left", "center", "right"]},
    "B05": {"type": "ken_burns", "pan": "left", "zoom_end": 1.13},
    "B06": {"type": "slow_push", "zoom_end": 1.06},
    "B07": {"type": "ken_burns", "pan": "right", "zoom_end": 1.1},
    "B08": {"type": "ken_burns", "pan": "left", "zoom_end": 1.1},
    "B09": {"type": "zag", "anchors": ["left", "right"]},
    "B10": {"type": "slow_push", "zoom_end": 1.07},
    "B11": {"type": "slow_push", "zoom_end": 1.08},
    "B13": {"type": "ken_burns", "pan": "right", "zoom_end": 1.11},
    "B14": {"type": "zag", "anchors": ["left", "center-right"]},
    "B15": {"type": "zag", "anchors": ["left", "center", "right"]},
    "B16": {"type": "ken_burns", "pan": "right", "zoom_end": 1.08, "y_end": 0.38},
    "B17": {"type": "slow_push", "zoom_end": 1.1},
}

ANCHOR_X: dict[str, float] = {
    "left": 0.0,
    "center-left": 0.25,
    "center": 0.5,
    "center-right": 0.75,
    "right": 1.0,
}

PAN_START_END: dict[str, tuple[float, float]] = {
    "left": (0.65, 0.35),
    "right": (0.35, 0.65),
    "up": (0.5, 0.5),  # y handled separately
    "down": (0.5, 0.5),
}


def resolve_motion(shot: dict) -> dict[str, Any]:
    profile = MOTION_BY_SHOT.get(shot["id"])
    if profile:
        return profile
    anim = shot.get("animation") or "slow_push"
    if anim == "slow_push":
        return {"type": "slow_push", "zoom_end": 1.08}
    return {"type": anim}


def ken_burns_vf(
    dur: float,
    *,
    zoom_start: float = 1.0,
    zoom_end: float = 1.1,
    x_start: float = 0.5,
    x_end: float = 0.5,
    y_start: float = 0.5,
    y_end: float = 0.5,
) -> str:
    frames = max(int(round(dur * FPS)), 1)
    z0, z1 = zoom_start, zoom_end
    z_expr = f"'if(lte(on,{frames}),{z0}+({z1}-{z0})*on/{frames},{z1})'"
    x_expr = f"'(iw-iw/zoom)*({x_start}+({x_end}-{x_start})*on/{frames})'"
    y_expr = f"'(ih-ih/zoom)*({y_start}+({y_end}-{y_start})*on/{frames})'"
    return (
        f"scale=8000:-1,"
        f"zoompan=z={z_expr}:x={x_expr}:y={y_expr}:d={frames}:s={W}x{H}:fps={FPS},"
        f"format=yuv420p"
    )


def ken_burns_from_profile(dur: float, profile: dict[str, Any]) -> str:
    pan = profile.get("pan", "none")
    zoom_end = float(profile.get("zoom_end", 1.1))
    y_end = float(profile.get("y_end", 0.5))
    if pan in PAN_START_END:
        x_start, x_end = PAN_START_END[pan]
    else:
        x_start = x_end = 0.5
    y_start = 0.5
    if pan == "up":
        y_start, y_end = 0.55, 0.35
    elif pan == "down":
        y_start, y_end = 0.45, 0.55
    return ken_burns_vf(
        dur,
        zoom_end=zoom_end,
        x_start=x_start,
        x_end=x_end,
        y_start=y_start,
        y_end=y_end,
    )


def slow_push_vf(dur: float, zoom_end: float = 1.08) -> str:
    return ken_burns_vf(dur, zoom_end=zoom_end)


def zag_beat_vf(anchor: str, zoom: float = 1.22) -> str:
    x_frac = ANCHOR_X.get(anchor, 0.5)
    zw, zh = int(W * zoom), int(H * zoom)
    return (
        f"scale={zw}:{zh}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H}:x='max(0,min(iw-{W},(iw-{W})*{x_frac}))':y='(ih-{H})/2',"
        f"fps={FPS},format=yuv420p"
    )


def zag_beats(profile: dict[str, Any]) -> list[str]:
    return list(profile.get("anchors", ["left", "right"]))
