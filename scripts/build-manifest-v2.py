#!/usr/bin/env python3
"""
Build updated manifest.json from all generated chapter images.
Merges character turnarounds + chapter headers + scene images.
"""

import json
from datetime import datetime
from pathlib import Path

ROOT = Path("/workspace")
OUTPUT = ROOT / "viewer/public/data/manifest.json"

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

def build_item(img_path: Path, meta_path: Path, shot_num: int) -> dict:
    """Build a manifest item from image and its metadata JSON."""
    meta = {}
    if meta_path.exists():
        meta = json.loads(meta_path.read_text())
    
    rel_path = f"/assets/chapters/{img_path.parent.name}/{img_path.name}"
    chapter_key = img_path.parent.name
    chapter_info = CHAPTERS.get(chapter_key, {"title": chapter_key, "era": ""})
    
    return {
        "shotNumber": shot_num,
        "id": img_path.stem,
        "filename": img_path.name,
        "section": chapter_key.upper(),
        "sectionTitle": chapter_info["title"],
        "mood": {"number": 0, "name": "scene"},
        "register": "R1",
        "description": meta.get("scene", ""),
        "category": "scene",
        "storyPart": chapter_info["title"],
        "storyBeat": meta.get("scene", ""),
        "tags": ["scene", chapter_key, meta.get("lighting", ""), meta.get("camera", "")],
        "url": rel_path,
        "imagePath": rel_path,
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "path": rel_path[1:]}],
        "physical": {
            "format": "png",
            "width": 3840,
            "height": 2160,
            "aspectRatio": "16:9",
            "fileSizeBytes": img_path.stat().st_size,
            "medium": "layered cut-paper (R1)",
            "palette": "deep indigo · bone · iron grey · tarnished gold",
            "orientation": "landscape",
        },
        "context": {
            "era": "Late Antiquity",
            "yearApprox": chapter_info["era"],
            "lighting": meta.get("lighting", ""),
            "camera": meta.get("camera", ""),
            "materialCulture": "Late 4th century CE",
        },
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }


def build_turnaround_item(img_path: Path, shot_num: int) -> dict:
    """Build a manifest item for character turnaround."""
    char_id = img_path.stem.replace("-turnaround", "")
    names = {"FRI-001": "Fritigern", "ALA-001": "Alavivus", "LUP-001": "Lupicinus"}
    name = names.get(char_id, char_id)
    
    rel_path = f"/assets/characters/{img_path.name}"
    
    return {
        "shotNumber": shot_num,
        "id": img_path.stem,
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
        "url": rel_path,
        "imagePath": rel_path,
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "path": rel_path[1:]}],
        "physical": {
            "format": "png",
            "width": 3840,
            "height": 2160,
            "fileSizeBytes": img_path.stat().st_size,
            "medium": "layered cut-paper (R1)",
        },
        "context": {"era": "Late Antiquity", "yearApprox": "376 CE"},
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }


def build_header_item(img_path: Path, shot_num: int) -> dict:
    """Build a manifest item for chapter header."""
    chapter_key = img_path.stem.lower().replace("ch0", "ch").split("-")[0]
    chapter_info = CHAPTERS.get(chapter_key, {"title": img_path.stem, "era": ""})
    
    rel_path = f"/assets/chapters/{img_path.name}"
    
    return {
        "shotNumber": shot_num,
        "id": img_path.stem,
        "filename": img_path.name,
        "section": "H",
        "sectionTitle": "Chapter Headers",
        "mood": {"number": 0, "name": "header"},
        "register": "R1",
        "description": f"Chapter header: {chapter_info['title']}",
        "category": "header",
        "storyPart": chapter_info["title"],
        "storyBeat": f"Chapter header for {chapter_info['title']}",
        "tags": ["header", chapter_key],
        "url": rel_path,
        "imagePath": rel_path,
        "version": "v1",
        "versions": [{"label": "v1", "status": "current", "path": rel_path[1:]}],
        "physical": {
            "format": "png",
            "width": 3840,
            "height": 2160,
            "fileSizeBytes": img_path.stat().st_size,
            "medium": "layered cut-paper (R1)",
        },
        "context": {"era": "Late Antiquity", "yearApprox": chapter_info["era"]},
        "review": {"status": "unreviewed"},
        "generator": "openai",
        "exists": True,
    }


def main():
    items = []
    shot_num = 1
    
    # Turnarounds
    for img in sorted((ROOT / "assets/characters").glob("*-turnaround.png")):
        items.append(build_turnaround_item(img, shot_num))
        shot_num += 1
    
    # Chapter headers
    for img in sorted((ROOT / "assets/chapters").glob("CH*.png")):
        if img.parent.name == "chapters":  # Only top-level headers
            items.append(build_header_item(img, shot_num))
            shot_num += 1
    
    # Scene images (ch01-ch09 subdirectories)
    for ch_dir in sorted((ROOT / "assets/chapters").glob("ch0*")):
        for img in sorted(ch_dir.glob("CH*.png")):
            meta_path = img.with_suffix(".json")
            items.append(build_item(img, meta_path, shot_num))
            shot_num += 1
    
    manifest = {
        "schemaVersion": "2.0.0",
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "title": "Gothic Invasion — Frame Review",
        "styleSuffix": STYLE_SUFFIX,
        "totalShots": len(items),
        "source": "local",
        "items": items,
    }
    
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(manifest, indent=2))
    
    print(f"Manifest written: {OUTPUT}")
    print(f"Total items: {len(items)}")
    print(f"  - Turnarounds: {sum(1 for i in items if i['category'] == 'turnaround')}")
    print(f"  - Headers: {sum(1 for i in items if i['category'] == 'header')}")
    print(f"  - Scenes: {sum(1 for i in items if i['category'] == 'scene')}")


if __name__ == "__main__":
    main()
