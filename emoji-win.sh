#!/bin/bash
#
# Root-level shell script for emoji-win CLI
#
# This script allows running emoji-win commands from the project root directory
# using uv without needing to cd into the converter/ subdirectory.
#
# Usage from project root:
#   ./emoji-win.sh convert input.ttf output.ttf
#   ./emoji-win.sh diagnose font.ttf
#   ./emoji-win.sh analyze font.ttf
#
# Author: jjjuk
# License: MIT

# Get the directory where this script is located (project root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONVERTER_DIR="$SCRIPT_DIR/converter"

# Check if converter directory exists
if [ ! -d "$CONVERTER_DIR" ]; then
    echo "❌ Error: converter/ directory not found."
    echo "Make sure you're running this from the project root."
    exit 1
fi

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH."
    echo "Please install uv or use: python ../emoji-win.py instead"
    exit 1
fi

# Change to converter directory for dependency management, but set environment
# variable so the CLI knows the original working directory
export EMOJI_WIN_PROJECT_ROOT="$SCRIPT_DIR"
cd "$CONVERTER_DIR"

# Run the emoji-win CLI with original arguments (no path manipulation)
exec uv run python -m emoji_win "$@"
