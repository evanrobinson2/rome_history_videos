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

### What you need from Vercel

1. **A Vercel account** — [vercel.com/signup](https://vercel.com/signup) (Hobby is fine for private review)
2. **GitHub connection** — link your GitHub account so Vercel can read `evanrobinson2/rome_history_videos`
3. **New Project** — Import the repo, then set:
   - **Root Directory:** `viewer`
   - **Framework Preset:** Next.js (auto-detected)
   - **Build Command:** `npm run build` (default)
   - **Install Command:** `npm install` (default)
4. **No environment variables required** for the viewer itself — it is fully static
5. **Deploy** — first build will bundle ~160MB of PNGs via the asset symlink/copy step

### Optional (recommended for production)

| Need | Why |
|------|-----|
| **Pro plan** if repo + assets exceed Hobby limits | Hobby has deployment size limits; ~160MB of PNGs may need Pro or external asset hosting |
| **Vercel Blob** or **Cloudinary** | Serve images from CDN instead of bundling into every deploy — faster builds, smaller deployments |
| **Password protection** (Pro) or **Vercel Authentication** | Keep draft frames private during review |
| **Custom domain** | e.g. `frames.yourdomain.com` |

### Quick CLI deploy

```bash
npm i -g vercel
cd viewer
vercel
# follow prompts — set root to viewer if asked
vercel --prod
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
