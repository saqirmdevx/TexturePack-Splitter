# TextureSplitter

Splits TexturePacker-style spritesheets (PNG + JSON) into individual frame
images, organized into per-animation folders. Comes with both a command-line
script and a desktop GUI.

*Português (Brasil): [README_BR.md](README_BR.md)*

## Features

- **GUI** (`app.py`): pick the JSON from a file picker — the PNG is
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

The GUI additionally needs `tkinter`, which ships with the standard Python
installer on Windows/macOS. On Linux, install it separately (see above) since
it isn't distributed via pip.

## 3. Run it

### GUI

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

Input and output folders are fixed — always `input/` and `output/` next to the
script, no path flags needed. On macOS/Linux you can also use `./run.sh`, and
on Windows `run.bat` (both expect the `.venv` folder to already exist).

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
