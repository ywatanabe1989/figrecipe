#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Grid-based layout composition for figures."""

import math
from typing import List, Tuple

from PIL import Image


def compose_grid_layout(
    images: List[Image.Image], layout: str, gap_px: int
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

    Returns
    -------
    result : Image
        Composed image.
    positions : list
        List of (x, y, width, height) in pixels for each panel.
    """
    positions = []  # List of (x, y, width, height) for each image

    if layout == "horizontal":
        total_width = sum(img.width for img in images) + gap_px * (len(images) - 1)
        max_height = max(img.height for img in images)
        result = Image.new("RGBA", (total_width, max_height), (255, 255, 255, 255))
        x_offset = 0
        for img in images:
            result.paste(img, (x_offset, 0))
            positions.append((x_offset, 0, img.width, img.height))
            x_offset += img.width + gap_px

    elif layout == "vertical":
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + gap_px * (len(images) - 1)
        result = Image.new("RGBA", (max_width, total_height), (255, 255, 255, 255))
        y_offset = 0
        for img in images:
            result.paste(img, (0, y_offset))
            positions.append((0, y_offset, img.width, img.height))
            y_offset += img.height + gap_px

    elif layout == "grid":
        ncols = math.ceil(math.sqrt(len(images)))
        nrows = math.ceil(len(images) / ncols)
        max_w = max(img.width for img in images)
        max_h = max(img.height for img in images)
        total_width = ncols * max_w + (ncols - 1) * gap_px
        total_height = nrows * max_h + (nrows - 1) * gap_px
        result = Image.new("RGBA", (total_width, total_height), (255, 255, 255, 255))
        for idx, img in enumerate(images):
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
