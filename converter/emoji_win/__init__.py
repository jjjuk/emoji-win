#!/usr/bin/env python3
"""
emoji-win - Get beautiful Apple emojis on Windows 11

Converts Apple Color Emoji fonts to be fully compatible with Windows 11
and replaces the default Windows emoji font.

Tired of boring Windows emojis? This tool brings Apple's beautiful,
expressive emojis to your Windows machine!

Get Apple Color Emoji fonts from:
https://github.com/samuelngs/apple-emoji-linux/releases

Author: jjjuk
License: MIT
"""

__version__ = "1.0.0"
__author__ = "jjjuk"
__license__ = "MIT"

# Import main functions for easy access
from .font_converter import convert_apple_emoji_to_windows
from .font_diagnostics import diagnose_cbdt_cblc_directwrite_issues, analyze_font_structure
from .bitmap_processor import fix_cbdt_cblc_sizes_for_directwrite
from .cli import main

__all__ = [
    "convert_apple_emoji_to_windows",
    "diagnose_cbdt_cblc_directwrite_issues", 
    "analyze_font_structure",
    "fix_cbdt_cblc_sizes_for_directwrite",
    "main"
]
