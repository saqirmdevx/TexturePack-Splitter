#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$DIR/.venv/bin/python" ]; then
    echo "Virtual environment not found. Run this first:" >&2
    echo "  python3 -m venv .venv" >&2
    echo "  .venv/bin/pip install -r requirements.txt" >&2
    exit 1
fi

"$DIR/.venv/bin/python" "$DIR/split_spritesheet.py" "$@"
