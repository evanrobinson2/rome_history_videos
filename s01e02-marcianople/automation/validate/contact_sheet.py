#!/usr/bin/env python3
"""Generate HTML contact sheet with MJ dump variant picker + favorites export."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
OUT = EPISODE / "renders" / "reviews" / "contact-sheet.html"

sys.path.insert(0, str(EPISODE / "automation" / "render"))
from asset_resolver import resolve_asset  # noqa: E402


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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


def variant_thumb(path: str) -> str:
    if path.lower().endswith(".mp4"):
        return f'<video src="/{path}" muted playsinline preload="metadata"></video>'
    return f'<img src="/{path}" alt="" loading="lazy" />'


def render() -> None:
    shots = load_yaml_shots(EPISODE / "episode.yaml")
    mj = load_json(EPISODE / "manifests" / "mj-session-index.json")
    favorites = load_json(EPISODE / "manifests" / "shot-favorites.json")
    prompts = load_prompts()

    cards = []
    for shot in shots:
        sid = shot["id"]
        asset, source = resolve_asset(shot)
        mj_pick = mj.get("shot_picks", {}).get(sid)
        favored = favorites.get("picks", {}).get(sid)
        status = shot.get("image_status", "needed")
        prompt = prompts.get(sid, {})

        img_html = (
            f'<img src="/{asset}" alt="{sid}" loading="lazy" />'
            if asset and (ROOT / asset).exists()
            else '<div class="placeholder">No asset</div>'
        )

        variants_html = ""
        if mj_pick:
            thumbs = []
            for vpath in mj_pick.get("all_variant_paths", []):
                if not (ROOT / vpath).exists():
                    continue
                sel = favored and favored.get("path") == vpath
                thumbs.append(
                    f'<button type="button" class="variant{" selected" if sel else ""}" '
                    f'data-path="{vpath}" data-job="{mj_pick.get("job_id","")}" '
                    f'title="{Path(vpath).name}">{variant_thumb(vpath)}</button>'
                )
            if thumbs:
                variants_html = f'<div class="variants"><span class="label">Dump variants (click to favor):</span>{"".join(thumbs)}</div>'

        mode_note = shot.get("visual_mode", "")
        if mode_note == "brutalist_print":
            mode_note += " · red-black screen-print"

        cards.append(
            f"""
      <article class="card" data-shot="{sid}" data-status="{status}" data-source="{source}">
        <header><code>{sid}</code> · {shot.get('movement','')} · {status} · <em>{source}</em></header>
        <figure>{img_html}</figure>
        <p class="purpose">{shot.get('purpose','')}</p>
        <p class="mode">{mode_note}</p>
        {variants_html}
        <details>
          <summary>Prompt</summary>
          <pre>{prompt.get('prompt','—')}</pre>
        </details>
        <div class="actions">
          <button type="button" data-action="approve">Mark approved</button>
          <button type="button" data-action="reject">Reject</button>
          <textarea placeholder="Notes…" rows="2"></textarea>
        </div>
      </article>"""
        )

    fav_template = json.dumps(favorites, indent=2)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>S01E02 Marcianople — Contact Sheet</title>
  <style>
    :root {{ font-family: ui-sans-serif, system-ui, sans-serif; background: #1a1a1a; color: #e8e4dc; }}
    body {{ margin: 0; padding: 1.5rem; }}
    h1 {{ font-weight: 500; letter-spacing: 0.02em; }}
    .toolbar {{ margin: 1rem 0; display: flex; gap: 0.75rem; flex-wrap: wrap; align-items: center; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr)); gap: 1rem; }}
    .card {{ background: #242424; border: 1px solid #333; border-radius: 6px; padding: 0.75rem; }}
    .card[data-status="approved"] {{ border-color: #4a7c59; }}
    .card[data-status="legacy_tentative"] {{ border-color: #8a7344; }}
    .card[data-source="favored"] {{ box-shadow: 0 0 0 1px #4a7c59; }}
    .card[data-source="mj_sample"] {{ box-shadow: 0 0 0 1px #5a6a8a; }}
    figure {{ margin: 0.5rem 0; aspect-ratio: 16/9; background: #111; display: flex; align-items: center; justify-content: center; overflow: hidden; }}
    figure img, figure video {{ width: 100%; height: 100%; object-fit: cover; }}
    .placeholder {{ color: #666; font-size: 0.85rem; }}
    .variants {{ display: flex; gap: 0.35rem; flex-wrap: wrap; margin: 0.5rem 0; }}
    .variants .label {{ width: 100%; font-size: 0.72rem; color: #888; }}
    .variant {{ padding: 0; border: 2px solid #444; background: #111; width: 72px; height: 40px; overflow: hidden; cursor: pointer; border-radius: 3px; }}
    .variant.selected {{ border-color: #c44; box-shadow: 0 0 6px #c446; }}
    .variant img, .variant video {{ width: 100%; height: 100%; object-fit: cover; pointer-events: none; }}
    pre {{ white-space: pre-wrap; font-size: 0.72rem; max-height: 8rem; overflow: auto; background: #111; padding: 0.5rem; }}
    textarea {{ width: 100%; margin-top: 0.5rem; background: #111; color: inherit; border: 1px solid #444; }}
    button {{ background: #333; color: inherit; border: 1px solid #555; padding: 0.25rem 0.5rem; cursor: pointer; }}
    .actions {{ margin-top: 0.5rem; }}
    .actions button {{ margin-right: 0.5rem; }}
    .purpose {{ font-size: 0.9rem; margin: 0.25rem 0; }}
    .mode {{ font-size: 0.75rem; color: #999; margin: 0; }}
    header em {{ color: #7a9; font-style: normal; font-size: 0.8rem; }}
  </style>
</head>
<body>
  <h1>S01E02 · Fritigern's Gambit — Shot Contact Sheet</h1>
  <p>Preview uses <strong>dump samples</strong> until you favor a variant. Heist banquet shots = red-black screen-print from inbox only.</p>
  <div class="toolbar">
    <button type="button" id="export-favorites">Export shot-favorites.json</button>
    <label>Import favorites <input type="file" id="import-favorites" accept="application/json" /></label>
    <span id="fav-count">0 favored</span>
  </div>
  <div class="grid">{''.join(cards)}</div>
  <script>
    const SESSION_DIR = {json.dumps(favorites.get('session_dir', ''))};
    let favorites = {json.dumps(favorites.get('picks', {}))};

    function updateCount() {{
      document.getElementById('fav-count').textContent = Object.keys(favorites).length + ' favored';
    }}

    document.querySelectorAll('.variant').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const card = btn.closest('.card');
        const shot = card.dataset.shot;
        favorites[shot] = {{
          path: btn.dataset.path,
          job_id: btn.dataset.job,
          grid_index: parseInt(btn.dataset.path.match(/_(\\d+)\\.(png|mp4)$/)?.[1] || '0', 10),
          favored_at: new Date().toISOString(),
          notes: card.querySelector('textarea')?.value || ''
        }};
        card.querySelectorAll('.variant').forEach(v => v.classList.remove('selected'));
        btn.classList.add('selected');
        card.dataset.source = 'favored';
        card.dataset.status = 'review_needed';
        updateCount();
      }});
    }});

    document.getElementById('export-favorites').addEventListener('click', () => {{
      const payload = {{
        schemaVersion: '1.0.0',
        session_dir: SESSION_DIR,
        updated_at: new Date().toISOString(),
        picks: favorites
      }};
      const blob = new Blob([JSON.stringify(payload, null, 2) + '\\n'], {{type: 'application/json'}});
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'shot-favorites.json';
      a.click();
    }});

    document.getElementById('import-favorites').addEventListener('change', e => {{
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = () => {{
        try {{
          const data = JSON.parse(reader.result);
          favorites = data.picks || {{}};
          location.reload();
        }} catch (err) {{ alert('Invalid JSON'); }}
      }};
      reader.readAsText(file);
    }});

    document.querySelectorAll('.card').forEach(card => {{
      card.querySelectorAll('.actions button').forEach(btn => {{
        btn.addEventListener('click', () => {{
          const action = btn.dataset.action;
          const notes = card.querySelector('textarea').value;
          console.log(JSON.stringify({{ shot: card.dataset.shot, action, notes, ts: new Date().toISOString() }}));
          if (action === 'approve') card.dataset.status = 'approved';
          if (action === 'reject') card.dataset.status = 'rejected';
        }});
      }});
    }});

    updateCount();
  </script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(shots)} shots)")


if __name__ == "__main__":
    render()
