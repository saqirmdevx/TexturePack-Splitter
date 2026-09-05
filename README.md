# TextureSplitter

Splits TexturePacker-style spritesheets (PNG + JSON) into individual frame
images, organized into per-animation folders, and packs them back. Comes with
command-line tools and a desktop GUI.

## Features

- **GUI (new, in progress)** (`gui_app.py`): PySide6 rewrite with a 3-pane
  layout — Explorer tree on the left, a gray zoomable canvas in the middle,
  and a pivot-point (anchor) editor on the right. Load a spritesheet JSON or
  a folder of frame images, multi-select frames in the Explorer, set their
  normalized pivot point (typed values or presets: Center, Top left, Top
  center, Bottom center, Bottom right), then **Split Sheet** or **Publish
  Sprite Sheet** to export. Coexists with the legacy GUI below; see
  [Running the new GUI](#running-the-new-gui-preview) below.
- **GUI (legacy)** (`app.py`): pick the JSON from a file picker — the PNG is
  auto-detected next to it via the JSON's `meta.image` field — choose a
  sprite size (16, 32, 48, 64, 96, 128, 256, 512, or custom), preview every
  sprite, inspect its JSON metadata (`frame`, `anchor`, `spriteSourceSize`,
  `sourceSize`, `rotated`, `trimmed`), and export straight to a folder you
  choose.
  - `64 x 64` by default; the artwork is never resized, only centered on a
    transparent canvas.
  - Output mirrors the JSON's `animations` block into per-animation folders;
    without `animations`, output is flat.
  - Available in Portuguese, English, Spanish, 中文, and Slovak.
  - On Windows, tries to create a `TextureSplitter.lnk` shortcut on the
    desktop.
- **CLI** (`split_spritesheet.py`): batch-processes every spritesheet found
  under `input/`, with an optional `-fs` flag to pad frames onto a fixed-size
  canvas.
- **Packer CLI** (`pack_spritesheet.py`): the inverse of the splitter — packs
  a folder of individual frame images back into one spritesheet PNG + JSON.

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
  sudo apt install python3 python3-venv python3-tk
  ```
  (`python3-tk` is required for the GUI; the CLI script doesn't need it.)

## 2. Install the requirements

From the project folder, create a virtual environment and install
dependencies (currently just [Pillow](https://python-pillow.org/), the image
library):

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

The legacy GUI additionally needs `tkinter`, which ships with the standard
Python installer on Windows/macOS. On Linux, install it separately (see
above) since it isn't distributed via pip. The new GUI needs `PySide6`
instead — install it with:

```bash
pip install -r requirements-gui.txt
```

## 3. Run it

### Running the new GUI (preview)

With `requirements-gui.txt` installed and the virtual environment activated:

```bash
python gui_app.py
```

Use **Load Spritesheet** (a JSON+PNG pair) or **Load Folder** (a folder of
loose frame images, subfolders becoming animations) to populate the
Explorer. Select one or more frames there — folders select every frame
inside them — to filter the canvas and enable the pivot-point editor on the
right: check **Enable pivot points**, then type normalized `x`/`y` values,
their pixel-space equivalents, or pick a preset; it applies to every frame
currently selected. **Split Sheet** exports the loaded frames individually;
**Publish Sprite Sheet** repacks them into a new spritesheet PNG+JSON,
writing each frame's edited pivot point into its `"anchor"` field (or the
default center for every frame if pivot points are left disabled).

This GUI is still early — the Explorer only holds one loaded document at a
time (loading something new replaces it), and canvas thumbnails aren't yet
clickable for selection (use the Explorer tree). The legacy Tkinter GUI below
remains fully functional.

### Legacy GUI

With the virtual environment activated, run:

```bash
python app.py
```

On Windows you can also double-click `run_TextureSplitter.bat`.

Select the JSON file (its PNG is loaded automatically from `meta.image`),
pick a sprite size, choose an output folder, and click **CUT IMAGES**. Use
the language button in the top-right corner to switch the interface
language.

### CLI

With the virtual environment activated, run it from the project folder:

```bash
python split_spritesheet.py
```

By default it reads from `input/` and writes to `output/`, both next to the
script — no path flags needed. On macOS/Linux you can also use `./run.sh`, and
on Windows `run.bat` (both expect the `.venv` folder to already exist).

### Options

| Flag | Description | Default |
|---|---|---|
| `-fs N`, `--frame-size N` | Pad every frame onto a centered, transparent `N x N` canvas (no resizing) | off |
| `-i PATH`, `--input PATH` | Folder to recursively scan for spritesheet `.json` files | `input` |
| `-o PATH`, `--output PATH` | Folder to write split frames to | `output` |

Example:

```bash
# Pad every frame to 64x64 (adds transparent space, does not scale the art)
python split_spritesheet.py -fs 64

# Split spritesheets from a different folder
python split_spritesheet.py -i path/to/spritesheets -o path/to/out
```

### Input structure

The script recursively scans `input/` for `.json` files. Each JSON's
`meta.image` field names the PNG sitting next to it in the same folder, so
multiple spritesheets can live side by side in the same folder or nested in
subfolders:

```
input/
  objects/
    golds.json         # meta.image: "golds.png"
    golds.png
    bushes.json
    bushes.png
    runes/
      haste_rune.json
      haste_rune.png
```

### Output structure

Each spritesheet's output mirrors its JSON's folder location under `input/`,
then adds one more folder named after the JSON file itself (its filename
without the `.json` extension) — this keeps sheets that share a folder, or
share frame/animation names, from overwriting each other:

- If the JSON defines an `"animations"` block, frames are further grouped
  into one folder per animation, named after each frame's original filename:
  ```
  output/objects/DivineKatanaObj/Idle/1.png
  output/objects/DivineKatanaObj/Idle/2.png
  output/objects/DivineKatanaObj/Init/1.png
  output/objects/runes/haste_rune/Idle/1.png
  ...
  ```
- If no `"animations"` block is present, all frames for that spritesheet are
  written flat into its target folder:
  ```
  output/objects/golds/1.png
  output/objects/golds/2.png
  output/objects/bushes/1.png
  ...
  ```

### Clearing old output

If `output/` already has content, the script asks before touching it:

```
Output directory 'output' is not empty. Clear it before continuing? [y/N]:
```

- `y` — deletes everything in `output/` first, then writes fresh results.
- `n` (or just pressing Enter) — leaves existing files alone; the run still
  writes/overwrites frames for whatever spritesheets it finds, but stale files
  from previous runs are not removed.

### Packer CLI

`pack_spritesheet.py` packs one folder of frame images into one spritesheet —
the exact inverse of the splitter above. Point it at a folder produced by (or
shaped like) the splitter's output:

```bash
python pack_spritesheet.py -i output/objects/golds -o packed
```

- Every image directly inside the input folder becomes a flat frame, keyed by
  its filename (e.g. `"1.png"`).
- Every image inside a subfolder becomes part of an `"animations"` entry named
  after that subfolder's path (e.g. `"Attack/0.png"`), regardless of nesting
  depth.
- Frames are packed without rotation or trimming: `"spriteSourceSize"` always
  matches `"sourceSize"` at offset `(0, 0)`, and no `"rotated"`/`"trimmed"`
  fields are written.
- Each frame gets a normalized `"anchor"` (pivot point, 0–1), defaulting to
  the center `(0.5, 0.5)`.

| Flag | Description | Default |
|---|---|---|
| `-i PATH`, `--input PATH` | Folder of frame images to pack (required) | — |
| `-o PATH`, `--output PATH` | Folder to write the packed `.png`/`.json` into | `packed` |
| `--name NAME` | Output file basename, without extension | the input folder's name |
| `-p N`, `--padding N` | Pixels of empty space between packed frames | `0` |
| `--max-width N` | Target maximum atlas width in pixels; a single frame wider than this still gets its own row | `2048` |
| `--anchor X Y` | Normalized pivot point (0–1) applied to every frame | `0.5 0.5` |

```bash
# Pack DivineKatanaObj's Idle/Init/Remove folders into DivineKatanaObj.png/.json
python pack_spritesheet.py -i output/objects/DivineKatanaObj -o packed --anchor 0.5 0.41
```

Packing a folder and splitting the result reproduces the original frames
pixel-for-pixel and the original folder structure exactly.

## Building a standalone executable

You can package the GUI and CLI into standalone binaries (no Python
installation required to run them) using [PyInstaller](https://pyinstaller.org/).
Each platform's binary must be built on that platform — there's no
cross-compiling.

- **macOS**: `./build_mac.sh`
- **Windows**: double-click `build_windows.bat` (or run it from a terminal)

Both scripts create/reuse a `.venv`, install `requirements.txt` and
`requirements-build.txt` (just `pyinstaller`), then build from
`TextureSplitter.spec` (GUI) and `TextureSplitterCLI.spec` (CLI). Output lands
in `dist/`:

- `dist/TextureSplitter.app` (macOS) / `dist/TextureSplitter.exe` (Windows) — the GUI
- `dist/TextureSplitterCLI` (macOS) / `dist/TextureSplitterCLI.exe` (Windows) — the CLI

Note: PyInstaller bundles the Python bytecode into the executable, it doesn't
protect it — tools like `pyinstxtractor` can extract it back out. It hides the
`.py` source from a casual user, not from someone deliberately reverse-engineering it.

### Prebuilt builds via GitHub Actions

Every push to `main` (and every pull request) triggers the
[Build Desktop Apps](.github/workflows/build.yml) workflow, which builds the
GUI and CLI for both macOS and Windows and uploads them as workflow artifacts.
To grab a build without building it yourself: open the workflow run under the
repo's **Actions** tab and download the artifact zip from the run summary
page.

## Quality notes

- Frames are cropped pixel-for-pixel from the source sheet — no resampling or
  recompression artifacts are introduced.
- The `-fs` padding option pastes the frame onto a fully transparent canvas
  without blending, so anti-aliased/semi-transparent edge pixels are copied
  exactly as-is.
- Output PNGs carry the source spritesheet's ICC color profile when present,
  or fall back to the bundled standard sRGB profile (`srgb.icc`), so exported
  frames are correctly color-tagged rather than left as untagged RGB.
