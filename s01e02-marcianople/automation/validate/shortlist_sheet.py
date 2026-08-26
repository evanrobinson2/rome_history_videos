#!/usr/bin/env python3
"""Generate mobile-first shortlist UI — one 4-up MJ grid at a time."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EPISODE = ROOT / "s01e02-marcianople"
OUT = EPISODE / "renders" / "reviews" / "shortlist.html"
MJ = EPISODE / "manifests" / "mj-session-index.json"
SHORTLIST = EPISODE / "manifests" / "shot-shortlist.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def build_queue(mj: dict, shortlist: dict) -> list[dict]:
    reviewed = set(shortlist.get("jobs", {}).keys())
    items: list[dict] = []
    for job_id, job in mj.get("jobs", {}).items():
        if job_id in reviewed:
            continue
        sid = job.get("suggested_shot_id")
        if not sid:
            continue
        paths = [v["path"] for v in job.get("variants", []) if v["ext"] == "png"]
        if len(paths) < 1:
            paths = [v["path"] for v in job.get("variants", [])]
        if not paths:
            continue
        items.append({
            "job_id": job_id,
            "shot_id": sid,
            "prefix": job.get("prefix", ""),
            "reason": job.get("mapping_reason", ""),
            "paths": paths[:4],
            "source": job.get("source", "mj_session"),
        })
    # Unreviewed first; agent-bus runs before bulk session
    items.sort(key=lambda x: (0 if x["source"] == "mj_runs" else 1, x["shot_id"]))
    return items


def render() -> None:
    mj = load_json(MJ)
    shortlist = load_json(SHORTLIST)
    queue = build_queue(mj, shortlist)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
  <title>S01E02 Shortlist</title>
  <style>
    :root {{ font-family: ui-sans-serif, system-ui, sans-serif; background: #121212; color: #e8e4dc; }}
    body {{ margin: 0; padding: 1rem; max-width: 480px; margin-inline: auto; }}
    h1 {{ font-size: 1.1rem; font-weight: 500; }}
    .meta {{ color: #888; font-size: 0.85rem; margin-bottom: 1rem; }}
    .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }}
    .cell {{ position: relative; aspect-ratio: 16/10; background: #1e1e1e; border: 2px solid #333; border-radius: 4px; overflow: hidden; cursor: pointer; }}
    .cell.selected {{ border-color: #c44; box-shadow: 0 0 8px #c446; }}
    .cell img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
    .cell .idx {{ position: absolute; top: 4px; left: 6px; font-size: 0.7rem; background: #000a; padding: 2px 5px; border-radius: 3px; }}
    .actions {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }}
    button {{ flex: 1; min-width: 7rem; padding: 0.65rem; background: #2a2a2a; color: inherit; border: 1px solid #444; border-radius: 6px; font-size: 0.9rem; cursor: pointer; }}
    button.primary {{ background: #4a2020; border-color: #844; }}
    button:disabled {{ opacity: 0.4; }}
    .progress {{ margin: 0.75rem 0; height: 4px; background: #333; border-radius: 2px; }}
    .progress > div {{ height: 100%; background: #c44; border-radius: 2px; transition: width 0.2s; }}
    textarea {{ width: 100%; margin-top: 0.75rem; background: #1a1a1a; color: inherit; border: 1px solid #444; border-radius: 4px; padding: 0.5rem; }}
    .toolbar {{ margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid #333; }}
  </style>
</head>
<body>
  <h1>S01E02 Shortlist</h1>
  <p class="meta">Tap cells to ⭐ · one grid at a time · export when done</p>
  <div class="progress"><div id="bar" style="width:0%"></div></div>
  <div id="card">
    <p class="meta" id="label">Loading…</p>
    <div class="grid" id="grid"></div>
    <textarea id="notes" placeholder="Notes for this grid…" rows="2"></textarea>
    <div class="actions">
      <button type="button" id="reject">Reject grid</button>
      <button type="button" id="skip">Skip</button>
      <button type="button" class="primary" id="shortlist">⭐ Shortlist</button>
    </div>
  </div>
  <div class="toolbar">
    <p class="meta"><span id="count">0</span> reviewed · <span id="starred">0</span> shortlisted grids</p>
    <button type="button" id="export">Export shot-shortlist.json</button>
    <button type="button" id="import-btn">Import JSON</button>
    <input type="file" id="import" accept="application/json" hidden />
  </div>
  <script>
    const QUEUE = {json.dumps(queue)};
    let idx = 0;
    let shortlist = {json.dumps(shortlist.get("jobs", {}))};
    let selected = new Set();

    const grid = document.getElementById('grid');
    const label = document.getElementById('label');
    const notes = document.getElementById('notes');
    const bar = document.getElementById('bar');

    function updateProgress() {{
      const pct = QUEUE.length ? Math.round((idx / QUEUE.length) * 100) : 100;
      bar.style.width = pct + '%';
      document.getElementById('count').textContent = idx;
      document.getElementById('starred').textContent = Object.values(shortlist).filter(j => j.status === 'shortlisted').length;
    }}

    function renderCard() {{
      selected.clear();
      if (idx >= QUEUE.length) {{
        label.textContent = 'Done — export shot-shortlist.json';
        grid.innerHTML = '';
        notes.value = '';
        updateProgress();
        return;
      }}
      const item = QUEUE[idx];
      label.innerHTML = `<strong>${{item.shot_id}}</strong> · ${{item.reason || item.prefix}}<br><span style="color:#666">${{idx + 1}} / ${{QUEUE.length}} · ${{item.source}}</span>`;
      grid.innerHTML = item.paths.map((p, i) =>
        `<div class="cell" data-i="${{i}}" data-path="${{p}}"><span class="idx">${{i}}</span><img src="/${{p}}" alt="" loading="lazy" /></div>`
      ).join('');
      notes.value = '';
      grid.querySelectorAll('.cell').forEach(cell => {{
        cell.addEventListener('click', () => {{
          const i = cell.dataset.i;
          if (selected.has(i)) selected.delete(i); else selected.add(i);
          cell.classList.toggle('selected', selected.has(i));
        }});
      }});
      updateProgress();
    }}

    document.getElementById('shortlist').addEventListener('click', () => {{
      if (idx >= QUEUE.length) return;
      const item = QUEUE[idx];
      const paths = [...selected].map(i => item.paths[+i]);
      shortlist[item.job_id] = {{
        shot_id: item.shot_id,
        status: paths.length ? 'shortlisted' : 'skipped',
        paths,
        rejected_paths: item.paths.filter(p => !paths.includes(p)),
        notes: notes.value,
        reviewed_at: new Date().toISOString()
      }};
      idx++;
      renderCard();
    }});

    document.getElementById('reject').addEventListener('click', () => {{
      if (idx >= QUEUE.length) return;
      const item = QUEUE[idx];
      shortlist[item.job_id] = {{
        shot_id: item.shot_id,
        status: 'rejected',
        paths: [],
        rejected_paths: item.paths,
        notes: notes.value,
        reviewed_at: new Date().toISOString()
      }};
      idx++;
      renderCard();
    }});

    document.getElementById('skip').addEventListener('click', () => {{ idx++; renderCard(); }});

    document.getElementById('export').addEventListener('click', () => {{
      const payload = {{
        schemaVersion: '1.0.0',
        updated_at: new Date().toISOString(),
        jobs: shortlist
      }};
      const a = document.createElement('a');
      a.href = URL.createObjectURL(new Blob([JSON.stringify(payload, null, 2) + '\\n'], {{type: 'application/json'}}));
      a.download = 'shot-shortlist.json';
      a.click();
    }});

    document.getElementById('import-btn').addEventListener('click', () => document.getElementById('import').click());
    document.getElementById('import').addEventListener('change', e => {{
      const f = e.target.files[0];
      if (!f) return;
      const r = new FileReader();
      r.onload = () => {{ shortlist = JSON.parse(r.result).jobs || {{}}; idx = 0; renderCard(); }};
      r.readAsText(f);
    }});

    renderCard();
  </script>
</body>
</html>
"""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(queue)} grids in queue)")


if __name__ == "__main__":
    render()
