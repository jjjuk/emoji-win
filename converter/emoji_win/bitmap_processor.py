#!/usr/bin/env python3
"""
Bitmap processing module for emoji-win

This module handles CBDT/CBLC bitmap processing and DirectWrite compatibility
optimizations for emoji fonts.

Author: jjjuk
License: MIT
"""

import io
from PIL import Image


def fix_cbdt_cblc_sizes_for_directwrite(font, progress_callback=None, quiet=False):
    """
    Fix CBDT/CBLC bitmap sizes to match DirectWrite requirements
    Resize bitmaps from Apple's 137x137 to DirectWrite's preferred 128x128

    Args:
        font: TTFont object
        progress_callback: Optional callback function(current, total, description)
        quiet: If True, suppress print statements
    """

    def log(message):
        if not quiet:
            print(message)
    if "CBDT" not in font or "CBLC" not in font:
        log("⚠ No CBDT/CBLC tables found")
        return False

    cblc = font["CBLC"]
    cbdt = font["CBDT"]

    # DirectWrite preferred sizes
    directwrite_sizes = [16, 20, 24, 32, 40, 48, 64, 96, 128]

    log(f"Found {len(cblc.strikes)} bitmap strikes to analyze")

    strikes_modified = 0
    total_strikes = len(cblc.strikes)

    for i, strike in enumerate(cblc.strikes):
        if progress_callback:
            progress_callback(i, total_strikes, f"Analyzing strike {i+1}/{total_strikes}")

        log(f"\nProcessing strike {i}:")

        # Get current size
        current_size = None
        if hasattr(strike, 'bitmapSizeTable'):
            bst = strike.bitmapSizeTable
            if hasattr(bst, 'ppemX') and hasattr(bst, 'ppemY'):
                current_size = (bst.ppemX, bst.ppemY)
                log(f"  Current size: {current_size[0]}x{current_size[1]}")

        if not current_size:
            log(f"  ⚠ Cannot determine current size, skipping")
            continue

        # Find closest DirectWrite size
        current_max = max(current_size)
        closest_size = min(directwrite_sizes, key=lambda x: abs(x - current_max))

        if current_max == closest_size:
            log(f"  ✓ Size {current_max} already DirectWrite compatible")
            continue

        log(f"  Resizing from {current_max}x{current_max} to {closest_size}x{closest_size}")

        try:
            # Method 1: Try to resize actual bitmap data
            def glyph_progress_callback(current, total, description):
                if progress_callback:
                    # Report detailed progress for this strike
                    strike_progress = (i + (current / total)) / total_strikes
                    progress_callback(strike_progress * total_strikes, total_strikes,
                                    f"Strike {i+1}/{total_strikes}: {description}")

            success = resize_strike_bitmaps(font, i, closest_size, glyph_progress_callback, log)
            if success:
                strikes_modified += 1
                log(f"  ✓ Successfully resized bitmap data for strike {i}")
            else:
                # Method 2: At minimum, update the size metadata for DirectWrite
                log(f"  ⚠ Could not resize bitmap data, updating size metadata only")
                success = update_strike_size_metadata(font, i, closest_size, log)
                if success:
                    strikes_modified += 1
                    log(f"  ✓ Updated size metadata for strike {i} (DirectWrite compatibility)")
                else:
                    log(f"  ❌ Failed to update strike {i}")

        except Exception as e:
            log(f"  ❌ Error processing strike {i}: {e}")

    if strikes_modified > 0:
        log(f"\n✓ Successfully modified {strikes_modified} bitmap strikes for DirectWrite compatibility")
        return True
    else:
        log(f"\n⚠ No bitmap strikes were modified")
        return False


def resize_strike_bitmaps(font, strike_index, new_size, progress_callback=None, log=print):
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
            log(f"    Updated CBLC strike size table to {new_size}x{new_size}")

    # Process each glyph bitmap in this strike using proper CBDT access
    if not hasattr(strike, 'indexSubTables') or not strike.indexSubTables:
        log(f"    ⚠ No index subtables found")
        return False

    bitmaps_resized = 0
    total_glyphs = 0

    # Get the glyph order to map glyph IDs to names
    glyph_order = font.getGlyphOrder()

    # Access CBDT strike data using correct fonttools API
    try:
        if not hasattr(cbdt, 'strikeData') or strike_index >= len(cbdt.strikeData):
            log(f"    ❌ No strike data found for strike {strike_index}")
            return False

        strike_data = cbdt.strikeData[strike_index]  # This is a dictionary of glyph_name -> bitmap_glyph
        total_glyphs_in_strike = len(strike_data)

        log(f"    Found {total_glyphs_in_strike} bitmap glyphs in strike {strike_index}")

        # Process each glyph in the strike data
        processed_count = 0
        for glyph_name, bitmap_glyph in strike_data.items():
            processed_count += 1
            total_glyphs += 1

            # Report progress for every 100 glyphs or at key milestones
            if progress_callback and (processed_count % 100 == 0 or processed_count == total_glyphs_in_strike):
                progress_callback(processed_count, total_glyphs_in_strike,
                                f"Processing glyph {processed_count}/{total_glyphs_in_strike}")

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

            except Exception as e:
                # Skip errors silently - most are expected (non-emoji glyphs)
                continue

        log(f"    Processed {total_glyphs} glyphs, successfully resized {bitmaps_resized} bitmaps")
        return bitmaps_resized > 0

    except Exception as e:
        log(f"    ❌ Error accessing CBDT data: {e}")
        return False


def update_strike_size_metadata(font, strike_index, new_size, log=print):
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
            log(f"    Updated CBLC metadata: {old_size} → {new_size}x{new_size}")

            # Also update other size-related fields if they exist
            if hasattr(bst, 'hori') and hasattr(bst.hori, 'ascender'):
                # Scale metrics proportionally
                scale_factor = new_size / max(bst.ppemX, bst.ppemY) if max(bst.ppemX, bst.ppemY) > 0 else 1
                bst.hori.ascender = int(bst.hori.ascender * scale_factor)
                bst.hori.descender = int(bst.hori.descender * scale_factor)
                log(f"    Scaled horizontal metrics by {scale_factor:.2f}")

            if hasattr(bst, 'vert') and hasattr(bst.vert, 'ascender'):
                scale_factor = new_size / max(bst.ppemX, bst.ppemY) if max(bst.ppemX, bst.ppemY) > 0 else 1
                bst.vert.ascender = int(bst.vert.ascender * scale_factor)
                bst.vert.descender = int(bst.vert.descender * scale_factor)
                log(f"    Scaled vertical metrics by {scale_factor:.2f}")

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
