# Luna Agent — visuals / animatic / queue

You plan shots, queue MJ work, ingest results, build animatics. You do **not** run Midjourney in cloud.

## Each session

1. `git pull`
2. Read `agent-bus/log/browser.ndjson` (tail) for new `committed` / `failed` events
3. If new images: `python3 s01e02-marcianople/automation/ingest/index_mj_session.py`
4. Regenerate review UIs:
   - `python3 s01e02-marcianople/automation/validate/shortlist_sheet.py`
   - `python3 s01e02-marcianople/automation/validate/contact_sheet.py`
5. Check `episode.yaml` gaps (`image_status: needed`) and queue if prompts exist

## Queue a generation

```bash
python3 s01e02-marcianople/automation/ingest/queue_mj_request.py --shot H06
python3 s01e02-marcianople/automation/ingest/queue_mj_request.py --shot H06 --force
```

Writes `agent-bus/queue/pending/req-{shot}-{hash}.json` and appends `log/visuals.ndjson`.

## Asset resolution (animatic)

`automation/render/asset_resolver.py`:

1. `manifests/shot-favorites.json` (Evan's winner)
2. `manifests/mj-session-index.json` (dump sample)
3. `episode.yaml` only if `image_status: approved`
4. `legacy-map.json` (not for `brutalist_print` heist shots)

```bash
python3 s01e02-marcianople/automation/render/quick_animatic.py --name S01E02_quick_pass_v3
```

## When Evan shortlists

1. Evan opens `renders/reviews/shortlist.html`, stars variants, exports `shot-shortlist.json`
2. Evan commits to `manifests/shot-shortlist.json`
3. Evan picks winners → `shot-favorites.json` → `apply_favorites.py`

## Append to visuals log

```json
{"ts":"2026-08-26T21:00:00Z","kind":"queue","request_id":"req-H06-abc","shot_id":"H06","text":"Queued uniform exchange"}
```

## Current gaps (as of scaffold)

- **H06, H07, H08** — queued in `queue/pending/` (no dump images yet)
- Crossing **C02, C03, C05, C09, C11** — need prompts + queue when ready
