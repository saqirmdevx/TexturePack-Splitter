"""Single-document data model shared by gui_app.py.

Bridges the headless core already implemented in split_spritesheet.py
(splitting) and pack_spritesheet.py (packing) into one in-memory document
that the GUI can load, edit (pivot points), and export from — without
duplicating the cropping/packing logic itself.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image

from pack_spritesheet import (
    build_animations,
    discover_frames,
    load_default_icc_profile,
    load_images,
    pack_frames,
)
from split_spritesheet import build_targets, crop_frame
from version import __version__

PIVOT_PRESETS = {
    "Center": (0.5, 0.5),
    "Top left": (0.0, 0.0),
    "Top center": (0.5, 0.0),
    "Bottom center": (0.5, 1.0),
    "Bottom right": (1.0, 1.0),
}

DEFAULT_ANCHOR = (0.5, 0.5)


@dataclass
class SpriteFrame:
    key: str
    image: Image.Image
    anchor: tuple = DEFAULT_ANCHOR


@dataclass
class SpriteDocument:
    name: str
    frames: dict = field(default_factory=dict)
    animations: Optional[dict] = None
    pivot_points_enabled: bool = False


def load_from_spritesheet(json_path: Path) -> SpriteDocument:
    """Load a JSON+PNG spritesheet, cropping every frame into memory."""
    with open(json_path, "r") as fh:
        data = json.load(fh)

    if "frames" not in data:
        raise ValueError(f"{json_path} has no 'frames' key")

    image_name = data.get("meta", {}).get("image")
    if not image_name:
        raise ValueError(f"{json_path} has no meta.image")

    png_path = json_path.parent / image_name
    if not png_path.exists():
        raise FileNotFoundError(f"image '{png_path}' referenced by {json_path} not found")

    sheet = Image.open(png_path).convert("RGBA")
    targets = build_targets(data)

    frames = {}
    for frame_key, rel_path in targets.items():
        frame_data = data["frames"][frame_key]
        cropped = crop_frame(sheet, frame_data)
        key = rel_path.as_posix()
        anchor_data = frame_data.get("anchor") or {}
        anchor = (anchor_data.get("x", 0.5), anchor_data.get("y", 0.5))
        frames[key] = SpriteFrame(key=key, image=cropped, anchor=anchor)

    animations = None
    raw_animations = data.get("animations")
    if raw_animations:
        animations = {}
        for anim_name, frame_keys in raw_animations.items():
            keys = [targets[fk].as_posix() for fk in frame_keys if fk in targets]
            if keys:
                animations[anim_name] = keys

    return SpriteDocument(name=json_path.stem, frames=frames, animations=animations)


def load_from_folder(folder_path: Path) -> SpriteDocument:
    """Load every image under a folder (subfolders become animations)."""
    frame_paths = discover_frames(folder_path)
    if not frame_paths:
        raise ValueError(f"no .png files found under '{folder_path}'")

    images = load_images(frame_paths)
    frames = {key: SpriteFrame(key=key, image=im) for key, im in images.items()}
    animations = build_animations(images.keys())
    return SpriteDocument(name=folder_path.name, frames=frames, animations=animations)


def set_anchor(doc: SpriteDocument, keys: Iterable[str], anchor: tuple) -> None:
    """Apply a normalized (0-1) anchor to every given frame key."""
    for key in keys:
        frame = doc.frames.get(key)
        if frame is not None:
            frame.anchor = anchor


def export_split(doc: SpriteDocument, out_dir: Path) -> int:
    """Write every frame back out as an individual image file."""
    out_dir.mkdir(parents=True, exist_ok=True)
    icc_profile = load_default_icc_profile()
    save_kwargs = {"icc_profile": icc_profile} if icc_profile is not None else {}

    count = 0
    for key, frame in doc.frames.items():
        out_path = out_dir / key
        out_path.parent.mkdir(parents=True, exist_ok=True)
        frame.image.save(out_path, **save_kwargs)
        count += 1
    return count


def export_publish(doc: SpriteDocument, out_dir: Path, name: Optional[str] = None):
    """Pack every frame into one spritesheet PNG + JSON, honoring per-frame
    anchors when pivot points are enabled (else every frame gets the default
    center anchor, matching the unchecked "Enable pivot points" state)."""
    name = name or doc.name
    images = {key: frame.image for key, frame in doc.frames.items()}
    atlas, positions = pack_frames(images, max_width=2048, padding=0)

    frames_json = {}
    for key, frame in doc.frames.items():
        x, y = positions[key]
        w, h = frame.image.width, frame.image.height
        anchor = frame.anchor if doc.pivot_points_enabled else DEFAULT_ANCHOR
        frames_json[key] = {
            "frame": {"x": x, "y": y, "w": w, "h": h},
            "spriteSourceSize": {"x": 0, "y": 0, "w": w, "h": h},
            "sourceSize": {"w": w, "h": h},
            "anchor": {"x": anchor[0], "y": anchor[1]},
        }

    data = {"frames": frames_json}
    if doc.animations:
        data["animations"] = doc.animations
    data["meta"] = {
        "app": "Spritesheet Utility",
        "version": __version__,
        "image": f"{name}.png",
        "size": {"w": atlas.width, "h": atlas.height},
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    png_path = out_dir / f"{name}.png"
    json_path = out_dir / f"{name}.json"

    icc_profile = load_default_icc_profile()
    save_kwargs = {"icc_profile": icc_profile} if icc_profile is not None else {}
    atlas.save(png_path, **save_kwargs)
    json_path.write_text(json.dumps(data, separators=(",", ":")))

    return png_path, json_path
