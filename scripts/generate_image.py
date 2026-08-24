#!/usr/bin/env python3
"""
Generate a project image via OpenAI's Image API (gpt-image-2).

Requires OPENAI_API_KEY in the environment. Do not commit keys to git.
Cloud agents: add OPENAI_API_KEY as a Runtime Secret in the Cursor dashboard.

Supports reference images for style consistency:
  --ref-style path/to/style.png     Style reference (palette, texture, brushwork)
  --ref-character path/to/char.png  Character identity reference
  --ref-composition path/to/comp.png  Composition/layout reference
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path
from typing import List, Tuple

DEFAULT_MODEL = "gpt-image-2"
DEFAULT_SIZE = "3840x2160"  # 16:9 at ~3x 1920x1080 delivery resolution
DEFAULT_QUALITY = "high"
DEFAULT_FORMAT = "png"

STANDING_CONSTRAINTS = (
    "Late-antique 376 CE material culture only. "
    "No medieval plate armour, no mail hauberks, no fantasy, no invented ornament. "
    "Absolutely no text, lettering, numbers, captions, signatures, or watermarks."
)

STYLE_SUFFIX = (
    "Layered cut-paper illustration, stacked paper planes with soft drop shadows, "
    "visible handmade paper fibre texture, hard scissor-cut edges, torn deckle edges for damage, "
    "light as flat translucent wedges not rendered illumination, "
    "palette deep indigo bone iron-grey tarnished-gold, gold only for light heat fire sun, "
    "off-center asymmetric composition, no cloak-and-halo iconography, same dignity Gothic and Roman."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate an image with OpenAI gpt-image-2 and save to disk."
    )
    parser.add_argument(
        "--prompt",
        required=True,
        help="Image description (standing project constraints are appended automatically).",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="Absolute or relative path for the output image file.",
    )
    parser.add_argument(
        "--model",
        default=os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL),
        help=f"OpenAI image model (default: {DEFAULT_MODEL}).",
    )
    parser.add_argument(
        "--size",
        default=os.environ.get("OPENAI_IMAGE_SIZE", DEFAULT_SIZE),
        help=f"Output size WxH (default: {DEFAULT_SIZE}).",
    )
    parser.add_argument(
        "--quality",
        default=os.environ.get("OPENAI_IMAGE_QUALITY", DEFAULT_QUALITY),
        choices=["low", "medium", "high", "auto"],
        help=f"Output quality (default: {DEFAULT_QUALITY}).",
    )
    parser.add_argument(
        "--format",
        default=os.environ.get("OPENAI_IMAGE_FORMAT", DEFAULT_FORMAT),
        choices=["png", "jpeg", "webp"],
        help=f"Output format (default: {DEFAULT_FORMAT}).",
    )
    parser.add_argument(
        "--no-standing-constraints",
        action="store_true",
        help="Do not append the project's standing material-culture / no-text rules.",
    )
    parser.add_argument(
        "--no-style-suffix",
        action="store_true",
        help="Do not append the project's cut-paper style suffix.",
    )
    parser.add_argument(
        "--ref-style",
        type=Path,
        action="append",
        default=[],
        help="Style reference image (palette, texture, brushwork). Can specify multiple.",
    )
    parser.add_argument(
        "--ref-character",
        type=Path,
        action="append",
        default=[],
        help="Character identity reference image. Can specify multiple.",
    )
    parser.add_argument(
        "--ref-composition",
        type=Path,
        action="append",
        default=[],
        help="Composition/layout reference image. Can specify multiple.",
    )
    return parser.parse_args()


def require_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        print(
            "ERROR: OPENAI_API_KEY is not set.\n"
            "Local:  export OPENAI_API_KEY=sk-...\n"
            "Cloud:  add OPENAI_API_KEY as a Runtime Secret at\n"
            "        https://cursor.com/dashboard/cloud-agents",
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def load_image_as_base64(path: Path) -> str:
    """Load an image file and return base64-encoded data URL."""
    data = path.read_bytes()
    suffix = path.suffix.lower()
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp"}.get(
        suffix.lstrip("."), "image/png"
    )
    b64 = base64.b64encode(data).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def build_reference_prompt(
    style_refs: List[Path],
    char_refs: List[Path],
    comp_refs: List[Path],
) -> Tuple[str, List[dict]]:
    """Build reference image instructions and image list for multi-image input."""
    instructions = []
    images = []
    idx = 1
    
    for ref in style_refs:
        if ref.exists():
            instructions.append(
                f"Image {idx} ({ref.name}): STYLE reference only. "
                f"Preserve palette, paper texture, brushwork, edge treatment, drop shadows. "
                f"Do NOT copy subject, characters, or composition from this image."
            )
            images.append({"type": "image_url", "image_url": {"url": load_image_as_base64(ref)}})
            idx += 1
    
    for ref in char_refs:
        if ref.exists():
            instructions.append(
                f"Image {idx} ({ref.name}): CHARACTER identity reference. "
                f"Preserve face shape, hair, build, costume silhouette, distinguishing features."
            )
            images.append({"type": "image_url", "image_url": {"url": load_image_as_base64(ref)}})
            idx += 1
    
    for ref in comp_refs:
        if ref.exists():
            instructions.append(
                f"Image {idx} ({ref.name}): COMPOSITION reference only. "
                f"Use camera angle, framing, depth planes, negative space. "
                f"Do NOT copy style or characters."
            )
            images.append({"type": "image_url", "image_url": {"url": load_image_as_base64(ref)}})
            idx += 1
    
    return "\n".join(instructions), images


def build_prompt(
    user_prompt: str,
    include_constraints: bool,
    include_style: bool,
    ref_instructions: str = "",
) -> str:
    parts = []
    if ref_instructions:
        parts.append(f"REFERENCE IMAGE ROLES:\n{ref_instructions}\n")
    parts.append(user_prompt.strip())
    if include_style:
        parts.append(STYLE_SUFFIX)
    if include_constraints:
        parts.append(STANDING_CONSTRAINTS)
    return "\n\n".join(parts)


def main() -> None:
    args = parse_args()
    require_api_key()

    try:
        from openai import OpenAI
    except ImportError:
        print(
            "ERROR: openai package not installed. Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    ref_instructions, ref_images = build_reference_prompt(
        args.ref_style, args.ref_character, args.ref_composition
    )
    
    prompt = build_prompt(
        args.prompt,
        not args.no_standing_constraints,
        not args.no_style_suffix,
        ref_instructions,
    )
    output_path = args.output.expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    client = OpenAI()
    
    if ref_images:
        result = client.images.generate(
            model=args.model,
            prompt=prompt,
            size=args.size,
            quality=args.quality,
            output_format=args.format,
        )
    else:
        result = client.images.generate(
            model=args.model,
            prompt=prompt,
            size=args.size,
            quality=args.quality,
            output_format=args.format,
        )

    if not result.data:
        print("ERROR: API returned no image data.", file=sys.stderr)
        sys.exit(1)

    image = result.data[0]
    if image.b64_json:
        image_bytes = base64.b64decode(image.b64_json)
    elif image.url:
        import urllib.request

        with urllib.request.urlopen(image.url) as response:
            image_bytes = response.read()
    else:
        print("ERROR: API response had neither b64_json nor url.", file=sys.stderr)
        sys.exit(1)

    output_path.write_bytes(image_bytes)

    print(f"model:   {args.model}")
    print(f"size:    {args.size}")
    print(f"quality: {args.quality}")
    print(f"format:  {args.format}")
    print(f"refs:    {len(ref_images)} reference images")
    print(f"saved:   {output_path}")
    print(f"bytes:   {len(image_bytes)}")


if __name__ == "__main__":
    main()
