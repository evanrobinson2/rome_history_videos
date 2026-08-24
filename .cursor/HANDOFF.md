# Agent Handoff: Cloudflare R2 Setup

## Context
Migrating 102 OpenAI-generated images (~1.4GB as 4K PNGs) from suspended Vercel Blob to Cloudflare R2.

## What's Done
- ✅ 102 images generated with OpenAI gpt-image-2 in `/workspace/assets/`
- ✅ Cloudflare skills installed: `~/.agents/skills/`
- ✅ MCP config written: `/workspace/.cursor/mcp.json`
- ✅ Local manifest ready: `/workspace/viewer/public/data/manifest.json`

## What's Needed
1. **Cloudflare API Token** — user needs to create at https://dash.cloudflare.com/profile/api-tokens
   - Permissions needed: R2 read/write
   - Add as `CLOUDFLARE_API_TOKEN` in Cloud Agent secrets

2. **Once token available:**
   ```bash
   export CLOUDFLARE_API_TOKEN="..."
   export CLOUDFLARE_ACCOUNT_ID="..."  # from dashboard
   npx wrangler r2 bucket create rome-frames
   ```

3. **Upload images** (compress first):
   ```bash
   # Convert to WebP, upload to R2
   for f in assets/chapters/*/*.png assets/characters/*.png; do
     # convert and upload
   done
   ```

4. **Update manifest** to point to R2 URLs:
   `https://<bucket>.r2.cloudflarestorage.com/...`

5. **Redeploy** rome-history-videos.vercel.app with new manifest

## Image Stats
- 102 images total (3 turnarounds, 9 headers, 90 scenes)
- Currently 4K PNG (~14MB each)
- Should compress to WebP 1080p (~300KB each, ~30MB total)

## Production Site
- URL: https://rome-history-videos.vercel.app
- Currently showing: 50 old Cursor images (stale)
- Target: 102 new OpenAI images from R2

## Files to Know
- `/workspace/assets/chapters/` — scene images by chapter
- `/workspace/assets/characters/` — turnarounds
- `/workspace/scripts/build-local-manifest.py` — generates manifest
- `/workspace/viewer/` — Next.js viewer app
