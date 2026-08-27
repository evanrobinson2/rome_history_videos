# MJ Browser Agent — run every ~60 seconds

You have **browser control** (Playwright). Luna has **repo planning**. You coordinate only through git files.

## Startup

1. `cd` to `rome_history_videos` clone.
2. Read `s01e02-marcianople/agent-bus/README.md` and `STATUS.json`.
3. `git pull --rebase`

## Each tick (repeat every minute)

```
IF STATUS.state != "idle":
  UPDATE heartbeat_at in STATUS.json, commit+push, EXIT

IF queue/pending/ is empty:
  UPDATE heartbeat_at, EXIT

PICK oldest file in queue/pending/
MOVE it to queue/in_progress/
SET STATUS.state = "generating"
SET STATUS.current_request_id = request.id
COMMIT + PUSH (claim)

READ request JSON — fields: shot_id, prompt, output_dir, filenames[4], mj, visual_mode

IF visual_mode == "brutalist_print" AND prompt lacks "screen-print":
  LOG warning; continue anyway if prompt mentions vermilion/brutalist

OPEN Midjourney (authenticated profile — path from env MJ_BROWSER_PROFILE)
SUBMIT prompt with aspect_ratio from request.mj
WAIT for 4-up grid to finish
DOWNLOAD 4 upscaled PNGs to output_dir with EXACT filenames from request.filenames

WRITE output_dir/job.json:
  - copy of request
  - mj_job_id if visible
  - completed_at ISO timestamp
  - paths[4]

git add output_dir/
git commit -m "mj: {shot_id} {purpose slug} (4 variants) [{request.id}]"
git push

APPEND log/browser.ndjson:
  {"ts":"...","kind":"committed","request_id":"...","shot_id":"...","commit":"...","paths":[...]}

MOVE queue/in_progress/{id}.json → queue/done/
SET STATUS.state = "idle"
SET STATUS.current_request_id = null
SET STATUS.last_commit_sha = <sha>
COMMIT + PUSH
```

## On failure

```
APPEND log/browser.ndjson:
  {"ts":"...","kind":"failed","request_id":"...","error":"..."}

MOVE request to queue/failed/
SET STATUS.state = "idle"
SET STATUS.last_error = "<message>"
COMMIT + PUSH
```

Do **not** retry automatically unless Evan or Luna sets `retry: true` on the request.

## Environment

```bash
export MJ_BROWSER_PROFILE=/path/to/your/playwright/profile  # never commit
```

Human checkpoints: login, CAPTCHA, payment, credit spend — pause and update `STATUS.last_error` with `needs_human: true`.

## Filename contract

Each run directory:

```
feedback/inbox/mj-runs/2026-08-26-H06-uniform-exchange-a1b2c3/
  job.json
  H06_0.png
  H06_1.png
  H06_2.png
  H06_3.png
```

Indexer maps `{shot_id}_{n}.png` → shot automatically.
