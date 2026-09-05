#!/usr/bin/env python3
"""Pack a folder of individual frame images into one TexturePacker-style
spritesheet (PNG + JSON) — the inverse of split_spritesheet.py.

Every image directly inside the input folder becomes a flat frame, keyed by
its filename (e.g. "1.png"). Every image inside a subfolder becomes part of
an animation named after that subfolder's path (e.g. "Attack/0.png"), which
mirrors exactly how split_spritesheet.py lays frames back out on disk.

Frames are packed without rotation or trimming, so "spriteSourceSize" always
matches "sourceSize" at offset (0, 0) and no "rotated"/"trimmed" fields are
written. Each frame gets a normalized "anchor" (pivot point), defaulting to
the center (0.5, 0.5) unless overridden with --anchor.

Usage:
    python pack_spritesheet.py -i output/objects/golds -o packed
    python pack_spritesheet.py -i output/objects/DivineKatanaObj --name Katana
"""

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Optional

from PIL import Image

from split_spritesheet import DEFAULT_ICC_PROFILE_PATH
from version import __version__

OUTPUT_DIR = Path("packed")
IMAGE_EXTENSIONS = {".png"}


def natural_key(s: str):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


def load_default_icc_profile() -> Optional[bytes]:
    try:
        return DEFAULT_ICC_PROFILE_PATH.read_bytes()
    except FileNotFoundError:
        print(f"warning: {DEFAULT_ICC_PROFILE_PATH.name} not found, saving without an ICC color profile", file=sys.stderr)
        return None


def discover_frames(root: Path) -> dict:
    """Map frame_key (posix path relative to root) -> absolute image path."""
    frames = {}
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS:
            key = path.relative_to(root).as_posix()
            frames[key] = path
    return frames


def load_images(frame_paths: dict) -> dict:
    return {key: Image.open(path).convert("RGBA") for key, path in frame_paths.items()}


def pack_frames(images: dict, max_width: int, padding: int):
    """Shelf-pack images left-to-right, wrapping at max_width. Returns (atlas, positions)."""
    items = sorted(images.items(), key=lambda kv: (-kv[1].height, -kv[1].width, kv[0]))

    positions = {}
    x = y = shelf_height = 0
    atlas_width = 0
    for key, im in items:
        w, h = im.width, im.height
        if x > 0 and x + w > max_width:
            y += shelf_height + padding
            x = 0
            shelf_height = 0
        positions[key] = (x, y)
        shelf_height = max(shelf_height, h)
        atlas_width = max(atlas_width, x + w)
        x += w + padding
    atlas_height = y + shelf_height

    atlas = Image.new("RGBA", (atlas_width, atlas_height), (0, 0, 0, 0))
    for key, im in items:
        atlas.paste(im, positions[key])
    return atlas, positions


def build_animations(frame_keys) -> Optional[dict]:
    """Group frame keys by parent folder; None if every frame is at the root."""
    groups = {}
    for key in frame_keys:
        parent = PurePosixPath(key).parent.as_posix()
        groups.setdefault(parent, []).append(key)

    if all(parent == "." for parent in groups):
        return None

    animations = {}
    for parent in sorted((p for p in groups if p != "."), key=natural_key):
        animations[parent] = sorted(groups[parent], key=lambda k: natural_key(PurePosixPath(k).name))
    return animations


def build_json(images: dict, positions: dict, atlas_size: tuple, name: str, anchor: tuple) -> dict:
    frames = {}
    for key, im in images.items():
        x, y = positions[key]
        w, h = im.width, im.height
        frames[key] = {
            "frame": {"x": x, "y": y, "w": w, "h": h},
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h},
            "anchor": {"x": anchor[0], "y": anchor[1]},
        }

    data = {"frames": frames}
    animations = build_animations(images.keys())
    if animations:
        data["animations"] = animations

    data["meta"] = {
        "app": "TextureSplitter Packer",
        "version": __version__,
        "image": f"{name}.png",
        "size": {"w": atlas_size[0], "h": atlas_size[1]},
    }
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-i", "--input", type=Path, required=True,
                         help="folder of frame images to pack (subfolders become animations)")
    parser.add_argument("-o", "--output", type=Path, default=OUTPUT_DIR,
                         help=f"folder to write the packed .png/.json into (default: {OUTPUT_DIR})")
    parser.add_argument("--name", default=None,
                         help="output file basename, without extension (default: the input folder's name)")
    parser.add_argument("-p", "--padding", type=int, default=0,
                         help="pixels of empty space between packed frames (default: 0)")
    parser.add_argument("--max-width", type=int, default=2048,
                         help="target maximum atlas width in pixels; a single frame wider than this still "
                              "gets its own row (default: 2048)")
    parser.add_argument("--anchor", type=float, nargs=2, metavar=("X", "Y"), default=(0.5, 0.5),
                         help="normalized pivot point (0-1) applied to every frame (default: 0.5 0.5)")
    parser.add_argument("-v", "--version", action="version", version=f"TextureSplitter {__version__}")
    args = parser.parse_args()

    if not args.input.is_dir():
        print(f"error: input directory '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    frame_paths = discover_frames(args.input)
    if not frame_paths:
        print(f"error: no .png files found under '{args.input}'", file=sys.stderr)
        sys.exit(1)

    name = args.name or args.input.name
    images = load_images(frame_paths)
    atlas, positions = pack_frames(images, max_width=args.max_width, padding=args.padding)
    data = build_json(images, positions, (atlas.width, atlas.height), name, tuple(args.anchor))

    args.output.mkdir(parents=True, exist_ok=True)
    png_path = args.output / f"{name}.png"
    json_path = args.output / f"{name}.json"

    save_kwargs = {}
    icc_profile = load_default_icc_profile()
    if icc_profile is not None:
        save_kwargs["icc_profile"] = icc_profile
    atlas.save(png_path, **save_kwargs)
    json_path.write_text(json.dumps(data, separators=(",", ":")))

    print(f"Packed {len(frame_paths)} frame(s) from '{args.input}' into {png_path} "
          f"({atlas.width}x{atlas.height}) + {json_path}")


if __name__ == "__main__":
    main()
