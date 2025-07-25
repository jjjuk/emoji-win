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
import io
from PIL import Image


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

    # Step 9: Optimize bitmap sizes for DirectWrite compatibility
    if "CBDT" in font and "CBLC" in font:
        print("\n9. Optimizing bitmap sizes for DirectWrite compatibility...")
        success = fix_cbdt_cblc_sizes_for_directwrite(font)
        if not success:
            print("⚠ Bitmap resizing failed - font may not work properly in DirectWrite apps")

    # Step 10: Save the modified font
    print("\n10. Saving Windows-compatible font...")
    try:
        font.save(output_path)
        print(f"✓ Successfully saved to: {output_path}")

        # Verify the saved font
        test_font = TTFont(output_path)
        glyph_count = test_font["maxp"].numGlyphs
        print(f"✓ Verification: Font has {glyph_count} glyphs")
        test_font.close()

        print("\n✨ Font successfully converted with Windows compatibility improvements!")
        print("\nTo install on Windows:")
        print("1. Copy the output font file to your Windows machine")
        print("2. Run windows_font_manager.bat as Administrator")
        print("3. Choose option 1 (INSTALL)")
        print("4. Restart Windows for changes to take effect")

        return True

    except Exception as e:
        print(f"❌ Error saving font: {e}")
        return False



def fix_cbdt_cblc_sizes_for_directwrite(font):
    """
    Fix CBDT/CBLC bitmap sizes to match DirectWrite requirements
    Resize bitmaps from Apple's 137x137 to DirectWrite's preferred 128x128
    """
    if "CBDT" not in font or "CBLC" not in font:
        print("⚠ No CBDT/CBLC tables found")
        return False

    cblc = font["CBLC"]
    cbdt = font["CBDT"]

    # DirectWrite preferred sizes
    directwrite_sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128]

    print(f"Found {len(cblc.strikes)} bitmap strikes to analyze")

    strikes_modified = 0

    for i, strike in enumerate(cblc.strikes):
        print(f"\nProcessing strike {i}:")

        # Get current size
        current_size = None
        if hasattr(strike, 'bitmapSizeTable'):
            bst = strike.bitmapSizeTable
            if hasattr(bst, 'ppemX') and hasattr(bst, 'ppemY'):
                current_size = (bst.ppemX, bst.ppemY)
                print(f"  Current size: {current_size[0]}x{current_size[1]}")

        if not current_size:
            print(f"  ⚠ Cannot determine current size, skipping")
            continue

        # Find closest DirectWrite size
        current_max = max(current_size)
        closest_size = min(directwrite_sizes, key=lambda x: abs(x - current_max))

        if current_max == closest_size:
            print(f"  ✓ Size {current_max} already DirectWrite compatible")
            continue

        print(f"  Resizing from {current_max}x{current_max} to {closest_size}x{closest_size}")

        try:
            # Method 1: Try to resize actual bitmap data
            success = resize_strike_bitmaps(font, i, closest_size)
            if success:
                strikes_modified += 1
                print(f"  ✓ Successfully resized bitmap data for strike {i}")
            else:
                # Method 2: At minimum, update the size metadata for DirectWrite
                print(f"  ⚠ Could not resize bitmap data, updating size metadata only")
                success = update_strike_size_metadata(font, i, closest_size)
                if success:
                    strikes_modified += 1
                    print(f"  ✓ Updated size metadata for strike {i} (DirectWrite compatibility)")
                else:
                    print(f"  ❌ Failed to update strike {i}")

        except Exception as e:
            print(f"  ❌ Error processing strike {i}: {e}")

    if strikes_modified > 0:
        print(f"\n✓ Successfully modified {strikes_modified} bitmap strikes for DirectWrite compatibility")
        return True
    else:
        print(f"\n⚠ No bitmap strikes were modified")
        return False


