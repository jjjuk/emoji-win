# emoji-win Python Converter

Get beautiful Apple emojis on Windows 11! This tool converts Apple Color Emoji fonts to be fully compatible with Windows 11 and replaces the default Windows emoji font.

Tired of boring Windows emojis? This tool brings Apple's beautiful, expressive emojis to your Windows machine!

## Features

- 🍎 Convert Apple Color Emoji fonts for Windows compatibility
- 🔧 DirectWrite compatibility optimizations
- 📊 Font diagnostics and analysis tools
- 🎯 Bitmap size optimization for DirectWrite
- 📋 Comprehensive font structure analysis

## Installation

### Using uv (recommended)

```bash
# Install dependencies
uv sync

# Run the tool
uv run python main.py input.ttf output.ttf
```

### Using pip

```bash
# Install dependencies
pip install -r requirements.txt

# Run the tool
python main.py input.ttf output.ttf
```

## Usage

### Basic Conversion (Legacy Mode)

```bash
python main.py AppleColorEmoji.ttf SegoeUIEmoji.ttf
```

### New CLI Interface

```bash
# Convert font
python -m emoji_win convert AppleColorEmoji.ttf SegoeUIEmoji.ttf

# Diagnose DirectWrite compatibility issues
python -m emoji_win diagnose AppleColorEmoji.ttf

# Analyze font structure
python -m emoji_win analyze AppleColorEmoji.ttf

# Get help
python -m emoji_win --help
```

### As an installed package

```bash
# Install the package
pip install -e .

# Use the command-line tool
emoji-win convert AppleColorEmoji.ttf SegoeUIEmoji.ttf
emoji-win diagnose AppleColorEmoji.ttf
emoji-win analyze AppleColorEmoji.ttf
```

## Getting Apple Color Emoji Font

Download the Apple Color Emoji font from:
https://github.com/samuelngs/apple-emoji-linux/releases

## Installation on Windows

After converting the font:

1. Copy the output font file to your Windows machine
2. Run `windows_font_manager.bat` as Administrator
3. Choose option 1 (INSTALL)
4. Restart Windows for changes to take effect

## Project Structure

```
python-converter/
├── emoji_win/              # Main package
│   ├── __init__.py         # Package initialization
│   ├── __main__.py         # Module entry point
│   ├── cli.py              # Command-line interface
│   ├── font_converter.py   # Core font conversion logic
│   ├── bitmap_processor.py # CBDT/CBLC bitmap processing
│   └── font_diagnostics.py # Font analysis and diagnostics
├── main.py                 # Legacy entry point
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## DirectWrite Compatibility

This tool specifically addresses DirectWrite compatibility issues that cause emoji to appear as empty spaces in native Windows applications. The converter:

- Optimizes bitmap sizes for DirectWrite requirements
- Sets proper typography metrics and flags
- Ensures correct character mapping tables
- Validates bitmap format compatibility

## License

MIT License - see LICENSE file for details.

## Author

jjjuk
