#!/usr/bin/env python3
"""
Command-line interface for emoji-win

This module provides the CLI entry point and argument parsing for the emoji-win
font conversion tool.

Author: jjjuk
License: MIT
"""

import sys
import argparse
from pathlib import Path
from fontTools.ttLib import TTFont

from .font_converter import convert_apple_emoji_to_windows
from .font_diagnostics import diagnose_cbdt_cblc_directwrite_issues, analyze_font_structure


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        prog="emoji-win",
        description="Get beautiful Apple emojis on Windows 11 - convert Apple Color Emoji fonts for Windows compatibility",
        epilog="""
Examples:
  %(prog)s convert AppleColorEmoji.ttf SegoeUIEmoji.ttf
  %(prog)s diagnose AppleColorEmoji.ttf
  %(prog)s analyze AppleColorEmoji.ttf

Get AppleColorEmoji.ttf from:
  https://github.com/samuelngs/apple-emoji-linux/releases
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Convert command
    convert_parser = subparsers.add_parser(
        'convert', 
        help='Convert Apple emoji font to Windows-compatible format'
    )
    convert_parser.add_argument(
        'input_font',
        help='Path to input Apple Color Emoji font file (.ttf)'
    )
    convert_parser.add_argument(
        'output_font',
        help='Path for output Windows-compatible font file (.ttf)'
    )
    
    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        'diagnose',
        help='Diagnose DirectWrite compatibility issues in a font'
    )
    diagnose_parser.add_argument(
        'font_file',
        help='Path to font file to diagnose (.ttf)'
    )
    
    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze font structure and compatibility'
    )
    analyze_parser.add_argument(
        'font_file',
        help='Path to font file to analyze (.ttf)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle no command provided (backward compatibility)
    if not args.command:
        if len(sys.argv) == 3:
            # Legacy mode: python main.py input.ttf output.ttf
            return convert_command(sys.argv[1], sys.argv[2])
        else:
            parser.print_help()
            return 1
    
    # Execute the appropriate command
    if args.command == 'convert':
        return convert_command(args.input_font, args.output_font)
    elif args.command == 'diagnose':
        return diagnose_command(args.font_file)
    elif args.command == 'analyze':
        return analyze_command(args.font_file)
    else:
        parser.print_help()
        return 1


def convert_command(input_path, output_path):
    """Execute the convert command"""
    # Validate input file
    input_file = Path(input_path)
    if not input_file.exists():
        print(f"❌ Error: Input font file not found: {input_path}")
        return 1
    
    if not input_file.suffix.lower() == '.ttf':
        print(f"⚠ Warning: Input file doesn't have .ttf extension: {input_path}")
    
    # Validate output path
    output_file = Path(output_path)
    if output_file.exists():
        response = input(f"Output file already exists: {output_path}\nOverwrite? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Operation cancelled.")
            return 1
    
    # Create output directory if it doesn't exist
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    print("emoji-win - Get beautiful Apple emojis on Windows 11")
    print("=" * 60)
    print(f"Input:  {input_path}")
    print(f"Output: {output_path}")
    print("=" * 60)
    
    try:
        success = convert_apple_emoji_to_windows(str(input_file), str(output_file))
        if success:
            print("\n🎉 Conversion completed successfully!")
            return 0
        else:
            print("\n❌ Conversion failed!")
            return 1
    except Exception as e:
        print(f"\n❌ Conversion failed with error: {e}")
        return 1


def diagnose_command(font_path):
    """Execute the diagnose command"""
    # Validate input file
    font_file = Path(font_path)
    if not font_file.exists():
        print(f"❌ Error: Font file not found: {font_path}")
        return 1
    
    print("emoji-win - DirectWrite Compatibility Diagnostics")
    print("=" * 60)
    print(f"Analyzing: {font_path}")
    print("=" * 60)
    
    try:
        font = TTFont(str(font_file))
        diagnose_cbdt_cblc_directwrite_issues(font)
        font.close()
        return 0
    except Exception as e:
        print(f"❌ Diagnostic failed with error: {e}")
        return 1


def analyze_command(font_path):
    """Execute the analyze command"""
    # Validate input file
    font_file = Path(font_path)
    if not font_file.exists():
        print(f"❌ Error: Font file not found: {font_path}")
        return 1
    
    print("emoji-win - Font Structure Analysis")
    print("=" * 60)
    print(f"Analyzing: {font_path}")
    print("=" * 60)
    
    try:
        font = TTFont(str(font_file))
        analyze_font_structure(font)
        font.close()
        return 0
    except Exception as e:
        print(f"❌ Analysis failed with error: {e}")
        return 1


def legacy_main():
    """Legacy main function for backward compatibility"""
    if len(sys.argv) != 3:
        print("emoji-win - Get beautiful Apple emojis on Windows 11")
        print("Usage: python main.py <input_apple_font.ttf> <output_windows_font.ttf>")
        print("\nExample:")
        print("  python main.py AppleColorEmoji.ttf SegoeUIEmoji.ttf")
        print("\nGet AppleColorEmoji.ttf from:")
        print("  https://github.com/samuelngs/apple-emoji-linux/releases")
        print("\nFor more options, use: python -m emoji_win --help")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    success = convert_apple_emoji_to_windows(input_path, output_path)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    sys.exit(main())