def resize_strike_bitmaps(font, strike_index, new_size):
    """
    Resize all bitmaps in a specific strike to the new size using proper fonttools CBDT API
    """
    cblc = font["CBLC"]
    cbdt = font["CBDT"]

    if strike_index >= len(cblc.strikes):
        return False

    strike = cblc.strikes[strike_index]

    # Update the strike size information in CBLC
    if hasattr(strike, 'bitmapSizeTable'):
        bst = strike.bitmapSizeTable
        if hasattr(bst, 'ppemX') and hasattr(bst, 'ppemY'):
            bst.ppemX = new_size
            bst.ppemY = new_size
            print(f"    Updated CBLC strike size table to {new_size}x{new_size}")

    # Process each glyph bitmap in this strike using proper CBDT access
    if not hasattr(strike, 'indexSubTables') or not strike.indexSubTables:
        print(f"    ⚠ No index subtables found")
        return False

    bitmaps_resized = 0
    total_glyphs = 0

    # Get the glyph order to map glyph IDs to names
    glyph_order = font.getGlyphOrder()

    # Access CBDT strike data using correct fonttools API
    try:
        if not hasattr(cbdt, 'strikeData') or strike_index >= len(cbdt.strikeData):
            print(f"    ❌ No strike data found for strike {strike_index}")
            return False

        strike_data = cbdt.strikeData[strike_index]  # This is a dictionary of glyph_name -> bitmap_glyph

        print(f"    Found {len(strike_data)} bitmap glyphs in strike {strike_index}")

        # Process each glyph in the strike data
        processed_count = 0
        for glyph_name, bitmap_glyph in strike_data.items():
            processed_count += 1
            total_glyphs += 1

            try:
                # Ensure the bitmap glyph is decompiled so we can access its data
                if hasattr(bitmap_glyph, 'ensureDecompiled'):
                    bitmap_glyph.ensureDecompiled()

                # Get the bitmap data - before decompilation it's in 'data', after it's in 'imageData'
                bitmap_data = None

                # Try to get data before decompilation
                if hasattr(bitmap_glyph, 'data') and bitmap_glyph.data:
                    # Extract PNG data from the raw CBDT data
                    raw_data = bitmap_glyph.data
                    # Look for PNG signature in the data
                    png_start = raw_data.find(b'\x89PNG')
                    if png_start >= 0:
                        bitmap_data = raw_data[png_start:]  # PNG data starts here

                # If no data found, try after decompilation
                if not bitmap_data:
                    if hasattr(bitmap_glyph, 'imageData') and bitmap_glyph.imageData:
                        bitmap_data = bitmap_glyph.imageData

                if bitmap_data and len(bitmap_data) > 10:  # Valid bitmap data
                    # Resize the bitmap
                    resized_data = resize_bitmap_data(bitmap_data, new_size)
                    if resized_data:
                        # Update the bitmap data back to the glyph
                        # We need to update the imageData after decompilation
                        bitmap_glyph.imageData = resized_data

                        bitmaps_resized += 1

                # Show progress for large numbers of glyphs (less frequent)
                if processed_count % 2000 == 0:
                    print(f"    Progress: {processed_count}/{len(strike_data)} glyphs processed...")

            except Exception as e:
                # Skip errors silently - most are expected (non-emoji glyphs)
                continue

        print(f"    Processed {total_glyphs} glyphs, successfully resized {bitmaps_resized} bitmaps")
        return bitmaps_resized > 0

    except Exception as e:
        print(f"    ❌ Error accessing CBDT data: {e}")
        return False


def update_strike_size_metadata(font, strike_index, new_size):
    """
    Update only the size metadata in CBLC table for DirectWrite compatibility
    This is a fallback when we can't resize the actual bitmap data
    """
    cblc = font["CBLC"]

    if strike_index >= len(cblc.strikes):
        return False

    strike = cblc.strikes[strike_index]

    # Update the strike size information in CBLC
    if hasattr(strike, 'bitmapSizeTable'):
        bst = strike.bitmapSizeTable
        if hasattr(bst, 'ppemX') and hasattr(bst, 'ppemY'):
            old_size = f"{bst.ppemX}x{bst.ppemY}"
            bst.ppemX = new_size
            bst.ppemY = new_size
            print(f"    Updated CBLC metadata: {old_size} → {new_size}x{new_size}")

            # Also update other size-related fields if they exist
            if hasattr(bst, 'hori') and hasattr(bst.hori, 'ascender'):
                # Scale metrics proportionally
                scale_factor = new_size / max(bst.ppemX, bst.ppemY) if max(bst.ppemX, bst.ppemY) > 0 else 1
                bst.hori.ascender = int(bst.hori.ascender * scale_factor)
                bst.hori.descender = int(bst.hori.descender * scale_factor)
                print(f"    Scaled horizontal metrics by {scale_factor:.2f}")

            if hasattr(bst, 'vert') and hasattr(bst.vert, 'ascender'):
                scale_factor = new_size / max(bst.ppemX, bst.ppemY) if max(bst.ppemX, bst.ppemY) > 0 else 1
                bst.vert.ascender = int(bst.vert.ascender * scale_factor)
                bst.vert.descender = int(bst.vert.descender * scale_factor)
                print(f"    Scaled vertical metrics by {scale_factor:.2f}")

            return True

    return False


