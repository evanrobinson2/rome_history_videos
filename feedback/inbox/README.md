# Inbox log

Where each file came from. A Mac path here is provenance only — cloud agents
cannot open it. Use the file in this folder.

**`audio1834333043.m4a`** — Evan's Zoom review (48:31). **Gitignored** (local only).
Transcript also local: `feedback/inbox/transcript/audio1834333043.{json,txt,srt}`.
Creative direction extracted to `feedback/2026-08-25-direction-notes.md`.
Cloud agents cannot hear files. Do not `Read` the `.m4a` as text.

| File | Landed | Original path | How |
| --- | --- | --- | --- |
| audio1834333043.m4a | 2026-08-25 | `/Users/evanrobinson/Documents/Zoom/2026-08-25 19.19.55 Evan Robinson's Zoom Meeting/audio1834333043.m4a` | user uploaded via localhost |
| audio1834333043.m4a | 2026-08-25 | `/Users/evanrobinson/.Trash/2026-08-25 19.19.55 Evan Robinson's Zoom Meeting/audio1834333043.m4a` | user uploaded via localhost (same file, already in inbox) |
| 2026-08-25-frozen-plain-thrace.mp3 | 2026-08-25 | `/Users/evanrobinson/Downloads/Frozen Plain Thrace.mp3` | user uploaded via localhost |
| 2026-08-24-dust-on-the-steppe.mp3 | 2026-08-25 | `/Users/evanrobinson/Downloads/Dust on the Steppe.mp3` | user uploaded via localhost |
| 2026-08-25-zoom-recording.conf | 2026-08-25 | `/Users/evanrobinson/.Trash/2026-08-25 19.19.55 Evan Robinson's Zoom Meeting/recording.conf` | user uploaded via localhost |
| 2026-08-26-bread-for-the-child.jpg | 2026-08-26 | chat attachment (Luna window) | user uploaded via localhost — mother offers bread to the child, wagon, paper-cut |
| 2026-08-26-midjourney-session/ | 2026-08-26 | `/Users/evanrobinson/Downloads/midjourney_session.zip` (596 MB) | unzipped — GitHub blocks the zip as one file; 277 PNGs/MP4s, none over 10 MB |
| 2026-08-26-archive-music/ | 2026-08-26 | `/Users/evanrobinson/Downloads/Archive.zip` (338 MB) | unzipped — 98 MP3s, none over 7 MB |

After music lands, run:

```bash
python3 s01e02-marcianople/automation/ingest/index_music_archive.py
```

Maps filenames → episode cues and copies canonical picks into `s01e02-marcianople/assets/music/`.

### MJ agent-bus runs

Browser agent commits 4-up grids to `feedback/inbox/mj-runs/`. Luna re-indexes with:

```bash
python3 s01e02-marcianople/automation/ingest/index_mj_session.py
```

See `s01e02-marcianople/agent-bus/README.md`.
