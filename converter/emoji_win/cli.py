#!/usr/bin/env python3
"""
Command-line interface for emoji-win

This module provides the CLI entry point and argument parsing for the emoji-win
font conversion tool with beautiful interactive features.

Author: jjjuk
License: MIT
"""

import sys
import os
import argparse
from pathlib import Path
from fontTools.ttLib import TTFont

try:
    from rich.console import Console
    from rich import print as rprint
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    rprint = print

from .font_converter import convert_apple_emoji_to_windows
from .font_diagnostics import diagnose_cbdt_cblc_directwrite_issues, analyze_font_structure

# Import interactive CLI if available
try:
    from .interactive_cli import InteractiveCLI
    INTERACTIVE_AVAILABLE = True
except ImportError:
    INTERACTIVE_AVAILABLE = False


def main():
    """Main CLI entry point"""

    # Handle working directory - if called from root via shell script,
    # change back to project root for natural path handling
    project_root = os.environ.get('EMOJI_WIN_PROJECT_ROOT')
    if project_root and Path(project_root).exists():
        os.chdir(project_root)

    parser = argparse.ArgumentParser(
        prog="emoji-win",
        description="Get beautiful Apple emojis on Windows 11 - convert Apple Color Emoji fonts for Windows compatibility",
        epilog="""
Examples:
  %(prog)s                                              # Interactive mode
  %(prog)s convert AppleColorEmoji.ttf SegoeUIEmoji.ttf # Direct conversion
  %(prog)s diagnose AppleColorEmoji.ttf                 # Diagnose font
  %(prog)s analyze AppleColorEmoji.ttf                  # Analyze font

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
        nargs='?',  # Make optional for interactive mode
        help='Path to input Apple Color Emoji font file (.ttf)'
    )
    convert_parser.add_argument(
        'output_font',
        nargs='?',  # Make optional for interactive mode
        help='Path for output Windows-compatible font file (.ttf)'
    )

    # Diagnose command
    diagnose_parser = subparsers.add_parser(
        'diagnose',
        help='Diagnose DirectWrite compatibility issues in a font'
    )
    diagnose_parser.add_argument(
        'font_file',
        nargs='?',  # Make optional for interactive mode
        help='Path to font file to diagnose (.ttf)'
    )

    # Analyze command
    analyze_parser = subparsers.add_parser(
        'analyze',
        help='Analyze font structure and compatibility'
    )
    analyze_parser.add_argument(
        'font_file',
        nargs='?',  # Make optional for interactive mode
        help='Path to font file to analyze (.ttf)'
    )

    # Parse arguments
    args = parser.parse_args()

    # Handle no command provided - enter interactive mode
    if not args.command:
        if len(sys.argv) == 3:
            # Legacy mode: python main.py input.ttf output.ttf
            return convert_command(sys.argv[1], sys.argv[2])
        elif len(sys.argv) == 1:
            # Interactive mode
            return interactive_mode()
        else:
            parser.print_help()
            return 1

    # Execute the appropriate command
    if args.command == 'convert':
        if args.input_font and args.output_font:
            return convert_command(args.input_font, args.output_font)
        else:
            return interactive_convert()
    elif args.command == 'diagnose':
        if args.font_file:
            return diagnose_command(args.font_file)
        else:
            return interactive_diagnose()
    elif args.command == 'analyze':
        if args.font_file:
            return analyze_command(args.font_file)
        else:
            return interactive_analyze()
    else:
        parser.print_help()
        return 1


def interactive_mode():
    """Enter interactive mode for command selection"""
    if not INTERACTIVE_AVAILABLE:
        rprint("[red]❌ Interactive mode requires additional packages.[/red]")
        rprint("[dim]Please run: uv sync[/dim]")
        return 1

    try:
        import inquirer

        questions = [
            inquirer.List(
                'action',
                message="What would you like to do?",
                choices=[
                    'Convert font (Apple → Windows)',
                    'Analyze font structure',
                    'Diagnose DirectWrite issues',
                    'Exit'
                ],
                carousel=True
            )
        ]

        answers = inquirer.prompt(questions)
        if not answers or answers['action'] == 'Exit':
            return 0

        cli = InteractiveCLI()

        if answers['action'] == 'Convert font (Apple → Windows)':
            return 0 if cli.interactive_convert() else 1
        elif answers['action'] == 'Analyze font structure':
            return 0 if cli.interactive_analyze() else 1
        elif answers['action'] == 'Diagnose DirectWrite issues':
            return 0 if cli.interactive_diagnose() else 1

    except (KeyboardInterrupt, EOFError):
        rprint("\n[yellow]Goodbye! 👋[/yellow]")
        return 0
    except Exception as e:
        rprint(f"[red]❌ Error in interactive mode: {e}[/red]")
        return 1


def interactive_convert():
    """Interactive convert mode"""
    if not INTERACTIVE_AVAILABLE:
        rprint("[red]❌ Interactive mode requires additional packages.[/red]")
        rprint("[dim]Please run: uv sync[/dim]")
        return 1

    cli = InteractiveCLI()
    return 0 if cli.interactive_convert() else 1


def interactive_analyze():
    """Interactive analyze mode"""
    if not INTERACTIVE_AVAILABLE:
        rprint("[red]❌ Interactive mode requires additional packages.[/red]")
        rprint("[dim]Please run: uv sync[/dim]")
        return 1

    cli = InteractiveCLI()
    return 0 if cli.interactive_analyze() else 1


def interactive_diagnose():
    """Interactive diagnose mode"""
    if not INTERACTIVE_AVAILABLE:
        rprint("[red]❌ Interactive mode requires additional packages.[/red]")
        rprint("[dim]Please run: uv sync[/dim]")
        return 1

    cli = InteractiveCLI()
    return 0 if cli.interactive_diagnose() else 1


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
