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

    # Check if image has alpha channel (RGBA)
    if len(img_array.shape) == 3 and img_array.shape[2] == 4:
        # Use alpha channel to find content (non-transparent pixels)
        alpha = img_array[:, :, 3]
        rows = np.any(alpha > 0, axis=1)
        cols = np.any(alpha > 0, axis=0)
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
        Margin in millimeters to keep around content (default: 1.0mm).
        Converted to pixels using image DPI (or 300 DPI if not available).
    margin_px : int, optional
        Margin in pixels (overrides margin_mm if provided).
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

    # Calculate margin in pixels
    if margin_px is not None:
        margin = margin_px
    else:
        margin = mm_to_pixels(margin_mm, dpi)

    if verbose:
        print(f"Original: {original_width}x{original_height}")
        print(f"DPI: {dpi}")
        print(f"Margin: {margin_mm}mm = {margin}px")

    # Use explicit crop_box or auto-detect
    if crop_box is not None:
        left, upper, right, lower = crop_box
        if verbose:
            print(f"Using explicit crop_box: {crop_box}")
    else:
        left, upper, right, lower = find_content_area(input_path)
        if verbose:
            print(
                f"Content area: left={left}, upper={upper}, right={right}, lower={lower}"
            )

        # Add margin, clamping to image boundaries
        left = max(left - margin, 0)
        upper = max(upper - margin, 0)
        right = min(right + margin, img.width)
        lower = min(lower + margin, img.height)

    if verbose:
        print(f"Cropping to: {left},{upper} -> {right},{lower}")
        print(f"New size: {right - left}x{lower - upper}")

    # Crop the image
    cropped_img = img.crop((left, upper, right, lower))

    # Preserve metadata
    save_kwargs = {}
    if "dpi" in img.info:
        save_kwargs["dpi"] = img.info["dpi"]

    ext = output_path.suffix.lower()
    if ext == ".png":
        save_kwargs["compress_level"] = 0
        save_kwargs["optimize"] = False

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
