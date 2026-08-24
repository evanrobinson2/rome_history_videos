#!/usr/bin/env python3
"""
Batch generate chapter scene images with varied lighting, camera, and scenery.
Writes metadata JSON alongside each image.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

CHAPTERS = {
    "ch01": {
        "title": "Hunnic Pressure",
        "era": "c. 375 CE",
        "location": "Gothic territories east of the Danube",
        "shots": [
            {"id": "01", "lighting": "pre-dawn grey", "camera": "extreme wide, high angle", "scene": "Gothic village from hilltop, smoke columns on eastern horizon"},
            {"id": "02", "lighting": "harsh midday", "camera": "medium wide, eye level", "scene": "Empty road with abandoned cart, dust devils"},
            {"id": "03", "lighting": "sunset backlit", "camera": "low angle silhouette", "scene": "Mounted scouts on ridge, gesturing eastward"},
            {"id": "04", "lighting": "firelight interior", "camera": "medium close, Dutch angle", "scene": "Elder's hut, faces lit by hearth, maps on table"},
            {"id": "05", "lighting": "overcast flat", "camera": "wide tracking", "scene": "Livestock being herded, children running alongside"},
            {"id": "06", "lighting": "blue hour dusk", "camera": "extreme wide panorama", "scene": "Valley with multiple villages, each with smoke rising"},
            {"id": "07", "lighting": "torchlight night", "camera": "medium, through doorframe", "scene": "Messenger arriving at hall, guards alert"},
            {"id": "08", "lighting": "storm light", "camera": "wide, low horizon", "scene": "Dark clouds approaching, wheat fields bending"},
            {"id": "09", "lighting": "dawn mist", "camera": "close detail", "scene": "Dew on shield boss, sword being lifted"},
            {"id": "10", "lighting": "golden hour side", "camera": "medium wide, profile", "scene": "Family loading wagon, long shadows"},
        ]
    },
    "ch02": {
        "title": "Flight to the Danube",
        "era": "376 CE",
        "location": "Roads and plains toward the Danube",
        "shots": [
            {"id": "01", "lighting": "grey dawn", "camera": "extreme wide aerial", "scene": "Column stretching to horizon, wagons and walkers"},
            {"id": "02", "lighting": "noon harsh", "camera": "close ground level", "scene": "Feet and wheels on dusty road, exhaustion"},
            {"id": "03", "lighting": "late afternoon", "camera": "medium wide", "scene": "River ford crossing, water splashing"},
            {"id": "04", "lighting": "campfire night", "camera": "medium, warm pool of light", "scene": "Families circled around fire, wagons as windbreak"},
            {"id": "05", "lighting": "overcast rain", "camera": "wide, rain streaks", "scene": "Column trudging through mud, cloaks soaked"},
            {"id": "06", "lighting": "sunrise behind", "camera": "silhouette panorama", "scene": "First sight of the Danube, figures stopping to look"},
            {"id": "07", "lighting": "flat midday", "camera": "high angle looking down", "scene": "Crossroads with multiple columns converging"},
            {"id": "08", "lighting": "dusk purple", "camera": "medium close", "scene": "Old man being helped onto wagon, dignity maintained"},
            {"id": "09", "lighting": "moonlight blue", "camera": "wide night", "scene": "Camp sleeping, single watchfire, stars"},
            {"id": "10", "lighting": "foggy morning", "camera": "through fog layers", "scene": "River appearing through mist, distant shore"},
        ]
    },
    "ch03": {
        "title": "The Crossing and Waiting",
        "era": "376 CE",
        "location": "Danube riverbank and crossing points",
        "shots": [
            {"id": "01", "lighting": "grey overcast", "camera": "extreme wide", "scene": "Thousands on riverbank, boats in water"},
            {"id": "02", "lighting": "rain slanting", "camera": "medium, rain-lashed", "scene": "Families huddled under wagon, children shivering"},
            {"id": "03", "lighting": "dawn pink", "camera": "wide river view", "scene": "First boats launching, Roman shore distant"},
            {"id": "04", "lighting": "harsh noon", "camera": "close detail", "scene": "Hands gripping boat gunwale, knuckles white"},
            {"id": "05", "lighting": "afternoon haze", "camera": "from water level", "scene": "Overloaded boat mid-river, far shores both visible"},
            {"id": "06", "lighting": "sunset gold on water", "camera": "panorama", "scene": "River as golden road, silhouette boats"},
            {"id": "07", "lighting": "night torches", "camera": "medium wide", "scene": "Roman checkpoint on far shore, torchlit processing"},
            {"id": "08", "lighting": "foggy cold", "camera": "intimate close", "scene": "Mother holding infant, breath visible"},
            {"id": "09", "lighting": "storm approaching", "camera": "wide dramatic sky", "scene": "Boats racing for shore, dark clouds"},
            {"id": "10", "lighting": "morning after storm", "camera": "wide aftermath", "scene": "Debris on bank, people searching, calm water"},
        ]
    },
    "ch04": {
        "title": "Exploitation, Famine, the Price of Food",
        "era": "376 CE",
        "location": "Roman processing camps and markets",
        "shots": [
            {"id": "01", "lighting": "flat institutional", "camera": "wide, clinical", "scene": "Counting station, queues of people, Roman clerks"},
            {"id": "02", "lighting": "harsh noon shadows", "camera": "medium, high contrast", "scene": "Weapons pile, Gothic hands surrendering swords"},
            {"id": "03", "lighting": "dim interior", "camera": "through bars/fence", "scene": "Holding pen, families sitting on ground"},
            {"id": "04", "lighting": "morning market", "camera": "medium transaction", "scene": "Grain being weighed, desperate reach"},
            {"id": "05", "lighting": "afternoon dust", "camera": "wide camp overview", "scene": "Tents and hovels, Roman guards patrolling"},
            {"id": "06", "lighting": "firelight", "camera": "close faces", "scene": "Thin children around small fire, single pot"},
            {"id": "07", "lighting": "grey drizzle", "camera": "medium queue", "scene": "Line for water, buckets, patience exhausted"},
            {"id": "08", "lighting": "sunset red", "camera": "silhouette wide", "scene": "Camp perimeter, guards and watched"},
            {"id": "09", "lighting": "night minimal", "camera": "intimate close", "scene": "Parent dividing bread, portions painfully small"},
            {"id": "10", "lighting": "dawn cold", "camera": "wide establishing", "scene": "Camp waking, frost on ground, people stirring"},
        ]
    },
    "ch05": {
        "title": "Marcianople",
        "era": "376 CE",
        "location": "City of Marcianople - gate, headquarters, banquet hall",
        "shots": [
            {"id": "01", "lighting": "morning clear", "camera": "wide approach", "scene": "City walls from road, Gothic delegation approaching"},
            {"id": "02", "lighting": "noon shadow", "camera": "through gate arch", "scene": "Gate interior, darkness framing bright exterior crowd"},
            {"id": "03", "lighting": "courtyard afternoon", "camera": "medium wide", "scene": "Headquarters courtyard, retainers waiting, geometry"},
            {"id": "04", "lighting": "interior lamplight", "camera": "wide room", "scene": "Banquet hall preparation, servants, tables"},
            {"id": "05", "lighting": "warm interior", "camera": "medium table level", "scene": "Food and wine on table, Roman hospitality display"},
            {"id": "06", "lighting": "courtyard dusk", "camera": "medium, tension", "scene": "Retainers pacing, shadows lengthening"},
            {"id": "07", "lighting": "interior gold", "camera": "through doorway", "scene": "Glimpse of banquet from courtyard door"},
            {"id": "08", "lighting": "torchlight sudden", "camera": "dutch angle", "scene": "Messenger running through courtyard"},
            {"id": "09", "lighting": "interior chaos", "camera": "wide room", "scene": "Banquet disrupted, overturned cups, movement"},
            {"id": "10", "lighting": "night aftermath", "camera": "wide gate exterior", "scene": "Gate closed, crowd pressing, torches both sides"},
        ]
    },
    "ch06": {
        "title": "Open Revolt Across Thrace",
        "era": "376-377 CE",
        "location": "Thracian countryside, villages, roads",
        "shots": [
            {"id": "01", "lighting": "dawn red", "camera": "extreme wide", "scene": "Multiple fires across valley, smoke columns"},
            {"id": "02", "lighting": "noon dust", "camera": "medium action", "scene": "Gothic warriors on road, Roman supplies captured"},
            {"id": "03", "lighting": "afternoon golden", "camera": "wide landscape", "scene": "Burning villa in distance, figures moving away"},
            {"id": "04", "lighting": "firelight night", "camera": "medium gathering", "scene": "War council around fire, maps on ground"},
            {"id": "05", "lighting": "grey morning", "camera": "wide battlefield after", "scene": "Skirmish aftermath, scattered equipment, empty"},
            {"id": "06", "lighting": "sunset dramatic", "camera": "silhouette ridge", "scene": "Gothic band on hilltop, surveying terrain"},
            {"id": "07", "lighting": "overcast flat", "camera": "medium movement", "scene": "Column on march, armed, organized"},
            {"id": "08", "lighting": "storm light", "camera": "wide ominous", "scene": "Roman fort in distance, Gothic forces gathering"},
            {"id": "09", "lighting": "night minimal", "camera": "close detail", "scene": "Hands sharpening blade, firelight glint"},
            {"id": "10", "lighting": "dawn mist", "camera": "wide mysterious", "scene": "Figures emerging from fog, Roman watchtower"},
        ]
    },
    "ch07": {
        "title": "Valens Turns East to West",
        "era": "377-378 CE",
        "location": "Imperial campaign headquarters, roads west",
        "shots": [
            {"id": "01", "lighting": "tent interior gold", "camera": "wide command", "scene": "Imperial tent, maps, officers standing"},
            {"id": "02", "lighting": "afternoon formal", "camera": "medium portrait", "scene": "Emperor at field desk, dispatches"},
            {"id": "03", "lighting": "dawn departure", "camera": "wide column", "scene": "Imperial army breaking camp, standards raised"},
            {"id": "04", "lighting": "noon dust march", "camera": "medium wide", "scene": "Cavalry column on road, dust cloud"},
            {"id": "05", "lighting": "evening camp", "camera": "wide establishing", "scene": "Military camp layout, organized, imperial"},
            {"id": "06", "lighting": "interior lamplight", "camera": "over shoulder", "scene": "Map being studied, finger tracing route"},
            {"id": "07", "lighting": "sunset dramatic", "camera": "silhouette imperial", "scene": "Emperor on horseback, aides, western horizon"},
            {"id": "08", "lighting": "night stars", "camera": "wide camp", "scene": "Thousand fires, army at rest, clear sky"},
            {"id": "09", "lighting": "grey morning", "camera": "medium ranks", "scene": "Infantry forming up, armor and shields"},
            {"id": "10", "lighting": "harsh noon", "camera": "wide approach", "scene": "Army nearing Adrianople, city visible"},
        ]
    },
    "ch08": {
        "title": "Adrianople",
        "era": "9 August 378 CE",
        "location": "Plains outside Adrianople",
        "shots": [
            {"id": "01", "lighting": "dawn pre-battle", "camera": "extreme wide", "scene": "Both armies visible, plain between, low sun"},
            {"id": "02", "lighting": "morning heat building", "camera": "medium ranks", "scene": "Roman infantry waiting, dust rising"},
            {"id": "03", "lighting": "noon brutal", "camera": "close detail", "scene": "Sweat on face, hand gripping pilum"},
            {"id": "04", "lighting": "afternoon dust haze", "camera": "wide chaos", "scene": "Gothic cavalry charge, dust cloud, impact"},
            {"id": "05", "lighting": "sun through dust", "camera": "from within press", "scene": "Shields locked, spears overhead, compression"},
            {"id": "06", "lighting": "afternoon gold harsh", "camera": "wide encirclement", "scene": "Roman square collapsing, cavalry all sides"},
            {"id": "07", "lighting": "late afternoon", "camera": "ground level", "scene": "Fallen standards, trampled ground, chaos"},
            {"id": "08", "lighting": "sunset blood red", "camera": "wide aftermath beginning", "scene": "Fighting dying down, scattered groups"},
            {"id": "09", "lighting": "dusk purple", "camera": "medium searching", "scene": "Figures moving among fallen, looking"},
            {"id": "10", "lighting": "night fires", "camera": "wide field", "scene": "Scattered fires, field of debris, silence"},
        ]
    },
    "ch09": {
        "title": "Aftermath",
        "era": "378 CE",
        "location": "Battlefield and surrounding territory",
        "shots": [
            {"id": "01", "lighting": "grey dawn", "camera": "extreme wide empty", "scene": "Battlefield morning after, mist, stillness"},
            {"id": "02", "lighting": "morning pale", "camera": "close detail", "scene": "Fallen imperial standard, gold eagle, dirt"},
            {"id": "03", "lighting": "flat overcast", "camera": "wide searching", "scene": "Figures walking field, looking, not finding"},
            {"id": "04", "lighting": "afternoon", "camera": "medium", "scene": "Burial parties working, distant, methodical"},
            {"id": "05", "lighting": "sunset lonely", "camera": "silhouette single figure", "scene": "Survivor walking away, road to horizon"},
            {"id": "06", "lighting": "grey", "camera": "wide city", "scene": "Adrianople walls, closed gates, nobody"},
            {"id": "07", "lighting": "rain", "camera": "medium detail", "scene": "Equipment in mud, rain pooling in helmet"},
            {"id": "08", "lighting": "night stars", "camera": "extreme wide", "scene": "Empty field under stars, no fires"},
            {"id": "09", "lighting": "dawn pale", "camera": "birds eye", "scene": "Crows circling, field below, distance"},
            {"id": "10", "lighting": "morning clearing", "camera": "wide road", "scene": "Empty road leading away, grass reclaiming edges"},
        ]
    },
}

def build_prompt(chapter_key: str, shot: dict) -> str:
    ch = CHAPTERS[chapter_key]
    return (
        f"{shot['scene']}. "
        f"Lighting: {shot['lighting']}. "
        f"Camera: {shot['camera']}. "
        f"Setting: {ch['location']}, {ch['era']}. "
        f"Layered cut-paper illustration with stacked depth planes, visible handmade paper texture, "
        f"hard scissor-cut edges and torn deckle edges for damage, "
        f"light rendered as flat translucent shapes not illumination, "
        f"palette of deep indigo bone iron-grey and tarnished gold (gold for light/fire only), "
        f"off-center asymmetric composition, figures as silhouettes where distant."
    )


def build_metadata(chapter_key: str, shot: dict, output_path: Path, file_size: int) -> dict:
    ch = CHAPTERS[chapter_key]
    return {
        "id": f"{chapter_key.upper()}-{shot['id']}",
        "chapter": chapter_key,
        "chapterTitle": ch["title"],
        "era": ch["era"],
        "location": ch["location"],
        "shotNumber": int(shot["id"]),
        "lighting": shot["lighting"],
        "camera": shot["camera"],
        "scene": shot["scene"],
        "generator": "openai",
        "model": "gpt-image-2",
        "size": "3840x2160",
        "quality": "high",
        "filePath": str(output_path),
        "fileSizeBytes": file_size,
        "generatedAt": datetime.utcnow().isoformat() + "Z",
    }


def generate_single(chapter_key: str, shot: dict, ref_style: Path) -> dict:
    ch_num = chapter_key.replace("ch", "")
    output_dir = Path(f"/workspace/assets/chapters/{chapter_key}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / f"{chapter_key.upper()}-{shot['id']}.png"
    prompt = build_prompt(chapter_key, shot)
    
    cmd = [
        "python3", "/workspace/scripts/generate_image.py",
        "--output", str(output_path),
        "--ref-style", str(ref_style),
        "--prompt", prompt,
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        return {"error": result.stderr, "shot": shot["id"], "chapter": chapter_key}
    
    file_size = output_path.stat().st_size if output_path.exists() else 0
    metadata = build_metadata(chapter_key, shot, output_path, file_size)
    
    # Write metadata JSON alongside image
    meta_path = output_path.with_suffix(".json")
    meta_path.write_text(json.dumps(metadata, indent=2))
    
    return metadata


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--chapter", required=True, help="Chapter key (ch01-ch09)")
    parser.add_argument("--shot", help="Specific shot ID (01-10), or 'all'")
    parser.add_argument("--ref-style", default="/workspace/assets/references/style-ref-01.png")
    args = parser.parse_args()
    
    if args.chapter not in CHAPTERS:
        print(f"Unknown chapter: {args.chapter}")
        sys.exit(1)
    
    ref_style = Path(args.ref_style)
    ch = CHAPTERS[args.chapter]
    
    if args.shot and args.shot != "all":
        shots = [s for s in ch["shots"] if s["id"] == args.shot]
    else:
        shots = ch["shots"]
    
    results = []
    for shot in shots:
        print(f"Generating {args.chapter} shot {shot['id']}: {shot['scene'][:50]}...")
        result = generate_single(args.chapter, shot, ref_style)
        results.append(result)
        if "error" not in result:
            print(f"  Done: {result['filePath']} ({result['fileSizeBytes']} bytes)")
        else:
            print(f"  ERROR: {result['error']}")
    
    # Write chapter summary
    summary_path = Path(f"/workspace/assets/chapters/{args.chapter}/manifest.json")
    summary_path.write_text(json.dumps({
        "chapter": args.chapter,
        "title": ch["title"],
        "generatedAt": datetime.utcnow().isoformat() + "Z",
        "shots": results,
    }, indent=2))
    
    print(f"\nChapter {args.chapter} complete. Manifest: {summary_path}")


if __name__ == "__main__":
    main()
