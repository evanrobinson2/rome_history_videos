# Agent coordination

**Start here** on every new cloud/local agent session. Repo + committed artifacts are
truth; this file is the **live coordination layer** — who is doing what, what's
blocked, what the next agent should do first.

Update this file when you **start** meaningful work and when you **finish** or
hand off. Keep it short. Put long narrative in `session_N.md` when a session ends.

---

## Read order (new agent)

1. **This file** (`sessions/AGENT.md`) — current state + locks
2. `bible/00-scope-and-decisions.md` + `bible/01-creative-principles.md`
3. `assets/production/SHOT-LIST-50.md` — 50-frame batch
4. `assets/production/CATALOG-SCHEMA.md` — versioned metadata
5. `viewer/README.md` — preview app + Blob workflow
6. `docs/CLOUD-SETUP.md` — `OPENAI_API_KEY` (Runtime Secret; new session only)

---

## Current state (2026-08-24)

| Area | Status |
| --- | --- |
| **50-shot batch** | Generated v2; 26 versioned (v1 in `assets/rejected/v1/`) |
| **Turnarounds** | FRI, ALA, LUP + BANQUET-PAIR in catalog |
| **Catalog** | 54 items, schema 2.0 — `viewer/public/data/manifest.json` |
| **Viewer** | Mobile review app in `viewer/`; deployed on Vercel |
| **Blob** | Scripts ready (`blob:seed`, `blob:add`); user may not have seeded yet |
| **Song arc** | Planned in `assets/production/STANZA-01-NORTH.md`, `SONG-ARC-STANZAS-02-07.md` |
| **Image pipeline** | **OpenAI `gpt-image-2`** via `scripts/generate_image.py` — **not** Cursor GenerateImage |
| **Branch** | `cursor/story-batch-images-4c2f` — PR #2 |

### Not done yet

- Stanza 1 images (`STZ01-*`) — planned, not generated
- `ALR-001` character sheet + turnaround (stanzas 6–7)
- Human review pass on 3 flagged frames (see `REVIEW-v1.md`)
- Blob seed + `NEXT_PUBLIC_CATALOG_URL` on Vercel (if not done)
- Lyrics finalization + Suno instrumental

---

## Active work

| Agent / branch | Task | Started | Notes |
| --- | --- | --- | --- |
| — | — | — | *No active claim. Next agent: claim a row when you start.* |

**Claim protocol:** Add a row with date (UTC), branch, and task. Remove or move to
"Recent completions" when done. Do not work on a claimed task without coordinating.

---

## Locks (do not change without explicit user ask)

- `bible/00-scope-and-decisions.md`, `bible/01-creative-principles.md`
- Four-colour palette; gold = light/heat only; no segmentata; Principle 5 dignity
- Romans as antagonists through **actions**, not uglier rendering
- `SCENE-10-BETRAYAL-03-R3.png` — intentional R3 charcoal register

---

## Environment checklist

```bash
# New cloud agent — verify before batch image gen:
python3 -c "import os; print('OPENAI_API_KEY:', 'set' if os.getenv('OPENAI_API_KEY') else 'MISSING — start new agent or export manually')"
```

- **Runtime Secret** does not hot-reload mid-session → **new agent** after adding key
- **Vercel env** (`NEXT_PUBLIC_CATALOG_URL`, `BLOB_READ_WRITE_TOKEN`) ≠ agent OpenAI key

---

## Recent completions

| Date (UTC) | What |
| --- | --- |
| 2026-08-24 | Viewer: mobile UX, Blob catalog, facet filters, rich metadata v2 |
| 2026-08-24 | Vercel deploy fix (root Next entry) |
| 2026-08-23 | 50-shot v2 regen; artistic review; song arc plans |

---

## Recent decisions (binding until user changes)

- Viewer is a **preview surface**, not the product — keep UI minimal
- Images: add via **Blob + catalog** when possible (no redeploy per frame)
- Cavalry charge at Adrianople included despite Principle 6 (user request)
- Alavivus at Marcianople; Alaric seeds later (~6 in 376)

---

## Open questions (user has not locked)

1. Speaker: collective "we" vs single elder?
2. Fritigern named in stanza 1 or communal voice?
3. Alaric: child in stanza 3 → king in stanza 6?
4. Sack violence level: smoke/flight only vs fallen defenders?
5. v3 regen for flagged Valens / pair frames?

---

## Handoff template (paste when ending a session)

```markdown
### Agent handoff — YYYY-MM-DD

**Did:** …
**Branch / PR:** …
**Artifacts:** paths or commit SHA
**Blocked on:** …
**Next agent should:** …
**Updated AGENT.md:** yes/no
```

Archive long notes in `sessions/session_N.md`; link from `sessions/README.md`.

---

## What NOT to put here

- API keys, tokens, passwords
- Full prompts or image binaries (use `assets/` + catalog)
- Duplicate of bible/style rules (link instead)
