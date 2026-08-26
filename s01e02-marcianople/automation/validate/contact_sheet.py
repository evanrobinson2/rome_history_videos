#!/usr/bin/env python3
"""Generate static HTML contact sheet for S01E02 shot review."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
OUT = EPISODE / "renders" / "reviews" / "contact-sheet.html"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml_shots(path: Path) -> list[dict]:
    shots: list[dict] = []
    current: dict | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("- id:"):
            if current:
                shots.append(current)
            current = {"id": line.split(":", 1)[1].strip()}
        elif current is not None and line.strip().startswith("purpose:"):
            current["purpose"] = line.split(":", 1)[1].strip()
        elif current is not None and line.strip().startswith("movement:"):
            current["movement"] = line.split(":", 1)[1].strip()
        elif current is not None and line.strip().startswith("visual_mode:"):
            current["visual_mode"] = line.split(":", 1)[1].strip().strip("'\"")
        elif current is not None and line.strip().startswith("image_status:"):
            current["image_status"] = line.split(":", 1)[1].strip()
        elif current is not None and line.strip().startswith("approved_asset:"):
            val = line.split(":", 1)[1].strip()
            current["approved_asset"] = None if val == "null" else val
    if current:
        shots.append(current)
    return shots


def load_prompts() -> dict[str, dict]:
    prompts: dict[str, dict] = {}
    prompt_dir = EPISODE / "prompts" / "images"
    for jsonl in sorted(prompt_dir.glob("*.jsonl")):
        for line in jsonl.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            prompts[row["shot_id"]] = row
    return prompts


def asset_for_shot(shot_id: str, legacy: dict, shots_manifest: dict) -> str | None:
    for m in legacy.get("mappings", []):
        if m["shot_id"] == shot_id:
            return m["path"]
    for s in shots_manifest.get("shots", []):
        if s["id"] == shot_id and s.get("approved_asset"):
            return s["approved_asset"]
    return None


def render() -> None:
    shots = load_yaml_shots(EPISODE / "episode.yaml")
    legacy = load_json(EPISODE / "manifests" / "legacy-map.json")
    shots_manifest = load_json(EPISODE / "manifests" / "shots.json")
    prompts = load_prompts()

    cards = []
    for shot in shots:
        sid = shot["id"]
        asset = asset_for_shot(sid, legacy, shots_manifest)
        legacy_entry = next((m for m in legacy["mappings"] if m["shot_id"] == sid), None)
        status = legacy_entry["status"] if legacy_entry else shot.get("image_status", "needed")
        prompt = prompts.get(sid, {})
        img_html = (
            f'<img src="/{asset}" alt="{sid}" loading="lazy" />'
            if asset and (ROOT / asset).exists()
            else '<div class="placeholder">No asset</div>'
        )
        cards.append(
            f"""
      <article class="card" data-shot="{sid}" data-status="{status}">
        <header><code>{sid}</code> · {shot.get('movement','')} · {status}</header>
        <figure>{img_html}</figure>
        <p class="purpose">{shot.get('purpose','')}</p>
        <p class="mode">{shot.get('visual_mode','')}</p>
        <details>
          <summary>Prompt</summary>
          <pre>{prompt.get('prompt','—')}</pre>
        </details>
        <div class="actions">
          <button type="button" data-action="approve">Approve</button>
          <button type="button" data-action="reject">Reject</button>
          <textarea placeholder="Notes…" rows="2"></textarea>
        </div>
      </article>"""
        )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>S01E02 Marcianople — Contact Sheet</title>
  <style>
    :root {{ font-family: ui-sans-serif, system-ui, sans-serif; background: #1a1a1a; color: #e8e4dc; }}
    body {{ margin: 0; padding: 1.5rem; }}
    h1 {{ font-weight: 500; letter-spacing: 0.02em; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }}
    .card {{ background: #242424; border: 1px solid #333; border-radius: 6px; padding: 0.75rem; }}
    .card[data-status="approved"] {{ border-color: #4a7c59; }}
    .card[data-status="legacy_tentative"] {{ border-color: #8a7344; }}
    figure {{ margin: 0.5rem 0; aspect-ratio: 16/9; background: #111; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    img {{ width: 100%; height: 100%; object-fit: cover; }}
    .placeholder {{ color: #666; font-size: 0.85rem; }}
    pre {{ white-space: pre-wrap; font-size: 0.72rem; max-height: 8rem; overflow: auto; background: #111; padding: 0.5rem; }}
    textarea {{ width: 100%; margin-top: 0.5rem; background: #111; color: inherit; border: 1px solid #444; }}
    button {{ margin-right: 0.5rem; background: #333; color: inherit; border: 1px solid #555; padding: 0.25rem 0.5rem; cursor: pointer; }}
    .actions {{ margin-top: 0.5rem; }}
    .purpose {{ font-size: 0.9rem; margin: 0.25rem 0; }}
    .mode {{ font-size: 0.75rem; color: #999; margin: 0; }}
  </style>
</head>
<body>
  <h1>S01E02 · Fritigern's Gambit — Shot Contact Sheet</h1>
  <p>Review UI writes notes locally only. Update <code>manifests/legacy-map.json</code> and <code>episode.yaml</code> after decisions.</p>
  <div class="grid">{''.join(cards)}</div>
  <script>
    document.querySelectorAll('.card').forEach(card => {{
      card.querySelectorAll('button').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const action = btn.dataset.action;
          const notes = card.querySelector('textarea').value;
          console.log(JSON.stringify({{ shot: card.dataset.shot, action, notes, ts: new Date().toISOString() }}));
          if (action === 'approve') card.dataset.status = 'approved';
          if (action === 'reject') card.dataset.status = 'rejected';
        }});
      }});
    }});
  </script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(shots)} shots)")


if __name__ == "__main__":
    render()
