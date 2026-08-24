#!/usr/bin/env python3
"""Build catalog.json with Vercel Blob URLs for the viewer."""

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path("/workspace")
OUTPUT = ROOT / "viewer/public/data/catalog-blob.json"
BLOB_BASE = "https://hxhi8wuqcbh0xuqb.public.blob.vercel-storage.com/frames"

STYLE_SUFFIX = (
    "Layered cut-paper illustration, late-antique 376 CE, stacked paper planes soft drop shadows, "
    "handmade paper fibre, scissor-cut edges torn deckle for damage, light as flat translucent wedges, "
    "palette deep indigo bone iron grey tarnished gold gold only for light heat fire sun, "
    "16:9 horizontal with crop headroom, no text no watermark no invented heraldry no medieval plate "
    "no mail hauberks, named principals stylized visible cut-paper faces, crowds faceless silhouettes, "
    "same dignity Gothic and Roman, not Batman not black void silhouettes, off-center composition."
)

CHAPTERS = {
    "ch01": {"title": "1. Hunnic Pressure", "era": "c. 375 CE"},
    "ch02": {"title": "2. Flight to the Danube", "era": "376 CE"},
    "ch03": {"title": "3. The Crossing and Waiting", "era": "376 CE"},
    "ch04": {"title": "4. Exploitation, Famine", "era": "376 CE"},
    "ch05": {"title": "5. Marcianople", "era": "376 CE"},
    "ch06": {"title": "6. Open Revolt Across Thrace", "era": "376-377 CE"},
    "ch07": {"title": "7. Valens Turns", "era": "377-378 CE"},
    "ch08": {"title": "8. Adrianople", "era": "9 August 378 CE"},
    "ch09": {"title": "9. Aftermath", "era": "378 CE"},
}

def blob_url(img_id: str) -> str:
    return f"{BLOB_BASE}/{img_id}/v1.png"

def build_turnaround(img_path: Path, shot_num: int) -> dict:
    char_id = img_path.stem.replace("-turnaround", "")
    img_id = img_path.stem
    names = {"FRI-001": "Fritigern", "ALA-001": "Alavivus", "LUP-001": "Lupicinus"}
    name = names.get(char_id, char_id)
    
    return {
        "shotNumber": shot_num,
        "id": img_id,
        "filename": img_path.name,
        "section": "T",
        "sectionTitle": "Turnarounds — identity locks",
        "mood": {"number": 0, "name": "neutral"},
        "register": "R1",
        "description": f"{name} four-view turnaround",
        "category": "turnaround",
        "storyPart": "T. Turnarounds — identity locks",
        "storyBeat": f"{name} identity lock: four views, face visible",
        "tags": ["turnaround", char_id, "reference"],
        "url": blob_url(img_id),
        "imagePath": blob_url(img_id),
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "url": blob_url(img_id)}],
        "physical": {"format": "png", "width": 3840, "height": 2160},
        "context": {"era": "Late Antiquity", "yearApprox": "376 CE"},
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }

def build_header(img_path: Path, shot_num: int) -> dict:
    img_id = img_path.stem
    ch_key = img_id.lower().split("-")[0].replace("ch0", "ch")
    chapter_info = CHAPTERS.get(ch_key, {"title": img_id, "era": ""})
    
    return {
        "shotNumber": shot_num,
        "id": img_id,
        "filename": img_path.name,
        "section": "H",
        "sectionTitle": "Chapter Headers",
        "mood": {"number": 0, "name": "header"},
        "register": "R1",
        "description": f"Chapter header: {chapter_info['title']}",
        "category": "header",
        "storyPart": chapter_info["title"],
        "storyBeat": f"Chapter header for {chapter_info['title']}",
        "tags": ["header", ch_key],
        "url": blob_url(img_id),
        "imagePath": blob_url(img_id),
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "url": blob_url(img_id)}],
        "physical": {"format": "png", "width": 3840, "height": 2160},
        "context": {"era": "Late Antiquity", "yearApprox": chapter_info["era"]},
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }

def build_scene(img_path: Path, meta_path: Path, shot_num: int) -> dict:
    img_id = img_path.stem
    ch_key = img_path.parent.name
    chapter_info = CHAPTERS.get(ch_key, {"title": ch_key, "era": ""})
    
    meta = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    
    return {
        "shotNumber": shot_num,
        "id": img_id,
        "filename": img_path.name,
        "section": ch_key.upper(),
        "sectionTitle": chapter_info["title"],
        "mood": {"number": 0, "name": "scene"},
        "register": "R1",
        "description": meta.get("scene", ""),
        "category": "scene",
        "storyPart": chapter_info["title"],
        "storyBeat": meta.get("scene", ""),
        "tags": ["scene", ch_key, meta.get("lighting", ""), meta.get("camera", "")],
        "url": blob_url(img_id),
        "imagePath": blob_url(img_id),
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "url": blob_url(img_id)}],
        "physical": {"format": "png", "width": 3840, "height": 2160},
        "context": {
            "era": "Late Antiquity",
            "yearApprox": chapter_info["era"],
            "lighting": meta.get("lighting", ""),
            "camera": meta.get("camera", ""),
        },
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }

def main():
    items = []
    shot_num = 1
    
    # Turnarounds
    for img in sorted((ROOT / "assets/characters").glob("*-turnaround.png")):
        items.append(build_turnaround(img, shot_num))
        shot_num += 1
    
    # Chapter headers
    for img in sorted((ROOT / "assets/chapters").glob("CH*.png")):
        if img.parent.name == "chapters":
            items.append(build_header(img, shot_num))
            shot_num += 1
    
    # Scene images
    for ch_dir in sorted((ROOT / "assets/chapters").glob("ch0*")):
        for img in sorted(ch_dir.glob("CH*.png")):
            meta_path = img.with_suffix(".json")
            items.append(build_scene(img, meta_path, shot_num))
            shot_num += 1
    
    catalog = {
        "schemaVersion": "2.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "title": "Gothic Invasion — Frame Review",
        "styleSuffix": STYLE_SUFFIX,
        "totalShots": len(items),
        "source": "vercel-blob",
        "items": items,
    }
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(catalog, indent=2))
    
    print(f"Catalog written: {OUTPUT}")
    print(f"Total items: {len(items)}")

if __name__ == "__main__":
    main()
