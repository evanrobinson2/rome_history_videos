#!/usr/bin/env python3
"""Generate deck-driven production plan review UI."""

from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
PLAN = EPISODE / "manifests" / "deck-shot-plan.json"
PROMPTS_DIR = EPISODE / "prompts" / "images"
OUT = EPISODE / "renders" / "reviews" / "deck-plan.html"

STATUS_COLORS = {
    "needed": "#c44",
    "redo": "#c84",
    "review_dump": "#48a",
    "skip": "#666",
}


def load_prompts() -> dict[str, str]:
    prompts: dict[str, str] = {}
    for path in sorted(PROMPTS_DIR.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            sid = row.get("shot_id")
            if sid:
                prompts[sid] = row.get("prompt", "")
    return prompts


def resolve_prompt(ref: str | None, prompts: dict[str, str]) -> str:
    if not ref:
        return ""
    if ":" in ref:
        _, sid = ref.split(":", 1)
        return prompts.get(sid, "")
    return prompts.get(ref, "")


def render_card(beat: dict, prompts: dict[str, str]) -> str:
    slide = beat["slide"]
    status = beat.get("mj_status", "")
    color = STATUS_COLORS.get(status, "#888")
    shots = beat.get("shot_ids") or []
    shot_html = ", ".join(f"<code>{html.escape(s)}</code>" for s in shots) if shots else "—"
    title = beat.get("title") or beat.get("deck_label") or ""
    body = beat.get("body") or ""
    notes = beat.get("notes") or ""
    deck_ask = beat.get("deck_ask") or ""
    episode_note = beat.get("episode_note") or ""
    prompt_ref = beat.get("prompt_ref")
    prompt_text = resolve_prompt(prompt_ref, prompts) if prompt_ref else ""

    ref_block = ""
    if prompt_ref:
        ref_block = f'<p class="ref">Prompt: <code>{html.escape(prompt_ref)}</code></p>'
    if prompt_text:
        ref_block += f'<details><summary>Prompt text</summary><pre>{html.escape(prompt_text)}</pre></details>'
    if episode_note:
        ref_block += f'<p class="note">⚠ {html.escape(episode_note)}</p>'

    img = f's01e02-marcianople/canon/google-slides/slides/slide-{slide:02d}.png'
    return f"""
    <article class="card" data-status="{html.escape(status)}">
      <header>
        <strong>Slide {slide:02d}</strong>
        <span class="badge" style="background:{color}">{html.escape(status or '—')}</span>
        <span class="shots">{shot_html}</span>
      </header>
      <figure><img src="/{img}" alt="slide {slide}" loading="lazy" /></figure>
      <h2>{html.escape(title)}</h2>
      {f'<pre class="body">{html.escape(body)}</pre>' if body else ''}
      {f'<details><summary>Speaker notes</summary><pre>{html.escape(notes)}</pre></details>' if notes else ''}
      <p class="ask">{html.escape(deck_ask)}</p>
      {ref_block}
    </article>"""


def render() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    prompts = load_prompts()
    beats = plan.get("beats", [])
    summary = plan.get("summary", {})

    cards = "\n".join(render_card(b, prompts) for b in beats)
    policy = plan.get("policy", {})
    deck_notes = plan.get("deck_vs_episode", [])

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Deck shot plan — S01E02</title>
  <style>
    body {{ font-family: system-ui, sans-serif; background: #111; color: #e8e4dc; margin: 0; padding: 1rem; }}
    h1 {{ font-size: 1.25rem; }}
    .meta {{ color: #888; font-size: 0.9rem; max-width: 60rem; }}
    .policy {{ background: #1a1a1a; border: 1px solid #333; border-radius: 8px; padding: 1rem; margin: 1rem 0; max-width: 60rem; }}
    .policy ul {{ margin: 0.5rem 0 0 1.2rem; }}
    .toolbar {{ margin: 1rem 0; display: flex; flex-wrap: wrap; gap: 0.5rem; }}
    .toolbar button {{ padding: 0.4rem 0.8rem; background: #2a2a2a; color: inherit; border: 1px solid #444; border-radius: 4px; cursor: pointer; }}
    .toolbar button.active {{ background: #4a2020; border-color: #844; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }}
    .card {{ background: #222; border: 1px solid #333; border-radius: 8px; padding: 0.75rem; }}
    .card.hidden {{ display: none; }}
    header {{ display: flex; flex-wrap: wrap; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem; }}
    .badge {{ font-size: 0.7rem; padding: 2px 6px; border-radius: 3px; color: #fff; }}
    .shots code {{ font-size: 0.75rem; }}
    img {{ width: 100%; border-radius: 4px; background: #000; }}
    h2 {{ font-size: 1rem; margin: 0.5rem 0; }}
    pre {{ white-space: pre-wrap; font-size: 0.8rem; color: #aaa; }}
    .ask {{ font-size: 0.85rem; color: #ccc; border-left: 3px solid #844; padding-left: 0.75rem; margin: 0.75rem 0; }}
    .note {{ font-size: 0.8rem; color: #c96; }}
    .ref {{ font-size: 0.8rem; color: #888; }}
  </style>
</head>
<body>
  <h1>S01E02 deck shot plan</h1>
  <p class="meta">Authoritative brief from Evan's Google Slides storyboard. Deck beats override <code>episode.yaml</code> gaps.</p>
  <div class="policy">
    <strong>Policy:</strong> queue MJ = <code>{html.escape(str(policy.get('queue_mj', False)))}</code>
    — {html.escape(policy.get('reason', ''))}
    <ul>
      {''.join(f'<li>{html.escape(n)}</li>' for n in deck_notes)}
    </ul>
    <p>Summary: {summary.get('actionable', '?')} actionable · {summary.get('needed', '?')} needed · {summary.get('redo', '?')} redo · {summary.get('review_dump', '?')} review dump · {summary.get('skip', '?')} skip</p>
  </div>
  <div class="toolbar" id="filters">
    <button class="active" data-filter="all">All</button>
    <button data-filter="needed">Needed</button>
    <button data-filter="redo">Redo</button>
    <button data-filter="review_dump">Review dump</button>
    <button data-filter="skip">Skip</button>
  </div>
  <div class="grid" id="grid">
    {cards}
  </div>
  <script>
    const buttons = document.querySelectorAll('#filters button');
    const cards = document.querySelectorAll('.card');
    buttons.forEach(btn => {{
      btn.addEventListener('click', () => {{
        buttons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        const f = btn.dataset.filter;
        cards.forEach(c => {{
          c.classList.toggle('hidden', f !== 'all' && c.dataset.status !== f);
        }});
      }});
    }});
  </script>
</body>
</html>"""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(beats)} beats)")


if __name__ == "__main__":
    render()
