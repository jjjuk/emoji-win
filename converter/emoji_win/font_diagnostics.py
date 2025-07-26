#!/usr/bin/env python3
"""
Font diagnostics module for emoji-win

This module provides diagnostic and analysis functions for debugging font
compatibility issues, particularly with DirectWrite.

Author: jjjuk
License: MIT
"""


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


def analyze_font_structure(font):
    """
    Analyze the overall structure of a font for compatibility issues
    """
    print("\n=== FONT STRUCTURE ANALYSIS ===")
    
    print(f"Available tables: {sorted(font.keys())}")
    print(f"Font flavor: {font.flavor}")
    print(f"SFNT version: {font.sfntVersion}")

    # Check what type of emoji data we have
    emoji_formats = []
    if "sbix" in font:
        emoji_formats.append("Apple sbix (color bitmap)")
    if "COLR" in font and "CPAL" in font:
        emoji_formats.append("COLR/CPAL (color vector)")
    if "CBDT" in font and "CBLC" in font:
        emoji_formats.append("CBDT/CBLC (bitmap)")
    if "glyf" in font:
        emoji_formats.append("glyf (outline)")
    
    if emoji_formats:
        print(f"Emoji formats found: {', '.join(emoji_formats)}")
    else:
        print("⚠ No emoji formats detected")

    # Analyze cmap table
    if "cmap" in font:
        cmap = font["cmap"]
        print(f"\nCharacter mapping (cmap):")
        print(f"  Subtables: {len(cmap.tables)}")
        
        for subtable in cmap.tables:
            char_count = len(subtable.cmap) if hasattr(subtable, "cmap") else 0
            platform_name = _get_platform_name(subtable.platformID)
            encoding_name = _get_encoding_name(subtable.platformID, subtable.platEncID)
            print(f"  - {platform_name} {encoding_name} ({char_count} chars)")

    # Analyze OS/2 table for DirectWrite compatibility
    if "OS/2" in font:
        os2 = font["OS/2"]
        print(f"\nOS/2 table analysis:")
        print(f"  Version: {os2.version}")
        print(f"  USE_TYPO_METRICS flag: {'✓' if (os2.fsSelection & (1 << 7)) else '❌'}")
        print(f"  Typography metrics: Ascender={os2.sTypoAscender}, Descender={os2.sTypoDescender}, LineGap={os2.sTypoLineGap}")


def _get_platform_name(platform_id):
    """Get human-readable platform name"""
    platforms = {
        0: "Unicode",
        1: "Apple",
        2: "ISO",
        3: "Microsoft"
    }
    return platforms.get(platform_id, f"Platform {platform_id}")


def _get_encoding_name(platform_id, encoding_id):
    """Get human-readable encoding name"""
    if platform_id == 3:  # Microsoft
        encodings = {
            0: "Symbol",
            1: "Unicode BMP",
            10: "Unicode Full"
        }
        return encodings.get(encoding_id, f"Encoding {encoding_id}")
    elif platform_id == 1:  # Apple
        encodings = {
            0: "Roman"
        }
        return encodings.get(encoding_id, f"Encoding {encoding_id}")
    else:
        return f"Encoding {encoding_id}"
