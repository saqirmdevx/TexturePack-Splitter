#!/usr/bin/env python3
"""Split TexturePacker-style spritesheets (PNG + JSON) into individual frame files.

Recursively scans ./input for *.json files. Each JSON's "meta.image" field
names the PNG sitting alongside it. Output mirrors each JSON's folder
location under ./output, then splits into per-animation subfolders (or a flat
folder if the JSON defines no "animations").

Usage:
    python split_spritesheet.py
    python split_spritesheet.py -fs 64   # pad every frame onto a 64x64 transparent canvas
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Optional

from PIL import Image

from version import __version__

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

# Bundled standard sRGB ICC profile (HP/Microsoft "sRGB IEC61966-2.1"), used as a
# fallback so exported frames carry an explicit, universally recognized color
# profile even when the source spritesheet doesn't embed one itself.
DEFAULT_ICC_PROFILE_PATH = Path(__file__).parent / "srgb.icc"


def sanitize(name: str) -> str:
    return re.sub(r"[\\/]+", "_", name)


def load_icc_profile(sheet: Image.Image) -> Optional[bytes]:
    if "icc_profile" in sheet.info:
        return sheet.info["icc_profile"]
    try:
        return DEFAULT_ICC_PROFILE_PATH.read_bytes()
    except FileNotFoundError:
        print(f"warning: {DEFAULT_ICC_PROFILE_PATH.name} not found, saving frames without an ICC color profile", file=sys.stderr)
        return None


def place_on_canvas(frame: Image.Image, size: int) -> Image.Image:
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - frame.width) // 2
    y = (size - frame.height) // 2
    # No mask: the target region is empty transparent space, so a direct paste
    # copies pixels exactly. Passing `frame` as its own mask would instead blend
    # by its alpha channel, squaring alpha on anti-aliased edge pixels.
    canvas.paste(frame, (x, y))
    return canvas


def crop_frame(sheet: Image.Image, frame_data: dict) -> Image.Image:
    f = frame_data["frame"]
    box = (f["x"], f["y"], f["x"] + f["w"], f["y"] + f["h"])
    return sheet.crop(box)


def build_targets(data: dict) -> dict:
    """Map frame_key -> output relative path (without extension handling)."""
    frames = data["frames"]
    animations = data.get("animations")

    targets = {}
    if animations:
        for anim_name, frame_keys in animations.items():
            for frame_key in frame_keys:
                if frame_key not in frames:
                    print(f"warning: '{frame_key}' listed in animations but missing from frames, skipping", file=sys.stderr)
                    continue
                filename = Path(frame_key).name
                targets[frame_key] = Path(anim_name) / filename
    else:
        for frame_key in frames:
            targets[frame_key] = Path(sanitize(frame_key))

    return targets


def prompt_clear_output(output_dir: Path) -> None:
    if not output_dir.exists():
        return
    entries = [e for e in output_dir.iterdir() if e.name != ".DS_Store"]
    if not entries:
        return

    try:
        answer = input(f"Output directory '{output_dir}' is not empty. Clear it before continuing? [y/N]: ").strip().lower()
    except EOFError:
        answer = "n"

    if answer in ("y", "yes"):
        for entry in entries:
            if entry.is_dir():
                shutil.rmtree(entry)
            else:
                entry.unlink()
        print(f"Cleared {output_dir}")


def process_spritesheet(json_path: Path, out_dir: Path, frame_size: Optional[int]) -> int:
    with open(json_path, "r") as fh:
        data = json.load(fh)

    if "frames" not in data:
        print(f"warning: {json_path} has no 'frames' key, skipping", file=sys.stderr)
        return 0

    image_name = data.get("meta", {}).get("image")
    if not image_name:
        print(f"warning: {json_path} has no meta.image, skipping", file=sys.stderr)
        return 0

    png_path = json_path.parent / image_name
    if not png_path.exists():
        print(f"warning: image '{png_path}' referenced by {json_path} not found, skipping", file=sys.stderr)
        return 0

    sheet = Image.open(png_path).convert("RGBA")
    icc_profile = load_icc_profile(sheet)
    dpi = sheet.info.get("dpi")
    targets = build_targets(data)

    count = 0
    for frame_key, rel_path in targets.items():
        frame_data = data["frames"][frame_key]
        cropped = crop_frame(sheet, frame_data)

        if frame_size:
            if cropped.width > frame_size or cropped.height > frame_size:
                print(f"warning: '{frame_key}' ({cropped.width}x{cropped.height}) exceeds -fs {frame_size}, leaving unpadded", file=sys.stderr)
            else:
                cropped = place_on_canvas(cropped, frame_size)

        out_path = out_dir / rel_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        save_kwargs = {}
        if icc_profile is not None:
            save_kwargs["icc_profile"] = icc_profile
        if dpi is not None:
            save_kwargs["dpi"] = dpi
        cropped.save(out_path, **save_kwargs)
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-fs", "--frame-size", type=int, default=None,
                         help="pad each frame onto an NxN transparent canvas, centered, without resizing")
    parser.add_argument("-v", "--version", action="version", version=f"TextureSplitter {__version__}")
    args = parser.parse_args()

    if not INPUT_DIR.is_dir():
        print(f"error: input directory '{INPUT_DIR}' not found", file=sys.stderr)
        sys.exit(1)

    json_files = sorted(INPUT_DIR.rglob("*.json"))
    if not json_files:
        print(f"error: no .json files found under '{INPUT_DIR}'", file=sys.stderr)
        sys.exit(1)

    prompt_clear_output(OUTPUT_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    total = 0
    for json_path in json_files:
        rel_dir = json_path.parent.relative_to(INPUT_DIR)
        out_dir = OUTPUT_DIR / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        written = process_spritesheet(json_path, out_dir, args.frame_size)
        if written:
            print(f"{json_path}: wrote {written} frame(s) to {out_dir}")
        total += written

    print(f"Wrote {total} frame(s) from {len(json_files)} spritesheet(s) to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
