#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [ ! -f ".venv/bin/python3" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

PY=".venv/bin/python3"

"$PY" -m pip install --upgrade pip
"$PY" -m pip install -r requirements.txt -r requirements-build.txt -r requirements-gui.txt

"$PY" -m PyInstaller --noconfirm TextureSplitter.spec

echo
echo "Done. Build output is in the dist/ folder:"
echo "  dist/TextureSplitter.app     (GUI app bundle)"
