# S01E02 Agent Bus

Git is the message bus between **Luna** (planning / review / animatic) and **MJ Browser** (Playwright Midjourney on laptop).

## Layout

```
agent-bus/
  README.md              ← you are here
  BROWSER-AGENT.md       ← paste into laptop Claude (runs ~every minute)
  LUNA-AGENT.md          ← Luna / cloud agent instructions
  STATUS.json            ← browser heartbeat + mutex (one job at a time)
  queue/
    pending/               ← Luna writes one JSON per MJ request
    in_progress/         ← browser claims by moving file here
    done/
    failed/
  log/
    browser.ndjson       ← browser append-only events
    visuals.ndjson       ← Luna append-only events

feedback/inbox/mj-runs/
  YYYY-MM-DD-{shot}-{slug}-{hash}/
    job.json
    H06_0.png … H06_3.png

manifests/
  shot-shortlist.json    ← triage: starred variants per job grid
  shot-favorites.json    ← one winner per shot (approved)
```

## Rules

1. **One request = one MJ submit = exactly 4 PNGs** in one commit.
2. **Mutex:** browser sets `STATUS.state` to `generating` while working; only one `in_progress` file.
3. **Heist shots** (`visual_mode: brutalist_print`) must use red-black screen-print prompts.
4. **Dedupe:** if `prompt_hash` exists in `mj-runs/` and `force` is false, skip (move request to `failed` with reason).
5. **Never commit** browser profiles, cookies, or API keys.

## Quick commands

```bash
# Luna: queue a shot from prompts/images/*.jsonl
python3 s01e02-marcianople/automation/ingest/queue_mj_request.py --shot H06

# Luna: re-index all inbox dumps + mj-runs
python3 s01e02-marcianople/automation/ingest/index_mj_session.py

# Luna: regenerate mobile shortlist UI
python3 s01e02-marcianople/automation/validate/shortlist_sheet.py

# Evan: triage → export shot-shortlist.json → commit
# Evan: pick winners → shot-favorites.json → apply_favorites.py

# Browser: see BROWSER-AGENT.md
```

## Review workflow

| Step | Who | Output |
| --- | --- | --- |
| Queue | Luna | `queue/pending/req-*.json` |
| Generate | Browser | `feedback/inbox/mj-runs/…/` + 4 PNGs |
| Index | Luna | `manifests/mj-session-index.json` |
| Shortlist | Evan | `manifests/shot-shortlist.json` |
| Approve | Evan | `manifests/shot-favorites.json` |
| Animatic | Luna | `renders/animatics/S01E02_quick_pass_v3.mp4` |
