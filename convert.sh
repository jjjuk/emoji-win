#!/bin/bash
# Apple Color Emoji to Windows Converter - Easy Wrapper Script
# Usage: ./convert.sh [input_font.ttf] [output_font.ttf]

set -e

echo "🍎 Apple Color Emoji to Windows Converter"
echo "=========================================="

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install uv first:"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

# Default file paths
INPUT_FONT="${1:-fonts/AppleColorEmoji.ttf}"
OUTPUT_FONT="${2:-fonts/SegoeUIEmoji.ttf}"

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
echo "1. Copy $OUTPUT_FONT to your Windows machine"
echo "2. Run windows_font_manager.bat as Administrator"
echo "3. Choose option 1 (BACKUP) - this will backup original + install converted font"
echo "4. Restart Windows"
echo "5. To restore later, run the batch script and choose option 2 (RESTORE)"
echo
echo "🎉 Enjoy your Apple emojis on Windows!"
