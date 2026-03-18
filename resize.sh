#!/usr/bin/env bash
# Cross-platform wrapper for resize.py (macOS/Linux)
# Usage: ./resize.sh [--max-size 1024] [--quality 85] [--no-backup]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet Pillow
fi

"$VENV_DIR/bin/python" "$SCRIPT_DIR/resize.py" "$@"
