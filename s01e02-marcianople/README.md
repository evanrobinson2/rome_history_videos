# S01E02 — Marcianople · *Fritigern's Gambit*

First-draft illustrated episode: Gothic crossing → Roman mistreatment → banquet heist → wagon battle → mercy → Alaric inheritance.

**Canonical spec:** [`canon/remaster-directive.md`](canon/remaster-directive.md)  
**Shot authority:** [`episode.yaml`](episode.yaml) + [`manifests/shots.json`](manifests/shots.json)  
**Character anchors:** [`canon/character-bible.md`](canon/character-bible.md)

## Status

| Phase | State |
| --- | --- |
| 1 Scaffold + ingest | **done** — structure, manifests, asset inventory, legacy map |
| 2 Prompt + review | **in progress** — C01–C13 prompts, validator, contact sheet |
| 3 Browser generation | cowork / Playwright — dry-run first |
| 4 Narration + captions | after visual contact sheet |
| 5 Animatic | FFmpeg pipeline |
| 6 Polish | — |

## Music (inbox reference)

| Cue | File (repo) |
| --- | --- |
| Battle | `assets/music/battle.mp3` ← *The Gothic Fracture (1)* |
| Denouement | `assets/music/denouement.mp3` ← *Frozen Plain Thrace (1)* |
| Crossing | `assets/music/crossing_open.mp3` ← *The First Step Across the (1)* |
| Crossing ref | `assets/music/crossing_reference.mp3` ← *Dust on the Steppe (1)* |
| Heist | `assets/music/heist_groove.mp3` ← *Wah-Step Pulse (Remastered) (1)* |
| Family / memory | `assets/music/family_memory.mp3` ← *Exile Lullaby (1)* |

Full archive: `feedback/inbox/2026-08-26-archive-music/` (98 tracks). Manifest: `manifests/music-manifest.json`.

## Approved stills (register, do not regenerate)

Per directive §22: match existing Midjourney proofs to **H01–H11**, **B03**, **B06–B10**, **B15**, **B17** when ingested from laptop/cowork.

**In repo now (commit `b05c11d`):** `feedback/inbox/2026-08-26-midjourney-session/` — 277 files (272 PNG + 5 MP4), 72 MJ jobs.

Auto-mapped **20/41 shots** → see `manifests/mj-session-index.json`. Status `review_needed` until Evan confirms variants (especially **B15 mercy** grid pick).

**Animatic sampling:** renders use `asset_resolver.py` — favorites → MJ dump sample → approved only → legacy placeholder. Heist banquet shots (`brutalist_print`) are **dump-only** (red-black screen-print stills, never legacy cut-paper).

**Favoriting workflow:**
1. Open `renders/reviews/contact-sheet.html` — click dump variants to favor
2. Export `shot-favorites.json` → save to `manifests/shot-favorites.json`
3. `python3 automation/ingest/apply_favorites.py` — writes winners to `episode.yaml` as `approved`

**Also:** `feedback/inbox/2026-08-26-bread-for-the-child.jpg` → **C12**.

## Three questions (every frame)

Whose experience is this? What changed? Why must this image exist?

## Automation (local)

```bash
# Agent bus — see s01e02-marcianople/agent-bus/README.md
python3 s01e02-marcianople/automation/ingest/queue_mj_request.py --shot H06
python3 s01e02-marcianople/automation/ingest/index_mj_session.py
python3 s01e02-marcianople/automation/validate/shortlist_sheet.py   # mobile triage UI
python3 s01e02-marcianople/automation/validate/contact_sheet.py
python3 s01e02-marcianople/automation/ingest/apply_favorites.py
python3 s01e02-marcianople/automation/render/quick_animatic.py
python3 s01e02-marcianople/automation/validate/validate_prompts.py
```

**Browser agent (laptop):** read `agent-bus/BROWSER-AGENT.md` — runs every ~60s, commits 4 PNGs per request.

**Review:** `renders/reviews/shortlist.html` (triage) → `shot-shortlist.json` → `shot-favorites.json` → animatic.
