"""Caption copy + ASS styling for S01E02 animatic.

Design refs (2025–2026):
- Long-form / documentary: humanist sans, sentence case, lower-third, soft shadow,
  ~38 chars/line, 2 lines max — not TikTok stroke/highlight (ChatCut, Elysiate).
- Chapter cards: brief, separate from narration rhythm.
- Accessibility export: clean SRT without production metadata.
"""

from __future__ import annotations

import textwrap
from dataclasses import dataclass

# Movement chapter cards (designed typography — brief, not production notes)
MOVEMENT_CHAPTERS: dict[str, tuple[str, str]] = {
    "crossing": ("The Danube", "376 CE"),
    "heist": ("Marcianople", "The banquet trap"),
    "battle": ("Nine miles from the city", "They mistook hunger for helplessness"),
}

# Narrator voice — restrained, intimate; never labels the shot ID
NARRATION: dict[str, str] = {
    "C01": "They looked across the water and believed Rome would shelter them.",
    "C04": "Weapons were surrendered for a promise of land and peace.",
    "C06": "The barrier closed. Fields and granaries stayed visible beyond the fence.",
    "C07": "Food became leverage. Bowls stayed empty while grain was guarded.",
    "C08": "A bronze horse clasp changed hands for a crust of bread.",
    "C10": "A brother was taken. The family broke in plain sight.",
    "C12": "She fed what was left of the child. A torn scarf stayed in his fist.",
    "C13": "Lupicinus offered a banquet — warmth performed as reconciliation.",
    "H01": "Below the hall, Roman blades were readied in secret.",
    "H02": "The invitation was an execution dressed as hospitality.",
    "H03": "Fritigern took Lupicinus hostage before the trap could close.",
    "H04": "The hall became violence.",
    "H05": "While spectacle held the room, the counteroperation moved elsewhere.",
    "H09": "Confiscated arms crossed the postern gate in wagons.",
    "H10": "Cloaked riders carried the weapons into indigo night.",
    "H11": "Fritigern left with Lupicinus still alive.",
    "B01": "The stolen weapons reached a wooded clearing.",
    "B02": "Children, wounded, and elders waited among the wagons.",
    "B03": "Travel cloaks fell. Men trained to fight stood in their place.",
    "B05": "Roman infantry approached as if slaughtering refugees would be simple.",
    "B06": "A young soldier saw what was forming ahead — and understood too late.",
    "B07": "Arrows found Roman shields.",
    "B08": "Gothic shields drove the line backward.",
    "B09": "Orders dissolved into noise.",
    "B10": "An older Roman saw children beneath the canvas.",
    "B11": "Alaric watched without understanding everything — only that it was terror.",
    "B13": "The Roman formation fractured. The Gothic line held.",
    "B14": "Fritigern and Lupicinus fought toward the wagons where families hid.",
    "B15": "He had taken up the knife for his child. He would not teach the child to worship it.",
    "B16": "Sunlight and flowers continued after the violence fell away.",
    "B17": "A damaged Roman helmet passed into the child's hands — inheritance, not trophy.",
}

DISCLOSURE = (
    "Inspired by the Gothic migration and war of 376–382 CE. "
    "Some characters, relationships, chronology, and events have been dramatized."
)

CHARS_PER_LINE = 40
MAX_LINES = 2
CHAPTER_SEC = 2.4


@dataclass
class CaptionEvent:
    start: float
    end: float
    style: str
    text: str


def wrap_narration(text: str) -> str:
    lines = textwrap.wrap(text, width=CHARS_PER_LINE)
    if len(lines) > MAX_LINES:
        # Prefer breaking at em-dash or period
        lines = textwrap.wrap(text, width=CHARS_PER_LINE, break_long_words=False, break_on_hyphens=False)
    return "\\N".join(lines[:MAX_LINES])


def sec_to_ass(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def sec_to_srt(t: float) -> str:
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def build_events(shots: list[dict]) -> tuple[list[CaptionEvent], float]:
    events: list[CaptionEvent] = []
    t = 0.0
    last_movement = None
    for shot in shots:
        mov = shot["movement"]
        dur = float(shot["duration_target_sec"])
        end = t + dur
        narr_start = t

        if mov != last_movement:
            title, subtitle = MOVEMENT_CHAPTERS.get(mov, (mov.title(), ""))
            chapter_end = min(t + CHAPTER_SEC, end - 0.5) if dur > CHAPTER_SEC + 1 else min(t + 1.8, end - 0.3)
            chapter_text = title if not subtitle else f"{title}\\N{subtitle}"
            events.append(CaptionEvent(t, chapter_end, "Chapter", chapter_text))
            narr_start = chapter_end
            last_movement = mov

        text = NARRATION.get(shot["id"], shot.get("purpose", ""))
        if narr_start < end - 0.2:
            events.append(CaptionEvent(narr_start, end, "Narration", wrap_narration(text)))
        t = end

    disc_end = t + 5.0
    events.append(CaptionEvent(t, disc_end, "Disclosure", wrap_narration(DISCLOSURE)))
    return events, disc_end


ASS_HEADER = """[Script Info]
Title: S01E02 Marcianople
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Narration,Inter,48,&H00E8E4DC,&H000000FF,&H00000000,&H64000000,0,0,0,0,100,100,0,0,3,0,3,80,80,88,1
Style: Chapter,Inter,62,&H00D4C4A8,&H000000FF,&H00000000,&H78000000,-1,0,0,0,102,100,2,0,3,0,4,0,0,0,1
Style: Disclosure,Inter,34,&H00B8B8B8,&H000000FF,&H00000000,&H50000000,0,0,0,0,100,100,0,0,1,0,0,2,120,120,72,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def write_ass(events: list[CaptionEvent], path) -> None:
    lines = [ASS_HEADER]
    for ev in events:
        lines.append(
            f"Dialogue: 0,{sec_to_ass(ev.start)},{sec_to_ass(ev.end)},"
            f"{ev.style},,0,0,0,,{ev.text}"
        )
    path.write_text("\n".join(lines), encoding="utf-8")


def write_srt(events: list[CaptionEvent], path) -> None:
    """Accessibility export — narration + disclosure only, no chapter styling metadata."""
    lines: list[str] = []
    idx = 1
    for ev in events:
        if ev.style == "Chapter":
            continue
        plain = ev.text.replace("\\N", "\n")
        lines += [str(idx), f"{sec_to_srt(ev.start)} --> {sec_to_srt(ev.end)}", plain, ""]
        idx += 1
    path.write_text("\n".join(lines), encoding="utf-8")
