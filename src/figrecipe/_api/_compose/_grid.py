#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grid-based layout composition for figures."""

import math
from typing import List, Tuple

from PIL import Image

from ._utils import flatten_alpha


def _get_background_rgba(facecolor: str) -> Tuple[int, int, int, int]:
    """Convert facecolor string to RGBA tuple."""
    if facecolor.lower() == "white":
        return (255, 255, 255, 255)
    elif facecolor.lower() == "black":
        return (0, 0, 0, 255)
    else:
        try:
            from PIL import ImageColor

            rgb = ImageColor.getrgb(facecolor)
            return (*rgb, 255)
        except ValueError:
            return (255, 255, 255, 255)


def compose_grid_layout(
    images: List[Image.Image], layout: str, gap_px: int, facecolor: str = "white"
) -> Tuple[Image.Image, List[Tuple[int, int, int, int]]]:
    """Compose images into layout and return result with positions.

    Parameters
    ----------
    images : list of Image
        Source images to compose.
    layout : str
        Layout mode: 'horizontal', 'vertical', or 'grid'.
    gap_px : int
        Gap between panels in pixels.
    facecolor : str
        Background color for the canvas. Default is 'white'.

    Returns
    -------
    result : Image
        Composed image.
    positions : list
        List of (x, y, width, height) in pixels for each panel.
    """
    positions = []  # List of (x, y, width, height) for each image
    bg_rgba = _get_background_rgba(facecolor)

    # Flatten all images to handle transparent backgrounds
    flattened_images = [flatten_alpha(img, facecolor) for img in images]

    if layout == "horizontal":
        total_width = sum(img.width for img in flattened_images) + gap_px * (
            len(flattened_images) - 1
        )
        max_height = max(img.height for img in flattened_images)
        result = Image.new("RGBA", (total_width, max_height), bg_rgba)
        x_offset = 0
        for img in flattened_images:
            result.paste(img, (x_offset, 0))
            positions.append((x_offset, 0, img.width, img.height))
            x_offset += img.width + gap_px

    elif layout == "vertical":
        max_width = max(img.width for img in flattened_images)
        total_height = sum(img.height for img in flattened_images) + gap_px * (
            len(flattened_images) - 1
        )
        result = Image.new("RGBA", (max_width, total_height), bg_rgba)
        y_offset = 0
        for img in flattened_images:
            result.paste(img, (0, y_offset))
            positions.append((0, y_offset, img.width, img.height))
            y_offset += img.height + gap_px

    elif layout == "grid":
        ncols = math.ceil(math.sqrt(len(flattened_images)))
        nrows = math.ceil(len(flattened_images) / ncols)
        max_w = max(img.width for img in flattened_images)
        max_h = max(img.height for img in flattened_images)
        total_width = ncols * max_w + (ncols - 1) * gap_px
        total_height = nrows * max_h + (nrows - 1) * gap_px
        result = Image.new("RGBA", (total_width, total_height), bg_rgba)
        for idx, img in enumerate(flattened_images):
            row = idx // ncols
            col = idx % ncols
            x = col * (max_w + gap_px)
            y = row * (max_h + gap_px)
            result.paste(img, (x, y))
            positions.append((x, y, img.width, img.height))
    else:
        raise ValueError(
            f"Unknown layout: {layout}. Use 'horizontal', 'vertical', or 'grid'"
        )

    return result, positions