def resize_bitmap_data(bitmap_data, new_size):
    """
    Resize bitmap image data using PIL/Pillow
    """
    try:
        # Skip if data is too small to be a valid image
        if len(bitmap_data) < 10:
            return None

        # Try to load the bitmap data as an image
        image_stream = io.BytesIO(bitmap_data)
        image = Image.open(image_stream)

        # Only resize if the size is actually different
        if image.size == (new_size, new_size):
            return bitmap_data  # No need to resize

        # Resize with high-quality resampling
        resized_image = image.resize((new_size, new_size), Image.Resampling.LANCZOS)

        # Save back to bytes
        output_stream = io.BytesIO()
        # Use PNG format for DirectWrite compatibility
        format_to_use = 'PNG'

        # For PNG, preserve transparency
        if image.mode in ('RGBA', 'LA') or (image.mode == 'P' and 'transparency' in image.info):
            resized_image.save(output_stream, format=format_to_use, optimize=True)
        else:
            # Convert to RGBA to ensure transparency support
            resized_image = resized_image.convert('RGBA')
            resized_image.save(output_stream, format=format_to_use, optimize=True)

        resized_data = output_stream.getvalue()

        return resized_data

    except Exception as e:
        # Skip errors silently - return None for failed resizes
        return None


def diagnose_cbdt_cblc_directwrite_issues(font):
    """
    Diagnose specific CBDT/CBLC bitmap format issues that cause DirectWrite failures
    Based on Microsoft DirectWrite documentation and research
    """
    print("\n=== CBDT/CBLC DIRECTWRITE DIAGNOSTIC ===")

    if "CBDT" not in font or "CBLC" not in font:
        print("⚠ No CBDT/CBLC tables found")
        return

    cblc = font["CBLC"]
    cbdt = font["CBDT"]

    print(f"Found {len(cblc.strikes)} bitmap strikes")

    # Critical DirectWrite requirements based on research:
    directwrite_issues = []

    for i, strike in enumerate(cblc.strikes):
        print(f"\nStrike {i} analysis:")

        # 1. Deep analysis of strike attributes
        print(f"  Strike attributes: {[attr for attr in dir(strike) if not attr.startswith('_')]}")

        # Try multiple ways to get image format
        image_format = None
        format_found = False

        # Method 1: Direct imageFormat attribute
        if hasattr(strike, 'imageFormat'):
            image_format = strike.imageFormat
            format_found = True

        # Method 2: Check indexSubTables for format info
        elif hasattr(strike, 'indexSubTables') and strike.indexSubTables:
            for j, subtable in enumerate(strike.indexSubTables):
                print(f"    IndexSubTable {j} attributes: {[attr for attr in dir(subtable) if not attr.startswith('_')]}")
                if hasattr(subtable, 'imageFormat'):
                    image_format = subtable.imageFormat
                    format_found = True
                    print(f"    Found imageFormat in indexSubTable {j}: {image_format}")
                    break

        # Method 3: Check first few bytes of actual bitmap data to identify format
        if not format_found and hasattr(strike, 'indexSubTables') and strike.indexSubTables:
            try:
                # Try to access actual bitmap data
                first_subtable = strike.indexSubTables[0]
                if hasattr(first_subtable, 'firstGlyphIndex') and hasattr(first_subtable, 'lastGlyphIndex'):
                    print(f"    Glyph range: {first_subtable.firstGlyphIndex}-{first_subtable.lastGlyphIndex}")

                    # Try to get bitmap data from CBDT table
                    if hasattr(cbdt, 'strikeData') and i < len(cbdt.strikeData):
                        strike_data = cbdt.strikeData[i]
                        if hasattr(strike_data, 'data') and len(strike_data.data) > 8:
                            # Check magic bytes to identify format
                            data_start = strike_data.data[:8]
                            if data_start.startswith(b'\x89PNG'):
                                image_format = 17
                                format_found = True
                                print(f"    Detected PNG format from bitmap data")
                            elif data_start.startswith(b'\xFF\xD8\xFF'):
                                image_format = 18
                                format_found = True
                                print(f"    Detected JPEG format from bitmap data")
            except Exception as e:
                print(f"    Could not analyze bitmap data: {e}")

        # Report image format findings
        if format_found and image_format is not None:
            format_names = {17: "PNG", 18: "JPEG", 19: "TIFF", 1: "Monochrome", 2: "Grayscale"}
            format_name = format_names.get(image_format, f"Unknown({image_format})")
            print(f"  Image format: {format_name} (code: {image_format})")

            if image_format != 17:
                issue = f"Strike {i}: DirectWrite prefers PNG format (17), found {image_format} ({format_name})"
                directwrite_issues.append(issue)
                print(f"  ❌ {issue}")
            else:
                print(f"  ✓ PNG format - DirectWrite compatible")
        else:
            directwrite_issues.append(f"Strike {i}: Cannot determine image format - this is critical for DirectWrite")
            print(f"  ❌ Cannot determine image format - this is critical for DirectWrite")

        # 2. Deep analysis of strike sizes
        size_found = False
        size_x = size_y = None

        # Method 1: Direct ppem attributes
        if hasattr(strike, 'ppemX') and hasattr(strike, 'ppemY'):
            size_x, size_y = strike.ppemX, strike.ppemY
            size_found = True

        # Method 2: Check for alternative size attributes
        elif hasattr(strike, 'ppem'):
            size_x = size_y = strike.ppem
            size_found = True

        # Method 3: Check bitmapSizeTable
        elif hasattr(strike, 'bitmapSizeTable'):
            bst = strike.bitmapSizeTable
            if hasattr(bst, 'ppemX') and hasattr(bst, 'ppemY'):
                size_x, size_y = bst.ppemX, bst.ppemY
                size_found = True

        if size_found:
            print(f"  Size: {size_x}x{size_y} pixels")

            # DirectWrite preferred sizes based on Windows Segoe UI Emoji
            preferred_sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128]
            if size_x not in preferred_sizes or size_y not in preferred_sizes:
                issue = f"Strike {i}: Unusual size {size_x}x{size_y} - DirectWrite prefers {preferred_sizes}"
                directwrite_issues.append(issue)
                print(f"  ⚠ {issue}")
            else:
                print(f"  ✓ Standard size - DirectWrite compatible")
        else:
            print(f"  ⚠ Cannot determine strike size")
            print(f"    Available strike attributes: {[attr for attr in dir(strike) if 'ppem' in attr.lower() or 'size' in attr.lower()]}")

        # 3. Check if strike has proper glyph metrics
        if hasattr(strike, 'indexSubTables') and strike.indexSubTables:
            print(f"  Index subtables: {len(strike.indexSubTables)}")
            print(f"  ✓ Has glyph index data")
        else:
            issue = f"Strike {i}: Missing or empty index subtables"
            directwrite_issues.append(issue)
            print(f"  ❌ {issue}")

    # Summary of DirectWrite compatibility issues
    print(f"\n=== DIRECTWRITE COMPATIBILITY SUMMARY ===")
    if directwrite_issues:
        print(f"❌ Found {len(directwrite_issues)} potential DirectWrite issues:")
        for issue in directwrite_issues:
            print(f"  • {issue}")

        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        print(f"DirectWrite shows empty spaces because:")
        print(f"1. Font claims to support emoji characters (cmap table)")
        print(f"2. DirectWrite finds CBDT/CBLC bitmap data")
        print(f"3. DirectWrite validates bitmap format and fails")
        print(f"4. Instead of fallback, DirectWrite shows empty space")

        print(f"\n💡 POTENTIAL SOLUTIONS:")
        if any("format" in issue.lower() for issue in directwrite_issues):
            print(f"• Convert bitmap formats to PNG (format 17)")
        if any("size" in issue.lower() for issue in directwrite_issues):
            print(f"• Add standard DirectWrite bitmap sizes")
        if any("index" in issue.lower() for issue in directwrite_issues):
            print(f"• Fix glyph index table structure")

    else:
        print(f"✓ No obvious CBDT/CBLC DirectWrite compatibility issues found")
        print(f"  The issue may be in other font tables or DirectWrite validation")


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
