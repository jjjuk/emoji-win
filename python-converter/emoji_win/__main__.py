#!/usr/bin/env python3
"""
Main entry point for emoji_win package when run as a module.

Usage: python -m emoji_win [command] [args...]
"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main())
