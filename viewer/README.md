# Frame Review Viewer

A thin Next.js viewer for reviewing the 50-frame Gothic Invasion cut-paper batch.

## Features

- **Thumbnail strip** — all 50 shots, colour-coded by your keep / discard / reroll decisions
- **Main stage** — full image with ← → navigation (keyboard supported)
- **Feedback toolbar** — Keep · Discard · Reroll (K / D / R shortcuts)
- **Tabbed details** — Details · Story · Prompt · Review (agent QA notes from `REVIEW-v1.md`)
- **Export** — download your decisions as JSON
- **Reroll** — marks frame + copies generation prompt to clipboard

## Local dev

```bash
cd viewer
npm install
npm run dev
```

Open http://localhost:3000

The `predev` script builds `public/data/manifest.json` from production markdown and symlinks `../assets` into `public/assets`.

## Deploy to Vercel

### Fix for the first failed deploy

The GitHub → Vercel project was created with **Root Directory = null**, so Vercel
tried to build the monorepo root (no Next.js app) and failed.

**Do this once in the Vercel dashboard** (most reliable):

1. Open [rome-history-videos project settings](https://vercel.com/evan-8467/rome-history-videos/settings/general)
2. Under **Root Directory**, click **Edit** → set to `viewer` → Save
3. Redeploy the latest commit (Deployments → ⋯ → Redeploy)

The repo also has a root `vercel.json` that points `@vercel/next` at `viewer/package.json`
as a fallback when Root Directory is unset.

### What you need from Vercel

1. **A Vercel account** — [vercel.com/signup](https://vercel.com/signup) (Hobby is fine for private review)
2. **GitHub connection** — link your GitHub account so Vercel can read `evanrobinson2/rome_history_videos`
3. **Root Directory:** `viewer` (see above — required for clean Next.js builds)
4. **Framework Preset:** Next.js
5. **No environment variables** for the viewer itself
6. **Deploy** — build copies `assets/` into `public/assets` (`VERCEL=1` forces copy, not symlink)

### Optional (recommended for production)

| Need | Why |
|------|-----|
| **Pro plan** if repo + assets exceed Hobby limits | Hobby has deployment size limits; ~160MB of PNGs may need Pro or external asset hosting |
| **Vercel Blob** or **Cloudinary** | Serve images from CDN instead of bundling into every deploy — faster builds, smaller deployments |
| **Password protection** (Pro) or **Vercel Authentication** | Keep draft frames private during review |
| **Custom domain** | e.g. `frames.yourdomain.com` |

### Quick CLI deploy

```bash
cd viewer
npx vercel login          # browser OAuth
npx vercel link           # select team + rome-history-videos
npx vercel inspect dpl_xxx --logs   # read failed build logs
npx vercel --prod
```

### After deploy

Your feedback is stored in **browser localStorage** on that device. Use **Export** to save decisions, then share the JSON back into the repo or a PR comment.

## Rebuild manifest

When `SHOT-LIST-50.md` or `REVIEW-v1.md` changes:

```bash
npm run manifest
```

## File map

| File | Role |
|------|------|
| `scripts/build-manifest.mjs` | Parses shot list + review + batch prompts |
| `scripts/link-assets.mjs` | Symlinks `../assets` → `public/assets` |
| `public/data/manifest.json` | Generated at build time |
| `components/ViewerShell.tsx` | Main app shell |
