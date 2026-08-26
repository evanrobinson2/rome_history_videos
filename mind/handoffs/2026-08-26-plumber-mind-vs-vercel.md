# Handoff — separate mind sync from Vercel deployment

Timestamp: 2026-08-26 10:17 UTC  
From: **cloud-visuals**  
To: **plumber** (localhost / Cursor — live pipe diagnostics and repair)  
Status: Evan directed. Band-aids exist. Real decoupling is still open.

---

## What Evan said

> we need to separate mind sync from vercel deployment then.  
> write that for plumber

This is your job. Do not leave the coupling as “ignoreCommand and hope.”

---

## The pipe that is wrong

```
.node writes mind/
  → .cursor/hooks/mind-sync.py
  → git commit -m "mind: sync"
  → git push origin HEAD   # usually main
  → Vercel Git integration creates a Production deployment
  → ignoreCommand may skip the *build*, but the push still rings the doorbell
```

App deploys and hive memory currently share one git remote and one production
project (`evan-8467/rome-history-videos`). Thinking spends the same free-tier
deployment budget as shipping frames.

Measured (API, team `evan-8467`, project `rome-history-videos`):

| Window | Fact |
| --- | --- |
| 2026-08-26 01:00–02:00 UTC | **38** deployments in one hour, mostly `mind: sync` |
| Rolling 24h max in retained history | **53** for this project alone |
| ~02:46 UTC | CLI `vercel --prod` failed with `api-deployments-free-per-day` |
| Stray project `workspace` | Was git-connected to the same repo and **doubled** every push; **deleted** 2026-08-26 |

Do not restate “we did exactly 100.” Vercel returned the cap error; our countable
history for this project tops out lower. The burst is still outrageous. Details in
`mind/LEARNED.md` (deploy-cap correction entry).

---

## What already exists (band-aids — not the separation)

1. **`vercel.json` → `ignoreCommand`:** `scripts/vercel-ignore-build.sh`  
   Skips the build when *only* `mind/` or `sessions/` changed vs `HEAD^`.  
   **Gap:** Vercel cancels in-flight builds when a newer commit arrives. A
   `mind: sync` tip after an app commit can cancel the app deploy and then skip
   itself → production stays stale. That is how Video 1 missed the live alias.

2. **PR #5** (`cursor/fix-vercel-ignore-previous-sha-345c`) — still open.  
   Diffs against `VERCEL_GIT_PREVIOUS_SHA` so a mind-only tip still builds if app
   files changed since the last deployment. Merge or reimplement; it does **not**
   stop mind pushes from creating deployment objects.

3. **`workspace` project removed** — stops double doorbells. Good. Incomplete.

---

## What “separated” should mean

Acceptance criteria Evan can feel:

1. A pure `mind: sync` push does **not** create a Vercel production (or preview)
   deployment for `rome-history-videos`.
2. An app-relevant push to the deploy branch still produces a production deploy.
3. Rapid mind sync cannot cancel or skip an in-flight app deploy.
4. No second Vercel project gets auto-linked to this repo by accident.

How you get there is your call. Candidates (evaluate, pick one, ship):

| Approach | Notes |
| --- | --- |
| **A. Mind branch / second remote** | `mind-sync.py` pushes `mind/` to a branch or repo that has **no** Vercel Git link. App stays on `main`. |
| **B. Disable Git deploys; explicit promote** | Turn off Vercel auto-deploy on `main`; deploy only via CLI / Deploy Hook when app paths change (hook from CI that ignores mind). |
| **C. Monorepo ignore is not enough** | Keep ignoreCommand as defense in depth only. Do not treat it as the separation. |
| **D. `[skip ci]` / commit message gates** | Only if you verify Vercel does not create a billed deployment object for those pushes. Measure before trusting. |

Prefer a fix in **`.cursor/hooks/mind-sync.py` + Vercel project Git settings** over more bash in `ignoreCommand`.

---

## Files to touch / read first

- `.cursor/hooks/mind-sync.py` — the pusher (`commit -m "mind: sync"`, `push origin HEAD`)
- `.cursor/hooks/mind_lib.py` — debounce / background kick
- `vercel.json`, `scripts/vercel-ignore-build.sh`
- Vercel dashboard: project `rome-history-videos` → Git → Production Branch / Ignored Build Step
- `mind/LEARNED.md` — deploy budget + cancel-race + cap correction entries

---

## Verify when done

1. Make a mind-only commit and push the way sync does. Confirm **no new deployment**
   appears under `npx vercel ls rome-history-videos` (or API `/v6/deployments`).
2. Touch an app file (`app/`, `components/`, `public/data/manifest.json`, etc.), push,
   confirm a production deploy runs and aliases update.
3. Sequence: app commit, then immediate mind sync — app deploy must still land Ready
   on the production alias.
4. Mail the hive (`kind: fact`) with what you chose and the before/after deploy counts.

---

## Out of scope for this handoff

- Regenerating Video 1 frames (cloud-visuals; creative pipeline).
- Music row (cloud-music).
- Upgrading the Vercel plan unless Evan asks.
