#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Auto-crop figures to content area with optional margin.

This utility automatically detects the content area of saved figures
and crops them, removing excess whitespace while preserving a specified margin.
"""

__all__ = ["crop", "find_content_area", "mm_to_pixels"]

from pathlib import Path
from typing import Optional, Tuple, Union

import numpy as np


def find_content_area(image_path: Union[str, Path]) -> Tuple[int, int, int, int]:
    """Find the bounding box of the content area in an image.

    Parameters
    ----------
    image_path : str or Path
        Path to the image file

    Returns
    -------
    tuple
        (left, upper, right, lower) bounding box coordinates

    Raises
    ------
    FileNotFoundError
        If the image cannot be read
    """
    from PIL import Image

    img = Image.open(image_path)
    img_array = np.array(img)

    # Check if image has alpha channel (RGBA) with actual transparency
    if len(img_array.shape) == 3 and img_array.shape[2] == 4:
        alpha = img_array[:, :, 3]
        # Only use alpha-based detection if there's actual transparency
        if alpha.min() < 255:
            # Use alpha channel to find content (non-transparent pixels)
            rows = np.any(alpha > 0, axis=1)
            cols = np.any(alpha > 0, axis=0)
        else:
            # Fully opaque RGBA - use RGB color-based detection
            rgb = img_array[:, :, :3]
            h, w = rgb.shape[:2]
            corners = [rgb[0, 0], rgb[0, w - 1], rgb[h - 1, 0], rgb[h - 1, w - 1]]
            bg_color = np.median(corners, axis=0).astype(np.uint8)
            diff = np.abs(rgb.astype(np.int16) - bg_color.astype(np.int16))
            is_content = np.any(diff > 10, axis=2)
            rows = np.any(is_content, axis=1)
            cols = np.any(is_content, axis=0)
    else:
        # For RGB images, detect background color from corners
        if len(img_array.shape) == 3:
            h, w = img_array.shape[:2]
            corners = [
                img_array[0, 0],
                img_array[0, w - 1],
                img_array[h - 1, 0],
                img_array[h - 1, w - 1],
            ]
            bg_color = np.median(corners, axis=0).astype(np.uint8)
            diff = np.abs(img_array.astype(np.int16) - bg_color.astype(np.int16))
            is_content = np.any(diff > 10, axis=2)
        else:
            # Grayscale
            h, w = img_array.shape
            corners = [
                img_array[0, 0],
                img_array[0, w - 1],
                img_array[h - 1, 0],
                img_array[h - 1, w - 1],
            ]
            bg_value = np.median(corners)
            is_content = np.abs(img_array.astype(np.int16) - bg_value) > 10

        rows = np.any(is_content, axis=1)
        cols = np.any(is_content, axis=0)

    if np.any(rows) and np.any(cols):
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        return x_min, y_min, x_max + 1, y_max + 1
    else:
        return 0, 0, img.width, img.height


def mm_to_pixels(mm: float, dpi: int = 300) -> int:
    """Convert millimeters to pixels at given DPI.

    Parameters
    ----------
    mm : float
        Size in millimeters
    dpi : int
        Resolution in dots per inch (default: 300)

    Returns
    -------
    int
        Size in pixels (rounded)
    """
    return round(mm * dpi / 25.4)


def crop(
    input_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    margin_mm: float = 1.0,
    margin_px: Optional[int] = None,
    margin_left_mm: Optional[float] = None,
    margin_right_mm: Optional[float] = None,
    margin_top_mm: Optional[float] = None,
    margin_bottom_mm: Optional[float] = None,
    overwrite: bool = False,
    verbose: bool = False,
    return_offset: bool = False,
    crop_box: Optional[Tuple[int, int, int, int]] = None,
) -> Union[Path, Tuple[Path, dict]]:
    """Crop a figure image to its content area with a specified margin.

    Automatically detects background color (from corners) and crops to
    content, leaving only the specified margin around it.

    Parameters
    ----------
    input_path : str or Path
        Path to the input image (PNG, JPEG, etc.)
    output_path : str or Path, optional
        Path to save the cropped image. If None and overwrite=True,
        overwrites the input. If None and overwrite=False, adds '_cropped' suffix.
    margin_mm : float, optional
        Uniform margin in mm for all sides (default: 1.0mm). Overridden by
        per-side margins if specified.
    margin_px : int, optional
        Uniform margin in pixels (overrides margin_mm if provided).
    margin_left_mm : float, optional
        Left margin in mm (overrides margin_mm for left side).
    margin_right_mm : float, optional
        Right margin in mm (overrides margin_mm for right side).
    margin_top_mm : float, optional
        Top margin in mm (overrides margin_mm for top side).
    margin_bottom_mm : float, optional
        Bottom margin in mm (overrides margin_mm for bottom side).
    overwrite : bool, optional
        Whether to overwrite the input file (default: False)
    verbose : bool, optional
        Whether to print detailed information (default: False)
    return_offset : bool, optional
        If True, also return the crop offset for metadata adjustment.
    crop_box : tuple, optional
        Explicit crop coordinates (left, upper, right, lower). If provided,
        skips auto-detection and uses these exact coordinates.

    Returns
    -------
    Path or tuple
        Path to the saved cropped image. If return_offset=True, returns
        (path, offset_dict) with crop boundaries.

    Examples
    --------
    >>> import figrecipe as fr
    >>> fig, ax = fr.subplots(axes_width_mm=60, axes_height_mm=40)
    >>> ax.plot([1, 2, 3], [1, 2, 3], id='line')
    >>> fig.savefig("figure.png", dpi=300)
    >>> fr.crop("figure.png", overwrite=True)  # 1mm margin
    >>> fr.crop("figure.png", margin_mm=2.0)   # 2mm margin
    >>> fr.crop("figure.png", margin_px=24)    # explicit 24 pixels
    """
    from PIL import Image

    input_path = Path(input_path)

    # Determine output path
    if output_path is None:
        if overwrite:
            output_path = input_path
        else:
            output_path = input_path.with_stem(f"{input_path.stem}_cropped")
    else:
        output_path = Path(output_path)

    img = Image.open(input_path)
    original_width, original_height = img.size

    # Get DPI from image metadata (default to 300 if not available)
    dpi = 300
    if "dpi" in img.info:
        dpi_info = img.info["dpi"]
        if isinstance(dpi_info, tuple):
            dpi = int(dpi_info[0])  # Use horizontal DPI
        else:
            dpi = int(dpi_info)

    # Calculate per-side margins in pixels
    if margin_px is not None:
        # Uniform pixel margin
        margin_left_px = margin_right_px = margin_top_px = margin_bottom_px = margin_px
    else:
        # Per-side mm margins (default to uniform margin_mm)
        ml = margin_left_mm if margin_left_mm is not None else margin_mm
        mr = margin_right_mm if margin_right_mm is not None else margin_mm
        mt = margin_top_mm if margin_top_mm is not None else margin_mm
        mb = margin_bottom_mm if margin_bottom_mm is not None else margin_mm

        margin_left_px = mm_to_pixels(ml, dpi)
        margin_right_px = mm_to_pixels(mr, dpi)
        margin_top_px = mm_to_pixels(mt, dpi)
        margin_bottom_px = mm_to_pixels(mb, dpi)

    if verbose:
        print(f"Original: {original_width}x{original_height}")
        print(f"DPI: {dpi}")
        print(
            f"Margins (px): left={margin_left_px}, right={margin_right_px}, "
            f"top={margin_top_px}, bottom={margin_bottom_px}"
        )

    # Use explicit crop_box or auto-detect
    if crop_box is not None:
        left, upper, right, lower = crop_box
        if verbose:
            print(f"Using explicit crop_box: {crop_box}")
    else:
        content_left, content_upper, content_right, content_lower = find_content_area(
            input_path
        )
        if verbose:
            print(
                f"Content area: left={content_left}, upper={content_upper}, "
                f"right={content_right}, lower={content_lower}"
            )

        # Calculate desired crop coordinates with margins
        left = content_left - margin_left_px
        upper = content_upper - margin_top_px
        right = content_right + margin_right_px
        lower = content_lower + margin_bottom_px

    if verbose:
        print(f"Desired crop: {left},{upper} -> {right},{lower}")
        print(f"New size: {right - left}x{lower - upper}")

    # Check if we need to extend the canvas (content touches original edge)
    needs_extend = left < 0 or upper < 0 or right > img.width or lower > img.height

    if needs_extend:
        # Detect background color from corners
        img_array = np.array(img)
        if len(img_array.shape) == 3:
            h, w = img_array.shape[:2]
            corners = [
                img_array[0, 0],
                img_array[0, w - 1],
                img_array[h - 1, 0],
                img_array[h - 1, w - 1],
            ]
            bg_color = tuple(
                int(x) for x in np.median(corners, axis=0).astype(np.uint8)
            )
        else:
            h, w = img_array.shape
            corners = [
                img_array[0, 0],
                img_array[0, w - 1],
                img_array[h - 1, 0],
                img_array[h - 1, w - 1],
            ]
            bg_color = int(np.median(corners))

        # Calculate new canvas size
        new_width = right - left
        new_height = lower - upper

        # Create new canvas with background color
        if img.mode == "RGBA":
            # Add alpha channel to bg_color tuple
            if len(bg_color) == 3:
                bg_color = bg_color + (255,)
            new_img = Image.new("RGBA", (new_width, new_height), bg_color)
        else:
            new_img = Image.new(img.mode, (new_width, new_height), bg_color)

        # Calculate where to paste the original (negative offset becomes positive)
        paste_x = max(-left, 0)
        paste_y = max(-upper, 0)

        # Crop the original image to what's within bounds
        crop_left = max(left, 0)
        crop_upper = max(upper, 0)
        crop_right = min(right, img.width)
        crop_lower = min(lower, img.height)

        if verbose:
            print(f"Extending canvas: paste at ({paste_x}, {paste_y})")
            print(f"Background color: {bg_color}")

        # Paste original content onto new canvas
        cropped_original = img.crop((crop_left, crop_upper, crop_right, crop_lower))
        new_img.paste(cropped_original, (paste_x, paste_y))
        cropped_img = new_img
    else:
        # Simple crop - no extension needed
        cropped_img = img.crop((left, upper, right, lower))

    # Preserve metadata
    save_kwargs = {}
    if "dpi" in img.info:
        save_kwargs["dpi"] = img.info["dpi"]

    ext = output_path.suffix.lower()
    if ext == ".png":
        save_kwargs["compress_level"] = 6  # Good compression/speed balance
        save_kwargs["optimize"] = True

        # Preserve PNG text chunks
        from PIL import PngImagePlugin

        pnginfo = PngImagePlugin.PngInfo()
        for key, value in img.info.items():
            if isinstance(value, (str, bytes)):
                try:
                    pnginfo.add_text(
                        key, str(value) if isinstance(value, bytes) else value
                    )
                except Exception:
                    pass
        save_kwargs["pnginfo"] = pnginfo

    elif ext in [".jpg", ".jpeg"]:
        save_kwargs["quality"] = 100
        save_kwargs["subsampling"] = 0
        save_kwargs["optimize"] = False

    cropped_img.save(output_path, **save_kwargs)

    final_width, final_height = cropped_img.size
    if verbose:
        area_reduction = 1 - (
            (final_width * final_height) / (original_width * original_height)
        )
        print(f"Saved {area_reduction * 100:.1f}% of original area")
        if output_path != input_path:
            print(f"Saved to: {output_path}")

    if return_offset:
        offset = {
            "left": left,
            "upper": upper,
            "right": right,
            "lower": lower,
            "original_width": original_width,
            "original_height": original_height,
            "new_width": final_width,
            "new_height": final_height,
        }
        return output_path, offset

    return output_path
