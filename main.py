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
        print(
            "  Note: Keeping original bitmap format as COLR/CPAL conversion is complex"
        )
        print("  This may limit emoji rendering in some Windows applications")
    elif has_colr_cpal:
        print("✓ Font already has COLR/CPAL color tables (Windows-preferred)")
    else:
        print("⚠ No color tables found")

    # Step 3: Create minimal glyf table if missing (Windows requirement)
    print("\n3. Ensuring glyf table exists...")
    if "glyf" not in font:
        print("⚠ Creating minimal glyf table for Windows compatibility...")
        from fontTools.ttLib.tables._g_l_y_f import table__g_l_y_f, Glyph
        from fontTools.ttLib.tables._l_o_c_a import table__l_o_c_a

        # Create glyf table with empty glyphs
        glyf_table = table__g_l_y_f()
        glyf_table.glyphs = {}

        # Get glyph order from the font
        glyph_order = font.getGlyphOrder()

        # Create empty glyphs for all glyphs in the font
        for glyph_name in glyph_order:
            empty_glyph = Glyph()
            empty_glyph.numberOfContours = 0
            empty_glyph.xMin = empty_glyph.yMin = empty_glyph.xMax = (
                empty_glyph.yMax
            ) = 0
            glyf_table.glyphs[glyph_name] = empty_glyph

        # Create corresponding loca table
        loca_table = table__l_o_c_a()
        loca_table.locations = [0] * (len(glyph_order) + 1)

        font["glyf"] = glyf_table
        font["loca"] = loca_table
        print(
            f"✓ Created minimal glyf/loca tables with {len(glyph_order)} empty glyphs"
        )
    else:
        print("✓ glyf table already exists")

    # Step 4: Replace font names to mimic Segoe UI Emoji
    print("\n4. Updating font names...")
    name_table = font["name"]
    name_table.names = []

    windows_names = [
        (1, "Segoe UI Emoji"),
        (2, "Regular"),
        (3, "Microsoft:Segoe UI Emoji Regular:2023"),
        (4, "Segoe UI Emoji"),
        (5, "Version 1.00"),
        (6, "SegoeUIEmoji"),
        (16, "Segoe UI Emoji"),
        (17, "Regular"),
    ]

    for name_id, name_string in windows_names:
        record = NameRecord()
        record.nameID = name_id
        record.platformID = 3
        record.platEncID = 1
        record.langID = 0x409
        record.string = name_string
        name_table.names.append(record)

    # Step 5: Update OS/2 table for Windows compatibility
    print("\n5. Updating OS/2 table...")
    if "OS/2" in font:
        os2 = font["OS/2"]
        os2.version = 4
        os2.usWeightClass = 400
        os2.usWidthClass = 5
        os2.fsSelection = 64
        os2.fsType = 0
        os2.sFamilyClass = 0

        # Set Unicode ranges to indicate emoji support
        os2.ulUnicodeRange1 = 0x00000001  # Basic Latin
        os2.ulUnicodeRange2 = 0x00000000
        os2.ulUnicodeRange3 = 0x00000000
        os2.ulUnicodeRange4 = 0x00000000

        # Update PANOSE
        panose = os2.panose
        panose.bFamilyType = 5
        panose.bSerifStyle = 0
        panose.bWeight = 5
        panose.bProportion = 0
        panose.bContrast = 0
        panose.bStrokeVariation = 0
        panose.bArmStyle = 0
        panose.bLetterform = 0
        panose.bMidline = 0
        panose.bXHeight = 0

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

    # Step 8: Save the modified font
    print("\n8. Saving Windows-compatible font...")
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

        return True

    except Exception as e:
        print(f"✗ Error saving font: {e}")
        return False


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
