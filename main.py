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

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import sys


def convert_apple_emoji_to_windows(input_path, output_path):
    """Convert AppleColorEmoji.ttf to work as Windows 11 Segoe UI Emoji replacement"""

    # Load the Apple emoji font
    font = TTFont(input_path)

    print(f"Loading Apple emoji font...")
    print(f"Available tables: {sorted(font.keys())}")
    print(f"Font flavor: {font.flavor}")
    print(f"SFNT version: {font.sfntVersion}")

    # Check what type of emoji data we have
    if "sbix" in font:
        print("✓ Found Apple sbix color bitmap table")
    if "COLR" in font and "CPAL" in font:
        print("✓ Found COLR/CPAL color vector table")
    if "CBDT" in font and "CBLC" in font:
        print("✓ Found CBDT/CBLC bitmap table")
    if "glyf" in font:
        print("✓ Found glyf outline table")
    else:
        print("⚠ No glyf outline table - this may cause Windows issues")

    # Check cmap table
    if "cmap" in font:
        cmap = font["cmap"]
        print(f"✓ Found cmap with {len(cmap.tables)} subtables")
        for subtable in cmap.tables:
            char_count = len(subtable.cmap) if hasattr(subtable, "cmap") else 0
            print(
                f"  - Platform {subtable.platformID}, Encoding {subtable.platEncID} ({char_count} chars)"
            )

    # Step 1: Ensure we have a Windows-compatible cmap
    print("\n1. Ensuring Windows-compatible character mapping...")
    cmap = font["cmap"]
    has_windows_unicode_bmp = False
    has_windows_unicode_full = False
    unicode_full_subtable = None

    for subtable in cmap.tables:
        if subtable.platformID == 3 and subtable.platEncID == 1:
            has_windows_unicode_bmp = True
        elif subtable.platformID == 3 and subtable.platEncID == 10:
            has_windows_unicode_full = True
            unicode_full_subtable = subtable

    if not has_windows_unicode_bmp and has_windows_unicode_full:
        print(
            "⚠ Missing Windows Unicode BMP cmap - creating minimal one like Windows Segoe UI Emoji..."
        )

        # Create a minimal BMP subtable (Windows Segoe UI Emoji has 716 BMP chars, mostly text)
        # We'll only include actual BMP characters, not try to map SMP emoji
        bmp_subtable = CmapSubtable.newSubtable(4)  # Format 4 for BMP
        bmp_subtable.platformID = 3
        bmp_subtable.platEncID = 1
        bmp_subtable.language = 0

        bmp_cmap = {}

        if unicode_full_subtable and hasattr(unicode_full_subtable, "cmap"):
            # Only add actual BMP characters (like Windows does)
            for codepoint, glyph_name in unicode_full_subtable.cmap.items():
                if 0x0000 <= codepoint <= 0xFFFF:
                    bmp_cmap[codepoint] = glyph_name

        bmp_subtable.cmap = bmp_cmap
        cmap.tables.insert(1, bmp_subtable)  # Insert after Unicode subtable
        print(
            f"✓ Created minimal Windows Unicode BMP cmap with {len(bmp_cmap)} characters"
        )
        print(
            "  (Following Windows Segoe UI Emoji pattern: emoji stay in full Unicode cmap)"
        )

        # Also ensure we have a proper Format 12 subtable for full Unicode support
        has_format12 = False
        for subtable in cmap.tables:
            if (
                subtable.platformID == 3
                and subtable.platEncID == 10
                and subtable.format == 12
            ):
                has_format12 = True
                break

        if not has_format12 and unicode_full_subtable:
            print("⚠ Ensuring Format 12 cmap subtable for full Unicode support...")
            # Convert existing subtable to Format 12 if it isn't already
            if unicode_full_subtable.format != 12:
                format12_subtable = CmapSubtable.newSubtable(12)
                format12_subtable.platformID = 3
                format12_subtable.platEncID = 10
                format12_subtable.language = 0
                format12_subtable.cmap = unicode_full_subtable.cmap.copy()

                # Replace the existing subtable
                for i, subtable in enumerate(cmap.tables):
                    if subtable.platformID == 3 and subtable.platEncID == 10:
                        cmap.tables[i] = format12_subtable
                        break
                print("✓ Converted to Format 12 cmap for better Unicode support")
    elif not has_windows_unicode_bmp:
        print("⚠ No Windows Unicode cmap found - this will cause issues")

    # Step 2: Check color table format (Windows prefers COLR/CPAL over CBDT/CBLC)
    print("\n2. Analyzing color table format...")
    has_cbdt_cblc = "CBDT" in font and "CBLC" in font
    has_colr_cpal = "COLR" in font and "CPAL" in font

    if has_cbdt_cblc and not has_colr_cpal:
        print("⚠ Font uses CBDT/CBLC (bitmap) - Windows prefers COLR/CPAL (vector)")
        print("  Note: Keeping original bitmap format as COLR/CPAL conversion is complex")
        print("  This may limit emoji rendering in some Windows applications")
    elif has_colr_cpal:
        print("✓ Font already has COLR/CPAL color tables (Windows-preferred)")
    else:
        print("⚠ No color tables found")

    # Step 3: Check essential tables (informational only)
    print("\n3. Checking essential font tables...")
    if "glyf" not in font:
        print("⚠ No glyf table - this is expected for CBDT/CBLC emoji fonts")
    else:
        print("✓ glyf table present")

    # Step 4: Replace font names to mimic Segoe UI Emoji with enhanced compatibility
    print("\n4. Updating font names for maximum application compatibility...")
    name_table = font["name"]
    name_table.names = []

    # Enhanced name table with multiple platform/encoding combinations for better compatibility
    windows_names = [
        (1, "Segoe UI Emoji"),      # Font Family name
        (2, "Regular"),             # Font Subfamily name
        (3, "Microsoft:Segoe UI Emoji Regular:2023"),  # Unique font identifier
        (4, "Segoe UI Emoji"),      # Full font name
        (5, "Version 1.00"),        # Version string
        (6, "SegoeUIEmoji"),        # PostScript name
        (16, "Segoe UI Emoji"),     # Typographic Family name
        (17, "Regular"),            # Typographic Subfamily name
        (21, "Segoe UI Emoji"),     # WWS Family Name
        (22, "Regular"),            # WWS Subfamily Name
    ]

    # Add names for multiple platform/encoding combinations for broader compatibility
    platforms = [
        (3, 1, 0x409),   # Microsoft Unicode BMP (most common)
        (3, 10, 0x409),  # Microsoft Unicode full repertoire
        (1, 0, 0),       # Apple Unicode (for cross-platform apps)
    ]

    for platform_id, plat_enc_id, lang_id in platforms:
        for name_id, name_string in windows_names:
            record = NameRecord()
            record.nameID = name_id
            record.platformID = platform_id
            record.platEncID = plat_enc_id
            record.langID = lang_id
            record.string = name_string
            name_table.names.append(record)

    print(f"✓ Added {len(name_table.names)} name records for enhanced compatibility")

    # Step 5: Update OS/2 table for Windows and DirectWrite compatibility
    print("\n5. Updating OS/2 table for DirectWrite compatibility...")
    if "OS/2" in font:
        os2 = font["OS/2"]
        os2.version = 4
        os2.usWeightClass = 400
        os2.usWidthClass = 5
        os2.fsType = 0
        os2.sFamilyClass = 0

        # CRITICAL DirectWrite fixes - Typography metrics matching Windows Segoe UI Emoji
        os2.sTypoAscender = 1069
        os2.sTypoDescender = -293
        os2.sTypoLineGap = 0

        # CRITICAL: USE_TYPO_METRICS flag (bit 7) - DirectWrite requires this
        os2.fsSelection = 64 | (1 << 7)  # Regular style + USE_TYPO_METRICS

        # Set proper character range for emoji
        os2.usFirstCharIndex = 0x20  # Space character
        os2.usLastCharIndex = 0x1F6FF  # Last emoji in range

        # DirectWrite Unicode ranges for emoji support
        os2.ulUnicodeRange1 = 0x00000001 | (1 << 25)  # Basic Latin + Latin-1 Supplement
        os2.ulUnicodeRange2 = (1 << (57 - 32)) | (1 << (58 - 32)) | (1 << (59 - 32))  # Emoji ranges
        os2.ulUnicodeRange3 = 0x00000000
        os2.ulUnicodeRange4 = 0x00000000

        # Update PANOSE for emoji font
        panose = os2.panose
        panose.bFamilyType = 5  # Decorative
        panose.bSerifStyle = 0
        panose.bWeight = 5  # Medium
        panose.bProportion = 0
        panose.bContrast = 0
        panose.bStrokeVariation = 0
        panose.bArmStyle = 0
        panose.bLetterform = 0
        panose.bMidline = 0
        panose.bXHeight = 0

        print("✓ Applied DirectWrite typography metrics (matching Windows Segoe UI Emoji)")
        print("✓ Set USE_TYPO_METRICS flag (critical for DirectWrite)")
        print("✓ Updated Unicode ranges for emoji support")

    # Step 6: Update head table
    print("\n6. Updating head table...")
    if "head" in font:
        head = font["head"]
        head.macStyle = 0

    # Step 7: Update post table for Windows compatibility
    print("\n7. Updating post table...")
    if "post" in font:
        post = font["post"]
        post.formatType = 3.0  # No glyph names stored

    # Step 8: Verify essential font tables
    print("\n8. Verifying essential font tables...")

    essential_tables = ["maxp", "hhea", "hmtx", "cmap", "name", "OS/2", "head", "post"]
    missing_tables = []

    for table_name in essential_tables:
        if table_name in font:
            print(f"✓ {table_name} table present")
        else:
            print(f"⚠ Missing {table_name} table")
            missing_tables.append(table_name)

    if missing_tables:
        print(f"⚠ Missing essential tables: {', '.join(missing_tables)}")
        print("  This may cause compatibility issues with some applications")

    # Check if we have proper bitmap strikes for CBDT/CBLC
    if has_cbdt_cblc:
        cblc = font["CBLC"]
        print(f"✓ CBDT/CBLC bitmap strikes: {len(cblc.strikes)} available")
        for i, strike in enumerate(cblc.strikes):
            # Strike objects have different attribute names, let's be safe
            try:
                if hasattr(strike, 'ppemX') and hasattr(strike, 'ppemY'):
                    print(f"  - Strike {i}: {strike.ppemX}x{strike.ppemY} pixels")
                elif hasattr(strike, 'ppem'):
                    print(f"  - Strike {i}: {strike.ppem} pixels")
                else:
                    print(f"  - Strike {i}: Available")
            except AttributeError:
                print(f"  - Strike {i}: Available")

    # Step 10: Save the modified font
    print("\n10. Saving Windows-compatible font...")
    try:
        font.save(output_path)
        print(f"✓ Successfully saved to: {output_path}")

        # Verify the saved font
        test_font = TTFont(output_path)
        glyph_count = test_font["maxp"].numGlyphs
        print(f"✓ Verification: Font has {glyph_count} glyphs")
        print(f"✓ Saved font tables: {sorted(test_font.keys())}")
        test_font.close()

        print("\n🎉 SUCCESS! Your font is now Windows-compatible!")
        print("\nTo install on Windows:")
        print("1. Copy the output font file to your Windows machine")
        print(
            "2. Right-click the font file and select 'Install for all users' (requires admin)"
        )
        print("3. Restart applications to use the new emoji font")
        print(
            "\n✨ Font successfully converted with Windows compatibility improvements!"
        )

        # Create DirectWrite analysis report
        create_directwrite_analysis(font, output_path)

        return True

    except Exception as e:
        print(f"✗ Error saving font: {e}")
        return False


