#!/usr/bin/env python3
"""
Font conversion core module for emoji-win

This module contains the main font conversion logic for converting Apple Color Emoji
fonts to be compatible with Windows 11 DirectWrite.

Author: jjjuk
License: MIT
"""

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._n_a_m_e import NameRecord
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
from .bitmap_processor import fix_cbdt_cblc_sizes_for_directwrite


def convert_apple_emoji_to_windows(input_path, output_path, progress_callback=None, quiet=False):
    """Convert AppleColorEmoji.ttf to work as Windows 11 Segoe UI Emoji replacement

    Args:
        input_path: Path to input font
        output_path: Path to output font
        progress_callback: Optional callback function(step, total, description)
        quiet: If True, suppress print statements
    """

    def log(message):
        if not quiet:
            print(message)

    def update_progress(step, total, description):
        if progress_callback:
            progress_callback(step, total, description)

    # Load the Apple emoji font
    update_progress(1, 10, "Loading Apple emoji font...")
    font = TTFont(input_path)

    log(f"Loading Apple emoji font...")
    log(f"Available tables: {sorted(font.keys())}")
    log(f"Font flavor: {font.flavor}")
    log(f"SFNT version: {font.sfntVersion}")

    # Check what type of emoji data we have
    if "sbix" in font:
        log("✓ Found Apple sbix color bitmap table")
    if "COLR" in font and "CPAL" in font:
        log("✓ Found COLR/CPAL color vector table")
    if "CBDT" in font and "CBLC" in font:
        log("✓ Found CBDT/CBLC bitmap table")
    if "glyf" in font:
        log("✓ Found glyf outline table")
    else:
        log("⚠ No glyf outline table - this may cause Windows issues")

    # Check cmap table
    if "cmap" in font:
        cmap = font["cmap"]
        log(f"✓ Found cmap with {len(cmap.tables)} subtables")
        for subtable in cmap.tables:
            char_count = len(subtable.cmap) if hasattr(subtable, "cmap") else 0
            log(
                f"  - Platform {subtable.platformID}, Encoding {subtable.platEncID} ({char_count} chars)"
            )

    # Step 1: Ensure we have a Windows-compatible cmap
    update_progress(2, 10, "Ensuring Windows-compatible character mapping...")
    _ensure_windows_compatible_cmap(font, log)

    # Step 2: Check color table format (Windows prefers COLR/CPAL over CBDT/CBLC)
    update_progress(3, 10, "Analyzing color table format...")
    _check_color_table_format(font, log)

    # Step 3: Check essential tables (informational only)
    update_progress(4, 10, "Checking essential font tables...")
    _check_essential_tables(font, log)

    # Step 4: Replace font names to mimic Segoe UI Emoji with enhanced compatibility
    update_progress(5, 10, "Updating font names for compatibility...")
    _update_font_names(font, log)

    # Step 5: Update OS/2 table for Windows and DirectWrite compatibility
    update_progress(6, 10, "Updating OS/2 table for DirectWrite...")
    _update_os2_table(font, log)

    # Step 6: Update head table
    update_progress(7, 10, "Updating head table...")
    _update_head_table(font, log)

    # Step 7: Update post table for Windows compatibility
    update_progress(8, 10, "Updating post table...")
    _update_post_table(font, log)

    # Step 8: Verify essential font tables
    update_progress(8, 10, "Verifying essential font tables...")
    _verify_essential_tables(font, log)

    # Step 9: Optimize bitmap sizes for DirectWrite compatibility
    if "CBDT" in font and "CBLC" in font:
        update_progress(9, 10, "Optimizing bitmap sizes for DirectWrite...")
        log("\n9. Optimizing bitmap sizes for DirectWrite compatibility...")

        def bitmap_progress_callback(current, total, description):
            # Convert bitmap progress to overall progress (step 9 is 90% of total work)
            bitmap_percent = (current / total) if total > 0 else 0
            overall_progress = 8.5 + (bitmap_percent * 1.0)  # 8.5 to 9.5 out of 10
            update_progress(overall_progress, 10, f"Processing bitmaps: {description}")

        success = fix_cbdt_cblc_sizes_for_directwrite(font, bitmap_progress_callback, quiet)
        if not success:
            log("⚠ Bitmap resizing failed - font may not work properly in DirectWrite apps")

    # Step 10: Save the modified font
    update_progress(9.5, 10, "Saving Windows-compatible font...")
    return _save_font(font, output_path, log)


