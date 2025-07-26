# emoji-win Monorepo

This monorepo contains tools for getting beautiful Apple emojis working on Windows 11, with a focus on DirectWrite compatibility.

## Project Structure

```
emoji-win/
├── converter/                 # Python font conversion tool
│   ├── emoji_win/             # Main Python package
│   ├── main.py                # Legacy entry point
│   ├── pyproject.toml         # Python project config
│   └── README.md              # Python converter docs
├── directwrite-test/          # .NET DirectWrite testing app (planned)
├── fonts/                     # Shared fonts directory
├── emoji-win.py               # Root-level CLI entry point
├── emoji-win.sh               # Root-level shell script
├── emoji-win.bat              # Root-level Windows batch file
├── README.md                  # Original project README
├── MONOREPO_README.md         # This file
└── LICENSE                    # MIT License
```

## Components

### Python Converter (`converter/`)

The main font conversion tool that transforms Apple Color Emoji fonts to be compatible with Windows 11 and DirectWrite. Features include:

- 🍎 Apple Color Emoji to Windows conversion
- 🔧 DirectWrite compatibility optimizations  
- 📊 Font diagnostics and analysis
- 🎯 Bitmap size optimization
- 📋 Comprehensive font structure analysis

**Quick Start (from project root):**
```bash
# Recommended - shell script with automatic dependency management
./emoji-win.sh convert fonts/AppleColorEmoji.ttf fonts/SegoeUIEmoji.ttf

# Alternative methods from root:
uv run python emoji-win.py convert fonts/AppleColorEmoji.ttf fonts/SegoeUIEmoji.ttf
emoji-win.bat convert fonts/AppleColorEmoji.ttf fonts/SegoeUIEmoji.ttf  # Windows

# Traditional way (requires cd):
cd converter
uv sync
uv run python main.py AppleColorEmoji.ttf SegoeUIEmoji.ttf
```

### .NET DirectWrite Test App (`directwrite-test/`)

*Planned:* A .NET application that uses native DirectWrite libraries to test emoji font rendering and identify compatibility issues. This will help debug why some apps render emoji incorrectly even after conversion.

## DirectWrite Compatibility Issues

The main issue this project addresses is that some native Windows applications using DirectWrite show empty spaces instead of emoji, even when using converted Apple emoji fonts. This happens because:

1. Font claims to support emoji characters (cmap table)
2. DirectWrite finds CBDT/CBLC bitmap data
3. DirectWrite validates bitmap format and fails
4. Instead of fallback, DirectWrite shows empty space

## Development Workflow

1. **Font Conversion**: Use the Python converter to transform Apple fonts
2. **Testing**: Use the .NET DirectWrite test app to validate rendering
3. **Debugging**: Use diagnostic tools to identify specific issues
4. **Iteration**: Refine conversion based on test results

## Getting Started

1. Clone this repository
2. Follow setup instructions in `python-converter/README.md`
3. Download Apple Color Emoji font from: https://github.com/samuelngs/apple-emoji-linux/releases
4. Convert and test the font

## License

MIT License - see LICENSE file for details.

## Author

jjjuk
