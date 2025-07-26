#!/usr/bin/env python3
"""
Root-level entry point for emoji-win CLI

This script allows running emoji-win commands from the project root directory
without needing to cd into the converter/ subdirectory.

Usage from project root:
  python emoji-win.py convert input.ttf output.ttf
  python emoji-win.py diagnose font.ttf
  python emoji-win.py analyze font.ttf

Note: This script requires dependencies to be installed.
For automatic dependency management, use ./emoji-win.sh instead.

Author: jjjuk
License: MIT
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main entry point that delegates to uv in the converter directory"""

    # Get paths
    script_dir = Path(__file__).parent
    converter_dir = script_dir / "converter"

    # Check if converter directory exists
    if not converter_dir.exists():
        print("❌ Error: converter/ directory not found.")
        print("Make sure you're running this from the project root.")
        return 1

    # Build the uv command - pass arguments as-is, no path manipulation
    cmd = ["uv", "run", "python", "-m", "emoji_win"] + sys.argv[1:]

    try:
        # Run uv from the project root directory (not converter)
        # This way all paths work naturally from the user's perspective
        result = subprocess.run(
            cmd,
            cwd=script_dir,  # Run from project root
            env={**subprocess.os.environ, "PYTHONPATH": str(converter_dir)},  # Add converter to Python path
            check=False  # Don't raise exception on non-zero exit
        )
        return result.returncode

    except FileNotFoundError:
        print("❌ Error: uv is not installed or not in PATH.")
        print("Please install uv or run commands directly from converter/ directory:")
        print(f"  cd converter && python -m emoji_win {' '.join(sys.argv[1:])}")
        return 1
    except Exception as e:
        print(f"❌ Error running emoji-win: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
