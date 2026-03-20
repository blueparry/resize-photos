#!/usr/bin/env bash
# Cross-platform launcher for Photo Resizer (macOS/Linux)
# Usage:
#   ./resize.sh          - opens GUI
#   ./resize.sh --cli    - runs CLI mode (pass args after --cli)

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    "$VENV_DIR/bin/pip" install --quiet Pillow
fi

if [ "$1" = "--cli" ]; then
    shift
    "$VENV_DIR/bin/python" "$SCRIPT_DIR/resize.py" "$@"
else
    "$VENV_DIR/bin/python" "$SCRIPT_DIR/resize_gui.py" "$@"
fi
