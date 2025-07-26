#!/bin/bash
# emoji-win - Get beautiful Apple emojis on Windows 11
# Usage: ./convert.sh [input_font.ttf] [output_font.ttf]

set -e

echo "🍎 emoji-win - Get beautiful Apple emojis on Windows 11"
echo "======================================================="

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Default file paths
INPUT_FONT="${1:-fonts/AppleColorEmoji.ttf}"
OUTPUT_FONT="${2:-fonts/AppleColorEmojiForWindows.ttf}"

echo "📥 Input font: $INPUT_FONT"
echo "📤 Output font: $OUTPUT_FONT"
echo

# Check if input font exists
if [ ! -f "$INPUT_FONT" ]; then
    echo "❌ Input font not found: $INPUT_FONT"
    echo
    echo "📋 To get AppleColorEmoji.ttf:"
    echo "1. Visit: https://github.com/samuelngs/apple-emoji-linux/releases"
    echo "2. Download the latest AppleColorEmoji.ttf"
    echo "3. Place it in the fonts/ directory"
    echo
    echo "📋 For best DirectWrite compatibility (optional):"
    echo "1. Copy seguiemj.ttf from C:\\Windows\\Fonts\\ on any Windows system"
    echo "2. Place it as fonts/seguiemj.ttf"
    echo "3. This enables COLR/CPAL support for Windows Terminal, Telegram Desktop"
    echo
    echo "Or specify a different path:"
    echo "  ./convert.sh /path/to/your/AppleColorEmoji.ttf output.ttf"
    exit 1
fi

# Create output directory if it doesn't exist
OUTPUT_DIR=$(dirname "$OUTPUT_FONT")
mkdir -p "$OUTPUT_DIR"

echo "🔄 Converting font (dependencies handled automatically)..."
echo

# Run the converter with uv
uv run python main.py "$INPUT_FONT" "$OUTPUT_FONT"

echo
echo "✅ Conversion completed!"
echo "📁 Output saved to: $OUTPUT_FONT"
echo
echo "📋 Next steps for Windows installation:"
echo "1. Copy $OUTPUT_FONT and windows_font_manager.bat to your Windows machine"
echo "2. Create a 'fonts' folder next to windows_font_manager.bat"
echo "3. Place $OUTPUT_FONT in the fonts folder"
echo "4. Double-click windows_font_manager.bat (auto-elevates to admin)"
echo "5. Choose option 1 (INSTALL) - auto-detects font from fonts folder"
echo "6. Restart Windows"
echo "7. To restore later, run the batch script and choose option 2 (RESTORE)"
echo
echo "🎉 Enjoy your Apple emojis on Windows!"
