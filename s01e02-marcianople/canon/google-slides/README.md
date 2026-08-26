# Google Slides storyboard (S01E02)

Evan's narrative storyboard deck, ingested for shot planning and MJ reference.

**Source:** https://docs.google.com/presentation/d/1480U-gIaQ1XGXPlE_FMH6Vxk3kmRPPvLVocrdzvE98M/edit

## Refresh

```bash
python3 s01e02-marcianople/automation/ingest/ingest_google_slides.py
```

Downloads PPTX/PDF (cached in `_download/`), exports:
- `slides/slide-NN.png` — rendered slide images (1440×810)
- `manifest.json` — title, body, speaker notes, suggested shot ID per slide
- `outline.txt` — plain-text export
- `renders/reviews/google-slides.html` — review UI

## Layout

```
canon/google-slides/
  README.md
  manifest.json
  outline.txt
  slides/slide-01.png … slide-44.png
  _download/          # raw pptx/pdf (gitignored)
```

`_download/` is not committed (large binaries). Slide PNGs + manifest are committed.

## Shot mapping

`manifest.json` includes heuristic `suggested_shot_id` from slide copy (e.g. screenprint slides → H04–H06). Evan overrides via shortlist/favorites workflow.