def create_directwrite_analysis(font, output_path):
    """Create analysis report for DirectWrite compatibility debugging"""
    report_path = output_path.replace('.ttf', '_directwrite_analysis.txt')

    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=== DIRECTWRITE COMPATIBILITY ANALYSIS ===\n\n")

            # OS/2 table analysis
            if "OS/2" in font:
                os2 = font["OS/2"]
                f.write("OS/2 TABLE ANALYSIS:\n")
                f.write(f"  Version: {os2.version}\n")
                f.write(f"  fsSelection: {bin(os2.fsSelection)} (USE_TYPO_METRICS: {'YES' if os2.fsSelection & (1 << 7) else 'NO'})\n")
                f.write(f"  Typography metrics: Ascender={os2.sTypoAscender}, Descender={os2.sTypoDescender}, LineGap={os2.sTypoLineGap}\n")
                f.write(f"  Weight class: {os2.usWeightClass}\n")
                f.write(f"  Unicode ranges: {hex(os2.ulUnicodeRange1)}, {hex(os2.ulUnicodeRange2)}\n\n")

            # CMAP analysis
            if "cmap" in font:
                cmap = font["cmap"]
                f.write("CMAP TABLE ANALYSIS:\n")
                f.write(f"  Total subtables: {len(cmap.tables)}\n")
                for i, subtable in enumerate(cmap.tables):
                    char_count = len(subtable.cmap) if hasattr(subtable, "cmap") else 0
                    f.write(f"  Subtable {i}: Platform {subtable.platformID}, Encoding {subtable.platEncID}, Format {subtable.format}, Chars: {char_count}\n")
                f.write("\n")

            # Color table analysis
            color_formats = []
            if "CBDT" in font and "CBLC" in font:
                color_formats.append("CBDT/CBLC (bitmap)")
            if "COLR" in font and "CPAL" in font:
                color_formats.append("COLR/CPAL (vector)")
            if "sbix" in font:
                color_formats.append("sbix (Apple bitmap)")

            f.write("COLOR FORMAT ANALYSIS:\n")
            f.write(f"  Available formats: {', '.join(color_formats) if color_formats else 'None detected'}\n")

            if "CBLC" in font:
                cblc = font["CBLC"]
                f.write(f"  CBDT/CBLC strikes: {len(cblc.strikes)}\n")
                for i, strike in enumerate(cblc.strikes):
                    try:
                        if hasattr(strike, 'ppemX') and hasattr(strike, 'ppemY'):
                            f.write(f"    Strike {i}: {strike.ppemX}x{strike.ppemY} pixels\n")
                        elif hasattr(strike, 'ppem'):
                            f.write(f"    Strike {i}: {strike.ppem} pixels\n")
                        else:
                            f.write(f"    Strike {i}: Available\n")
                    except:
                        f.write(f"    Strike {i}: Available\n")
            f.write("\n")

            # Essential tables check
            essential_tables = ["maxp", "hhea", "hmtx", "cmap", "name", "OS/2", "head", "post"]
            f.write("ESSENTIAL TABLES CHECK:\n")
            for table_name in essential_tables:
                status = "✓ Present" if table_name in font else "✗ Missing"
                f.write(f"  {table_name}: {status}\n")

            f.write("\n=== DIRECTWRITE TROUBLESHOOTING NOTES ===\n")
            f.write("If DirectWrite apps (Windows Terminal, Telegram, VS Code) don't show emojis:\n")
            f.write("1. Check USE_TYPO_METRICS flag is set (should be YES above)\n")
            f.write("2. Verify typography metrics match Windows Segoe UI Emoji\n")
            f.write("3. Ensure CBDT/CBLC bitmap strikes are available\n")
            f.write("4. Check that cmap has both BMP (3,1) and full Unicode (3,10) subtables\n")
            f.write("5. Restart Windows after font installation\n")

        print(f"✓ DirectWrite analysis saved to: {report_path}")

    except Exception as e:
        print(f"⚠ Could not create analysis report: {e}")


def main():
    """Main CLI entry point"""
    if len(sys.argv) != 3:
        print("emoji-win - Get beautiful Apple emojis on Windows 11")
        print("Usage: python main.py <input_apple_font.ttf> <output_windows_font.ttf>")
        print("\nExample:")
        print("  python main.py AppleColorEmoji.ttf SegoeUIEmoji.ttf")
        print("\nGet AppleColorEmoji.ttf from:")
        print("  https://github.com/samuelngs/apple-emoji-linux/releases")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    success = convert_apple_emoji_to_windows(input_path, output_path)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
