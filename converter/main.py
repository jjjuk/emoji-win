#!/usr/bin/env python3
"""
emoji-win - Get beautiful Apple emojis on Windows 11

Main entry point for the emoji-win font conversion tool.
This file maintains backward compatibility with the original main.py interface.

For the new modular CLI interface, use:
  python -m emoji_win --help

Author: jjjuk
License: MIT
"""

from emoji_win.cli import legacy_main

if __name__ == "__main__":
    legacy_main()
