# TextureSplitter

Splits TexturePacker-style spritesheets (PNG + JSON) into individual frame
images, organized into per-animation folders.

## 1. Install Python

You need Python 3.8 or newer.

- **macOS**: Python 3 usually comes preinstalled. Check with:
  ```bash
  python3 --version
  ```
  If it's missing or too old, install via [Homebrew](https://brew.sh):
  ```bash
  brew install python
  ```
- **Windows**: Download the installer from [python.org/downloads](https://www.python.org/downloads/)
  and run it (check "Add python.exe to PATH" during setup).
- **Linux**: Install via your package manager, e.g.:
  ```bash
  sudo apt install python3 python3-venv
  ```

## 2. Install the requirements

From the project folder, create a virtual environment and install dependencies
(currently just [Pillow](https://python-pillow.org/), the image library):

```bash
python3 -m venv .venv
```

Activate it:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## 3. Run the script

With the virtual environment activated, run it from the project folder:

```bash
python split_spritesheet.py
```

Input and output folders are fixed — always `input/` and `output/` next to the
script, no path flags needed.

### Options

| Flag | Description | Default |
|---|---|---|
| `-fs N`, `--frame-size N` | Pad every frame onto a centered, transparent `N x N` canvas (no resizing) | off |

Example:

```bash
# Pad every frame to 64x64 (adds transparent space, does not scale the art)
python split_spritesheet.py -fs 64
```

### Input structure

The script recursively scans `input/` for `.json` files. Each JSON's
`meta.image` field names the PNG sitting next to it in the same folder, so you
can split multiple spritesheets in one run by nesting them in subfolders:

```
input/
  creatures/
    0/
      spritesheet.json   # meta.image: "spritesheet.png"
      spritesheet.png
    1/
      spritesheet.json
      spritesheet.png
```

### Output structure

Each spritesheet's output mirrors its folder location under `input/`, then
splits into animations inside that folder:

- If the JSON defines an `"animations"` block, frames are grouped into one
  folder per animation, named after each frame's original filename:
  ```
  output/creatures/0/Attack/0.png
  output/creatures/0/Attack/1.png
  output/creatures/0/Walk/0.png
  output/creatures/1/Attack/0.png
  ...
  ```
- If no `"animations"` block is present, all frames for that spritesheet are
  written flat into its target folder (folder path separators in the frame
  name are replaced with `_` to keep filenames unique).

### Clearing old output

If `output/` already has content, the script asks before touching it:

```
Output directory 'output' is not empty. Clear it before continuing? [y/N]:
```

- `y` — deletes everything in `output/` first, then writes fresh results.
- `n` (or just pressing Enter) — leaves existing files alone; the run still
  writes/overwrites frames for whatever spritesheets it finds, but stale files
  from previous runs are not removed.

## Quality notes

- Frames are cropped pixel-for-pixel from the source sheet — no resampling or
  recompression artifacts are introduced.
- The `-fs` padding option pastes the frame onto a fully transparent canvas
  without blending, so anti-aliased/semi-transparent edge pixels are copied
  exactly as-is.
- Output PNGs carry the source spritesheet's ICC color profile when present,
  or fall back to the bundled standard sRGB profile (`srgb.icc`), so exported
  frames are correctly color-tagged rather than left as untagged RGB.