def _ensure_windows_compatible_cmap(font, log=print):
    """Ensure we have a Windows-compatible character mapping"""
    log("\n1. Ensuring Windows-compatible character mapping...")
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
        log(
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
        log(
            f"✓ Created minimal Windows Unicode BMP cmap with {len(bmp_cmap)} characters"
        )
        log(
            "  (Following Windows Segoe UI Emoji pattern: emoji stay in full Unicode cmap)"
        )

        # Also ensure we have a proper Format 12 subtable for full Unicode support
        _ensure_format12_cmap(cmap, unicode_full_subtable, log)
    elif not has_windows_unicode_bmp:
        log("⚠ No Windows Unicode cmap found - this will cause issues")


def _ensure_format12_cmap(cmap, unicode_full_subtable, log=print):
    """Ensure we have a proper Format 12 subtable for full Unicode support"""
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
        log("⚠ Ensuring Format 12 cmap subtable for full Unicode support...")
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
            log("✓ Converted to Format 12 cmap for better Unicode support")


def _check_color_table_format(font, log=print):
    """Check color table format (Windows prefers COLR/CPAL over CBDT/CBLC)"""
    log("\n2. Analyzing color table format...")
    has_cbdt_cblc = "CBDT" in font and "CBLC" in font
    has_colr_cpal = "COLR" in font and "CPAL" in font

    if has_cbdt_cblc and not has_colr_cpal:
        log("⚠ Font uses CBDT/CBLC (bitmap) - Windows prefers COLR/CPAL (vector)")
        log("  Note: Keeping original bitmap format as COLR/CPAL conversion is complex")
        log("  This may limit emoji rendering in some Windows applications")
    elif has_colr_cpal:
        log("✓ Font already has COLR/CPAL color tables (Windows-preferred)")
    else:
        log("⚠ No color tables found")


def _check_essential_tables(font, log=print):
    """Check essential tables (informational only)"""
    log("\n3. Checking essential font tables...")
    if "glyf" not in font:
        log("⚠ No glyf table - this is expected for CBDT/CBLC emoji fonts")
    else:
        log("✓ glyf table present")


def _update_font_names(font, log=print):
    """Replace font names to mimic Segoe UI Emoji with enhanced compatibility"""
    log("\n4. Updating font names for maximum application compatibility...")
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

    log(f"✓ Added {len(name_table.names)} name records for enhanced compatibility")


def _update_os2_table(font, log=print):
    """Update OS/2 table for Windows and DirectWrite compatibility"""
    log("\n5. Updating OS/2 table for DirectWrite compatibility...")
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

        log("✓ Applied DirectWrite typography metrics (matching Windows Segoe UI Emoji)")
        log("✓ Set USE_TYPO_METRICS flag (critical for DirectWrite)")
        log("✓ Updated Unicode ranges for emoji support")


def _update_head_table(font, log=print):
    """Update head table"""
    log("\n6. Updating head table...")
    if "head" in font:
        head = font["head"]
        head.macStyle = 0


def _update_post_table(font, log=print):
    """Update post table for Windows compatibility"""
    log("\n7. Updating post table...")
    if "post" in font:
        post = font["post"]
        post.formatType = 3.0  # No glyph names stored


def _verify_essential_tables(font, log=print):
    """Verify essential font tables"""
    log("\n8. Verifying essential font tables...")

    essential_tables = ["maxp", "hhea", "hmtx", "cmap", "name", "OS/2", "head", "post"]
    missing_tables = []

    for table_name in essential_tables:
        if table_name in font:
            log(f"✓ {table_name} table present")
        else:
            log(f"⚠ Missing {table_name} table")
            missing_tables.append(table_name)

    if missing_tables:
        log(f"⚠ Missing essential tables: {', '.join(missing_tables)}")
        log("  This may cause compatibility issues with some applications")

    # Check if we have proper bitmap strikes for CBDT/CBLC
    has_cbdt_cblc = "CBDT" in font and "CBLC" in font
    if has_cbdt_cblc:
        cblc = font["CBLC"]
        log(f"✓ CBDT/CBLC bitmap strikes: {len(cblc.strikes)} available")
        for i, strike in enumerate(cblc.strikes):
            # Strike objects have different attribute names, let's be safe
            try:
                if hasattr(strike, 'ppemX') and hasattr(strike, 'ppemY'):
                    log(f"  - Strike {i}: {strike.ppemX}x{strike.ppemY} pixels")
                elif hasattr(strike, 'ppem'):
                    log(f"  - Strike {i}: {strike.ppem} pixels")
                else:
                    log(f"  - Strike {i}: Available")
            except AttributeError:
                log(f"  - Strike {i}: Available")


def _save_font(font, output_path, log=print):
    """Save the modified font"""
    log("\n10. Saving Windows-compatible font...")
    try:
        font.save(output_path)
        log(f"✓ Successfully saved to: {output_path}")

        # Verify the saved font
        test_font = TTFont(output_path)
        glyph_count = test_font["maxp"].numGlyphs
        log(f"✓ Verification: Font has {glyph_count} glyphs")
        test_font.close()

        log("\n✨ Font successfully converted with Windows compatibility improvements!")
        log("\nTo install on Windows:")
        log("1. Copy the output font file to your Windows machine")
        log("2. Run windows_font_manager.bat as Administrator")
        log("3. Choose option 1 (INSTALL)")
        log("4. Restart Windows for changes to take effect")

        return True

    except Exception as e:
        log(f"❌ Error saving font: {e}")
        return False
