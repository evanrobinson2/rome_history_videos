#!/usr/bin/env python3
"""Download Suno library tracks using a browser session token.

Suno has no official public export API. This script uses the same internal
feed endpoint the web app calls. You must supply a short-lived Bearer token
copied from your logged-in browser session.

Usage:
  export SUNO_TOKEN="eyJ..."   # paste token only, no "Bearer " prefix
  python3 scripts/suno_download.py --out assets/audio

Get your token (desktop browser):
  1. Log in at https://suno.com
  2. Open DevTools → Network
  3. Filter: feed
  4. Reload or open Library
  5. Click the POST to studio-api-prod.suno.com (often /api/feed/v3)
  6. Request Headers → Authorization → copy the JWT after "Bearer "

Token expires in ~1 hour. Re-copy when you get 401 errors.

This script never stores or sends your token anywhere except Suno's API.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

API_BASE = "https://studio-api-prod.suno.com"
FEED_PATH = "/api/feed/v3"


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Origin": "https://suno.com",
        "Referer": "https://suno.com/",
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
    }


def _post_json(url: str, token: str, payload: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode(),
        headers=_headers(token),
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode())


def _download_file(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": _headers("")["User-Agent"]})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())


def _safe_name(title: str, clip_id: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", title or "untitled").strip()
    cleaned = re.sub(r"\s+", "_", cleaned)[:80] or "untitled"
    return f"{cleaned}__{clip_id[:8]}"


def fetch_all_clips(token: str, delay: float) -> list[dict]:
    clips: list[dict] = []
    cursor: str | None = None
    page = 0

    while True:
        payload: dict = {"page": page}
        if cursor:
            payload = {"cursor": cursor, "limit": 20}

        data = _post_json(f"{API_BASE}{FEED_PATH}", token, payload)
        batch = data.get("clips") or data.get("items") or []
        if not batch:
            break

        clips.extend(batch)
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
        page += 1

        print(f"  fetched {len(batch)} clips (total {len(clips)})")
        if not has_more and not cursor:
            break
        time.sleep(delay)

    return clips


def main() -> int:
    parser = argparse.ArgumentParser(description="Download Suno library MP3s")
    parser.add_argument(
        "--token",
        default=os.environ.get("SUNO_TOKEN", ""),
        help="Bearer JWT (or set SUNO_TOKEN env var)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("assets/audio"),
        help="Output directory (default: assets/audio)",
    )
    parser.add_argument(
        "--metadata",
        action="store_true",
        help="Also save per-track JSON metadata alongside MP3s",
    )
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between API pages")
    args = parser.parse_args()

    token = args.token.strip()
    if token.lower().startswith("bearer "):
        token = token[7:].strip()
    if not token:
        print("Error: no token. Set SUNO_TOKEN or pass --token.", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Listing library → {args.out.resolve()}")

    try:
        clips = fetch_all_clips(token, args.delay)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        print(f"API error {e.code}: {body[:500]}", file=sys.stderr)
        if e.code == 401:
            print("\nToken expired or invalid. Copy a fresh one from DevTools.", file=sys.stderr)
        return 1

    if not clips:
        print("No clips returned. Token may be valid but library empty, or API shape changed.")
        return 0

    downloaded = 0
    skipped = 0
    for clip in clips:
        clip_id = clip.get("id") or ""
        title = clip.get("title") or "untitled"
        audio_url = clip.get("audio_url") or (
            f"https://cdn1.suno.ai/{clip_id}.mp3" if clip_id else ""
        )
        status = clip.get("status", "")

        if not audio_url or status not in ("", "complete", "streaming"):
            print(f"  skip {title!r} (status={status!r}, no url)")
            skipped += 1
            continue

        base = _safe_name(title, clip_id)
        mp3_path = args.out / f"{base}.mp3"
        if mp3_path.exists():
            print(f"  exists {mp3_path.name}")
            skipped += 1
            continue

        print(f"  download {mp3_path.name}")
        try:
            _download_file(audio_url, mp3_path)
            downloaded += 1
            if args.metadata:
                meta_path = args.out / f"{base}.json"
                meta_path.write_text(json.dumps(clip, indent=2), encoding="utf-8")
        except urllib.error.HTTPError as e:
            print(f"  failed {title!r}: HTTP {e.code}", file=sys.stderr)
        time.sleep(0.5)

    print(f"\nDone: {downloaded} downloaded, {skipped} skipped, {len(clips)} total clips.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
